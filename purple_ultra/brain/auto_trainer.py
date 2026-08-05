"""Auto-Trainer: Automatic learning from every conversation.

Learns facts, user preferences, response quality, and patterns from every interaction.
Persists all learned data across sessions.
"""

from __future__ import annotations

import json
import re
import hashlib
import threading
import time
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Any
from collections import defaultdict


# ═══════════════════════════════════════════════════════════════════════════
#  DYNAMIC KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class KnowledgeEntry:
    """A learned knowledge entry."""
    key: str
    value: str
    source: str = "conversation"
    confidence: float = 1.0
    access_count: int = 0
    last_accessed: float = 0.0
    created_at: float = field(default_factory=time.time)
    tags: list[str] = field(default_factory=list)


class DynamicKnowledgeBase:
    """Knowledge base that grows from conversations."""

    __slots__ = ('_entries', '_path', '_lock', '_stats')

    def __init__(self, memory_dir: str = "memory/knowledge"):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._entries: dict[str, KnowledgeEntry] = {}
        self._stats = {"total_learned": 0, "total_accessed": 0, "total_pruned": 0}
        self._load()

    def _load(self):
        """Load learned knowledge from disk."""
        knowledge_file = self._path / "learned.json"
        if knowledge_file.exists():
            try:
                data = json.loads(knowledge_file.read_text())
                for key, entry_data in data.get("entries", {}).items():
                    self._entries[key] = KnowledgeEntry(**entry_data)
                self._stats = data.get("stats", self._stats)
            except Exception:
                pass

    def save(self):
        """Persist learned knowledge to disk."""
        with self._lock:
            data = {
                "entries": {k: asdict(v) for k, v in self._entries.items()},
                "stats": self._stats,
            }
            (self._path / "learned.json").write_text(json.dumps(data, indent=2))

    def learn(self, key: str, value: str, source: str = "conversation",
              confidence: float = 1.0, tags: list[str] | None = None) -> bool:
        """Learn a new fact or update an existing one."""
        with self._lock:
            key_lower = key.lower().strip()

            if key_lower in self._entries:
                existing = self._entries[key_lower]
                if len(value) > len(existing.value):
                    existing.value = value
                    existing.confidence = max(existing.confidence, confidence)
                    existing.tags = list(set(existing.tags + (tags or [])))
                existing.access_count += 1
                return False

            self._entries[key_lower] = KnowledgeEntry(
                key=key_lower,
                value=value,
                source=source,
                confidence=confidence,
                tags=tags or [],
            )
            self._stats["total_learned"] += 1
            return True

    def recall(self, query: str) -> str | None:
        """Recall knowledge matching the query."""
        query_lower = query.lower()
        query_words = set(query_lower.split())

        best_match = None
        best_score = 0.0

        with self._lock:
            for key, entry in self._entries.items():
                score = 0.0

                if key in query_lower:
                    score = 2.0 + len(key) / 20
                elif query_lower in key:
                    score = 1.5
                else:
                    key_words = set(key.split())
                    overlap = len(query_words & key_words)
                    if overlap >= 2:
                        score = overlap / max(len(query_words), len(key_words))

                if score > best_score:
                    best_score = score
                    best_match = entry

            if best_match and best_score > 1.0:
                best_match.access_count += 1
                best_match.last_accessed = time.time()
                self._stats["total_accessed"] += 1
                return best_match.value

        return None

    def extract_facts(self, text: str) -> list[tuple[str, str]]:
        """Extract facts from text using pattern matching."""
        facts = []

        patterns = [
            (r'(?:my name is|i\'m called|i am)\s+(.+)', "user_name"),
            (r'(?:i work at|i work for|i\'m at)\s+(.+)', "user_workplace"),
            (r'(?:i like|i love|i enjoy|i prefer)\s+(.+)', "user_preference"),
            (r"(?:i hate|i dislike|i don't like)\s+(.+)", "user_dislike"),
            (r'(?:i live in|i\'m from|i\'m in)\s+(.+)', "user_location"),
            (r'(?:my favorite|favourite)\s+(?:color|colour|food|animal|movie|song|music)\s+(?:is|are)\s+(.+)', "user_favorite"),
            (r'(\w+)\s+(?:is|are)\s+(?:a|an|the)\s+(.+)', "definition"),
            (r'(?:remember that|note that|keep in mind)\s+(.+)', "explicit_fact"),
            (r'(?:i learned|i found out|i discovered)\s+(?:that\s+)?(.+)', "learned_fact"),
            (r'(?:the answer is|it is|that is)\s+(.+)', "answer"),
        ]

        for pattern, category in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                fact = match.group(1).strip().rstrip('.')
                if len(fact) > 3 and len(fact) < 200:
                    facts.append((fact, category))

        return facts

    def get_stats(self) -> dict:
        """Get knowledge base statistics."""
        with self._lock:
            return {
                "total_entries": len(self._entries),
                "total_learned": self._stats["total_learned"],
                "total_accessed": self._stats["total_accessed"],
                "sources": defaultdict(int, {
                    e.source: sum(1 for e in self._entries.values() if e.source == e.source)
                    for e in self._entries.values()
                }),
            }


