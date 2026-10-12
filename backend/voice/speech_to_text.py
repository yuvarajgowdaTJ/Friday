"""
backend/voice/speech_to_text.py
Speech-To-Text Engine for FRIDAY with noise resilience, failure logging, and stop-command parsing.
"""

import io
import wave
import re
import logging
from typing import Optional
import numpy as np

logger = logging.getLogger("FRIDAY.Voice.STT")

STOP_COMMAND_PATTERNS = [
    r"\b(?:stop|stop talking|stop speaking|cancel|be quiet|quiet|shut up|silence|pause|abort|halt|stop it)\b"
]


class SpeechToTextEngine:
    """
    Speech-To-Text Engine for FRIDAY.
    Supports transcription from:
    1. Audio file paths (.wav)
    2. In-memory PCM audio bytes
    3. Numpy audio arrays from sounddevice
    Handles silence, unrecognized speech, and network drops gracefully with structured logging.
    """

    def __init__(self):
        self.recognizer = None
        self._init_recognizer()

    def _init_recognizer(self):
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            logger.info("SpeechRecognition STT engine initialized successfully.")
        except Exception as e:
            logger.warning("SpeechRecognition STT initialization failed: %s. Audio transcription will be unavailable.", e)
            self.recognizer = None

    @staticmethod
    def is_stop_command(text: Optional[str]) -> bool:
        """Returns True if the transcribed text matches a voice stop/interruption command."""
        if not text:
            return False
        clean = text.strip().lower()
        for pat in STOP_COMMAND_PATTERNS:
            if re.search(pat, clean):
                return True
        return False

    def transcribe_audio_file(self, file_path: str, language: str = "en-US") -> Optional[str]:
        """Transcribe audio from a WAV file."""
        if not self.recognizer:
            self._init_recognizer()
        if not self.recognizer:
            logger.error("STT transcription failure: Speech recognition engine is not initialized.")
            return None

        try:
            import speech_recognition as sr
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=language)
                result = text.strip() if text else None
                if result:
                    logger.info("STT: Successfully transcribed audio file to '%s'", result)
                return result
        except sr.UnknownValueError:
            logger.info("STT: Audio recorded but no intelligible speech recognized.")
            return None
        except sr.RequestError as e:
            logger.error("STT recognition service error (connectivity/quota): %s", e)
            return None
        except Exception as e:
            logger.error("STT unexpected error while transcribing file '%s': %s", file_path, e, exc_info=True)
            return None

    def transcribe_pcm_data(
        self,
        pcm_bytes: bytes,
        sample_rate: int = 16000,
        sample_width: int = 2,
        channels: int = 1,
        language: str = "en-US",
    ) -> Optional[str]:
        """Transcribe raw PCM bytes by wrapping in an in-memory WAV container."""
        if not pcm_bytes or len(pcm_bytes) < 500:
            logger.debug("STT: PCM data is empty or too short (%d bytes).", len(pcm_bytes) if pcm_bytes else 0)
            return None

        if not self.recognizer:
            self._init_recognizer()
        if not self.recognizer:
            logger.error("STT transcription failure: Speech recognition engine is not initialized.")
            return None

        try:
            import speech_recognition as sr
            wav_io = io.BytesIO()
            with wave.open(wav_io, "wb") as wf:
                wf.setnchannels(channels)
                wf.setsampwidth(sample_width)
                wf.setframerate(sample_rate)
                wf.writeframes(pcm_bytes)

            wav_io.seek(0)
            with sr.AudioFile(wav_io) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio, language=language)
                result = text.strip() if text else None
                if result:
                    logger.info("STT: Successfully transcribed PCM stream to '%s'", result)
                return result
        except sr.UnknownValueError:
            logger.info("STT: No intelligible speech recognized in PCM stream.")
            return None
        except sr.RequestError as e:
            logger.error("STT recognition service API error: %s", e)
            return None
        except Exception as e:
            logger.error("STT unexpected error transcribing PCM data: %s", e, exc_info=True)
            return None

    def transcribe_numpy_array(
        self,
        audio_data: Optional[np.ndarray],
        sample_rate: int = 16000,
        language: str = "en-US",
    ) -> Optional[str]:
        """Transcribe audio captured directly via sounddevice numpy array."""
        if audio_data is None or len(audio_data) == 0:
            logger.debug("STT: Received empty audio numpy array for transcription.")
            return None

        # Convert float32 or int16 numpy array to int16 bytes
        if audio_data.dtype in (np.float32, np.float64):
            audio_int16 = (np.clip(audio_data, -1.0, 1.0) * 32767).astype(np.int16)
        else:
            audio_int16 = audio_data.astype(np.int16)

        return self.transcribe_pcm_data(audio_int16.tobytes(), sample_rate=sample_rate, language=language)


stt_engine = SpeechToTextEngine()
