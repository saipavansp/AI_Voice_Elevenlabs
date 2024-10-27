"""Module for generating voice content using ElevenLabs API."""
import streamlit as st
from typing import Optional, List, Dict
from elevenlabs.client import ElevenLabs
import time

class VoiceGenerator:
    def __init__(self):
        """Initialize the voice generator."""
        if 'ELEVEN_LABS_API_KEY' not in st.secrets:
            st.error("ElevenLabs API key not found in secrets!")
            st.stop()

        try:
            self.client = ElevenLabs(api_key=st.secrets['ELEVEN_LABS_API_KEY'])

            # Get available voices from the API
            all_voices = self.client.voices.get_all()

            # Store available voice IDs
            self.available_voices = {
                voice.name: voice.voice_id for voice in all_voices
            }

            # Initialize default voices (will be updated with available voices)
            self.voices = {
                "Sarah": None,
                "Mike": None
            }

            # Try to find appropriate voices
            for voice in all_voices:
                if voice.name.lower() in ['rachel', 'emily', 'bella']:
                    self.voices["Sarah"] = voice.voice_id
                elif voice.name.lower() in ['josh', 'adam', 'sam']:
                    self.voices["Mike"] = voice.voice_id

            # If we couldn't find specific voices, use the first two available
            if not self.voices["Sarah"] or not self.voices["Mike"]:
                available_ids = list(self.available_voices.values())
                if len(available_ids) >= 2:
                    self.voices["Sarah"] = available_ids[0]
                    self.voices["Mike"] = available_ids[1]
                else:
                    raise Exception("Not enough voices available")

            self.initialized = True

        except Exception as e:
            st.error(f"Error initializing ElevenLabs: {str(e)}")
            self.initialized = False

    def generate_audio_segment(self, text: str, speaker: str) -> Optional[bytes]:
        """Generate audio for a single segment of conversation."""
        try:
            if not self.initialized:
                raise Exception("Voice generator not initialized")

            voice_id = self.voices.get(speaker)
            if not voice_id:
                raise Exception(f"No voice ID found for speaker {speaker}")

            # Generate audio
            audio_response = self.client.text_to_speech.convert(
                text=text,
                voice_id=voice_id,
                model_id="eleven_monolingual_v1"
            )

            # Convert response to bytes
            audio_data = b""
            for chunk in audio_response:
                audio_data += chunk

            return audio_data

        except Exception as e:
            st.error(f"Error generating audio segment: {str(e)}")
            return None

    def create_podcast(self, script: str) -> Optional[bytes]:
        """Create a natural-sounding podcast from the script."""
        try:
            if not self.initialized:
                raise Exception("Voice generator not initialized")

            # Split script into segments
            segments = []
            for line in script.split('\n'):
                if ':' not in line:
                    continue

                speaker, text = line.split(':', 1)
                speaker = speaker.strip()
                text = text.strip()

                if not text or speaker not in self.voices:
                    continue

                segments.append((speaker, text))

            if not segments:
                raise Exception("No valid segments found in script")

            # Generate audio for each segment
            audio_segments = []

            for speaker, text in segments:
                # Add a small delay between requests to avoid rate limits
                time.sleep(0.5)

                audio = self.generate_audio_segment(text, speaker)
                if audio:
                    audio_segments.append(audio)
                    # Add a short silence between segments
                    audio_segments.append(b'\x00' * 1000)  # Add silence

            if not audio_segments:
                raise Exception("Failed to generate any audio segments")

            # Combine all segments
            final_audio = b''.join(audio_segments)
            return final_audio

        except Exception as e:
            st.error(f"Error creating podcast: {str(e)}")
            return None

    def debug_voices(self):
        """Debug function to print available voices."""
        st.write("Available Voices:")
        for name, voice_id in self.available_voices.items():
            st.write(f"- {name}: {voice_id}")

        st.write("\nSelected Voices:")
        for speaker, voice_id in self.voices.items():
            st.write(f"- {speaker}: {voice_id}")

def test_voice_generator():
    """Test the voice generator."""
    print("Testing Voice Generator...")

    generator = VoiceGenerator()

    if not generator.initialized:
        print("Failed to initialize voice generator")
        return

    # Test simple audio generation
    test_script = """
    Sarah: Hello, this is a test of the voice generation system.
    Mike: Yes, let's see how well this works.
    Sarah: We're testing different voices and audio generation.
    """

    print("\nGenerating test audio...")
    audio = generator.create_podcast(test_script)

    if audio:
        with open("test_podcast.mp3", "wb") as f:
            f.write(audio)
        print("Test audio saved as test_podcast.mp3")
    else:
        print("Failed to generate audio")

if __name__ == "__main__":
    test_voice_generator()