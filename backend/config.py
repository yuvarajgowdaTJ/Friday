import os
from pathlib import Path
from pydantic_settings import BaseSettings

# Project Directories
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
SCREENSHOTS_DIR = BASE_DIR / "screenshots"

DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
SCREENSHOTS_DIR.mkdir(exist_ok=True)

class Settings(BaseSettings):
    JARVIS_NAME: str = "FRIDAY"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    JARVIS_PORT: int = 8000
    HOST: str = "127.0.0.1"
    DATABASE_URL: str = f"sqlite:///{DATA_DIR / 'jarvis.db'}"
    LOG_LEVEL: str = "INFO"
    ENABLE_VOICE: bool = True
    ENABLE_VISION: bool = True
    SAFE_MODE: bool = True
    # Stage 2: voice pipeline flags
    VOICE_CONTINUOUS: bool = True          # auto-restart listening after each response
    VOICE_WAKEWORD_ONLY: bool = False      # require "FRIDAY" before listening
    VOICE_RECORDING_TIMEOUT: float = 15.0  # max seconds per utterance (avoid recording indefinitely)
    VOICE_INITIAL_SILENCE_TIMEOUT: float = 5.0 # max seconds waiting for initial speech
    VOICE_SILENCE_CUTOFF: float = 1.2      # seconds of silence to detect end-of-speech
    VOICE_RMS_THRESHOLD: float = 0.015     # VAD RMS energy threshold for speech
    FRIDAY_TTS_VOICE: str = os.getenv("FRIDAY_TTS_VOICE", "HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Speech\\Voices\\Tokens\\TTS_MS_EN-US_ZIRA_11.0") # Configurable female voice ID
    TTS_VOICE_PREFERENCE: str = "zira,heera,female,eva,hazel,jenny,aria" # preferred natural female TTS voices
    TTS_RATE: int = 155                    # Natural, calm conversational pace (words per minute)
    TTS_VOLUME: float = 1.0                # TTS volume (0.0 to 1.0)

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
