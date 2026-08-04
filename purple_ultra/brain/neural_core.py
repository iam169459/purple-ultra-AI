"""Neural Core - The fundamental nervous system of Purple Ultra AI.

The Neural Core is the底层 processing engine that handles:
- Signal processing (encode → process → decode)
- Attention mechanisms (selective focus)
- Memory systems (working, episodic, semantic, procedural)
- Emotion processing (valence-arousal-dominance model)
- Decision making (multi-criteria weighted voting)
- Learning loops (reinforcement, supervised, unsupervised)
- Homeostasis (internal state balance)
- Dream consolidation (background processing)
- Temporal processing (sequence, timing)
- Pattern completion (fill missing info)
- Associative memory (link concepts)
- Metacognition (self-monitoring)

Pure Python - no external dependencies.
"""

import json
import math
import os
import random
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum, IntEnum


# ═══════════════════════════════════════════════════════════════════════════
#  CORE ENUMS & CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════

class SignalType(Enum):
    INPUT = "input"
    HIDDEN = "hidden"
    OUTPUT = "output"
    FEEDBACK = "feedback"
    REWARD = "reward"
    PREDICTION = "prediction"
    ATTENTION = "attention"
    EMOTION = "emotion"
    MEMORY = "memory"


class MemoryType(Enum):
    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class EmotionDimension(IntEnum):
    VALENCE = 0      # -1 (negative) to +1 (positive)
    AROUSAL = 1      # -1 (calm) to +1 (excited)
    DOMINANCE = 2    # -1 (submissive) to +1 (dominant)


class DecisionStrategy(Enum):
    WEIGHTED_VOTE = "weighted_vote"
    MAX_CONFIDENCE = "max_confidence"
    SOFTMAX = "softmax"
    CONSENSUS = "consensus"


class LearningMode(Enum):
    REINFORCEMENT = "reinforcement"
    SUPERVISED = "supervised"
    UNSUPERVISED = "unsupervised"
    SELF_SUPERVISED = "self_supervised"


NEURAL_CONSTANTS = {
    "working_memory_slots": 7,
    "working_memory_decay": 0.1,
    "episodic_memory_capacity": 1000,
    "semantic_memory_consolidation_threshold": 3,
    "attention_heads": 4,
    "emotion_decay_rate": 0.05,
    "homeostasis_rate": 0.02,
    "dream_consolidation_interval": 100,
    "prediction_horizon": 5,
    "metacognition_sample_rate": 0.1,
    "pathway_plasticity": 0.1,
    "signal_noise_threshold": 0.01,
    "max_processing_depth": 10,
    "temporal_window": 20,
}


# ═══════════════════════════════════════════════════════════════════════════
#  SIGNAL
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class Signal:
    """A neural signal traveling through pathways."""
    signal_type: SignalType
    values: list[float]
    source: str
    destination: str
    strength: float = 1.0
    timestamp: float = field(default_factory=time.time)
    metadata: dict = field(default_factory=dict)
    decay_rate: float = 0.01
    _age: float = 0.0

    def age(self, dt: float) -> "Signal":
        self._age += dt
        self.strength *= (1.0 - self.decay_rate * dt)
        return self

    @property
    def is_alive(self) -> bool:
        return self.strength > 0.01 and self._age < 10.0

    @property
    def dimension(self) -> int:
        return len(self.values)

    def normalize(self) -> "Signal":
        norm = math.sqrt(sum(v * v for v in self.values)) or 1.0
        self.values = [v / norm for v in self.values]
        return self

    def add_noise(self, amount: float = 0.01) -> "Signal":
        self.values = [v + random.gauss(0, amount) for v in self.values]
        return self


# ═══════════════════════════════════════════════════════════════════════════
#  PROCESSING UNIT
# ═══════════════════════════════════════════════════════════════════════════

class ProcessingUnit:
    """A single neural processing unit with activation dynamics."""

    def __init__(self, unit_id: str, dim: int = 16, bias: float = 0.0):
        self.unit_id = unit_id
        self.dim = dim
        self.bias = bias
        self.activation = [0.0] * dim
        self.resting_potential = [0.0] * dim
        self.threshold = 0.3
        self.refractory_period = 0.05
        self._last_fire_time = 0.0
        self._fire_count = 0
        self._total_activation = 0.0

    def receive(self, signal: Signal) -> None:
        if signal.dimension != self.dim:
            signal.values = signal.values[:self.dim] + [0.0] * max(0, self.dim - signal.dimension)
        for i in range(self.dim):
            self.activation[i] += signal.values[i] * signal.strength

    def process(self, dt: float = 0.01) -> list[float]:
        current_time = time.time()
        if current_time - self._last_fire_time < self.refractory_period:
            return [0.0] * self.dim

        output = []
        fired = False
        for i in range(self.dim):
            self.activation[i] += self.bias * dt
            self.activation[i] *= (1.0 - 0.1 * dt)
            self.activation[i] = max(-5.0, min(5.0, self.activation[i]))
            val = self.activation[i] - self.threshold
            if val > 0:
                out = math.tanh(val)
                fired = True
            else:
                out = 0.0
            output.append(out)

        if fired:
            self._last_fire_time = current_time
            self._fire_count += 1
            self._total_activation += sum(abs(a) for a in self.activation)

        self.activation = [
            a * (1.0 - NEURAL_CONSTANTS["working_memory_decay"] * dt)
            for a in self.activation
        ]
        return output

    @property
    def activity_level(self) -> float:
        return sum(abs(a) for a in self.activation) / self.dim if self.dim > 0 else 0.0

    @property
    def fire_rate(self) -> float:
        return self._fire_count / max(1, time.time() - self._last_fire_time)


