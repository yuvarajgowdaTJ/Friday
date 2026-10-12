"""
conftest.py for tests/voice/

Installs module-level mocks into sys.modules BEFORE any backend.voice module
is imported. This prevents test cross-contamination when pytest runs all test
files in the same process.
"""
import sys
import wave
import numpy as np


# ─────────────────────────────────────────────────────────────────────────────
# Shared constants
# ─────────────────────────────────────────────────────────────────────────────
DEVICE_NAME = "Fake Microphone"
STT_RETURN_TEXT = "calculate three divided by three"
BLOCK_SIZE = 512
SR = 16000


# ─────────────────────────────────────────────────────────────────────────────
# sounddevice mock — must have play(), stop(), get_stream(), sleep(), InputStream
# ─────────────────────────────────────────────────────────────────────────────
class _SD:
    class default:
        device = [1, 4]

    @staticmethod
    def query_devices(idx=None):
        d = {
            "name": DEVICE_NAME,
            "max_input_channels": 2,
            "max_output_channels": 0,
            "default_samplerate": SR,
        }
        return d if idx is not None else [d, d]

    @staticmethod
    def play(data, sr):
        pass

    @staticmethod
    def stop():
        pass

    @staticmethod
    def get_stream():
        # Return None → "no active stream" so the polling loop in speak() exits
        return None

    @staticmethod
    def sleep(ms):
        import time
        time.sleep(ms / 1000)

    class InputStream:
        """
        Feeds exactly 45 synthetic audio blocks via callback during __enter__:
          - 5  silent blocks  (pre-speech)
          - 10 speech blocks  (RMS > 0.05 → triggers speech_started)
          - 30 silent blocks  (exactly SILENCE_BLOCKS_CUTOFF → VAD exits)
        Total: 45 blocks → queue is drained and loop exits cleanly, no timeout.
        """
        def __init__(self, *, callback, device=None, samplerate=SR,
                     channels=1, dtype="float32", blocksize=BLOCK_SIZE, **kw):
            self._cb = callback
            self._blocksize = blocksize

        def __enter__(self):
            rng = np.random.default_rng(42)
            for i in range(45):
                if 5 <= i < 15:
                    block = rng.uniform(0.05, 0.2, (self._blocksize, 1)).astype("float32")
                else:
                    block = np.zeros((self._blocksize, 1), dtype="float32")
                self._cb(block, self._blocksize, None, None)
            return self

        def __exit__(self, *a):
            pass


# ─────────────────────────────────────────────────────────────────────────────
# soundfile mock
# ─────────────────────────────────────────────────────────────────────────────
class _SF:
    @staticmethod
    def read(path):
        return np.zeros(SR, dtype="float32"), SR


# ─────────────────────────────────────────────────────────────────────────────
# pyttsx3 mock
# ─────────────────────────────────────────────────────────────────────────────
class _Voice:
    def __init__(self, name, vid, gender="Female"):
        self.name = name
        self.id = vid
        self.gender = gender


class _Engine:
    def __init__(self):
        self._voice = "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0"
        self._rate = 155
        self._volume = 1.0
        self._voices = [
            _Voice("Microsoft Zira Desktop - English (United States)", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0", "Female"),
            _Voice("Microsoft David Desktop - English (United States)", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_DAVID_11.0", "Male")
        ]

    def getProperty(self, name):
        if name == "rate": return self._rate
        if name == "volume": return self._volume
        if name == "voice": return self._voice
        if name == "voices": return self._voices
        return []

    def setProperty(self, name, value):
        if name == "rate": self._rate = value
        elif name == "volume": self._volume = value
        elif name == "voice": self._voice = value

    def save_to_file(self, text, path):
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SR)
            wf.writeframes(b"\x00" * (SR * 2))   # 1 second, > 100 bytes
    def runAndWait(self): pass
    def stop(self): pass
    def say(self, text): pass


class _Pyttsx3:
    @staticmethod
    def init():
        return _Engine()


# ─────────────────────────────────────────────────────────────────────────────
# speech_recognition mock
# ─────────────────────────────────────────────────────────────────────────────
class _UnknownValueError(Exception): pass
class _RequestError(Exception): pass


class _Recognizer:
    energy_threshold = 300
    dynamic_energy_threshold = True
    def record(self, src): return object()
    def recognize_google(self, audio, language=None): return STT_RETURN_TEXT


class _AudioFile:
    def __init__(self, src): pass
    def __enter__(self): return self
    def __exit__(self, *a): pass


class _SR:
    Recognizer = _Recognizer
    AudioFile = _AudioFile
    UnknownValueError = _UnknownValueError
    RequestError = _RequestError


# ─────────────────────────────────────────────────────────────────────────────
# Install mocks into sys.modules
# ─────────────────────────────────────────────────────────────────────────────
sys.modules["sounddevice"]        = _SD()       # type: ignore
sys.modules["soundfile"]          = _SF()        # type: ignore
sys.modules["pyttsx3"]            = _Pyttsx3()   # type: ignore
sys.modules["speech_recognition"] = _SR()        # type: ignore

# Force-reload all backend.voice modules so they pick up the mocks
import importlib
_voice_mods = [
    "backend.voice.microphone",
    "backend.voice.speech_to_text",
    "backend.voice.text_to_speech",
    "backend.voice.wake_word",
    "backend.api.voice",
]
for _m in _voice_mods:
    if _m in sys.modules:
        importlib.reload(sys.modules[_m])
