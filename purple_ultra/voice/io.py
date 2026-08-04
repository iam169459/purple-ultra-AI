"""Voice I/O system with STT (Faster-Whisper), TTS (Piper/macOS say/pyttsx3), and voiceprint extraction."""

from __future__ import annotations

import io
import os
import struct
import subprocess
import sys
import tempfile
import wave
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import numpy as np

from ..config.settings import Config, VoiceConfig
from .super_admin import get_super_admin_voice, SuperAdminVoice, SUPER_ADMIN_ID


@dataclass(frozen=True)
class Heard:
    text: str
    voiceprint: list[float] = field(default_factory=list)


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


class VoiceIO:
    """Handles all voice input/output operations."""

    __slots__ = ('config', '_whisper_model', '_pyttsx3_engine', '_piper_available',
                 '_super_admin', '_admin_override')

    def __init__(self, config: Config):
        self.config = config
        self._whisper_model = None
        self._pyttsx3_engine = None
        self._piper_available = None
        self._super_admin = get_super_admin_voice()
        self._admin_override = False

    def _ensure_whisper(self):
        if self._whisper_model is None:
            try:
                from faster_whisper import WhisperModel
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
            except ImportError:
                print("Warning: faster-whisper not installed. STT unavailable.")
                self._whisper_model = False

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
            sample_rate = 16000
            audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
            sd.wait()
            audio_flat = audio.flatten()

            voiceprint = self._extract_voiceprint(audio_flat, sample_rate)

            if np.max(np.abs(audio_flat)) < 0.002:
                return Heard(text="", voiceprint=voiceprint)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            with wave.open(tmp_path, "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                audio_int16 = (audio_flat * 32767).astype(np.int16)
                wf.writeframes(audio_int16.tobytes())

            segments, _ = self._whisper_model.transcribe(
                tmp_path,
                language=self.config.stt.language,
                beam_size=5,
            )
            text = " ".join(s.text.strip() for s in segments).strip()

            try:
                os.unlink(tmp_path)
            except OSError:
                pass

            return Heard(text=text, voiceprint=voiceprint)

        except Exception as e:
            print(f"Listen error: {e}")
            return Heard(text="")

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
            segments, _ = self._whisper_model.transcribe(
                tmp_path, language=self.config.stt.language, beam_size=5,
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

        if self._can_use_piper():
            self._speak_piper(text, voice_cfg)
        elif sys.platform == "darwin":
            self._speak_macos(text, voice_cfg)
        else:
            self._speak_pyttsx3(text, voice_cfg)

    def speak_admin(self, text: str, mood: str = None):
        """Speak with super admin voice - cannot be intercepted."""
        self._super_admin.speak(text, mood)

    def set_admin_override(self, enabled: bool):
        """Enable/disable admin voice override."""
        self._admin_override = enabled

    def get_admin_status(self) -> dict:
        """Get super admin voice status."""
        return self._super_admin.get_status()

    def speak_effect(self, effect: str):
        """Speak a vocal effect."""
        if effect and effect in EFFECT_PHRASES:
            self.speak(EFFECT_PHRASES[effect])

    def _speak_piper(self, text: str, voice_cfg: VoiceConfig):
        """Speak using Piper neural TTS."""
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                tmp_path = f.name
            process = subprocess.Popen(
                ["piper", "--model", self.config.tts.piper_model, "--output_file", tmp_path],
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
