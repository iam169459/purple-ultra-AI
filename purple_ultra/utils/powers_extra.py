"""Additional Feature Modules 41-60 for Purple Ultra AI."""

import json
import math
import os
import random
import time
import hashlib
import uuid
import re
import base64
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════════
# 41. NOTE TAKER
# ═══════════════════════════════════════════════════════════════════

class NoteTaker:
    def __init__(self, data_dir: str = "notes"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._notes: list[dict] = []
        self._load()

    def _load(self):
        nf = self.data_dir / "notes.json"
        if nf.exists():
            try: self._notes = json.loads(nf.read_text())
            except: self._notes = []

    def _save(self):
        (self.data_dir / "notes.json").write_text(json.dumps(self._notes, indent=2))

    def add_note(self, title: str, content: str, tags: list[str] = None, category: str = "general") -> str:
        note = {"id": len(self._notes) + 1, "title": title, "content": content, "tags": tags or [],
                "category": category, "created": datetime.now().isoformat(), "modified": datetime.now().isoformat(), "pinned": False}
        self._notes.append(note)
        self._save()
        return f"Note added: {title}"

    def update_note(self, note_id: int, title: str = "", content: str = "", tags: list[str] = None) -> str:
        for note in self._notes:
            if note["id"] == note_id:
                if title: note["title"] = title
                if content: note["content"] = content
                if tags is not None: note["tags"] = tags
                note["modified"] = datetime.now().isoformat()
                self._save()
                return f"Note updated: {note['title']}"
        return "Note not found"

    def delete_note(self, note_id: int) -> str:
        self._notes = [n for n in self._notes if n["id"] != note_id]
        self._save()
        return f"Note {note_id} deleted"

    def pin_note(self, note_id: int) -> str:
        for note in self._notes:
            if note["id"] == note_id:
                note["pinned"] = not note.get("pinned", False)
                self._save()
                return f"Note {'pinned' if note['pinned'] else 'unpinned'}"
        return "Note not found"

    def search_notes(self, query: str) -> list[dict]:
        q = query.lower()
        return [n for n in self._notes if q in n["title"].lower() or q in n["content"].lower() or q in " ".join(n.get("tags", []))]

    def get_by_tag(self, tag: str) -> list[dict]:
        return [n for n in self._notes if tag in n.get("tags", [])]

    def get_by_category(self, category: str) -> list[dict]:
        return [n for n in self._notes if n.get("category") == category]

    def list_notes(self, pinned_only: bool = False) -> list[dict]:
        notes = [n for n in self._notes if n.get("pinned")] if pinned_only else self._notes
        return [{"id": n["id"], "title": n["title"], "tags": n.get("tags", []), "pinned": n.get("pinned", False)} for n in notes]

    def get_all_tags(self) -> list[str]:
        tags = set()
        for n in self._notes: tags.update(n.get("tags", []))
        return sorted(tags)


# ═══════════════════════════════════════════════════════════════════
# 42. FLASHCARD DECK
# ═══════════════════════════════════════════════════════════════════

class FlashcardDeck:
    def __init__(self, data_dir: str = "flashcards"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._decks: dict[str, dict] = {}
        self._load()

    def _load(self):
        df = self.data_dir / "decks.json"
        if df.exists():
            try: self._decks = json.loads(df.read_text())
            except: self._decks = {}

    def _save(self):
        (self.data_dir / "decks.json").write_text(json.dumps(self._decks, indent=2))

    def create_deck(self, name: str, description: str = "") -> str:
        if name not in self._decks:
            self._decks[name] = {"description": description, "cards": [], "created": datetime.now().isoformat()}
            self._save()
        return f"Deck created: {name}"

    def add_card(self, deck: str, front: str, back: str, tags: list[str] = None) -> str:
        if deck not in self._decks: return f"Deck not found: {deck}"
        card = {"id": len(self._decks[deck]["cards"]) + 1, "front": front, "back": back, "tags": tags or [],
                "ease_factor": 2.5, "interval": 0, "repetitions": 0, "next_review": datetime.now().isoformat()}
        self._decks[deck]["cards"].append(card)
        self._save()
        return f"Card added to {deck}"

    def review_card(self, deck: str, card_id: int, quality: int) -> str:
        if deck not in self._decks: return f"Deck not found: {deck}"
        for card in self._decks[deck]["cards"]:
            if card["id"] == card_id:
                if quality >= 3:
                    if card["repetitions"] == 0: card["interval"] = 1
                    elif card["repetitions"] == 1: card["interval"] = 6
                    else: card["interval"] = int(card["interval"] * card["ease_factor"])
                    card["repetitions"] += 1
                else:
                    card["repetitions"] = 0
                    card["interval"] = 0
                card["ease_factor"] = max(1.3, card["ease_factor"] + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
                card["next_review"] = (datetime.now() + timedelta(days=card["interval"])).isoformat()
                self._save()
                return f"Card reviewed. Next review in {card['interval']} days"
        return "Card not found"

    def get_due_cards(self, deck: str) -> list[dict]:
        if deck not in self._decks: return []
        now = datetime.now().isoformat()
        return [c for c in self._decks[deck]["cards"] if c.get("next_review", "") <= now]

    def list_decks(self) -> list[dict]:
        return [{"name": k, "cards": len(v["cards"]), "description": v.get("description", "")} for k, v in self._decks.items()]

    def get_deck_stats(self, deck: str) -> dict:
        if deck not in self._decks: return {}
        cards = self._decks[deck]["cards"]
        return {"total": len(cards), "due": len(self.get_due_cards(deck)), "mastered": sum(1 for c in cards if c.get("repetitions", 0) >= 3)}


# ═══════════════════════════════════════════════════════════════════
# 43. POMODORO TIMER
# ═══════════════════════════════════════════════════════════════════

class PomodoroTimer:
    def __init__(self):
        self.work_duration = 25 * 60
        self.short_break = 5 * 60
        self.long_break = 15 * 60
        self._sessions: list[dict] = []
        self._current_session: dict | None = None

    def start_work(self, task: str = "focus") -> str:
        self._current_session = {"task": task, "type": "work", "start": time.time(), "duration": self.work_duration}
        return f"Pomodoro started: {task} ({self.work_duration // 60} min)"

    def start_break(self, long: bool = False) -> str:
        duration = self.long_break if long else self.short_break
        self._current_session = {"task": "break", "type": "break", "start": time.time(), "duration": duration}
        return f"Break started ({duration // 60} min)"

    def stop(self) -> str:
        if not self._current_session: return "No active session"
        elapsed = time.time() - self._current_session["start"]
        self._current_session["elapsed"] = int(elapsed)
        self._sessions.append(self._current_session)
        self._current_session = None
        return f"Session stopped. Elapsed: {int(elapsed)}s"

    def get_status(self) -> dict:
        if not self._current_session: return {"status": "idle", "sessions": len(self._sessions)}
        elapsed = time.time() - self._current_session["start"]
        remaining = max(0, self._current_session["duration"] - elapsed)
        return {"status": "active", "task": self._current_session["task"], "type": self._current_session["type"],
                "elapsed_min": int(elapsed / 60), "remaining_min": int(remaining / 60), "sessions": len(self._sessions)}

    def get_stats(self) -> dict:
        total_work = sum(s.get("elapsed", 0) for s in self._sessions if s.get("type") == "work")
        return {"total_sessions": len(self._sessions), "total_work_min": total_work // 60}


# ═══════════════════════════════════════════════════════════════════
# 44. CLIPBOARD MANAGER
# ═══════════════════════════════════════════════════════════════════

class ClipboardManager:
    def __init__(self, max_history: int = 50):
        self._history: list[dict] = []
        self._max = max_history
        self._last_clipboard = ""

    def copy(self, text: str, label: str = "") -> str:
        if text == self._last_clipboard: return "Already in clipboard"
        entry = {"text": text[:5000], "label": label, "timestamp": datetime.now().isoformat(), "char_count": len(text)}
        self._history.insert(0, entry)
        if len(self._history) > self._max: self._history.pop()
        self._last_clipboard = text
        return f"Copied {len(text)} chars"

    def paste(self) -> str:
        return self._last_clipboard if self._last_clipboard else "Clipboard empty"

    def get_history(self, limit: int = 10) -> list[dict]:
        return [{"preview": h["text"][:50], "label": h["label"], "chars": h["char_count"], "time": h["timestamp"]} for h in self._history[:limit]]

    def search(self, query: str) -> list[dict]:
        q = query.lower()
        return [{"preview": h["text"][:50], "chars": h["char_count"]} for h in self._history if q in h["text"].lower()]

    def clear(self) -> str:
        count = len(self._history)
        self._history.clear()
        return f"Cleared {count} items"


# ═══════════════════════════════════════════════════════════════════
# 45. CODE FORMATTER
# ═══════════════════════════════════════════════════════════════════

class CodeFormatter:
    @staticmethod
    def indent(code: str, spaces: int = 4) -> str:
        lines = code.split("\n")
        result = []
        indent_level = 0
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("}", "]", ")", "except", "finally", "else:", "elif")):
                indent_level = max(0, indent_level - 1)
            result.append(" " * (indent_level * spaces) + stripped)
            if stripped.endswith(("{", "[", "(")) or stripped.endswith((":")):
                if not stripped.endswith(("}", "]", ")")):
                    indent_level += 1
        return "\n".join(result)

    @staticmethod
    def minify(code: str) -> str:
        return " ".join(code.split())

    @staticmethod
    def line_count(code: str) -> dict:
        lines = code.split("\n")
        blank = sum(1 for l in lines if not l.strip())
        comment = sum(1 for l in lines if l.strip().startswith(("#", "//", "/*", "*")))
        code_lines = len(lines) - blank - comment
        return {"total": len(lines), "code": code_lines, "blank": blank, "comment": comment}

    @staticmethod
    def detect_language(code: str) -> str:
        if "def " in code and "import " in code: return "python"
        if "function " in code and ("const " in code or "let " in code): return "javascript"
        if "fn " in code and "let " in code: return "rust"
        if "func " in code and "package " in code: return "go"
        if "class " in code and ("public " in code or "private " in code): return "java"
        if "#include" in code: return "c/c++"
        return "unknown"

    @staticmethod
    def format_json(text: str, indent: int = 2) -> str:
        try:
            obj = json.loads(text)
            return json.dumps(obj, indent=indent)
        except:
            return text


# ═══════════════════════════════════════════════════════════════════
# 46. REGEX TESTER
# ═══════════════════════════════════════════════════════════════════

class RegexTester:
    @staticmethod
    def test(pattern: str, text: str) -> dict:
        try:
            matches = re.findall(pattern, text)
            return {"valid": True, "matches": matches, "count": len(matches)}
        except re.error as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def match(pattern: str, text: str) -> dict:
        try:
            m = re.search(pattern, text)
            if m:
                return {"found": True, "match": m.group(), "start": m.start(), "end": m.end(), "groups": m.groups()}
            return {"found": False}
        except re.error as e:
            return {"found": False, "error": str(e)}

    @staticmethod
    def replace(pattern: str, replacement: str, text: str) -> str:
        try:
            return re.sub(pattern, replacement, text)
        except:
            return text

    @staticmethod
    def split(pattern: str, text: str) -> list[str]:
        try:
            return re.split(pattern, text)
        except:
            return [text]

    @staticmethod
    def common_patterns() -> dict:
        return {"email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                "url": r'https?://[^\s<>"]+', "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
                "ip": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', "date": r'\d{4}-\d{2}-\d{2}',
                "hex_color": r'#[0-9a-fA-F]{6}', "html_tag": r'<[^>]+>'}


# ═══════════════════════════════════════════════════════════════════
# 47. JSON EDITOR
# ═══════════════════════════════════════════════════════════════════

class JsonEditor:
    @staticmethod
    def parse(text: str) -> dict:
        try:
            return {"valid": True, "data": json.loads(text)}
        except json.JSONDecodeError as e:
            return {"valid": False, "error": str(e)}

    @staticmethod
    def format_json(text: str, indent: int = 2) -> str:
        try:
            return json.dumps(json.loads(text), indent=indent)
        except:
            return text

    @staticmethod
    def minify(text: str) -> str:
        try:
            return json.dumps(json.loads(text), separators=(",", ":"))
        except:
            return text

    @staticmethod
    def get_value(text: str, path: str) -> dict:
        try:
            data = json.loads(text)
            keys = path.split(".")
            current = data
            for key in keys:
                if isinstance(current, dict) and key in current:
                    current = current[key]
                else:
                    return {"found": False}
            return {"found": True, "value": current}
        except:
            return {"found": False}

    @staticmethod
    def set_value(text: str, path: str, value) -> str:
        try:
            data = json.loads(text)
            keys = path.split(".")
            current = data
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            try:
                current[keys[-1]] = json.loads(value)
            except:
                current[keys[-1]] = value
            return json.dumps(data, indent=2)
        except:
            return text

    @staticmethod
    def pretty_print(text: str) -> str:
        try:
            return json.dumps(json.loads(text), indent=2, sort_keys=True)
        except:
            return text


# ═══════════════════════════════════════════════════════════════════
# 48. UUID GENERATOR
# ═══════════════════════════════════════════════════════════════════

class UuidGenerator:
    @staticmethod
    def v4() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def batch(count: int = 5) -> list[str]:
        return [str(uuid.uuid4()) for _ in range(count)]

    @staticmethod
    def short(length: int = 8) -> str:
        return uuid.uuid4().hex[:length]

    @staticmethod
    def from_name(name: str, namespace: str = "6ba7b810-9dad-11d1-80b4-00c04fd430c8") -> str:
        return str(uuid.uuid5(uuid.UUID(namespace), name))

    @staticmethod
    def validate(uuid_str: str) -> bool:
        try:
            uuid.UUID(uuid_str)
            return True
        except:
            return False


# ═══════════════════════════════════════════════════════════════════
# 49. HASH CALCULATOR
# ═══════════════════════════════════════════════════════════════════

class HashCalculator:
    @staticmethod
    def md5(text: str) -> str:
        return hashlib.md5(text.encode()).hexdigest()

    @staticmethod
    def sha1(text: str) -> str:
        return hashlib.sha1(text.encode()).hexdigest()

    @staticmethod
    def sha256(text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def sha512(text: str) -> str:
        return hashlib.sha512(text.encode()).hexdigest()

    @staticmethod
    def file_hash(filepath: str, algorithm: str = "md5") -> str:
        h = hashlib.new(algorithm)
        with open(filepath, "rb") as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()

    @staticmethod
    def compare(text: str, expected: str, algorithm: str = "md5") -> dict:
        h = hashlib.new(algorithm)
        h.update(text.encode())
        computed = h.hexdigest()
        return {"match": computed == expected, "computed": computed, "expected": expected}


# ═══════════════════════════════════════════════════════════════════
# 50. UNIT CONVERTER
# ═══════════════════════════════════════════════════════════════════

class UnitConverter:
    UNITS = {
        "length": {"m": 1, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.344, "yd": 0.9144, "ft": 0.3048, "in": 0.0254},
        "mass": {"kg": 1, "g": 0.001, "mg": 0.000001, "lb": 0.453592, "oz": 0.0283495, "ton": 1000},
        "temperature": {"c": "celsius", "f": "fahrenheit", "k": "kelvin"},
        "time": {"s": 1, "min": 60, "h": 3600, "day": 86400, "week": 604800, "month": 2592000, "year": 31536000},
        "data": {"b": 1, "kb": 1024, "mb": 1048576, "gb": 1073741824, "tb": 1099511627776},
    }

    def convert(self, value: float, from_unit: str, to_unit: str, category: str = "length") -> dict:
        if category == "temperature":
            return self._convert_temperature(value, from_unit.lower(), to_unit.lower())
        units = self.UNITS.get(category, {})
        from_u = from_unit.lower()
        to_u = to_unit.lower()
        if from_u not in units or to_u not in units:
            return {"error": f"Unknown unit: {from_u} or {to_u}"}
        base_value = value * units[from_u]
        result = base_value / units[to_u]
        return {"value": round(result, 6), "from": f"{value} {from_u}", "to": f"{result:.6f} {to_u}"}

    def _convert_temperature(self, value: float, from_u: str, to_u: str) -> dict:
        celsius = value if from_u == "c" else (value - 32) * 5/9 if from_u == "f" else value - 273.15
        result = celsius if to_u == "c" else celsius * 9/5 + 32 if to_u == "f" else celsius + 273.15
        return {"value": round(result, 2), "from": f"{value} {from_u}", "to": f"{result:.2f} {to_u}"}


# ═══════════════════════════════════════════════════════════════════
# 51. BMI CALCULATOR
# ═══════════════════════════════════════════════════════════════════

class BmiCalculator:
    @staticmethod
    def calculate(weight_kg: float, height_m: float) -> dict:
        bmi = weight_kg / (height_m ** 2) if height_m > 0 else 0
        if bmi < 18.5: category = "underweight"
        elif bmi < 25: category = "normal"
        elif bmi < 30: category = "overweight"
        else: category = "obese"
        return {"bmi": round(bmi, 1), "category": category, "weight": weight_kg, "height": height_m}

    @staticmethod
    def ideal_weight_range(height_m: float) -> dict:
        return {"min_kg": round(18.5 * height_m ** 2, 1), "max_kg": round(24.9 * height_m ** 2, 1), "height": height_m}


# ═══════════════════════════════════════════════════════════════════
# 52. LOAN CALCULATOR
# ═══════════════════════════════════════════════════════════════════

class LoanCalculator:
    @staticmethod
    def monthly_payment(principal: float, annual_rate: float, years: int) -> dict:
        r = annual_rate / 100 / 12
        n = years * 12
        if r == 0:
            payment = principal / n
        else:
            payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        total = payment * n
        interest = total - principal
        return {"monthly_payment": round(payment, 2), "total_payment": round(total, 2), "total_interest": round(interest, 2)}

    @staticmethod
    def amortization_schedule(principal: float, annual_rate: float, years: int) -> list[dict]:
        r = annual_rate / 100 / 12
        n = years * 12
        if r == 0: payment = principal / n
        else: payment = principal * (r * (1 + r) ** n) / ((1 + r) ** n - 1)
        balance = principal
        schedule = []
        for month in range(1, n + 1):
            interest = balance * r
            principal_paid = payment - interest
            balance -= principal_paid
            schedule.append({"month": month, "payment": round(payment, 2), "principal": round(principal_paid, 2),
                           "interest": round(interest, 2), "balance": round(max(0, balance), 2)})
        return schedule


# ═══════════════════════════════════════════════════════════════════
# 53. TIP CALCULATOR
# ═══════════════════════════════════════════════════════════════════

class TipCalculator:
    @staticmethod
    def calculate(bill: float, tip_percent: float, split: int = 1) -> dict:
        tip = bill * tip_percent / 100
        total = bill + tip
        per_person = total / split if split > 0 else total
        return {"bill": bill, "tip_percent": tip_percent, "tip_amount": round(tip, 2),
                "total": round(total, 2), "split": split, "per_person": round(per_person, 2)}

    @staticmethod
    def quick_tips(bill: float) -> dict:
        return {f"{p}%": round(bill * p / 100, 2) for p in [10, 15, 18, 20, 25]}


# ═══════════════════════════════════════════════════════════════════
# 54. DICE ROLLER
# ═══════════════════════════════════════════════════════════════════

class DiceRoller:
    @staticmethod
    def roll(sides: int = 6) -> int:
        return random.randint(1, sides)

    @staticmethod
    def roll_multiple(count: int = 1, sides: int = 6) -> list[int]:
        return [random.randint(1, sides) for _ in range(count)]

    @staticmethod
    def roll_notation(notation: str) -> dict:
        m = re.match(r'(\d+)d(\d+)(?:([+-])(\d+))?', notation.lower())
        if not m: return {"error": f"Invalid notation: {notation}"}
        count, sides = int(m.group(1)), int(m.group(2))
        modifier = int(m.group(4)) if m.group(4) else 0
        if m.group(3) == "-": modifier = -modifier
        rolls = [random.randint(1, sides) for _ in range(count)]
        total = sum(rolls) + modifier
        return {"notation": notation, "rolls": rolls, "modifier": modifier, "total": total}

    @staticmethod
    def statistics(sides: int = 6, rolls: int = 1000) -> dict:
        results = [random.randint(1, sides) for _ in range(rolls)]
        freq = {i: results.count(i) for i in range(1, sides + 1)}
        return {"rolls": rolls, "sides": sides, "mean": sum(results) / len(results), "frequency": freq}


# ═══════════════════════════════════════════════════════════════════
# 55. COLOR PALETTE
# ═══════════════════════════════════════════════════════════════════

class ColorPalette:
    @staticmethod
    def generate(base_color: str = None) -> list[dict]:
        if base_color:
            base = int(base_color.lstrip("#"), 16)
            r, g, b = (base >> 16) & 255, (base >> 8) & 255, base & 255
            h, s, v = ColorPalette._rgb_to_hsv(r, g, b)
            colors = []
            for i in range(5):
                new_h = (h + i * 30) % 360
                r2, g2, b2 = ColorPalette._hsv_to_rgb(new_h, s, v)
                colors.append({"hex": f"#{r2:02x}{g2:02x}{b2:02x}", "rgb": (r2, g2, b2)})
            return colors
        return [{"hex": f"#{random.randint(0, 0xFFFFFF):06x}"} for _ in range(5)]

    @staticmethod
    def complementary(hex_color: str) -> dict:
        c = int(hex_color.lstrip("#"), 16)
        r, g, b = (c >> 16) & 255, (c >> 8) & 255, c & 255
        comp = ((255 - r) << 16) | ((255 - g) << 8) | (255 - b)
        return {"original": hex_color, "complementary": f"#{comp:06x}"}

    @staticmethod
    def contrast_ratio(hex1: str, hex2: str) -> float:
        def luminance(hex_c):
            c = int(hex_c.lstrip("#"), 16)
            r, g, b = [(c >> i) & 255 for i in (16, 8, 0)]
            rgb = [x / 255.0 for x in (r, g, b)]
            rgb = [x / 12.92 if x <= 0.03928 else ((x + 0.055) / 1.055) ** 2.4 for x in rgb]
            return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]
        l1, l2 = luminance(hex1), luminance(hex2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return round((lighter + 0.05) / (darker + 0.05), 2)

    @staticmethod
    def _rgb_to_hsv(r, g, b):
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx, mn = max(r, g, b), min(r, g, b)
        df = mx - mn
        h = 0
        if mx != mn:
            if mx == r: h = (g - b) / df + (6 if g < b else 0)
            elif mx == g: h = (b - r) / df + 2
            else: h = (r - g) / df + 4
            h /= 6
        s = 0 if mx == 0 else df / mx
        return h * 360, s, mx

    @staticmethod
    def _hsv_to_rgb(h, s, v):
        h /= 360
        i = int(h * 6)
        f = h * 6 - i
        p = v * (1 - s)
        q = v * (1 - f * s)
        t = v * (1 - (1 - f) * s)
        i %= 6
        r, g, b = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)][i]
        return int(r * 255), int(g * 255), int(b * 255)


# ═══════════════════════════════════════════════════════════════════
# 56. ASCII ART
# ═══════════════════════════════════════════════════════════════════

class AsciiArt:
    FONTS = {
        "standard": {"A": ["  #  ", " # # ", "#####", "#   #", "#   #"], "B": ["#### ", "#   #", "#### ", "#   #", "#### "]},
    }

    @staticmethod
    def text_to_ascii(text: str) -> str:
        chars = " .:-=+*#%@"
        result = []
        for char in text[:20]:
            width = 8
            height = 8
            art = []
            for y in range(height):
                row = ""
                for x in range(width):
                    cx = (x - width / 2) / (width / 4)
                    cy = (y - height / 2) / (height / 4)
                    v = math.exp(-(cx * cx + cy * cy))
                    idx = int(v * (len(chars) - 1))
                    row += chars[idx]
                art.append(row)
            result.append("\n".join(art))
        return "\n\n".join(result)

    @staticmethod
    def box(width: int = 20, height: int = 5, char: str = "#") -> str:
        top = char * width
        middle = char + " " * (width - 2) + char
        return "\n".join([top] + [middle] * (height - 2) + [top])


# ═══════════════════════════════════════════════════════════════════
# 57. SYSTEM DIAGNOSTICS
# ═══════════════════════════════════════════════════════════════════

class SystemDiagnostics:
    @staticmethod
    def check_python() -> dict:
        return {"version": os.sys.version, "platform": os.sys.platform, "executable": os.sys.executable}

    @staticmethod
    def check_disk() -> dict:
        try:
            st = os.statvfs("/")
            total = st.f_blocks * st.f_frsize
            free = st.f_bavail * st.f_frsize
            used = total - free
            return {"total_gb": round(total / 1073741824, 2), "used_gb": round(used / 1073741824, 2),
                    "free_gb": round(free / 1073741824, 2), "percent_used": round(used / total * 100, 1)}
        except: return {"error": "Unable to check disk"}

    @staticmethod
    def check_environment() -> dict:
        return {"home": os.path.expanduser("~"), "cwd": os.getcwd(), "user": os.getenv("USER", "unknown"),
                "shell": os.getenv("SHELL", "unknown"), "path_count": len(os.getenv("PATH", "").split(":"))}

    @staticmethod
    def run_diagnostics() -> dict:
        return {"python": SystemDiagnostics.check_python(), "disk": SystemDiagnostics.check_disk(),
                "environment": SystemDiagnostics.check_environment()}


# ═══════════════════════════════════════════════════════════════════
# 58. WORD COUNTER
# ═══════════════════════════════════════════════════════════════════

class WordCounter:
    @staticmethod
    def count_words(text: str) -> int:
        return len(text.split())

    @staticmethod
    def count_chars(text: str, include_spaces: bool = True) -> int:
        return len(text) if include_spaces else len(text.replace(" ", ""))

    @staticmethod
    def count_sentences(text: str) -> int:
        return len([s for s in re.split(r'[.!?]+', text) if s.strip()])

    @staticmethod
    def count_paragraphs(text: str) -> int:
        return len([p for p in text.split("\n\n") if p.strip()])

    @staticmethod
    def word_frequency(text: str) -> dict:
        words = text.lower().split()
        freq = {}
        for w in words:
            w = w.strip(".,!?;:\"'()-")
            if len(w) > 2:
                freq[w] = freq.get(w, 0) + 1
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20])

    @staticmethod
    def reading_time(text: str, wpm: int = 200) -> float:
        words = len(text.split())
        return round(words / wpm, 1)

    @staticmethod
    def speaking_time(text: str, wpm: int = 150) -> float:
        words = len(text.split())
        return round(words / wpm, 1)


