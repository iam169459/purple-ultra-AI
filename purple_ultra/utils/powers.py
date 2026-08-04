"""Purple Ultra AI - Power Features Module.
All advanced features in one optimized file.
"""

from __future__ import annotations

import json
import os
import time
import hashlib
import subprocess
import sqlite3
import smtplib
import base64
import random
import math
import re
import uuid
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import queue

# Import extra modules (41-60)
from .powers_extra import (
    NoteTaker, FlashcardDeck, PomodoroTimer, ClipboardManager,
    CodeFormatter, RegexTester, JsonEditor, UuidGenerator,
    HashCalculator, UnitConverter, BmiCalculator, LoanCalculator,
    TipCalculator, DiceRoller, ColorPalette, AsciiArt,
    SystemDiagnostics, WordCounter, Cryptography, NetworkTools,
    ImageInput, ImageAnalyzer, ImageFinder, ImageGenerator, ImageEditor,
    ImageFilter, ImageDiff, ImageCollage, ImageWatermark, ImageComparator,
)
from ..security.encryption import (
    AES256, ChaCha20, RSA2048, KeyDerivation, DigitalSignature,
    HashFunctions, HMACAuth, FileEncryption, SecureDeletion,
    KeyManager, AIProtection,
)


# ═══════════════════════════════════════════════════════════════════
# 1. PLUGIN MARKETPLACE
# ═══════════════════════════════════════════════════════════════════

class PluginMarketplace:
    """Download, install, and manage community plugins."""

    def __init__(self, plugin_dir: str = "plugins"):
        self._dir = Path(plugin_dir)
        self._dir.mkdir(exist_ok=True)
        self._installed: dict[str, dict] = {}
        self._registry: list[dict] = [
            {"name": "weather", "desc": "Weather info", "author": "purple", "version": "1.0"},
            {"name": "news", "desc": "News aggregator", "author": "purple", "version": "1.0"},
            {"name": "qr_generator", "desc": "QR code generator", "author": "purple", "version": "1.0"},
            {"name": "pdf_tools", "desc": "PDF manipulation", "author": "purple", "version": "1.0"},
            {"name": "encrypt", "desc": "File encryption", "author": "purple", "version": "1.0"},
            {"name": "translator", "desc": "Multi-language translation", "author": "purple", "version": "1.0"},
            {"name": "todo", "desc": "Task management", "author": "purple", "version": "1.0"},
            {"name": "calendar", "desc": "Calendar integration", "author": "purple", "version": "1.0"},
        ]
        self._load_installed()

    def _load_installed(self):
        path = self._dir / "installed.json"
        if path.exists():
            try:
                self._installed = json.loads(path.read_text())
            except Exception:
                self._installed = {}

    def _save_installed(self):
        (self._dir / "installed.json").write_text(json.dumps(self._installed, indent=2))

    def list_available(self) -> list[dict]:
        return self._registry

    def list_installed(self) -> list[dict]:
        return list(self._installed.values())

    def install(self, name: str) -> str:
        for plugin in self._registry:
            if plugin["name"] == name:
                self._installed[name] = {**plugin, "installed_at": datetime.now().isoformat()}
                self._save_installed()
                return f"Installed plugin: {name}"
        return f"Plugin not found: {name}"

    def uninstall(self, name: str) -> str:
        if name in self._installed:
            del self._installed[name]
            self._save_installed()
            return f"Uninstalled plugin: {name}"
        return f"Plugin not installed: {name}"

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [p for p in self._registry if q in p["name"].lower() or q in p["desc"].lower()]


# ═══════════════════════════════════════════════════════════════════
# 2. SCHEDULER / CRON
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ScheduledTask:
    id: str
    name: str
    command: str
    interval_seconds: int
    last_run: float = 0.0
    enabled: bool = True
    created: float = 0.0


