"""Advanced streaming and real-time processing."""

from __future__ import annotations

import time
import threading
from dataclasses import dataclass, field
from typing import Any, Callable
from collections import deque
from enum import Enum


class StreamState(Enum):
    IDLE = "idle"
    STREAMING = "streaming"
    PAUSED = "paused"
    ERROR = "error"


@dataclass
class StreamEvent:
    event_type: str
    data: Any
    timestamp: float = field(default_factory=time.time)
    event_id: str = ""


class DataStream:
    def __init__(self, name: str, buffer_size: int = 1000):
        self.name = name
        self._buffer: deque = deque(maxlen=buffer_size)
        self._state = StreamState.IDLE
        self._subscribers: list[Callable] = []
        self._processors: list[Callable] = []
        self._metrics = {"events_processed": 0, "errors": 0, "avg_latency": 0}
        self._lock = threading.Lock()

    def publish(self, event: StreamEvent):
        with self._lock:
            self._buffer.append(event)
            self._metrics["events_processed"] += 1
        for subscriber in self._subscribers:
            try:
                subscriber(event)
            except Exception:
                self._metrics["errors"] += 1

    def subscribe(self, callback: Callable):
        self._subscribers.append(callback)

    def add_processor(self, processor: Callable):
        self._processors.append(processor)

    def process_buffer(self) -> list[Any]:
        results = []
        while self._buffer:
            event = self._buffer.popleft()
            for processor in self._processors:
                try:
                    result = processor(event)
                    if result is not None:
                        results.append(result)
                except Exception:
                    self._metrics["errors"] += 1
        return results

    def get_state(self) -> StreamState:
        return self._state

    def get_metrics(self) -> dict:
        return dict(self._metrics)

    def clear(self):
        self._buffer.clear()


class StreamProcessor:
    def __init__(self):
        self._streams: dict[str, DataStream] = {}
        self._pipeline: list[Callable] = []
        self._results: deque = deque(maxlen=1000)
        self._running = False

    def create_stream(self, name: str, buffer_size: int = 1000) -> DataStream:
        stream = DataStream(name, buffer_size)
        self._streams[name] = stream
        return stream

    def get_stream(self, name: str) -> DataStream | None:
        return self._streams.get(name)

    def add_to_pipeline(self, processor: Callable):
        self._pipeline.append(processor)

    def process_event(self, stream_name: str, event: StreamEvent) -> Any:
        stream = self._streams.get(stream_name)
        if not stream:
            return None
        result = event
        for processor in self._pipeline:
            try:
                result = processor(result)
                if result is None:
                    return None
            except Exception:
                return None
        self._results.append(result)
        return result

    def start_continuous(self):
        self._running = True
        threading.Thread(target=self._continuous_loop, daemon=True).start()

    def stop_continuous(self):
        self._running = False

    def _continuous_loop(self):
        while self._running:
            for stream in self._streams.values():
                stream.process_buffer()
            time.sleep(0.01)

    def get_results(self, count: int = 10) -> list[Any]:
        return list(self._results)[-count:]

    def get_status(self) -> dict:
        return {
            "streams": len(self._streams),
            "pipeline_stages": len(self._pipeline),
            "results_buffered": len(self._results),
            "running": self._running,
        }


class WindowAggregator:
    def __init__(self, window_size: float = 60):
        self._window_size = window_size
        self._windows: dict[str, deque] = {}

    def add(self, key: str, value: float, timestamp: float = None):
        timestamp = timestamp or time.time()
        if key not in self._windows:
            self._windows[key] = deque()
        self._windows[key].append((timestamp, value))
        self._cleanup_window(key, timestamp)

    def _cleanup_window(self, key: str, current_time: float):
        window = self._windows.get(key, deque())
        while window and current_time - window[0][0] > self._window_size:
            window.popleft()

    def get_stats(self, key: str) -> dict:
        window = self._windows.get(key, deque())
        if not window:
            return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0}
        values = [v for _, v in window]
        return {
            "count": len(values),
            "sum": sum(values),
            "avg": sum(values) / len(values),
            "min": min(values),
            "max": max(values),
        }

    def get_all_stats(self) -> dict:
        return {key: self.get_stats(key) for key in self._windows}


class RateLimiter:
    def __init__(self, max_rate: int = 100, window: float = 1.0):
        self._max_rate = max_rate
        self._window = window
        self._timestamps: deque = deque()
        self._blocked = 0

    def allow(self) -> bool:
        now = time.time()
        while self._timestamps and now - self._timestamps[0] > self._window:
            self._timestamps.popleft()
        if len(self._timestamps) < self._max_rate:
            self._timestamps.append(now)
            return True
        self._blocked += 1
        return False

    def get_stats(self) -> dict:
        return {
            "current_rate": len(self._timestamps),
            "max_rate": self._max_rate,
            "blocked": self._blocked,
        }
