"""
backend/voice/text_to_speech.py
Natural Female Text-to-Speech Engine for FRIDAY with voice selection, markdown sanitization,
instant interruption/stop capability, and failure logging.
Guarantees Microsoft Zira (Female) voice selection on Windows SAPI5 without David fallback.
"""

import logging
import threading
import tempfile
import os
import re
import time
from typing import Optional, Dict, Any

try:
    from backend.config import settings
except ImportError:
    settings = None

logger = logging.getLogger("FRIDAY.Voice.TTS")


def sanitize_text_for_speech(text: str) -> str:
    """
    Cleans markdown formatting, code snippets, URLs, and symbols
    to produce smooth, natural conversational spoken English.
    """
    if not text:
        return ""
    # Strip markdown code blocks ```...```
    cleaned = re.sub(r"```[\s\S]*?```", " Code block omitted. ", text)
    # Strip inline code `...`
    cleaned = re.sub(r"`([^`]+)`", r"\1", cleaned)
    # Strip URLs
    cleaned = re.sub(r"https?://\S+", " web link ", cleaned)
    # Strip markdown headers (# Header)
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    # Strip bold / italics (**bold**, *italic*, __bold__, _italic_)
    cleaned = re.sub(r"\*\*([^*]+)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*([^*]+)\*", r"\1", cleaned)
    cleaned = re.sub(r"__([^_]+)__", r"\1", cleaned)
    cleaned = re.sub(r"_([^_]+)_", r"\1", cleaned)
    # Strip list bullets (* or - or + at start of line)
    cleaned = re.sub(r"^\s*[-*+]\s+", "", cleaned, flags=re.MULTILINE)
    # Strip markdown links [text](url)
    cleaned = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", cleaned)
    # Collapse multiple whitespaces and newlines
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


