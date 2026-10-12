"""
tests/voice/test_friday_voice_system.py
Verification suite for FRIDAY's upgraded voice system covering the 7 requested tests:
1. microphone initialization
2. speech detection
3. transcription
4. response generation
5. TTS
6. interruption
7. return to listening/idle state
"""

import sys
import importlib
import numpy as np
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.voice.microphone import (
    MicrophoneCapture,
    list_input_devices,
    get_default_input_device,
    SAMPLE_RATE,
)
from backend.voice.speech_to_text import SpeechToTextEngine
from backend.voice.text_to_speech import TextToSpeechEngine, sanitize_text_for_speech
from backend.voice.wake_word import wake_word_detector
from backend.core.agent_router import NaturalLanguageAgent
from backend.database.database import get_db
import backend.api.voice as voice_api_module
from tests.voice.conftest import DEVICE_NAME, STT_RETURN_TEXT, BLOCK_SIZE, SR, _UnknownValueError, _Recognizer


# Dummy in-memory session for database
class DummyDB:
    def add(self, obj): pass
    def commit(self): pass
    def refresh(self, obj): pass


@pytest.fixture
def api_client():
    app = FastAPI()
    app.include_router(voice_api_module.router)
    app.dependency_overrides[get_db] = lambda: DummyDB()
    return TestClient(app)


# -----------------------------------------------------------------------------
# 1. Microphone Initialization
# -----------------------------------------------------------------------------
def test_1_microphone_initialization():
    """Verify input device enumeration, default device retrieval, and stream lifecycle."""
    devices = list_input_devices()
    assert isinstance(devices, list)
    assert len(devices) > 0
    assert devices[0]["name"] == DEVICE_NAME

    default_dev = get_default_input_device()
    assert default_dev is not None
    assert default_dev["name"] == DEVICE_NAME

    mic = MicrophoneCapture()
    assert not mic.is_recording
    assert mic._device is None


# -----------------------------------------------------------------------------
# 2. Speech Detection (VAD, Silence, Timeout)
# -----------------------------------------------------------------------------
def test_2_speech_detection():
    """Verify VAD correctly triggers on speech onset and cuts off on silence."""
    mic = MicrophoneCapture()
    audio, sr = mic.record_utterance(silence_threshold=0.01, silence_cutoff_blocks=30)
    assert audio is not None
    assert isinstance(audio, np.ndarray)
    assert sr == SAMPLE_RATE
    assert len(audio) > 0


def test_2_speech_detection_silence_timeout(monkeypatch):
    """Verify recording terminates gracefully on silence and does not record indefinitely."""
    sd_mock = sys.modules["sounddevice"]

    class SilentInputStream:
        def __init__(self, *, callback, **kw):
            self._cb = callback

        def __enter__(self):
            for _ in range(20):
                self._cb(np.zeros((BLOCK_SIZE, 1), dtype=np.float32), BLOCK_SIZE, None, None)
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(sd_mock, "InputStream", SilentInputStream)
    mic = MicrophoneCapture()
    audio, sr = mic.record_utterance(
        silence_threshold=0.05,
        initial_silence_timeout=0.2  # ~6 blocks
    )
    assert audio is None
    assert sr == SAMPLE_RATE


# -----------------------------------------------------------------------------
# 3. Transcription (STT)
# -----------------------------------------------------------------------------
def test_3_transcription_success():
    """Verify transcription of captured audio array."""
    stt = SpeechToTextEngine()
    fake_audio = np.zeros(16000, dtype=np.float32)
    transcript = stt.transcribe_numpy_array(fake_audio, sample_rate=16000)
    assert transcript == STT_RETURN_TEXT


def test_3_transcription_empty_and_unintelligible():
    """Verify handling of empty audio and unrecognizable audio."""
    stt = SpeechToTextEngine()
    assert stt.transcribe_numpy_array(None) is None
    assert stt.transcribe_numpy_array(np.array([])) is None

    class UnintelligibleRecognizer(_Recognizer):
        def recognize_google(self, audio, language=None):
            raise _UnknownValueError("Not understood")

    stt.recognizer = UnintelligibleRecognizer()
    assert stt.transcribe_numpy_array(np.zeros(16000, dtype=np.float32)) is None


# -----------------------------------------------------------------------------
# 4. Response Generation (FRIDAY Router)
# -----------------------------------------------------------------------------
def test_4_response_generation():
    """Verify FRIDAY router takes user text and generates a natural response."""
    result = NaturalLanguageAgent.process_request(
        user_message="Hello FRIDAY, are you online?",
        session_id="test_session"
    )
    assert isinstance(result, dict)
    response_text = result.get("response")
    assert response_text is not None
    assert len(response_text) > 0
    assert "FRIDAY" in response_text or "online" in response_text.lower() or "sir" in response_text.lower()


# -----------------------------------------------------------------------------
# 5. Text-To-Speech (TTS)
# -----------------------------------------------------------------------------
def test_5_tts_synthesis_and_sanitization():
    """Verify TTS speech synthesis and natural markdown sanitization."""
    tts = TextToSpeechEngine()
    raw_markdown = "**Good day**, sir! Here is `var x = 10;`. Have a nice day."
    sanitized = sanitize_text_for_speech(raw_markdown)
    assert "**" not in sanitized
    assert "`" not in sanitized
    assert "Good day, sir!" in sanitized

    success = tts.speak(raw_markdown)
    assert success is True
    assert not tts.is_speaking


# -----------------------------------------------------------------------------
# 6. Interruption & Stop-Speaking Command
# -----------------------------------------------------------------------------
def test_6_interruption():
    """Verify stop() halts active TTS immediately and clears speaking state."""
    tts = TextToSpeechEngine()
    tts._is_speaking = True
    tts.stop()
    assert not tts.is_speaking
    assert tts._stop_requested is True

    # Test stop command parsing
    assert wake_word_detector.detect_stop_command("stop")
    assert wake_word_detector.detect_stop_command("FRIDAY stop talking")
    assert wake_word_detector.detect_stop_command("be quiet please")
    assert wake_word_detector.detect_stop_command("shut up")
    assert not wake_word_detector.detect_stop_command("tell me the weather")


def test_6_interruption_via_api(api_client):
    """Verify /api/voice/interrupt and /api/voice/stop endpoints."""
    res = api_client.post("/api/voice/stop")
    assert res.status_code == 200
    assert res.json()["status"] == "stopped"

    res_int = api_client.post("/api/voice/interrupt")
    assert res_int.status_code == 200
    assert res_int.json()["status"] == "stopped"


# -----------------------------------------------------------------------------
# 7. Return to Listening / Idle State
# -----------------------------------------------------------------------------
def test_7_return_to_listening_idle_state(api_client):
    """Verify voice state transitions properly return to IDLE at end of cycle."""
    # Check initial status
    status_res = api_client.get("/api/voice/status")
    assert status_res.status_code == 200
    assert status_res.json()["state"] == "IDLE"

    # Run converse pipeline cycle
    converse_res = api_client.post("/api/voice/converse", json={"speak_response": False})
    assert converse_res.status_code == 200
    data = converse_res.json()
    assert data["status"] == "success"
    assert data["transcription"] is not None
    assert data["response"] is not None

    # After cycle, state must have returned to IDLE
    final_status = api_client.get("/api/voice/status")
    assert final_status.json()["state"] == "IDLE"
