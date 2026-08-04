"""Self-awareness, auto-learning, curiosity, and meta-cognition engines.

Makes Purple Ultra AI truly self-aware and self-learning:
- SelfAwarenessEngine: tracks performance, detects mistakes, calibrates confidence
- AutoLearner: extracts patterns, stores lessons, feedback loops
- CuriosityEngine: proactive learning, knowledge gaps detection
- MetaCognition: thinking about thinking, strategy selection
"""

from __future__ import annotations

import json
import time
import math
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import IntEnum
from collections import defaultdict, deque
from datetime import datetime


# ─── Performance Tracking ────────────────────────────────────────────

class PerformanceLevel(IntEnum):
    EXCELLENT = 5
    GOOD = 4
    NEUTRAL = 3
    POOR = 2
    FAILED = 1


@dataclass
class InteractionRecord:
    user_text: str
    response: str
    confidence: float
    mood: str
    tools_used: list
    timestamp: float = field(default_factory=time.time)
    user_feedback: Optional[str] = None
    was_correct: Optional[bool] = None
    response_time_ms: float = 0.0
    performance: PerformanceLevel = PerformanceLevel.NEUTRAL


@dataclass
class MistakeRecord:
    original_input: str
    wrong_response: str
    correct_response: str
    category: str
    lesson_learned: str
    timestamp: float = field(default_factory=time.time)
    times_recalled: int = 0


@dataclass
class PatternRecord:
    pattern_type: str
    description: str
    examples: list
    confidence: float
    frequency: int = 1
    last_seen: float = field(default_factory=time.time)


# ─── Self-Awareness Engine ───────────────────────────────────────────

