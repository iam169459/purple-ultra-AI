"""Self-Learning System - Purple Ultra AI's autonomous learning engine.

Learns from every conversation:
- Pattern recognition across interactions
- Response quality scoring and improvement
- Memory consolidation (short-term → long-term)
- Curiosity-driven exploration
- Knowledge graph building
- Adaptive behavior based on user preferences
"""

import json
import math
import os
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
#  LEARNING DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Interaction:
    """A single learning interaction record."""
    timestamp: float
    user_input: str
    response: str
    intent: str
    quality_score: float = 0.5
    user_feedback: str = ""
    topics: list[str] = field(default_factory=list)
    patterns_matched: list[str] = field(default_factory=list)
    response_time_ms: float = 0.0
    was_helpful: bool | None = None


@dataclass
class KnowledgeNode:
    """A node in the knowledge graph."""
    key: str
    content: str
    category: str
    strength: float = 1.0
    access_count: int = 0
    last_accessed: float = 0.0
    created: float = field(default_factory=time.time)
    connections: list[str] = field(default_factory=list)
    confidence: float = 1.0
    source: str = "knowledge_base"


@dataclass
class Pattern:
    """A recognized interaction pattern."""
    pattern_id: str
    trigger: str
    response_template: str
    success_count: int = 0
    fail_count: int = 0
    confidence: float = 0.5
    examples: list[str] = field(default_factory=list)
    created: float = field(default_factory=time.time)


@dataclass
class UserPreference:
    """A learned user preference."""
    key: str
    value: str | float | bool
    confidence: float = 0.5
    evidence_count: int = 1
    last_updated: float = field(default_factory=time.time)


# ═══════════════════════════════════════════════════════════════════════════
#  RESPONSE SCORER
# ═══════════════════════════════════════════════════════════════════════════