class TextToSpeechEngine:
    """
    Robust Natural Female Text-to-Speech engine supporting:
    - Thread-safe non-overlapping speech playback
    - Real-time stop / cancel capability via sounddevice and SAPI5
    - Explicit Microsoft Zira (Female) voice selection with zero fallback to David
    - Windows native SAPI fallback if pyttsx3 fails or overrides voice
    - Markdown sanitization for natural spoken delivery
    """

    def __init__(self):
        self.engine = None
        self._lock = threading.Lock()
        self._speaking_lock = threading.Lock()
        self._is_speaking = False
        self._stop_requested = False
        self.selected_voice_name = "Microsoft Zira Desktop"
        self.selected_voice_id = ""
        self.selected_voice_gender = "Female"
        self.current_rate = 155
        self.current_volume = 1.0
        self._use_native_sapi = False
        self._init_engine()

    def _init_engine(self):
        try:
            import pyttsx3

            # Explicitly initialize with Windows SAPI5 driver
            self.engine = pyttsx3.init("sapi5")

            # Set speech rate (155 WPM: calm, elegant, intelligent)
            desired_rate = getattr(settings, "TTS_RATE", 155) if settings else 155
            self.current_rate = desired_rate
            self.engine.setProperty("rate", desired_rate)

            # Set volume
            desired_volume = getattr(settings, "TTS_VOLUME", 1.0) if settings else 1.0
            self.current_volume = desired_volume
            self.engine.setProperty("volume", desired_volume)

            voices = self.engine.getProperty("voices")
            selected_voice = None

            # Explicitly search installed voices by name / ID for "Zira"
            for voice in voices:
                v_name = (getattr(voice, "name", "") or "").lower()
                v_id = (getattr(voice, "id", "") or "").lower()
                if "zira" in v_name or "zira" in v_id:
                    selected_voice = voice
                    break

            if selected_voice:
                self.selected_voice_name = selected_voice.name or "Microsoft Zira Desktop"
                self.selected_voice_id = selected_voice.id or ""
                self.selected_voice_gender = "Female"
                self.engine.setProperty("voice", selected_voice.id)
                try:
                    self.engine.runAndWait()
                except Exception:
                    pass

                # Check if pyttsx3 properly retained Zira or defaulted to David
                try:
                    active_id = (self.engine.getProperty("voice") or "").lower()
                    if "david" in active_id:
                        logger.warning("TTS: pyttsx3 SAPI5 reverted to David. Enabling native SAPI mode for Zira.")
                        self._use_native_sapi = True
                except Exception:
                    pass

                logger.info(
                    "TTS: Explicitly initialized Microsoft Zira female voice '%s' (ID: %s, Rate: %d WPM).",
                    self.selected_voice_name, self.selected_voice_id, self.current_rate
                )
            else:
                # Do NOT fall back to David or voices[0]. Log a clear error.
                avail_names = [getattr(v, "name", str(v)) for v in voices]
                logger.error(
                    "TTS: Microsoft Zira female voice was NOT found among installed system voices: %s. Refusing fallback to male voice.",
                    avail_names
                )
                self.selected_voice_name = "Microsoft Zira Desktop (Unavailable)"
                self.selected_voice_id = ""
                self.selected_voice_gender = "Female"

            logger.info("TTS engine initialization completed.")
        except Exception as e:
            logger.warning("pyttsx3 SAPI5 engine initialization encountered error: %s. Falling back to native SAPI.", e)
            self.engine = None
            self._use_native_sapi = True

    def _synthesize_with_sapi_native(self, text: str, wav_path: str) -> bool:
        """
        Directly uses Windows Native SAPI.SpVoice with SAPI.SpFileStream.
        Guarantees Microsoft Zira voice output even if pyttsx3 fails or overrides it.
        """
        try:
            try:
                import pythoncom
                pythoncom.CoInitialize()
            except Exception:
                pass
            import win32com.client

            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            zira_voice = None
            for v in speaker.GetVoices():
                desc = (v.GetDescription() or "").lower()
                vid = (v.Id or "").lower()
                if "zira" in desc or "zira" in vid:
                    zira_voice = v
                    break

            if not zira_voice:
                logger.error("TTS Native SAPI: Microsoft Zira voice not found in SAPI voice tokens.")
                return False

            speaker.Voice = zira_voice
            # SAPI Rate range is -10 to +10 (0 ~ 155 WPM)
            sapi_rate = max(-10, min(10, int((self.current_rate - 155) / 10)))
            speaker.Rate = sapi_rate
            speaker.Volume = max(0, min(100, int(self.current_volume * 100)))

            stream = win32com.client.Dispatch("SAPI.SpFileStream")
            stream.Open(wav_path, 3)  # 3 = SSFMCreateForWrite
            speaker.AudioOutputStream = stream
            speaker.Speak(text)
            speaker.AudioOutputStream = None
            stream.Close()
            return os.path.exists(wav_path) and os.path.getsize(wav_path) > 100
        except Exception as e:
            logger.error("TTS Native SAPI synthesis failed: %s", e, exc_info=True)
            return False

    def get_voice_info(self) -> Dict[str, Any]:
        """Returns details regarding the active TTS voice and configuration."""
        return {
            "engine": "pyttsx3 (SAPI5 / Windows Speech)" if not self._use_native_sapi else "Windows Native SAPI (SpVoice)",
            "name": self.selected_voice_name,
            "id": self.selected_voice_id,
            "gender": self.selected_voice_gender,
            "rate": self.current_rate,
            "volume": self.current_volume,
            "is_speaking": self._is_speaking
        }

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def stop(self) -> bool:
        """Immediately interrupts and halts active speech playback."""
        self._stop_requested = True
        logger.info("TTS: stop/interruption requested.")

        try:
            import sounddevice as sd
            sd.stop()
            logger.info("Active sounddevice playback stopped.")
        except Exception as e:
            logger.debug("sounddevice stop error: %s", e)

        try:
            if self.engine:
                self.engine.stop()
        except Exception as e:
            logger.debug("pyttsx3 stop error: %s", e)

        try:
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak("", 2)  # 2 = SVSFPurgeBeforeSpeak
        except Exception:
            pass

        self._is_speaking = False
        return True

    def speak(self, text: str) -> bool:
        """
        Synthesizes and speaks text directly on the physical output device.
        Guarantees:
        - Spoken using natural female voice (Microsoft Zira)
        - Never falls back to Microsoft David
        - Text sanitization for natural conversational spoken output
        - Single speaker process at a time (thread-safe lock)
        - Can be immediately cancelled via stop()
        - Waits for speech completion before returning
        """
        if not text or not text.strip():
            logger.debug("TTS: speak called with empty text.")
            return False

        spoken_text = sanitize_text_for_speech(text)
        if not spoken_text:
            return False

        with self._speaking_lock:
            self._is_speaking = True
            self._stop_requested = False
            tmp_wav = None

            try:
                try:
                    import pythoncom
                    pythoncom.CoInitialize()
                except Exception:
                    pass

                # If Zira is unavailable, refuse to speak with David
                if "unavailable" in self.selected_voice_name.lower():
                    logger.error("TTS: Refusing to speak because Microsoft Zira is unavailable and male voice fallback is disabled.")
                    self._is_speaking = False
                    return False

                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
                    tmp_wav = f.name

                synth_success = False

                # Strategy 1: Use pyttsx3 with SAPI5 if not forced to native SAPI
                if not self._use_native_sapi:
                    with self._lock:
                        if not self.engine:
                            self._init_engine()
                        if self.engine and self.selected_voice_id:
                            self.engine.setProperty("voice", self.selected_voice_id)
                            self.engine.save_to_file(spoken_text, tmp_wav)
                            self.engine.runAndWait()
                            if os.path.exists(tmp_wav) and os.path.getsize(tmp_wav) > 100:
                                synth_success = True

                # Strategy 2 (Requirement 11): Use Windows Native SAPI if pyttsx3 failed or forced David
                if not synth_success:
                    logger.info("TTS: Synthesizing speech via Windows Native SAPI with Microsoft Zira.")
                    synth_success = self._synthesize_with_sapi_native(spoken_text, tmp_wav)

                if self._stop_requested:
                    logger.info("TTS: speech aborted prior to playback.")
                    self._is_speaking = False
                    return True

                if synth_success and os.path.exists(tmp_wav) and os.path.getsize(tmp_wav) > 100:
                    import sounddevice as sd
                    import soundfile as sf
                    data, sr = sf.read(tmp_wav)
                    sd.play(data, sr)
                    # Poll while playing so stop() can break immediately
                    while sd.get_stream() and sd.get_stream().active:
                        if self._stop_requested:
                            logger.info("TTS: speech interrupted during playback.")
                            sd.stop()
                            break
                        sd.sleep(30)
                    return True
                else:
                    # Strategy 3: Direct SAPI playback with Zira if WAV file playback is unavailable
                    logger.warning("TTS: WAV file playback unavailable; speaking via direct SAPI SpVoice.")
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    zira_voice = None
                    for v in speaker.GetVoices():
                        desc = (v.GetDescription() or "").lower()
                        if "zira" in desc:
                            zira_voice = v
                            break
                    if zira_voice:
                        speaker.Voice = zira_voice
                    else:
                        logger.error("TTS direct SAPI: Zira voice not found.")
                        return False

                    sapi_rate = max(-10, min(10, int((self.current_rate - 155) / 10)))
                    speaker.Rate = sapi_rate
                    speaker.Volume = max(0, min(100, int(self.current_volume * 100)))

                    speaker.Speak(spoken_text, 1)  # 1 = SVSFlagsAsync
                    while speaker.Status.RunningState == 2:  # 2 = SPRSTextSpeaking
                        if self._stop_requested:
                            speaker.Speak("", 2)  # purge
                            break
                        time.sleep(0.03)
                    return True
            except Exception as e:
                logger.error("TTS speak error: %s", e, exc_info=True)
                return False
            finally:
                self._is_speaking = False
                if tmp_wav and os.path.exists(tmp_wav):
                    try:
                        os.remove(tmp_wav)
                    except Exception:
                        pass


tts_engine = TextToSpeechEngine()