# ═══════════════════════════════════════════════════════════════════════════
#  USER PREFERENCE TRACKER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class UserPreferences:
    """Tracked user preferences."""
    response_length: str = "moderate"  # brief, moderate, detailed
    technical_level: str = "intermediate"  # beginner, intermediate, expert
    style: str = "informative"  # informative, casual, formal, friendly
    topics_of_interest: list[str] = field(default_factory=list)
    topics_to_avoid: list[str] = field(default_factory=list)
    interaction_count: int = 0
    last_updated: float = 0.0


class UserPreferenceTracker:
    """Tracks user preferences from interactions."""

    __slots__ = ('_preferences', '_path', '_lock')

    def __init__(self, memory_dir: str = "memory/preferences"):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._preferences = UserPreferences()
        self._load()

    def _load(self):
        pref_file = self._path / "preferences.json"
        if pref_file.exists():
            try:
                data = json.loads(pref_file.read_text())
                for k, v in data.items():
                    if hasattr(self._preferences, k):
                        setattr(self._preferences, k, v)
            except Exception:
                pass

    def save(self):
        with self._lock:
            self._preferences.last_updated = time.time()
            (self._path / "preferences.json").write_text(
                json.dumps(asdict(self._preferences), indent=2)
            )

    def update_from_interaction(self, user_text: str, response: str,
                                 feedback: str | None = None):
        """Update preferences based on interaction."""
        with self._lock:
            self._preferences.interaction_count += 1

            # Learn response length preference
            if len(user_text.split()) < 6:
                self._preferences.response_length = "brief"
            elif len(user_text.split()) > 15:
                self._preferences.response_length = "detailed"

            # Learn technical level
            tech_words = {"api", "algorithm", "protocol", "architecture",
                          "implementation", "optimization", "deploy"}
            if any(w in user_text.lower() for w in tech_words):
                self._preferences.technical_level = "expert"
            elif any(w in user_text.lower() for w in {"how", "what is", "explain"}):
                self._preferences.technical_level = "beginner"

            # Learn style from feedback
            if feedback:
                if feedback in ("good", "great", "thanks", "perfect", "excellent"):
                    # Reinforce current style
                    pass
                elif feedback in ("bad", "wrong", "incorrect", "terrible"):
                    # Try different style
                    styles = ["informative", "casual", "formal", "friendly"]
                    idx = styles.index(self._preferences.style)
                    self._preferences.style = styles[(idx + 1) % len(styles)]

            # Track topics
            words = set(user_text.lower().split())
            stop_words = {"what", "is", "the", "how", "do", "does", "can",
                          "you", "tell", "me", "about", "why", "when", "where"}
            topic_words = words - stop_words
            for word in topic_words:
                if len(word) > 3 and word not in self._preferences.topics_of_interest:
                    self._preferences.topics_of_interest.append(word)
                    if len(self._preferences.topics_of_interest) > 50:
                        self._preferences.topics_of_interest.pop(0)

    def get_preferences(self) -> UserPreferences:
        with self._lock:
            return self._preferences


