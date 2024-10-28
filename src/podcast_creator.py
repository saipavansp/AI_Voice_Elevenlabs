import streamlit as st
from dataclasses import dataclass
from typing import Optional, List
import pyttsx3
import io
import threading
import queue
from concurrent.futures import ThreadPoolExecutor


@dataclass
class PodcastResponse:
    """Data class for podcast response."""

    text_answer: str
    podcast_script: Optional[str]
    audio: Optional[bytes]
    error: Optional[str] = None


class AudioProcessor:
    """Handles text-to-speech conversion with caching."""

    def __init__(self):
        self._engine = None
        self._audio_cache = {}
        self._lock = threading.Lock()
        self.initialize_engine()

    def initialize_engine(self):
        """Initialize TTS engine with optimal settings."""
        with self._lock:
            if not self._engine:
                self._engine = pyttsx3.init()
                self._engine.setProperty('rate', 160)  # Slightly faster speech
                self._engine.setProperty('volume', 0.9)
                voices = self._engine.getProperty('voices')
                if isinstance(voices, (list, tuple)) and len(voices) > 0:
                    self.voices = {
                        'host1': voices[0].id,
                        'host2': voices[1].id if len(voices) > 1 else voices[0].id
                    }
                else:
                    raise ValueError("No voices available in the TTS engine")

    def get_audio(self, text: str, voice_id: str) -> Optional[bytes]:
        """Get audio with caching."""
        cache_key = f"{text}:{voice_id}"
        if cache_key in self._audio_cache:
            return self._audio_cache[cache_key]

        try:
            buffer = io.BytesIO()
            with self._lock:
                self._engine.setProperty('voice', voice_id)
                self._engine.save_to_file(text, 'temp.wav')
                self._engine.runAndWait()

            with open('temp.wav', 'rb') as f:
                audio_data = f.read()

            self._audio_cache[cache_key] = audio_data
            return audio_data
        except Exception as e:
            st.error(f"Audio generation error: {str(e)}")
            return None


class PodcastCreator:
    def __init__(self):
        """Initialize podcast creator with optimized processing."""
        self.audio_processor = AudioProcessor()
        self.executor = ThreadPoolExecutor(max_workers=2)
        self._response_queue = queue.Queue()

    def clean_script(self, script: str) -> List[tuple]:
        """Process script into speaker-text pairs."""
        segments = []
        current_speaker = None
        current_text = []

        for line in script.split('\n'):
            if ':' in line:
                if current_speaker and current_text:
                    segments.append((current_speaker, ' '.join(current_text)))
                    current_text = []

                speaker, text = line.split(':', 1)
                current_speaker = speaker.strip()
                current_text.append(text.strip())
            elif current_speaker and line.strip():
                current_text.append(line.strip())

        if current_speaker and current_text:
            segments.append((current_speaker, ' '.join(current_text)))

        return segments

    def process_segment(self, text: str, is_first_speaker: bool) -> Optional[bytes]:
        """Process a single conversation segment."""
        voice_id = self.audio_processor.voices['host1'] if is_first_speaker else self.audio_processor.voices['host2']
        print(text)
        return self.audio_processor.get_audio(text, voice_id)

    def create_podcast(self, script: str) -> Optional[bytes]:
        """Create podcast with parallel processing."""
        try:
            segments = self.clean_script(script)
            if not segments:
                return None

            # Process segments in parallel
            futures = []
            for idx, (_, text) in enumerate(segments):
                future = self.executor.submit(
                    self.process_segment,
                    text,
                    idx % 2 == 0
                )
                futures.append(future)

            # Collect results
            audio_segments = []
            for future in futures:
                segment = future.result()
                if segment:
                    audio_segments.append(segment)

            if not audio_segments:
                return None

            # Combine segments
            return b''.join(audio_segments)

        except Exception as e:
            st.error(f"Podcast creation error: {str(e)}")
            return None

    def process_answer(self, text_answer: str, podcast_script: Optional[str]) -> PodcastResponse:
        """Generate podcast response with progress indication."""
        try:
            if not podcast_script:
                return PodcastResponse(
                    text_answer=text_answer,
                    podcast_script=None,
                    audio=None
                )

            # Create progress placeholder
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Process in steps
            status_text.text("Preparing script...")
            progress_bar.progress(0.2)

            status_text.text("Generating audio...")
            audio = self.create_podcast(podcast_script)
            progress_bar.progress(0.8)

            status_text.text("Finalizing...")
            progress_bar.progress(1.0)

            # Clean up
            progress_bar.empty()
            status_text.empty()

            return PodcastResponse(
                text_answer=text_answer,
                podcast_script=podcast_script,
                audio=audio
            )

        except Exception as e:
            return PodcastResponse(
                text_answer=text_answer,
                podcast_script=None,
                audio=None,
                error=str(e)
            )

    def __del__(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=False)