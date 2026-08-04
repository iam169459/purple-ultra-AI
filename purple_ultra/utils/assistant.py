"""Personal assistant module - calendar, reminders, tasks, notes, habits."""

from __future__ import annotations

import json
import time
from pathlib import Path


class PersonalAssistant:
    def __init__(self, data_dir: str = "data"):
        self._dir = Path(data_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._tasks_file = self._dir / "tasks.json"
        self._reminders_file = self._dir / "reminders.json"
        self._habits_file = self._dir / "habits.json"
        self._tasks: list[dict] = []
        self._reminders: list[dict] = []
        self._habits: dict[str, list] = {}
        self._load()

    def _load(self):
        try:
            if self._tasks_file.exists():
                self._tasks = json.loads(self._tasks_file.read_text())
            if self._reminders_file.exists():
                self._reminders = json.loads(self._reminders_file.read_text())
            if self._habits_file.exists():
                self._habits = json.loads(self._habits_file.read_text())
        except Exception:
            pass

    def _save(self):
        try:
            self._tasks_file.write_text(json.dumps(self._tasks, indent=2))
            self._reminders_file.write_text(json.dumps(self._reminders, indent=2))
            self._habits_file.write_text(json.dumps(self._habits, indent=2))
        except Exception:
            pass

    def add_task(self, task: str, priority: int = 5, due: str = "") -> str:
        self._tasks.append({
            "task": task,
            "priority": priority,
            "due": due,
            "done": False,
            "created": time.time(),
        })
        self._save()
        return f"Task added: {task}"

    def complete_task(self, index: int) -> str:
        if 0 <= index < len(self._tasks):
            self._tasks[index]["done"] = True
            self._save()
            return f"Completed: {self._tasks[index]['task']}"
        return "Invalid task index"

    def list_tasks(self, include_done: bool = False) -> list[dict]:
        if include_done:
            return self._tasks
        return [t for t in self._tasks if not t.get("done")]

    def add_reminder(self, text: str, time_str: str = "") -> str:
        self._reminders.append({
            "text": text,
            "time": time_str,
            "active": True,
            "created": time.time(),
        })
        self._save()
        return f"Reminder set: {text}"

    def get_due_reminders(self) -> list[dict]:
        now = time.time()
        return [r for r in self._reminders if r.get("active")]

    def add_habit(self, habit: str, frequency: str = "daily") -> str:
        if habit not in self._habits:
            self._habits[habit] = []
        self._habits[habit].append({
            "frequency": frequency,
            "created": time.time(),
            "streak": 0,
        })
        self._save()
        return f"Habit tracked: {habit}"

    def get_habits(self) -> dict:
        return self._habits

    def get_summary(self) -> str:
        pending = len(self.list_tasks())
        reminders = len(self.get_due_reminders())
        habits = len(self._habits)
        return f"Tasks: {pending} pending | Reminders: {reminders} active | Habits: {habits} tracked"
