"""Tests for backend/voice/microphone.py (mocks installed by conftest.py)."""
import importlib
import numpy as np
import pytest
import sys

import backend.voice.microphone as mic_module
importlib.reload(mic_module)
from backend.voice.microphone import (
    MicrophoneCapture, list_input_devices, get_default_input_device
)

from tests.voice.conftest import DEVICE_NAME, BLOCK_SIZE, SR


def test_list_input_devices():
    devices = list_input_devices()
    assert isinstance(devices, list)
    assert len(devices) >= 1
    assert devices[0]["name"] == DEVICE_NAME


def test_get_default_input_device():
    dev = get_default_input_device()
    assert dev is not None
    assert dev["name"] == DEVICE_NAME


def test_record_utterance_detects_speech():
    """Mock InputStream feeds exactly 45 blocks (5 silent, 10 speech, 30 silent)."""
    cap = MicrophoneCapture()
    audio, sr = cap.record_utterance(silence_threshold=0.01, silence_cutoff_blocks=30)
    assert audio is not None, "Expected audio array but got None"
    assert isinstance(audio, np.ndarray)
    assert sr == 16000
    assert len(audio) > 0


def test_record_utterance_double_start_blocked():
    cap = MicrophoneCapture()
    cap._recording_lock.acquire()
    try:
        audio, sr = cap.record_utterance()
        assert audio is None
    finally:
        cap._recording_lock.release()


def test_stop_aborts_recording():
    cap = MicrophoneCapture()
    cap._stop_requested = False
    cap.stop()
    assert cap._stop_requested is True


def test_is_recording_property():
    cap = MicrophoneCapture()
    assert not cap.is_recording
    assert cap._recording_lock.acquire()
    assert cap.is_recording
    cap._recording_lock.release()
    assert not cap.is_recording


def test_record_utterance_initial_silence_timeout(monkeypatch):
    """When only silence is streamed, it must terminate after initial silence timeout."""
    sd_mock = sys.modules["sounddevice"]

    class SilentInputStream:
        def __init__(self, *, callback, **kw):
            self._cb = callback

        def __enter__(self):
            # Stream 25 silent blocks
            for _ in range(25):
                self._cb(np.zeros((BLOCK_SIZE, 1), dtype=np.float32), BLOCK_SIZE, None, None)
            return self

        def __exit__(self, *a):
            pass

    monkeypatch.setattr(sd_mock, "InputStream", SilentInputStream)
    cap = MicrophoneCapture()
    # 10 blocks at 512 samples / 16000 SR = ~0.32 seconds timeout
    audio, sr = cap.record_utterance(
        silence_threshold=0.05,
        initial_silence_timeout=0.32
    )
    assert audio is None
    assert sr == SR


def test_stream_init_failure_handled(monkeypatch):
    sd_mock = sys.modules["sounddevice"]

    def faulty_init(*args, **kwargs):
        raise RuntimeError("PortAudio device unavailable")

    monkeypatch.setattr(sd_mock, "InputStream", faulty_init)
    cap = MicrophoneCapture()
    audio, sr = cap.record_utterance()
    assert audio is None
    assert not cap.is_recording
