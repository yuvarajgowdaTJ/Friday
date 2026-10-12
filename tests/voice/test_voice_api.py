"""Integration tests for backend/api/voice.py (mocks installed by conftest.py)."""
import importlib
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

import backend.api.voice as voice_api_module
importlib.reload(voice_api_module)
from backend.database.database import get_db

app = FastAPI()
app.include_router(voice_api_module.router)

# Dummy in-memory session for converse endpoint in test
class DummyDB:
    def add(self, obj): pass
    def commit(self): pass
    def refresh(self, obj): pass

app.dependency_overrides[get_db] = lambda: DummyDB()
client = TestClient(app)


def test_get_voice_status():
    res = client.get("/api/voice/status")
    assert res.status_code == 200
    data = res.json()
    assert "state" in data
    assert "enable_voice" in data
    assert "recording_timeout" in data
    assert "initial_silence_timeout" in data


def test_get_voice_devices():
    res = client.get("/api/voice/devices")
    assert res.status_code == 200
    data = res.json()
    assert "devices" in data
    assert isinstance(data["devices"], list)


def test_post_speak_async():
    res = client.post("/api/voice/speak", json={"text": "Hello sir.", "async_speak": True})
    assert res.status_code == 200
    assert res.json()["status"] == "speaking_queued"


def test_post_speak_sync():
    res = client.post("/api/voice/speak", json={"text": "Hello sir.", "async_speak": False})
    assert res.status_code == 200
    assert res.json()["status"] == "completed"


def test_post_speak_empty_text():
    res = client.post("/api/voice/speak", json={"text": "", "async_speak": False})
    assert res.status_code == 400


def test_post_stop():
    res = client.post("/api/voice/stop")
    assert res.status_code == 200
    assert res.json()["status"] == "stopped"


def test_post_interrupt():
    res = client.post("/api/voice/interrupt")
    assert res.status_code == 200
    assert res.json()["status"] == "stopped"


def test_wake_check_positive():
    res = client.post("/api/voice/wake-check", json={"text": "Hey FRIDAY, what time is it?"})
    assert res.status_code == 200
    assert res.json()["wake_word_detected"] is True
    assert res.json()["phrase"] == "FRIDAY"


def test_wake_check_stop_command():
    res = client.post("/api/voice/wake-check", json={"text": "FRIDAY please stop talking"})
    assert res.status_code == 200
    assert res.json()["is_stop_command"] is True


def test_wake_check_negative():
    res = client.post("/api/voice/wake-check", json={"text": "open Chrome"})
    assert res.status_code == 200
    assert res.json()["wake_word_detected"] is False
    assert res.json()["is_stop_command"] is False


def test_post_listen():
    res = client.post("/api/voice/listen")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["transcription"] is not None


def test_post_converse_success():
    res = client.post("/api/voice/converse", json={"speak_response": False})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["transcription"] is not None
    assert data["response"] is not None
