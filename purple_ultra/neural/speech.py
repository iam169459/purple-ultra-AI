"""Neural speech recognition with speaker diarization."""

from __future__ import annotations

import json
import time
import wave
import tempfile
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TranscriptSegment:
    text: str
    start: float
    end: float
    confidence: float
    speaker: str = "unknown"


@dataclass
class SpeakerProfile:
    name: str
    embeddings: list[list[float]] = field(default_factory=list)
    sample_count: int = 0


class NeuralSpeechRecognizer:
    def __init__(self, model_name: str = "Systran/faster-whisper-small.en", device: str = "cpu"):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._speaker_profiles: dict[str, SpeakerProfile] = {}
        self._profiles_file = Path("memory/neural_speakers.json")
        self._load_profiles()

    def _ensure_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
                self._model = WhisperModel(self._model_name, device=self._device, compute_type="int8")
            except ImportError:
                self._model = False

    def _load_profiles(self):
        if self._profiles_file.exists():
            try:
                data = json.loads(self._profiles_file.read_text())
                for name, info in data.items():
                    self._speaker_profiles[name] = SpeakerProfile(
                        name=name, embeddings=info.get("embeddings", []),
                        sample_count=info.get("sample_count", 0),
                    )
            except Exception:
                pass

    def _save_profiles(self):
        try:
            self._profiles_file.parent.mkdir(parents=True, exist_ok=True)
            data = {
                name: {"embeddings": p.embeddings[-5:], "sample_count": p.sample_count}
                for name, p in self._speaker_profiles.items()
            }
            self._profiles_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def transcribe(self, audio_path: str, language: str = "en") -> list[TranscriptSegment]:
        self._ensure_model()
        if not self._model:
            return self._fallback_transcribe(audio_path)
        try:
            segments, info = self._model.transcribe(audio_path, language=language, beam_size=5, word_timestamps=True)
            results = []
            for segment in segments:
                speaker = self._identify_speaker_from_segment(audio_path, segment.start, segment.end)
                results.append(TranscriptSegment(
                    text=segment.text.strip(),
                    start=segment.start,
                    end=segment.end,
                    confidence=segment.avg_logprob if hasattr(segment, "avg_logprob") else 0.5,
                    speaker=speaker,
                ))
            return results
        except Exception:
            return self._fallback_transcribe(audio_path)

    def _fallback_transcribe(self, audio_path: str) -> list[TranscriptSegment]:
        try:
            import speech_recognition as sr
            recognizer = sr.Recognizer()
            with sr.AudioFile(audio_path) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
            return [TranscriptSegment(text=text, start=0, end=0, confidence=0.7)]
        except Exception:
            return [TranscriptSegment(text="", start=0, end=0, confidence=0, speaker="unknown")]

    def _identify_speaker_from_segment(self, audio_path: str, start: float, end: float) -> str:
        try:
            embedding = self._extract_segment_embedding(audio_path, start, end)
            if not embedding:
                return "unknown"
            return self._identify_speaker(embedding)
        except Exception:
            return "unknown"

    def _extract_segment_embedding(self, audio_path: str, start: float, end: float) -> list[float]:
        try:
            with wave.open(audio_path, "rb") as wf:
                sample_rate = wf.getframerate()
                start_frame = int(start * sample_rate)
                end_frame = int(end * sample_rate)
                wf.setpos(start_frame)
                frames = wf.readframes(end_frame - start_frame)
                audio = np.frombuffer(frames, dtype=np.int16).astype(float)
            if len(audio) < 100:
                return []
            rms = float(np.sqrt(np.mean(audio ** 2)))
            fft = np.abs(np.fft.rfft(audio))
            spectral_centroid = float(np.sum(fft) / (len(fft) + 1e-10))
            zero_crossings = float(np.sum(np.abs(np.diff(np.sign(audio)))) / (2 * len(audio)))
            return [rms, spectral_centroid / 1000, zero_crossings]
        except Exception:
            return []

    def _identify_speaker(self, embedding: list[float]) -> str:
        if not self._speaker_profiles or not embedding:
            return "unknown"
        best_name = "unknown"
        best_dist = float("inf")
        emb = np.array(embedding)
        for name, profile in self._speaker_profiles.items():
            for sample_emb in profile.embeddings:
                sample = np.array(sample_emb[:len(emb)])
                if len(sample) == len(emb):
                    dist = np.linalg.norm(emb - sample)
                    if dist < best_dist:
                        best_dist = dist
                        best_name = name
        if best_dist < 0.5:
            return best_name
        return "unknown"

    def register_speaker(self, name: str, audio_path: str) -> str:
        embedding = self._extract_segment_embedding(audio_path, 0, 5)
        if not embedding:
            return "Failed to extract speaker features"
        if name not in self._speaker_profiles:
            self._speaker_profiles[name] = SpeakerProfile(name=name)
        profile = self._speaker_profiles[name]
        profile.embeddings.append(embedding)
        if len(profile.embeddings) > 5:
            profile.embeddings = profile.embeddings[-5:]
        profile.sample_count += 1
        self._save_profiles()
        return f"Registered speaker: {name}"

    def list_speakers(self) -> list[str]:
        return list(self._speaker_profiles.keys())

    def transcribe_stream(self, audio_path: str, language: str = "en"):
        self._ensure_model()
        if not self._model:
            return
        try:
            segments, _ = self._model.transcribe(audio_path, language=language, beam_size=5)
            for segment in segments:
                yield TranscriptSegment(
                    text=segment.text.strip(),
                    start=segment.start,
                    end=segment.end,
                    confidence=0.5,
                )
        except Exception:
            pass

    def get_status(self) -> dict:
        return {
            "model": self._model_name,
            "device": self._device,
            "loaded": self._model is not None and self._model is not False,
            "speakers": len(self._speaker_profiles),
        }
