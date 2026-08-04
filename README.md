# Purple Ultra AI v2.0.0

**Advanced Offline Voice Assistant** — Self-aware, self-learning, self-healing AI with 79 features, neural networks, and military-grade encryption.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Linux%20%7C%20Windows-purple.svg)]()
[![Version](https://img.shields.io/badge/Version-2.0.0-orange.svg)]()

---

## Quick Start

```bash
git clone https://github.com/refat189/purple-ultra-AI.git
cd purple-ultra-AI
./run.sh install
./run.sh
```

**Windows:** `run.bat install` then `run.bat`

That's it. No cloud. No API keys required. Fully offline.

---

## What Is This?

Purple Ultra AI is a fully offline voice assistant that:

- **Thinks** — Chain-of-thought reasoning, multi-step planning, hypothesis evaluation
- **Learns** — Auto-learns from every conversation, stores lessons permanently
- **Heals** — Detects and fixes its own errors automatically
- **Protects** — Military-grade encryption (AES-256, ChaCha20, RSA-2048)
- **Evolves** — Self-modifies its own code, creates new tools, writes plugins
- **Remembers** — Episodic, semantic, and procedural memory with auto-consolidation

---

## Features

| Category | What You Get |
|----------|-------------|
| **Brain** | Self-awareness, self-learning, self-modification, autonomous improvement |
| **Neural Network** | 17,555 neurons, 26M parameters, intent classification, pattern recognition |
| **Encryption** | AES-256-CTR, ChaCha20, RSA-2048, SHA-256, SHA-512, HMAC, PBKDF2, digital signatures |
| **Voice** | Offline STT (Whisper), multi-backend TTS, 18 mood profiles, speaker recognition |
| **79 Feature Modules** | Todo, notes, calendar, weather, news, crypto, stocks, fitness, recipes, image/video processing, and more |
| **240 Commands** | Neural thinking, reasoning, planning, self-heal, code analysis, and more |
| **Self-Heal** | Auto-detects and fixes errors, modification log, rollback support |
| **Cross-Platform** | macOS, Linux, Windows |

---

## Run Commands

```bash
./run.sh              # Interactive text mode (default)
./run.sh voice        # Voice-first mode
./run.sh background   # Run in background
./run.sh stop         # Stop background process
./run.sh status       # Show status
./run.sh install      # Install/reinstall dependencies
./run.sh clean        # Clean temporary files
```

---

## Chat Commands

Once running, type these:

### Basic
| Command | Description |
|---------|-------------|
| `help` | Show all available tools |
| `status` | System status |
| `time` | Current date/time |
| `mood` | Current mood |

### Brain
| Command | Description |
|---------|-------------|
| `think about <topic>` | Deep thinking |
| `reflect` | Self-reflection |
| `self aware` | Self-awareness status |
| `who are you` | Identity info |
| `curiosity` | Knowledge gaps |
| `autonomous` | Self-improvement status |
| `learn <fact>` | Teach something |
| `correct <wrong> -> <right>` | Correct a mistake |

### Self-Heal
| Command | Description |
|---------|-------------|
| `self heal` | Scan and fix issues |
| `auto repair` | Auto-repair scan |
| `health` | Health report |
| `log` | Modification log |
| `summary` | Modification summary |

### Code
| Command | Description |
|---------|-------------|
| `codebase` | Show project structure |
| `find code <query>` | Search code |
| `analyze code <file>` | Code analysis |
| `read source <file>` | Read source file |
| `optimize <file>` | Optimize file |

### Neural
| Command | Description |
|---------|-------------|
| `neural status` | Neural system info |
| `neural think <problem>` | Neural thinking |
| `neural reason <problem>` | Neural reasoning |
| `neural plan <goal>` | Neural planning |
| `neural cognitive` | Cognitive state |
| `embed <text>` | Store in memory |
| `search memory <query>` | Recall memories |
| `neural sentiment <text>` | Deep sentiment analysis |
| `neural intent <text>` | Intent classification |

### Utilities
| Command | Description |
|---------|-------------|
| `sentiment <text>` | Analyze sentiment |
| `todo add <task>` | Add task |
| `notes write <text>` | Save note |
| `plugins` | List plugins |
| `tasks` | Show scheduled tasks |

---

## Configuration

Edit `config.toml` to customize:

```toml
[assistant]
name = "Purple Ultra"
version = "2.0.0"

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

### LLM Options

| Provider | Setup |
|----------|-------|
| **Ollama** (recommended) | Install [Ollama](https://ollama.ai), run `ollama pull llama3` |
| **OpenAI** | Set `api_key` in config.toml |
| **LM Studio** | Install [LM Studio](https://lmstudio.ai), start server |
| **None** | Works without LLM (offline brain only) |

---

## Requirements

- **Python 3.10+**
- **Optional:** [Ollama](https://ollama.ai) for local LLM
- **Optional:** `brew install piper` for neural TTS (macOS)
- **Optional:** `pyttsx3` for cross-platform TTS fallback

Core dependencies install automatically with `./run.sh install`.

---

## Project Structure

```
purple-ultra-AI/
├── main.py                    # Entry point
├── config.toml                # Configuration
├── run.sh / run.bat           # Launchers
├── requirements.txt           # Python dependencies
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
├── keys/                      # Encryption keys (auto-created)
└── logs/                      # Application logs
```

---

## Features List (79 Modules)

### Core (20)
Marketplace, Scheduler, Scraper, API Builder, Database, Email, SSH, VPN, FTP, Music, Weather, News, QR Generator, PDF Tools, Encrypted Vault, Workflow Builder, Multi-Language, Todo Manager, Calendar, Docker Control

### System (20)
System Monitor, File Organizer, Backup Manager, Git Manager, Package Manager, Cron Scheduler, Data Analyzer, Text Processor, Image Processor, Audio Processor, Video Processor, Crypto Tracker, Stock Tracker, Fitness Tracker, Budget Manager, Recipe Manager, Book Library, Habit Tracker, Password Generator, Web Scraper

### Productivity (20)
Note Taker, Flashcard Deck, Pomodoro Timer, Clipboard Manager, Code Formatter, Regex Tester, JSON Editor, UUID Generator, Hash Calculator, Unit Converter, BMI Calculator, Loan Calculator, Tip Calculator, Dice Roller, Color Palette, ASCII Art, System Diagnostics, Word Counter, Cryptography, Network Tools

### Image (10)
Image Input, Image Analyzer, Image Finder, Image Generator, Image Editor, Image Filter, Image Diff, Image Collage, Image Watermark, Image Comparator

### Video (1)
Video Analyzer (metadata, frames, scenes, motion, quality)

### Encryption (8)
AI Protection, File Encryption, Secure Deletion, Key Manager, Digital Signatures, Hash Functions, HMAC Authentication, Key Derivation

---

## Architecture

```
User Input → VoiceIO → Brain (LLM) → ToolRunner → VoiceIO → Response
                |                        |
                v                        v
          MoodState              MemoryStore
          EmotionEngine          ThinkingEngine
          SpeakerRecognizer      KnowledgeGraph
          NeuralNetwork          SelfAwareness
          SelfLearning           SelfModification
```

---

## How It Works

1. **Input** — Text or voice input via VoiceIO
2. **Identify** — Speaker recognition detects who is talking
3. **Emotion** — Emotion engine analyzes sentiment
4. **Think** — Brain decides response using LLM + offline knowledge
5. **Act** — Tool runner executes any needed actions
6. **Learn** — System auto-learns from the interaction
7. **Heal** — Self-heal scans for issues after each turn
8. **Respond** — Voice or text output with appropriate mood

---

## License

MIT License — Copyright (c) 2026 Refat

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

See [LICENSE](LICENSE) for full text.
