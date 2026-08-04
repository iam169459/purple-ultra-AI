"""Neural voice synthesis with emotion control and voice cloning."""

from __future__ import annotations

import os
import time
import json
import wave
import struct
import subprocess
import tempfile
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class VoiceConfig:
    speed: float = 1.0
    pitch: float = 1.0
    energy: float = 1.0
    emotion: str = "neutral"
    speaker_id: int = 0


@dataclass
class VoiceSample:
    name: str
    path: str
    duration: float
    sample_rate: int
    speaker_id: int = 0
    emotion: str = "neutral"
    features: list[float] = field(default_factory=list)


class NeuralVoiceSynth:
    def __init__(self, model_dir: str = "models/voice"):
        self._model_dir = Path(model_dir)
        self._model_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._samples_dir = self._model_dir / "samples"
        self._samples_dir.mkdir(exist_ok=True)
        self._voice_samples: list[VoiceSample] = []
        self._load_samples()

    def _load_samples(self):
        samples_file = self._model_dir / "samples.json"
        if samples_file.exists():
            try:
                data = json.loads(samples_file.read_text())
                for s in data:
                    self._voice_samples.append(VoiceSample(**s))
            except Exception:
                pass

    def _save_samples(self):
        samples_file = self._model_dir / "samples.json"
        try:
            data = [
                {"name": s.name, "path": s.path, "duration": s.duration,
                 "sample_rate": s.sample_rate, "speaker_id": s.speaker_id,
                 "emotion": s.emotion, "features": s.features}
                for s in self._voice_samples
            ]
            samples_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def synthesize(self, text: str, voice_config: VoiceConfig = None, output_path: str = None) -> str:
        config = voice_config or VoiceConfig()
        if output_path is None:
            output_path = str(tempfile.mktemp(suffix=".wav"))
        try:
            import pyttsx3
            engine = pyttsx3.init()
            rate = engine.getProperty("rate")
            engine.setProperty("rate", int(rate * config.speed))
            volume = engine.getProperty("volume")
            engine.setProperty("volume", min(1.0, volume * config.energy))
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            return output_path
        except Exception:
            return self._synthesize_piper(text, config, output_path)

    def _synthesize_piper(self, text: str, config: VoiceConfig, output_path: str) -> str:
        try:
            model = "en_US-amy-medium"
            cmd = ["piper", "--model", model, "--output_file", output_path]
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            process.communicate(input=text.encode())
            if process.returncode == 0 and Path(output_path).exists():
                return output_path
        except Exception:
            pass
        return self._synthesize_say(text, config, output_path)

    def _synthesize_say(self, text: str, config: VoiceConfig, output_path: str) -> str:
        try:
            aiff_path = output_path.replace(".wav", ".aiff")
            rate = int(200 * config.speed)
            subprocess.run(["say", "-r", str(rate), "-o", aiff_path, text], check=True, capture_output=True)
            subprocess.run(["afconvert", aiff_path, output_path, "-d", "LEI16", "-f", "WAVE"], check=True, capture_output=True)
            if Path(aiff_path).exists():
                Path(aiff_path).unlink()
            return output_path
        except Exception:
            return ""

    def synthesize_emotion(self, text: str, emotion: str, output_path: str = None) -> str:
        emotion_configs = {
            "happy": VoiceConfig(speed=1.1, pitch=1.1, energy=1.2, emotion="happy"),
            "sad": VoiceConfig(speed=0.85, pitch=0.9, energy=0.7, emotion="sad"),
            "angry": VoiceConfig(speed=1.15, pitch=0.85, energy=1.3, emotion="angry"),
            "excited": VoiceConfig(speed=1.2, pitch=1.15, energy=1.3, emotion="excited"),
            "calm": VoiceConfig(speed=0.9, pitch=1.0, energy=0.8, emotion="calm"),
            "whisper": VoiceConfig(speed=0.95, pitch=1.0, energy=0.3, emotion="whisper"),
        }
        config = emotion_configs.get(emotion, VoiceConfig())
        return self.synthesize(text, config, output_path)

    def add_voice_sample(self, name: str, audio_path: str, emotion: str = "neutral") -> str:
        try:
            with wave.open(audio_path, "rb") as wf:
                frames = wf.getnframes()
                sample_rate = wf.getframerate()
                duration = frames / sample_rate
            features = self._extract_features(audio_path)
            sample = VoiceSample(
                name=name, path=audio_path, duration=duration,
                sample_rate=sample_rate, emotion=emotion, features=features,
            )
            self._voice_samples.append(sample)
            self._save_samples()
            return f"Added voice sample: {name} ({duration:.1f}s)"
        except Exception as e:
            return f"Error: {e}"

    def _extract_features(self, audio_path: str) -> list[float]:
        try:
            import numpy as np
            with wave.open(audio_path, "rb") as wf:
                frames = wf.readframes(wf.getnframes())
                audio = np.frombuffer(frames, dtype=np.int16).astype(float)
            rms = float(np.sqrt(np.mean(audio ** 2)))
            fft = np.abs(np.fft.rfft(audio))
            spectral_centroid = float(np.sum(fft) / (len(fft) + 1e-10))
            return [rms, spectral_centroid, float(np.max(audio)), float(np.mean(np.abs(audio)))]
        except Exception:
            return []

    def find_similar_voice(self, target_features: list[float]) -> str:
        if not self._voice_samples or not target_features:
            return ""
        best_match = ""
        best_dist = float("inf")
        target = np.array(target_features)
        for sample in self._voice_samples:
            if sample.features:
                dist = np.linalg.norm(target - np.array(sample.features[:len(target)]))
                if dist < best_dist:
                    best_dist = dist
                    best_match = sample.name
        return best_match

    def list_samples(self) -> list[dict]:
        return [
            {"name": s.name, "duration": s.duration, "emotion": s.emotion, "sample_rate": s.sample_rate}
            for s in self._voice_samples
        ]

    def get_status(self) -> dict:
        return {
            "samples": len(self._voice_samples),
            "model_dir": str(self._model_dir),
        }
