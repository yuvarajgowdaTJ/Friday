"""Tests for backend/voice/speech_to_text.py (mocks installed by conftest.py)."""
import importlib
import numpy as np
import pytest

import backend.voice.speech_to_text as stt_module
importlib.reload(stt_module)
from backend.voice.speech_to_text import SpeechToTextEngine
from tests.voice.conftest import STT_RETURN_TEXT, _UnknownValueError, _RequestError, _Recognizer


def test_transcribe_numpy_array_success():
    engine = SpeechToTextEngine()
    audio = np.zeros(16000, dtype=np.float32)
    result = engine.transcribe_numpy_array(audio, sample_rate=16000)
    assert result == STT_RETURN_TEXT


def test_transcribe_numpy_array_empty_returns_none():
    engine = SpeechToTextEngine()
    result = engine.transcribe_numpy_array(np.array([]), sample_rate=16000)
    assert result is None


def test_transcribe_pcm_data_success():
    engine = SpeechToTextEngine()
    pcm = np.zeros(16000, dtype=np.int16).tobytes()
    result = engine.transcribe_pcm_data(pcm, sample_rate=16000)
    assert result == STT_RETURN_TEXT


def test_transcribe_pcm_data_too_short_returns_none():
    engine = SpeechToTextEngine()
    result = engine.transcribe_pcm_data(b"\x00" * 10, sample_rate=16000)
    assert result is None


def test_transcribe_unknown_value_returns_none():
    engine = SpeechToTextEngine()

    class _Raises(_Recognizer):
        def recognize_google(self, audio, language=None):
            raise _UnknownValueError("not understood")

    engine.recognizer = _Raises()
    audio = np.zeros(16000, dtype=np.float32)
    result = engine.transcribe_numpy_array(audio, sample_rate=16000)
    assert result is None


def test_transcribe_request_error_returns_none():
    engine = SpeechToTextEngine()

    class _RaisesReq(_Recognizer):
        def recognize_google(self, audio, language=None):
            raise _RequestError("Network drop or service unreachable")

    engine.recognizer = _RaisesReq()
    audio = np.zeros(16000, dtype=np.float32)
    result = engine.transcribe_numpy_array(audio, sample_rate=16000)
    assert result is None


def test_is_stop_command():
    assert SpeechToTextEngine.is_stop_command("stop")
    assert SpeechToTextEngine.is_stop_command("FRIDAY stop talking")
    assert SpeechToTextEngine.is_stop_command("be quiet please")
    assert SpeechToTextEngine.is_stop_command("shut up")
    assert SpeechToTextEngine.is_stop_command("pause")
    assert SpeechToTextEngine.is_stop_command("cancel that")
    assert not SpeechToTextEngine.is_stop_command("What time is it in Tokyo?")
    assert not SpeechToTextEngine.is_stop_command("")
    assert not SpeechToTextEngine.is_stop_command(None)
