# Purple Ultra AI v2.0.0

**Advanced Offline Voice Assistant** - Self-aware, self-learning, self-healing AI with 79 features, neural networks, and military-grade encryption.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-purple.svg)]()

## Quick Start (3 steps)

```bash
# 1. Clone
git clone https://github.com/refat189/purple-ultra-AI.git
cd purple-ultra-AI

# 2. Install
./run.sh install

# 3. Run
./run.sh
```

**Windows:** `run.bat install` then `run.bat`

## What You Get

| Category | Features |
|----------|----------|
| **Brain** | Self-awareness, self-learning, self-modification, autonomous improvement |
| **Neural** | 17,555 neurons, 26M params, intent classification, pattern recognition |
| **Encryption** | AES-256, ChaCha20, RSA-2048, SHA-256, HMAC, digital signatures |
| **Voice** | Offline STT (Whisper), multi-backend TTS, 18 mood profiles, speaker recognition |
| **79 Modules** | Todo, notes, calendar, weather, news, crypto, stocks, fitness, recipes, image/video processing, and more |
| **240 Commands** | Neural thinking, reasoning, planning, self-heal, code analysis, and more |
| **Self-Heal** | Auto-detects and fixes errors, modification log, rollback support |

## Commands

```bash
./run.sh              # Interactive text mode (default)
./run.sh voice        # Voice-first mode
./run.sh background   # Run in background
./run.sh stop         # Stop background process
./run.sh status       # Show status
./run.sh install      # Install/reinstall dependencies
```

## Chat Commands

Once running, try these:

| Command | Description |
|---------|-------------|
| `help` | Show all available tools |
| `status` | System status |
| `time` | Current date/time |
| `think about <topic>` | Deep thinking |
| `reflect` | Self-reflection |
| `self aware` | Self-awareness status |
| `who are you` | Identity info |
| `curiosity` | Knowledge gaps |
| `autonomous` | Self-improvement status |
| `self heal` | Scan and fix issues |
| `auto repair` | Auto-repair scan |
| `health` | Health report |
| `codebase` | Show project structure |
| `find code <query>` | Search code |
| `analyze code <file>` | Code analysis |
| `neural status` | Neural system info |
| `embed <text>` | Store in memory |
| `search memory <query>` | Recall memories |
| `sentiment <text>` | Analyze sentiment |
| `learn <fact>` | Teach something |
| `correct <wrong> -> <right>` | Correct a mistake |
| `todo add <task>` | Add task |
| `notes write <text>` | Save note |

## Configuration

Edit `config.toml`:

```toml
[llm]
provider = "ollama"           # ollama, openai, lmstudio
model = "llama3:latest"
host = "http://127.0.0.1:11434"

[tts]
engine = "auto"               # auto, piper, say, pyttsx3

[stt]
engine = "faster-whisper"
model = "Systran/faster-whisper-small.en"

[personality]
mode = "professional"         # professional, companion
name = "Purple Ultra"
```

## Requirements

- Python 3.10+
- Optional: [Ollama](https://ollama.ai) for local LLM
- Optional: `brew install piper` for neural TTS (macOS)

## Project Structure

```
purple-ultra-AI/
├── main.py                    # Entry point
├── config.toml                # Configuration
├── run.sh / run.bat           # Launchers
├── purple_ultra/
│   ├── core/                  # Orchestrator, brain, mood
│   ├── brain/                 # LLM, emotion, thinking, knowledge
│   ├── neural/                # Neural networks, embeddings, reasoning
│   ├── advanced/              # Multi-agent, RLHF, security
│   ├── voice/                 # STT, TTS, speaker recognition
│   ├── memory/                # Episodic, semantic, procedural
│   ├── tools/                 # 30+ built-in tools
│   ├── security/              # AES-256, ChaCha20, RSA encryption
│   ├── utils/                 # 79 feature modules
│   └── personality/           # Persona management
├── personality/               # Personality definition
├── memory/                    # Persistent data (auto-created)
└── logs/                      # Application logs
```

## Features List (79 Modules)

<details>
<summary>Click to expand full list</summary>

**Core (20):** Marketplace, Scheduler, Scraper, API Builder, Database, Email, SSH, VPN, FTP, Music, Weather, News, QR, PDF, Vault, Workflow, Language, Todo, Calendar, Docker

**System (20):** Monitor, File Organizer, Backup, Git, Packages, Cron, Analyzer, Text, Image, Audio, Video, Crypto, Stocks, Fitness, Budget, Recipes, Library, Habits, Password, Web Scraper

**Productivity (20):** Notes, Flashcards, Pomodoro, Clipboard, Formatter, Regex, JSON Editor, UUID, Hash, Units, BMI, Loan, Tip, Dice, Colors, ASCII Art, Diagnostics, Word Counter, Crypto Tools, Network Tools

**Image (10):** Input, Analyzer, Finder, Generator, Editor, Filter, Diff, Collage, Watermark, Comparator

**Video (1):** Video Analyzer (metadata, frames, scenes, motion, quality)

**Encryption (8):** AI Protection, File Encryption, Secure Deletion, Key Manager, Digital Signatures, Hash Functions, HMAC, Key Derivation

</details>

## Architecture

```
User Input → VoiceIO → Brain (LLM) → ToolRunner → VoiceIO → Response
                |                        |
                v                        v
          MoodState              MemoryStore
          EmotionEngine          ThinkingEngine
          SpeakerRecognizer      KnowledgeGraph
          NeuralNetwork          SelfAwareness
```

## License

MIT - Free to use, modify, and distribute.