# ═══════════════════════════════════════════════════════════════════════════
#  RESPONSE QUALITY TRACKER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ResponseRecord:
    """Record of a response and its quality."""
    query: str
    response: str
    intent: str = "unknown"
    quality_score: float = 0.5
    user_feedback: str | None = None
    timestamp: float = field(default_factory=time.time)
    was_helpful: bool | None = None


class ResponseQualityTracker:
    """Tracks response quality to learn what works."""

    __slots__ = ('_records', '_patterns', '_path', '_lock', '_max_records')

    def __init__(self, memory_dir: str = "memory/responses", max_records: int = 2000):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._max_records = max_records
        self._records: list[ResponseRecord] = []
        self._patterns: dict[str, dict] = defaultdict(lambda: {"good": 0, "bad": 0, "total": 0})
        self._load()

    def _load(self):
        records_file = self._path / "records.json"
        if records_file.exists():
            try:
                data = json.loads(records_file.read_text())
                for r in data.get("records", [])[-self._max_records:]:
                    self._records.append(ResponseRecord(**r))
                self._patterns = defaultdict(
                    lambda: {"good": 0, "bad": 0, "total": 0},
                    data.get("patterns", {})
                )
            except Exception:
                pass

    def save(self):
        with self._lock:
            data = {
                "records": [asdict(r) for r in self._records[-self._max_records:]],
                "patterns": dict(self._patterns),
            }
            (self._path / "records.json").write_text(json.dumps(data, indent=2))

    def record_response(self, query: str, response: str, intent: str = "unknown"):
        """Record a response for quality tracking."""
        with self._lock:
            record = ResponseRecord(
                query=query,
                response=response,
                intent=intent,
            )
            self._records.append(record)
            if len(self._records) > self._max_records:
                self._records = self._records[-self._max_records:]

    def record_feedback(self, response: str, positive: bool):
        """Record user feedback on a response."""
        with self._lock:
            for record in reversed(self._records):
                if response[:100] in record.query or record.response[:100] in response:
                    record.was_helpful = positive
                    record.user_feedback = "positive" if positive else "negative"

                    intent = record.intent
                    if positive:
                        self._patterns[intent]["good"] += 1
                    else:
                        self._patterns[intent]["bad"] += 1
                    self._patterns[intent]["total"] += 1
                    break

    def get_quality_score(self, intent: str) -> float:
        """Get quality score for an intent based on history."""
        with self._lock:
            pattern = self._patterns.get(intent, {"good": 0, "bad": 0, "total": 0})
            if pattern["total"] == 0:
                return 0.5
            return pattern["good"] / pattern["total"]

    def get_best_responses(self, intent: str, limit: int = 5) -> list[str]:
        """Get best responses for an intent based on feedback."""
        with self._lock:
            scored = []
            for record in self._records:
                if record.intent == intent and record.was_helpful is not None:
                    score = 1.0 if record.was_helpful else 0.0
                    scored.append((score, record.response))
            scored.sort(key=lambda x: x[0], reverse=True)
            return [r for _, r in scored[:limit]]


# ═══════════════════════════════════════════════════════════════════════════
#  AUTO TRAINER (Main Orchestrator)
# ═══════════════════════════════════════════════════════════════════════════

