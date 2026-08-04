"""Background task scheduler with cron-like support."""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Callable, Any
from enum import Enum


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ScheduledTask:
    name: str
    func: Callable
    args: tuple = ()
    kwargs: dict = field(default_factory=dict)
    interval: float = 0
    cron: str = ""
    once: bool = False
    enabled: bool = True
    status: TaskStatus = TaskStatus.PENDING
    last_run: float = 0
    next_run: float = 0
    run_count: int = 0
    error_count: int = 0
    last_error: str = ""


class TaskScheduler:
    def __init__(self):
        self._tasks: dict[str, ScheduledTask] = {}
        self._running = False
        self._thread: threading.Thread | None = None
        self._lock = threading.Lock()
        self._on_complete: list[Callable] = []
        self._on_error: list[Callable] = []

    def schedule(
        self,
        name: str,
        func: Callable,
        interval: float = 0,
        cron: str = "",
        once: bool = False,
        args: tuple = (),
        kwargs: dict = None,
    ) -> str:
        task = ScheduledTask(
            name=name,
            func=func,
            args=args,
            kwargs=kwargs or {},
            interval=interval,
            cron=cron,
            once=once,
            next_run=time.time() + interval if interval else 0,
        )
        with self._lock:
            self._tasks[name] = task
        return f"Task '{name}' scheduled"

    def schedule_daily(self, name: str, func: Callable, hour: int = 9, minute: int = 0):
        return self.schedule(name, func, cron=f"{minute} {hour} * * *")

    def schedule_weekly(self, name: str, func: Callable, day: int = 0, hour: int = 9, minute: int = 0):
        return self.schedule(name, func, cron=f"{minute} {hour} * * {day}")

    def schedule_once(self, name: str, func: Callable, delay: float = 0):
        return self.schedule(name, func, interval=delay, once=True)

    def cancel(self, name: str) -> str:
        with self._lock:
            if name in self._tasks:
                self._tasks[name].enabled = False
                self._tasks[name].status = TaskStatus.CANCELLED
                return f"Task '{name}' cancelled"
        return f"Task '{name}' not found"

    def remove(self, name: str) -> str:
        with self._lock:
            if name in self._tasks:
                del self._tasks[name]
                return f"Task '{name}' removed"
        return f"Task '{name}' not found"

    def run_now(self, name: str) -> str:
        with self._lock:
            if name in self._tasks:
                task = self._tasks[name]
                self._execute_task(task)
                return f"Task '{name}' executed"
        return f"Task '{name}' not found"

    def _execute_task(self, task: ScheduledTask):
        task.status = TaskStatus.RUNNING
        task.last_run = time.time()
        try:
            task.func(*task.args, **task.kwargs)
            task.status = TaskStatus.COMPLETED
            task.run_count += 1
            for cb in self._on_complete:
                try:
                    cb(task)
                except Exception:
                    pass
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_count += 1
            task.last_error = str(e)
            for cb in self._on_error:
                try:
                    cb(task, e)
                except Exception:
                    pass

    def _should_run(self, task: ScheduledTask) -> bool:
        if not task.enabled:
            return False
        now = time.time()
        if task.interval > 0 and now >= task.next_run:
            return True
        if task.cron:
            return self._check_cron(task.cron, now)
        return False

    def _check_cron(self, cron_expr: str, timestamp: float) -> bool:
        import datetime
        try:
            parts = cron_expr.split()
            if len(parts) != 5:
                return False
            dt = datetime.datetime.fromtimestamp(timestamp)
            minute, hour, day, month, dow = parts
            if minute != "*" and dt.minute != int(minute):
                return False
            if hour != "*" and dt.hour != int(hour):
                return False
            if day != "*" and dt.day != int(day):
                return False
            if month != "*" and dt.month != int(month):
                return False
            if dow != "*" and dt.weekday() != int(dow):
                return False
            return True
        except Exception:
            return False

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            with self._lock:
                for task in self._tasks.values():
                    if self._should_run(task):
                        self._execute_task(task)
                        if task.once:
                            task.enabled = False
                        else:
                            task.next_run = time.time() + task.interval
            time.sleep(1)

    def on_complete(self, callback: Callable):
        self._on_complete.append(callback)

    def on_error(self, callback: Callable):
        self._on_error.append(callback)

    def list_tasks(self) -> list[dict]:
        return [
            {
                "name": t.name,
                "status": t.status.value,
                "interval": t.interval,
                "cron": t.cron,
                "once": t.once,
                "enabled": t.enabled,
                "run_count": t.run_count,
                "error_count": t.error_count,
                "last_run": t.last_run,
                "next_run": t.next_run,
            }
            for t in self._tasks.values()
        ]

    def get_status(self) -> dict:
        tasks = list(self._tasks.values())
        return {
            "running": self._running,
            "total": len(tasks),
            "enabled": sum(1 for t in tasks if t.enabled),
            "running_now": sum(1 for t in tasks if t.status == TaskStatus.RUNNING),
            "completed": sum(1 for t in tasks if t.status == TaskStatus.COMPLETED),
            "failed": sum(1 for t in tasks if t.status == TaskStatus.FAILED),
        }
