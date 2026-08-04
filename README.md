# Purple Ultra AI

**Advanced Offline Voice Assistant** - Combining the best of Purple AI and Purple-Plus AI into one unified, cross-platform, fully offline voice assistant.

## Features

### Voice System
- **Offline STT**: Faster-Whisper local speech-to-text
- **Multi-backend TTS**: Piper neural TTS, macOS `say`, pyttsx3 (cross-platform fallback)
- **18 mood-based voice profiles**: Each mood has unique rate, pitch, and volume
- **Voice effects**: Breathing, yawning, sneezing, and more
- **Speaker recognition**: Voiceprint-based identification

### Intelligence
- **Multi-LLM support**: Ollama (local), OpenAI API, LM Studio
- **Chain-of-Thought reasoning**: Multi-step reasoning with hypothesis evaluation
- **Emotion detection**: Context-aware emotion analysis from text
- **Metacognition**: Self-awareness and strategy selection
- **Knowledge graph**: Structured relationships with causal reasoning

### Memory
- **Episodic memory**: Specific events with emotional context
- **Semantic memory**: Facts and concepts
- **Procedural memory**: Skills and routines
- **Conversation history**: JSONL append-only with rotation
- **Auto-learning**: Private reflection extracts durable lessons

### Tools (30+)
- **System**: Open apps, screenshots, battery, network, volume, clipboard
- **Files**: List, search, read, write, copy, move, delete
- **Web**: Search, fetch URLs, open browser, YouTube
- **Media**: Play, pause, next, previous, volume control
- **Assistant**: Tasks, reminders, notes, habits
- **Creative**: Image generation from prompts

### Personality
- **Professional mode**: Efficient, focused assistant
- **Companion mode**: Warm, playful, affectionate persona
- **Configurable**: Edit `personality/default.md` to customize

### Training
- **History export**: Convert conversations to training data
- **LoRA fine-tuning**: Apple Silicon MLX-based fine-tuning
- **Auto-learning**: Extracts lessons from every interaction

## Quick Start

### Prerequisites
- Python 3.10+
- Ollama (for local LLM) - [Install](https://ollama.ai)
- macOS users: `brew install piper` (optional, for neural TTS)

### Installation

```bash
cd purple-ultra AI
./run.sh install
```

### Run

```bash
# Interactive text mode
./run.sh

# Voice-first mode
./run.sh voice

# Run in background
./run.sh background

# Stop background process
./run.sh stop
```

### Windows
```cmd
run.bat install
run.bat
run.bat voice
```

## Configuration

Edit `config.toml` to customize:

```toml
[llm]
provider = "ollama"    # ollama, openai, lmstudio
model = "llama3:latest"
host = "http://127.0.0.1:11434"

[stt]
engine = "faster-whisper"
model = "Systran/faster-whisper-small.en"

[tts]
engine = "auto"        # auto, piper, say, pyttsx3

[personality]
mode = "professional"  # professional, companion
name = "Purple Ultra"
```

## Project Structure

```
purple-ultra AI/
├── main.py                    # Entry point
├── config.toml                # Configuration
├── purple_ultra/              # Core package
│   ├── config/                # Frozen dataclass config
│   ├── core/                  # Orchestrator, mood, brain
│   ├── brain/                 # LLM, emotion, thinking, knowledge
│   ├── voice/                 # STT, TTS, speaker recognition
│   ├── memory/                # Episodic, semantic, procedural
│   ├── tools/                 # Tool registry and execution
│   ├── personality/           # Persona management
│   └── utils/                 # Screen, assistant, training, repair
├── personality/               # Personality definition files
├── memory/                    # Persistent memory (auto-created)
├── data/                      # Knowledge graph, archives
├── models/                    # Local ML models
├── training/                  # Training data and output
├── generated/                 # Generated images, screenshots
└── logs/                      # Application logs
```

## Architecture

Purple Ultra AI uses a modular, pipeline-based architecture:

```
User Input -> VoiceIO -> Brain (LLM) -> ToolRunner -> VoiceIO -> Response
                  |                        |
                  v                        v
            MoodState              MemoryStore
            EmotionEngine          ThinkingEngine
            SpeakerRecognizer      KnowledgeGraph
```

Key design principles:
- **Frozen dataclasses** for immutable configuration
- **Plugin-based tool registry** for extensibility
- **Pipeline orchestration** with before/after hooks
- **Unified memory** with deduplication and rotation
- **Cross-platform** with platform-specific optimizations

## Available Tools

| Tool | Description | Dangerous |
|------|-------------|-----------|
| `open_app` | Open an application | No |
| `open_url` | Open URL in browser | No |
| `browser_search` | Search the web | No |
| `youtube_search` | Search YouTube | No |
| `youtube_play` | Play YouTube video | No |
| `media_control` | Control playback | No |
| `take_screenshot` | Capture screen | No |
| `generate_image` | Create SVG image | No |
| `web_search` | Search internet | No |
| `get_time` | Current date/time | No |
| `system_info` | System information | No |
| `get_clipboard` | Read clipboard | No |
| `set_clipboard` | Write clipboard | No |
| `list_dir` | List directory | No |
| `search_files` | Find files | No |
| `read_file` | Read text file | No |
| `write_file` | Write text file | **Yes** |
| `delete_file` | Delete file | **Yes** |
| `copy_file` | Copy file | No |
| `move_file` | Move file | No |
| `run_shell` | Execute command | **Yes** |
| `remember` | Store a fact | No |
| `add_note` | Save a note | No |
| `set_reminder` | Set reminder | No |
| `add_task` | Add to-do | No |
| `execute_code` | Run Python | **Yes** |
| `volume_control` | Adjust volume | No |
| `get_battery` | Battery status | No |
| `get_network` | Network info | No |

## Training

```bash
# Export conversation history
python -m purple_ultra.utils.training export

# Add manual examples
python -m purple_ultra.utils.training add-example --user "Hello" --assistant "Hi there!"

# Run LoRA fine-tuning (Apple Silicon)
python -m purple_ultra.utils.training train
```

## License

MIT
