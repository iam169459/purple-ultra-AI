"""Advanced memory system with consolidation, replay, and dreaming."""

from __future__ import annotations

import json
import time
import random
import math
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from collections import deque


@dataclass
class MemoryTrace:
    content: str
    importance: float
    emotion: str
    timestamp: float
    access_count: int = 0
    last_accessed: float = 0
    associations: list[str] = field(default_factory=list)
    embedding: list[float] = field(default_factory=list)
    consolidated: bool = False


class HierarchicalMemory:
    def __init__(self, memory_dir: str = "memory/advanced"):
        self._dir = Path(memory_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._sensory: deque[MemoryTrace] = deque(maxlen=100)
        self._short_term: deque[MemoryTrace] = deque(maxlen=500)
        self._long_term: list[MemoryTrace] = []
        self._episodic: list[dict] = []
        self._semantic: dict[str, Any] = {}
        self._procedural: dict[str, list] = {}
        self._consolidation_threshold = 0.6
        self._load()

    def _load(self):
        try:
            lt_file = self._dir / "long_term.json"
            if lt_file.exists():
                data = json.loads(lt_file.read_text())
                for item in data:
                    self._long_term.append(MemoryTrace(**item))
            ep_file = self._dir / "episodic.json"
            if ep_file.exists():
                self._episodic = json.loads(ep_file.read_text())
            sem_file = self._dir / "semantic.json"
            if sem_file.exists():
                self._semantic = json.loads(sem_file.read_text())
        except Exception:
            pass

    def _save(self):
        try:
            lt_data = [
                {"content": m.content, "importance": m.importance, "emotion": m.emotion,
                 "timestamp": m.timestamp, "access_count": m.access_count,
                 "last_accessed": m.last_accessed, "associations": m.associations,
                 "embedding": m.embedding, "consolidated": m.consolidated}
                for m in self._long_term[-2000:]
            ]
            (self._dir / "long_term.json").write_text(json.dumps(lt_data, indent=2))
            (self._dir / "episodic.json").write_text(json.dumps(self._episodic[-1000:], indent=2))
            (self._dir / "semantic.json").write_text(json.dumps(self._semantic, indent=2))
        except Exception:
            pass

    def store(self, content: str, importance: float = 0.5, emotion: str = "neutral", embedding: list[float] = None) -> str:
        trace = MemoryTrace(
            content=content, importance=importance, emotion=emotion,
            timestamp=time.time(), last_accessed=time.time(),
            embedding=embedding or [],
        )
        self._sensory.append(trace)
        self._consolidate()
        return f"Stored in sensory memory (importance: {importance:.2f})"

    def _consolidate(self):
        for trace in list(self._sensory):
            if trace.importance >= self._consolidation_threshold:
                self._short_term.append(trace)
                self._sensory.remove(trace)
        for trace in list(self._short_term):
            if trace.importance >= 0.8 or trace.access_count > 3:
                trace.consolidated = True
                self._long_term.append(trace)
                self._short_term.remove(trace)
        if len(self._long_term) > 2000:
            self._long_term.sort(key=lambda x: x.importance, reverse=True)
            self._long_term = self._long_term[:2000]

    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        results = []
        query_lower = query.lower()
        for trace in self._long_term:
            score = 0
            words = set(query_lower.split())
            content_words = set(trace.content.lower().split())
            overlap = len(words & content_words)
            score += overlap * 0.3
            if trace.importance > 0.7:
                score += 0.2
            recency = time.time() - trace.last_accessed
            if recency < 3600:
                score += 0.3
            elif recency < 86400:
                score += 0.1
            if score > 0.1:
                results.append({
                    "content": trace.content,
                    "score": score,
                    "importance": trace.importance,
                    "emotion": trace.emotion,
                    "age_hours": (time.time() - trace.timestamp) / 3600,
                })
                trace.access_count += 1
                trace.last_accessed = time.time()
        results.sort(key=lambda x: -x["score"])
        return results[:top_k]

    def dream(self):
        """Memory consolidation during idle time - reorganize and strengthen memories."""
        if len(self._long_term) < 10:
            return
        sample_size = min(20, len(self._long_term))
        sample = random.sample(self._long_term, sample_size)
        for trace in sample:
            trace.importance *= 1.05
            trace.importance = min(trace.importance, 1.0)
            if random.random() < 0.1:
                trace.importance *= 0.95
        associations = self._find_associations()
        for trace in self._long_term[-50:]:
            for assoc in associations:
                if any(word in trace.content.lower() for word in assoc["words"]):
                    trace.associations.extend(assoc["trace_contents"][:3])
                    trace.associations = list(set(trace.associations))[:10]
        self._save()

    def _find_associations(self) -> list[dict]:
        associations = []
        word_traces: dict[str, list[str]] = {}
        for trace in self._long_term[-100:]:
            for word in trace.content.lower().split():
                if len(word) > 3:
                    if word not in word_traces:
                        word_traces[word] = []
                    word_traces[word].append(trace.content[:50])
        for word, contents in word_traces.items():
            if 2 <= len(contents) <= 10:
                associations.append({"words": [word], "trace_contents": contents})
        return associations[:20]

    def associate(self, content1: str, content2: str):
        for trace in self._long_term:
            if content1[:50] in trace.content:
                trace.associations.append(content2[:50])
            elif content2[:50] in trace.content:
                trace.associations.append(content1[:50])

    def store_episodic(self, event: str, context: dict = None):
        self._episodic.append({
            "event": event,
            "context": context or {},
            "timestamp": time.time(),
        })
        if len(self._episodic) > 1000:
            self._episodic = self._episodic[-1000:]

    def recall_episodes(self, query: str, limit: int = 5) -> list[dict]:
        results = []
        query_lower = query.lower()
        for ep in reversed(self._episodic):
            if any(word in ep["event"].lower() for word in query_lower.split()):
                results.append(ep)
                if len(results) >= limit:
                    break
        return results

    def store_semantic(self, key: str, value: Any):
        self._semantic[key] = {"value": value, "timestamp": time.time()}
        self._save()

    def recall_semantic(self, key: str) -> Any:
        entry = self._semantic.get(key)
        return entry["value"] if entry else None

    def store_procedural(self, skill: str, steps: list[str]):
        self._procedural[skill] = steps
        self._save()

    def recall_procedural(self, skill: str) -> list[str]:
        return self._procedural.get(skill, [])

    def get_stats(self) -> dict:
        return {
            "sensory": len(self._sensory),
            "short_term": len(self._short_term),
            "long_term": len(self._long_term),
            "episodic": len(self._episodic),
            "semantic": len(self._semantic),
            "procedural": len(self._procedural),
            "total": len(self._sensory) + len(self._short_term) + len(self._long_term),
        }

    def get_health(self) -> float:
        if not self._long_term:
            return 100.0
        avg_importance = sum(m.importance for m in self._long_term) / len(self._long_term)
        consolidation_rate = sum(1 for m in self._long_term if m.consolidated) / len(self._long_term)
        return (avg_importance * 50 + consolidation_rate * 50)


class MemoryReplay:
    def __init__(self, memory: HierarchicalMemory):
        self._memory = memory
        self._replay_count = 0

    def replay_recent(self, count: int = 10) -> list[dict]:
        recent = self._memory._long_term[-count:]
        results = []
        for trace in recent:
            results.append({
                "content": trace.content,
                "importance": trace.importance,
                "replayed": True,
            })
            trace.access_count += 1
            trace.last_accessed = time.time()
            trace.importance *= 1.02
        self._replay_count += 1
        return results

    def replay_emotional(self, emotion: str, count: int = 5) -> list[dict]:
        emotional = [m for m in self._memory._long_term if m.emotion == emotion]
        sample = random.sample(emotional, min(count, len(emotional)))
        results = []
        for trace in sample:
            results.append({
                "content": trace.content,
                "emotion": trace.emotion,
                "importance": trace.importance,
            })
            trace.access_count += 1
            trace.importance *= 1.03
        return results

    def replay_important(self, count: int = 5) -> list[dict]:
        important = sorted(self._memory._long_term, key=lambda x: -x.importance)[:count]
        results = []
        for trace in important:
            results.append({
                "content": trace.content,
                "importance": trace.importance,
            })
            trace.access_count += 1
        return results

    def get_stats(self) -> dict:
        return {"replay_count": self._replay_count}
