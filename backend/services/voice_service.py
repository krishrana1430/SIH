"""
WeatherGPT Voice Service
Speech-to-Text and Text-to-Speech implementation
Supports multiple providers: Web Speech API, Google Cloud, Azure, OpenAI Whisper
"""

import os
import io
import logging
from typing import Optional, Dict, Any, BinaryIO
import tempfile
import base64

logger = logging.getLogger(__name__)


class VoiceService:
    """Voice service with STT and TTS capabilities."""

    def __init__(self):
        self.stt_provider = os.getenv("STT_PROVIDER", "whisper")  # whisper, google, azure, web
        self.tts_provider = os.getenv("TTS_PROVIDER", "web")  # web, google, azure, elevenlabs

        logger.info(f"Voice service initialized: STT={self.stt_provider}, TTS={self.tts_provider}")

    async def transcribe_audio(
        self,
        audio_data: bytes,
        language: str = "en",
        audio_format: str = "wav"
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using configured provider.

        Args:
            audio_data: Raw audio bytes
            language: Language code (en, hi, ta, etc.)
            audio_format: Audio format (wav, mp3, ogg, flac)

        Returns:
            Transcription result with text and metadata
        """
        try:
            if self.stt_provider == "whisper":
                return await self._transcribe_with_whisper(audio_data, language)
            elif self.stt_provider == "groq":
                return await self._transcribe_with_groq(audio_data, language)
            else:
                # Fallback to mock transcription
                return {
                    "text": "[Mock transcription - configure STT provider]",
                    "language": language,
                    "confidence": 0.0,
                    "provider": "mock"
                }

        except Exception as e:
            logger.error(f"STT error: {e}")
            raise

    async def _transcribe_with_whisper(
        self,
        audio_data: bytes,
        language: str
    ) -> Dict[str, Any]:
        """Transcribe using OpenAI Whisper API."""
        try:
            from openai import AsyncOpenAI

            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_PRIMARY_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not configured")

            client = AsyncOpenAI(api_key=api_key)

            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Transcribe
            with open(temp_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language if language != "auto" else None
                )

            # Cleanup
            os.unlink(temp_file_path)

            return {
                "text": transcript.text,
                "language": language,
                "confidence": 1.0,
                "provider": "whisper"
            }

        except Exception as e:
            logger.error(f"Whisper STT error: {e}")
            raise

    async def _transcribe_with_groq(
        self,
        audio_data: bytes,
        language: str
    ) -> Dict[str, Any]:
        """Transcribe using Groq Whisper API."""
        try:
            from openai import AsyncOpenAI

            api_key = os.getenv("LLM_PRIMARY_API_KEY")
            if not api_key:
                raise ValueError("Groq API key not configured")

            client = AsyncOpenAI(
                api_key=api_key,
                base_url="https://api.groq.com/openai/v1"
            )

            # Save audio to temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name

            # Transcribe with Groq's Whisper
            with open(temp_file_path, "rb") as audio_file:
                transcript = await client.audio.transcriptions.create(
                    model="whisper-large-v3",
                    file=audio_file,
                    language=language if language != "auto" else None,
                    temperature=0.0
                )

            # Cleanup
            os.unlink(temp_file_path)

            return {
                "text": transcript.text,
                "language": language,
                "confidence": 1.0,
                "provider": "groq-whisper"
            }

        except Exception as e:
            logger.error(f"Groq Whisper STT error: {e}")
            # Fallback to mock
            return {
                "text": f"[STT unavailable: {str(e)}]",
                "language": language,
                "confidence": 0.0,
                "provider": "error"
            }

    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        voice_gender: str = "female",
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Convert text to speech.

        Args:
            text: Text to synthesize
            language: Language code
            voice_gender: male or female
            speed: Speech rate (0.5 to 2.0)

        Returns:
            Audio data and metadata
        """
        try:
            if self.tts_provider == "groq":
                return await self._synthesize_with_groq(text, language, voice_gender, speed)
            elif self.tts_provider == "openai":
                return await self._synthesize_with_openai(text, language, voice_gender, speed)
            else:
                # Return metadata for Web Speech API (client-side TTS)
                return {
                    "provider": "web",
                    "text": text,
                    "language": language,
                    "voice_gender": voice_gender,
                    "speed": speed,
                    "audio_url": None,  # Client will synthesize
                    "instructions": "Use browser Web Speech API for synthesis"
                }

        except Exception as e:
            logger.error(f"TTS error: {e}")
            raise

    async def _synthesize_with_openai(
        self,
        text: str,
        language: str,
        voice_gender: str,
        speed: float
    ) -> Dict[str, Any]:
        """Synthesize speech using OpenAI TTS."""
        try:
            from openai import AsyncOpenAI

            api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_PRIMARY_API_KEY")
            if not api_key:
                raise ValueError("OpenAI API key not configured")

            client = AsyncOpenAI(api_key=api_key)

            # Map voice gender to OpenAI voices
            voice_map = {
                "female": "nova",  # or "alloy", "shimmer"
                "male": "onyx"     # or "echo", "fable"
            }
            voice = voice_map.get(voice_gender, "nova")

            # Generate speech
            response = await client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=text[:4096],  # Limit to 4096 chars
                speed=speed
            )

            # Get audio bytes
            audio_data = response.content

            # Encode as base64 for JSON response
            audio_base64 = base64.b64encode(audio_data).decode('utf-8')

            return {
                "provider": "openai-tts",
                "text": text,
                "language": language,
                "voice": voice,
                "speed": speed,
                "audio_format": "mp3",
                "audio_base64": audio_base64,
                "audio_size": len(audio_data)
            }

        except Exception as e:
            logger.error(f"OpenAI TTS error: {e}")
            raise

    async def _synthesize_with_groq(
        self,
        text: str,
        language: str,
        voice_gender: str,
        speed: float
    ) -> Dict[str, Any]:
        """Synthesize speech using Groq (if available)."""
        # Groq doesn't have TTS API yet, fallback to web
        return {
            "provider": "web",
            "text": text,
            "language": language,
            "voice_gender": voice_gender,
            "speed": speed,
            "audio_url": None,
            "instructions": "Use browser Web Speech API for synthesis"
        }

    def get_supported_languages(self) -> list:
        """Get list of supported languages for voice."""
        return [
            {"code": "en", "name": "English", "locale": "en-IN"},
            {"code": "hi", "name": "Hindi", "locale": "hi-IN"},
            {"code": "ta", "name": "Tamil", "locale": "ta-IN"},
            {"code": "te", "name": "Telugu", "locale": "te-IN"},
            {"code": "bn", "name": "Bengali", "locale": "bn-IN"},
            {"code": "mr", "name": "Marathi", "locale": "mr-IN"},
            {"code": "kn", "name": "Kannada", "locale": "kn-IN"},
            {"code": "gu", "name": "Gujarati", "locale": "gu-IN"},
            {"code": "ml", "name": "Malayalam", "locale": "ml-IN"},
            {"code": "pa", "name": "Punjabi", "locale": "pa-IN"}
        ]


# Global instance
voice_service = VoiceService()
