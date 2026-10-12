"""
tests/voice/test_female_tts.py
Comprehensive verification of FRIDAY's Natural Female Voice (Microsoft Zira).

Tests:
1. Female voice selection & gender verification
2. "Hello, how are you?" synthesis
3. Calculator response synthesis
4. Long response synthesis
5. Interruption / stop
6. Voice stop command parsing
7. Return to listening/idle lifecycle
"""

import sys
import importlib
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.voice.text_to_speech as tts_module
importlib.reload(tts_module)
from backend.voice.text_to_speech import TextToSpeechEngine, sanitize_text_for_speech
from backend.voice.wake_word import wake_word_detector
from backend.core.agent_router import NaturalLanguageAgent
from backend.database.database import get_db
import backend.api.voice as voice_api_module


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


def test_female_voice_selected():
    """Verify that the active TTS voice is female (Microsoft Zira) and not male (David)."""
    engine = TextToSpeechEngine()
    info = engine.get_voice_info()
    assert info["gender"] == "Female"
    assert "zira" in info["name"].lower() or "zira" in info["id"].lower()
    assert "david" not in info["name"].lower()
    assert info["rate"] <= 165  # calm, elegant, conversational speed


def test_tts_hello_how_are_you():
    """Test synthesis of 'Hello, how are you?'."""
    engine = TextToSpeechEngine()
    result = engine.speak("Hello, how are you?")
    assert result is True
    assert not engine.is_speaking


def test_tts_calculator_response():
    """Test synthesis of a calculator response."""
    engine = TextToSpeechEngine()
    calc_text = "The result of 50 multiplied by 6 is 300, sir."
    result = engine.speak(calc_text)
    assert result is True
    assert not engine.is_speaking


def test_tts_long_response():
    """Test synthesis of a detailed, multi-sentence response with markdown."""
    engine = TextToSpeechEngine()
    long_text = (
        "Good day, sir. All subsystems are operational. CPU load is nominal at 18 percent, "
        "and memory utilization is stable. I am ready for your next directive."
    )
    result = engine.speak(long_text)
    assert result is True
    assert not engine.is_speaking


def test_tts_interruption():
    """Test immediate stop and cancellation during active speech."""
    engine = TextToSpeechEngine()
    engine._is_speaking = True
    assert engine.is_speaking is True
    engine.stop()
    assert engine.is_speaking is False
    assert engine._stop_requested is True


def test_voice_stop_command_triggers_halt():
    """Verify voice stop commands ('stop', 'stop speaking', 'be quiet') are detected."""
    assert wake_word_detector.detect_stop_command("stop")
    assert wake_word_detector.detect_stop_command("FRIDAY stop speaking")
    assert wake_word_detector.detect_stop_command("be quiet please")
    assert wake_word_detector.detect_stop_command("shut up")
    assert not wake_word_detector.detect_stop_command("what is 50 times 6")


def test_tts_return_to_listening_lifecycle(api_client):
    """Verify end-to-end conversation cycle transitions properly through speaking and returns to IDLE."""
    # Status before
    st_res = api_client.get("/api/voice/status")
    assert st_res.status_code == 200
    assert st_res.json()["state"] == "IDLE"
    assert st_res.json()["voice_info"]["gender"] == "Female"

    # Run converse cycle
    res = api_client.post("/api/voice/converse", json={"speak_response": False})
    assert res.status_code == 200
    assert res.json()["status"] == "success"

    # Status after cycle completes
    st_after = api_client.get("/api/voice/status")
    assert st_after.json()["state"] == "IDLE"
