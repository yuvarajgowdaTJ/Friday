"""
backend/voice/wake_word.py
Wake-word and voice interruption/stop command detection for FRIDAY.
"""

import re
import logging
from typing import Optional, List

logger = logging.getLogger("FRIDAY.Voice.WakeWord")

WAKE_PHRASES = [
    "hey friday", "friday", "okay friday", "ok friday", "hello friday",
    "hey jarvis", "jarvis", "okay jarvis", "ok jarvis", "hello jarvis"
]

STOP_PHRASES = [
    "stop", "stop speaking", "stop talking", "be quiet", "shut up",
    "quiet", "silence", "pause", "cancel", "stop it", "abort", "halt"
]


class WakeWordDetector:
    def __init__(self, wake_phrases: Optional[List[str]] = None, stop_phrases: Optional[List[str]] = None):
        self.wake_phrases = [p.lower() for p in (wake_phrases or WAKE_PHRASES)]
        self.stop_phrases = [p.lower() for p in (stop_phrases or STOP_PHRASES)]

    def detect_in_text(self, text: str) -> bool:
        """Returns True if input text contains a wake phrase."""
        if not text:
            return False
        text_clean = text.strip().lower()
        for phrase in self.wake_phrases:
            pattern = rf"\b{re.escape(phrase)}\b"
            if re.search(pattern, text_clean):
                return True
        return False

    def detect_stop_command(self, text: str) -> bool:
        """Returns True if input text is or contains a stop/interruption command."""
        if not text:
            return False
        text_clean = text.strip().lower()
        for phrase in self.stop_phrases:
            pattern = rf"\b{re.escape(phrase)}\b"
            if re.search(pattern, text_clean):
                return True
        return False

    def strip_wake_word(self, text: str) -> str:
        """Removes the wake word prefix/suffix to return the clean command."""
        if not text:
            return ""
        cleaned = text.strip()
        for phrase in sorted(self.wake_phrases, key=len, reverse=True):
            cleaned = re.sub(rf"^\s*{re.escape(phrase)}[,!\.\s]*", "", cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(rf"[,!\.\s]*{re.escape(phrase)}\s*$", "", cleaned, flags=re.IGNORECASE)
        return cleaned.strip()


wake_word_detector = WakeWordDetector()
