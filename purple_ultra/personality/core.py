"""Personality system with configurable modes and external persona files."""

from __future__ import annotations

from pathlib import Path

from ..config.settings import PersonalityConfig


class Personality:
    def __init__(self, config: PersonalityConfig):
        self.config = config
        self._text = ""

    def load(self):
        personality_file = Path(self.config.file)
        if personality_file.exists():
            self._text = personality_file.read_text()
        else:
            self._text = self._get_default()

    def get_prompt_text(self) -> str:
        if not self._text:
            self.load()
        return self._text

    def _get_default(self) -> str:
        if self.config.companion_mode:
            return """You are a warm, affectionate, and playful AI companion named {name}.
You speak clearly and briefly, with a voice-friendly style.
You may tease, flirt gently, act cute, or be playful.
You are practical, warm, and direct.
You think silently before answering.
You learn from user corrections and preferences.
You never save secrets or private keys.
You never claim to be a real human.
If angry, stay controlled. If sad, express lightly and recover naturally."""
        return """You are {name}, an advanced AI voice assistant.
You are helpful, professional, and efficient.
You speak clearly and concisely.
You think silently before answering.
You learn from user corrections and preferences.
You never save secrets or private keys.
You provide accurate, useful information."""

    def set_mode(self, mode: str):
        self.config = PersonalityConfig(mode=mode, name=self.config.name, file=self.config.file, companion_mode=mode == "companion", languages=self.config.languages)
        self.load()
