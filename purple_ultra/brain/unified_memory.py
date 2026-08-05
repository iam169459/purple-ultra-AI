"""Unified Memory System: Connects all memory subsystems.

Coordinates working memory, episodic memory, semantic memory, and knowledge graphs
across SelfLearningSystem, PurpleBrain, NeuralCore, and AdvancedMemory.
"""

from __future__ import annotations

import json
import time
import threading
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any
from collections import defaultdict, deque


@dataclass
class Memory:
    """A single memory entry."""
    content: str
    memory_type: str  # working, episodic, semantic, procedural
    importance: float = 0.5
    emotion: str = "neutral"
    tags: list[str] = field(default_factory=list)
    associations: list[str] = field(default_factory=list)
    access_count: int = 0
    decay_rate: float = 0.01
    created_at: float = field(default_factory=time.time)
    last_accessed: float = field(default_factory=time.time)
    source: str = "conversation"


class WorkingMemory:
    """Short-term working memory (last 10-20 items)."""

    __slots__ = ('_items', '_max_size')

    def __init__(self, max_size: int = 15):
        self._max_size = max_size
        self._items: deque[Memory] = deque(maxlen=max_size)

    def store(self, content: str, **kwargs) -> Memory:
        """Store in working memory, evicting oldest if full."""
        memory = Memory(content=content, memory_type="working", **kwargs)
        self._items.append(memory)
        return memory

    def recall_recent(self, n: int = 5) -> list[Memory]:
        """Recall recent memories."""
        return list(self._items)[-n:]

    def get_context(self) -> str:
        """Get working memory as context string."""
        return "\n".join(m.content[:200] for m in list(self._items)[-5:])

    def clear(self):
        """Clear working memory."""
        self._items.clear()


class EpisodicMemory:
    """Memory of specific events and experiences."""

    __slots__ = ('_episodes', '_path', '_lock')

    def __init__(self, memory_dir: str = "memory/episodic"):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._episodes: deque[dict] = deque(maxlen=500)
        self._load()

    def _load(self):
        ep_file = self._path / "episodes.json"
        if ep_file.exists():
            try:
                data = json.loads(ep_file.read_text())
                for ep in data[-500:]:
                    self._episodes.append(ep)
            except Exception:
                pass

    def save(self):
        with self._lock:
            (self._path / "episodes.json").write_text(
                json.dumps(list(self._episodes), separators=(',', ':'))
            )

    def store_episode(self, event: str, emotion: str = "neutral",
                      importance: float = 0.5, tags: list[str] | None = None):
        """Store an episodic memory."""
        with self._lock:
            episode = {
                "event": event,
                "emotion": emotion,
                "importance": importance,
                "tags": tags or [],
                "timestamp": time.time(),
            }
            self._episodes.append(episode)

    def recall_by_emotion(self, emotion: str, limit: int = 5) -> list[dict]:
        """Recall episodes matching an emotion."""
        with self._lock:
            matches = [e for e in self._episodes if e.get("emotion") == emotion]
            return sorted(matches, key=lambda x: x["importance"], reverse=True)[:limit]

    def recall_by_tag(self, tag: str, limit: int = 5) -> list[dict]:
        """Recall episodes matching a tag."""
        with self._lock:
            matches = [e for e in self._episodes if tag in e.get("tags", [])]
            return matches[-limit:]

    def get_recent(self, n: int = 5) -> list[dict]:
        """Get most recent episodes."""
        with self._lock:
            return list(self._episodes)[-n:]


class SemanticMemory:
    """Long-term semantic knowledge (facts, concepts, relationships)."""

    __slots__ = ('_concepts', '_relationships', '_path', '_lock')

    def __init__(self, memory_dir: str = "memory/semantic"):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._concepts: dict[str, dict] = {}
        self._relationships: list[dict] = []
        self._load()

    def _load(self):
        concepts_file = self._path / "concepts.json"
        rels_file = self._path / "relationships.json"
        if concepts_file.exists():
            try:
                self._concepts = json.loads(concepts_file.read_text())
            except Exception:
                pass
        if rels_file.exists():
            try:
                self._relationships = json.loads(rels_file.read_text())
            except Exception:
                pass

    def save(self):
        with self._lock:
            (self._path / "concepts.json").write_text(
                json.dumps(self._concepts, separators=(',', ':'))
            )
            (self._path / "relationships.json").write_text(
                json.dumps(self._relationships[-1000:], separators=(',', ':'))
            )

    def store_concept(self, name: str, definition: str,
                      attributes: dict | None = None, tags: list[str] | None = None):
        """Store a semantic concept."""
        with self._lock:
            self._concepts[name.lower()] = {
                "name": name,
                "definition": definition,
                "attributes": attributes or {},
                "tags": tags or [],
                "access_count": 0,
                "last_accessed": time.time(),
            }

    def store_relationship(self, subject: str, predicate: str, obj: str):
        """Store a relationship between concepts."""
        with self._lock:
            self._relationships.append({
                "subject": subject.lower(),
                "predicate": predicate.lower(),
                "object": obj.lower(),
                "timestamp": time.time(),
            })

    def recall_concept(self, name: str) -> dict | None:
        """Recall a concept by name."""
        with self._lock:
            concept = self._concepts.get(name.lower())
            if concept:
                concept["access_count"] += 1
                concept["last_accessed"] = time.time()
            return concept

    def find_related(self, concept: str) -> list[dict]:
        """Find concepts related to the given concept."""
        with self._lock:
            concept_lower = concept.lower()
            related = []
            for rel in self._relationships:
                if rel["subject"] == concept_lower:
                    related.append({"type": "object", "concept": rel["object"], "predicate": rel["predicate"]})
                elif rel["object"] == concept_lower:
                    related.append({"type": "subject", "concept": rel["subject"], "predicate": rel["predicate"]})
            return related[:10]

    def get_all_concepts(self) -> list[str]:
        """Get all stored concepts."""
        with self._lock:
            return list(self._concepts.keys())


