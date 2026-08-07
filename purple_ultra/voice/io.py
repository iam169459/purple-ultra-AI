"""Voice I/O system with STT (Faster-Whisper), TTS (Piper/macOS say/pyttsx3), and voiceprint extraction."""

from __future__ import annotations

import io
import os
import struct
import subprocess
import sys
import tempfile
import wave
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from ..config.settings import Config, VoiceConfig
from .super_admin import get_super_admin_voice, SuperAdminVoice, SUPER_ADMIN_ID
from .analyzer import VoiceAnalyzer, VoiceEmotion


@dataclass(frozen=True)
class Heard:
    text: str
    voiceprint: list[float] = field(default_factory=list)
    emotion: Optional[VoiceEmotion] = None


EFFECT_PHRASES: dict[str, str] = {
    "breath": "[[slnc 300]] Hmm. [[slnc 200]]",
    "yawn": "[[slnc 400]] *yaaawn* [[slnc 300]]",
    "sneeze": "*achoo!* [[slnc 200]]",
    "sniffle": "*sniff* [[slnc 200]]",
    "soft_cough": "*ahem* [[slnc 200]]",
    "sleepy_sigh": "[[slnc 500]] *sigh* [[slnc 300]]",
    "lazy_pause": "[[slnc 800]]",
}

MOOD_OPENERS: dict[str, str] = {
    "happy": "Great! ",
    "sad": "Oh... ",
    "angry": "Look, ",
    "excited": "Awesome! ",
    "calm": "",
    "playful": "Hehe! ",
    "worried": "Um, ",
    "love": "",
    "sarcastic": "Oh, wow. ",
    "surprised": "Oh! ",
    "proud": "Yes! ",
    "grateful": "Thank you! ",
    "bored": "So... ",
    "confused": "Hmm... ",
    "motivated": "Let's do this! ",
    "tired": "*yawn* ",
    "inspired": "You know what? ",
    "neutral": "",
}


BANGLA_VOICE_MAP: dict[str, str] = {
    "Samantha": "Ting-Ting",
    "Alex": "Ting-Ting",
    "Daniel": "Ting-Ting",
    "Karen": "Ting-Ting",
    "Moira": "Ting-Ting",
    "Tessa": "Ting-Ting",
    "Veena": "Veena",
}

BANGLA_PIPER_MODEL = "bn_BD-nishita-medium"

BANGLA_STT_SETTINGS = {
    "beam_size": 5,
    "best_of": 5,
    "patience": 2.0,
    "vad_filter": True,
    "vad_parameters": {
        "min_silence_duration_ms": 500,
        "speech_pad_ms": 400,
        "threshold": 0.35,
    },
}

BANGLA_TTS_SETTINGS = {
    "speed": 1.0,
    "sentence_silence": 0.3,
    "length_scale": 1.0,
}


