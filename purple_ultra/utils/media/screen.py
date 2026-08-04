"""Screen awareness module - monitors screen content and provides proactive suggestions."""

from __future__ import annotations

import json
import time
import subprocess
import platform
from pathlib import Path
from typing import Callable


class ScreenAwareness:
    def __init__(self, memory_dir: str = "memory"):
        self._context_file = Path(memory_dir) / "screen_context.json"
        self._context: dict = {}
        self._last_suggestion_time: float = 0
        self._suggestion_cooldown: float = 300
        self._load()

    def _load(self):
        if self._context_file.exists():
            try:
                self._context = json.loads(self._context_file.read_text())
            except Exception:
                pass

    def _save(self):
        try:
            self._context_file.parent.mkdir(parents=True, exist_ok=True)
            self._context_file.write_text(json.dumps(self._context, indent=2))
        except Exception:
            pass

    def take_screenshot(self) -> str:
        try:
            screenshot_dir = Path("data/screenshots")
            screenshot_dir.mkdir(parents=True, exist_ok=True)
            filename = screenshot_dir / f"screen_{int(time.time())}.png"
            if platform.system() == "Darwin":
                subprocess.run(["screencapture", str(filename)], check=True, capture_output=True)
                return str(filename)
        except Exception:
            pass
        return ""

    def get_screen_text(self) -> str:
        screenshot = self.take_screenshot()
        if not screenshot:
            return ""
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(screenshot)
            text = pytesseract.image_to_string(img)
            return text[:5000]
        except ImportError:
            return ""
        except Exception:
            return ""

    def analyze_activity(self) -> dict:
        text = self.get_screen_text()
        activity = {
            "text_preview": text[:500],
            "timestamp": time.time(),
            "type": self._classify_activity(text),
        }
        self._context = activity
        self._save()
        return activity

    def _classify_activity(self, text: str) -> str:
        text_lower = text.lower()
        if any(w in text_lower for w in ("code", "function", "class", "import", "def ", "return")):
            return "coding"
        if any(w in text_lower for w in ("email", "inbox", "message", "chat")):
            return "communication"
        if any(w in text_lower for w in ("search", "google", "browse", "http")):
            return "browsing"
        if any(w in text_lower for w in ("document", "paper", "article", "read")):
            return "reading"
        return "unknown"

    def get_suggestion(self, activity: dict = None) -> str:
        if time.time() - self._last_suggestion_time < self._suggestion_cooldown:
            return ""
        activity = activity or self._context
        activity_type = activity.get("type", "unknown")
        suggestions = {
            "coding": "I see you're coding. Want me to analyze your code or help with debugging?",
            "communication": "You seem to be in a conversation. Want me to draft a reply?",
            "browsing": "You're browsing. Want me to search for something or save this page?",
            "reading": "Reading something interesting? Want me to summarize it?",
        }
        suggestion = suggestions.get(activity_type, "")
        if suggestion:
            self._last_suggestion_time = time.time()
        return suggestion

    def get_context_summary(self) -> str:
        if not self._context:
            return "No screen context available"
        return f"Activity: {self._context.get('type', 'unknown')}\nPreview: {self._context.get('text_preview', '')[:200]}"