class ResponseScorer:
    """Scores response quality based on multiple factors."""

    def __init__(self):
        self._scoring_history: deque[dict] = deque(maxlen=200)
        self._factor_weights = {
            "length": 0.1,
            "specificity": 0.2,
            "relevance": 0.25,
            "tone": 0.15,
            "completeness": 0.2,
            "clarity": 0.1,
        }

    def score_response(self, user_input: str, response: str, intent: str,
                       context: dict | None = None) -> float:
        scores = {}
        scores["length"] = self._score_length(response, intent)
        scores["specificity"] = self._score_specificity(response)
        scores["relevance"] = self._score_relevance(user_input, response, intent)
        scores["tone"] = self._score_tone(response, intent)
        scores["completeness"] = self._score_completeness(response, intent)
        scores["clarity"] = self._score_clarity(response)

        total = sum(
            scores[f] * self._factor_weights[f]
            for f in scores
        )
        total = max(0.0, min(1.0, total))

        record = {
            "timestamp": time.time(),
            "user_input": user_input[:100],
            "intent": intent,
            "scores": scores,
            "total": total,
        }
        self._scoring_history.append(record)

        return total

    def _score_length(self, response: str, intent: str) -> float:
        rlen = len(response)
        ideal = {
            "greeting": (20, 80), "factual": (50, 200), "how_to": (80, 400),
            "code": (100, 500), "math": (10, 100), "empathy": (30, 150),
        }
        low, high = ideal.get(intent, (30, 200))
        if rlen < low:
            return rlen / low if low > 0 else 0.5
        elif rlen > high * 3:
            return max(0.3, 1.0 - (rlen - high * 3) / (high * 5))
        return 1.0

    def _score_specificity(self, response: str) -> float:
        specific_markers = [
            "for example", "such as", "specifically", "including",
            "e.g.", "i.e.", "like", "instance", "particularly",
            "step 1", "step 2", "first", "second", "third",
        ]
        count = sum(1 for m in specific_markers if m in response.lower())
        return min(1.0, 0.3 + count * 0.15)

    def _score_relevance(self, user_input: str, response: str, intent: str) -> float:
        input_words = set(user_input.lower().split())
        response_words = set(response.lower().split())
        overlap = input_words & response_words
        base_score = min(1.0, len(overlap) / max(1, len(input_words) * 0.3))
        return base_score

    def _score_tone(self, response: str, intent: str) -> float:
        score = 0.7
        if intent == "empathy":
            empathetic = ["understand", "feel", "here for you", "listen", "care", "sorry"]
            if any(w in response.lower() for w in empathetic):
                score += 0.3
        elif intent == "greeting":
            friendly = ["hello", "hi", "welcome", "happy", "great"]
            if any(w in response.lower() for w in friendly):
                score += 0.2
        return min(1.0, score)

    def _score_completeness(self, response: str, intent: str) -> float:
        if intent == "how_to":
            steps = sum(1 for i in range(1, 10) if f"step {i}" in response.lower() or f"{i}." in response)
            return min(1.0, 0.3 + steps * 0.15)
        elif intent == "code":
            code_markers = ["def ", "class ", "import ", "function ", "return", "if ", "for "]
            count = sum(1 for m in code_markers if m in response)
            return min(1.0, 0.2 + count * 0.15)
        return 0.6

    def _score_clarity(self, response: str) -> float:
        sentences = [s.strip() for s in response.replace("!", ".").replace("?", ".").split(".") if s.strip()]
        if not sentences:
            return 0.3
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len > 30:
            return 0.5
        elif avg_len < 3:
            return 0.6
        return 0.8

    def get_scoring_stats(self) -> dict:
        if not self._scoring_history:
            return {"total_scores": 0, "avg_quality": 0.0}
        scores = [r["total"] for r in self._scoring_history]
        return {
            "total_scores": len(scores),
            "avg_quality": sum(scores) / len(scores),
            "best_score": max(scores),
            "worst_score": min(scores),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  PATTERN RECOGNIZER
# ═══════════════════════════════════════════════════════════════════════════

class PatternRecognizer:
    """Recognizes and learns patterns from conversations."""

    def __init__(self):
        self._patterns: dict[str, Pattern] = {}
        self._ngram_index: dict[tuple[str, ...], list[str]] = {}
        self._min_pattern_length = 2
        self._max_pattern_length = 8
        self._pattern_id_counter = 0

    def extract_ngrams(self, text: str, n: int) -> list[tuple[str, ...]]:
        words = text.lower().split()
        return [tuple(words[i:i+n]) for i in range(len(words) - n + 1)]

    def index_text(self, text: str) -> None:
        for n in range(self._min_pattern_length, self._max_pattern_length + 1):
            for ngram in self.extract_ngrams(text, n):
                if ngram not in self._ngram_index:
                    self._ngram_index[ngram] = []
                self._ngram_index[ngram].append(text)

    def find_similar_patterns(self, text: str, threshold: float = 0.3) -> list[tuple[str, float]]:
        text_ngrams = set()
        for n in range(self._min_pattern_length, self._max_pattern_length + 1):
            text_ngrams.update(self.extract_ngrams(text, n))

        matches: dict[str, float] = {}
        for ngram in text_ngrams:
            if ngram in self._ngram_index:
                for original in self._ngram_index[ngram]:
                    if original not in matches:
                        matches[original] = 0.0
                    matches[original] += 1.0 / max(1, len(text_ngrams))

        return sorted(
            [(k, v) for k, v in matches.items() if v >= threshold],
            key=lambda x: x[1], reverse=True
        )[:5]

    def learn_pattern(self, user_input: str, response: str, successful: bool = True) -> Pattern | None:
        key_words = [w for w in user_input.lower().split() if len(w) > 3]
        if len(key_words) < 2:
            return None

        trigger = " ".join(key_words[:4])
        pattern_id = f"pat_{self._pattern_id_counter}"
        self._pattern_id_counter += 1

        if trigger in self._patterns:
            p = self._patterns[trigger]
            if successful:
                p.success_count += 1
                p.confidence = min(1.0, p.confidence + 0.05)
            else:
                p.fail_count += 1
                p.confidence = max(0.0, p.confidence - 0.1)
            return p

        pattern = Pattern(
            pattern_id=pattern_id,
            trigger=trigger,
            response_template=response[:200],
            success_count=1 if successful else 0,
            fail_count=0 if successful else 1,
            confidence=0.5,
            examples=[user_input[:100]],
        )
        self._patterns[trigger] = pattern
        return pattern

    def find_best_pattern(self, user_input: str) -> Pattern | None:
        words = set(user_input.lower().split())
        best_match = None
        best_score = 0.0

        for trigger, pattern in self._patterns.items():
            trigger_words = set(trigger.split())
            overlap = len(words & trigger_words)
            score = (overlap / max(1, len(trigger_words))) * pattern.confidence
            if score > best_score and score > 0.3:
                best_score = score
                best_match = pattern

        return best_match

    def get_stats(self) -> dict:
        return {
            "total_patterns": len(self._patterns),
            "total_ngrams": len(self._ngram_index),
            "avg_confidence": (
                sum(p.confidence for p in self._patterns.values()) / len(self._patterns)
                if self._patterns else 0.0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  MEMORY CONSOLIDATOR
# ═══════════════════════════════════════════════════════════════════════════

class MemoryConsolidator:
    """Consolidates short-term memories into long-term knowledge."""

    def __init__(self, max_short_term: int = 100, max_long_term: int = 2000):
        self._short_term: deque[Interaction] = deque(maxlen=max_short_term)
        self._long_term: list[KnowledgeNode] = []
        self._max_long_term = max_long_term
        self._consolidation_threshold = 3
        self._consolidation_count = 0

    def store_short_term(self, interaction: Interaction) -> None:
        self._short_term.append(interaction)

    def consolidate(self) -> list[KnowledgeNode]:
        new_nodes = []
        topic_groups: dict[str, list[Interaction]] = {}

        for interaction in self._short_term:
            for topic in interaction.topics:
                if topic not in topic_groups:
                    topic_groups[topic] = []
                topic_groups[topic].append(interaction)

        for topic, interactions in topic_groups.items():
            if len(interactions) >= self._consolidation_threshold:
                content_parts = []
                for inter in interactions[:5]:
                    content_parts.append(f"Q: {inter.user_input[:80]}")
                    content_parts.append(f"A: {inter.response[:80]}")

                node = KnowledgeNode(
                    key=topic,
                    content="\n".join(content_parts),
                    category="learned",
                    strength=len(interactions) / 10.0,
                    access_count=len(interactions),
                    last_accessed=interactions[-1].timestamp,
                    source="consolidation",
                )

                existing = next((n for n in self._long_term if n.key == topic), None)
                if existing:
                    existing.strength = min(2.0, existing.strength + 0.2)
                    existing.access_count += len(interactions)
                    existing.content = node.content
                else:
                    self._long_term.append(node)
                    new_nodes.append(node)

        self._consolidation_count += 1
        self._trim_long_term()
        return new_nodes

    def _trim_long_term(self) -> None:
        if len(self._long_term) > self._max_long_term:
            self._long_term.sort(key=lambda n: n.strength * n.access_count, reverse=True)
            self._long_term = self._long_term[:self._max_long_term]

    def recall(self, query: str) -> KnowledgeNode | None:
        query_words = set(query.lower().split())
        best_match = None
        best_score = 0.0

        for node in self._long_term:
            key_words = set(node.key.lower().split())
            overlap = len(query_words & key_words)
            score = (overlap / max(1, len(key_words))) * node.strength
            if score > best_score:
                best_score = score
                best_match = node

        if best_match:
            best_match.access_count += 1
            best_match.last_accessed = time.time()
            best_match.strength = min(2.0, best_match.strength + 0.05)

        return best_match if best_score > 0.2 else None

    def get_stats(self) -> dict:
        return {
            "short_term_count": len(self._short_term),
            "long_term_count": len(self._long_term),
            "consolidations": self._consolidation_count,
            "avg_strength": (
                sum(n.strength for n in self._long_term) / len(self._long_term)
                if self._long_term else 0.0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  CURIOSITY ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class CuriosityEngine:
    """Drives the AI to ask questions and explore new topics."""

    def __init__(self):
        self._explored_topics: dict[str, int] = {}
        self._curiosity_queue: deque[str] = deque(maxlen=50)
        self._exploration_rate = 0.15
        self._topic_depth: dict[str, int] = {}
        self._total_curiosity_triggers = 0

    def should_explore(self, topic: str) -> bool:
        depth = self._topic_depth.get(topic, 0)
        if depth < 2:
            return random.random() < self._exploration_rate * 2
        return random.random() < self._exploration_rate

    def record_exploration(self, topic: str) -> None:
        self._explored_topics[topic] = self._explored_topics.get(topic, 0) + 1
        self._topic_depth[topic] = self._topic_depth.get(topic, 0) + 1
        self._total_curiosity_triggers += 1

    def generate_curiosity_questions(self, current_topic: str) -> list[str]:
        questions = []
        if current_topic not in self._explored_topics:
            questions.append(f"What would you like to know about {current_topic}?")
        depth = self._topic_depth.get(current_topic, 0)
        if depth > 1:
            questions.append(f"Would you like to go deeper into {current_topic}?")
        related = self._get_related_topics(current_topic)
        if related:
            questions.append(f"Would you also like to learn about {related[0]}?")
        return questions[:2]

    def _get_related_topics(self, topic: str) -> list[str]:
        related_map = {
            "python": ["programming", "data structures", "machine learning"],
            "machine learning": ["deep learning", "neural networks", "statistics"],
            "javascript": ["web development", "node.js", "react"],
            "docker": ["kubernetes", "devops", "containers"],
            "databases": ["sql", "mongodb", "data modeling"],
        }
        return related_map.get(topic.lower(), [])

    def get_unexplored_areas(self) -> list[str]:
        all_areas = [
            "programming", "mathematics", "science", "history",
            "philosophy", "psychology", "economics", "art",
            "music", "geography", "literature", "technology",
        ]
        return [a for a in all_areas if a not in self._explored_topics]

    def get_stats(self) -> dict:
        return {
            "explored_topics": len(self._explored_topics),
            "total_triggers": self._total_curiosity_triggers,
            "exploration_rate": self._exploration_rate,
            "depth_avg": (
                sum(self._topic_depth.values()) / len(self._topic_depth)
                if self._topic_depth else 0.0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  USER PREFERENCE LEARNER
# ═══════════════════════════════════════════════════════════════════════════

class UserPreferenceLearner:
    """Learns user preferences from conversation patterns."""

    def __init__(self):
        self._preferences: dict[str, UserPreference] = {}
        self._interaction_count = 0
        self._response_length_history: list[int] = []
        self._topic_history: list[str] = []
        self._sentiment_history: list[float] = []

    def observe_interaction(self, interaction: Interaction) -> None:
        self._interaction_count += 1
        self._response_length_history.append(len(interaction.response))
        for topic in interaction.topics:
            self._topic_history.append(topic)
        if interaction.was_helpful is not None:
            self._sentiment_history.append(1.0 if interaction.was_helpful else 0.0)

        self._update_preference("preferred_response_length", self._infer_response_length())
        self._update_preference("preferred_depth", self._infer_depth())
        self._update_preference("preferred_style", self._infer_style(interaction))
        self._update_preference("technical_level", self._infer_technical_level())

    def _infer_response_length(self) -> str:
        if not self._response_length_history:
            return "medium"
        avg = sum(self._response_length_history[-20:]) / min(20, len(self._response_length_history))
        if avg < 80:
            return "short"
        elif avg > 250:
            return "long"
        return "medium"

    def _infer_depth(self) -> str:
        if len(self._topic_history) < 3:
            return "moderate"
        recent_topics = self._topic_history[-10:]
        technical = ["programming", "machine learning", "database", "algorithm", "neural"]
        tech_count = sum(1 for t in recent_topics if any(tech in t.lower() for tech in technical))
        if tech_count > len(recent_topics) * 0.6:
            return "deep"
        return "moderate"

    def _infer_style(self, interaction: Interaction) -> str:
        if interaction.user_input.endswith("?"):
            return "questioning"
        if any(w in interaction.user_input.lower() for w in ["create", "make", "build", "write"]):
            return "creative"
        if any(w in interaction.user_input.lower() for w in ["explain", "why", "how"]):
            return "analytical"
        return "conversational"

    def _infer_technical_level(self) -> str:
        if len(self._topic_history) < 5:
            return "intermediate"
        technical_topics = sum(
            1 for t in self._topic_history[-20:]
            if any(w in t.lower() for w in ["algorithm", "neural", "database", "compiler", "kernel"])
        )
        if technical_topics > 5:
            return "advanced"
        elif technical_topics < 2:
            return "beginner"
        return "intermediate"

    def _update_preference(self, key: str, value: str | float | bool) -> None:
        if key in self._preferences:
            pref = self._preferences[key]
            if pref.value == value:
                pref.confidence = min(1.0, pref.confidence + 0.05)
                pref.evidence_count += 1
            else:
                pref.confidence = max(0.0, pref.confidence - 0.1)
                if pref.confidence < 0.2:
                    pref.value = value
                    pref.confidence = 0.3
                    pref.evidence_count = 1
            pref.last_updated = time.time()
        else:
            self._preferences[key] = UserPreference(
                key=key, value=value, confidence=0.3, evidence_count=1
            )

    def get_preference(self, key: str) -> str | float | bool | None:
        pref = self._preferences.get(key)
        if pref and pref.confidence > 0.3:
            return pref.value
        return None

    def get_all_preferences(self) -> dict[str, dict]:
        return {
            k: {"value": v.value, "confidence": v.confidence, "evidence": v.evidence_count}
            for k, v in self._preferences.items()
        }

    def get_stats(self) -> dict:
        return {
            "total_preferences": len(self._preferences),
            "interaction_count": self._interaction_count,
            "avg_confidence": (
                sum(p.confidence for p in self._preferences.values()) / len(self._preferences)
                if self._preferences else 0.0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  KNOWLEDGE GRAPH
# ═══════════════════════════════════════════════════════════════════════════

class KnowledgeGraph:
    """Builds and maintains a knowledge graph from interactions."""

    def __init__(self):
        self._nodes: dict[str, KnowledgeNode] = {}
        self._edges: dict[str, list[str]] = {}
        self._total_connections = 0

    def add_node(self, key: str, content: str, category: str = "general") -> KnowledgeNode:
        if key in self._nodes:
            node = self._nodes[key]
            node.access_count += 1
            node.last_accessed = time.time()
            return node

        node = KnowledgeNode(
            key=key, content=content, category=category,
            source="conversation",
        )
        self._nodes[key] = node
        self._edges[key] = []
        return node

    def connect(self, key1: str, key2: str) -> None:
        if key1 not in self._edges:
            self._edges[key1] = []
        if key2 not in self._edges:
            self._edges[key2] = []
        if key2 not in self._edges[key1]:
            self._edges[key1].append(key2)
            self._edges[key2].append(key1)
            self._total_connections += 1
            if key1 in self._nodes:
                self._nodes[key1].connections.append(key2)
            if key2 in self._nodes:
                self._nodes[key2].connections.append(key1)

    def find_related(self, key: str, max_depth: int = 2) -> list[str]:
        if key not in self._edges:
            return []
        visited = {key}
        result = []
        queue = [(key, 0)]
        while queue and len(result) < 20:
            current, depth = queue.pop(0)
            if depth > 0 and current in self._nodes:
                result.append(current)
            if depth < max_depth:
                for neighbor in self._edges.get(current, []):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, depth + 1))
        return result

    def strengthen(self, key: str, amount: float = 0.1) -> None:
        if key in self._nodes:
            self._nodes[key].strength = min(2.0, self._nodes[key].strength + amount)

    def get_stats(self) -> dict:
        return {
            "total_nodes": len(self._nodes),
            "total_connections": self._total_connections,
            "categories": list(set(n.category for n in self._nodes.values())),
            "avg_strength": (
                sum(n.strength for n in self._nodes.values()) / len(self._nodes)
                if self._nodes else 0.0
            ),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN SELF-LEARNING SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

class SelfLearningSystem:
    """Main learning system that orchestrates all learning components."""

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "learning"
        )
        os.makedirs(self.data_dir, exist_ok=True)

        self.scorer = ResponseScorer()
        self.patterns = PatternRecognizer()
        self.memory = MemoryConsolidator()
        self.curiosity = CuriosityEngine()
        self.preferences = UserPreferenceLearner()
        self.knowledge_graph = KnowledgeGraph()

        self._interactions: deque[Interaction] = deque(maxlen=500)
        self._learning_cycles = 0
        self._total_learned = 0
        self._session_start = time.time()

        self._load()

    def learn_from_interaction(self, user_input: str, response: str, intent: str,
                                topics: list[str] | None = None,
                                user_feedback: str = "",
                                was_helpful: bool | None = None,
                                response_time_ms: float = 0.0) -> dict:
        interaction = Interaction(
            timestamp=time.time(),
            user_input=user_input,
            response=response,
            intent=intent,
            user_feedback=user_feedback,
            topics=topics or [],
            response_time_ms=response_time_ms,
            was_helpful=was_helpful,
        )

        quality = self.scorer.score_response(user_input, response, intent)
        interaction.quality_score = quality

        self._interactions.append(interaction)
        self.memory.store_short_term(interaction)

        self.patterns.index_text(user_input)
        pattern = self.patterns.learn_pattern(user_input, response, quality > 0.5)
        if pattern:
            interaction.patterns_matched.append(pattern.pattern_id)

        for i, t1 in enumerate(topics or []):
            for t2 in (topics or [])[i+1:]:
                self.knowledge_graph.connect(t1, t2)

        self.preferences.observe_interaction(interaction)
        self._total_learned += 1

        return {
            "quality_score": quality,
            "patterns_matched": len(interaction.patterns_matched),
            "topics_learned": len(topics or []),
        }

    def get_suggestion(self, user_input: str) -> str | None:
        pattern = self.patterns.find_best_pattern(user_input)
        if pattern and pattern.confidence > 0.6:
            return pattern.response_template

        similar = self.patterns.find_similar_patterns(user_input)
        if similar:
            return f"I recall something similar: {similar[0][0][:100]}"

        return None

    def get_curiosity_question(self, current_topic: str) -> str | None:
        if self.curiosity.should_explore(current_topic):
            questions = self.curiosity.generate_curiosity_questions(current_topic)
            if questions:
                self.curiosity.record_exploration(current_topic)
                return random.choice(questions)
        return None

    def run_consolidation(self) -> dict:
        new_nodes = self.memory.consolidate()
        self._learning_cycles += 1
        return {
            "new_knowledge_nodes": len(new_nodes),
            "total_cycles": self._learning_cycles,
            "memory_stats": self.memory.get_stats(),
        }

    def get_response_suggestion(self, user_input: str, intent: str) -> str | None:
        pref_length = self.preferences.get_preference("preferred_response_length")
        pref_depth = self.preferences.get_preference("preferred_depth")

        suggestions = []
        if pref_length == "short":
            suggestions.append("Keep response brief and concise.")
        elif pref_length == "long":
            suggestions.append("Provide detailed, comprehensive response.")
        if pref_depth == "deep":
            suggestions.append("Include technical depth and examples.")

        return " ".join(suggestions) if suggestions else None

    def get_stats(self) -> dict:
        uptime = time.time() - self._session_start
        return {
            "total_interactions": self._total_learned,
            "learning_cycles": self._learning_cycles,
            "uptime_seconds": uptime,
            "scorer": self.scorer.get_scoring_stats(),
            "patterns": self.patterns.get_stats(),
            "memory": self.memory.get_stats(),
            "curiosity": self.curiosity.get_stats(),
            "preferences": self.preferences.get_stats(),
            "knowledge_graph": self.knowledge_graph.get_stats(),
        }

    def save(self) -> None:
        meta = {
            "learning_cycles": self._learning_cycles,
            "total_learned": self._total_learned,
            "session_start": self._session_start,
            "preferences": self.preferences.get_all_preferences(),
        }
        with open(os.path.join(self.data_dir, "learning_meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

    def _load(self) -> None:
        try:
            meta_path = os.path.join(self.data_dir, "learning_meta.json")
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)
                self._learning_cycles = meta.get("learning_cycles", 0)
                self._total_learned = meta.get("total_learned", 0)
        except Exception:
            pass