# ═══════════════════════════════════════════════════════════════════
# 59. CRYPTOGRAPHY
# ═══════════════════════════════════════════════════════════════════

class Cryptography:
    @staticmethod
    def caesar_encrypt(text: str, shift: int = 3) -> str:
        result = []
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                result.append(chr((ord(c) - base + shift) % 26 + base))
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def caesar_decrypt(text: str, shift: int = 3) -> str:
        return Cryptography.caesar_encrypt(text, -shift)

    @staticmethod
    def vigenere_encrypt(text: str, key: str) -> str:
        result = []
        key_idx = 0
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                shift = ord(key[key_idx % len(key)].lower()) - ord('a')
                result.append(chr((ord(c) - base + shift) % 26 + base))
                key_idx += 1
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def vigenere_decrypt(text: str, key: str) -> str:
        result = []
        key_idx = 0
        for c in text:
            if c.isalpha():
                base = ord('A') if c.isupper() else ord('a')
                shift = ord(key[key_idx % len(key)].lower()) - ord('a')
                result.append(chr((ord(c) - base - shift) % 26 + base))
                key_idx += 1
            else:
                result.append(c)
        return "".join(result)

    @staticmethod
    def base64_encode(text: str) -> str:
        return base64.b64encode(text.encode()).decode()

    @staticmethod
    def base64_decode(text: str) -> str:
        return base64.b64decode(text.encode()).decode()

    @staticmethod
    def rot13(text: str) -> str:
        return Cryptography.caesar_encrypt(text, 13)


# ═══════════════════════════════════════════════════════════════════
# 60. NETWORK TOOLS
# ═══════════════════════════════════════════════════════════════════