# ═══════════════════════════════════════════════════════════════════════════
#  NEURAL PATHWAY
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class NeuralPathway:
    """A weighted connection between two processing units."""
    source_id: str
    target_id: str
    weights: list[list[float]]
    plasticity: float = 0.1
    strength: float = 1.0
    usage_count: int = 0
    last_used: float = 0.0
    created: float = field(default_factory=time.time)

    def transmit(self, signal: Signal) -> Signal:
        if signal.dimension != len(self.weights):
            signal.values = signal.values[:len(self.weights)] + [0.0] * max(
                0, len(self.weights) - signal.dimension
            )
        output = [0.0] * len(self.weights[0]) if self.weights else []
        for j in range(len(self.weights[0])):
            for i in range(len(self.weights)):
                if i < len(signal.values):
                    output[j] += signal.values[i] * self.weights[i][j]

        self.usage_count += 1
        self.last_used = time.time()

        return Signal(
            signal_type=signal.signal_type,
            values=output,
            source=self.source_id,
            destination=self.target_id,
            strength=signal.strength * self.strength,
            timestamp=time.time(),
        )

    def strengthen(self, amount: float = 0.05) -> None:
        self.strength = min(2.0, self.strength + amount * self.plasticity)

    def weaken(self, amount: float = 0.02) -> None:
        self.strength = max(0.0, self.strength - amount * self.plasticity)


# ═══════════════════════════════════════════════════════════════════════════
#  ATTENTION MECHANISM
# ═══════════════════════════════════════════════════════════════════════════

class AttentionMechanism:
    """Multi-head attention for selective focus."""

    def __init__(self, num_heads: int = 4, dim: int = 32):
        self.num_heads = num_heads
        self.dim = dim
        self.heads: list[dict] = []
        for _ in range(num_heads):
            self.heads.append({
                "query": [random.gauss(0, 0.1) for _ in range(dim)],
                "key": [random.gauss(0, 0.1) for _ in range(dim)],
                "value": [random.gauss(0, 0.1) for _ in range(dim)],
            })
        self._attention_history: deque[dict] = deque(maxlen=100)

    def compute_attention(self, query: list[float], keys: list[list[float]],
                          values: list[list[float]], mask: list[bool] | None = None) -> list[float]:
        if not keys or not values:
            return [0.0] * self.dim

        scores = []
        for k in keys:
            score = sum(q * ki for q, ki in zip(query[:len(k)], k[:len(query)]))
            scores.append(score / math.sqrt(max(1, len(query))))

        if mask:
            scores = [s if not m else float('-inf') for s, m in zip(scores, mask)]

        max_score = max(scores) if scores else 0
        exp_scores = [math.exp(s - max_score) for s in scores]
        total = sum(exp_scores) or 1.0
        weights = [e / total for e in exp_scores]

        output = [0.0] * self.dim
        for w, v in zip(weights, values):
            for i in range(min(self.dim, len(v))):
                output[i] += w * v[i]

        return output

    def multi_head_attention(self, query: list[float], keys: list[list[float]],
                             values: list[list[float]]) -> list[float]:
        outputs = []
        head_dim = self.dim // self.num_heads

        for head in self.heads:
            hq = [q * k for q, k in zip(query[:head_dim], head["query"][:head_dim])]
            head_output = self.compute_attention(hq, keys, values)
            outputs.extend(head_output[:head_dim])

        return outputs[:self.dim]

    def focus(self, input_signal: Signal, context: list[list[float]] | None = None) -> Signal:
        if not context:
            context = [input_signal.values]

        query = input_signal.values
        keys = context
        values = context

        attended = self.multi_head_attention(query, keys, values)

        return Signal(
            signal_type=SignalType.ATTENTION,
            values=attended,
            source=input_signal.source,
            destination=input_signal.destination,
            strength=input_signal.strength,
        )


# ═══════════════════════════════════════════════════════════════════════════
#  MEMORY SYSTEM
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class MemoryTrace:
    """A single memory trace."""
    content: list[float]
    metadata: dict
    memory_type: MemoryType
    strength: float = 1.0
    access_count: int = 0
    created: float = field(default_factory=time.time)
    last_accessed: float = 0.0
    emotional_valence: float = 0.0


