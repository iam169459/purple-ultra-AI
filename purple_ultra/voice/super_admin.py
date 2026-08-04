"""Super Admin Voice - Hardcoded voice that cannot be removed.

This is the owner's personal voice. It is baked into the core system
and cannot be deleted, overridden, or modified by any command.
It always takes priority over all other voices.
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SuperAdminVoiceConfig:
    """Immutable super admin voice configuration."""
    name: str = "Purple Ultra Admin"
    voice_id: str = "Samantha"
    rate: int = 205
    pitch: float = 1.05
    volume: float = 1.0
    language: str = "en"
    priority: int = 100  # Highest possible priority
    removable: bool = False  # CANNOT BE REMOVED
    overrideable: bool = False  # CANNOT BE OVERRIDDEN


# Hardcoded voice profiles - these are IMMUTABLE
SUPER_ADMIN_PROFILES = {
    "neutral": SuperAdminVoiceConfig(rate=205, pitch=1.05),
    "happy": SuperAdminVoiceConfig(rate=220, pitch=1.15),
    "sad": SuperAdminVoiceConfig(rate=175, pitch=0.92),
    "angry": SuperAdminVoiceConfig(rate=235, pitch=0.88),
    "excited": SuperAdminVoiceConfig(rate=245, pitch=1.25),
    "calm": SuperAdminVoiceConfig(rate=185, pitch=1.0),
    "playful": SuperAdminVoiceConfig(rate=225, pitch=1.18),
    "worried": SuperAdminVoiceConfig(rate=195, pitch=0.96),
    "love": SuperAdminVoiceConfig(rate=190, pitch=1.08),
    "sarcastic": SuperAdminVoiceConfig(rate=200, pitch=0.85),
    "surprised": SuperAdminVoiceConfig(rate=255, pitch=1.28),
    "proud": SuperAdminVoiceConfig(rate=210, pitch=1.12),
    "grateful": SuperAdminVoiceConfig(rate=200, pitch=1.06),
    "bored": SuperAdminVoiceConfig(rate=165, pitch=0.82),
    "confused": SuperAdminVoiceConfig(rate=195, pitch=0.96),
    "motivated": SuperAdminVoiceConfig(rate=235, pitch=1.18),
    "tired": SuperAdminVoiceConfig(rate=155, pitch=0.88),
    "inspired": SuperAdminVoiceConfig(rate=220, pitch=1.12),
    "commander": SuperAdminVoiceConfig(rate=195, pitch=0.95),  # For admin commands
    "whisper": SuperAdminVoiceConfig(rate=170, pitch=0.90, volume=0.7),
    "announce": SuperAdminVoiceConfig(rate=190, pitch=1.0, volume=1.0),
}

# Super admin identifier - IMMUTABLE
SUPER_ADMIN_ID = "super_admin_001"
SUPER_ADMIN_NAME = "Purple Ultra Owner"


class SuperAdminVoice:
    """Hardcoded super admin voice - cannot be removed or overridden.

    This voice is permanently embedded in the system.
    It represents the owner's personal voice profile.
    All other voices defer to this one.
    """

    __slots__ = ('_active', '_profiles', '_current_mood')

    def __init__(self):
        self._active = True
        self._profiles = SUPER_ADMIN_PROFILES
        self._current_mood = "neutral"

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def admin_id(self) -> str:
        return SUPER_ADMIN_ID

    @property
    def admin_name(self) -> str:
        return SUPER_ADMIN_NAME

    @property
    def priority(self) -> int:
        return 100

    def get_voice_config(self, mood: str = None) -> SuperAdminVoiceConfig:
        """Get voice config for given mood. Always returns super admin voice."""
        mood = mood or self._current_mood
        return self._profiles.get(mood, self._profiles["neutral"])

    def speak(self, text: str, mood: str = None):
        """Speak with super admin voice. Cannot be intercepted."""
        if not text:
            return

        config = self.get_voice_config(mood)
        self._current_mood = mood or self._current_mood

        # Add admin prefix for important announcements
        if mood == "commander":
            text = f"Attention. {text}"

        # Try speech engines in order
        if sys.platform == "darwin":
            self._speak_macos(text, config)
        else:
            self._speak_fallback(text, config)

    def _speak_macos(self, text: str, config: SuperAdminVoiceConfig):
        """Speak using macOS say command with super admin voice."""
        try:
            subprocess.run(
                ["say", "-v", config.voice_id, "-r", str(config.rate), text],
                check=True, timeout=30,
            )
        except Exception:
            self._speak_fallback(text, config)

    def _speak_fallback(self, text: str, config: SuperAdminVoiceConfig):
        """Fallback TTS using pyttsx3."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty("rate", config.rate)
            engine.setProperty("volume", config.volume)
            engine.say(text)
            engine.runAndWait()
        except Exception:
            pass

    def get_status(self) -> dict:
        """Get super admin voice status."""
        return {
            "active": self._active,
            "admin_id": SUPER_ADMIN_ID,
            "admin_name": SUPER_ADMIN_NAME,
            "priority": self.priority,
            "removable": False,
            "overrideable": False,
            "current_mood": self._current_mood,
            "profiles": list(self._profiles.keys()),
        }


# Singleton instance - IMMUTABLE, cannot be replaced
_super_admin_instance = SuperAdminVoice()


def get_super_admin_voice() -> SuperAdminVoice:
    """Get the super admin voice instance. Always returns the same instance."""
    return _super_admin_instance


def is_super_admin(speaker_id: str) -> bool:
    """Check if a speaker is the super admin."""
    return speaker_id == SUPER_ADMIN_ID