class VoiceIO:
    """Handles all voice input/output operations."""

    __slots__ = ('config', '_whisper_model', '_pyttsx3_engine', '_piper_available',
                 '_super_admin', '_admin_override', '_last_effect', '_refuted_effects',
                 '_analyzer', '_current_language', '_whisper_models', '_audio_buffer',
                 '_sample_rate', '_preloaded')

    def __init__(self, config: Config):
        self.config = config
        self._whisper_model = None
        self._whisper_models: dict[str, object] = {}
        self._pyttsx3_engine = None
        self._piper_available = None
        self._super_admin = get_super_admin_voice()
        self._admin_override = False
        self._last_effect: str | None = None
        self._refuted_effects: list[dict] = []
        self._analyzer = VoiceAnalyzer()
        self._current_language = "en"
        self._audio_buffer: deque[np.ndarray] = deque(maxlen=3)
        self._sample_rate = 16000
        self._preloaded: dict[str, bool] = {"en": False, "bn": False}

    def set_language(self, lang: str):
        """Set the current language for STT and TTS."""
        if lang in ("en", "bn", "bangla", "bengali"):
            self._current_language = "bn" if lang in ("bn", "bangla", "bengali") else "en"
            self._whisper_model = None
            return True
        return False

    def get_language(self) -> str:
        """Get the current language code."""
        return self._current_language

    def preload_models(self, lang: str = None):
        """Preload Whisper models for faster first recognition."""
        langs = [lang] if lang else ["en", "bn"]
        for l in langs:
            if l in ("bn", "bangla", "bengali"):
                l = "bn"
            elif l in ("en", "english"):
                l = "en"
            if not self._preloaded.get(l):
                self._ensure_whisper_for_lang(l)

    def _ensure_whisper_for_lang(self, lang: str):
        """Ensure Whisper model is loaded for a specific language."""
        if lang in self._whisper_models:
            self._whisper_model = self._whisper_models[lang]
            return

        try:
            from faster_whisper import WhisperModel
            if lang == "bn":
                model_path = self.config.stt.model_bangla
            else:
                model_path = self.config.stt.model
            models_dir = Path("models")
            models_dir.mkdir(exist_ok=True)
            local_path = models_dir / model_path.split("/")[-1]
            if local_path.exists():
                model_path = str(local_path)
            self._whisper_model = WhisperModel(
                model_path,
                device=self.config.stt.device,
                compute_type=self.config.stt.compute_type,
            )
            self._whisper_models[lang] = self._whisper_model
            self._preloaded[lang] = True
        except ImportError:
            print("Warning: faster-whisper not installed. STT unavailable.")
            self._whisper_model = False

    def _ensure_whisper(self):
        lang = self._current_language
        if lang in self._whisper_models:
            self._whisper_model = self._whisper_models[lang]
            return
        self._ensure_whisper_for_lang(lang)

    def _ensure_pyttsx3(self):
        if self._pyttsx3_engine is None:
            try:
                import pyttsx3
                self._pyttsx3_engine = pyttsx3.init()
            except Exception:
                self._pyttsx3_engine = False

    def _can_use_piper(self) -> bool:
        if self._piper_available is None:
            try:
                result = subprocess.run(
                    ["piper", "--version"],
                    capture_output=True, timeout=5
                )
                self._piper_available = result.returncode == 0
            except (FileNotFoundError, subprocess.TimeoutExpired):
                self._piper_available = False
        return self._piper_available

    def listen(self) -> Heard:
        """Record audio and transcribe to text with voiceprint extraction."""
        self._ensure_whisper()
        if not self._whisper_model:
            return Heard(text="")

        try:
            import sounddevice as sd
        except ImportError:
            return self._listen_fallback()

        try:
            duration = self.config.stt.listen_seconds
            sample_rate = self._sample_rate
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()
            audio_flat = audio.flatten()

            voiceprint = self._extract_voiceprint(audio_flat, sample_rate)
            emotion = self._analyzer.analyze_audio(audio_flat)

            if np.max(np.abs(audio_flat)) < 0.002:
                return Heard(text="", voiceprint=voiceprint, emotion=emotion)

            audio_processed = self._preprocess_audio(audio_flat, sample_rate)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                audio_int16 = (audio_processed * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())

            lang = "bn" if self._current_language == "bn" else "en"
            transcribe_kwargs = {
                "language": lang,
                "beam_size": BANGLA_STT_SETTINGS["beam_size"],
                "patience": BANGLA_STT_SETTINGS["patience"],
                "vad_filter": BANGLA_STT_SETTINGS["vad_filter"],
                "vad_parameters": BANGLA_STT_SETTINGS["vad_parameters"],
            }

            segments, info = self._whisper_model.transcribe(tmp_path, **transcribe_kwargs)
            text = " ".join(s.text.strip() for s in segments).strip()

            if info.language and info.language != lang:
                detected_lang = info.language
                if detected_lang in ("bn", "bn"):
                    pass

            if emotion.confidence < 0.3:
                text_emotion = self._analyzer.analyze_text_sentiment(text)
                if text_emotion.confidence > emotion.confidence:
                    emotion = text_emotion

            try:
                os.unlink(tmp_path)
            except OSError:
                pass

            return Heard(text=text, voiceprint=voiceprint, emotion=emotion)

        except Exception as e:
            print(f"Listen error: {e}")
            return Heard(text="")

    def _preprocess_audio(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """Preprocess audio for better recognition."""
        try:
            audio = audio.astype(np.float32)

            rms = np.sqrt(np.mean(audio ** 2))
            if rms > 0:
                target_rms = 0.1
                audio = audio * (target_rms / rms)

            audio = np.clip(audio, -1.0, 1.0)

            audio = self._apply_pre_emphasis(audio, 0.97)

            audio = self._normalize_audio(audio)

            audio = self._apply_noise_gate(audio, threshold=0.01)

            return audio
        except Exception:
            return audio

    def _apply_pre_emphasis(self, audio: np.ndarray, factor: float = 0.97) -> np.ndarray:
        """Apply pre-emphasis filter to boost high frequencies."""
        return np.append(audio[0], audio[1:] - factor * audio[:-1])

    def _normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Normalize audio to [-1, 1] range."""
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio = audio / max_val
        return audio

    def _apply_noise_gate(self, audio: np.ndarray, threshold: float = 0.01) -> np.ndarray:
        """Apply noise gate to reduce background noise."""
        mask = np.abs(audio) > threshold
        return audio * mask

    def _listen_fallback(self) -> Heard:
        """Fallback using system microphone recording."""
        self._ensure_whisper()
        if not self._whisper_model:
            return Heard(text="")
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            if sys.platform == "darwin":
                subprocess.run(
                    ["rec", "-r", "16000", "-c", "1", "-b", "16", tmp_path, "trim", "0", str(self.config.stt.listen_seconds)],
                    capture_output=True, timeout=self.config.stt.listen_seconds + 5,
                )
            else:
                return Heard(text="")

            lang = "bn" if self._current_language == "bn" else "en"
            segments, _ = self._whisper_model.transcribe(
                tmp_path,
                language=lang,
                beam_size=BANGLA_STT_SETTINGS["beam_size"],
                vad_filter=BANGLA_STT_SETTINGS["vad_filter"],
                vad_parameters=BANGLA_STT_SETTINGS["vad_parameters"],
            )
            text = " ".join(s.text.strip() for s in segments).strip()
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            return Heard(text=text)
        except Exception:
            return Heard(text="")

    def _extract_voiceprint(self, audio: np.ndarray, sample_rate: int) -> list[float]:
        """Extract a simple 7-dimensional voiceprint from audio."""
        try:
            rms = float(np.sqrt(np.mean(audio ** 2)))
            zero_crossings = int(np.sum(np.abs(np.diff(np.sign(audio)))) / 2)
            zcr = zero_crossings / len(audio) if len(audio) > 0 else 0

            fft = np.abs(np.fft.rfft(audio))
            freqs = np.fft.rfftfreq(len(audio), 1.0 / sample_rate)
            spectral_centroid = float(np.sum(freqs * fft) / (np.sum(fft) + 1e-10))
            spectral_spread = float(np.sqrt(np.sum(((freqs - spectral_centroid) ** 2) * fft) / (np.sum(fft) + 1e-10)))

            bands = np.array_split(fft, 3)
            low_energy = float(np.mean(bands[0])) if len(bands[0]) > 0 else 0.0
            mid_energy = float(np.mean(bands[1])) if len(bands[1]) > 0 else 0.0
            high_energy = float(np.mean(bands[2])) if len(bands[2]) > 0 else 0.0

            total = low_energy + mid_energy + high_energy + 1e-10
            return [rms, zcr, spectral_centroid / 1000, spectral_spread / 1000, low_energy / total, mid_energy / total, high_energy / total]
        except Exception:
            return []

    def speak(self, text: str, mood: str = None, force_admin: bool = False):
        """Speak text with mood-appropriate voice parameters.
        
        Super admin voice always takes priority when:
        - force_admin=True
        - speaker is super admin
        - admin override is active
        """
        if not text:
            return

        # Super admin voice takes priority
        if force_admin or self._admin_override:
            self._super_admin.speak(text, mood)
            return

        opener = MOOD_OPENERS.get(mood, "") if mood else ""
        text = opener + text

        mood_config = self.config.mood
        if mood and mood in mood_config.voices:
            voice_cfg = mood_config.voices[mood]
        else:
            voice_cfg = self.config.voice

        if self._current_language == "bn":
            self._speak_bangla(text, voice_cfg)
        elif self._can_use_piper():
            self._speak_piper(text, voice_cfg)
        elif sys.platform == "darwin":
            self._speak_macos(text, voice_cfg)
        else:
            self._speak_pyttsx3(text, voice_cfg)

    def _speak_bangla(self, text: str, voice_cfg: VoiceConfig):
        """Speak Bangla text using Piper or macOS say with optimized settings."""
        chunks = self._split_bangla_text(text, max_chars=400)

        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue

            if self._can_use_piper():
                try:
                    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                        tmp_path = f.name
                    model = self.config.tts.piper_model_bangla
                    piper_args = [
                        "piper",
                        "--model", model,
                        "--output_file", tmp_path,
                        "--sentence_silence", str(BANGLA_TTS_SETTINGS["sentence_silence"]),
                    ]
                    process = subprocess.Popen(
                        piper_args,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    )
                    process.communicate(input=chunk.encode("utf-8"))
                    if process.returncode == 0:
                        subprocess.run(["afplay", tmp_path], capture_output=True)
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass
                    continue
                except Exception:
                    pass

            if sys.platform == "darwin":
                try:
                    voice_name = BANGLA_VOICE_MAP.get(voice_cfg.name, "Ting-Ting")
                    rate = int(voice_cfg.rate * BANGLA_TTS_SETTINGS["speed"])
                    rate_param = f"-r {rate}"
                    subprocess.run(
                        ["say", "-v", f"{voice_name}", rate_param, chunk],
                        capture_output=True, timeout=30,
                    )
                    continue
                except Exception:
                    pass

            self._speak_pyttsx3(chunk, voice_cfg)

    def _split_bangla_text(self, text: str, max_chars: int = 400) -> list[str]:
        """Split Bangla text into chunks for better TTS processing."""
        if len(text) <= max_chars:
            return [text]

        chunks = []
        sentences = text.replace("।", "।|").replace("?", "?|").replace("!", "!|").split("|")
        current_chunk = ""

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(current_chunk) + len(sentence) + 1 <= max_chars:
                current_chunk = (current_chunk + " " + sentence).strip()
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence

        if current_chunk:
            chunks.append(current_chunk)

        return chunks if chunks else [text]

    def speak_admin(self, text: str, mood: str = None):
        """Speak with super admin voice - cannot be intercepted."""
        self._super_admin.speak(text, mood)

    def set_admin_override(self, enabled: bool):
        """Enable/disable admin voice override."""
        self._admin_override = enabled

    def get_admin_status(self) -> dict:
        """Get super admin voice status."""
        return self._super_admin.get_status()

    def speak_effect(self, effect: str) -> bool:
        """Speak a vocal effect. Returns True if effect was spoken."""
        if effect and effect in EFFECT_PHRASES:
            self._last_effect = effect
            self.speak(EFFECT_PHRASES[effect])
            return True
        return False

    def refute_effect(self, reason: str = "") -> str:
        """Refute/cancel the last voice effect."""
        if self._last_effect:
            refuted = self._last_effect
            self._refuted_effects.append({
                "effect": refuted,
                "reason": reason,
                "timestamp": __import__('time').time(),
            })
            self._last_effect = None
            if reason:
                return f"Effect '{refuted}' refuted: {reason}"
            return f"Effect '{refuted}' refuted"
        return "No effect to refute"

    def get_last_effect(self) -> str | None:
        """Get the last applied effect."""
        return self._last_effect

    def get_refuted_effects(self) -> list[dict]:
        """Get history of refuted effects."""
        return self._refuted_effects[-20:]

    def clear_effect(self):
        """Clear the current effect without recording it."""
        self._last_effect = None

    def _speak_piper(self, text: str, voice_cfg: VoiceConfig):
        """Speak using Piper neural TTS."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            model = self.config.tts.piper_model
            process = subprocess.Popen(
                ["piper", "--model", model, "--output_file", tmp_path],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            process.communicate(input=text.encode())
            if process.returncode == 0:
                subprocess.run(["afplay", tmp_path], capture_output=True)
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        except Exception:
            if sys.platform == "darwin":
                self._speak_macos(text, voice_cfg)
            else:
                self._speak_pyttsx3(text, voice_cfg)

    def _speak_macos(self, text: str, voice_cfg: VoiceConfig):
        """Speak using macOS say command."""
        try:
            rate = voice_cfg.rate
            subprocess.run(
                ["say", "-v", voice_cfg.name, "-r", str(rate), text],
                check=True, timeout=30,
            )
        except Exception:
            self._speak_pyttsx3(text, voice_cfg)

    def _speak_pyttsx3(self, text: str, voice_cfg: VoiceConfig):
        """Speak using pyttsx3 (cross-platform fallback)."""
        self._ensure_pyttsx3()
        if not self._pyttsx3_engine:
            return
        try:
            self._pyttsx3_engine.setProperty("rate", voice_cfg.rate)
            self._pyttsx3_engine.setProperty("volume", voice_cfg.volume)
            self._pyttsx3_engine.say(text)
            self._pyttsx3_engine.runAndWait()
        except Exception:
            pass

    def sing(self, lyrics: str, mood: str = None):
        """Sing lyrics using stretched TTS."""
        if not lyrics:
            return
        if self._can_use_piper():
            try:
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    tmp_path = f.name
                process = subprocess.Popen(
                    ["piper", "--model", self.config.tts.piper_model, "--output_file", tmp_path],
                    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                )
                process.communicate(input=lyrics.encode())
                if process.returncode == 0:
                    subprocess.run(["afplay", tmp_path], capture_output=True)
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            except Exception:
                self.speak(lyrics, mood=mood)
        else:
            self.speak(lyrics, mood=mood)

    def get_analyzer(self) -> VoiceAnalyzer:
        """Get the voice analyzer instance."""
        return self._analyzer

    def get_emotion_history(self) -> list[dict]:
        """Get recent emotion detection history."""
        return self._analyzer.get_emotion_history()

    def get_emotional_state(self) -> str:
        """Get current emotional state description."""
        return self._analyzer.get_emotional_state()

    def analyze_text_emotion(self, text: str) -> VoiceEmotion:
        """Analyze text for emotional content."""
        return self._analyzer.analyze_text_sentiment(text)
