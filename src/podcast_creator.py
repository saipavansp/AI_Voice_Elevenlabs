"""Module for creating podcasts with improved audio processing."""
import streamlit as st
from dataclasses import dataclass
from typing import Optional, List, Tuple
import pyttsx3
import threading
from concurrent.futures import ThreadPoolExecutor
import wave
import os
from tempfile import NamedTemporaryFile


@dataclass
class PodcastResponse:
    """Data class for podcast response."""
    text_answer: str
    podcast_script: Optional[str]
    audio: Optional[bytes]
    error: Optional[str] = None


class AudioProcessor:
    """Handles text-to-speech conversion with improved audio concatenation."""

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
                self._engine.setProperty('rate', 160)  # Slightly slower for clarity
                self._engine.setProperty('volume', 0.9)
                voices = self._engine.getProperty('voices')
                if isinstance(voices, (list, tuple)) and len(voices) > 0:
                    self.voices = {
                        'host1': voices[0].id,
                        'host2': voices[1].id if len(voices) > 1 else voices[0].id
                    }
                else:
                    raise ValueError("No voices available in the TTS engine")

    @staticmethod
    def concatenate_wav_files(wav_files: List[str]) -> bytes:
        """Concatenate multiple WAV files into a single audio stream."""
        if not wav_files:
            return None

        # Read the first file to get parameters
        with wave.open(wav_files[0], 'rb') as first_wave:
            params = first_wave.getparams()

        # Create a temporary output file
        with NamedTemporaryFile(suffix='.wav', delete=False) as out_file:
            with wave.open(out_file.name, 'wb') as output:
                output.setparams(params)

                # Concatenate all files
                for wav_file in wav_files:
                    with wave.open(wav_file, 'rb') as w:
                        output.writeframes(w.readframes(w.getnframes()))

            # Read the final concatenated file
            with open(out_file.name, 'rb') as f:
                audio_data = f.read()

        # Cleanup temporary files
        try:
            os.unlink(out_file.name)
            for wav_file in wav_files:
                if os.path.exists(wav_file):
                    os.unlink(wav_file)
        except Exception as e:
            print(f"Cleanup error: {e}")

        return audio_data

    def get_audio(self, text: str, voice_id: str) -> Tuple[Optional[bytes], str]:
        """Get audio with improved handling of longer texts."""
        if not text.strip():
            return None, ""

        cache_key = f"{text}:{voice_id}"
        if cache_key in self._audio_cache:
            return self._audio_cache[cache_key], ""

        try:
            # Create a temporary file for this segment
            temp_file = NamedTemporaryFile(suffix='.wav', delete=False)
            temp_filename = temp_file.name
            temp_file.close()

            with self._lock:
                self._engine.setProperty('voice', voice_id)
                self._engine.save_to_file(text, temp_filename)
                self._engine.runAndWait()

            return temp_filename, ""
        except Exception as e:
            return None, str(e)


class PodcastCreator:
    def __init__(self):
        """Initialize podcast creator with improved processing."""
        self.audio_processor = AudioProcessor()
        self.executor = ThreadPoolExecutor(max_workers=2)

    def clean_script(self, script: str) -> List[tuple]:
        """Process script into speaker-text pairs with improved handling."""
        segments = []
        current_speaker = None
        current_text = []

        lines = [line.strip() for line in script.split('\n') if line.strip()]

        for line in lines:
            if ':' in line:
                # Save previous segment if exists
                if current_speaker and current_text:
                    segments.append((current_speaker, ' '.join(current_text)))
                    current_text = []

                # Start new segment
                speaker, text = line.split(':', 1)
                current_speaker = speaker.strip()
                current_text = [text.strip()]
            elif current_speaker:
                # Continue current segment
                current_text.append(line)

        # Add final segment
        if current_speaker and current_text:
            segments.append((current_speaker, ' '.join(current_text)))

        return segments

    def process_segment(self, text: str, is_first_speaker: bool) -> Optional[str]:
        """Process a single conversation segment."""
        voice_id = self.audio_processor.voices['host1'] if is_first_speaker else self.audio_processor.voices['host2']
        temp_filename, error = self.audio_processor.get_audio(text, voice_id)

        if error:
            st.error(f"Error processing segment: {error}")
            return None

        return temp_filename

    def create_podcast(self, script: str) -> Optional[bytes]:
        """Create podcast with improved audio handling."""
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

            # Collect temporary WAV files
            temp_files = []
            for future in futures:
                temp_file = future.result()
                if temp_file:
                    temp_files.append(temp_file)

            if not temp_files:
                return None

            # Concatenate all audio segments
            return self.audio_processor.concatenate_wav_files(temp_files)

        except Exception as e:
            st.error(f"Podcast creation error: {str(e)}")
            return None

    def process_answer(self, text_answer: str, podcast_script: Optional[str]) -> PodcastResponse:
        """Generate podcast response with improved progress tracking."""
        try:
            if not podcast_script:
                return PodcastResponse(
                    text_answer=text_answer,
                    podcast_script=None,
                    audio=None
                )

            progress_bar = st.progress(0)
            status_text = st.empty()

            # Process in steps
            status_text.text("Preparing script...")
            progress_bar.progress(0.2)

            status_text.text("Generating audio segments...")
            audio = self.create_podcast(podcast_script)
            progress_bar.progress(0.8)

            status_text.text("Finalizing podcast...")
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