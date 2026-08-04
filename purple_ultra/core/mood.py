"""Mood system with persistent state and voice mapping."""

from __future__ import annotations

import json
import time
from pathlib import Path

from ..config.settings import MoodConfig


class MoodState:
    """Manages mood state with persistence and transitions."""

    VALID_MOODS = [
        "neutral", "happy", "sad", "angry", "excited", "calm",
        "playful", "worried", "love", "sarcastic", "surprised",
        "proud", "grateful", "bored", "confused", "motivated",
        "tired", "inspired",
    ]

    TRANSITIONS = {
        "neutral": {"happy", "sad", "calm", "worried", "confused"},
        "happy": {"excited", "playful", "love", "proud", "grateful", "neutral"},
        "sad": {"worried", "neutral", "tired"},
        "angry": {"calm", "neutral", "worried"},
        "excited": {"happy", "playful", "proud", "neutral"},
        "calm": {"neutral", "happy", "inspired", "grateful"},
        "playful": {"happy", "excited", "sarcastic", "love"},
        "worried": {"calm", "neutral", "confused"},
        "love": {"happy", "calm", "playful", "grateful"},
        "sarcastic": {"bored", "amused", "neutral"},
        "surprised": {"excited", "confused", "happy"},
        "proud": {"happy", "motivated", "neutral"},
        "grateful": {"happy", "calm", "love"},
        "bored": {"neutral", "tired", "confused"},
        "confused": {"neutral", "worried", "calm"},
        "motivated": {"excited", "proud", "inspired"},
        "tired": {"neutral", "bored", "sad"},
        "inspired": {"excited", "motivated", "happy"},
    }

    def __init__(self, config: MoodConfig, memory_dir: str = "memory"):
        self.config = config
        self._current = config.default
        self._mood_file = Path(memory_dir) / "mood.json"
        self._mood_history: list[dict] = []
        self._load()

    def _load(self):
        if self._mood_file.exists():
            try:
                data = json.loads(self._mood_file.read_text())
                mood = data.get("mood", self.config.default)
                if mood in self.VALID_MOODS:
                    self._current = mood
                self._mood_history = data.get("history", [])
            except Exception:
                pass

    def _save(self):
        try:
            self._mood_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "mood": self._current,
                "timestamp": time.time(),
                "history": self._mood_history[-50:],
            }
            self._mood_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def current(self) -> str:
        return self._current

    def set(self, mood: str, reason: str = "") -> str:
        mood = mood.lower().strip()
        if mood not in self.VALID_MOODS:
            mood = self.config.default

        if mood != self._current:
            self._mood_history.append({
                "from": self._current,
                "to": mood,
                "reason": reason,
                "timestamp": time.time(),
            })
            self._current = mood
            self._save()

        return self._current

    def voice_for(self, mood: str = None) -> dict:
        mood = mood or self._current
        if mood in self.config.voices:
            vc = self.config.voices[mood]
            return {"name": vc.name, "rate": vc.rate, "pitch": vc.pitch, "volume": vc.volume}
        default = self.config.voices.get(self.config.default)
        if default:
            return {"name": default.name, "rate": default.rate, "pitch": default.pitch, "volume": default.volume}
        return {"name": "Samantha", "rate": 200, "pitch": 1.0, "volume": 0.9}

    def transition_suggest(self, context: str = "") -> str:
        """Suggest a natural mood transition based on context."""
        candidates = self.TRANSITIONS.get(self._current, {"neutral"})
        if not candidates:
            return self._current
        context_lower = context.lower()
        mood_keywords = {
            "happy": ["great", "awesome", "love", "wonderful", "nice", "perfect"],
            "sad": ["sad", "sorry", "unfortunately", "bad", "terrible"],
            "angry": ["angry", "frustrated", "annoyed", "hate", "stupid"],
            "excited": ["wow", "amazing", "incredible", "fantastic", "yes"],
            "calm": ["okay", "fine", "alright", "sure", "relax"],
            "worried": ["worried", "concerned", "afraid", "nervous", "scared"],
            "confused": ["confused", "unclear", "huh", "what", "don't understand"],
        }
        for mood, keywords in mood_keywords.items():
            if mood in candidates and any(k in context_lower for k in keywords):
                return mood
        return self._current

    def get_history(self, count: int = 10) -> list[dict]:
        return self._mood_history[-count:]

    def decay_to_neutral(self, steps: int = 1):
        """Gradually decay mood toward neutral."""
        if self._current == "neutral":
            return
        for _ in range(steps):
            if self._current in self.TRANSITIONS.get("neutral", set()):
                self._current = "neutral"
                self._save()
                return
