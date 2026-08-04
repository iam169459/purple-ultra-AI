"""Neural anomaly detection for system monitoring."""

from __future__ import annotations

import json
import time
import statistics
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque
import numpy as np


@dataclass
class Anomaly:
    metric: str
    value: float
    expected: float
    deviation: float
    severity: str
    timestamp: float = field(default_factory=time.time)


class NeuralAnomalyDetector:
    def __init__(self, window_size: int = 100, threshold: float = 2.5):
        self._window_size = window_size
        self._threshold = threshold
        self._history: dict[str, deque] = {}
        self._anomalies: list[Anomaly] = []
        self._baselines: dict[str, dict] = {}

    def add_datapoint(self, metric: str, value: float):
        if metric not in self._history:
            self._history[metric] = deque(maxlen=self._window_size)
        self._history[metric].append(value)
        if len(self._history[metric]) > 20:
            self._update_baseline(metric)

    def _update_baseline(self, metric: str):
        values = list(self._history[metric])
        self._baselines[metric] = {
            "mean": statistics.mean(values),
            "std": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
            "median": statistics.median(values),
        }

    def detect(self, metric: str, value: float) -> Anomaly | None:
        self.add_datapoint(metric, value)
        if metric not in self._baselines:
            return None
        baseline = self._baselines[metric]
        if baseline["std"] == 0:
            deviation = abs(value - baseline["mean"])
        else:
            deviation = abs(value - baseline["mean"]) / baseline["std"]
        if deviation > self._threshold:
            severity = "critical" if deviation > self._threshold * 2 else "high" if deviation > self._threshold * 1.5 else "medium"
            anomaly = Anomaly(
                metric=metric,
                value=value,
                expected=baseline["mean"],
                deviation=deviation,
                severity=severity,
            )
            self._anomalies.append(anomaly)
            if len(self._anomalies) > 500:
                self._anomalies = self._anomalies[-500:]
            return anomaly
        return None

    def detect_batch(self, metrics: dict[str, float]) -> list[Anomaly]:
        anomalies = []
        for metric, value in metrics.items():
            anomaly = self.detect(metric, value)
            if anomaly:
                anomalies.append(anomaly)
        return anomalies

    def get_anomalies(self, count: int = 20) -> list[dict]:
        return [
            {"metric": a.metric, "value": a.value, "expected": a.expected,
             "deviation": a.deviation, "severity": a.severity, "timestamp": a.timestamp}
            for a in self._anomalies[-count:]
        ]

    def get_baseline(self, metric: str) -> dict:
        return self._baselines.get(metric, {})

    def get_health_score(self) -> float:
        if not self._anomalies:
            return 100.0
        recent = [a for a in self._anomalies if time.time() - a.timestamp < 3600]
        if not recent:
            return 100.0
        penalty = sum(10 if a.severity == "critical" else 5 if a.severity == "high" else 2 for a in recent)
        return max(0, 100 - penalty)

    def get_stats(self) -> dict:
        return {
            "metrics_tracked": len(self._history),
            "total_anomalies": len(self._anomalies),
            "health_score": self.get_health_score(),
            "threshold": self._threshold,
        }


class PatternDetector:
    def __init__(self, min_occurrences: int = 3):
        self._min_occurrences = min_occurrences
        self._patterns: dict[str, list] = {}

    def add_event(self, category: str, event: str):
        if category not in self._patterns:
            self._patterns[category] = []
        self._patterns[category].append({
            "event": event,
            "timestamp": time.time(),
        })
        if len(self._patterns[category]) > 1000:
            self._patterns[category] = self._patterns[category][-1000:]

    def detect_recurring(self, category: str) -> list[dict]:
        if category not in self._patterns:
            return []
        events = self._patterns[category]
        event_counts = {}
        for e in events:
            event_counts[e["event"]] = event_counts.get(e["event"], 0) + 1
        return [
            {"event": event, "count": count}
            for event, count in event_counts.items()
            if count >= self._min_occurrences
        ]

    def detect_sequence(self, category: str, sequence: list[str]) -> int:
        if category not in self._patterns:
            return 0
        events = [e["event"] for e in self._patterns[category]]
        count = 0
        seq_len = len(sequence)
        for i in range(len(events) - seq_len + 1):
            if events[i:i+seq_len] == sequence:
                count += 1
        return count

    def get_frequent(self, category: str, top_k: int = 10) -> list[dict]:
        recurring = self.detect_recurring(category)
        return sorted(recurring, key=lambda x: -x["count"])[:top_k]