class AutoTrainer:
    """Orchestrates automatic learning from every conversation."""

    __slots__ = ('_knowledge', '_preferences', '_quality', '_interaction_log',
                 '_path', '_lock', '_stats')

    def __init__(self, memory_dir: str = "memory/auto_trainer"):
        self._path = Path(memory_dir)
        self._path.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

        self._knowledge = DynamicKnowledgeBase(str(self._path / "knowledge"))
        self._preferences = UserPreferenceTracker(str(self._path / "preferences"))
        self._quality = ResponseQualityTracker(str(self._path / "responses"))

        self._interaction_log: list[dict] = []
        self._stats = {
            "total_interactions": 0,
            "facts_learned": 0,
            "patterns_found": 0,
            "feedback_received": 0,
        }
        self._load()

    def _load(self):
        stats_file = self._path / "stats.json"
        if stats_file.exists():
            try:
                self._stats.update(json.loads(stats_file.read_text()))
            except Exception:
                pass

    def save(self):
        """Persist all learned data."""
        with self._lock:
            (self._path / "stats.json").write_text(json.dumps(self._stats, indent=2))
        self._knowledge.save()
        self._preferences.save()
        self._quality.save()

    def learn_from_interaction(self, user_text: str, response: str,
                                intent: str = "unknown", feedback: str | None = None):
        """Main learning method - call after every interaction."""
        with self._lock:
            self._stats["total_interactions"] += 1

            # 1. Extract and store facts
            facts = self._knowledge.extract_facts(user_text)
            for fact_key, fact_category in facts:
                if self._knowledge.learn(fact_key, f"[{fact_category}] {fact_key}"):
                    self._stats["facts_learned"] += 1

            # 2. Learn from the response too
            response_facts = self._knowledge.extract_facts(response)
            for fact_key, fact_category in response_facts:
                self._knowledge.learn(fact_key, response, source="response")

            # 3. Update user preferences
            self._preferences.update_from_interaction(user_text, response, feedback)

            # 4. Record response quality
            self._quality.record_response(user_text, response, intent)

            # 5. Handle explicit feedback
            if feedback:
                self._stats["feedback_received"] += 1
                positive = feedback.lower() in (
                    "good", "great", "thanks", "thank you", "perfect",
                    "excellent", "helpful", "awesome", "nice", "correct",
                    "right", "yes", "exactly", "precisely",
                )
                self._quality.record_feedback(response, positive)

            # 6. Log interaction
            self._interaction_log.append({
                "user": user_text[:200],
                "response": response[:200],
                "intent": intent,
                "feedback": feedback,
                "timestamp": time.time(),
            })
            if len(self._interaction_log) > 500:
                self._interaction_log = self._interaction_log[-500:]

            # 7. Auto-save periodically
            if self._stats["total_interactions"] % 10 == 0:
                self.save()

    def get_learned_knowledge(self, query: str) -> str | None:
        """Retrieve learned knowledge for a query."""
        return self._knowledge.recall(query)

    def get_user_style(self) -> str:
        """Get current user style preference."""
        return self._preferences.get_preferences().style

    def get_quality_score(self, intent: str) -> float:
        """Get quality score for an intent."""
        return self._quality.get_quality_score(intent)

    def get_stats(self) -> dict:
        """Get comprehensive training statistics."""
        with self._lock:
            return {
                "total_interactions": self._stats["total_interactions"],
                "facts_learned": self._stats["facts_learned"],
                "feedback_received": self._stats["feedback_received"],
                "knowledge_entries": self._knowledge.get_stats()["total_entries"],
                "user_preferences": asdict(self._preferences.get_preferences()),
                "top_intents": dict(sorted(
                    self._quality._patterns.items(),
                    key=lambda x: x[1]["total"],
                    reverse=True
                )[:10]),
            }

    def reflect(self) -> str:
        """Generate a reflection on what has been learned."""
        stats = self.get_stats()
        prefs = self._preferences.get_preferences()

        reflection = f"Auto-Training Reflection:\n"
        reflection += f"- Total interactions: {stats['total_interactions']}\n"
        reflection += f"- Facts learned: {stats['facts_learned']}\n"
        reflection += f"- Knowledge entries: {stats['knowledge_entries']}\n"
        reflection += f"- User style: {prefs.style}\n"
        reflection += f"- Technical level: {prefs.technical_level}\n"
        reflection += f"- Response length: {prefs.response_length}\n"

        if prefs.topics_of_interest:
            reflection += f"- Top interests: {', '.join(prefs.topics_of_interest[-5:])}\n"

        return reflection
