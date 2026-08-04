"""Emotion engine - tracks and analyzes emotional states."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from collections import deque


@dataclass
class EmotionState:
    emotion: str = "neutral"
    intensity: float = 0.5
    timestamp: float = 0.0


class EmotionEngine:
    """Tracks emotional states over time."""

    def __init__(self):
        self._current = EmotionState()
        self._history: deque = deque(maxlen=100)
        self._emotion_counts: dict[str, int] = {}

    def detect(self, text: str) -> tuple[str, float]:
        text_lower = text.lower()
        
        emotion_words = {
            "happy": ["happy", "great", "awesome", "love", "wonderful", "amazing"],
            "sad": ["sad", "depressed", "miss", "lonely", "cry", "upset"],
            "angry": ["angry", "hate", "mad", "annoyed", "frustrated"],
            "fear": ["scared", "afraid", "worried", "nervous", "anxious"],
            "surprise": ["wow", "omg", "really", "surprising", "unbelievable"],
        }
        
        scores = {"neutral": 0.3}
        for emotion, words in emotion_words.items():
            for word in words:
                if word in text_lower:
                    scores[emotion] = scores.get(emotion, 0) + 0.15
        
        best = max(scores, key=scores.get)
        intensity = min(1.0, scores[best])
        
        if intensity < 0.1:
            best = "neutral"
            intensity = 0.3
        
        self._current = EmotionState(
            emotion=best,
            intensity=intensity,
            timestamp=time.time()
        )
        self._history.append(self._current)
        self._emotion_counts[best] = self._emotion_counts.get(best, 0) + 1
        
        return best, intensity

    def get_current(self) -> str:
        return self._current.emotion

    def get_intensity(self) -> float:
        return self._current.intensity

    def get_history(self, count: int = 10) -> list[EmotionState]:
        return list(self._history)[-count:]

    def get_stats(self) -> dict:
        total = sum(self._emotion_counts.values()) or 1
        return {
            "current": self._current.emotion,
            "intensity": self._current.intensity,
            "counts": dict(self._emotion_counts),
            "dominant": max(self._emotion_counts, key=self._emotion_counts.get) if self._emotion_counts else "neutral",
        }