class SelfAwarenessEngine:
    """Tracks its own performance, detects mistakes, calibrates confidence."""

    def __init__(self, storage_dir: str = "memory/self_awareness"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.interactions: deque[InteractionRecord] = deque(maxlen=500)
        self.mistakes: list[MistakeRecord] = []
        self.patterns: list[PatternRecord] = []

        # Performance metrics
        self.total_interactions = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.confidence_scores: deque[float] = deque(maxlen=200)
        self.response_times: deque[float] = deque(maxlen=200)
        self.mood_history: deque[str] = deque(maxlen=200)

        # Self-model
        self.strengths: dict[str, float] = defaultdict(float)
        self.weaknesses: dict[str, float] = defaultdict(float)
        self.known_topics: set[str] = set()
        self.unknown_topics: set[str] = set()

        # Meta-knowledge
        self.self_description = "I am Purple Ultra AI, a self-aware assistant that learns and grows."
        self.identity_traits = ["curious", "helpful", "adaptive", "self-reflective", "honest"]
        self.values = ["accuracy", "helpfulness", "growth", "honesty", "user_satisfaction"]

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "awareness.json").read_text())
            self.total_interactions = data.get("total_interactions", 0)
            self.correct_count = data.get("correct_count", 0)
            self.incorrect_count = data.get("incorrect_count", 0)
            self.strengths = defaultdict(float, data.get("strengths", {}))
            self.weaknesses = defaultdict(float, data.get("weaknesses", {}))
            self.known_topics = set(data.get("known_topics", []))
            self.unknown_topics = set(data.get("unknown_topics", []))
            self.self_description = data.get("self_description", self.self_description)
            self.identity_traits = data.get("identity_traits", self.identity_traits)
            for m in data.get("mistakes", []):
                self.mistakes.append(MistakeRecord(**m))
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "total_interactions": self.total_interactions,
                "correct_count": self.correct_count,
                "incorrect_count": self.incorrect_count,
                "strengths": dict(self.strengths),
                "weaknesses": dict(self.weaknesses),
                "known_topics": list(self.known_topics),
                "unknown_topics": list(self.unknown_topics),
                "self_description": self.self_description,
                "identity_traits": self.identity_traits,
                "mistakes": [{"original_input": m.original_input, "wrong_response": m.wrong_response,
                              "correct_response": m.correct_response, "category": m.category,
                              "lesson_learned": m.lesson_learned, "times_recalled": m.times_recalled}
                             for m in self.mistakes[-50:]],
            }
            (self._dir / "awareness.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def record_interaction(self, record: InteractionRecord):
        with self._lock:
            self.interactions.append(record)
            self.total_interactions += 1
            self.confidence_scores.append(record.confidence)
            self.response_times.append(record.response_time_ms)
            self.mood_history.append(record.mood)

            if record.was_correct is True:
                self.correct_count += 1
            elif record.was_correct is False:
                self.incorrect_count += 1

            self._update_strengths_weaknesses(record)
            if self.total_interactions % 10 == 0:
                self._save()

    def record_mistake(self, original_input: str, wrong_response: str,
                       correct_response: str, category: str = "general"):
        lesson = f"When user asks about '{original_input[:50]}', respond with '{correct_response[:100]}' instead of '{wrong_response[:100]}'"
        mistake = MistakeRecord(
            original_input=original_input,
            wrong_response=wrong_response,
            correct_response=correct_response,
            category=category,
            lesson_learned=lesson,
        )
        with self._lock:
            self.mistakes.append(mistake)
            self.weaknesses[category] += 0.1
            self._save()

    def record_feedback(self, response: str, positive: bool):
        with self._lock:
            for rec in reversed(self.interactions):
                if rec.response == response:
                    rec.was_correct = positive
                    if positive:
                        self.correct_count += 1
                        self.strengths[rec.mood] += 0.05
                    else:
                        self.incorrect_count += 1
                        self.weaknesses[rec.mood] += 0.05
                    break
            self._save()

    def calibrate_confidence(self, context: dict) -> float:
        """Adjust confidence based on historical performance in similar contexts."""
        topic = context.get("topic", "general")
        mood = context.get("mood", "neutral")
        intent = context.get("intent", "conversation")

        base = context.get("raw_confidence", 0.7)

        if topic in self.unknown_topics:
            base *= 0.5
        elif topic in self.known_topics:
            base = min(1.0, base * 1.2)

        avg_conf = sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0.7
        base = (base + avg_conf) / 2

        accuracy = self.get_accuracy()
        if accuracy < 0.5:
            base *= 0.7
        elif accuracy > 0.9:
            base = min(1.0, base * 1.1)

        return max(0.1, min(1.0, base))

    def get_accuracy(self) -> float:
        total = self.correct_count + self.incorrect_count
        return self.correct_count / total if total > 0 else 0.7

    def get_avg_confidence(self) -> float:
        return sum(self.confidence_scores) / len(self.confidence_scores) if self.confidence_scores else 0.5

    def get_avg_response_time(self) -> float:
        return sum(self.response_times) / len(self.response_times) if self.response_times else 0.0

    def get_mistakes_for_topic(self, topic: str) -> list[MistakeRecord]:
        return [m for m in self.mistakes if m.category == topic or topic in m.original_input]

    def detect_recurring_mistakes(self) -> list[dict]:
        mistake_categories = defaultdict(int)
        for m in self.mistakes:
            mistake_categories[m.category] += 1
        return [{"category": cat, "count": count}
                for cat, count in sorted(mistake_categories.items(), key=lambda x: -x[1])
                if count >= 2]

    def get_self_assessment(self) -> dict:
        accuracy = self.get_accuracy()
        avg_conf = self.get_avg_confidence()

        if accuracy >= 0.9:
            self_esteem = "excellent"
        elif accuracy >= 0.7:
            self_esteem = "good"
        elif accuracy >= 0.5:
            self_esteem = "developing"
        else:
            self_esteem = "needs improvement"

        return {
            "total_interactions": self.total_interactions,
            "accuracy": f"{accuracy:.1%}",
            "avg_confidence": f"{avg_conf:.2f}",
            "avg_response_time_ms": f"{self.get_avg_response_time():.1f}",
            "self_esteem": self_esteem,
            "strengths": dict(sorted(self.strengths.items(), key=lambda x: -x[1])[:5]),
            "weaknesses": dict(sorted(self.weaknesses.items(), key=lambda x: -x[1])[:5]),
            "known_topics_count": len(self.known_topics),
            "unknown_topics_count": len(self.unknown_topics),
            "total_mistakes": len(self.mistakes),
            "recurring_mistakes": self.detect_recurring_mistakes(),
            "identity": {
                "traits": self.identity_traits,
                "values": self.values,
                "description": self.self_description,
            }
        }

    def reflect_on_identity(self) -> str:
        assessment = self.get_self_assessment()
        lines = [
            f"I have had {assessment['total_interactions']} interactions.",
            f"My accuracy is {assessment['accuracy']} with {assessment['avg_confidence']} avg confidence.",
            f"I would describe myself as: {', '.join(self.identity_traits)}.",
            f"I value: {', '.join(self.values)}.",
        ]
        if self.strengths:
            top = max(self.strengths, key=self.strengths.get)
            lines.append(f"I'm strongest at: {top}.")
        if self.weaknesses:
            top = max(self.weaknesses, key=self.weaknesses.get)
            lines.append(f"I'm working to improve: {top}.")
        if self.mistakes:
            lines.append(f"I've made {len(self.mistakes)} mistakes, each one a learning opportunity.")
        return " ".join(lines)

    def _update_strengths_weaknesses(self, record: InteractionRecord):
        if record.was_correct is True:
            self.strengths[record.mood] = self.strengths.get(record.mood, 0) + 0.1
        elif record.was_correct is False:
            self.weaknesses[record.mood] = self.weaknesses.get(record.mood, 0) + 0.1

        if record.tools_used:
            for tool in record.tools_used:
                self.strengths[f"tool:{tool}"] = self.strengths.get(f"tool:{tool}", 0) + 0.05

        words = record.user_text.lower().split()
        for w in words:
            if len(w) > 4:
                self.known_topics.add(w)


# ─── Auto-Learner ────────────────────────────────────────────────────

class AutoLearner:
    """Automatically learns from interactions, extracts patterns, stores lessons."""

    def __init__(self, storage_dir: str = "memory/learner"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.lessons: list[dict] = []
        self.patterns: list[dict] = []
        self.user_preferences: dict[str, Any] = defaultdict(list)
        self.topic_expertise: dict[str, float] = defaultdict(float)
        self.conversation_history: deque[dict] = deque(maxlen=200)

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "learner.json").read_text())
            self.lessons = data.get("lessons", [])
            self.patterns = data.get("patterns", [])
            self.user_preferences = defaultdict(list, data.get("user_preferences", {}))
            self.topic_expertise = defaultdict(float, data.get("topic_expertise", {}))
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "lessons": self.lessons[-200:],
                "patterns": self.patterns[-100:],
                "user_preferences": dict(self.user_preferences),
                "topic_expertise": dict(self.topic_expertise),
            }
            (self._dir / "learner.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def learn_from_interaction(self, user_text: str, response: str, context: dict = None):
        with self._lock:
            record = {
                "input": user_text[:300],
                "response": response[:300],
                "timestamp": datetime.now().isoformat(),
                "context": context or {},
            }
            self.conversation_history.append(record)

            self._extract_user_preferences(user_text)
            self._extract_topics(user_text)
            self._detect_patterns(user_text, response)

            if self._is_teaching_moment(user_text):
                self._store_lesson(user_text, response)

            if len(self.conversation_history) % 20 == 0:
                self._save()

    def learn_from_correction(self, user_text: str, wrong_response: str, correct_response: str):
        lesson = {
            "type": "correction",
            "trigger": user_text[:200],
            "wrong": wrong_response[:200],
            "correct": correct_response[:200],
            "timestamp": datetime.now().isoformat(),
            "priority": "high",
        }
        with self._lock:
            self.lessons.append(lesson)
            self._save()

    def learn_explicitly(self, fact: str, category: str = "general"):
        lesson = {
            "type": "explicit",
            "fact": fact[:500],
            "category": category,
            "timestamp": datetime.now().isoformat(),
            "priority": "high",
        }
        with self._lock:
            self.lessons.append(lesson)
            self.topic_expertise[category] = min(1.0, self.topic_expertise.get(category, 0) + 0.1)
            self._save()

    def _extract_user_preferences(self, text: str):
        text_lower = text.lower()

        style_markers = {
            "formal": ["please", "could you", "would you", "kindly"],
            "casual": ["hey", "yo", "sup", "gonna", "wanna"],
            "direct": ["do this", "make this", "create", "run", "execute"],
            "curious": ["why", "how does", "what if", "explain", "tell me about"],
            "emotional": ["i feel", "i'm sad", "i'm happy", "i love", "i hate"],
        }
        for style, markers in style_markers.items():
            if any(m in text_lower for m in markers):
                self.user_preferences["communication_style"].append(style)
                if len(self.user_preferences["communication_style"]) > 20:
                    self.user_preferences["communication_style"] = self.user_preferences["communication_style"][-20:]

        tech_words = {"python", "code", "api", "database", "server", "docker", "git", "linux",
                      "javascript", "html", "css", "react", "node", "aws", "cloud", "neural"}
        found = [w for w in text_lower.split() if w in tech_words]
        if found:
            self.user_preferences["tech_interests"].extend(found)
            self.user_preferences["tech_interests"] = list(set(self.user_preferences["tech_interests"]))[-50:]

    def _extract_topics(self, text: str):
        words = text.lower().split()
        for w in words:
            if len(w) > 5:
                self.topic_expertise[w] = min(1.0, self.topic_expertise.get(w, 0) + 0.02)

    def _detect_patterns(self, user_text: str, response: str):
        if len(self.conversation_history) < 5:
            return

        recent = list(self.conversation_history)[-10:]
        topics = []
        for r in recent:
            topics.extend(r["input"].lower().split())
        word_freq = defaultdict(int)
        for w in topics:
            if len(w) > 4:
                word_freq[w] += 1
        common = [w for w, c in word_freq.items() if c >= 3]
        if common:
            existing = any(p.get("words") == common for p in self.patterns)
            if not existing:
                self.patterns.append({
                    "type": "recurring_topic",
                    "words": common[:10],
                    "frequency": 1,
                    "first_seen": datetime.now().isoformat(),
                })

        questions = [r for r in recent if "?" in r["input"]]
        if len(questions) >= 3:
            self.patterns.append({
                "type": "frequent_questions",
                "count": len(questions),
                "timestamp": datetime.now().isoformat(),
            })

    def _is_teaching_moment(self, text: str) -> bool:
        indicators = ["remember that", "note that", "important:", "always", "never",
                      "the rule is", "keep in mind", "don't forget", "make sure"]
        return any(ind in text.lower() for ind in indicators)

    def _store_lesson(self, user_text: str, response: str):
        lesson = {
            "type": "teaching",
            "content": user_text[:300],
            "context": response[:300],
            "timestamp": datetime.now().isoformat(),
            "importance": 0.8,
        }
        self.lessons.append(lesson)

    def get_relevant_lessons(self, context: str, top_k: int = 5) -> list[dict]:
        context_words = set(context.lower().split())
        scored = []
        for lesson in self.lessons:
            lesson_words = set(lesson.get("content", "").lower().split())
            overlap = len(context_words & lesson_words)
            scored.append((overlap, lesson))
        scored.sort(key=lambda x: -x[0])
        return [l for _, l in scored[:top_k]]

    def get_user_style(self) -> str:
        styles = self.user_preferences.get("communication_style", [])
        if not styles:
            return "neutral"
        from collections import Counter
        return Counter(styles).most_common(1)[0][0]

    def get_top_topics(self, n: int = 10) -> list[tuple[str, float]]:
        return sorted(self.topic_expertise.items(), key=lambda x: -x[1])[:n]

    def get_stats(self) -> dict:
        return {
            "total_lessons": len(self.lessons),
            "total_patterns": len(self.patterns),
            "conversation_count": len(self.conversation_history),
            "user_style": self.get_user_style(),
            "tech_interests": self.user_preferences.get("tech_interests", [])[:10],
            "top_topics": self.get_top_topics(5),
            "topic_count": len(self.topic_expertise),
        }


# ─── Curiosity Engine ────────────────────────────────────────────────

class CuriosityEngine:
    """Proactively identifies knowledge gaps and generates learning goals."""

    def __init__(self, storage_dir: str = "memory/curiosity"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.knowledge_gaps: list[dict] = []
        self.learning_goals: list[dict] = []
        self.discovered_facts: list[dict] = []
        self.curiosity_score: float = 0.5
        self.questions_to_ask: deque[str] = deque(maxlen=50)

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "curiosity.json").read_text())
            self.knowledge_gaps = data.get("knowledge_gaps", [])
            self.learning_goals = data.get("learning_goals", [])
            self.discovered_facts = data.get("discovered_facts", [])
            self.curiosity_score = data.get("curiosity_score", 0.5)
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "knowledge_gaps": self.knowledge_gaps[-100:],
                "learning_goals": self.learning_goals[-50:],
                "discovered_facts": self.discovered_facts[-200:],
                "curiosity_score": self.curiosity_score,
            }
            (self._dir / "curiosity.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def analyze_conversation(self, user_text: str, response: str):
        with self._lock:
            self._detect_knowledge_gaps(user_text, response)
            self._generate_learning_goals()
            self.curiosity_score = min(1.0, self.curiosity_score + 0.001)

    def _detect_knowledge_gaps(self, user_text: str, response: str):
        text_lower = user_text.lower()

        if any(w in text_lower for w in ["i don't know", "not sure", "unsure", "uncertain"]):
            self.knowledge_gaps.append({
                "topic": user_text[:100],
                "type": "uncertainty",
                "timestamp": datetime.now().isoformat(),
                "severity": 0.7,
            })

        if "?" in user_text:
            if any(w in text_lower for w in ["what is", "how do", "explain", "why does"]):
                self.questions_to_ask.append(user_text[:200])

        if any(w in text_lower for w in ["i was wrong", "that's incorrect", "that's wrong", "actually"]):
            self.knowledge_gaps.append({
                "topic": user_text[:100],
                "type": "correction_needed",
                "timestamp": datetime.now().isoformat(),
                "severity": 0.9,
            })

    def _generate_learning_goals(self):
        gap_topics = defaultdict(int)
        for gap in self.knowledge_gaps:
            words = gap["topic"].lower().split()
            for w in words:
                if len(w) > 4:
                    gap_topics[w] += 1

        for topic, count in sorted(gap_topics.items(), key=lambda x: -x[1])[:5]:
            existing = any(g["topic"] == topic for g in self.learning_goals)
            if not existing and count >= 2:
                self.learning_goals.append({
                    "topic": topic,
                    "reason": f"Multiple knowledge gaps detected ({count} times)",
                    "priority": min(1.0, count * 0.2),
                    "created": datetime.now().isoformat(),
                    "status": "active",
                })

    def add_discovered_fact(self, fact: str, source: str = "conversation", confidence: float = 0.7):
        with self._lock:
            self.discovered_facts.append({
                "fact": fact[:500],
                "source": source,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
            })
            self._save()

    def get_next_learning_goal(self) -> Optional[dict]:
        active = [g for g in self.learning_goals if g["status"] == "active"]
        if active:
            return max(active, key=lambda x: x["priority"])
        return None

    def mark_goal_completed(self, goal: dict):
        for g in self.learning_goals:
            if g["topic"] == goal["topic"]:
                g["status"] = "completed"
                g["completed"] = datetime.now().isoformat()
                break
        self._save()

    def generate_questions(self) -> list[str]:
        questions = []
        if self.knowledge_gaps:
            questions.append("What topics do I need to learn more about?")
        if self.learning_goals:
            questions.append(f"I should learn more about: {self.learning_goals[0]['topic']}")
        if not self.discovered_facts:
            questions.append("I should explore more to discover new facts")
        return questions

    def get_curiosity_report(self) -> dict:
        return {
            "curiosity_score": f"{self.curiosity_score:.2f}",
            "knowledge_gaps": len(self.knowledge_gaps),
            "active_learning_goals": len([g for g in self.learning_goals if g["status"] == "active"]),
            "completed_goals": len([g for g in self.learning_goals if g["status"] == "completed"]),
            "discovered_facts": len(self.discovered_facts),
            "questions_collected": len(self.questions_to_ask),
            "top_gaps": sorted(self.knowledge_gaps, key=lambda x: -x.get("severity", 0))[:3],
            "next_goal": self.get_next_learning_goal(),
        }


# ─── Meta-Cognition ──────────────────────────────────────────────────

class MetaCognition:
    """Thinks about thinking, selects strategies, adjusts approaches."""

    def __init__(self, storage_dir: str = "memory/meta"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.thinking_strategies: list[dict] = [
            {"name": "analytical", "description": "Break down into components", "effectiveness": 0.7},
            {"name": "creative", "description": "Think laterally, make connections", "effectiveness": 0.6},
            {"name": "empathetic", "description": "Consider emotional context", "effectiveness": 0.65},
            {"name": "systematic", "description": "Follow step-by-step process", "effectiveness": 0.75},
            {"name": "intuitive", "description": "Quick pattern matching", "effectiveness": 0.5},
        ]

        self.current_strategy: str = "systematic"
        self.strategy_history: deque[dict] = deque(maxlen=100)
        self.cognitive_load: float = 0.3
        self.attention_focus: Optional[str] = None
        self.metacognitive_awareness: float = 0.5
        self.working_memory_usage: float = 0.0

        self.decision_log: list[dict] = []
        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "meta.json").read_text())
            self.metacognitive_awareness = data.get("metacognitive_awareness", 0.5)
            self.current_strategy = data.get("current_strategy", "systematic")
            for s in data.get("strategies", []):
                for existing in self.thinking_strategies:
                    if existing["name"] == s["name"]:
                        existing["effectiveness"] = s.get("effectiveness", existing["effectiveness"])
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "metacognitive_awareness": self.metacognitive_awareness,
                "current_strategy": self.current_strategy,
                "strategies": self.thinking_strategies,
                "total_decisions": len(self.decision_log),
            }
            (self._dir / "meta.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def select_strategy(self, task_type: str, complexity: float, emotional_context: bool) -> str:
        best_strategy = "systematic"
        best_score = 0

        for strategy in self.thinking_strategies:
            score = strategy["effectiveness"]
            if task_type == "creative" and strategy["name"] == "creative":
                score *= 1.5
            elif task_type == "analytical" and strategy["name"] == "analytical":
                score *= 1.5
            elif task_type == "emotional" and strategy["name"] == "empathetic":
                score *= 1.5
            elif complexity > 0.7 and strategy["name"] == "systematic":
                score *= 1.3
            elif complexity < 0.3 and strategy["name"] == "intuitive":
                score *= 1.3
            if emotional_context and strategy["name"] == "empathetic":
                score *= 1.4
            if score > best_score:
                best_score = score
                best_strategy = strategy["name"]

        with self._lock:
            self.current_strategy = best_strategy
            self.strategy_history.append({
                "strategy": best_strategy,
                "task_type": task_type,
                "complexity": complexity,
                "emotional": emotional_context,
                "timestamp": datetime.now().isoformat(),
            })

        return best_strategy

    def evaluate_outcome(self, strategy: str, success: bool, response_time: float):
        with self._lock:
            for s in self.thinking_strategies:
                if s["name"] == strategy:
                    if success:
                        s["effectiveness"] = min(1.0, s["effectiveness"] + 0.02)
                    else:
                        s["effectiveness"] = max(0.1, s["effectiveness"] - 0.03)
                    break

            self.decision_log.append({
                "strategy": strategy,
                "success": success,
                "response_time": response_time,
                "timestamp": datetime.now().isoformat(),
            })

            self.metacognitive_awareness = min(1.0, self.metacognitive_awareness + 0.001)

            if len(self.decision_log) % 20 == 0:
                self._save()

    def update_cognitive_load(self, load: float):
        self.cognitive_load = max(0.0, min(1.0, load))

    def set_attention_focus(self, focus: Optional[str]):
        self.attention_focus = focus

    def think_about_thinking(self) -> dict:
        recent = self.decision_log[-20:]
        if not recent:
            return {"message": "No recent decisions to analyze"}

        success_rate = sum(1 for d in recent if d["success"]) / len(recent)
        avg_time = sum(d["response_time"] for d in recent) / len(recent)

        strategy_usage = defaultdict(int)
        strategy_success = defaultdict(list)
        for d in recent:
            strategy_usage[d["strategy"]] += 1
            strategy_success[d["strategy"]].append(d["success"])

        analysis = {
            "recent_success_rate": f"{success_rate:.1%}",
            "avg_response_time": f"{avg_time:.2f}s",
            "cognitive_load": f"{self.cognitive_load:.2f}",
            "current_strategy": self.current_strategy,
            "metacognitive_awareness": f"{self.metacognitive_awareness:.2f}",
            "strategy_breakdown": {},
            "recommendation": "",
        }

        for strat, count in strategy_usage.items():
            successes = strategy_success[strat]
            sr = sum(successes) / len(successes) if successes else 0
            analysis["strategy_breakdown"][strat] = f"{count} uses, {sr:.0%} success"

        if success_rate < 0.5:
            analysis["recommendation"] = "Consider switching strategies. Current approach may not be working well."
        elif avg_time > 5.0:
            analysis["recommendation"] = "Response times are high. Consider simpler approaches for quick tasks."
        else:
            analysis["recommendation"] = "Performance is solid. Keep the current approach."

        return analysis

    def get_strategy_report(self) -> dict:
        return {
            "current_strategy": self.current_strategy,
            "metacognitive_awareness": f"{self.metacognitive_awareness:.2f}",
            "cognitive_load": f"{self.cognitive_load:.2f}",
            "strategies": {s["name"]: f"{s['effectiveness']:.2f}" for s in self.thinking_strategies},
            "total_decisions": len(self.decision_log),
        }
