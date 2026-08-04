"""Health monitoring and analytics dashboard."""

from __future__ import annotations

import time
import json
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Metric:
    name: str
    value: Any
    unit: str = ""
    timestamp: float = field(default_factory=time.time)


@dataclass
class HealthCheck:
    name: str
    status: str
    message: str
    latency_ms: float = 0
    timestamp: float = field(default_factory=time.time)


class HealthMonitor:
    def __init__(self, data_dir: str = "data"):
        self._data_dir = Path(data_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._metrics_file = self._data_dir / "metrics.json"
        self._health_file = self._data_dir / "health.json"
        self._metrics: list[Metric] = []
        self._health_checks: dict[str, HealthCheck] = {}
        self._alerts: list[dict] = []
        self._alert_rules: list[dict] = []
        self._subscribers: list[callable] = []

    def record_metric(self, name: str, value: Any, unit: str = ""):
        metric = Metric(name=name, value=value, unit=unit)
        self._metrics.append(metric)
        if len(self._metrics) > 10000:
            self._metrics = self._metrics[-10000:]
        self._check_alerts(name, value)

    def add_alert_rule(self, metric_name: str, condition: str, threshold: float, message: str = ""):
        self._alert_rules.append({
            "metric": metric_name,
            "condition": condition,
            "threshold": threshold,
            "message": message,
        })

    def _check_alerts(self, name: str, value: Any):
        for rule in self._alert_rules:
            if rule["metric"] == name:
                triggered = False
                if rule["condition"] == "gt" and value > rule["threshold"]:
                    triggered = True
                elif rule["condition"] == "lt" and value < rule["threshold"]:
                    triggered = True
                elif rule["condition"] == "eq" and value == rule["threshold"]:
                    triggered = True
                if triggered:
                    alert = {
                        "metric": name,
                        "value": value,
                        "threshold": rule["threshold"],
                        "condition": rule["condition"],
                        "message": rule["message"] or f"{name} {rule['condition']} {rule['threshold']}",
                        "timestamp": time.time(),
                    }
                    self._alerts.append(alert)
                    for cb in self._subscribers:
                        try:
                            cb(alert)
                        except Exception:
                            pass

    def on_alert(self, callback: callable):
        self._subscribers.append(callback)

    def health_check(self, name: str, check_func) -> HealthCheck:
        start = time.time()
        try:
            result = check_func()
            latency = (time.time() - start) * 1000
            status = "healthy" if result else "unhealthy"
            hc = HealthCheck(name=name, status=status, message=str(result), latency_ms=latency)
        except Exception as e:
            latency = (time.time() - start) * 1000
            hc = HealthCheck(name=name, status="error", message=str(e), latency_ms=latency)
        self._health_checks[name] = hc
        return hc

    def get_metrics(self, name: str = None, count: int = 100) -> list[dict]:
        metrics = self._metrics
        if name:
            metrics = [m for m in metrics if m.name == name]
        return [{"name": m.name, "value": m.value, "unit": m.unit, "timestamp": m.timestamp} for m in metrics[-count:]]

    def get_health(self) -> dict:
        return {name: {"status": hc.status, "message": hc.message, "latency_ms": hc.latency_ms, "timestamp": hc.timestamp}
                for name, hc in self._health_checks.items()}

    def get_alerts(self, count: int = 20) -> list[dict]:
        return self._alerts[-count:]

    def get_dashboard(self) -> dict:
        return {
            "health": self.get_health(),
            "recent_metrics": self.get_metrics(count=50),
            "recent_alerts": self.get_alerts(count=10),
            "total_metrics": len(self._metrics),
            "total_alerts": len(self._alerts),
        }

    def save(self):
        try:
            self._metrics_file.write_text(json.dumps(
                [{"name": m.name, "value": m.value, "unit": m.unit, "timestamp": m.timestamp}
                 for m in self._metrics[-1000:]], indent=2
            ))
            self._health_file.write_text(json.dumps(self.get_health(), indent=2))
        except Exception:
            pass