class WorkingMemory:
    """Active working memory with limited slots."""

    def __init__(self, slots: int = 7):
        self.slots = slots
        self._items: deque[MemoryTrace] = deque(maxlen=slots)
        self._total_accesses = 0

    def store(self, content: list[float], metadata: dict | None = None,
              emotional_valence: float = 0.0) -> MemoryTrace:
        trace = MemoryTrace(
            content=content,
            metadata=metadata or {},
            memory_type=MemoryType.WORKING,
            emotional_valence=emotional_valence,
        )
        if len(self._items) >= self.slots:
            weakest = min(self._items, key=lambda m: m.strength)
            weakest.strength *= 0.5
        self._items.append(trace)
        return trace

    def retrieve(self, query: list[float], top_k: int = 3) -> list[MemoryTrace]:
        scored = []
        for trace in self._items:
            score = sum(q * c for q, c in zip(query[:len(trace.content)], trace.content[:len(query)]))
            score = score / math.sqrt(max(1, len(query))) * trace.strength
            scored.append((score, trace))
        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, trace in scored[:top_k]:
            trace.access_count += 1
            trace.strength = min(2.0, trace.strength + 0.05)
            trace.last_accessed = time.time()
            self._total_accesses += 1
            results.append(trace)
        return results

    def decay(self, dt: float) -> None:
        for trace in self._items:
            trace.strength *= (1.0 - NEURAL_CONSTANTS["working_memory_decay"] * dt)

    @property
    def utilization(self) -> float:
        return len(self._items) / self.slots


class EpisodicMemory:
    """Long-term episodic memory for events and experiences."""

    def __init__(self, capacity: int = 1000):
        self.capacity = capacity
        self._episodes: deque[MemoryTrace] = deque(maxlen=capacity)
        self._total_recalls = 0

    def store_episode(self, content: list[float], metadata: dict,
                      emotional_valence: float = 0.0) -> MemoryTrace:
        trace = MemoryTrace(
            content=content,
            metadata=metadata,
            memory_type=MemoryType.EPISODIC,
            emotional_valence=emotional_valence,
        )
        self._episodes.append(trace)
        return trace

    def recall(self, query: list[float], top_k: int = 5,
               time_decay: bool = True) -> list[MemoryTrace]:
        now = time.time()
        scored = []
        for ep in self._episodes:
            score = sum(q * c for q, c in zip(query[:len(ep.content)], ep.content[:len(query)]))
            score /= math.sqrt(max(1, len(query)))
            if time_decay:
                age_hours = (now - ep.created) / 3600
                recency = math.exp(-age_hours / 24)
                score *= (0.5 + 0.5 * recency)
            score *= ep.strength
            emotional_boost = abs(ep.emotional_valence) * 0.3
            score *= (1.0 + emotional_boost)
            scored.append((score, ep))
        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for _, ep in scored[:top_k]:
            ep.access_count += 1
            ep.strength = min(2.0, ep.strength + 0.02)
            ep.last_accessed = now
            self._total_recalls += 1
            results.append(ep)
        return results

    def consolidate(self, min_strength: float = 0.3) -> list[MemoryTrace]:
        consolidated = []
        remaining = deque(maxlen=self.capacity)
        for ep in self._episodes:
            if ep.strength >= min_strength:
                remaining.append(ep)
            else:
                consolidated.append(ep)
        self._episodes = remaining
        return consolidated


class SemanticMemory:
    """Long-term semantic memory for facts and knowledge."""

    def __init__(self):
        self._nodes: dict[str, MemoryTrace] = {}
        self._category_index: dict[str, list[str]] = {}
        self._total_concepts = 0

    def store_concept(self, key: str, content: list[float], category: str = "general",
                      confidence: float = 1.0) -> MemoryTrace:
        trace = MemoryTrace(
            content=content,
            metadata={"key": key, "category": category},
            memory_type=MemoryType.SEMANTIC,
            strength=confidence,
        )
        self._nodes[key] = trace
        if category not in self._category_index:
            self._category_index[category] = []
        if key not in self._category_index[category]:
            self._category_index[category].append(key)
        self._total_concepts += 1
        return trace

    def retrieve(self, key: str) -> MemoryTrace | None:
        if key in self._nodes:
            trace = self._nodes[key]
            trace.access_count += 1
            trace.strength = min(2.0, trace.strength + 0.05)
            trace.last_accessed = time.time()
            return trace
        return None

    def find_by_category(self, category: str) -> list[MemoryTrace]:
        keys = self._category_index.get(category, [])
        return [self._nodes[k] for k in keys if k in self._nodes]

    def find_similar(self, query: list[float], top_k: int = 5) -> list[tuple[str, float]]:
        scored = []
        for key, trace in self._nodes.items():
            score = sum(q * c for q, c in zip(query[:len(trace.content)], trace.content[:len(query)]))
            score /= math.sqrt(max(1, len(query)))
            scored.append((key, score * trace.strength))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


class ProceduralMemory:
    """Memory for procedures, skills, and action sequences."""

    def __init__(self):
        self._procedures: dict[str, dict] = {}
        self._total_executions = 0

    def store_procedure(self, name: str, steps: list[dict],
                        success_rate: float = 0.5) -> None:
        self._procedures[name] = {
            "steps": steps,
            "success_rate": success_rate,
            "execution_count": 0,
            "created": time.time(),
        }

    def execute(self, name: str, context: dict | None = None) -> dict | None:
        if name not in self._procedures:
            return None
        proc = self._procedures[name]
        proc["execution_count"] += 1
        self._total_executions += 1
        success = random.random() < proc["success_rate"]
        if success:
            proc["success_rate"] = min(1.0, proc["success_rate"] + 0.05)
        else:
            proc["success_rate"] = max(0.0, proc["success_rate"] - 0.1)
        return {"procedure": name, "success": success, "steps": proc["steps"]}

    def get_best_procedure(self, keyword: str) -> str | None:
        matching = [
            (name, proc) for name, proc in self._procedures.items()
            if keyword.lower() in name.lower()
        ]
        if not matching:
            return None
        matching.sort(key=lambda x: x[1]["success_rate"], reverse=True)
        return matching[0][0]