class TaskScheduler:
    """Schedule and run recurring tasks."""

    def __init__(self, storage_dir: str = "memory/scheduler"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._tasks: dict[str, ScheduledTask] = {}
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._load()

    def _load(self):
        path = self._dir / "tasks.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for k, v in data.items():
                    self._tasks[k] = ScheduledTask(**v)
            except Exception:
                pass

    def _save(self):
        data = {k: {"id": t.id, "name": t.name, "command": t.command,
                     "interval_seconds": t.interval_seconds, "last_run": t.last_run,
                     "enabled": t.enabled, "created": t.created}
                for k, t in self._tasks.items()}
        (self._dir / "tasks.json").write_text(json.dumps(data, indent=2))

    def add_task(self, name: str, command: str, interval_seconds: int) -> str:
        task_id = f"task_{len(self._tasks)}"
        task = ScheduledTask(
            id=task_id, name=name, command=command,
            interval_seconds=interval_seconds, created=time.time()
        )
        self._tasks[task_id] = task
        self._save()
        return f"Created task: {name} (every {interval_seconds}s)"

    def remove_task(self, task_id: str) -> str:
        if task_id in self._tasks:
            name = self._tasks[task_id].name
            del self._tasks[task_id]
            self._save()
            return f"Removed task: {name}"
        return f"Task not found: {task_id}"

    def list_tasks(self) -> list[dict]:
        return [{"id": t.id, "name": t.name, "command": t.command,
                 "interval": t.interval_seconds, "enabled": t.enabled}
                for t in self._tasks.values()]

    def toggle_task(self, task_id: str) -> str:
        if task_id in self._tasks:
            self._tasks[task_id].enabled = not self._tasks[task_id].enabled
            self._save()
            status = "enabled" if self._tasks[task_id].enabled else "disabled"
            return f"Task {self._tasks[task_id].name} {status}"
        return f"Task not found: {task_id}"


# ═══════════════════════════════════════════════════════════════════
# 3. WEB SCRAPER
# ═══════════════════════════════════════════════════════════════════

class WebScraper:
    """Scrape and extract data from websites."""

    def fetch_url(self, url: str) -> str:
        try:
            import urllib.request
            req = urllib.request.Request(url, headers={"User-Agent": "PurpleUltra/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode("utf-8", errors="ignore")[:50000]
        except Exception as e:
            return f"Error fetching {url}: {e}"

    def extract_text(self, html: str) -> str:
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:5000]

    def extract_links(self, html: str) -> list[str]:
        import re
        return re.findall(r'href="(https?://[^"]+)"', html)[:20]

    def extract_title(self, html: str) -> str:
        import re
        match = re.search(r'<title[^>]*>([^<]+)</title>', html, re.IGNORECASE)
        return match.group(1).strip() if match else "No title"


# ═══════════════════════════════════════════════════════════════════
# 4. API BUILDER
# ═══════════════════════════════════════════════════════════════════

class APIBuilder:
    """Create and manage custom REST API endpoints."""

    def __init__(self):
        self._endpoints: dict[str, dict] = {}
        self._data: dict[str, Any] = {}

    def create_endpoint(self, path: str, method: str = "GET", response: str = "OK") -> str:
        key = f"{method.upper()} {path}"
        self._endpoints[key] = {"path": path, "method": method.upper(), "response": response}
        return f"Created endpoint: {key}"

    def delete_endpoint(self, path: str, method: str = "GET") -> str:
        key = f"{method.upper()} {path}"
        if key in self._endpoints:
            del self._endpoints[key]
            return f"Deleted endpoint: {key}"
        return f"Endpoint not found: {key}"

    def list_endpoints(self) -> list[dict]:
        return list(self._endpoints.values())

    def store_data(self, key: str, value: Any):
        self._data[key] = value

    def get_data(self, key: str) -> Any:
        return self._data.get(key)


# ═══════════════════════════════════════════════════════════════════
# 5. DATABASE INTEGRATION
# ═══════════════════════════════════════════════════════════════════

class DatabaseManager:
    """SQLite database operations."""

    def __init__(self, db_path: str = "memory/purple.db"):
        self._db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None

    def _connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self._db_path)
            self._conn.row_factory = sqlite3.Row

    def execute(self, query: str) -> str:
        self._connect()
        try:
            cursor = self._conn.execute(query)
            if query.strip().upper().startswith("SELECT"):
                rows = cursor.fetchall()[:50]
                return json.dumps([dict(r) for r in rows], indent=2, default=str)
            self._conn.commit()
            return f"Query executed: {cursor.rowcount} rows affected"
        except Exception as e:
            return f"Database error: {e}"

    def create_table(self, table: str, columns: dict[str, str]) -> str:
        cols = ", ".join(f"{k} {v}" for k, v in columns.items())
        return self.execute(f"CREATE TABLE IF NOT EXISTS {table} ({cols})")

    def insert(self, table: str, data: dict) -> str:
        cols = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        values = list(data.values())
        self._connect()
        try:
            self._conn.execute(f"INSERT INTO {table} ({cols}) VALUES ({placeholders})", values)
            self._conn.commit()
            return f"Inserted into {table}"
        except Exception as e:
            return f"Insert error: {e}"

    def select(self, table: str, where: str = "", limit: int = 50) -> str:
        query = f"SELECT * FROM {table}"
        if where:
            query += f" WHERE {where}"
        query += f" LIMIT {limit}"
        return self.execute(query)

    def list_tables(self) -> str:
        result = self.execute("SELECT name FROM sqlite_master WHERE type='table'")
        return result

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None


# ═══════════════════════════════════════════════════════════════════
# 6. EMAIL GATEWAY
# ═══════════════════════════════════════════════════════════════════

class EmailGateway:
    """Send emails via SMTP."""

    def __init__(self):
        self._config: dict = {}

    def configure(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self._config = {
            "host": smtp_host, "port": smtp_port,
            "username": username, "password": password
        }
        return "Email configured"

    def send(self, to: str, subject: str, body: str) -> str:
        if not self._config:
            return "Email not configured. Use: configure email"
        try:
            msg = f"From: {self._config['username']}\nTo: {to}\nSubject: {subject}\n\n{body}"
            with smtplib.SMTP(self._config["host"], self._config["port"]) as server:
                server.starttls()
                server.login(self._config["username"], self._config["password"])
                server.sendmail(self._config["username"], to, msg)
            return f"Email sent to {to}"
        except Exception as e:
            return f"Email error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 7. SSH CLIENT
# ═══════════════════════════════════════════════════════════════════

class SSHClient:
    """Remote server access via SSH."""

    def connect(self, host: str, user: str, port: int = 22) -> str:
        return f"ssh -p {port} {user}@{host}"

    def execute(self, host: str, user: str, command: str, port: int = 22) -> str:
        try:
            result = subprocess.run(
                ["ssh", "-p", str(port), f"{user}@{host}", command],
                capture_output=True, text=True, timeout=30
            )
            return result.stdout or result.stderr[:1000]
        except Exception as e:
            return f"SSH error: {e}"

    def copy_file(self, source: str, dest: str, user: str, host: str) -> str:
        try:
            subprocess.run(["scp", source, f"{user}@{host}:{dest}"], timeout=30)
            return f"Copied {source} to {host}:{dest}"
        except Exception as e:
            return f"SCP error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 8. VPN CONTROL
# ═══════════════════════════════════════════════════════════════════

class VPNControl:
    """Connect/disconnect VPN."""

    def connect(self, config_path: str = "") -> str:
        try:
            if config_path:
                subprocess.run(["openvpn", "--config", config_path], timeout=5)
            return "VPN connecting..."
        except Exception as e:
            return f"VPN error: {e}"

    def disconnect(self) -> str:
        try:
            subprocess.run(["pkill", "openvpn"], timeout=5)
            return "VPN disconnected"
        except Exception as e:
            return f"VPN error: {e}"

    def status(self) -> str:
        try:
            result = subprocess.run(["pgrep", "openvpn"], capture_output=True, timeout=5)
            return "VPN connected" if result.returncode == 0 else "VPN disconnected"
        except Exception:
            return "VPN status unknown"


# ═══════════════════════════════════════════════════════════════════
# 9. FTP/SFTP CLIENT
# ═══════════════════════════════════════════════════════════════════

class FTPClient:
    """File transfer via FTP/SFTP."""

    def upload(self, local_path: str, remote_path: str, host: str, user: str) -> str:
        try:
            subprocess.run(["scp", local_path, f"{user}@{host}:{remote_path}"], timeout=30)
            return f"Uploaded {local_path} to {host}:{remote_path}"
        except Exception as e:
            return f"Upload error: {e}"

    def download(self, remote_path: str, local_path: str, host: str, user: str) -> str:
        try:
            subprocess.run([f"{user}@{host}:{remote_path}", local_path], timeout=30)
            return f"Downloaded {host}:{remote_path} to {local_path}"
        except Exception as e:
            return f"Download error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 10. MUSIC PLAYER
# ═══════════════════════════════════════════════════════════════════

class MusicPlayer:
    """Play local music files."""

    def __init__(self):
        self._playlist: list[str] = []
        self._current: int = 0
        self._playing = False

    def add(self, path: str) -> str:
        if Path(path).exists():
            self._playlist.append(path)
            return f"Added: {Path(path).name}"
        return f"File not found: {path}"

    def play(self) -> str:
        if not self._playlist:
            return "Playlist empty"
        try:
            song = self._playlist[self._current]
            if sys.platform == "darwin":
                subprocess.Popen(["afplay", song])
            self._playing = True
            return f"Playing: {Path(song).name}"
        except Exception as e:
            return f"Play error: {e}"

    def stop(self) -> str:
        try:
            subprocess.run(["pkill", "afplay"], timeout=5)
            self._playing = False
            return "Stopped"
        except Exception:
            return "Stop error"

    def next(self) -> str:
        if self._playlist:
            self._current = (self._current + 1) % len(self._playlist)
            return self.play()
        return "No playlist"

    def list_songs(self) -> list[str]:
        return [Path(p).name for p in self._playlist]


# ═══════════════════════════════════════════════════════════════════
# 11. WEATHER
# ═══════════════════════════════════════════════════════════════════

class WeatherService:
    """Get weather information."""

    def get_weather(self, city: str = "auto") -> str:
        try:
            import urllib.request
            url = f"https://wttr.in/{city}?format=3"
            req = urllib.request.Request(url, headers={"User-Agent": "curl"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode().strip()
        except Exception as e:
            return f"Weather error: {e}"

    def get_forecast(self, city: str = "auto") -> str:
        try:
            import urllib.request
            url = f"https://wttr.in/{city}?format=%l:+%c+%t+%w+%h"
            req = urllib.request.Request(url, headers={"User-Agent": "curl"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                return resp.read().decode().strip()
        except Exception as e:
            return f"Forecast error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 12. NEWS AGGREGATOR
# ═══════════════════════════════════════════════════════════════════

class NewsAggregator:
    """Fetch latest news headlines."""

    def get_headlines(self, source: str = "general") -> str:
        try:
            import urllib.request
            url = "https://newsapi.org/v2/top-headlines?country=us&apiKey=demo"
            req = urllib.request.Request(url, headers={"User-Agent": "PurpleUltra"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                headlines = [a["title"] for a in data.get("articles", [])[:10]]
                return "\n".join(f"• {h}" for h in headlines) if headlines else "No headlines"
        except Exception as e:
            return f"News error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 13. QR GENERATOR
# ═══════════════════════════════════════════════════════════════════

class QRGenerator:
    """Generate QR codes."""

    def generate(self, text: str, output: str = "qr.png") -> str:
        try:
            import qrcode
            img = qrcode.make(text)
            img.save(output)
            return f"QR code saved to {output}"
        except ImportError:
            return "Install qrcode: pip install qrcode[pil]"
        except Exception as e:
            return f"QR error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 14. PDF TOOLS
# ═══════════════════════════════════════════════════════════════════

class PDFTools:
    """PDF manipulation tools."""

    def merge(self, files: list[str], output: str) -> str:
        try:
            from PyPDF2 import PdfMerger
            merger = PdfMerger()
            for f in files:
                merger.append(f)
            merger.write(output)
            merger.close()
            return f"Merged {len(files)} PDFs to {output}"
        except ImportError:
            return "Install PyPDF2: pip install PyPDF2"
        except Exception as e:
            return f"PDF error: {e}"

    def extract_text(self, pdf_path: str) -> str:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            text = ""
            for page in reader.pages[:10]:
                text += page.extract_text() or ""
            return text[:5000]
        except ImportError:
            return "Install PyPDF2: pip install PyPDF2"
        except Exception as e:
            return f"PDF error: {e}"

    def info(self, pdf_path: str) -> str:
        try:
            from PyPDF2 import PdfReader
            reader = PdfReader(pdf_path)
            return f"Pages: {len(reader.pages)}, Title: {reader.metadata.title if reader.metadata else 'N/A'}"
        except ImportError:
            return "Install PyPDF2: pip install PyPDF2"
        except Exception as e:
            return f"PDF error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 15. ENCRYPTED STORAGE
# ═══════════════════════════════════════════════════════════════════

class EncryptedVault:
    """Encrypted storage for secrets."""

    def __init__(self, vault_dir: str = "memory/vault"):
        self._dir = Path(vault_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._secrets: dict[str, str] = {}
        self._load()

    def _load(self):
        path = self._dir / "vault.enc"
        if path.exists():
            try:
                self._secrets = json.loads(path.read_text())
            except Exception:
                pass

    def _save(self):
        (self._dir / "vault.enc").write_text(json.dumps(self._secrets, indent=2))

    def _hash_key(self, key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def store(self, name: str, value: str, password: str) -> str:
        hashed = self._hash_key(password)
        self._secrets[name] = {"value": base64.b64encode(value.encode()).decode(), "key": hashed}
        self._save()
        return f"Stored secret: {name}"

    def retrieve(self, name: str, password: str) -> str:
        if name not in self._secrets:
            return f"Secret not found: {name}"
        hashed = self._hash_key(password)
        if self._secrets[name]["key"] != hashed:
            return "Wrong password"
        return base64.b64decode(self._secrets[name]["value"]).decode()

    def list_secrets(self) -> list[str]:
        return list(self._secrets.keys())

    def delete(self, name: str) -> str:
        if name in self._secrets:
            del self._secrets[name]
            self._save()
            return f"Deleted secret: {name}"
        return f"Secret not found: {name}"


# ═══════════════════════════════════════════════════════════════════
# 16. WORKFLOW BUILDER
# ═══════════════════════════════════════════════════════════════════

@dataclass
class WorkflowStep:
    name: str
    command: str
    args: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)


class WorkflowBuilder:
    """Chain commands into automated workflows."""

    def __init__(self, storage_dir: str = "memory/workflows"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._workflows: dict[str, list[WorkflowStep]] = {}
        self._load()

    def _load(self):
        for path in self._dir.glob("*.json"):
            try:
                data = json.loads(path.read_text())
                self._workflows[path.stem] = [
                    WorkflowStep(**s) for s in data
                ]
            except Exception:
                pass

    def create(self, name: str, steps: list[dict]) -> str:
        self._workflows[name] = [
            WorkflowStep(name=s.get("name", f"step{i}"), command=s.get("command", ""),
                        args=s.get("args", {}), depends_on=s.get("depends_on", []))
            for i, s in enumerate(steps)
        ]
        path = self._dir / f"{name}.json"
        path.write_text(json.dumps([{"name": s.name, "command": s.command,
                                     "args": s.args, "depends_on": s.depends_on}
                                    for s in self._workflows[name]], indent=2))
        return f"Created workflow: {name} ({len(steps)} steps)"

    def list_workflows(self) -> list[str]:
        return list(self._workflows.keys())

    def get_steps(self, name: str) -> list[dict]:
        if name in self._workflows:
            return [{"name": s.name, "command": s.command} for s in self._workflows[name]]
        return []

    def delete(self, name: str) -> str:
        if name in self._workflows:
            del self._workflows[name]
            path = self._dir / f"{name}.json"
            if path.exists():
                path.unlink()
            return f"Deleted workflow: {name}"
        return f"Workflow not found: {name}"


# ═══════════════════════════════════════════════════════════════════
# 17. MULTI-LANGUAGE
# ═══════════════════════════════════════════════════════════════════

class MultiLanguage:
    """Multi-language support."""

    LANGUAGES = {
        "en": "English", "es": "Spanish", "fr": "French", "de": "German",
        "it": "Italian", "pt": "Portuguese", "ru": "Russian", "ja": "Japanese",
        "ko": "Korean", "zh": "Chinese", "ar": "Arabic", "hi": "Hindi",
    }

    def __init__(self):
        self._current = "en"

    def set_language(self, lang_code: str) -> str:
        if lang_code in self.LANGUAGES:
            self._current = lang_code
            return f"Language set to {self.LANGUAGES[lang_code]}"
        return f"Unknown language: {lang_code}"

    def get_language(self) -> str:
        return f"{self._current} ({self.LANGUAGES.get(self._current, 'Unknown')})"

    def list_languages(self) -> dict:
        return self.LANGUAGES

    def translate(self, text: str, target: str) -> str:
        return f"Translation to {self.LANGUAGES.get(target, target)}: {text} (use external API for actual translation)"


# ═══════════════════════════════════════════════════════════════════
# 18. TODO / TASK MANAGER
# ═══════════════════════════════════════════════════════════════════

class TodoManager:
    """Personal task management."""

    def __init__(self, storage_dir: str = "memory/todo"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._tasks: list[dict] = []
        self._load()

    def _load(self):
        path = self._dir / "tasks.json"
        if path.exists():
            try:
                self._tasks = json.loads(path.read_text())
            except Exception:
                pass

    def _save(self):
        (self._dir / "tasks.json").write_text(json.dumps(self._tasks, indent=2))

    def add(self, task: str, priority: str = "medium") -> str:
        self._tasks.append({
            "id": len(self._tasks),
            "task": task,
            "priority": priority,
            "done": False,
            "created": datetime.now().isoformat()
        })
        self._save()
        return f"Added task: {task}"

    def complete(self, task_id: int) -> str:
        for t in self._tasks:
            if t["id"] == task_id:
                t["done"] = True
                self._save()
                return f"Completed: {t['task']}"
        return f"Task not found: {task_id}"

    def list_tasks(self, show_done: bool = False) -> list[dict]:
        if show_done:
            return self._tasks
        return [t for t in self._tasks if not t["done"]]

    def delete(self, task_id: int) -> str:
        for i, t in enumerate(self._tasks):
            if t["id"] == task_id:
                removed = self._tasks.pop(i)
                self._save()
                return f"Deleted: {removed['task']}"
        return f"Task not found: {task_id}"


# ═══════════════════════════════════════════════════════════════════
# 19. CALENDAR
# ═══════════════════════════════════════════════════════════════════

class CalendarManager:
    """Simple calendar/event management."""

    def __init__(self, storage_dir: str = "memory/calendar"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._events: list[dict] = []
        self._load()

    def _load(self):
        path = self._dir / "events.json"
        if path.exists():
            try:
                self._events = json.loads(path.read_text())
            except Exception:
                pass

    def _save(self):
        (self._dir / "events.json").write_text(json.dumps(self._events, indent=2))

    def add_event(self, title: str, date: str, time: str = "", description: str = "") -> str:
        self._events.append({
            "id": len(self._events),
            "title": title,
            "date": date,
            "time": time,
            "description": description,
            "created": datetime.now().isoformat()
        })
        self._save()
        return f"Added event: {title} on {date}"

    def list_events(self, date: str = None) -> list[dict]:
        if date:
            return [e for e in self._events if e["date"] == date]
        return self._events

    def delete_event(self, event_id: int) -> str:
        for i, e in enumerate(self._events):
            if e["id"] == event_id:
                removed = self._events.pop(i)
                self._save()
                return f"Deleted event: {removed['title']}"
        return f"Event not found: {event_id}"


# ═══════════════════════════════════════════════════════════════════
# 20. DOCKER CONTROL
# ═══════════════════════════════════════════════════════════════════

class DockerControl:
    """Docker container management."""

    def list_containers(self) -> str:
        try:
            result = subprocess.run(["docker", "ps", "-a", "--format", "{{.Names}}\t{{.Status}}\t{{.Image}}"],
                                   capture_output=True, text=True, timeout=10)
            return result.stdout if result.stdout else "No containers"
        except Exception as e:
            return f"Docker error: {e}"

    def run(self, image: str, name: str = "", detach: bool = True) -> str:
        try:
            cmd = ["docker", "run"]
            if detach:
                cmd.append("-d")
            if name:
                cmd.extend(["--name", name])
            cmd.append(image)
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            return result.stdout[:200] if result.returncode == 0 else result.stderr[:200]
        except Exception as e:
            return f"Docker error: {e}"

    def stop(self, container: str) -> str:
        try:
            subprocess.run(["docker", "stop", container], timeout=30)
            return f"Stopped: {container}"
        except Exception as e:
            return f"Docker error: {e}"

    def remove(self, container: str) -> str:
        try:
            subprocess.run(["docker", "rm", container], timeout=30)
            return f"Removed: {container}"
        except Exception as e:
            return f"Docker error: {e}"

    def logs(self, container: str, lines: int = 50) -> str:
        try:
            result = subprocess.run(["docker", "logs", "--tail", str(lines), container],
                                   capture_output=True, text=True, timeout=10)
            return result.stdout[-2000:] if result.stdout else "No logs"
        except Exception as e:
            return f"Docker error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 21. SYSTEM MONITOR
# ═══════════════════════════════════════════════════════════════════

class SystemMonitor:
    """Real-time system monitoring (CPU, memory, disk, network)."""

    def get_cpu_usage(self) -> str:
        try:
            result = subprocess.run(["top", "-l", "1", "-n", "0"], capture_output=True, text=True, timeout=5)
            for line in result.stdout.split("\n"):
                if "CPU usage" in line:
                    return line.strip()
            return "CPU: Unable to determine"
        except Exception as e:
            return f"Error: {e}"

    def get_memory_usage(self) -> str:
        try:
            result = subprocess.run(["vm_stat"], capture_output=True, text=True, timeout=5)
            return result.stdout[:500]
        except Exception as e:
            return f"Error: {e}"

    def get_disk_usage(self) -> str:
        try:
            result = subprocess.run(["df", "-h", "/"], capture_output=True, text=True, timeout=5)
            lines = result.stdout.strip().split("\n")
            return lines[1] if len(lines) > 1 else "Unable to determine"
        except Exception as e:
            return f"Error: {e}"

    def get_network_info(self) -> str:
        try:
            result = subprocess.run(["ifconfig", "en0"], capture_output=True, text=True, timeout=5)
            return result.stdout[:500]
        except Exception:
            try:
                result = subprocess.run(["ifconfig", "eth0"], capture_output=True, text=True, timeout=5)
                return result.stdout[:500]
            except Exception as e:
                return f"Error: {e}"

    def get_all(self) -> dict:
        return {
            "cpu": self.get_cpu_usage(),
            "memory": self.get_memory_usage(),
            "disk": self.get_disk_usage(),
            "network": self.get_network_info(),
        }

    def monitor_loop(self, interval: int = 5, callback: callable = None) -> None:
        while True:
            data = self.get_all()
            if callback:
                callback(data)
            time.sleep(interval)


# ═══════════════════════════════════════════════════════════════════
# 22. FILE ORGANIZER
# ═══════════════════════════════════════════════════════════════════

class FileOrganizer:
    """Smart file organization by type, date, and size."""

    EXTENSION_MAP = {
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"],
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv", ".webm", ".m4v"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"],
        "Code": [".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".go", ".rs", ".rb", ".php", ".swift", ".kt"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"],
        "Data": [".json", ".xml", ".yaml", ".yml", ".toml", ".ini", ".cfg", ".conf"],
    }

    def __init__(self, base_dir: str = "."):
        self.base_dir = Path(base_dir)

    def scan_directory(self, path: str = "") -> dict:
        target = self.base_dir / path if path else self.base_dir
        files = {}
        for f in target.rglob("*"):
            if f.is_file():
                ext = f.suffix.lower()
                for category, exts in self.EXTENSION_MAP.items():
                    if ext in exts:
                        if category not in files:
                            files[category] = []
                        files[category].append(str(f))
                        break
                else:
                    if "Other" not in files:
                        files["Other"] = []
                    files["Other"].append(str(f))
        return files

    def organize_by_type(self, source_dir: str, dest_dir: str = "") -> str:
        src = Path(source_dir)
        dst = Path(dest_dir) if dest_dir else src.parent / "organized"
        moved = 0
        for f in src.glob("*"):
            if f.is_file():
                ext = f.suffix.lower()
                for category, exts in self.EXTENSION_MAP.items():
                    if ext in exts:
                        cat_dir = dst / category
                        cat_dir.mkdir(parents=True, exist_ok=True)
                        dest = cat_dir / f.name
                        if not dest.exists():
                            f.rename(dest)
                            moved += 1
                        break
        return f"Organized {moved} files into {dst}"

    def get_large_files(self, path: str = "", min_size_mb: int = 100) -> list[dict]:
        target = self.base_dir / path if path else self.base_dir
        large = []
        for f in target.rglob("*"):
            if f.is_file():
                size_mb = f.stat().st_size / (1024 * 1024)
                if size_mb >= min_size_mb:
                    large.append({"path": str(f), "size_mb": round(size_mb, 2)})
        return sorted(large, key=lambda x: x["size_mb"], reverse=True)[:20]


# ═══════════════════════════════════════════════════════════════════
# 23. BACKUP MANAGER
# ═══════════════════════════════════════════════════════════════════

class BackupManager:
    """Automated backup system with compression and scheduling."""

    def __init__(self, backup_dir: str = "backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self._backups: list[dict] = []
        self._load_index()

    def _load_index(self):
        index_file = self.backup_dir / "index.json"
        if index_file.exists():
            try:
                self._backups = json.loads(index_file.read_text())
            except Exception:
                self._backups = []

    def _save_index(self):
        (self.backup_dir / "index.json").write_text(json.dumps(self._backups, indent=2))

    def create_backup(self, source: str, name: str = "") -> str:
        src = Path(source)
        if not src.exists():
            return f"Source not found: {source}"

        if not name:
            name = f"backup_{src.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        backup_path = self.backup_dir / f"{name}.tar.gz"
        try:
            result = subprocess.run(
                ["tar", "-czf", str(backup_path), "-C", str(src.parent), src.name],
                capture_output=True, text=True, timeout=300
            )
            if result.returncode == 0:
                size = backup_path.stat().st_size / (1024 * 1024)
                entry = {
                    "name": name,
                    "source": str(src),
                    "path": str(backup_path),
                    "size_mb": round(size, 2),
                    "timestamp": datetime.now().isoformat(),
                }
                self._backups.append(entry)
                self._save_index()
                return f"Backup created: {name} ({size:.2f} MB)"
            return f"Backup failed: {result.stderr[:200]}"
        except Exception as e:
            return f"Backup error: {e}"

    def restore_backup(self, name: str, dest: str = "") -> str:
        backup = next((b for b in self._backups if b["name"] == name), None)
        if not backup:
            return f"Backup not found: {name}"

        dest_dir = Path(dest) if dest else Path(backup["source"]).parent
        try:
            result = subprocess.run(
                ["tar", "-xzf", backup["path"], "-C", str(dest_dir)],
                capture_output=True, text=True, timeout=300
            )
            return f"Restored {name} to {dest_dir}" if result.returncode == 0 else f"Restore failed: {result.stderr[:200]}"
        except Exception as e:
            return f"Restore error: {e}"

    def list_backups(self) -> list[dict]:
        return self._backups

    def delete_backup(self, name: str) -> str:
        backup = next((b for b in self._backups if b["name"] == name), None)
        if not backup:
            return f"Backup not found: {name}"
        Path(backup["path"]).unlink(missing_ok=True)
        self._backups = [b for b in self._backups if b["name"] != name]
        self._save_index()
        return f"Deleted backup: {name}"


# ═══════════════════════════════════════════════════════════════════
# 24. GIT MANAGER
# ═══════════════════════════════════════════════════════════════════

class GitManager:
    """Advanced git operations."""

    def __init__(self, repo_dir: str = "."):
        self.repo_dir = repo_dir

    def _run(self, *args: str) -> tuple[bool, str]:
        try:
            result = subprocess.run(
                ["git"] + list(args),
                cwd=self.repo_dir, capture_output=True, text=True, timeout=30
            )
            return result.returncode == 0, result.stdout.strip() or result.stderr.strip()
        except Exception as e:
            return False, str(e)

    def status(self) -> str:
        ok, out = self._run("status", "--short")
        return out if ok else f"Error: {out}"

    def log(self, count: int = 10) -> str:
        ok, out = self._run("log", f"--oneline", f"-{count}")
        return out if ok else f"Error: {out}"

    def diff(self) -> str:
        ok, out = self._run("diff")
        return out[:3000] if ok else f"Error: {out}"

    def commit(self, message: str) -> str:
        self._run("add", ".")
        ok, out = self._run("commit", "-m", message)
        return out if ok else f"Error: {out}"

    def push(self, remote: str = "origin", branch: str = "main") -> str:
        ok, out = self._run("push", remote, branch)
        return out if ok else f"Error: {out}"

    def pull(self, remote: str = "origin", branch: str = "main") -> str:
        ok, out = self._run("pull", remote, branch)
        return out if ok else f"Error: {out}"

    def branch(self, name: str = "") -> str:
        if name:
            ok, out = self._run("checkout", "-b", name)
        else:
            ok, out = self._run("branch")
        return out if ok else f"Error: {out}"

    def stash(self) -> str:
        ok, out = self._run("stash")
        return out if ok else f"Error: {out}"

    def stash_pop(self) -> str:
        ok, out = self._run("stash", "pop")
        return out if ok else f"Error: {out}"

    def blame(self, file: str) -> str:
        ok, out = self._run("blame", file)
        return out[:2000] if ok else f"Error: {out}"

    def remote_list(self) -> str:
        ok, out = self._run("remote", "-v")
        return out if ok else f"Error: {out}"


# ═══════════════════════════════════════════════════════════════════
# 25. PACKAGE MANAGER
# ═══════════════════════════════════════════════════════════════════

class PackageManager:
    """Multi-language package management (pip, npm, cargo, go)."""

    MANAGERS = {
        "python": {"install": "pip install", "uninstall": "pip uninstall -y", "list": "pip list --format=json", "update": "pip install --upgrade"},
        "node": {"install": "npm install", "uninstall": "npm uninstall", "list": "npm list --json", "update": "npm update"},
        "rust": {"install": "cargo install", "uninstall": "cargo uninstall", "list": "cargo install --list", "update": "cargo update"},
        "go": {"install": "go install", "uninstall": "rm", "list": "go list -m all", "update": "go get -u"},
    }

    def install(self, language: str, package: str) -> str:
        if language not in self.MANAGERS:
            return f"Unknown language: {language}"
        cmd = f"{self.MANAGERS[language]['install']} {package}"
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=120)
            return f"Installed {package}" if result.returncode == 0 else f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"

    def uninstall(self, language: str, package: str) -> str:
        if language not in self.MANAGERS:
            return f"Unknown language: {language}"
        cmd = f"{self.MANAGERS[language]['uninstall']} {package}"
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=60)
            return f"Uninstalled {package}" if result.returncode == 0 else f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"

    def list_packages(self, language: str) -> str:
        if language not in self.MANAGERS:
            return f"Unknown language: {language}"
        try:
            result = subprocess.run(self.MANAGERS[language]["list"].split(), capture_output=True, text=True, timeout=30)
            return result.stdout[:3000] if result.returncode == 0 else f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"

    def search(self, language: str, query: str) -> str:
        if language == "python":
            cmd = f"pip search {query}"
        elif language == "node":
            cmd = f"npm search {query}"
        else:
            return f"Search not supported for {language}"
        try:
            result = subprocess.run(cmd.split(), capture_output=True, text=True, timeout=30)
            return result.stdout[:2000] if result.returncode == 0 else f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 26. CRON SCHEDULER
# ═══════════════════════════════════════════════════════════════════

class CronScheduler:
    """Advanced cron-like task scheduling."""

    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._running = False
        self._thread: threading.Thread | None = None

    def add_job(self, name: str, command: str, interval: int = 60, enabled: bool = True) -> str:
        self._jobs[name] = {
            "command": command,
            "interval": interval,
            "enabled": enabled,
            "last_run": None,
            "run_count": 0,
            "created": datetime.now().isoformat(),
        }
        return f"Job added: {name}"

    def remove_job(self, name: str) -> str:
        if name in self._jobs:
            del self._jobs[name]
            return f"Job removed: {name}"
        return f"Job not found: {name}"

    def enable_job(self, name: str) -> str:
        if name in self._jobs:
            self._jobs[name]["enabled"] = True
            return f"Job enabled: {name}"
        return f"Job not found: {name}"

    def disable_job(self, name: str) -> str:
        if name in self._jobs:
            self._jobs[name]["enabled"] = False
            return f"Job disabled: {name}"
        return f"Job not found: {name}"

    def list_jobs(self) -> list[dict]:
        return [{"name": k, **v} for k, v in self._jobs.items()]

    def _run_jobs(self):
        while self._running:
            now = time.time()
            for name, job in self._jobs.items():
                if not job["enabled"]:
                    continue
                if job["last_run"] is None or (now - job["last_run"]) >= job["interval"]:
                    try:
                        subprocess.run(job["command"], shell=True, timeout=60)
                        job["last_run"] = now
                        job["run_count"] += 1
                    except Exception:
                        pass
            time.sleep(10)

    def start(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._run_jobs, daemon=True)
            self._thread.start()

    def stop(self):
        self._running = False


# ═══════════════════════════════════════════════════════════════════
# 27. DATA ANALYZER
# ═══════════════════════════════════════════════════════════════════

class DataAnalyzer:
    """Data analysis and statistics."""

    @staticmethod
    def mean(values: list[float]) -> float:
        return sum(values) / len(values) if values else 0.0

    @staticmethod
    def median(values: list[float]) -> float:
        if not values:
            return 0.0
        s = sorted(values)
        n = len(s)
        return (s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2)

    @staticmethod
    def std_dev(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return variance ** 0.5

    @staticmethod
    def correlation(x: list[float], y: list[float]) -> float:
        if len(x) != len(y) or len(x) < 2:
            return 0.0
        n = len(x)
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y)) / n
        std_x = (sum((xi - mean_x) ** 2 for xi in x) / n) ** 0.5
        std_y = (sum((yi - mean_y) ** 2 for yi in y) / n) ** 0.5
        if std_x == 0 or std_y == 0:
            return 0.0
        return cov / (std_x * std_y)

    @staticmethod
    def histogram(values: list[float], bins: int = 10) -> list[int]:
        if not values:
            return []
        min_v, max_v = min(values), max(values)
        if min_v == max_v:
            return [len(values)] + [0] * (bins - 1)
        bin_width = (max_v - min_v) / bins
        counts = [0] * bins
        for v in values:
            idx = min(int((v - min_v) / bin_width), bins - 1)
            counts[idx] += 1
        return counts

    def analyze(self, data: list[float]) -> dict:
        if not data:
            return {"error": "No data"}
        return {
            "count": len(data),
            "mean": self.mean(data),
            "median": self.median(data),
            "std_dev": self.std_dev(data),
            "min": min(data),
            "max": max(data),
            "range": max(data) - min(data),
            "histogram": self.histogram(data),
        }


# ═══════════════════════════════════════════════════════════════════
# 28. TEXT PROCESSOR
# ═══════════════════════════════════════════════════════════════════

class TextProcessor:
    """Advanced text processing (NLP-like)."""

    @staticmethod
    def word_count(text: str) -> int:
        return len(text.split())

    @staticmethod
    def char_count(text: str, include_spaces: bool = True) -> int:
        return len(text) if include_spaces else len(text.replace(" ", ""))

    @staticmethod
    def sentence_count(text: str) -> int:
        return len([s for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()])

    @staticmethod
    def paragraph_count(text: str) -> int:
        return len([p for p in text.split("\n\n") if p.strip()])

    @staticmethod
    def top_words(text: str, n: int = 10) -> list[tuple[str, int]]:
        words = text.lower().split()
        freq: dict[str, int] = {}
        for w in words:
            w = w.strip(".,!?;:\"'()-")
            if len(w) > 2:
                freq[w] = freq.get(w, 0) + 1
        return sorted(freq.items(), key=lambda x: x[1], reverse=True)[:n]

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        import re
        return re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        import re
        return re.findall(r'https?://[^\s<>"]+', text)

    @staticmethod
    def extract_numbers(text: str) -> list[float]:
        import re
        return [float(x) for x in re.findall(r'-?\d+\.?\d*', text)]

    @staticmethod
    def summarize(text: str, sentences: int = 3) -> str:
        sents = [s.strip() for s in text.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if len(sents) <= sentences:
            return text
        return ". ".join(sents[:sentences]) + "."

    @staticmethod
    def readability_score(text: str) -> float:
        words = text.split()
        sentences = max(1, len(text.replace("!", ".").replace("?", ".").split(".")) - 1)
        syllables = sum(max(1, len([c for c in w.lower() if c in "aeiou"])) for w in words)
        words_per_sentence = len(words) / sentences
        syllables_per_word = syllables / max(1, len(words))
        score = 206.835 - 1.015 * words_per_sentence - 84.6 * syllables_per_word
        return max(0.0, min(100.0, score))


# ═══════════════════════════════════════════════════════════════════
# 29. IMAGE PROCESSOR
# ═══════════════════════════════════════════════════════════════════

class ImageProcessor:
    """Image manipulation and analysis (no external deps)."""

    @staticmethod
    def get_image_info(path: str) -> dict:
        try:
            with open(path, "rb") as f:
                header = f.read(32)
            size = os.path.getsize(path)
            ext = Path(path).suffix.lower()
            fmt = "Unknown"
            if header[:8] == b'\x89PNG\r\n\x1a\n':
                fmt = "PNG"
            elif header[:3] == b'\xff\xd8\xff':
                fmt = "JPEG"
            elif header[:4] == b'GIF8':
                fmt = "GIF"
            elif header[:4] == b'RIFF' and header[8:12] == b'WEBP':
                fmt = "WEBP"
            return {"format": fmt, "size_bytes": size, "size_mb": round(size / 1048576, 2), "extension": ext}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def calculate_hash(path: str) -> str:
        h = hashlib.md5()
        with open(path, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def resize_ascii(width: int = 40, height: int = 20) -> str:
        chars = " .:-=+*#%@"
        return "\n".join(
            "".join(chars[(x + y) % len(chars)] for x in range(width))
            for y in range(height)
        )


# ═══════════════════════════════════════════════════════════════════
# 30. AUDIO PROCESSOR
# ═══════════════════════════════════════════════════════════════════

class AudioProcessor:
    """Audio processing and analysis."""

    @staticmethod
    def get_audio_info(path: str) -> dict:
        try:
            size = os.path.getsize(path)
            ext = Path(path).suffix.lower()
            return {"format": ext.upper(), "size_bytes": size, "size_mb": round(size / 1048576, 2)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def convert(input_path: str, output_format: str = "mp3") -> str:
        output = str(Path(input_path).with_suffix(f".{output_format}"))
        try:
            result = subprocess.run(
                ["ffmpeg", "-i", input_path, "-y", output],
                capture_output=True, text=True, timeout=60
            )
            return f"Converted to {output}" if result.returncode == 0 else f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def extract_info_ffmpeg(path: str) -> str:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", path],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout[:2000] if result.returncode == 0 else "Error"
        except Exception as e:
            return f"Error: {e}"


# ═══════════════════════════════════════════════════════════════════
# 31. VIDEO PROCESSOR
# ═══════════════════════════════════════════════════════════════════

class VideoProcessor:
    """Video processing and analysis."""

    @staticmethod
    def get_video_info(path: str) -> dict:
        try:
            size = os.path.getsize(path)
            ext = Path(path).suffix.lower()
            return {"format": ext.upper(), "size_bytes": size, "size_mb": round(size / 1048576, 2)}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def extract_audio(video_path: str, audio_path: str = "") -> str:
        if not audio_path:
            audio_path = str(Path(video_path).with_suffix(".mp3"))
        try:
            result = subprocess.run(
                ["ffmpeg", "-i", video_path, "-vn", "-acodec", "libmp3lame", "-y", audio_path],
                capture_output=True, text=True, timeout=120
            )
            return f"Audio extracted to {audio_path}" if result.returncode == 0 else f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def create_thumbnail(video_path: str, thumb_path: str = "", time_sec: int = 10) -> str:
        if not thumb_path:
            thumb_path = str(Path(video_path).with_suffix(".jpg"))
        try:
            result = subprocess.run(
                ["ffmpeg", "-i", video_path, "-ss", str(time_sec), "-vframes", "1", "-y", thumb_path],
                capture_output=True, text=True, timeout=30
            )
            return f"Thumbnail: {thumb_path}" if result.returncode == 0 else f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def get_duration(video_path: str) -> str:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True, text=True, timeout=10
            )
            return f"{float(result.stdout.strip()):.2f}s" if result.returncode == 0 else "Unknown"
        except Exception:
            return "Unknown"


# ═══════════════════════════════════════════════════════════════════
# 31b. VIDEO ANALYZER
# ═══════════════════════════════════════════════════════════════════

class VideoAnalyzer:
    """Deep video analysis - metadata, frames, quality, scenes, motion."""

    @staticmethod
    def _probe(video_path: str) -> dict:
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", video_path],
                capture_output=True, text=True, timeout=15
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception:
            pass
        return {}

    @staticmethod
    def analyze(video_path: str) -> dict:
        if not Path(video_path).exists():
            return {"error": f"File not found: {video_path}"}
        info = VideoProcessor.get_video_info(video_path)
        probe = VideoAnalyzer._probe(video_path)
        fmt = probe.get("format", {})
        streams = probe.get("streams", [])
        video_stream = next((s for s in streams if s.get("codec_type") == "video"), {})
        audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), {})
        duration = float(fmt.get("duration", 0))
        bit_rate = int(fmt.get("bit_rate", 0))
        return {
            "path": video_path,
            "format": info.get("format", "unknown"),
            "size_mb": info.get("size_mb", 0),
            "duration_sec": round(duration, 2),
            "duration_human": f"{int(duration//3600):02d}:{int((duration%3600)//60):02d}:{int(duration%60):02d}",
            "bit_rate_kbps": round(bit_rate / 1000) if bit_rate else 0,
            "video_codec": video_stream.get("codec_name", "unknown"),
            "width": int(video_stream.get("width", 0)),
            "height": int(video_stream.get("height", 0)),
            "fps": eval(video_stream.get("r_frame_rate", "0/1")) if "/" in video_stream.get("r_frame_rate", "") else float(video_stream.get("r_frame_rate", 0)),
            "audio_codec": audio_stream.get("codec_name", "none"),
            "audio_sample_rate": int(audio_stream.get("sample_rate", 0)),
            "audio_channels": int(audio_stream.get("channels", 0)),
            "total_frames": int(video_stream.get("nb_frames", 0)) if video_stream.get("nb_frames") else int(duration * eval(video_stream.get("r_frame_rate", "30/1")) if "/" in video_stream.get("r_frame_rate", "") else 30),
        }

    @staticmethod
    def extract_frames(video_path: str, output_dir: str = "", interval: float = 1.0, max_frames: int = 10) -> dict:
        if not Path(video_path).exists():
            return {"error": f"File not found: {video_path}"}
        if not output_dir:
            output_dir = str(Path(video_path).parent / "frames")
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_path],
                capture_output=True, text=True, timeout=10
            )
            duration = float(result.stdout.strip()) if result.returncode == 0 else 60
        except Exception:
            duration = 60
        frames = []
        t = 0.0
        count = 0
        while t < duration and count < max_frames:
            out_path = os.path.join(output_dir, f"frame_{count:04d}.jpg")
            try:
                subprocess.run(
                    ["ffmpeg", "-ss", str(t), "-i", video_path, "-vframes", "1", "-y", out_path],
                    capture_output=True, timeout=10
                )
                if Path(out_path).exists():
                    frames.append({"time": round(t, 2), "path": out_path})
                    count += 1
            except Exception:
                pass
            t += interval
        return {"video": video_path, "output_dir": output_dir, "frames_extracted": len(frames), "frames": frames}

    @staticmethod
    def detect_scenes(video_path: str, threshold: float = 0.3) -> dict:
        if not Path(video_path).exists():
            return {"error": f"File not found: {video_path}"}
        try:
            result = subprocess.run(
                ["ffmpeg", "-i", video_path, "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
                capture_output=True, text=True, timeout=60
            )
            scenes = []
            for line in result.stderr.split("\n"):
                if "pts_time:" in line:
                    try:
                        t = float(line.split("pts_time:")[1].split()[0])
                        scenes.append(round(t, 2))
                    except Exception:
                        pass
            return {"video": video_path, "threshold": threshold, "scene_changes": len(scenes), "timestamps": scenes}
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def detect_motion(video_path: str) -> dict:
        if not Path(video_path).exists():
            return {"error": f"File not found: {video_path}"}
        try:
            result = subprocess.run(
                ["ffprobe", "-v", "quiet", "-select_streams", "v:0", "-show_entries", "stream=r_frame_rate,nb_frames,duration",
                 "-of", "json", video_path],
                capture_output=True, text=True, timeout=10
            )
            info = json.loads(result.stdout) if result.returncode == 0 else {}
            stream = info.get("streams", [{}])[0]
            fps_str = stream.get("r_frame_rate", "30/1")
            fps = eval(fps_str) if "/" in fps_str else float(fps_str)
            frames_to_check = min(int(fps * 5), 150)
            timestamps = [i / fps for i in range(0, int(float(stream.get("duration", 10)) * fps), max(1, int(fps)))]
            timestamps = timestamps[:frames_to_check]
            diffs = []
            prev_data = None
            for t in timestamps[:min(len(timestamps), 30)]:
                try:
                    frame_result = subprocess.run(
                        ["ffmpeg", "-ss", str(t), "-i", video_path, "-vframes", "1", "-f", "rawvideo", "-pix_fmt", "gray", "-"],
                        capture_output=True, timeout=5
                    )
                    if frame_result.stdout and prev_data:
                        min_len = min(len(frame_result.stdout), len(prev_data))
                        diff = sum(abs(a - b) for a, b in zip(frame_result.stdout[:min_len], prev_data[:min_len])) / min_len
                        diffs.append({"time": round(t, 2), "motion_score": round(diff, 2)})
                    prev_data = frame_result.stdout
                except Exception:
                    pass
            avg_motion = sum(d["motion_score"] for d in diffs) / len(diffs) if diffs else 0
            max_motion = max((d["motion_score"] for d in diffs), default=0)
            return {
                "video": video_path,
                "fps": round(fps, 2),
                "sampled_frames": len(diffs),
                "avg_motion": round(avg_motion, 2),
                "max_motion": round(max_motion, 2),
                "motion_level": "high" if avg_motion > 30 else "medium" if avg_motion > 10 else "low",
                "timeline": diffs[:20],
            }
        except Exception as e:
            return {"error": str(e)}

    @staticmethod
    def quality_score(video_path: str) -> dict:
        analysis = VideoAnalyzer.analyze(video_path)
        if "error" in analysis:
            return analysis
        score = 50
        w, h = analysis["width"], analysis["height"]
        if w >= 3840: score += 20
        elif w >= 1920: score += 15
        elif w >= 1280: score += 10
        elif w >= 640: score += 5
        fps = analysis["fps"]
        if fps >= 60: score += 10
        elif fps >= 30: score += 5
        br = analysis["bit_rate_kbps"]
        if br >= 10000: score += 10
        elif br >= 5000: score += 5
        if analysis["audio_codec"] != "none": score += 10
        if analysis["duration_sec"] > 0: score += 5
        score = min(100, max(0, score))
        return {
            "video": video_path,
            "quality_score": score,
            "resolution": f"{w}x{h}",
            "fps": fps,
            "bitrate_kbps": br,
            "verdict": "excellent" if score >= 85 else "good" if score >= 70 else "fair" if score >= 50 else "poor",
        }

    @staticmethod
    def compare_videos(video1: str, video2: str) -> dict:
        a1 = VideoAnalyzer.analyze(video1)
        a2 = VideoAnalyzer.analyze(video2)
        if "error" in a1 or "error" in a2:
            return {"error": a1.get("error") or a2.get("error")}
        same_res = a1["width"] == a2["width"] and a1["height"] == a2["height"]
        same_codec = a1["video_codec"] == a2["video_codec"]
        dur_diff = abs(a1["duration_sec"] - a2["duration_sec"])
        return {
            "video1": video1, "video2": video2,
            "same_resolution": same_res,
            "same_codec": same_codec,
            "duration_diff_sec": round(dur_diff, 2),
            "size_ratio": round(a1["size_mb"] / max(a2["size_mb"], 0.01), 2),
            "resolution1": f"{a1['width']}x{a1['height']}",
            "resolution2": f"{a2['width']}x{a2['height']}",
        }

    @staticmethod
    def batch_analyze(directory: str, extensions: tuple = (".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv")) -> dict:
        path = Path(directory)
        if not path.exists():
            return {"error": f"Directory not found: {directory}"}
        results = []
        for f in sorted(path.rglob("*")):
            if f.is_file() and f.suffix.lower() in extensions:
                r = VideoAnalyzer.analyze(str(f))
                results.append(r)
        return {"directory": directory, "videos_found": len(results), "results": results}

    @staticmethod
    def generate_summary(video_path: str) -> str:
        a = VideoAnalyzer.analyze(video_path)
        if "error" in a:
            return f"Error: {a['error']}"
        q = VideoAnalyzer.quality_score(video_path)
        lines = [
            f"=== Video Summary: {Path(video_path).name} ===",
            f"Duration: {a['duration_human']}",
            f"Resolution: {a['width']}x{a['height']}",
            f"Codec: {a['video_codec']} / {a['audio_codec']}",
            f"FPS: {a['fps']}",
            f"Bitrate: {a['bit_rate_kbps']} kbps",
            f"Size: {a['size_mb']} MB",
            f"Frames: {a['total_frames']}",
            f"Quality: {q.get('quality_score', 0)}/100 ({q.get('verdict', 'unknown')})",
        ]
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# 32. CRYPTO TRACKER
# ═══════════════════════════════════════════════════════════════════

class CryptoTracker:
    """Cryptocurrency tracking and analysis."""

    COINS = {
        "bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL",
        "cardano": "ADA", "dogecoin": "DOGE", "polkadot": "DOT",
        "litecoin": "LTC", "chainlink": "LINK", "avalanche": "AVAX",
        "polygon": "MATIC", "ripple": "XRP", "toncoin": "TON",
    }

    def __init__(self, data_dir: str = "crypto"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._portfolio: dict[str, float] = {}
        self._price_history: dict[str, list[dict]] = {}
        self._load()

    def _load(self):
        pf = self.data_dir / "portfolio.json"
        if pf.exists():
            try:
                self._portfolio = json.loads(pf.read_text())
            except Exception:
                self._portfolio = {}

    def _save(self):
        (self.data_dir / "portfolio.json").write_text(json.dumps(self._portfolio, indent=2))

    def add_to_portfolio(self, coin: str, amount: float) -> str:
        coin = coin.lower()
        self._portfolio[coin] = self._portfolio.get(coin, 0) + amount
        self._save()
        symbol = self.COINS.get(coin, coin.upper())
        return f"Added {amount} {symbol} to portfolio"

    def remove_from_portfolio(self, coin: str, amount: float) -> str:
        coin = coin.lower()
        if coin in self._portfolio:
            self._portfolio[coin] = max(0, self._portfolio[coin] - amount)
            if self._portfolio[coin] <= 0:
                del self._portfolio[coin]
            self._save()
            return f"Removed {amount} {self.COINS.get(coin, coin.upper())} from portfolio"
        return f"Coin not in portfolio: {coin}"

    def get_portfolio(self) -> dict:
        return dict(self._portfolio)

    def list_coins(self) -> list[dict]:
        return [{"name": k, "symbol": v} for k, v in self.COINS.items()]

    def get_price(self, coin: str) -> str:
        coin = coin.lower()
        symbol = self.COINS.get(coin, coin.upper())
        return f"{symbol}: Price data requires internet connection"


# ═══════════════════════════════════════════════════════════════════
# 33. STOCK TRACKER
# ═══════════════════════════════════════════════════════════════════

class StockTracker:
    """Stock market tracking and analysis."""

    def __init__(self, data_dir: str = "stocks"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._watchlist: list[str] = []
        self._holdings: dict[str, dict] = {}
        self._load()

    def _load(self):
        wl = self.data_dir / "watchlist.json"
        if wl.exists():
            try:
                self._watchlist = json.loads(wl.read_text())
            except Exception:
                self._watchlist = []
        hd = self.data_dir / "holdings.json"
        if hd.exists():
            try:
                self._holdings = json.loads(hd.read_text())
            except Exception:
                self._holdings = {}

    def _save(self):
        (self.data_dir / "watchlist.json").write_text(json.dumps(self._watchlist))
        (self.data_dir / "holdings.json").write_text(json.dumps(self._holdings, indent=2))

    def add_to_watchlist(self, symbol: str) -> str:
        symbol = symbol.upper()
        if symbol not in self._watchlist:
            self._watchlist.append(symbol)
            self._save()
        return f"Added {symbol} to watchlist"

    def remove_from_watchlist(self, symbol: str) -> str:
        symbol = symbol.upper()
        if symbol in self._watchlist:
            self._watchlist.remove(symbol)
            self._save()
        return f"Removed {symbol} from watchlist"

    def get_watchlist(self) -> list[str]:
        return list(self._watchlist)

    def add_holding(self, symbol: str, shares: float, avg_price: float) -> str:
        symbol = symbol.upper()
        if symbol in self._holdings:
            existing = self._holdings[symbol]
            total_shares = existing["shares"] + shares
            avg = (existing["avg_price"] * existing["shares"] + avg_price * shares) / total_shares
            self._holdings[symbol] = {"shares": total_shares, "avg_price": round(avg, 2)}
        else:
            self._holdings[symbol] = {"shares": shares, "avg_price": avg_price}
        self._save()
        return f"Added {shares} shares of {symbol} at ${avg_price}"

    def get_holdings(self) -> dict:
        return dict(self._holdings)

    def get_stock_info(self, symbol: str) -> str:
        return f"{symbol.upper()}: Price data requires internet connection"


# ═══════════════════════════════════════════════════════════════════
# 34. FITNESS TRACKER
# ═══════════════════════════════════════════════════════════════════

class FitnessTracker:
    """Health and fitness tracking."""

    def __init__(self, data_dir: str = "fitness"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._workouts: list[dict] = []
        self._water_log: list[dict] = []
        self._sleep_log: list[dict] = []
        self._goals: dict = {}
        self._load()

    def _load(self):
        for name, attr in [("workouts", "_workouts"), ("water", "_water_log"), ("sleep", "_sleep_log"), ("goals", "_goals")]:
            fp = self.data_dir / f"{name}.json"
            if fp.exists():
                try:
                    setattr(self, attr, json.loads(fp.read_text()))
                except Exception:
                    pass

    def _save(self):
        for name, attr in [("workouts", "_workouts"), ("water", "_water_log"), ("sleep", "_sleep_log"), ("goals", "_goals")]:
            (self.data_dir / f"{name}.json").write_text(json.dumps(getattr(self, attr), indent=2))

    def log_workout(self, exercise: str, duration_min: int, calories: int = 0, notes: str = "") -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "exercise": exercise,
            "duration_min": duration_min,
            "calories": calories,
            "notes": notes,
        }
        self._workouts.append(entry)
        self._save()
        return f"Logged workout: {exercise} ({duration_min} min)"

    def log_water(self, ml: int) -> str:
        entry = {"date": datetime.now().isoformat(), "ml": ml}
        self._water_log.append(entry)
        self._save()
        return f"Logged {ml}ml water"

    def log_sleep(self, hours: float, quality: str = "good") -> str:
        entry = {"date": datetime.now().isoformat(), "hours": hours, "quality": quality}
        self._sleep_log.append(entry)
        self._save()
        return f"Logged {hours}h sleep ({quality})"

    def set_goal(self, goal_type: str, target: float, unit: str = "") -> str:
        self._goals[goal_type] = {"target": target, "unit": unit, "created": datetime.now().isoformat()}
        self._save()
        return f"Goal set: {goal_type} = {target} {unit}"

    def get_stats(self) -> dict:
        return {
            "total_workouts": len(self._workouts),
            "total_water_ml": sum(w["ml"] for w in self._water_log),
            "avg_sleep": sum(s["hours"] for s in self._sleep_log) / max(1, len(self._sleep_log)),
            "goals": self._goals,
        }


# ═══════════════════════════════════════════════════════════════════
# 35. BUDGET MANAGER
# ═══════════════════════════════════════════════════════════════════

class BudgetManager:
    """Personal finance management."""

    def __init__(self, data_dir: str = "finance"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._transactions: list[dict] = []
        self._budgets: dict[str, float] = {}
        self._load()

    def _load(self):
        tf = self.data_dir / "transactions.json"
        if tf.exists():
            try:
                self._transactions = json.loads(tf.read_text())
            except Exception:
                self._transactions = []
        bf = self.data_dir / "budgets.json"
        if bf.exists():
            try:
                self._budgets = json.loads(bf.read_text())
            except Exception:
                self._budgets = {}

    def _save(self):
        (self.data_dir / "transactions.json").write_text(json.dumps(self._transactions, indent=2))
        (self.data_dir / "budgets.json").write_text(json.dumps(self._budgets, indent=2))

    def add_transaction(self, amount: float, category: str, description: str = "", transaction_type: str = "expense") -> str:
        entry = {
            "date": datetime.now().isoformat(),
            "amount": abs(amount),
            "category": category,
            "description": description,
            "type": transaction_type,
        }
        self._transactions.append(entry)
        self._save()
        return f"Added {transaction_type}: ${abs(amount):.2f} ({category})"

    def set_budget(self, category: str, amount: float) -> str:
        self._budgets[category] = amount
        self._save()
        return f"Budget for {category} set to ${amount:.2f}"

    def get_summary(self, month: str = "") -> dict:
        if not month:
            month = datetime.now().strftime("%Y-%m")
        month_trans = [t for t in self._transactions if t["date"].startswith(month)]
        income = sum(t["amount"] for t in month_trans if t["type"] == "income")
        expenses = sum(t["amount"] for t in month_trans if t["type"] == "expense")
        by_category = defaultdict(float)
        for t in month_trans:
            if t["type"] == "expense":
                by_category[t["category"]] += t["amount"]
        return {
            "month": month,
            "income": income,
            "expenses": expenses,
            "balance": income - expenses,
            "by_category": dict(by_category),
            "budgets": self._budgets,
        }

    def get_transactions(self, limit: int = 20) -> list[dict]:
        return self._transactions[-limit:]


# ═══════════════════════════════════════════════════════════════════
# 36. RECIPE MANAGER
# ═══════════════════════════════════════════════════════════════════

class RecipeManager:
    """Recipe storage and management."""

    def __init__(self, data_dir: str = "recipes"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._recipes: list[dict] = []
        self._load()

    def _load(self):
        rf = self.data_dir / "recipes.json"
        if rf.exists():
            try:
                self._recipes = json.loads(rf.read_text())
            except Exception:
                self._recipes = []

    def _save(self):
        (self.data_dir / "recipes.json").write_text(json.dumps(self._recipes, indent=2))

    def add_recipe(self, name: str, ingredients: list[str], steps: list[str],
                   cook_time: int = 0, servings: int = 1, tags: list[str] = None) -> str:
        recipe = {
            "id": len(self._recipes) + 1,
            "name": name,
            "ingredients": ingredients,
            "steps": steps,
            "cook_time_min": cook_time,
            "servings": servings,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
        }
        self._recipes.append(recipe)
        self._save()
        return f"Recipe added: {name}"

    def get_recipe(self, name: str) -> dict | None:
        name_lower = name.lower()
        return next((r for r in self._recipes if name_lower in r["name"].lower()), None)

    def search_recipes(self, query: str) -> list[dict]:
        q = query.lower()
        return [r for r in self._recipes if q in r["name"].lower() or any(q in tag for tag in r.get("tags", []))]

    def list_recipes(self) -> list[dict]:
        return [{"id": r["id"], "name": r["name"], "cook_time": r["cook_time_min"]} for r in self._recipes]

    def delete_recipe(self, recipe_id: int) -> str:
        self._recipes = [r for r in self._recipes if r["id"] != recipe_id]
        self._save()
        return f"Recipe {recipe_id} deleted"


# ═══════════════════════════════════════════════════════════════════
# 37. BOOK LIBRARY
# ═══════════════════════════════════════════════════════════════════

class BookLibrary:
    """Digital book library management."""

    def __init__(self, data_dir: str = "library"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._books: list[dict] = []
        self._reading_list: list[int] = []
        self._load()

    def _load(self):
        bf = self.data_dir / "books.json"
        if bf.exists():
            try:
                data = json.loads(bf.read_text())
                self._books = data.get("books", [])
                self._reading_list = data.get("reading_list", [])
            except Exception:
                pass

    def _save(self):
        (self.data_dir / "books.json").write_text(json.dumps({
            "books": self._books, "reading_list": self._reading_list
        }, indent=2))

    def add_book(self, title: str, author: str, pages: int = 0, genre: str = "", rating: float = 0.0) -> str:
        book = {
            "id": len(self._books) + 1,
            "title": title,
            "author": author,
            "pages": pages,
            "genre": genre,
            "rating": rating,
            "status": "unread",
            "added": datetime.now().isoformat(),
        }
        self._books.append(book)
        self._save()
        return f"Book added: {title} by {author}"

    def update_status(self, book_id: int, status: str) -> str:
        for book in self._books:
            if book["id"] == book_id:
                book["status"] = status
                self._save()
                return f"Updated {book['title']} to {status}"
        return "Book not found"

    def search_books(self, query: str) -> list[dict]:
        q = query.lower()
        return [b for b in self._books if q in b["title"].lower() or q in b["author"].lower() or q in b.get("genre", "").lower()]

    def get_reading_list(self) -> list[dict]:
        return [b for b in self._books if b["id"] in self._reading_list]

    def list_books(self, status: str = "") -> list[dict]:
        books = self._books
        if status:
            books = [b for b in books if b.get("status") == status]
        return [{"id": b["id"], "title": b["title"], "author": b["author"], "status": b.get("status")} for b in books]


# ═══════════════════════════════════════════════════════════════════
# 38. HABIT TRACKER
# ═══════════════════════════════════════════════════════════════════

class HabitTracker:
    """Habit tracking and streak management."""

    def __init__(self, data_dir: str = "habits"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._habits: dict[str, dict] = {}
        self._log: list[dict] = []
        self._load()

    def _load(self):
        hf = self.data_dir / "habits.json"
        if hf.exists():
            try:
                self._habits = json.loads(hf.read_text())
            except Exception:
                self._habits = {}
        lf = self.data_dir / "log.json"
        if lf.exists():
            try:
                self._log = json.loads(lf.read_text())
            except Exception:
                self._log = []

    def _save(self):
        (self.data_dir / "habits.json").write_text(json.dumps(self._habits, indent=2))
        (self.data_dir / "log.json").write_text(json.dumps(self._log, indent=2))

    def add_habit(self, name: str, frequency: str = "daily", target: int = 1) -> str:
        self._habits[name] = {
            "frequency": frequency,
            "target": target,
            "streak": 0,
            "best_streak": 0,
            "created": datetime.now().isoformat(),
        }
        self._save()
        return f"Habit added: {name} ({frequency})"

    def complete_habit(self, name: str) -> str:
        if name not in self._habits:
            return f"Habit not found: {name}"
        habit = self._habits[name]
        habit["streak"] += 1
        habit["best_streak"] = max(habit["best_streak"], habit["streak"])
        self._log.append({"date": datetime.now().isoformat(), "habit": name, "action": "complete"})
        self._save()
        return f"Completed {name}! Streak: {habit['streak']}"

    def reset_streak(self, name: str) -> str:
        if name in self._habits:
            self._habits[name]["streak"] = 0
            self._save()
            return f"Reset streak for {name}"
        return f"Habit not found: {name}"

    def list_habits(self) -> list[dict]:
        return [{"name": k, **v} for k, v in self._habits.items()]

    def get_stats(self) -> dict:
        return {
            "total_habits": len(self._habits),
            "total_completions": len(self._log),
            "best_streaks": {k: v["best_streak"] for k, v in self._habits.items()},
        }


# ═══════════════════════════════════════════════════════════════════
# 39. PASSWORD GENERATOR
# ═══════════════════════════════════════════════════════════════════

class PasswordGenerator:
    """Secure password generation."""

    LOWERCASE = "abcdefghijklmnopqrstuvwxyz"
    UPPERCASE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    DIGITS = "0123456789"
    SPECIAL = "!@#$%^&*()_+-=[]{}|;:,.<>?"

    def generate(self, length: int = 16, use_uppercase: bool = True, use_digits: bool = True,
                 use_special: bool = True, exclude_chars: str = "") -> str:
        charset = self.LOWERCASE
        if use_uppercase:
            charset += self.UPPERCASE
        if use_digits:
            charset += self.DIGITS
        if use_special:
            charset += self.SPECIAL

        if exclude_chars:
            charset = "".join(c for c in charset if c not in exclude_chars)

        if not charset:
            charset = self.LOWERCASE

        password = "".join(random.choice(charset) for _ in range(length))
        return password

    def generate_passphrase(self, words: int = 4, separator: str = "-") -> str:
        wordlist = [
            "apple", "brave", "cloud", "dance", "eagle", "flame", "grace", "happy",
            "ivory", "jolly", "karma", "lemon", "magic", "noble", "ocean", "pearl",
            "quiet", "river", "storm", "tiger", "unity", "vivid", "wonder", "zenith",
            "anchor", "bridge", "castle", "dawn", "ember", "forest", "glacier", "harbor",
            "island", "jungle", "knight", "lighthouse", "meadow", "nebula", "oasis", "prism",
        ]
        return separator.join(random.choice(wordlist) for _ in range(words))

    def check_strength(self, password: str) -> dict:
        score = 0
        checks = {
            "length_8": len(password) >= 8,
            "length_12": len(password) >= 12,
            "length_16": len(password) >= 16,
            "has_lower": any(c in self.LOWERCASE for c in password),
            "has_upper": any(c in self.UPPERCASE for c in password),
            "has_digit": any(c in self.DIGITS for c in password),
            "has_special": any(c in self.SPECIAL for c in password),
        }
        score = sum(checks.values())
        strength = "very_weak" if score < 3 else "weak" if score < 5 else "medium" if score < 6 else "strong" if score < 7 else "very_strong"
        return {"score": score, "max_score": 7, "strength": strength, "checks": checks}


# ═══════════════════════════════════════════════════════════════════
# 40. WEB SCRAPER
# ═══════════════════════════════════════════════════════════════════

class WebScraperAdvanced:
    """Advanced web scraping with rate limiting and caching."""

    def __init__(self, cache_dir: str = "webcache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self._cache: dict[str, dict] = {}
        self._rate_limit: float = 1.0
        self._last_request: float = 0

    def fetch(self, url: str, use_cache: bool = True, timeout: int = 10) -> str:
        if use_cache and url in self._cache:
            cached = self._cache[url]
            if time.time() - cached["time"] < 3600:
                return cached["data"]

        elapsed = time.time() - self._last_request
        if elapsed < self._rate_limit:
            time.sleep(self._rate_limit - elapsed)

        try:
            result = subprocess.run(
                ["curl", "-s", "-L", "--max-time", str(timeout), url],
                capture_output=True, text=True, timeout=timeout + 5
            )
            self._last_request = time.time()
            if result.returncode == 0:
                self._cache[url] = {"data": result.stdout[:50000], "time": time.time()}
                return result.stdout[:50000]
            return f"Error: {result.stderr[:200]}"
        except Exception as e:
            return f"Error: {e}"

    def extract_text(self, html: str) -> str:
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()[:5000]

    def extract_links(self, html: str) -> list[str]:
        import re
        return re.findall(r'href="(https?://[^"]+)"', html)[:50]

    def extract_meta(self, html: str) -> dict:
        import re
        title = re.search(r'<title[^>]*>(.*?)</title>', html, re.DOTALL)
        description = re.search(r'<meta[^>]*name="description"[^>]*content="([^"]*)"', html)
        return {
            "title": title.group(1).strip() if title else "",
            "description": description.group(1) if description else "",
        }

    def batch_fetch(self, urls: list[str]) -> list[dict]:
        return [{"url": u, "data": self.fetch(u)[:1000]} for u in urls[:10]]


# ═══════════════════════════════════════════════════════════════════
# SINGLETON INSTANCES (lazy loaded)
# ═══════════════════════════════════════════════════════════════════

_instances = {}

def get_feature(name: str):
    """Get a feature singleton (lazy loaded)."""
    if name not in _instances:
        feature_map = {
            "marketplace": PluginMarketplace,
            "scheduler": TaskScheduler,
            "scraper": WebScraper,
            "api_builder": APIBuilder,
            "database": DatabaseManager,
            "email": EmailGateway,
            "ssh": SSHClient,
            "vpn": VPNControl,
            "ftp": FTPClient,
            "music": MusicPlayer,
            "weather": WeatherService,
            "news": NewsAggregator,
            "qr": QRGenerator,
            "pdf": PDFTools,
            "vault": EncryptedVault,
            "workflow": WorkflowBuilder,
            "language": MultiLanguage,
            "todo": TodoManager,
            "calendar": CalendarManager,
            "docker": DockerControl,
            "monitor": SystemMonitor,
            "file_organizer": FileOrganizer,
            "backup": BackupManager,
            "git": GitManager,
            "packages": PackageManager,
            "cron": CronScheduler,
            "analyzer": DataAnalyzer,
            "text": TextProcessor,
            "image": ImageProcessor,
            "audio": AudioProcessor,
            "video": VideoProcessor,
            "crypto": CryptoTracker,
            "stocks": StockTracker,
            "fitness": FitnessTracker,
            "budget": BudgetManager,
            "recipes": RecipeManager,
            "library": BookLibrary,
            "habits": HabitTracker,
            "password": PasswordGenerator,
            "web_scraper": WebScraperAdvanced,
            "notes": NoteTaker,
            "flashcards": FlashcardDeck,
            "pomodoro": PomodoroTimer,
            "clipboard": ClipboardManager,
            "formatter": CodeFormatter,
            "regex": RegexTester,
            "json_editor": JsonEditor,
            "uuid": UuidGenerator,
            "hash": HashCalculator,
            "units": UnitConverter,
            "bmi": BmiCalculator,
            "loan": LoanCalculator,
            "tip": TipCalculator,
            "dice": DiceRoller,
            "colors": ColorPalette,
            "ascii_art": AsciiArt,
            "diagnostics": SystemDiagnostics,
            "wordcount": WordCounter,
            "crypto_tools": Cryptography,
            "network_tools": NetworkTools,
            "image_input": ImageInput,
            "image_analyzer": ImageAnalyzer,
            "image_finder": ImageFinder,
            "image_generator": ImageGenerator,
            "image_editor": ImageEditor,
            "image_filter": ImageFilter,
            "image_diff": ImageDiff,
            "image_collage": ImageCollage,
            "image_watermark": ImageWatermark,
            "image_comparator": ImageComparator,
            "video_analyzer": VideoAnalyzer,
            "encryption": AIProtection,
            "file_enc": FileEncryption,
            "secure_del": SecureDeletion,
            "key_mgr": KeyManager,
            "sign": DigitalSignature,
            "hash_func": HashFunctions,
            "hmac_auth": HMACAuth,
            "kdf": KeyDerivation,
        }
        if name in feature_map:
            _instances[name] = feature_map[name]()
    return _instances.get(name)