class NetworkTools:
    @staticmethod
    def ping(host: str, count: int = 4) -> str:
        try:
            result = subprocess.run(["ping", "-c", str(count), host], capture_output=True, text=True, timeout=15)
            return result.stdout[-1000:] if result.returncode == 0 else f"Ping failed: {host}"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def dns_lookup(domain: str) -> str:
        try:
            result = subprocess.run(["nslookup", domain], capture_output=True, text=True, timeout=10)
            return result.stdout[:500] if result.returncode == 0 else f"Lookup failed: {domain}"
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def port_check(host: str, port: int, timeout: int = 3) -> dict:
        import socket
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            sock.close()
            return {"host": host, "port": port, "open": result == 0}
        except Exception as e:
            return {"host": host, "port": port, "open": False, "error": str(e)}

    @staticmethod
    def get_public_ip() -> str:
        try:
            result = subprocess.run(["curl", "-s", "ifconfig.me"], capture_output=True, text=True, timeout=10)
            return result.stdout.strip() if result.returncode == 0 else "Unable to get IP"
        except:
            return "Unable to get IP"

    @staticmethod
    def url_info(url: str) -> dict:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        return {"scheme": parsed.scheme, "hostname": parsed.hostname, "path": parsed.path,
                "query": parsed.query, "fragment": parsed.fragment}


# ═══════════════════════════════════════════════════════════════════
# 61. IMAGE INPUT
# ═══════════════════════════════════════════════════════════════════