# ═══════════════════════════════════════════════════════════════════════════
#  EMOTION PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════

class EmotionProcessor:
    """Processes emotions using the Valence-Arousal-Dominance model."""

    def __init__(self, dim: int = 3):
        self.dim = dim
        self.state = [0.0, 0.0, 0.0]  # VAD
        self._target = [0.0, 0.0, 0.0]
        self._emotion_history: deque[dict] = deque(maxlen=50)
        self._emotional_memory: dict[str, list[float]] = {}

    def process_input(self, text: str) -> list[float]:
        text_lower = text.lower()
        valence = 0.0
        arousal = 0.0
        dominance = 0.0

        positive = ["happy", "love", "great", "awesome", "excited", "wonderful", "amazing",
                     "thanks", "thank", "appreciate", "good", "nice", "cool", "excellent"]
        negative = ["sad", "depressed", "lonely", "miss", "cry", "upset", "worried",
                     "anxious", "nervous", "scared", "afraid", "bad", "terrible", "hate"]
        calming = ["calm", "peace", "relax", "gentle", "quiet", "serene"]
        exciting = ["urgent", "quick", "fast", "hurry", "now", "immediately", "run"]

        for word in text_lower.split():
            if word in positive:
                valence += 0.3
            elif word in negative:
                valence -= 0.3
            if word in calming:
                arousal -= 0.2
            elif word in exciting:
                arousal += 0.2

        if "?" in text:
            dominance -= 0.1
        elif "!" in text:
            arousal += 0.1

        self._target = [
            max(-1.0, min(1.0, valence)),
            max(-1.0, min(1.0, arousal)),
            max(-1.0, min(1.0, dominance)),
        ]

        return self._target

    def update(self, dt: float = 0.01) -> list[float]:
        rate = NEURAL_CONSTANTS["emotion_decay_rate"]
        for i in range(self.dim):
            diff = self._target[i] - self.state[i]
            self.state[i] += diff * rate * dt * 10
            self.state[i] *= (1.0 - rate * dt)
            self.state[i] = max(-1.0, min(1.0, self.state[i]))
        return self.state[:]

    def get_mood_label(self) -> str:
        v, a, d = self.state
        if v > 0.3 and a > 0.3:
            return "excited"
        elif v > 0.3 and a < -0.3:
            return "serene"
        elif v > 0.3:
            return "happy"
        elif v < -0.3 and a > 0.3:
            return "angry"
        elif v < -0.3 and a < -0.3:
            return "sad"
        elif v < -0.3:
            return "unhappy"
        elif a > 0.3:
            return "alert"
        elif a < -0.3:
            return "calm"
        return "neutral"

    def get_emotion_vector(self) -> list[float]:
        return self.state[:]

    def influence_response(self, response: str, intensity: float = 0.3) -> str:
        mood = self.get_mood_label()
        modifiers = {
            "happy": ["! ", "That's great! ", "Wonderful! "],
            "excited": ["! ", "Amazing! ", "Fantastic! "],
            "sad": ["...", "I understand...", "That's tough..."],
            "calm": ["Okay. ", "I see. ", ""],
            "angry": ["This needs attention. ", ""],
            "serene": ["Peacefully. ", ""],
            "neutral": [""],
        }
        prefix = random.choice(modifiers.get(mood, [""]))
        if random.random() < intensity:
            return prefix + response
        return response

    def store_emotional_context(self, key: str) -> None:
        self._emotional_memory[key] = self.state[:]

    def recall_emotional_context(self, key: str) -> list[float] | None:
        return self._emotional_memory.get(key)


# ═══════════════════════════════════════════════════════════════════════════
#  DECISION MAKER
# ═══════════════════════════════════════════════════════════════════════════