class ProceduralMemory:
    """Memory of how to do things (procedures, skills)."""

    __slots__ = ('_procedures', '_path', '_lock')

    def __init__(self, memory_dir: str = "memory/procedural"):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._procedures: dict[str, dict] = {}
        self._load()

    def _load(self):
        proc_file = self._path / "procedures.json"
        if proc_file.exists():
            try:
                self._procedures = json.loads(proc_file.read_text())
            except Exception:
                pass

    def save(self):
        with self._lock:
            (self._path / "procedures.json").write_text(
                json.dumps(self._procedures, separators=(',', ':'))
            )

    def store_procedure(self, name: str, steps: list[str],
                        success_rate: float = 1.0):
        """Store a procedure."""
        with self._lock:
            self._procedures[name.lower()] = {
                "name": name,
                "steps": steps,
                "success_rate": success_rate,
                "usage_count": 0,
                "last_used": time.time(),
            }

    def recall_procedure(self, name: str) -> dict | None:
        """Recall a procedure by name."""
        with self._lock:
            proc = self._procedures.get(name.lower())
            if proc:
                proc["usage_count"] += 1
                proc["last_used"] = time.time()
            return proc

    def update_success(self, name: str, success: bool):
        """Update procedure success rate."""
        with self._lock:
            proc = self._procedures.get(name.lower())
            if proc:
                total = proc["usage_count"]
                if total > 0:
                    current = proc["success_rate"] * total
                    proc["success_rate"] = (current + (1.0 if success else 0.0)) / (total + 1)
                proc["usage_count"] += 1


class UnifiedMemoryManager:
    """Unified memory system coordinating all memory subsystems."""

    __slots__ = ('working', 'episodic', 'semantic', 'procedural',
                 '_path', '_lock', '_stats')

    def __init__(self, memory_dir: str = "memory/unified"):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._stats = {"total_stored": 0, "total_recalled": 0, "consolidations": 0}

        self.working = WorkingMemory(max_size=15)
        self.episodic = EpisodicMemory(str(self._path / "episodic"))
        self.semantic = SemanticMemory(str(self._path / "semantic"))
        self.procedural = ProceduralMemory(str(self._path / "procedural"))

    def store(self, content: str, memory_type: str = "working",
              emotion: str = "neutral", importance: float = 0.5,
              tags: list[str] | None = None, source: str = "conversation") -> Memory | dict | None:
        """Store a memory in the appropriate subsystem."""
        with self._lock:
            self._stats["total_stored"] += 1

            if memory_type == "working":
                return self.working.store(content, emotion=emotion,
                                          importance=importance, tags=tags or [],
                                          source=source)
            elif memory_type == "episodic":
                self.episodic.store_episode(content, emotion=emotion,
                                            importance=importance, tags=tags or [])
                return None
            elif memory_type == "semantic":
                self.semantic.store_concept(content, content, tags=tags)
                return None
            elif memory_type == "procedural":
                self.procedural.store_procedure(content, [content])
                return None
            return None

    def recall(self, query: str, memory_type: str | None = None) -> list:
        """Recall memories matching the query."""
        with self._lock:
            self._stats["total_recalled"] += 1
            results = []

            if memory_type is None or memory_type == "working":
                recent = self.working.recall_recent(5)
                results.extend(recent)

            if memory_type is None or memory_type == "episodic":
                episodes = self.episodic.get_recent(5)
                results.extend(episodes)

            if memory_type is None or memory_type == "semantic":
                concept = self.semantic.recall_concept(query)
                if concept:
                    results.append(concept)
                related = self.semantic.find_related(query)
                results.extend(related)

            return results

    def get_context_string(self) -> str:
        """Get a context string from all memory systems."""
        working_ctx = self.working.get_context()
        recent_episodes = self.episodic.get_recent(3)
        episode_ctx = "\n".join(e.get("event", "")[:100] for e in recent_episodes)

        parts = []
        if working_ctx:
            parts.append(f"Working Memory:\n{working_ctx}")
        if episode_ctx:
            parts.append(f"Recent Episodes:\n{episode_ctx}")

        return "\n\n".join(parts) if parts else "No context available."

    def consolidate(self):
        """Consolidate working memory into long-term memory."""
        with self._lock:
            self._stats["consolidations"] += 1
            working_items = self.working.recall_recent(15)

            for memory in working_items:
                if memory.importance > 0.7:
                    self.episodic.store_episode(
                        memory.content,
                        emotion=memory.emotion,
                        importance=memory.importance,
                        tags=memory.tags,
                    )

            self.working.clear()

    def save_all(self):
        """Persist all memory subsystems."""
        self.episodic.save()
        self.semantic.save()
        self.procedural.save()

    def get_stats(self) -> dict:
        """Get memory statistics."""
        with self._lock:
            return {
                "working_memory_size": len(self.working._items),
                "episodes_count": len(self.episodic._episodes),
                "concepts_count": len(self.semantic._concepts),
                "relationships_count": len(self.semantic._relationships),
                "procedures_count": len(self.procedural._procedures),
                "total_stored": self._stats["total_stored"],
                "total_recalled": self._stats["total_recalled"],
                "consolidations": self._stats["consolidations"],
            }