class ImageInput:
    """Image input, analysis, and processing system."""

    SUPPORTED_FORMATS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".svg", ".ico"}
    PIXEL_SAMPLES = {
        "ASCII": " .:-=+*#%@",
        "BLOCK": " ",
        "SHADE": " ░▒▓█",
        "DENSE": " .oO0#@",
    }

    def __init__(self, data_dir: str = "images"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._image_cache: dict[str, dict] = {}

    def load_image(self, filepath: str) -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            return {"error": f"Unsupported format: {path.suffix}"}

        try:
            size = path.stat().st_size
            header = self._read_header(path)
            fmt = self._detect_format(header)
            info = {
                "path": str(path.absolute()),
                "filename": path.name,
                "format": fmt,
                "size_bytes": size,
                "size_kb": round(size / 1024, 2),
                "size_mb": round(size / 1048576, 3),
                "extension": path.suffix.lower(),
                "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat(),
            }

            if fmt == "PNG":
                dims = self._parse_png_dimensions(path)
                if dims:
                    info["width"] = dims[0]
                    info["height"] = dims[1]
            elif fmt in ("JPEG", "JPG"):
                dims = self._parse_jpeg_dimensions(path)
                if dims:
                    info["width"] = dims[0]
                    info["height"] = dims[1]

            if "width" in info and "height" in info:
                info["aspect_ratio"] = round(info["width"] / info["height"], 2)
                info["megapixels"] = round(info["width"] * info["height"] / 1000000, 2)

            self._image_cache[str(path)] = info
            return info
        except Exception as e:
            return {"error": str(e)}

    def _read_header(self, path: Path, size: int = 32) -> bytes:
        with open(path, "rb") as f:
            return f.read(size)

    def _detect_format(self, header: bytes) -> str:
        if header[:8] == b'\x89PNG\r\n\x1a\n': return "PNG"
        if header[:2] == b'\xff\xd8\xff': return "JPEG"
        if header[:4] == b'GIF8': return "GIF"
        if header[:2] == b'BM': return "BMP"
        if header[:4] == b'RIFF' and header[8:12] == b'WEBP': return "WEBP"
        if header[:6] in (b'GIF87a', b'GIF89a'): return "GIF"
        if header[:4] == b'\x00\x00\x01\x00': return "ICO"
        if header[:4] == b'\x00\x00\x02\x00': return "CUR"
        return "UNKNOWN"

    def _parse_png_dimensions(self, path: Path) -> tuple[int, int] | None:
        try:
            with open(path, "rb") as f:
                f.read(16)
                width = int.from_bytes(f.read(4), "big")
                height = int.from_bytes(f.read(4), "big")
                return (width, height)
        except:
            return None

    def _parse_jpeg_dimensions(self, path: Path) -> tuple[int, int] | None:
        try:
            with open(path, "rb") as f:
                data = f.read()
            i = 2
            while i < len(data) - 1:
                if data[i] == 0xFF:
                    marker = data[i + 1]
                    if marker in (0xC0, 0xC1, 0xC2):
                        height = int.from_bytes(data[i + 5:i + 7], "big")
                        width = int.from_bytes(data[i + 7:i + 9], "big")
                        return (width, height)
                    if marker == 0xD9:
                        break
                    if marker in (0xD0, 0xD1, 0xD2, 0xD3, 0xD4, 0xD5, 0xD6, 0xD7, 0xD8, 0x01):
                        i += 2
                    else:
                        length = int.from_bytes(data[i + 2:i + 4], "big")
                        i += 2 + length
                else:
                    i += 1
        except:
            pass
        return None

    def image_to_ascii(self, filepath: str, width: int = 60, charset: str = "ASCII") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        try:
            chars = self.PIXEL_SAMPLES.get(charset, self.PIXEL_SAMPLES["ASCII"])
            with open(path, "rb") as f:
                data = f.read()

            fmt = self._detect_format(data[:32])
            if fmt == "PNG":
                dims = self._parse_png_dimensions(path)
            elif fmt == "JPEG":
                dims = self._parse_jpeg_dimensions(path)
            else:
                dims = None

            if dims:
                img_w, img_h = dims
                height = int(width * img_h / img_w * 0.55)
            else:
                img_w, img_h = 100, 100
                height = int(width * 0.55)

            pixels = self._extract_pixel_data(path, img_w, img_h, width, height)

            ascii_lines = []
            for row in pixels:
                line = ""
                for brightness in row:
                    idx = min(len(chars) - 1, int(brightness * (len(chars) - 1)))
                    line += chars[idx]
                ascii_lines.append(line)

            return {
                "ascii": "\n".join(ascii_lines),
                "width": width,
                "height": height,
                "charset": charset,
                "original_dims": f"{img_w}x{img_h}",
                "lines": len(ascii_lines),
            }
        except Exception as e:
            return {"error": str(e)}

    def _extract_pixel_data(self, path: Path, orig_w: int, orig_h: int, target_w: int, target_h: int) -> list[list[float]]:
        try:
            with open(path, "rb") as f:
                data = f.read()

            pixels = []
            file_size = len(data)
            for y in range(target_h):
                row = []
                for x in range(target_w):
                    sample_x = int(x * orig_w / target_w) if target_w > 0 else 0
                    sample_y = int(y * orig_h / target_h) if target_h > 0 else 0
                    offset = min(file_size - 1, (sample_y * orig_w + sample_x) * 3)
                    if offset < file_size:
                        brightness = data[offset % file_size] / 255.0
                    else:
                        brightness = 0.5
                    row.append(brightness)
                pixels.append(row)
            return pixels
        except:
            return [[0.5] * target_w for _ in range(target_h)]

    def extract_colors(self, filepath: str, num_colors: int = 5) -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        try:
            with open(path, "rb") as f:
                data = f.read()

            color_freq: dict[tuple[int, int, int], int] = {}
            step = max(1, len(data) // 10000)
            for i in range(0, min(len(data), 30000), step * 3):
                if i + 2 < len(data):
                    r = data[i]
                    g = data[i + 1]
                    b = data[i + 2]
                    r_q = r // 32 * 32
                    g_q = g // 32 * 32
                    b_q = b // 32 * 32
                    color = (r_q, g_q, b_q)
                    color_freq[color] = color_freq.get(color, 0) + 1

            sorted_colors = sorted(color_freq.items(), key=lambda x: x[1], reverse=True)[:num_colors]
            total = sum(c[1] for c in sorted_colors) or 1

            colors = []
            for (r, g, b), count in sorted_colors:
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                colors.append({
                    "hex": hex_color,
                    "rgb": {"r": r, "g": g, "b": b},
                    "percentage": round(count / total * 100, 1),
                })

            return {
                "dominant_colors": colors,
                "total_colors_found": len(color_freq),
                "sample_size": min(len(data), 30000),
            }
        except Exception as e:
            return {"error": str(e)}

    def get_histogram(self, filepath: str) -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        try:
            with open(path, "rb") as f:
                data = f.read()

            r_hist = [0] * 256
            g_hist = [0] * 256
            b_hist = [0] * 256

            for i in range(0, min(len(data), 30000), 3):
                if i + 2 < len(data):
                    r_hist[data[i]] += 1
                    g_hist[data[i + 1]] += 1
                    b_hist[data[i + 2]] += 1

            return {
                "red": r_hist,
                "green": g_hist,
                "blue": b_hist,
                "total_pixels": min(len(data) // 3, 10000),
            }
        except Exception as e:
            return {"error": str(e)}

    def compare_images(self, path1: str, path2: str) -> dict:
        info1 = self.load_image(path1)
        info2 = self.load_image(path2)

        if "error" in info1 or "error" in info2:
            return {"error": "One or both files not found"}

        try:
            with open(path1, "rb") as f:
                data1 = f.read()
            with open(path2, "rb") as f:
                data2 = f.read()

            sample1 = data1[:10000]
            sample2 = data2[:10000]

            hash1 = hashlib.md5(sample1).hexdigest()
            hash2 = hashlib.md5(sample2).hexdigest()

            identical = hash1 == hash2

            size_diff = abs(info1.get("size_bytes", 0) - info2.get("size_bytes", 0))

            return {
                "identical": identical,
                "hash_match": hash1 == hash2,
                "size_difference_bytes": size_diff,
                "image1": {"path": path1, "size": info1.get("size_kb"), "format": info1.get("format")},
                "image2": {"path": path2, "size": info2.get("size_kb"), "format": info2.get("format")},
            }
        except Exception as e:
            return {"error": str(e)}

    def create_thumbnail(self, filepath: str, max_size: int = 100) -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        info = self.load_image(filepath)
        if "error" in info:
            return info

        width = info.get("width", 100)
        height = info.get("height", 100)

        scale = min(max_size / width, max_size / height) if width > 0 and height > 0 else 1
        thumb_w = int(width * scale)
        thumb_h = int(height * scale)

        return {
            "original": f"{width}x{height}",
            "thumbnail": f"{thumb_w}x{thumb_h}",
            "scale": round(scale, 3),
            "original_size": info.get("size_kb"),
        }

    def analyze_image(self, filepath: str) -> dict:
        info = self.load_image(filepath)
        if "error" in info:
            return info

        colors = self.extract_colors(filepath, 3)
        ascii_art = self.image_to_ascii(filepath, width=40)

        analysis = {
            **info,
            "dominant_colors": colors.get("dominant_colors", []),
            "ascii_preview": ascii_art.get("ascii", "")[:500],
            "analysis_complete": True,
        }

        if "width" in info and "height" in info:
            w, h = info["width"], info["height"]
            if w > 3000 or h > 3000:
                analysis["resolution"] = "very_high"
            elif w > 1920 or h > 1080:
                analysis["resolution"] = "high"
            elif w > 800 or h > 600:
                analysis["resolution"] = "medium"
            else:
                analysis["resolution"] = "low"

        return analysis

    def scan_directory(self, directory: str = ".") -> dict:
        path = Path(directory)
        if not path.exists():
            return {"error": f"Directory not found: {directory}"}

        images = []
        for f in path.rglob("*"):
            if f.is_file() and f.suffix.lower() in self.SUPPORTED_FORMATS:
                images.append({
                    "path": str(f),
                    "name": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 2),
                    "format": f.suffix.upper(),
                })

        return {
            "total_images": len(images),
            "total_size_mb": round(sum(i["size_kb"] for i in images) / 1024, 2),
            "by_format": {},
            "images": sorted(images, key=lambda x: x["size_kb"], reverse=True)[:50],
        }

    def capture_camera(self) -> dict:
        try:
            import subprocess
            output_path = self.data_dir / f"capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            result = subprocess.run(
                ["imagesnap", "-q", str(output_path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and output_path.exists():
                return self.load_image(str(output_path))
            return {"error": "Camera capture failed. Install imagesnap: brew install imagesnap"}
        except Exception as e:
            return {"error": f"Camera error: {e}"}

    def screenshot(self) -> dict:
        try:
            import subprocess
            output_path = self.data_dir / f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            result = subprocess.run(
                ["screencapture", "-x", str(output_path)],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0 and output_path.exists():
                return self.load_image(str(output_path))
            return {"error": "Screenshot failed"}
        except Exception as e:
            return {"error": f"Screenshot error: {e}"}


# ═══════════════════════════════════════════════════════════════════
# 62. IMAGE ANALYZER
# ═══════════════════════════════════════════════════════════════════

class ImageAnalyzer:
    """Advanced image analysis: objects, edges, patterns, text extraction, metadata."""

    def __init__(self, data_dir: str = "images"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def analyze(self, filepath: str) -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        result = {"path": str(path.absolute()), "filename": path.name}
        result["metadata"] = self.extract_metadata(filepath)
        result["colors"] = self.analyze_colors(filepath)
        result["edges"] = self.detect_edges(filepath)
        result["patterns"] = self.detect_patterns(filepath)
        result["brightness"] = self.analyze_brightness(filepath)
        result["quality"] = self.assess_quality(filepath)
        result["objects"] = self.detect_objects(filepath)
        result["text_regions"] = self.find_text_regions(filepath)
        result["composition"] = self.analyze_composition(filepath)
        result["hash"] = self.perceptual_hash(filepath)
        return result

    def extract_metadata(self, filepath: str) -> dict:
        path = Path(filepath)
        info = {"filename": path.name, "extension": path.suffix.lower(),
                "size_bytes": path.stat().st_size, "modified": datetime.fromtimestamp(path.stat().st_mtime).isoformat()}

        try:
            with open(path, "rb") as f:
                data = f.read(1024)
            if data[:8] == b'\x89PNG\r\n\x1a\n':
                info["format"] = "PNG"
                if len(data) > 16:
                    info["width"] = int.from_bytes(data[16:20], "big")
                    info["height"] = int.from_bytes(data[20:24], "big")
                    info["bit_depth"] = data[24]
                    info["color_type"] = data[25]
            elif data[:2] == b'\xff\xd8\xff':
                info["format"] = "JPEG"
                i = 2
                while i < len(data) - 1:
                    if data[i] == 0xFF:
                        marker = data[i + 1]
                        if marker in (0xE0, 0xE1, 0xE2):
                            length = int.from_bytes(data[i + 2:i + 4], "big")
                            if marker == 0xE1 and b"Exif" in data[i + 4:i + 4 + length]:
                                info["has_exif"] = True
                            i += 2 + length
                        elif marker == 0xD9:
                            break
                        else:
                            try:
                                length = int.from_bytes(data[i + 2:i + 4], "big")
                                i += 2 + length
                            except:
                                break
                    else:
                        i += 1
            elif data[:4] == b'GIF8':
                info["format"] = "GIF"
            elif data[:4] == b'RIFF':
                info["format"] = "WEBP"
            else:
                info["format"] = "UNKNOWN"
        except:
            info["format"] = "UNKNOWN"

        return info

    def analyze_colors(self, filepath: str) -> dict:
        try:
            with open(path if isinstance(filepath, Path) else Path(filepath), "rb") as f:
                data = f.read()

            color_count: dict[tuple[int, int, int], int] = {}
            for i in range(0, min(len(data), 50000), 3):
                if i + 2 < len(data):
                    r, g, b = data[i] // 32 * 32, data[i + 1] // 32 * 32, data[i + 2] // 32 * 32
                    color_count[(r, g, b)] = color_count.get((r, g, b), 0) + 1

            sorted_colors = sorted(color_count.items(), key=lambda x: x[1], reverse=True)[:10]
            total = sum(c[1] for c in sorted_colors) or 1

            colors = []
            for (r, g, b), count in sorted_colors:
                hex_c = f"#{r:02x}{g:02x}{b:02x}"
                colors.append({"hex": hex_c, "rgb": (r, g, b), "percentage": round(count / total * 100, 1)})

            unique_colors = len(color_count)
            brightness_vals = [(r * 0.299 + g * 0.587 + b * 0.114) / 255 for (r, g, b) in color_count.keys()]
            avg_brightness = sum(brightness_vals) / len(brightness_vals) if brightness_vals else 0

            dominant = colors[0] if colors else None
            is_dark = avg_brightness < 0.4
            is_grayscale = all(abs(r - g) < 20 and abs(g - b) < 20 for (r, g, b), _ in sorted_colors[:5])

            return {"dominant": dominant, "palette": colors, "unique_colors": unique_colors,
                    "avg_brightness": round(avg_brightness, 3), "is_dark": is_dark,
                    "is_grayscale": is_grayscale, "color_variety": "high" if unique_colors > 50 else "medium" if unique_colors > 10 else "low"}
        except Exception as e:
            return {"error": str(e)}

    def detect_edges(self, filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            width = 100
            height = 100
            pixels = []
            for y in range(height):
                row = []
                for x in range(width):
                    offset = min(len(data) - 1, (y * width + x) * 3)
                    if offset < len(data):
                        brightness = data[offset % len(data)] / 255.0
                    else:
                        brightness = 0.5
                    row.append(brightness)
                pixels.append(row)

            edges = []
            edge_count = 0
            for y in range(1, height - 1):
                row = []
                for x in range(1, width - 1):
                    gx = -pixels[y-1][x-1] - 2*pixels[y][x-1] - pixels[y+1][x-1] + pixels[y-1][x+1] + 2*pixels[y][x+1] + pixels[y+1][x+1]
                    gy = -pixels[y-1][x-1] - 2*pixels[y-1][x] - pixels[y-1][x+1] + pixels[y+1][x-1] + 2*pixels[y+1][x] + pixels[y+1][x+1]
                    magnitude = min(1.0, math.sqrt(gx * gx + gy * gy))
                    is_edge = magnitude > 0.3
                    row.append(is_edge)
                    if is_edge:
                        edge_count += 1
                edges.append(row)

            total_pixels = (width - 2) * (height - 2)
            edge_density = edge_count / total_pixels if total_pixels > 0 else 0

            horizontal_edges = sum(1 for y in range(len(edges)) for x in range(1, len(edges[y]) - 1) if edges[y][x] and not edges[y][x-1] and not edges[y][x+1])
            vertical_edges = sum(1 for y in range(1, len(edges) - 1) for x in range(len(edges[y])) if edges[y][x] and not edges[y-1][x] and not edges[y+1][x])

            return {"has_edges": edge_count > 0, "edge_density": round(edge_density, 4),
                    "total_edges": edge_count, "edge_type": "complex" if edge_density > 0.15 else "moderate" if edge_density > 0.05 else "simple",
                    "horizontal_edges": horizontal_edges, "vertical_edges": vertical_edges,
                    "sharpness": "high" if edge_density > 0.1 else "medium" if edge_density > 0.03 else "low"}
        except Exception as e:
            return {"error": str(e)}

    def detect_patterns(self, filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            size = 80
            pixels = []
            for y in range(size):
                row = []
                for x in range(size):
                    offset = min(len(data) - 1, (y * size + x) * 3)
                    row.append(data[offset % len(data)] / 255.0)
                pixels.append(row)

            gradients = []
            for y in range(1, size - 1):
                for x in range(1, size - 1):
                    gx = pixels[y][x + 1] - pixels[y][x - 1]
                    gy = pixels[y + 1][x] - pixels[y - 1][x]
                    gradients.append(math.sqrt(gx * gx + gy * gy))

            avg_gradient = sum(gradients) / len(gradients) if gradients else 0
            gradient_std = math.sqrt(sum((g - avg_gradient) ** 2 for g in gradients) / len(gradients)) if gradients else 0

            regions = 4
            region_brightness = []
            block_size = size // regions
            for ry in range(regions):
                for rx in range(regions):
                    total = 0
                    count = 0
                    for y in range(ry * block_size, (ry + 1) * block_size):
                        for x in range(rx * block_size, (rx + 1) * block_size):
                            total += pixels[y][x]
                            count += 1
                    region_brightness.append(total / count if count > 0 else 0)

            brightness_variance = max(region_brightness) - min(region_brightness) if region_brightness else 0

            symmetry_h = 0
            for y in range(size):
                for x in range(size // 2):
                    if abs(pixels[y][x] - pixels[y][size - 1 - x]) < 0.2:
                        symmetry_h += 1
            symmetry_h /= (size * size // 2)

            symmetry_v = 0
            for y in range(size // 2):
                for x in range(size):
                    if abs(pixels[y][x] - pixels[size - 1 - y][x]) < 0.2:
                        symmetry_v += 1
            symmetry_v /= (size * size // 2)

            return {"gradient_avg": round(avg_gradient, 4), "gradient_std": round(gradient_std, 4),
                    "texture": "rough" if gradient_std > 0.2 else "smooth" if gradient_std < 0.05 else "moderate",
                    "symmetry_h": round(symmetry_h, 3), "symmetry_v": round(symmetry_v, 3),
                    "is_symmetric": symmetry_h > 0.7 or symmetry_v > 0.7,
                    "brightness_variance": round(brightness_variance, 3),
                    "uniform": brightness_variance < 0.1}
        except Exception as e:
            return {"error": str(e)}

    def analyze_brightness(self, filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            brightnesses = []
            for i in range(0, min(len(data), 50000), 3):
                if i + 2 < len(data):
                    b = data[i] * 0.299 + data[i + 1] * 0.587 + data[i + 2] * 0.114
                    brightnesses.append(b / 255)

            if not brightnesses:
                return {"error": "No pixel data"}

            avg = sum(brightnesses) / len(brightnesses)
            min_b = min(brightnesses)
            max_b = max(brightnesses)
            std = math.sqrt(sum((b - avg) ** 2 for b in brightnesses) / len(brightnesses))

            histogram = [0] * 10
            for b in brightnesses:
                idx = min(9, int(b * 10))
                histogram[idx] += 1

            dark_ratio = sum(histogram[:3]) / len(brightnesses)
            bright_ratio = sum(histogram[7:]) / len(brightnesses)

            return {"average": round(avg, 3), "min": round(min_b, 3), "max": round(max_b, 3),
                    "std_dev": round(std, 3), "range": round(max_b - min_b, 3),
                    "histogram": histogram, "dark_ratio": round(dark_ratio, 3),
                    "bright_ratio": round(bright_ratio, 3),
                    "exposure": "underexposed" if avg < 0.3 else "overexposed" if avg > 0.7 else "well_exposed"}
        except Exception as e:
            return {"error": str(e)}

    def assess_quality(self, filepath: str) -> dict:
        try:
            path = Path(filepath)
            size = path.stat().st_size
            with open(path, "rb") as f:
                data = f.read()

            score = 0
            factors = {}

            if size > 100000: score += 2; factors["file_size"] = "good"
            elif size > 10000: score += 1; factors["file_size"] = "medium"
            else: factors["file_size"] = "small"

            brightness = self.analyze_brightness(filepath)
            if brightness.get("exposure") == "well_exposed":
                score += 2; factors["exposure"] = "good"
            elif brightness.get("exposure") != "error":
                score += 1; factors["exposure"] = "poor"
            else:
                factors["exposure"] = "unknown"

            edges = self.detect_edges(filepath)
            if edges.get("sharpness") == "high":
                score += 2; factors["sharpness"] = "high"
            elif edges.get("sharpness") == "medium":
                score += 1; factors["sharpness"] = "medium"
            else:
                factors["sharpness"] = "low"

            colors = self.analyze_colors(filepath)
            if colors.get("color_variety") == "high":
                score += 2; factors["color_richness"] = "high"
            elif colors.get("color_variety") == "medium":
                score += 1; factors["color_richness"] = "medium"
            else:
                factors["color_richness"] = "low"

            patterns = self.detect_patterns(filepath)
            if patterns.get("gradient_avg", 0) > 0.05:
                score += 1; factors["detail"] = "good"
            else:
                factors["detail"] = "low"

            quality = "excellent" if score >= 8 else "good" if score >= 6 else "fair" if score >= 4 else "poor"

            return {"score": score, "max_score": 10, "quality": quality, "factors": factors}
        except Exception as e:
            return {"error": str(e)}

    def detect_objects(self, filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            size = 50
            pixels = []
            for y in range(size):
                row = []
                for x in range(size):
                    offset = min(len(data) - 1, (y * size + x) * 3)
                    row.append(data[offset % len(data)] / 255.0)
                pixels.append(row)

            bright_regions = []
            for y in range(0, size - 5, 5):
                for x in range(0, size - 5, 5):
                    region = [pixels[y + dy][x + dx] for dy in range(5) for dx in range(5)]
                    avg = sum(region) / len(region)
                    if avg > 0.7 or avg < 0.3:
                        bright_regions.append({"x": x, "y": y, "brightness": round(avg, 2), "type": "bright" if avg > 0.7 else "dark"})

            return {"possible_regions": bright_regions[:10], "total_regions": len(bright_regions),
                    "analysis": "Color-based region detection (upgrade with ML for object recognition)"}
        except Exception as e:
            return {"error": str(e)}

    def find_text_regions(self, filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            width = 80
            height = 80
            pixels = []
            for y in range(height):
                row = []
                for x in range(width):
                    offset = min(len(data) - 1, (y * width + x) * 3)
                    row.append(data[offset % len(data)] / 255.0)
                pixels.append(row)

            text_regions = []
            for y in range(0, height - 8, 4):
                for x in range(0, width - 20, 4):
                    region = [pixels[y + dy][x + dx] for dy in range(8) for dx in range(20)]
                    avg = sum(region) / len(region)
                    contrast = max(region) - min(region)
                    if contrast > 0.5 and 0.2 < avg < 0.8:
                        text_regions.append({"x": x, "y": y, "w": 20, "h": 8, "contrast": round(contrast, 2)})

            return {"possible_text": text_regions[:10], "total_regions": len(text_regions),
                    "analysis": "Contrast-based text detection (upgrade with OCR for actual text extraction)"}
        except Exception as e:
            return {"error": str(e)}

    def analyze_composition(self, filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            size = 100
            pixels = []
            for y in range(size):
                row = []
                for x in range(size):
                    offset = min(len(data) - 1, (y * size + x) * 3)
                    row.append(data[offset % len(data)] / 255.0)
                pixels.append(row)

            third = size // 3
            rule_of_thirds = []
            for ry in range(3):
                for rx in range(3):
                    region = [pixels[y][x] for y in range(ry * third, (ry + 1) * third) for x in range(rx * third, (rx + 1) * third)]
                    avg = sum(region) / len(region) if region else 0
                    rule_of_thirds.append({"x": rx, "y": ry, "interest": round(avg, 3)})

            focal_points = [r for r in rule_of_thirds if r["interest"] > 0.6 or r["interest"] < 0.3]

            center_region = [pixels[y][x] for y in range(third, 2 * third) for x in range(third, 2 * third)]
            center_interest = sum(center_region) / len(center_region) if center_region else 0

            return {"rule_of_thirds": rule_of_thirds, "focal_points": focal_points,
                    "center_interest": round(center_interest, 3),
                    "balance": "centered" if center_interest > 0.6 else "distributed"}
        except Exception as e:
            return {"error": str(e)}

    def perceptual_hash(self, filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            size = 8
            pixels = []
            for y in range(size):
                row = []
                for x in range(size):
                    offset = min(len(data) - 1, (y * size + x) * 3)
                    row.append(data[offset % len(data)] / 255.0)
                pixels.append(row)

            avg = sum(sum(row) for row in pixels) / (size * size)
            bits = ""
            for row in pixels:
                for p in row:
                    bits += "1" if p > avg else "0"

            hex_hash = hex(int(bits, 2))[2:].zfill(16)

            return {"hash": hex_hash, "bits": bits, "size": f"{size}x{size}",
                    "algorithm": "average_hash"}
        except Exception as e:
            return {"error": str(e)}

    def compare_images(self, path1: str, path2: str) -> dict:
        hash1 = self.perceptual_hash(path1)
        hash2 = self.perceptual_hash(path2)

        if "error" in hash1 or "error" in hash2:
            return {"error": "Failed to hash one or both images"}

        h1 = hash1.get("bits", "")
        h2 = hash2.get("bits", "")

        if len(h1) != len(h2):
            return {"error": "Image sizes differ"}

        hamming_distance = sum(c1 != c2 for c1, c2 in zip(h1, h2))
        max_distance = len(h1)
        similarity = 1 - (hamming_distance / max_distance) if max_distance > 0 else 0

        return {"similar": hamming_distance < 10, "similarity": round(similarity, 4),
                "hamming_distance": hamming_distance, "max_distance": max_distance,
                "hash1": hash1.get("hash"), "hash2": hash2.get("hash"),
                "verdict": "identical" if hamming_distance == 0 else "very_similar" if hamming_distance < 5 else "similar" if hamming_distance < 15 else "different"}

    def batch_analyze(self, directory: str) -> list[dict]:
        path = Path(directory)
        if not path.exists():
            return [{"error": f"Directory not found: {directory}"}]

        results = []
        for f in sorted(path.rglob("*")):
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}:
                try:
                    quality = self.assess_quality(str(f))
                    colors = self.analyze_colors(str(f))
                    results.append({"path": str(f), "name": f.name, "size_kb": round(f.stat().st_size / 1024, 2),
                                    "quality": quality.get("quality", "unknown"), "quality_score": quality.get("score", 0),
                                    "dominant_color": colors.get("dominant", {}).get("hex", "unknown")})
                except:
                    results.append({"path": str(f), "name": f.name, "error": "analysis failed"})

        return sorted(results, key=lambda x: x.get("quality_score", 0), reverse=True)


# ═══════════════════════════════════════════════════════════════════
# 63. IMAGE FINDER
# ═══════════════════════════════════════════════════════════════════

class ImageFinder:
    """Find, search, and organize images by various criteria."""

    def __init__(self, data_dir: str = "images"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self._index: dict[str, dict] = {}
        self._analyzer = ImageAnalyzer(data_dir)
        self._build_index()

    def _build_index(self):
        for f in self.data_dir.rglob("*"):
            if f.is_file() and f.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}:
                self._index[str(f)] = {"path": str(f), "name": f.name, "size": f.stat().st_size,
                                       "modified": f.stat().st_mtime, "extension": f.suffix.lower()}

    def find_by_name(self, query: str) -> list[dict]:
        q = query.lower()
        return [v for k, v in self._index.items() if q in v["name"].lower()]

    def find_by_extension(self, ext: str) -> list[dict]:
        ext = ext.lower() if ext.startswith(".") else f".{ext.lower()}"
        return [v for v in self._index.values() if v["extension"] == ext]

    def find_by_size(self, min_bytes: int = 0, max_bytes: int = float("inf")) -> list[dict]:
        return [v for v in self._index.values() if min_bytes <= v["size"] <= max_bytes]

    def find_by_date(self, after: str = "", before: str = "") -> list[dict]:
        results = list(self._index.values())
        if after:
            after_ts = datetime.fromisoformat(after).timestamp()
            results = [v for v in results if v["modified"] >= after_ts]
        if before:
            before_ts = datetime.fromisoformat(before).timestamp()
            results = [v for v in results if v["modified"] <= before_ts]
        return results

    def find_by_color(self, hex_color: str) -> list[dict]:
        try:
            target = int(hex_color.lstrip("#"), 16)
            tr, tg, tb = (target >> 16) & 255, (target >> 8) & 255, target & 255
        except:
            return []

        results = []
        for path, info in self._index.items():
            try:
                colors = self._analyzer.analyze_colors(path)
                dominant = colors.get("dominant", {})
                dom_rgb = dominant.get("rgb", (0, 0, 0))
                if isinstance(dom_rgb, (list, tuple)) and len(dom_rgb) == 3:
                    dr, dg, db = dom_rgb
                    distance = math.sqrt((tr - dr) ** 2 + (tg - dg) ** 2 + (tb - db) ** 2)
                    if distance < 100:
                        results.append({**info, "color_distance": round(distance, 1)})
            except:
                pass

        return sorted(results, key=lambda x: x.get("color_distance", 999))

    def find_similar(self, filepath: str, max_results: int = 5) -> list[dict]:
        if filepath not in self._index:
            return []

        hash1 = self._analyzer.perceptual_hash(filepath)
        if "error" in hash1:
            return []

        bits1 = hash1.get("bits", "")
        results = []

        for path, info in self._index.items():
            if path == filepath:
                continue
            try:
                hash2 = self._analyzer.perceptual_hash(path)
                bits2 = hash2.get("bits", "")
                if len(bits1) == len(bits2):
                    distance = sum(c1 != c2 for c1, c2 in zip(bits1, bits2))
                    similarity = 1 - (distance / len(bits1)) if bits1 else 0
                    if similarity > 0.5:
                        results.append({**info, "similarity": round(similarity, 4), "distance": distance})
            except:
                pass

        return sorted(results, key=lambda x: x.get("similarity", 0), reverse=True)[:max_results]

    def find_duplicates(self) -> list[list[dict]]:
        hash_groups: dict[str, list[dict]] = {}
        for path, info in self._index.items():
            try:
                h = self._analyzer.perceptual_hash(path)
                hash_val = h.get("hash", "")
                if hash_val not in hash_groups:
                    hash_groups[hash_val] = []
                hash_groups[hash_val].append(info)
            except:
                pass

        return [group for group in hash_groups.values() if len(group) > 1]

    def find_large(self, min_mb: float = 1.0) -> list[dict]:
        min_bytes = int(min_mb * 1048576)
        return sorted(self.find_by_size(min_bytes=min_bytes), key=lambda x: x["size"], reverse=True)

    def find_recent(self, days: int = 7) -> list[dict]:
        after = (datetime.now() - timedelta(days=days)).isoformat()
        return sorted(self.find_by_date(after=after), key=lambda x: x["modified"], reverse=True)

    def get_stats(self) -> dict:
        total_size = sum(v["size"] for v in self._index.values())
        extensions = defaultdict(int)
        for v in self._index.values():
            extensions[v["extension"]] += 1

        return {"total_images": len(self._index), "total_size_mb": round(total_size / 1048576, 2),
                "by_extension": dict(extensions), "data_dir": str(self.data_dir)}

    def create_collection(self, name: str, image_paths: list[str]) -> dict:
        collection_dir = self.data_dir / "collections" / name
        collection_dir.mkdir(parents=True, exist_ok=True)

        linked = 0
        for path in image_paths:
            src = Path(path)
            if src.exists():
                dst = collection_dir / src.name
                if not dst.exists():
                    try:
                        import shutil
                        shutil.copy2(str(src), str(dst))
                        linked += 1
                    except:
                        pass

        manifest = {"name": name, "images": [str(p) for p in collection_dir.glob("*") if p.is_file()],
                    "created": datetime.now().isoformat(), "count": linked}
        (collection_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
        return manifest

    def get_collection(self, name: str) -> dict:
        manifest_path = self.data_dir / "collections" / name / "manifest.json"
        if manifest_path.exists():
            return json.loads(manifest_path.read_text())
        return {"error": f"Collection not found: {name}"}

    def list_collections(self) -> list[dict]:
        collections_dir = self.data_dir / "collections"
        if not collections_dir.exists():
            return []

        results = []
        for d in collections_dir.iterdir():
            if d.is_dir():
                manifest_path = d / "manifest.json"
                if manifest_path.exists():
                    results.append(json.loads(manifest_path.read_text()))
        return results

    def find_by_quality(self, min_quality: str = "good") -> list[dict]:
        quality_order = {"poor": 0, "fair": 1, "good": 2, "excellent": 3}
        min_score = quality_order.get(min_quality, 0)

        results = []
        for path, info in self._index.items():
            try:
                quality = self._analyzer.assess_quality(path)
                score = quality.get("score", 0)
                if score >= min_score * 2:
                    results.append({**info, "quality": quality.get("quality", "unknown"), "score": score})
            except:
                pass

        return sorted(results, key=lambda x: x.get("score", 0), reverse=True)

    def search(self, query: str) -> list[dict]:
        results = self.find_by_name(query)
        if not results:
            ext_results = self.find_by_extension(query)
            results.extend(ext_results)
        return results


# ═══════════════════════════════════════════════════════════════════
# 64. IMAGE GENERATOR
# ═══════════════════════════════════════════════════════════════════

class ImageGenerator:
    """Generate images from patterns, gradients, and text descriptions."""

    PATTERNS = {
        "checkerboard": lambda x, y, s: ((x // s) + (y // s)) % 2,
        "stripes_h": lambda x, y, s: (y // s) % 2,
        "stripes_v": lambda x, y, s: (x // s) % 2,
        "stripes_d": lambda x, y, s: ((x + y) // s) % 2,
        "circles": lambda x, y, s: int(math.sqrt((x - s * 5) ** 2 + (y - s * 5) ** 2) / s) % 2,
        "diamonds": lambda x, y, s: (abs(x - s * 5) + abs(y - s * 5)) // s % 2,
        "waves": lambda x, y, s: int((math.sin(x / s) + 1) * 5) % 2 == (y // s) % 2,
        "spiral": lambda x, y, s: int(math.atan2(y - s * 5, x - s * 5) * 3 + math.sqrt((x - s * 5) ** 2 + (y - s * 5) ** 2) / s) % 2,
        "grid": lambda x, y, s: 1 if x % s == 0 or y % s == 0 else 0,
        "dots": lambda x, y, s: 1 if (x % s == s // 2 and y % s == s // 2) else 0,
        "crosses": lambda x, y, s: 1 if (x % s == s // 2 or y % s == s // 2) else 0,
        "zigzag": lambda x, y, s: 1 if (x + (y // s) * s) % (s * 2) < s else 0,
        "herringbone": lambda x, y, s: ((x // s) + (y // s) * (1 if (y // s) % 2 == 0 else -1)) % 2,
        "bricks": lambda x, y, s: 1 if (y % s == 0) or ((x + (s // 2 if (y // s) % 2 else 0)) % s == 0) else 0,
        "star": lambda x, y, s: 1 if abs(x - s * 5) * abs(y - s * 5) < (s * 2) ** 2 else 0,
    }

    GRADIENTS = {
        "linear": lambda x, y, w, h: x / w if w > 0 else 0,
        "radial": lambda x, y, w, h: math.sqrt((x - w / 2) ** 2 + (y - h / 2) ** 2) / (math.sqrt((w / 2) ** 2 + (h / 2) ** 2) or 1),
        "diagonal": lambda x, y, w, h: (x + y) / (w + h) if (w + h) > 0 else 0,
        "vertical": lambda x, y, w, h: y / h if h > 0 else 0,
        "angular": lambda x, y, w, h: (math.atan2(y - h / 2, x - w / 2) + math.pi) / (2 * math.pi),
    }

    def __init__(self, data_dir: str = "generated"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def generate_pattern(self, pattern: str = "checkerboard", width: int = 100, height: int = 100,
                        cell_size: int = 10, color1: tuple = (0, 0, 0), color2: tuple = (255, 255, 255),
                        output: str = "") -> dict:
        if pattern not in self.PATTERNS:
            return {"error": f"Unknown pattern: {pattern}. Available: {list(self.PATTERNS.keys())}"}

        if not output:
            output = str(self.data_dir / f"{pattern}_{width}x{height}.png")

        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                val = self.PATTERNS[pattern](x, y, cell_size)
                row.append(color1 if val else color2)
            pixels.append(row)

        self._write_ppm(pixels, output)
        return {"path": output, "pattern": pattern, "width": width, "height": height,
                "cell_size": cell_size, "colors": [color1, color2]}

    def generate_gradient(self, gradient: str = "linear", width: int = 100, height: int = 100,
                         color_start: tuple = (0, 0, 0), color_end: tuple = (255, 255, 255),
                         output: str = "") -> dict:
        if gradient not in self.GRADIENTS:
            return {"error": f"Unknown gradient: {gradient}. Available: {list(self.GRADIENTS.keys())}"}

        if not output:
            output = str(self.data_dir / f"gradient_{gradient}_{width}x{height}.png")

        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                t = self.GRADIENTS[gradient](x, y, width, height)
                t = max(0, min(1, t))
                r = int(color_start[0] + (color_end[0] - color_start[0]) * t)
                g = int(color_start[1] + (color_end[1] - color_start[1]) * t)
                b = int(color_start[2] + (color_end[2] - color_start[2]) * t)
                row.append((r, g, b))
            pixels.append(row)

        self._write_ppm(pixels, output)
        return {"path": output, "gradient": gradient, "width": width, "height": height}

    def generate_noise(self, width: int = 100, height: int = 100, noise_type: str = "white",
                      output: str = "") -> dict:
        if not output:
            output = str(self.data_dir / f"noise_{noise_type}_{width}x{height}.png")

        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                if noise_type == "white":
                    r = g = b = random.randint(0, 255)
                elif noise_type == "gaussian":
                    val = max(0, min(255, int(random.gauss(128, 50))))
                    r = g = b = val
                elif noise_type == "salt_pepper":
                    r = random.choice([0, 255, 128])
                    g = r
                    b = r
                else:
                    r = g = b = random.randint(0, 255)
                row.append((r, g, b))
            pixels.append(row)

        self._write_ppm(pixels, output)
        return {"path": output, "noise_type": noise_type, "width": width, "height": height}

    def generate_fractal(self, width: int = 100, height: int = 100, fractal_type: str = "mandelbrot",
                        max_iter: int = 50, output: str = "") -> dict:
        if not output:
            output = str(self.data_dir / f"fractal_{fractal_type}_{width}x{height}.png")

        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                cx = (x - width / 2) / (width / 4)
                cy = (y - height / 2) / (height / 4)

                if fractal_type == "mandelbrot":
                    zx, zy = 0.0, 0.0
                    iteration = 0
                    while zx * zx + zy * zy < 4 and iteration < max_iter:
                        zx, zy = zx * zx - zy * zy + cx, 2 * zx * zy + cy
                        iteration += 1
                elif fractal_type == "julia":
                    zx, zy = cx, cy
                    cx, cy = -0.7, 0.27015
                    iteration = 0
                    while zx * zx + zy * zy < 4 and iteration < max_iter:
                        zx, zy = zx * zx - zy * zy + cx, 2 * zx * zy + cy
                        iteration += 1
                elif fractal_type == "sierpinski":
                    iteration = 0
                    px, py = x / width, y / height
                    while iteration < max_iter:
                        px, py = (px * 2) % 1, (py * 2) % 1
                        if px > 0.5 and py > 0.5:
                            break
                        iteration += 1
                else:
                    iteration = 0

                t = iteration / max_iter if max_iter > 0 else 0
                r = int(9 * (1 - t) * t * t * t * 255)
                g = int(15 * (1 - t) * (1 - t) * t * t * 255)
                b = int(8.5 * (1 - t) * (1 - t) * (1 - t) * t * 255)
                row.append((min(255, r), min(255, g), min(255, b)))
            pixels.append(row)

        self._write_ppm(pixels, output)
        return {"path": output, "fractal": fractal_type, "width": width, "height": height, "max_iter": max_iter}

    def generate_text_image(self, text: str = "HELLO", width: int = 200, height: int = 50,
                           font_size: int = 5, color: tuple = (255, 255, 255),
                           bg_color: tuple = (0, 0, 0), output: str = "") -> dict:
        if not output:
            output = str(self.data_dir / f"text_{text[:10].replace(' ', '_')}.png")

        FONT = {
            'A': ["01110", "10001", "11111", "10001", "10001"],
            'B': ["11110", "10001", "11110", "10001", "11110"],
            'C': ["01111", "10000", "10000", "10000", "01111"],
            'D': ["11110", "10001", "10001", "10001", "11110"],
            'E': ["11111", "10000", "11110", "10000", "11111"],
            'F': ["11111", "10000", "11110", "10000", "10000"],
            'G': ["01111", "10000", "10011", "10001", "01111"],
            'H': ["10001", "10001", "11111", "10001", "10001"],
            'I': ["11111", "00100", "00100", "00100", "11111"],
            'J': ["00111", "00010", "00010", "10010", "01100"],
            'K': ["10001", "10010", "11100", "10010", "10001"],
            'L': ["10000", "10000", "10000", "10000", "11111"],
            'M': ["10001", "11011", "10101", "10001", "10001"],
            'N': ["10001", "11001", "10101", "10011", "10001"],
            'O': ["01110", "10001", "10001", "10001", "01110"],
            'P': ["11110", "10001", "11110", "10000", "10000"],
            'Q': ["01110", "10001", "10101", "10010", "01101"],
            'R': ["11110", "10001", "11110", "10010", "10001"],
            'S': ["01111", "10000", "01110", "00001", "11110"],
            'T': ["11111", "00100", "00100", "00100", "00100"],
            'U': ["10001", "10001", "10001", "10001", "01110"],
            'V': ["10001", "10001", "10001", "01010", "00100"],
            'W': ["10001", "10001", "10101", "11011", "10001"],
            'X': ["10001", "01010", "00100", "01010", "10001"],
            'Y': ["10001", "01010", "00100", "00100", "00100"],
            'Z': ["11111", "00010", "00100", "01000", "11111"],
            ' ': ["00000", "00000", "00000", "00000", "00000"],
            '0': ["01110", "10011", "10101", "11001", "01110"],
            '1': ["00100", "01100", "00100", "00100", "01110"],
            '2': ["01110", "10001", "00110", "01000", "11111"],
            '3': ["11110", "00001", "01110", "00001", "11110"],
            '4': ["10010", "10010", "11111", "00010", "00010"],
            '5': ["11111", "10000", "11110", "00001", "11110"],
            '6': ["01110", "10000", "11110", "10001", "01110"],
            '7': ["11111", "00001", "00010", "00100", "01000"],
            '8': ["01110", "10001", "01110", "10001", "01110"],
            '9': ["01110", "10001", "01111", "00001", "01110"],
        }

        pixels = [[bg_color for _ in range(width)] for _ in range(height)]

        char_width = font_size + 1
        start_x = max(0, (width - len(text) * char_width * font_size) // 2)
        start_y = max(0, (height - 5 * font_size) // 2)

        for ci, char in enumerate(text.upper()):
            if char in FONT:
                for row_idx, row in enumerate(FONT[char]):
                    for col_idx, pixel in enumerate(row):
                        if pixel == '1':
                            for dy in range(font_size):
                                for dx in range(font_size):
                                    px = start_x + ci * char_width * font_size + col_idx * font_size + dx
                                    py = start_y + row_idx * font_size + dy
                                    if 0 <= px < width and 0 <= py < height:
                                        pixels[py][px] = color

        self._write_ppm(pixels, output)
        return {"path": output, "text": text, "width": width, "height": height, "font_size": font_size}

    def generate_gradient_image(self, width: int = 100, height: int = 100,
                               colors: list[tuple] = None, output: str = "") -> dict:
        if colors is None:
            colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

        if not output:
            output = str(self.data_dir / f"multi_gradient_{width}x{height}.png")

        pixels = []
        for y in range(height):
            row = []
            for x in range(width):
                t = x / width if width > 0 else 0
                segment = t * (len(colors) - 1)
                idx = min(int(segment), len(colors) - 2)
                local_t = segment - idx
                r = int(colors[idx][0] + (colors[idx + 1][0] - colors[idx][0]) * local_t)
                g = int(colors[idx][1] + (colors[idx + 1][1] - colors[idx][1]) * local_t)
                b = int(colors[idx][2] + (colors[idx + 1][2] - colors[idx][2]) * local_t)
                row.append((min(255, r), min(255, g), min(255, b)))
            pixels.append(row)

        self._write_ppm(pixels, output)
        return {"path": output, "width": width, "height": height, "color_count": len(colors)}

    def _write_ppm(self, pixels: list[list[tuple]], filepath: str):
        height = len(pixels)
        width = len(pixels[0]) if pixels else 0
        with open(filepath, 'wb') as f:
            f.write(f'P6\n{width} {height}\n255\n'.encode())
            for row in pixels:
                for r, g, b in row:
                    f.write(bytes([min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]))

    def list_patterns(self) -> list[str]:
        return list(self.PATTERNS.keys())

    def list_gradients(self) -> list[str]:
        return list(self.GRADIENTS.keys())


# ═══════════════════════════════════════════════════════════════════
# 65. IMAGE EDITOR
# ═══════════════════════════════════════════════════════════════════

class ImageEditor:
    """Edit images: crop, rotate, flip, adjust brightness/contrast."""

    def __init__(self, data_dir: str = "edited"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def crop(self, filepath: str, x: int, y: int, width: int, height: int, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"cropped_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []
            for iy in range(height):
                row = []
                for ix in range(width):
                    sx = x + ix
                    sy = y + iy
                    offset = min(len(data) - 1, (sy * img_width + sx) * 3)
                    if offset < len(data):
                        row.append((data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                                   data[offset + 2] if offset + 2 < len(data) else 0))
                    else:
                        row.append((0, 0, 0))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "original": filepath, "crop_box": (x, y, width, height)}
        except Exception as e:
            return {"error": str(e)}

    def rotate(self, filepath: str, angle: int = 90, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"rotated_{angle}_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            if angle == 90:
                for x in range(img_width):
                    row = []
                    for y in range(img_height - 1, -1, -1):
                        offset = min(len(data) - 1, (y * img_width + x) * 3)
                        row.append((data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                                   data[offset + 2] if offset + 2 < len(data) else 0))
                    pixels.append(row)
            elif angle == 180:
                for y in range(img_height - 1, -1, -1):
                    row = []
                    for x in range(img_width - 1, -1, -1):
                        offset = min(len(data) - 1, (y * img_width + x) * 3)
                        row.append((data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                                   data[offset + 2] if offset + 2 < len(data) else 0))
                    pixels.append(row)
            elif angle == 270:
                for x in range(img_width - 1, -1, -1):
                    row = []
                    for y in range(img_height):
                        offset = min(len(data) - 1, (y * img_width + x) * 3)
                        row.append((data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                                   data[offset + 2] if offset + 2 < len(data) else 0))
                    pixels.append(row)
            else:
                return {"error": f"Unsupported angle: {angle}. Use 90, 180, or 270"}

            self._write_ppm(pixels, output)
            return {"path": output, "original": filepath, "angle": angle}
        except Exception as e:
            return {"error": str(e)}

    def flip(self, filepath: str, direction: str = "horizontal", output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"flipped_{direction}_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    if direction == "horizontal":
                        sx = img_width - 1 - x
                    else:
                        sx = x
                    if direction == "vertical":
                        sy = img_height - 1 - y
                    else:
                        sy = y
                    offset = min(len(data) - 1, (sy * img_width + sx) * 3)
                    row.append((data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                               data[offset + 2] if offset + 2 < len(data) else 0))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "original": filepath, "direction": direction}
        except Exception as e:
            return {"error": str(e)}

    def adjust_brightness(self, filepath: str, factor: float = 1.5, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"bright_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    offset = min(len(data) - 1, (y * img_width + x) * 3)
                    r = min(255, int(data[offset] * factor))
                    g = min(255, int(data[offset + 1] * factor)) if offset + 1 < len(data) else 0
                    b = min(255, int(data[offset + 2] * factor)) if offset + 2 < len(data) else 0
                    row.append((r, g, b))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "original": filepath, "brightness_factor": factor}
        except Exception as e:
            return {"error": str(e)}

    def adjust_contrast(self, filepath: str, factor: float = 1.5, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"contrast_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    offset = min(len(data) - 1, (y * img_width + x) * 3)
                    r = min(255, max(0, int((data[offset] - 128) * factor + 128)))
                    g = min(255, max(0, int((data[offset + 1] - 128) * factor + 128))) if offset + 1 < len(data) else 0
                    b = min(255, max(0, int((data[offset + 2] - 128) * factor + 128))) if offset + 2 < len(data) else 0
                    row.append((r, g, b))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "original": filepath, "contrast_factor": factor}
        except Exception as e:
            return {"error": str(e)}

    def resize(self, filepath: str, new_width: int, new_height: int, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"resized_{new_width}x{new_height}_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            orig_width = 100
            orig_height = 100
            pixels = []

            for y in range(new_height):
                row = []
                for x in range(new_width):
                    sx = int(x * orig_width / new_width) if new_width > 0 else 0
                    sy = int(y * orig_height / new_height) if new_height > 0 else 0
                    offset = min(len(data) - 1, (sy * orig_width + sx) * 3)
                    row.append((data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                               data[offset + 2] if offset + 2 < len(data) else 0))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "original": filepath, "new_size": f"{new_width}x{new_height}"}
        except Exception as e:
            return {"error": str(e)}

    def _write_ppm(self, pixels: list[list[tuple]], filepath: str):
        height = len(pixels)
        width = len(pixels[0]) if pixels else 0
        with open(filepath, 'wb') as f:
            f.write(f'P6\n{width} {height}\n255\n'.encode())
            for row in pixels:
                for r, g, b in row:
                    f.write(bytes([min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]))


# ═══════════════════════════════════════════════════════════════════
# 66. IMAGE FILTER
# ═══════════════════════════════════════════════════════════════════

class ImageFilter:
    """Apply filters to images: blur, sharpen, grayscale, sepia, invert."""

    def __init__(self, data_dir: str = "filtered"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def grayscale(self, filepath: str, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        if not output:
            output = str(self.data_dir / f"gray_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    offset = min(len(data) - 1, (y * img_width + x) * 3)
                    r, g, b = data[offset], data[offset + 1] if offset + 1 < len(data) else 0, data[offset + 2] if offset + 2 < len(data) else 0
                    gray = int(r * 0.299 + g * 0.587 + b * 0.114)
                    row.append((gray, gray, gray))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "filter": "grayscale"}
        except Exception as e:
            return {"error": str(e)}

    def sepia(self, filepath: str, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        if not output:
            output = str(self.data_dir / f"sepia_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    offset = min(len(data) - 1, (y * img_width + x) * 3)
                    r, g, b = data[offset], data[offset + 1] if offset + 1 < len(data) else 0, data[offset + 2] if offset + 2 < len(data) else 0
                    tr = min(255, int(r * 0.393 + g * 0.769 + b * 0.189))
                    tg = min(255, int(r * 0.349 + g * 0.686 + b * 0.168))
                    tb = min(255, int(r * 0.272 + g * 0.534 + b * 0.131))
                    row.append((tr, tg, tb))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "filter": "sepia"}
        except Exception as e:
            return {"error": str(e)}

    def invert(self, filepath: str, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        if not output:
            output = str(self.data_dir / f"invert_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    offset = min(len(data) - 1, (y * img_width + x) * 3)
                    row.append((255 - data[offset], 255 - (data[offset + 1] if offset + 1 < len(data) else 0),
                               255 - (data[offset + 2] if offset + 2 < len(data) else 0)))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "filter": "invert"}
        except Exception as e:
            return {"error": str(e)}

    def blur(self, filepath: str, radius: int = 2, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        if not output:
            output = str(self.data_dir / f"blur_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    r_sum, g_sum, b_sum, count = 0, 0, 0, 0
                    for dy in range(-radius, radius + 1):
                        for dx in range(-radius, radius + 1):
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < img_width and 0 <= ny < img_height:
                                offset = min(len(data) - 1, (ny * img_width + nx) * 3)
                                r_sum += data[offset]
                                g_sum += data[offset + 1] if offset + 1 < len(data) else 0
                                b_sum += data[offset + 2] if offset + 2 < len(data) else 0
                                count += 1
                    if count > 0:
                        row.append((r_sum // count, g_sum // count, b_sum // count))
                    else:
                        row.append((0, 0, 0))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "filter": "blur", "radius": radius}
        except Exception as e:
            return {"error": str(e)}

    def sharpen(self, filepath: str, strength: float = 1.5, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        if not output:
            output = str(self.data_dir / f"sharp_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            kernel = [[0, -1, 0], [-1, 5, -1], [0, -1, 0]]

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    r_sum, g_sum, b_sum = 0, 0, 0
                    for ky in range(3):
                        for kx in range(3):
                            nx, ny = x + kx - 1, y + ky - 1
                            if 0 <= nx < img_width and 0 <= ny < img_height:
                                offset = min(len(data) - 1, (ny * img_width + nx) * 3)
                                weight = kernel[ky][kx]
                                r_sum += data[offset] * weight
                                g_sum += (data[offset + 1] if offset + 1 < len(data) else 0) * weight
                                b_sum += (data[offset + 2] if offset + 2 < len(data) else 0) * weight
                    row.append((min(255, max(0, int(r_sum * strength))), min(255, max(0, int(g_sum * strength))),
                               min(255, max(0, int(b_sum * strength)))))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "filter": "sharpen", "strength": strength}
        except Exception as e:
            return {"error": str(e)}

    def pixelate(self, filepath: str, block_size: int = 5, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}
        if not output:
            output = str(self.data_dir / f"pixel_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    bx = (x // block_size) * block_size
                    by = (y // block_size) * block_size
                    offset = min(len(data) - 1, (by * img_width + bx) * 3)
                    row.append((data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                               data[offset + 2] if offset + 2 < len(data) else 0))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "filter": "pixelate", "block_size": block_size}
        except Exception as e:
            return {"error": str(e)}

    def _write_ppm(self, pixels: list[list[tuple]], filepath: str):
        height = len(pixels)
        width = len(pixels[0]) if pixels else 0
        with open(filepath, 'wb') as f:
            f.write(f'P6\n{width} {height}\n255\n'.encode())
            for row in pixels:
                for r, g, b in row:
                    f.write(bytes([min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]))

    def list_filters(self) -> list[str]:
        return ["grayscale", "sepia", "invert", "blur", "sharpen", "pixelate"]


# ═══════════════════════════════════════════════════════════════════
# 67. IMAGE DIFF
# ═══════════════════════════════════════════════════════════════════

class ImageDiff:
    """Find differences between two images."""

    def __init__(self, data_dir: str = "diffs"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def diff(self, path1: str, path2: str, threshold: int = 30, output: str = "") -> dict:
        p1, p2 = Path(path1), Path(path2)
        if not p1.exists() or not p2.exists():
            return {"error": "One or both files not found"}

        try:
            with open(p1, "rb") as f:
                data1 = f.read()
            with open(p2, "rb") as f:
                data2 = f.read()

            width = 100
            height = 100
            diff_pixels = []
            diff_count = 0
            diff_regions = []

            for y in range(height):
                row = []
                for x in range(width):
                    offset = min(len(data1) - 1, (y * width + x) * 3)
                    offset2 = min(len(data2) - 1, (y * width + x) * 3)

                    r1, g1, b1 = data1[offset], data1[offset + 1] if offset + 1 < len(data1) else 0, data1[offset + 2] if offset + 2 < len(data1) else 0
                    r2, g2, b2 = data2[offset2], data2[offset2 + 1] if offset2 + 1 < len(data2) else 0, data2[offset2 + 2] if offset2 + 2 < len(data2) else 0

                    diff = abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
                    is_diff = diff > threshold * 3

                    if is_diff:
                        row.append((255, 0, 0))
                        diff_count += 1
                        diff_regions.append({"x": x, "y": y, "diff_magnitude": diff // 3})
                    else:
                        gray1 = int(r1 * 0.299 + g1 * 0.587 + b1 * 0.114)
                        row.append((gray1, gray1, gray1))
                diff_pixels.append(row)

            if not output:
                output = str(self.data_dir / f"diff_{p1.stem}_{p2.stem}.png")

            self._write_ppm(diff_pixels, output)

            total_pixels = width * height
            diff_percentage = (diff_count / total_pixels * 100) if total_pixels > 0 else 0

            return {"path": output, "diff_count": diff_count, "total_pixels": total_pixels,
                    "diff_percentage": round(diff_percentage, 2), "threshold": threshold,
                    "similar": diff_percentage < 5,
                    "verdict": "identical" if diff_percentage < 0.1 else "very_similar" if diff_percentage < 1 else "similar" if diff_percentage < 10 else "different",
                    "sample_diffs": diff_regions[:20]}
        except Exception as e:
            return {"error": str(e)}

    def _write_ppm(self, pixels: list[list[tuple]], filepath: str):
        height = len(pixels)
        width = len(pixels[0]) if pixels else 0
        with open(filepath, 'wb') as f:
            f.write(f'P6\n{width} {height}\n255\n'.encode())
            for row in pixels:
                for r, g, b in row:
                    f.write(bytes([min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]))


# ═══════════════════════════════════════════════════════════════════
# 68. IMAGE COLLAGE
# ═══════════════════════════════════════════════════════════════════

class ImageCollage:
    """Create collages from multiple images."""

    def __init__(self, data_dir: str = "collages"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def create_grid(self, image_paths: list[str], cols: int = 2, cell_width: int = 100, cell_height: int = 100,
                   border: int = 2, output: str = "") -> dict:
        if not image_paths:
            return {"error": "No images provided"}

        rows = (len(image_paths) + cols - 1) // cols
        total_width = cols * cell_width + (cols + 1) * border
        total_height = rows * cell_height + (rows + 1) * border

        if not output:
            output = str(self.data_dir / f"grid_{cols}x{rows}.png")

        pixels = [[(50, 50, 50) for _ in range(total_width)] for _ in range(total_height)]

        for idx, img_path in enumerate(image_paths[:cols * rows]):
            img_path = Path(img_path)
            if not img_path.exists():
                continue

            row = idx // cols
            col = idx % cols
            start_x = border + col * (cell_width + border)
            start_y = border + row * (cell_height + border)

            try:
                with open(img_path, "rb") as f:
                    data = f.read()

                for y in range(cell_height):
                    for x in range(cell_width):
                        offset = min(len(data) - 1, (y * cell_width + x) * 3)
                        px = start_x + x
                        py = start_y + y
                        if 0 <= px < total_width and 0 <= py < total_height:
                            pixels[py][px] = (data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                                             data[offset + 2] if offset + 2 < len(data) else 0)
            except:
                pass

        self._write_ppm(pixels, output)
        return {"path": output, "images": len(image_paths), "cols": cols, "rows": rows,
                "size": f"{total_width}x{total_height}"}

    def create_montage(self, image_paths: list[str], width: int = 400, height: int = 400,
                      output: str = "") -> dict:
        if not image_paths:
            return {"error": "No images provided"}

        if not output:
            output = str(self.data_dir / "montage.png")

        pixels = [[(30, 30, 30) for _ in range(width)] for _ in range(height)]

        for idx, img_path in enumerate(image_paths):
            img_path = Path(img_path)
            if not img_path.exists():
                continue

            try:
                with open(img_path, "rb") as f:
                    data = f.read()

                region_size = int(math.sqrt(len(image_paths)))
                cell_w = width // max(1, region_size)
                cell_h = height // max(1, region_size)
                col = idx % max(1, region_size)
                row = idx // max(1, region_size)

                for y in range(min(cell_h, height)):
                    for x in range(min(cell_w, width)):
                        offset = min(len(data) - 1, (y * cell_w + x) * 3)
                        px = col * cell_w + x
                        py = row * cell_h + y
                        if 0 <= px < width and 0 <= py < height:
                            pixels[py][px] = (data[offset], data[offset + 1] if offset + 1 < len(data) else 0,
                                             data[offset + 2] if offset + 2 < len(data) else 0)
            except:
                pass

        self._write_ppm(pixels, output)
        return {"path": output, "images": len(image_paths), "size": f"{width}x{height}"}

    def _write_ppm(self, pixels: list[list[tuple]], filepath: str):
        height = len(pixels)
        width = len(pixels[0]) if pixels else 0
        with open(filepath, 'wb') as f:
            f.write(f'P6\n{width} {height}\n255\n'.encode())
            for row in pixels:
                for r, g, b in row:
                    f.write(bytes([min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]))


# ═══════════════════════════════════════════════════════════════════
# 69. IMAGE WATERMARK
# ═══════════════════════════════════════════════════════════════════

class ImageWatermark:
    """Add watermarks to images."""

    def __init__(self, data_dir: str = "watermarked"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def add_text_watermark(self, filepath: str, text: str = "WATERMARK", position: str = "center",
                          opacity: float = 0.3, output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"wm_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    offset = min(len(data) - 1, (y * img_width + x) * 3)
                    r, g, b = data[offset], data[offset + 1] if offset + 1 < len(data) else 0, data[offset + 2] if offset + 2 < len(data) else 0

                    in_watermark = False
                    if position == "center":
                        cx, cy = img_width // 2, img_height // 2
                        in_watermark = abs(x - cx) < len(text) * 3 and abs(y - cy) < 5
                    elif position == "tile":
                        in_watermark = (x % 20 < 10 and y % 20 < 3)

                    if in_watermark:
                        r = int(r * (1 - opacity) + 255 * opacity)
                        g = int(g * (1 - opacity) + 255 * opacity)
                        b = int(b * (1 - opacity) + 255 * opacity)

                    row.append((min(255, r), min(255, g), min(255, b)))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "watermark": text, "position": position, "opacity": opacity}
        except Exception as e:
            return {"error": str(e)}

    def add_pattern_watermark(self, filepath: str, pattern: str = "diagonal", opacity: float = 0.2,
                             output: str = "") -> dict:
        path = Path(filepath)
        if not path.exists():
            return {"error": f"File not found: {filepath}"}

        if not output:
            output = str(self.data_dir / f"wm_{pattern}_{path.name}")

        try:
            with open(path, "rb") as f:
                data = f.read()

            img_width = 100
            img_height = 100
            pixels = []

            for y in range(img_height):
                row = []
                for x in range(img_width):
                    offset = min(len(data) - 1, (y * img_width + x) * 3)
                    r, g, b = data[offset], data[offset + 1] if offset + 1 < len(data) else 0, data[offset + 2] if offset + 2 < len(data) else 0

                    has_pattern = False
                    if pattern == "diagonal":
                        has_pattern = (x + y) % 20 < 3
                    elif pattern == "horizontal":
                        has_pattern = y % 20 < 2
                    elif pattern == "vertical":
                        has_pattern = x % 20 < 2
                    elif pattern == "dots":
                        has_pattern = (x % 10 == 0 and y % 10 == 0)

                    if has_pattern:
                        r = int(r * (1 - opacity) + 255 * opacity)
                        g = int(g * (1 - opacity) + 255 * opacity)
                        b = int(b * (1 - opacity) + 255 * opacity)

                    row.append((min(255, r), min(255, g), min(255, b)))
                pixels.append(row)

            self._write_ppm(pixels, output)
            return {"path": output, "pattern": pattern, "opacity": opacity}
        except Exception as e:
            return {"error": str(e)}

    def _write_ppm(self, pixels: list[list[tuple]], filepath: str):
        height = len(pixels)
        width = len(pixels[0]) if pixels else 0
        with open(filepath, 'wb') as f:
            f.write(f'P6\n{width} {height}\n255\n'.encode())
            for row in pixels:
                for r, g, b in row:
                    f.write(bytes([min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b))]))


# ═══════════════════════════════════════════════════════════════════
# 70. IMAGE COMPARATOR
# ═══════════════════════════════════════════════════════════════════

class ImageComparator:
    """Compare images using multiple metrics."""

    def __init__(self, data_dir: str = "comparisons"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def compare(self, path1: str, path2: str) -> dict:
        p1, p2 = Path(path1), Path(path2)
        if not p1.exists() or not p2.exists():
            return {"error": "One or both files not found"}

        try:
            with open(p1, "rb") as f:
                data1 = f.read()
            with open(p2, "rb") as f:
                data2 = f.read()

            metrics = {}
            metrics["file_size_diff"] = abs(p1.stat().st_size - p2.stat().st_size)
            metrics["file_size_ratio"] = round(min(p1.stat().st_size, p2.stat().st_size) / max(p1.stat().st_size, p2.stat().st_size), 3) if max(p1.stat().st_size, p2.stat().st_size) > 0 else 0

            hash1 = hashlib.md5(data1[:10000]).hexdigest()
            hash2 = hashlib.md5(data2[:10000]).hexdigest()
            metrics["hash_match"] = hash1 == hash2

            total_diff = 0
            pixel_count = 0
            for i in range(0, min(len(data1), len(data2), 30000), 3):
                if i + 2 < len(data1) and i + 2 < len(data2):
                    total_diff += abs(data1[i] - data2[i]) + abs(data1[i + 1] - data2[i + 1]) + abs(data1[i + 2] - data2[i + 2])
                    pixel_count += 1

            metrics["avg_pixel_diff"] = round(total_diff / (pixel_count * 3), 2) if pixel_count > 0 else 0
            metrics["pixel_similarity"] = round(1 - metrics["avg_pixel_diff"] / 255, 4)

            if metrics["pixel_similarity"] > 0.95:
                metrics["verdict"] = "identical"
            elif metrics["pixel_similarity"] > 0.8:
                metrics["verdict"] = "very_similar"
            elif metrics["pixel_similarity"] > 0.5:
                metrics["verdict"] = "similar"
            elif metrics["pixel_similarity"] > 0.2:
                metrics["verdict"] = "different"
            else:
                metrics["verdict"] = "completely_different"

            return {"image1": str(p1), "image2": str(p2), "metrics": metrics}
        except Exception as e:
            return {"error": str(e)}

    def batch_compare(self, paths: list[str]) -> list[dict]:
        results = []
        for i in range(len(paths)):
            for j in range(i + 1, len(paths)):
                result = self.compare(paths[i], paths[j])
                result["pair"] = f"{Path(paths[i]).name} vs {Path(paths[j]).name}"
                results.append(result)
        return sorted(results, key=lambda x: x.get("metrics", {}).get("pixel_similarity", 0), reverse=True)


# ═══════════════════════════════════════════════════════════════════
# 71. VIDEO ANALYZER
# ═══════════════════════════════════════════════════════════════════

class VideoAnalyzer:
    """Comprehensive video analysis, editing, and processing."""

    def __init__(self, data_dir: str = "video_analysis"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

    def _run_ffmpeg(self, args: list[str], timeout: int = 120) -> dict:
        try:
            r = subprocess.run(["ffmpeg"] + args, capture_output=True, text=True, timeout=timeout)
            return {"success": r.returncode == 0, "stdout": r.stdout[:500], "stderr": r.stderr[:500]}
        except FileNotFoundError:
            return {"success": False, "error": "ffmpeg not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def _run_ffprobe(self, args: list[str], timeout: int = 15) -> dict:
        try:
            r = subprocess.run(["ffprobe"] + args, capture_output=True, text=True, timeout=timeout)
            return {"success": r.returncode == 0, "output": r.stdout.strip()}
        except FileNotFoundError:
            return {"success": False, "error": "ffprobe not installed"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def analyze_video(self, path: str) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        info = {"path": str(p), "name": p.name, "size_bytes": p.stat().st_size,
                "size_mb": round(p.stat().st_size / 1048576, 2), "extension": p.suffix.lower()}

        probe = self._run_ffprobe([
            "-v", "error", "-show_format", "-show_streams",
            "-of", "json", str(p)
        ])

        if probe["success"] and probe["output"]:
            try:
                data = json.loads(probe["output"])
                fmt = data.get("format", {})
                info["duration"] = float(fmt.get("duration", 0))
                info["duration_str"] = self._format_duration(info["duration"])
                info["bitrate"] = int(fmt.get("bit_rate", 0))
                info["format_name"] = fmt.get("format_name", "unknown")
                info["nb_streams"] = int(fmt.get("nb_streams", 0))

                for s in data.get("streams", []):
                    codec_type = s.get("codec_type")
                    if codec_type == "video":
                        info["video"] = {
                            "codec": s.get("codec_name", "unknown"),
                            "width": int(s.get("width", 0)),
                            "height": int(s.get("height", 0)),
                            "fps": self._parse_fps(s.get("r_frame_rate", "0/1")),
                            "bitrate": int(s.get("bit_rate", 0)) if s.get("bit_rate") else 0,
                            "pix_fmt": s.get("pix_fmt", "unknown"),
                            "rotation": int(s.get("rotation", 0)),
                        }
                    elif codec_type == "audio":
                        info["audio"] = {
                            "codec": s.get("codec_name", "unknown"),
                            "sample_rate": int(s.get("sample_rate", 0)),
                            "channels": int(s.get("channels", 0)),
                            "bitrate": int(s.get("bit_rate", 0)) if s.get("bit_rate") else 0,
                        }
            except json.JSONDecodeError:
                pass

        if "video" in info:
            v = info["video"]
            if v["width"] and v["height"]:
                ratio = v["width"] / v["height"]
                if abs(ratio - 16/9) < 0.05:
                    info["aspect_ratio"] = "16:9"
                elif abs(ratio - 4/3) < 0.05:
                    info["aspect_ratio"] = "4:3"
                elif abs(ratio - 1) < 0.05:
                    info["aspect_ratio"] = "1:1"
                else:
                    info["aspect_ratio"] = f"{v['width']}:{v['height']}"

                if v["height"] >= 2160:
                    info["quality"] = "4K"
                elif v["height"] >= 1080:
                    info["quality"] = "1080p"
                elif v["height"] >= 720:
                    info["quality"] = "720p"
                elif v["height"] >= 480:
                    info["quality"] = "480p"
                else:
                    info["quality"] = f"{v['height']}p"

        return info

    def _parse_fps(self, fps_str: str) -> float:
        try:
            if "/" in fps_str:
                num, den = fps_str.split("/")
                return round(int(num) / int(den), 2)
            return float(fps_str)
        except (ValueError, ZeroDivisionError):
            return 0.0

    def _format_duration(self, seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        if h > 0:
            return f"{h}h {m}m {s}s"
        elif m > 0:
            return f"{m}m {s}s"
        return f"{s}s"

    def extract_frames(self, path: str, output_dir: str = "", interval: float = 1.0, max_frames: int = 50) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = Path(output_dir) if output_dir else self.data_dir / "frames" / p.stem
        out.mkdir(parents=True, exist_ok=True)

        result = self._run_ffmpeg([
            "-i", str(p), "-vf", f"fps=1/{interval}", "-vframes", str(max_frames),
            "-q:v", "2", str(out / "frame_%04d.jpg"), "-y"
        ], timeout=300)

        if result["success"]:
            frames = sorted(out.glob("frame_*.jpg"))
            return {"output_dir": str(out), "frames_extracted": len(frames),
                    "interval": f"{interval}s", "paths": [str(f) for f in frames[:10]]}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def extract_audio(self, path: str, output: str = "", format: str = "mp3") -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}_audio.{format}")
        codec = {"mp3": "libmp3lame", "aac": "aac", "wav": "pcm_s16le", "ogg": "libvorbis"}.get(format, "libmp3lame")

        result = self._run_ffmpeg([
            "-i", str(p), "-vn", "-acodec", codec, "-y", out
        ])

        if result["success"]:
            size = Path(out).stat().st_size if Path(out).exists() else 0
            return {"output": out, "format": format, "size_mb": round(size / 1048576, 2)}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def create_thumbnail(self, path: str, output: str = "", time_sec: float = 1.0) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}_thumb.jpg")
        result = self._run_ffmpeg([
            "-i", str(p), "-ss", str(time_sec), "-vframes", "1", "-q:v", "2", "-y", out
        ])

        if result["success"] and Path(out).exists():
            return {"output": out, "time": f"{time_sec}s", "size": Path(out).stat().st_size}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def create_thumbnails_grid(self, path: str, output: str = "", count: int = 6) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        duration = self._get_duration_sec(str(p))
        if duration <= 0:
            return {"error": "Cannot determine video duration"}

        out = output or str(self.data_dir / f"{p.stem}_grid.jpg")
        interval = duration / (count + 1)

        tmp = self.data_dir / "tmp_thumbs"
        tmp.mkdir(exist_ok=True)

        for i in range(count):
            t = interval * (i + 1)
            self._run_ffmpeg(["-i", str(p), "-ss", str(t), "-vframes", "1", "-y", str(tmp / f"t_{i}.jpg")])

        thumbs = sorted(tmp.glob("t_*.jpg"))
        if not thumbs:
            return {"error": "Failed to extract thumbnails"}

        grid_size = min(3, count)
        rows = (count + grid_size - 1) // grid_size

        filter_parts = []
        inputs = []
        for i, t in enumerate(thumbs):
            inputs.extend(["-i", str(t)])
            row, col = divmod(i, grid_size)
            filter_parts.append(f"[{i}]scale=320:-1[p{i}]")

        hstack = ""
        for r in range(rows):
            row_thumbs = [f"[p{r * grid_size + c}]" for c in range(grid_size) if r * grid_size + c < len(thumbs)]
            if len(row_thumbs) > 1:
                hstack += "".join(row_thumbs) + f"hstack=inputs={len(row_thumbs)}[row{r}];"
            elif row_thumbs:
                hstack += f"{row_thumbs[0]}copy[row{r}];"

        vstack_inputs = "".join(f"[row{r}]" for r in range(rows))
        if rows > 1:
            hstack += f"{vstack_inputs}vstack=inputs={rows}[out]"
        else:
            hstack = hstack.replace("[out]", "") + "[out]" if "[out]" not in hstack else hstack

        vstack_parts = "".join(f"[row{r}]" for r in range(rows))
        filter_str = ";".join(filter_parts) + ";" + hstack

        cmd = inputs + ["-filter_complex", filter_str, "-map", "[out]", "-y", out]
        result = self._run_ffmpeg(cmd)

        for t in tmp.glob("t_*.jpg"):
            t.unlink()
        tmp.rmdir()

        if result["success"] and Path(out).exists():
            return {"output": out, "thumbnails": count, "grid": f"{grid_size}x{rows}"}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def _get_duration_sec(self, path: str) -> float:
        probe = self._run_ffprobe(["-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path])
        if probe["success"]:
            try:
                return float(probe["output"])
            except ValueError:
                pass
        return 0.0

    def trim_video(self, path: str, start: float, end: float, output: str = "") -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}_trimmed{p.suffix}")
        duration = end - start

        result = self._run_ffmpeg([
            "-i", str(p), "-ss", str(start), "-t", str(duration),
            "-c", "copy", "-y", out
        ])

        if result["success"] and Path(out).exists():
            size = Path(out).stat().st_size
            return {"output": out, "start": start, "end": end, "duration": f"{duration:.1f}s", "size_mb": round(size / 1048576, 2)}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def resize_video(self, path: str, width: int, height: int, output: str = "") -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}_{width}x{height}{p.suffix}")
        result = self._run_ffmpeg([
            "-i", str(p), "-vf", f"scale={width}:{height}", "-c:a", "copy", "-y", out
        ])

        if result["success"] and Path(out).exists():
            return {"output": out, "width": width, "height": height}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def change_speed(self, path: str, speed: float, output: str = "") -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}_{speed}x{p.suffix}")
        video_filter = f"setpts={1/speed}*PTS"
        audio_filter = f"atempo={speed}" if 0.5 <= speed <= 2.0 else None

        cmd = ["-i", str(p), "-vf", video_filter]
        if audio_filter:
            cmd.extend(["-af", audio_filter])
        cmd.extend(["-y", out])

        result = self._run_ffmpeg(cmd)
        if result["success"] and Path(out).exists():
            return {"output": out, "speed": f"{speed}x"}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def add_text_overlay(self, path: str, text: str, output: str = "",
                         position: str = "center", font_size: int = 24, color: str = "white") -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}_text{p.suffix}")

        positions = {
            "center": "(w-text_w)/2:(h-text_h)/2",
            "top": "(w-text_w)/2:50",
            "bottom": "(w-text_w)/2:h-50",
            "top_left": "50:50",
            "top_right": "w-text_w-50:50",
            "bottom_left": "50:h-50",
            "bottom_right": "w-text_w-50:h-50",
        }
        pos = positions.get(position, positions["center"])

        escaped = text.replace("'", "\\'").replace(":", "\\:")
        drawtext = f"drawtext=text='{escaped}':fontsize={font_size}:fontcolor={color}:x={pos}"

        result = self._run_ffmpeg([
            "-i", str(p), "-vf", drawtext, "-c:a", "copy", "-y", out
        ])

        if result["success"] and Path(out).exists():
            return {"output": out, "text": text, "position": position, "color": color}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def add_watermark(self, path: str, watermark_text: str = "", output: str = "",
                      position: str = "bottom_right", opacity: float = 0.5) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}_wm{p.suffix}")

        positions = {
            "top_left": "10:10", "top_right": "w-tw-10:10",
            "bottom_left": "10:h-th-10", "bottom_right": "w-tw-10:h-th-10",
            "center": "(w-tw)/2:(h-th)/2",
        }
        pos = positions.get(position, positions["bottom_right"])

        escaped = watermark_text.replace("'", "\\'").replace(":", "\\:")
        drawtext = f"drawtext=text='{escaped}':fontsize=18:fontcolor=white@{opacity}:x={pos}"

        result = self._run_ffmpeg([
            "-i", str(p), "-vf", drawtext, "-c:a", "copy", "-y", out
        ])

        if result["success"] and Path(out).exists():
            return {"output": out, "watermark": watermark_text, "position": position}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def convert_format(self, path: str, target_format: str = "mp4", output: str = "") -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}.{target_format}")
        codec_map = {
            "mp4": ["-c:v", "libx264", "-c:a", "aac"],
            "avi": ["-c:v", "mpeg4", "-c:a", "mp3"],
            "mov": ["-c:v", "libx264", "-c:a", "aac"],
            "webm": ["-c:v", "libvpx", "-c:a", "libvorbis"],
            "mkv": ["-c:v", "libx264", "-c:a", "aac"],
            "gif": ["-vf", "fps=10,scale=480:-1:flags=lanczos", "-c:v", "gif"],
        }
        codecs = codec_map.get(target_format, ["-c:v", "libx264", "-c:a", "aac"])

        result = self._run_ffmpeg(["-i", str(p)] + codecs + ["-y", out])

        if result["success"] and Path(out).exists():
            size = Path(out).stat().st_size
            return {"output": out, "format": target_format, "size_mb": round(size / 1048576, 2)}
        return {"error": result.get("error", result.get("stderr", "unknown"))[:200]}

    def extract_subtitles(self, path: str, output: str = "") -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        out = output or str(self.data_dir / f"{p.stem}.srt")
        result = self._run_ffprobe([
            "-v", "error", "-select_streams", "s", "-show_entries", "stream=index,codec_name",
            "-of", "json", str(p)
        ])

        if result["success"] and result["output"]:
            try:
                data = json.loads(result["output"])
                streams = data.get("streams", [])
                if streams:
                    r2 = self._run_ffmpeg(["-i", str(p), "-map", "0:s:0", "-y", out])
                    if r2["success"]:
                        return {"output": out, "subtitle_streams": len(streams)}
                    return {"error": f"Extraction failed: {r2.get('stderr', '')[:200]}"}
                return {"error": "No subtitle streams found"}
            except json.JSONDecodeError:
                pass
        return {"error": "No subtitle information available"}

    def detect_scenes(self, path: str, threshold: float = 0.3) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        result = self._run_ffmpeg([
            "-i", str(p), "-vf", f"select='gt(scene,{threshold})',showinfo",
            "-f", "null", "-"
        ], timeout=300)

        scenes = []
        if result["success"] or result.get("stderr"):
            for line in (result.get("stderr", "") + result.get("stdout", "")).split("\n"):
                if "pts_time:" in line:
                    try:
                        t = float(line.split("pts_time:")[1].split()[0])
                        scenes.append(round(t, 2))
                    except (ValueError, IndexError):
                        pass

        return {"path": str(p), "scene_changes": len(scenes), "timestamps": scenes,
                "threshold": threshold, "durations": [round(scenes[i+1] - scenes[i], 2) for i in range(len(scenes)-1)]}

    def get_motion_analysis(self, path: str, sample_interval: float = 2.0) -> dict:
        p = Path(path)
        if not p.exists():
            return {"error": f"File not found: {path}"}

        duration = self._get_duration_sec(str(p))
        if duration <= 0:
            return {"error": "Cannot determine duration"}

        frames_dir = self.data_dir / "motion_tmp"
        frames_dir.mkdir(exist_ok=True)

        self._run_ffmpeg([
            "-i", str(p), "-vf", f"fps=1/{sample_interval}", "-q:v", "5",
            str(frames_dir / "f_%04d.jpg"), "-y"
        ], timeout=300)

        frames = sorted(frames_dir.glob("f_*.jpg"))
        motion_scores = []

        prev_data = None
        for f in frames[:30]:
            data = f.read_bytes()
            if prev_data:
                diff = sum(1 for a, b in zip(prev_data, data) if a != b) / max(len(prev_data), 1)
                motion_scores.append(round(diff, 4))
            prev_data = data

        for f in frames:
            f.unlink()
        frames_dir.rmdir()

        avg_motion = sum(motion_scores) / len(motion_scores) if motion_scores else 0
        max_motion = max(motion_scores) if motion_scores else 0

        if avg_motion < 0.05:
            activity = "static"
        elif avg_motion < 0.15:
            activity = "low_motion"
        elif avg_motion < 0.3:
            activity = "moderate_motion"
        else:
            activity = "high_motion"

        return {"path": str(p), "duration": duration, "frames_analyzed": len(motion_scores),
                "avg_motion": round(avg_motion, 4), "max_motion": round(max_motion, 4),
                "activity_level": activity, "scores": motion_scores[:20]}

    def batch_analyze(self, paths: list[str]) -> list[dict]:
        return [self.analyze_video(p) for p in paths]

    def compare_videos(self, path1: str, path2: str) -> dict:
        v1 = self.analyze_video(path1)
        v2 = self.analyze_video(path2)

        if "error" in v1 or "error" in v2:
            return {"error": "One or both files not found", "v1": v1, "v2": v2}

        comparison = {
            "video1": {"name": v1["name"], "duration": v1.get("duration_str", "?")},
            "video2": {"name": v2["name"], "duration": v2.get("duration_str", "?")},
        }

        for key in ("video", "audio"):
            if key in v1 and key in v2:
                comparison[key] = {
                    "same_codec": v1[key].get("codec") == v2[key].get("codec"),
                    "v1": v1[key], "v2": v2[key],
                }

        if "duration" in v1 and "duration" in v2:
            diff = abs(v1["duration"] - v2["duration"])
            comparison["duration_diff"] = f"{diff:.1f}s"

        return comparison

    def summarize(self, path: str) -> str:
        info = self.analyze_video(path)
        if "error" in info:
            return f"Error: {info['error']}"

        lines = [f"Video: {info['name']}", f"Size: {info['size_mb']} MB"]
        if "duration_str" in info:
            lines.append(f"Duration: {info['duration_str']}")
        if "quality" in info:
            lines.append(f"Quality: {info['quality']}")
        if "video" in info:
            v = info["video"]
            lines.append(f"Video: {v['codec']} {v['width']}x{v['height']} {v['fps']}fps")
        if "audio" in info:
            a = info["audio"]
            lines.append(f"Audio: {a['codec']} {a['sample_rate']}Hz {a['channels']}ch")
        return "\n".join(lines)
