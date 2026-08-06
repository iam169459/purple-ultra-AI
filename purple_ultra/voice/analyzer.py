"""Voice emotion analyzer - detects feelings from voice characteristics."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np


@dataclass
class VoiceEmotion:
    """Detected emotion from voice analysis."""
    primary: str = "neutral"
    confidence: float = 0.0
    secondary: str = "neutral"
    valence: float = 0.0  # -1 (negative) to 1 (positive)
    arousal: float = 0.0  # -1 (calm) to 1 (excited)
    dominance: float = 0.0  # -1 (submissive) to 1 (dominant)
    energy: float = 0.0
    pitch_avg: float = 0.0
    pitch_var: float = 0.0
    speaking_rate: float = 0.0
    emotions: dict[str, float] = field(default_factory=dict)

    def __str__(self):
        return f"{self.primary} ({self.confidence:.0%})"

    def to_dict(self) -> dict:
        return {
            "primary": self.primary,
            "confidence": round(self.confidence, 3),
            "secondary": self.secondary,
            "valence": round(self.valence, 3),
            "arousal": round(self.arousal, 3),
            "dominance": round(self.dominance, 3),
            "energy": round(self.energy, 3),
            "pitch_avg": round(self.pitch_avg, 2),
            "pitch_var": round(self.pitch_var, 3),
            "speaking_rate": round(self.speaking_rate, 2),
            "emotions": {k: round(v, 3) for k, v in self.emotions.items()},
        }


class VoiceAnalyzer:
    """Analyzes voice characteristics to detect emotions and feelings."""

    EMOTION_PROFILES = {
        "happy": {
            "valence": (0.4, 1.0),
            "arousal": (0.2, 0.8),
            "dominance": (0.3, 0.8),
            "pitch_range": (0.9, 1.3),
            "energy_range": (0.5, 1.0),
            "zcr_range": (0.3, 0.8),
        },
        "sad": {
            "valence": (-1.0, -0.3),
            "arousal": (-0.8, -0.2),
            "dominance": (-0.7, -0.2),
            "pitch_range": (0.7, 0.95),
            "energy_range": (0.1, 0.4),
            "zcr_range": (0.1, 0.4),
        },
        "angry": {
            "valence": (-0.8, -0.2),
            "arousal": (0.5, 1.0),
            "dominance": (0.5, 1.0),
            "pitch_range": (1.0, 1.5),
            "energy_range": (0.7, 1.0),
            "zcr_range": (0.5, 0.9),
        },
        "fear": {
            "valence": (-0.9, -0.3),
            "arousal": (0.4, 0.9),
            "dominance": (-0.9, -0.3),
            "pitch_range": (1.1, 1.6),
            "energy_range": (0.4, 0.8),
            "zcr_range": (0.4, 0.8),
        },
        "surprise": {
            "valence": (0.1, 0.8),
            "arousal": (0.5, 1.0),
            "dominance": (0.0, 0.5),
            "pitch_range": (1.2, 1.8),
            "energy_range": (0.6, 1.0),
            "zcr_range": (0.5, 0.9),
        },
        "calm": {
            "valence": (-0.1, 0.3),
            "arousal": (-0.8, -0.3),
            "dominance": (-0.2, 0.3),
            "pitch_range": (0.8, 1.0),
            "energy_range": (0.2, 0.5),
            "zcr_range": (0.2, 0.5),
        },
        "excited": {
            "valence": (0.5, 1.0),
            "arousal": (0.6, 1.0),
            "dominance": (0.4, 0.9),
            "pitch_range": (1.1, 1.6),
            "energy_range": (0.7, 1.0),
            "zcr_range": (0.5, 0.9),
        },
        "tired": {
            "valence": (-0.3, 0.1),
            "arousal": (-1.0, -0.5),
            "dominance": (-0.5, -0.1),
            "pitch_range": (0.6, 0.9),
            "energy_range": (0.05, 0.3),
            "zcr_range": (0.05, 0.3),
        },
        "frustrated": {
            "valence": (-0.7, -0.2),
            "arousal": (0.3, 0.7),
            "dominance": (-0.3, 0.3),
            "pitch_range": (0.9, 1.2),
            "energy_range": (0.5, 0.8),
            "zcr_range": (0.4, 0.7),
        },
        "confused": {
            "valence": (-0.3, 0.2),
            "arousal": (0.0, 0.5),
            "dominance": (-0.4, 0.1),
            "pitch_range": (0.9, 1.2),
            "energy_range": (0.3, 0.6),
            "zcr_range": (0.3, 0.6),
        },
        "bored": {
            "valence": (-0.4, 0.0),
            "arousal": (-0.9, -0.4),
            "dominance": (-0.4, 0.0),
            "pitch_range": (0.7, 0.95),
            "energy_range": (0.1, 0.35),
            "zcr_range": (0.1, 0.35),
        },
        "anxious": {
            "valence": (-0.7, -0.2),
            "arousal": (0.3, 0.8),
            "dominance": (-0.7, -0.2),
            "pitch_range": (1.0, 1.4),
            "energy_range": (0.4, 0.7),
            "zcr_range": (0.4, 0.7),
        },
        "confident": {
            "valence": (0.2, 0.7),
            "arousal": (0.1, 0.5),
            "dominance": (0.5, 1.0),
            "pitch_range": (0.85, 1.1),
            "energy_range": (0.5, 0.8),
            "zcr_range": (0.3, 0.6),
        },
        "neutral": {
            "valence": (-0.2, 0.2),
            "arousal": (-0.3, 0.3),
            "dominance": (-0.2, 0.2),
            "pitch_range": (0.85, 1.15),
            "energy_range": (0.3, 0.6),
            "zcr_range": (0.2, 0.5),
        },
    }

    SPEECH_RATE_THRESHOLDS = {
        "very_slow": 2.0,
        "slow": 3.5,
        "normal": 5.0,
        "fast": 7.0,
        "very_fast": 9.0,
    }

    def __init__(self, sample_rate: int = 16000):
        self.sample_rate = sample_rate
        self._history: list[VoiceEmotion] = []
        self._max_history = 50

    def analyze_audio(self, audio: np.ndarray) -> VoiceEmotion:
        """Analyze raw audio waveform and detect emotion."""
        if audio is None or len(audio) < 100:
            return VoiceEmotion()

        features = self._extract_features(audio)
        emotion = self._classify_emotion(features)
        self._history.append(emotion)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        return emotion

    def analyze_voiceprint(self, voiceprint: list[float]) -> VoiceEmotion:
        """Analyze a pre-extracted voiceprint for emotion."""
        if not voiceprint or len(voiceprint) < 7:
            return VoiceEmotion()

        rms = voiceprint[0]
        zcr = voiceprint[1]
        spectral_centroid = voiceprint[2] * 1000
        spectral_spread = voiceprint[3] * 1000
        low_ratio = voiceprint[4]
        mid_ratio = voiceprint[5]
        high_ratio = voiceprint[6]

        energy = min(1.0, rms * 10)
        zcr_norm = min(1.0, zcr * 2)
        pitch_proxy = spectral_centroid / 500

        features = {
            "energy": energy,
            "zcr": zcr_norm,
            "pitch_proxy": pitch_proxy,
            "spectral_spread": min(1.0, spectral_spread / 2000),
            "low_ratio": low_ratio,
            "mid_ratio": mid_ratio,
            "high_ratio": high_ratio,
        }

        emotion = self._classify_emotion(features)
        self._history.append(emotion)
        if len(self._history) > self._max_history:
            self._history.pop(0)
        return emotion

    def analyze_text_sentiment(self, text: str) -> VoiceEmotion:
        """Analyze text for emotional cues (supplements voice analysis)."""
        text_lower = text.lower()
        scores = {e: 0.0 for e in self.EMOTION_PROFILES}

        emotion_words = {
            "happy": ["happy", "great", "awesome", "love", "wonderful", "amazing", "excellent", "fantastic", "glad", "joy", "smile", "laugh", "yay", "woo"],
            "sad": ["sad", "unhappy", "depressed", "miserable", "terrible", "awful", "horrible", "worst", "cry", "tears", "upset", "heartbroken", "lonely"],
            "angry": ["angry", "mad", "furious", "rage", "hate", "annoyed", "irritated", "frustrated", "pissed", "damn", "stupid", "idiot"],
            "fear": ["scared", "afraid", "terrified", "frightened", "worried", "anxious", "nervous", "panic", "fear", "dread", "uneasy"],
            "surprise": ["wow", "whoa", "omg", "really", "seriously", "no way", "unbelievable", "incredible", "shocked", "astonished"],
            "excited": ["excited", "pumped", "stoked", "thrilled", "ecstatic", "can't wait", "yay", "woo", "awesome", "amazing"],
            "tired": ["tired", "exhausted", "sleepy", "yawn", "drained", "worn out", "beat", "fatigued", "rest", "nap"],
            "confused": ["confused", "confusing", "unclear", "don't understand", "lost", "complicated", "complex", "what", "huh"],
            "bored": ["bored", "boring", "dull", "monotonous", "tedious", "nothing to do", "yawn"],
            "confident": ["sure", "definitely", "absolutely", "certain", "know", "guarantee", "promise", "without doubt"],
            "frustrated": ["frustrated", "stuck", "can't", "impossible", "difficult", "hard", "struggling", "ugh", "argh"],
        }

        for emotion, words in emotion_words.items():
            for word in words:
                if word in text_lower:
                    scores[emotion] += 0.2

        negation_words = ["not", "no", "never", "don't", "can't", "won't", "isn't", "aren't"]
        has_negation = any(w in text_lower for w in negation_words)
        if has_negation:
            scores["happy"] *= 0.5
            scores["sad"] *= 1.3
            scores["angry"] *= 1.2

        exclamations = text.count("!")
        question_marks = text.count("?")
        if exclamations > 2:
            scores["excited"] += 0.3
            scores["angry"] += 0.1
        if question_marks > 1:
            scores["confused"] += 0.2

        all_caps_ratio = sum(1 for c in text if c.isupper()) / max(1, len(text))
        if all_caps_ratio > 0.5 and len(text) > 5:
            scores["angry"] += 0.3
            scores["excited"] += 0.2

        best_emotion = max(scores, key=lambda e: scores[e])
        best_score = scores[best_emotion]

        valence = 0.0
        arousal = 0.0
        dominance = 0.0

        if best_score > 0:
            profile = self.EMOTION_PROFILES[best_emotion]
            valence = (profile["valence"][0] + profile["valence"][1]) / 2
            arousal = (profile["arousal"][0] + profile["arousal"][1]) / 2
            dominance = (profile["dominance"][0] + profile["dominance"][1]) / 2

        return VoiceEmotion(
            primary=best_emotion,
            confidence=min(1.0, best_score),
            valence=valence,
            arousal=arousal,
            dominance=dominance,
            emotions=scores,
        )

    def get_emotional_state(self) -> str:
        """Get a description of the current emotional trend."""
        if not self._history:
            return "No voice data yet"

        recent = self._history[-5:]
        avg_valence = sum(e.valence for e in recent) / len(recent)
        avg_arousal = sum(e.arousal for e in recent) / len(recent)
        primary = max(set(e.primary for e in recent), key=lambda x: sum(1 for e in recent if e.primary == x))

        trend = "stable"
        if len(self._history) >= 3:
            old = self._history[-3]
            new = self._history[-1]
            if new.valence > old.valence + 0.2:
                trend = "improving"
            elif new.valence < old.valence - 0.2:
                trend = "declining"

        return f"{primary} (valence: {avg_valence:.2f}, arousal: {avg_arousal:.2f}, trend: {trend})"

    def get_emotion_history(self) -> list[dict]:
        """Get recent emotion history."""
        return [e.to_dict() for e in self._history[-20:]]

    def _extract_features(self, audio: np.ndarray) -> dict[str, float]:
        """Extract audio features for emotion classification."""
        try:
            rms = float(np.sqrt(np.mean(audio ** 2)))
            energy = min(1.0, rms * 10)

            zero_crossings = int(np.sum(np.abs(np.diff(np.sign(audio)))) / 2)
            zcr = zero_crossings / len(audio) if len(audio) > 0 else 0
            zcr_norm = min(1.0, zcr * 2)

            fft = np.abs(np.fft.rfft(audio))
            freqs = np.fft.rfftfreq(len(audio), 1.0 / self.sample_rate)

            if np.sum(fft) > 0:
                spectral_centroid = float(np.sum(freqs * fft) / np.sum(fft))
            else:
                spectral_centroid = 0.0

            pitch_proxy = spectral_centroid / 500

            bands = np.array_split(fft, 3)
            low_energy = float(np.mean(bands[0])) if len(bands[0]) > 0 else 0.0
            mid_energy = float(np.mean(bands[1])) if len(bands[1]) > 0 else 0.0
            high_energy = float(np.mean(bands[2])) if len(bands[2]) > 0 else 0.0
            total = low_energy + mid_energy + high_energy + 1e-10

            return {
                "energy": energy,
                "zcr": zcr_norm,
                "pitch_proxy": pitch_proxy,
                "spectral_spread": 0.5,
                "low_ratio": low_energy / total,
                "mid_ratio": mid_energy / total,
                "high_ratio": high_energy / total,
            }
        except Exception:
            return {"energy": 0.3, "zcr": 0.3, "pitch_proxy": 1.0, "spectral_spread": 0.5,
                    "low_ratio": 0.33, "mid_ratio": 0.34, "high_ratio": 0.33}

    def _classify_emotion(self, features: dict[str, float]) -> VoiceEmotion:
        """Classify emotion from extracted features."""
        energy = features.get("energy", 0.3)
        zcr = features.get("zcr", 0.3)
        pitch_proxy = features.get("pitch_proxy", 1.0)
        low_ratio = features.get("low_ratio", 0.33)
        high_ratio = features.get("high_ratio", 0.33)

        scores = {}
        for emotion, profile in self.EMOTION_PROFILES.items():
            score = 0.0
            v_range = profile["valence"]
            a_range = profile["arousal"]
            p_range = profile["pitch_range"]
            e_range = profile["energy_range"]
            z_range = profile["zcr_range"]

            v_center = (v_range[0] + v_range[1]) / 2
            a_center = (a_range[0] + a_range[1]) / 2

            v_val = energy * 0.5 + (1 - low_ratio) * 0.3 + high_ratio * 0.2
            v_val = v_val * 2 - 1

            a_val = energy * 0.4 + zcr * 0.3 + pitch_proxy * 0.3
            a_val = a_val * 2 - 1

            v_score = max(0, 1 - abs(v_val - v_center) / max(0.1, abs(v_range[1] - v_range[0])))
            a_score = max(0, 1 - abs(a_val - a_center) / max(0.1, abs(a_range[1] - a_range[0])))
            e_score = max(0, 1 - abs(energy - (e_range[0] + e_range[1]) / 2) / max(0.1, (e_range[1] - e_range[0])))
            z_score = max(0, 1 - abs(zcr - (z_range[0] + z_range[1]) / 2) / max(0.1, (z_range[1] - z_range[0])))

            score = v_score * 0.3 + a_score * 0.3 + e_score * 0.2 + z_score * 0.2
            scores[emotion] = score

        best_emotion = max(scores, key=lambda e: scores[e])
        best_score = scores[best_emotion]

        sorted_emotions = sorted(scores.items(), key=lambda x: -x[1])
        secondary = sorted_emotions[1][0] if len(sorted_emotions) > 1 else "neutral"

        profile = self.EMOTION_PROFILES[best_emotion]
        valence = (profile["valence"][0] + profile["valence"][1]) / 2
        arousal = (profile["arousal"][0] + profile["arousal"][1]) / 2
        dominance = (profile["dominance"][0] + profile["dominance"][1]) / 2

        return VoiceEmotion(
            primary=best_emotion,
            confidence=min(1.0, best_score),
            secondary=secondary,
            valence=valence,
            arousal=arousal,
            dominance=dominance,
            energy=energy,
            pitch_avg=pitch_proxy,
            pitch_var=0.0,
            speaking_rate=0.0,
            emotions=scores,
        )
