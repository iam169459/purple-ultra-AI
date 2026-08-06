"""Configuration system with frozen dataclasses and TOML support."""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VoiceConfig:
    name: str = "Samantha"
    rate: int = 200
    pitch: float = 1.0
    volume: float = 0.9
    language: str = "en"

    BANGLA_VOICES: dict[str, str] = field(default_factory=lambda: {
        "Samantha": "Ting-Ting",
        "Alex": "Ting-Ting",
        "Daniel": "Ting-Ting",
    })

    BANGLA_PIPER_MODEL: str = "bn_BD-nishita-medium"

    BANGLA_NAMES: list[str] = field(default_factory=lambda: ["Ting-Ting", "Veena"])


@dataclass(frozen=True)
class TtsConfig:
    engine: str = "auto"
    piper_model: str = "en_US-amy-medium"
    piper_model_bangla: str = "bn_BD-nishita-medium"
    fallback_to_say: bool = True
    fallback_to_pyttsx3: bool = True
    chunk_size: int = 500


@dataclass(frozen=True)
class SttConfig:
    engine: str = "faster-whisper"
    model: str = "Systran/faster-whisper-small.en"
    model_bangla: str = "Systran/faster-whisper-small"
    device: str = "cpu"
    compute_type: str = "int8"
    language: str = "en"
    listen_seconds: float = 6.0
    energy_threshold: int = 300


@dataclass(frozen=True)
class LlmConfig:
    provider: str = "ollama"
    host: str = "http://127.0.0.1:11434"
    model: str = "llama3:latest"
    api_key: str = ""
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    timeout: int = 5
    enabled: bool = False


@dataclass(frozen=True)
class MoodConfig:
    default: str = "neutral"
    voices: dict[str, VoiceConfig] = field(default_factory=lambda: {
        "neutral": VoiceConfig(name="Samantha", rate=200, pitch=1.0),
        "happy": VoiceConfig(name="Samantha", rate=210, pitch=1.1),
        "sad": VoiceConfig(name="Samantha", rate=170, pitch=0.9),
        "angry": VoiceConfig(name="Samantha", rate=230, pitch=0.8),
        "excited": VoiceConfig(name="Samantha", rate=240, pitch=1.2),
        "calm": VoiceConfig(name="Samantha", rate=180, pitch=1.0),
        "playful": VoiceConfig(name="Samantha", rate=220, pitch=1.15),
        "worried": VoiceConfig(name="Samantha", rate=190, pitch=0.95),
        "love": VoiceConfig(name="Samantha", rate=185, pitch=1.05),
        "sarcastic": VoiceConfig(name="Samantha", rate=195, pitch=0.85),
        "surprised": VoiceConfig(name="Samantha", rate=250, pitch=1.25),
        "proud": VoiceConfig(name="Samantha", rate=205, pitch=1.1),
        "grateful": VoiceConfig(name="Samantha", rate=195, pitch=1.05),
        "bored": VoiceConfig(name="Samantha", rate=160, pitch=0.8),
        "confused": VoiceConfig(name="Samantha", rate=190, pitch=0.95),
        "motivated": VoiceConfig(name="Samantha", rate=230, pitch=1.15),
        "tired": VoiceConfig(name="Samantha", rate=150, pitch=0.85),
        "inspired": VoiceConfig(name="Samantha", rate=215, pitch=1.1),
    })


@dataclass(frozen=True)
class SpeakerConfig:
    enabled: bool = True
    threshold: float = 0.9
    max_samples: int = 5
    profiles_file: str = "memory/speakers.json"


@dataclass(frozen=True)
class MemoryConfig:
    max_history: int = 1000
    history_file: str = "memory/history.jsonl"
    profile_file: str = "memory/profile.md"
    notes_file: str = "memory/notes.md"
    learned_file: str = "memory/learned.md"
    episodic_file: str = "memory/episodic.json"
    semantic_file: str = "memory/semantic.json"
    procedural_file: str = "memory/procedural.json"
    knowledge_graph_file: str = "data/knowledge_graph.json"
    patterns_file: str = "memory/patterns.json"


@dataclass(frozen=True)
class ToolConfig:
    enabled: bool = True
    allow_shell: bool = False
    allow_internet: bool = True
    allow_file_write: bool = True
    allow_camera: bool = True
    sandbox_path: str = ""
    max_actions_per_turn: int = 5
    dangerous_tools: tuple[str, ...] = ("run_shell", "write_file", "delete_file", "execute_code")


@dataclass(frozen=True)
class EmotionConfig:
    enabled: bool = True
    auto_detect: bool = True
    persistence: bool = True
    decay_rate: float = 0.1


