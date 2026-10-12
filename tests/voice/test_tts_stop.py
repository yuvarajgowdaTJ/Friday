"""Tests for backend/voice/text_to_speech.py (mocks installed by conftest.py)."""
import importlib
import threading
import pytest

import backend.voice.text_to_speech as tts_module
importlib.reload(tts_module)
from backend.voice.text_to_speech import TextToSpeechEngine, sanitize_text_for_speech


def test_speak_returns_true():
    engine = TextToSpeechEngine()
    result = engine.speak("Hello, FRIDAY test.")
    assert result is True


def test_stop_clears_speaking_flag():
    engine = TextToSpeechEngine()
    engine._is_speaking = True
    engine.stop()
    assert engine._is_speaking is False


def test_stop_requested_flag_set():
    engine = TextToSpeechEngine()
    engine.stop()
    assert engine._stop_requested is True


def test_speak_empty_text_returns_false():
    engine = TextToSpeechEngine()
    result = engine.speak("")
    assert result is False


def test_no_overlap_simultaneous_speak():
    """Two speak() calls must not deadlock and both must return."""
    engine = TextToSpeechEngine()
    results = []

    def do_speak():
        results.append(engine.speak("Testing overlap."))

    t1 = threading.Thread(target=do_speak)
    t2 = threading.Thread(target=do_speak)
    t1.start()
    t2.start()
    t1.join(timeout=10)
    t2.join(timeout=10)
    assert len(results) == 2


def test_sanitize_text_for_speech():
    raw = "# Title\nHere is **bold** and *italic* with `code` and ```python\nprint('hello')\n``` and [a link](https://example.com)."
    sanitized = sanitize_text_for_speech(raw)
    assert "Title" in sanitized
    assert "bold" in sanitized
    assert "italic" in sanitized
    assert "code" in sanitized
    assert "**" not in sanitized
    assert "```" not in sanitized
    assert "https://" not in sanitized
    assert "Code block omitted" in sanitized


def test_speak_error_recovers_gracefully(monkeypatch):
    engine = TextToSpeechEngine()

    def faulty_save(*args, **kwargs):
        raise RuntimeError("SAPI driver crashed")

    engine.engine.save_to_file = faulty_save
    result = engine.speak("Will fail during save")
    assert result is False
    assert not engine.is_speaking