class DecisionMaker:
    """Multi-criteria decision making with multiple strategies."""

    def __init__(self, strategy: DecisionStrategy = DecisionStrategy.WEIGHTED_VOTE):
        self.strategy = strategy
        self._decision_history: deque[dict] = deque(maxlen=200)
        self._criteria_weights: dict[str, float] = {
            "relevance": 0.25,
            "confidence": 0.20,
            "emotional_fit": 0.15,
            "novelty": 0.10,
            "consistency": 0.10,
            "efficiency": 0.10,
            "safety": 0.10,
        }
        self._total_decisions = 0
        self._correct_decisions = 0

    def evaluate_options(self, options: list[dict], context: dict | None = None) -> dict:
        if not options:
            return {"selected": None, "confidence": 0.0}

        scored_options = []
        for option in options:
            scores = {}
            for criterion, weight in self._criteria_weights.items():
                scores[criterion] = option.get("scores", {}).get(criterion, 0.5) * weight
            total_score = sum(scores.values())
            scored_options.append({
                "option": option,
                "total_score": total_score,
                "scores": scores,
            })

        if self.strategy == DecisionStrategy.WEIGHTED_VOTE:
            scored_options.sort(key=lambda x: x["total_score"], reverse=True)
            selected = scored_options[0]
        elif self.strategy == DecisionStrategy.SOFTMAX:
            scores = [o["total_score"] for o in scored_options]
            max_s = max(scores) if scores else 0
            exps = [math.exp(s - max_s) for s in scores]
            total = sum(exps) or 1.0
            probs = [e / total for e in exps]
            idx = random.choices(range(len(scored_options)), weights=probs, k=1)[0]
            selected = scored_options[idx]
        elif self.strategy == DecisionStrategy.CONSENSUS:
            avg_score = sum(o["total_score"] for o in scored_options) / len(scored_options)
            consensus = [o for o in scored_options if o["total_score"] > avg_score]
            selected = consensus[0] if consensus else scored_options[0]
        else:
            selected = max(scored_options, key=lambda x: x["total_score"])

        self._total_decisions += 1
        decision_record = {
            "timestamp": time.time(),
            "num_options": len(options),
            "selected_score": selected["total_score"],
            "strategy": self.strategy.value,
        }
        self._decision_history.append(decision_record)

        return {
            "selected": selected["option"],
            "confidence": min(1.0, selected["total_score"]),
            "all_scores": [(o["option"].get("label", "?"), o["total_score"]) for o in scored_options],
        }

    def update_weights(self, feedback: dict) -> None:
        for criterion, adjustment in feedback.items():
            if criterion in self._criteria_weights:
                self._criteria_weights[criterion] = max(
                    0.01, min(0.5, self._criteria_weights[criterion] + adjustment)
                )
        total = sum(self._criteria_weights.values())
        for k in self._criteria_weights:
            self._criteria_weights[k] /= total

    def get_stats(self) -> dict:
        return {
            "total_decisions": self._total_decisions,
            "strategy": self.strategy.value,
            "criteria_weights": dict(self._criteria_weights),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  HOMEOSTASIS
# ═══════════════════════════════════════════════════════════════════════════

class Homeostasis:
    """Maintains internal balance of the neural system."""

    def __init__(self):
        self._setpoints = {
            "activation_level": 0.3,
            "memory_utilization": 0.5,
            "emotion_intensity": 0.3,
            "learning_rate": 0.01,
            "novelty-seeking": 0.5,
        }
        self._current = dict(self._setpoints)
        self._deviation_history: deque[dict] = deque(maxlen=100)

    def get_deviation(self, metric: str) -> float:
        if metric not in self._setpoints:
            return 0.0
        return self._current.get(metric, 0) - self._setpoints[metric]

    def adjust(self, metric: str, delta: float) -> None:
        if metric in self._current:
            self._current[metric] = max(0.0, min(1.0, self._current[metric] + delta))

    def update(self, dt: float = 0.01) -> None:
        rate = NEURAL_CONSTANTS["homeostasis_rate"]
        for metric in self._setpoints:
            deviation = self.get_deviation(metric)
            if abs(deviation) > 0.1:
                correction = -deviation * rate * dt * 10
                self._current[metric] = max(0.0, min(1.0, self._current[metric] + correction))
                self._deviation_history.append({
                    "timestamp": time.time(),
                    "metric": metric,
                    "deviation": deviation,
                    "correction": correction,
                })

    def get_state(self) -> dict:
        return {k: {"current": v, "setpoint": self._setpoints[k], "deviation": v - self._setpoints[k]}
                for k, v in self._current.items()}


# ═══════════════════════════════════════════════════════════════════════════
#  METACOGNITION
# ═══════════════════════════════════════════════════════════════════════════

class Metacognition:
    """Self-monitoring and self-regulation of cognitive processes."""

    def __init__(self):
        self._monitoring_data: deque[dict] = deque(maxlen=200)
        self._confidence_history: deque[float] = deque(maxlen=100)
        self._error_detection_count = 0
        self._self_correction_count = 0

    def monitor_process(self, process_name: str, input_hash: str,
                        output_quality: float, confidence: float) -> dict:
        record = {
            "timestamp": time.time(),
            "process": process_name,
            "input_hash": input_hash,
            "quality": output_quality,
            "confidence": confidence,
        }
        self._monitoring_data.append(record)
        self._confidence_history.append(confidence)

        if output_quality < 0.3:
            self._error_detection_count += 1

        return record

    def get_confidence_trend(self) -> str:
        if len(self._confidence_history) < 5:
            return "insufficient_data"
        recent = list(self._confidence_history)[-10:]
        older = list(self._confidence_history)[-20:-10] if len(self._confidence_history) >= 20 else recent
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older)
        if avg_recent > avg_older + 0.05:
            return "improving"
        elif avg_recent < avg_older - 0.05:
            return "declining"
        return "stable"

    def should_retry(self, last_confidence: float) -> bool:
        return last_confidence < 0.4

    def get_stats(self) -> dict:
        avg_conf = sum(self._confidence_history) / len(self._confidence_history) if self._confidence_history else 0
        return {
            "total_monitored": len(self._monitoring_data),
            "avg_confidence": avg_conf,
            "confidence_trend": self.get_confidence_trend(),
            "errors_detected": self._error_detection_count,
            "self_corrections": self._self_correction_count,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  DREAM CONSOLIDATOR
# ═══════════════════════════════════════════════════════════════════════════

class DreamConsolidator:
    """Background consolidation of memories during idle periods."""

    def __init__(self):
        self._consolidation_queue: deque[MemoryTrace] = deque(maxlen=500)
        self._consolidated_count = 0
        self._last_consolidation = time.time()

    def queue_for_consolidation(self, trace: MemoryTrace) -> None:
        self._consolidation_queue.append(trace)

    def consolidate_batch(self, batch_size: int = 10) -> list[dict]:
        results = []
        batch = []
        while self._consolidation_queue and len(batch) < batch_size:
            batch.append(self._consolidation_queue.popleft())

        for trace in batch:
            trace.strength *= 1.2
            trace.access_count += 1
            self._consolidated_count += 1
            results.append({
                "type": trace.memory_type.value,
                "strength_after": trace.strength,
                "metadata": trace.metadata,
            })

        self._last_consolidation = time.time()
        return results

    @property
    def pending_count(self) -> int:
        return len(self._consolidation_queue)

    def get_stats(self) -> dict:
        return {
            "pending": self.pending_count,
            "consolidated": self._consolidated_count,
            "last_consolidation": self._last_consolidation,
        }


# ═══════════════════════════════════════════════════════════════════════════
#  TEMPORAL PROCESSOR
# ═══════════════════════════════════════════════════════════════════════════

class TemporalProcessor:
    """Handles sequence processing and timing."""

    def __init__(self, window_size: int = 20):
        self.window_size = window_size
        self._sequence_buffer: deque[list[float]] = deque(maxlen=window_size)
        self._timestamps: deque[float] = deque(maxlen=window_size)
        self._pattern_buffer: deque[str] = deque(maxlen=window_size)

    def add_step(self, values: list[float], label: str = "") -> None:
        self._sequence_buffer.append(values)
        self._timestamps.append(time.time())
        self._pattern_buffer.append(label)

    def get_sequence(self, length: int | None = None) -> list[list[float]]:
        if length is None:
            return list(self._sequence_buffer)
        return list(self._sequence_buffer)[-length:]

    def detect_repetition(self) -> str | None:
        if len(self._pattern_buffer) < 3:
            return None
        recent = list(self._pattern_buffer)[-6:]
        for window in range(2, len(recent) // 2 + 1):
            pattern = recent[-window:]
            matches = sum(
                1 for i in range(len(recent) - window)
                if recent[i:i+window] == pattern
            )
            if matches >= 2:
                return "-".join(pattern)
        return None

    def get_intervals(self) -> list[float]:
        timestamps = list(self._timestamps)
        if len(timestamps) < 2:
            return []
        return [timestamps[i+1] - timestamps[i] for i in range(len(timestamps) - 1)]

    def predict_next(self) -> list[float] | None:
        if len(self._sequence_buffer) < 3:
            return None
        recent = list(self._sequence_buffer)[-3:]
        dim = len(recent[0]) if recent[0] else 0
        predicted = [0.0] * dim
        for i in range(dim):
            values = [step[i] for step in recent if i < len(step)]
            if values:
                predicted[i] = sum(values) / len(values)
        return predicted


# ═══════════════════════════════════════════════════════════════════════════
#  ASSOCIATIVE MEMORY
# ═══════════════════════════════════════════════════════════════════════════

class AssociativeMemory:
    """Links related concepts and enables spreading activation."""

    def __init__(self):
        self._nodes: dict[str, dict] = {}
        self._associations: dict[str, dict[str, float]] = {}
        self._activation_levels: dict[str, float] = {}

    def add_concept(self, key: str, content: list[float], category: str = "general") -> None:
        self._nodes[key] = {"content": content, "category": category, "created": time.time()}
        if key not in self._associations:
            self._associations[key] = {}
        if key not in self._activation_levels:
            self._activation_levels[key] = 0.0

    def associate(self, key1: str, key2: str, strength: float = 0.5) -> None:
        if key1 not in self._associations:
            self._associations[key1] = {}
        if key2 not in self._associations:
            self._associations[key2] = {}
        self._associations[key1][key2] = strength
        self._associations[key2][key1] = strength

    def activate(self, key: str, amount: float = 1.0) -> None:
        if key in self._activation_levels:
            self._activation_levels[key] = min(1.0, self._activation_levels[key] + amount)

    def spread_activation(self, decay: float = 0.5, rounds: int = 2) -> dict[str, float]:
        for _ in range(rounds):
            new_activation = dict(self._activation_levels)
            for key, level in self._activation_levels.items():
                if level > 0.1:
                    for assoc_key, strength in self._associations.get(key, {}).items():
                        spread = level * strength * decay
                        new_activation[assoc_key] = min(
                            1.0, new_activation.get(assoc_key, 0.0) + spread
                        )
            self._activation_levels = new_activation
        return dict(self._activation_levels)

    def get_most_active(self, top_k: int = 5) -> list[tuple[str, float]]:
        sorted_nodes = sorted(
            self._activation_levels.items(), key=lambda x: x[1], reverse=True
        )
        return sorted_nodes[:top_k]

    def find_associations(self, key: str, min_strength: float = 0.1) -> list[tuple[str, float]]:
        if key not in self._associations:
            return []
        assocs = self._associations[key]
        return sorted(
            [(k, v) for k, v in assocs.items() if v >= min_strength],
            key=lambda x: x[1], reverse=True
        )

    def decay_all(self, rate: float = 0.1) -> None:
        for key in self._activation_levels:
            self._activation_levels[key] *= (1.0 - rate)
            if self._activation_levels[key] < 0.01:
                self._activation_levels[key] = 0.0


# ═══════════════════════════════════════════════════════════════════════════
#  NEURAL CORE
# ═══════════════════════════════════════════════════════════════════════════

class NeuralCore:
    """The fundamental nervous system of Purple Ultra AI.

    Orchestrates all neural processing:
    - Signal routing between processing units
    - Attention-based selective processing
    - Multi-system memory management
    - Emotion-driven response modulation
    - Decision making with multiple strategies
    - Homeostatic balance maintenance
    - Metacognitive self-monitoring
    - Background dream consolidation
    - Temporal sequence processing
    - Associative concept spreading
    """

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "neural_core"
        )
        os.makedirs(self.data_dir, exist_ok=True)

        self.working_memory = WorkingMemory()
        self.episodic_memory = EpisodicMemory()
        self.semantic_memory = SemanticMemory()
        self.procedural_memory = ProceduralMemory()
        self.attention = AttentionMechanism()
        self.emotion = EmotionProcessor()
        self.decision_maker = DecisionMaker()
        self.homeostasis = Homeostasis()
        self.metacognition = Metacognition()
        self.dream = DreamConsolidator()
        self.temporal = TemporalProcessor()
        self.associative = AssociativeMemory()

        self._processing_units: dict[str, ProcessingUnit] = {}
        self._pathways: list[NeuralPathway] = []
        self._signal_queue: deque[Signal] = deque(maxlen=500)
        self._processed_signals: deque[Signal] = deque(maxlen=200)

        self._total_processing_cycles = 0
        self._total_signals_processed = 0
        self._total_learning_events = 0
        self._session_start = time.time()

        self._init_units()
        self._init_pathways()

    def _init_units(self) -> None:
        unit_configs = [
            ("input_encoder", 32),
            ("intent_detector", 16),
            ("emotion_analyzer", 8),
            ("memory_indexer", 24),
            ("reasoning_engine", 32),
            ("response_generator", 32),
            ("output_decoder", 16),
            ("metacog_monitor", 8),
        ]
        for unit_id, dim in unit_configs:
            self._processing_units[unit_id] = ProcessingUnit(unit_id, dim)

    def _init_pathways(self) -> None:
        connections = [
            ("input_encoder", "intent_detector", 32, 16),
            ("input_encoder", "emotion_analyzer", 32, 8),
            ("input_encoder", "memory_indexer", 32, 24),
            ("intent_detector", "reasoning_engine", 16, 32),
            ("emotion_analyzer", "reasoning_engine", 8, 32),
            ("memory_indexer", "reasoning_engine", 24, 32),
            ("reasoning_engine", "response_generator", 32, 32),
            ("response_generator", "output_decoder", 32, 16),
            ("metacog_monitor", "reasoning_engine", 8, 32),
        ]
        for src, dst, in_dim, out_dim in connections:
            weights = [[random.gauss(0, 0.1) for _ in range(out_dim)] for _ in range(in_dim)]
            pathway = NeuralPathway(src, dst, weights)
            self._pathways.append(pathway)

    def process_signal(self, signal: Signal) -> Signal:
        self._signal_queue.append(signal)
        current = signal

        for pathway in self._pathways:
            if pathway.source_id == current.destination or pathway.source_id == signal.source:
                current = pathway.transmit(current)

        self._processed_signals.append(current)
        self._total_signals_processed += 1
        return current

    def attend(self, signal: Signal, context: list[list[float]] | None = None) -> Signal:
        return self.attention.focus(signal, context)

    def think(self, user_input: str, context: dict | None = None) -> dict:
        self._total_processing_cycles += 1
        start_time = time.time()

        input_signal = Signal(
            signal_type=SignalType.INPUT,
            values=[ord(c) / 127.0 for c in user_input[:32]],
            source="user",
            destination="input_encoder",
        )

        encoded = self.process_signal(input_signal)
        attended = self.attend(encoded)

        self.emotion.process_input(user_input)
        self.emotion.update()

        wm_trace = self.working_memory.store(
            attended.values,
            metadata={"input": user_input[:100]},
            emotional_valence=self.emotion.state[0],
        )

        for unit in self._processing_units.values():
            unit.receive(attended)
            unit.process()

        episodic_matches = self.episodic_memory.recall(attended.values, top_k=3)
        semantic_matches = self.semantic_memory.find_similar(attended.values, top_k=3)

        options = []
        for em in episodic_matches:
            options.append({
                "label": f"episodic_{em.metadata.get('input', '')[:20]}",
                "scores": {"relevance": 0.5, "confidence": em.strength * 0.5,
                           "emotional_fit": 0.5, "novelty": 0.3, "consistency": 0.6,
                           "efficiency": 0.7, "safety": 0.9},
            })
        for sm in semantic_matches:
            options.append({
                "label": f"semantic_{sm[0]}",
                "scores": {"relevance": sm[1] * 0.5, "confidence": 0.6,
                           "emotional_fit": 0.5, "novelty": 0.4, "consistency": 0.7,
                           "efficiency": 0.6, "safety": 0.9},
            })

        decision = self.decision_maker.evaluate_options(options) if options else {"selected": None, "confidence": 0.5}

        self.temporal.add_step(attended.values, label=user_input[:20])

        self.associative.activate(user_input[:20])
        self.associative.spread_activation()

        self.homeostasis.update()

        self.metacognition.monitor_process(
            "think",
            hashlib.md5(user_input.encode()).hexdigest()[:8],
            decision.get("confidence", 0.5),
            decision.get("confidence", 0.5),
        )

        processing_time = (time.time() - start_time) * 1000

        self.dream.queue_for_consolidation(wm_trace)
        if self._total_processing_cycles % NEURAL_CONSTANTS["dream_consolidation_interval"] == 0:
            self.dream.consolidate_batch()

        return {
            "attended_values": attended.values,
            "emotion_state": self.emotion.get_emotion_vector(),
            "mood_label": self.emotion.get_mood_label(),
            "working_memory_utilization": self.working_memory.utilization,
            "episodic_matches": len(episodic_matches),
            "semantic_matches": len(semantic_matches),
            "decision": decision,
            "repetition_detected": self.temporal.detect_repetition(),
            "confidence_trend": self.metacognition.get_confidence_trend(),
            "processing_time_ms": processing_time,
            "homeostasis": self.homeostasis.get_state(),
        }

    def learn_association(self, key1: str, key2: str, strength: float = 0.5) -> None:
        self.associative.associate(key1, key2, strength)
        self.semantic_memory.store_concept(key1, [random.gauss(0, 0.1) for _ in range(16)], "learned")
        self.semantic_memory.store_concept(key2, [random.gauss(0, 0.1) for _ in range(16)], "learned")
        self._total_learning_events += 1

    def store_episode(self, content: str, metadata: dict | None = None,
                      emotional_valence: float = 0.0) -> None:
        values = [ord(c) / 127.0 for c in content[:32]]
        values = values + [0.0] * max(0, 32 - len(values))
        self.episodic_memory.store_episode(values, metadata or {"text": content[:100]}, emotional_valence)

    def store_knowledge(self, key: str, content: str, category: str = "general") -> None:
        values = [ord(c) / 127.0 for c in content[:32]]
        values = values + [0.0] * max(0, 32 - len(values))
        self.semantic_memory.store_concept(key, values, category)
        self.associative.add_concept(key, values, category)

    def store_procedure(self, name: str, steps: list[dict]) -> None:
        self.procedural_memory.store_procedure(name, steps)

    def execute_procedure(self, name: str) -> dict | None:
        return self.procedural_memory.execute(name)

    def get_stats(self) -> dict:
        uptime = time.time() - self._session_start
        return {
            "uptime_seconds": uptime,
            "processing_cycles": self._total_processing_cycles,
            "signals_processed": self._total_signals_processed,
            "learning_events": self._total_learning_events,
            "processing_units": len(self._processing_units),
            "pathways": len(self._pathways),
            "working_memory": {
                "utilization": self.working_memory.utilization,
                "items": len(self.working_memory._items),
                "slots": self.working_memory.slots,
            },
            "episodic_memory": {
                "episodes": len(self.episodic_memory._episodes),
                "capacity": self.episodic_memory.capacity,
            },
            "semantic_memory": {
                "concepts": self.semantic_memory._total_concepts,
                "categories": list(self.semantic_memory._category_index.keys()),
            },
            "procedural_memory": {
                "procedures": len(self.procedural_memory._procedures),
                "executions": self.procedural_memory._total_executions,
            },
            "emotion": {
                "mood": self.emotion.get_mood_label(),
                "state": self.emotion.get_emotion_vector(),
            },
            "metacognition": self.metacognition.get_stats(),
            "dream": self.dream.get_stats(),
            "homeostasis": self.homeostasis.get_state(),
            "associative_memory": {
                "concepts": len(self.associative._nodes),
                "associations": sum(len(a) for a in self.associative._associations.values()),
            },
        }

    def save(self) -> None:
        meta = {
            "total_processing_cycles": self._total_processing_cycles,
            "total_signals_processed": self._total_signals_processed,
            "total_learning_events": self._total_learning_events,
        }
        with open(os.path.join(self.data_dir, "neural_core_meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

    def _load(self) -> None:
        try:
            meta_path = os.path.join(self.data_dir, "neural_core_meta.json")
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)
                self._total_processing_cycles = meta.get("total_processing_cycles", 0)
                self._total_signals_processed = meta.get("total_signals_processed", 0)
                self._total_learning_events = meta.get("total_learning_events", 0)
        except Exception:
            pass