@dataclass(frozen=True)
class ThinkingConfig:
    enabled: bool = True
    deep_thinking: bool = True
    metacognition: bool = True
    hypothesis_engine: bool = True
    autonomous_goals: bool = True
    max_chain_depth: int = 10


@dataclass(frozen=True)
class ScreenConfig:
    enabled: bool = False
    monitor_interval: float = 60.0
    ocr_enabled: bool = True
    proactive_suggestions: bool = True


@dataclass(frozen=True)
class TrainingConfig:
    enabled: bool = False
    base_model: str = "mlx-community/Qwen2.5-3B-Instruct-4bit"
    output_dir: str = "training/output"
    max_iterations: int = 200
    auto_export: bool = True


@dataclass(frozen=True)
class PersonalityConfig:
    mode: str = "professional"
    name: str = "Ultra"
    file: str = "personality/default.md"
    companion_mode: bool = False
    languages: tuple[str, ...] = ("en",)


@dataclass(frozen=True)
class WebConfig:
    enabled: bool = True
    search_engines: tuple[str, ...] = ("duckduckgo", "google", "bing")
    media_platforms: tuple[str, ...] = ("youtube", "spotify", "netflix")
    browser: str = "auto"


@dataclass(frozen=True)
class SystemConfig:
    platform: str = "auto"
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = "logs/purple_ultra.log"
    data_dir: str = "data"
    temp_dir: str = "temp"


@dataclass(frozen=True)
class AssistantConfig:
    name: str = "Purple Ultra"
    version: str = "1.0.0"
    voice_mode: str = "always"
    text_mode: bool = True


@dataclass(frozen=True)
class Config:
    assistant: AssistantConfig = field(default_factory=AssistantConfig)
    voice: VoiceConfig = field(default_factory=VoiceConfig)
    tts: TtsConfig = field(default_factory=TtsConfig)
    stt: SttConfig = field(default_factory=SttConfig)
    llm: LlmConfig = field(default_factory=LlmConfig)
    mood: MoodConfig = field(default_factory=MoodConfig)
    speaker: SpeakerConfig = field(default_factory=SpeakerConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    tools: ToolConfig = field(default_factory=ToolConfig)
    emotion: EmotionConfig = field(default_factory=EmotionConfig)
    thinking: ThinkingConfig = field(default_factory=ThinkingConfig)
    screen: ScreenConfig = field(default_factory=ScreenConfig)
    training: TrainingConfig = field(default_factory=TrainingConfig)
    personality: PersonalityConfig = field(default_factory=PersonalityConfig)
    web: WebConfig = field(default_factory=WebConfig)
    system: SystemConfig = field(default_factory=SystemConfig)


def _build_dataclass(cls, data: dict[str, Any]):
    """Recursively build a frozen dataclass from a dict."""
    if not isinstance(data, dict):
        return data
    field_map = {f.name: f for f in cls.__dataclass_fields__.values()}
    kwargs = {}
    for key, value in data.items():
        if key in field_map:
            ft = field_map[key].type
            if hasattr(ft, "__dataclass_fields__") and isinstance(value, dict):
                kwargs[key] = _build_dataclass(ft, value)
            else:
                kwargs[key] = value
    return cls(**kwargs)


def load_config(path: Path | str = Path("config.toml")) -> Config:
    """Load configuration from a TOML file."""
    path = Path(path)
    if not path.exists():
        return Config()

    with open(path, "rb") as f:
        raw = tomllib.load(f)

    sections = {
        "assistant": (AssistantConfig, raw.get("assistant", {})),
        "voice": (VoiceConfig, raw.get("voice", {})),
        "tts": (TtsConfig, raw.get("tts", {})),
        "stt": (SttConfig, raw.get("stt", raw.get("speech_to_text", {}))),
        "llm": (LlmConfig, raw.get("llm", {})),
        "mood": (MoodConfig, raw.get("mood", {})),
        "speaker": (SpeakerConfig, raw.get("speaker", {})),
        "memory": (MemoryConfig, raw.get("memory", {})),
        "tools": (ToolConfig, raw.get("tools", {})),
        "emotion": (EmotionConfig, raw.get("emotion", {})),
        "thinking": (ThinkingConfig, raw.get("thinking", {})),
        "screen": (ScreenConfig, raw.get("screen", {})),
        "training": (TrainingConfig, raw.get("training", {})),
        "personality": (PersonalityConfig, raw.get("personality", {})),
        "web": (WebConfig, raw.get("web", {})),
        "system": (SystemConfig, raw.get("system", {})),
    }

    kwargs = {}
    for name, (cls, data) in sections.items():
        if data:
            kwargs[name] = _build_dataclass(cls, data)
        else:
            kwargs[name] = cls()

    return Config(**kwargs)
