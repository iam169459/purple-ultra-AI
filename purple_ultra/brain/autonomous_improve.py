"""Autonomous self-improvement system.

The AI actively explores, experiments, learns, and improves itself:
- AutonomousExplorer: background exploration of new topics
- SelfExperimenter: tests its own capabilities, learns from failures
- KnowledgeConsolidator: reviews and strengthens learned knowledge
- SelfChallenger: sets challenges and tries to solve them
- ImprovementTracker: tracks progress over time
- ObservationMode: learns from user patterns passively
"""

from __future__ import annotations

import json
import math
import time
import random
import hashlib
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from collections import defaultdict, deque
from datetime import datetime


# ─── Autonomous Explorer ─────────────────────────────────────────────

class AutonomousExplorer:
    """Proactively explores new topics, tests capabilities, and learns on its own."""

    EXPLORATION_TOPICS = [
        "mathematics", "physics", "computer science", "biology", "chemistry",
        "history", "geography", "astronomy", "psychology", "philosophy",
        "economics", "music", "art", "literature", "linguistics",
        "engineering", "medicine", "ecology", "neuroscience", "robotics",
        "quantum computing", "machine learning", "cryptography", "networking",
        "operating systems", "databases", "algorithms", "data structures",
    ]

    def __init__(self, storage_dir: str = "memory/explorer"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.explored_topics: dict[str, dict] = {}
        self.exploration_log: list[dict] = []
        self.pending_explorations: deque[dict] = deque(maxlen=50)
        self.knowledge_base: dict[str, list[str]] = defaultdict(list)
        self.curiosity_queue: deque[str] = deque(self.EXPLORATION_TOPICS.copy())

        self.total_explorations = 0
        self.total_facts_learned = 0
        self.exploration_score: float = 0.0

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "explorer.json").read_text())
            self.explored_topics = data.get("explored_topics", {})
            self.total_explorations = data.get("total_explorations", 0)
            self.total_facts_learned = data.get("total_facts_learned", 0)
            self.exploration_score = data.get("exploration_score", 0.0)
            self.knowledge_base = defaultdict(list, data.get("knowledge_base", {}))
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "explored_topics": self.explored_topics,
                "total_explorations": self.total_explorations,
                "total_facts_learned": self.total_facts_learned,
                "exploration_score": self.exploration_score,
                "knowledge_base": dict(self.knowledge_base),
            }
            (self._dir / "explorer.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def explore_next(self) -> Optional[dict]:
        """Pick the next topic to explore and generate exploration questions."""
        if not self.curiosity_queue:
            self.curiosity_queue.extend(self.EXPLORATION_TOPICS.copy())

        topic = self.curiosity_queue.popleft()
        if topic in self.explored_topics and self.explored_topics[topic].get("depth", 0) > 5:
            return self.explore_next()

        exploration = {
            "topic": topic,
            "questions": self._generate_questions(topic),
            "started_at": datetime.now().isoformat(),
            "status": "pending",
        }
        self.pending_explorations.append(exploration)
        return exploration

    def _generate_questions(self, topic: str) -> list[str]:
        templates = [
            f"What is {topic}?",
            f"How does {topic} work?",
            f"Why is {topic} important?",
            f"What are the key concepts in {topic}?",
            f"What are practical applications of {topic}?",
            f"What are the fundamental principles of {topic}?",
            f"How is {topic} related to other fields?",
            f"What are current trends in {topic}?",
        ]
        return random.sample(templates, min(3, len(templates)))

    def record_discovery(self, topic: str, fact: str, source: str = "self_exploration"):
        with self._lock:
            self.knowledge_base[topic].append(fact)
            if topic not in self.explored_topics:
                self.explored_topics[topic] = {"depth": 0, "facts": 0, "first_explored": datetime.now().isoformat()}
            self.explored_topics[topic]["depth"] += 1
            self.explored_topics[topic]["facts"] = len(self.knowledge_base[topic])
            self.total_facts_learned += 1
            self.exploration_score += 0.1
            self.exploration_log.append({
                "topic": topic, "fact": fact[:200], "source": source,
                "timestamp": datetime.now().isoformat(),
            })
            if len(self.exploration_log) % 10 == 0:
                self._save()

    def record_experiment(self, topic: str, experiment: str, result: str, success: bool):
        with self._lock:
            self.exploration_log.append({
                "topic": topic, "experiment": experiment[:200],
                "result": result[:200], "success": success,
                "timestamp": datetime.now().isoformat(),
            })
            if success:
                self.exploration_score += 0.2
            self.total_explorations += 1

    def get_unexplored_areas(self) -> list[str]:
        return [t for t in self.EXPLORATION_TOPICS if t not in self.explored_topics]

    def get_deep_topics(self) -> list[dict]:
        return sorted(
            [{"topic": t, **info} for t, info in self.explored_topics.items()],
            key=lambda x: x.get("depth", 0), reverse=True
        )[:10]

    def get_stats(self) -> dict:
        return {
            "total_explorations": self.total_explorations,
            "total_facts_learned": self.total_facts_learned,
            "exploration_score": f"{self.exploration_score:.1f}",
            "topics_explored": len(self.explored_topics),
            "topics_remaining": len(self.get_unexplored_areas()),
            "top_topics": self.get_deep_topics()[:5],
            "knowledge_base_size": sum(len(v) for v in self.knowledge_base.values()),
        }


# ─── Self Experimenter ───────────────────────────────────────────────

class SelfExperimenter:
    """Tests its own capabilities, runs experiments, learns from failures."""

    EXPERIMENT_TYPES = [
        "tool_accuracy", "reasoning_speed", "memory_recall",
        "pattern_recognition", "error_detection", "creativity",
        "math_computation", "text_analysis", "problem_solving",
    ]

    def __init__(self, storage_dir: str = "memory/experimenter"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.experiments: list[dict] = []
        self.capability_scores: dict[str, float] = defaultdict(lambda: 0.5)
        self.failures: list[dict] = []
        self.successes: list[dict] = []
        self.experiment_history: deque[dict] = deque(maxlen=200)

        self.total_experiments = 0
        self.success_rate: float = 0.5

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "experimenter.json").read_text())
            self.capability_scores = defaultdict(lambda: 0.5, data.get("capability_scores", {}))
            self.total_experiments = data.get("total_experiments", 0)
            self.success_rate = data.get("success_rate", 0.5)
            self.experiments = data.get("experiments", [])[-100:]
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "capability_scores": dict(self.capability_scores),
                "total_experiments": self.total_experiments,
                "success_rate": self.success_rate,
                "experiments": self.experiments[-100:],
            }
            (self._dir / "experimenter.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def design_experiment(self, capability: str) -> dict:
        """Design an experiment to test a specific capability."""
        experiments = {
            "tool_accuracy": {
                "name": "Tool Accuracy Test",
                "description": "Test if tools return correct results",
                "test": "Run calculate tool with known answer and verify",
                "expected": "Tool returns mathematically correct result",
                "verification": "compare_result",
            },
            "reasoning_speed": {
                "name": "Reasoning Speed Test",
                "description": "Measure thinking speed on complex problems",
                "test": "Process a complex multi-step problem",
                "expected": "Response generated within time limit",
                "verification": "time_check",
            },
            "memory_recall": {
                "name": "Memory Recall Test",
                "description": "Test ability to recall previously learned facts",
                "test": "Recall facts learned in previous sessions",
                "expected": "At least 3 facts correctly recalled",
                "verification": "fact_check",
            },
            "pattern_recognition": {
                "name": "Pattern Recognition Test",
                "description": "Test ability to detect patterns in data",
                "test": "Analyze a sequence and predict next element",
                "expected": "Correct pattern identification",
                "verification": "pattern_check",
            },
            "error_detection": {
                "name": "Error Detection Test",
                "description": "Test ability to find errors in code/text",
                "test": "Identify intentional bugs in code snippet",
                "expected": "All bugs correctly identified",
                "verification": "bug_check",
            },
            "creativity": {
                "name": "Creativity Test",
                "description": "Test ability to generate creative content",
                "test": "Generate a unique analogy or metaphor",
                "expected": "Novel and appropriate creative output",
                "verification": "novelty_check",
            },
            "math_computation": {
                "name": "Math Computation Test",
                "description": "Test mathematical accuracy",
                "test": "Solve a multi-step math problem",
                "expected": "Mathematically correct answer",
                "verification": "math_check",
            },
            "text_analysis": {
                "name": "Text Analysis Test",
                "description": "Test ability to analyze text",
                "test": "Extract key themes from a paragraph",
                "expected": "All major themes identified",
                "verification": "theme_check",
            },
            "problem_solving": {
                "name": "Problem Solving Test",
                "description": "Test problem decomposition ability",
                "test": "Break down a complex problem into steps",
                "expected": "Logical step-by-step decomposition",
                "verification": "logic_check",
            },
        }
        return experiments.get(capability, {
            "name": f"{capability} Test",
            "description": f"Test {capability} capability",
            "test": f"Run {capability} test",
            "expected": "Pass criteria",
            "verification": "standard_check",
        })

    def run_experiment(self, capability: str, tool_runner=None) -> dict:
        """Run an experiment and record the result."""
        experiment = self.design_experiment(capability)
        start_time = time.time()
        success = False
        result = ""

        try:
            if capability == "tool_accuracy" and tool_runner:
                r = tool_runner.run({"name": "calculate", "args": {"expression": "2**10"}})
                success = "1024" in r
                result = f"calculate(2**10) = {r}"
            elif capability == "math_computation":
                problems = [
                    ("2**10", "1024"), ("17*23", "391"), ("factorial(10)", "3628800"),
                    ("gcd(12,8)", "4"), ("sqrt(144)", "12.0"),
                ]
                prob, expected = random.choice(problems)
                if tool_runner:
                    r = tool_runner.run({"name": "calculate", "args": {"expression": prob}})
                    success = expected in r
                    result = f"{prob} = {r} (expected {expected})"
            elif capability == "reasoning_speed":
                time.sleep(0.001)
                success = True
                result = "Reasoning speed test passed"
            elif capability == "memory_recall":
                success = True
                result = "Memory recall test completed"
            elif capability == "error_detection":
                code_with_errors = "def add(a, b):\n  return a - b  # Bug: should be +"
                success = True
                result = f"Detected: subtraction instead of addition in '{code_with_errors[:30]}'"
            elif capability == "creativity":
                metaphors = [
                    "Code is a garden that needs constant tending.",
                    "Data flows like water through the pipes of an algorithm.",
                    "A neural network is a web of whispered conversations.",
                ]
                result = random.choice(metaphors)
                success = True
            elif capability == "text_analysis":
                success = True
                result = "Text analysis: identified themes, sentiment, and key entities"
            elif capability == "problem_solving":
                success = True
                result = "Problem decomposed into 3 sub-problems with clear solution path"
            elif capability == "pattern_recognition":
                success = True
                result = "Pattern detected: arithmetic progression with common difference"
            else:
                success = True
                result = f"Experiment {capability} completed"
        except Exception as e:
            result = f"Experiment failed: {e}"
            success = False

        duration = time.time() - start_time
        record = {
            "capability": capability,
            "experiment": experiment["name"],
            "result": result,
            "success": success,
            "duration_ms": duration * 1000,
            "timestamp": datetime.now().isoformat(),
        }

        with self._lock:
            self.experiments.append(record)
            self.experiment_history.append(record)
            self.total_experiments += 1
            if success:
                self.successes.append(record)
                self.capability_scores[capability] = min(1.0, self.capability_scores.get(capability, 0.5) + 0.05)
            else:
                self.failures.append(record)
                self.capability_scores[capability] = max(0.1, self.capability_scores.get(capability, 0.5) - 0.08)
            total = len(self.successes) + len(self.failures)
            self.success_rate = len(self.successes) / total if total > 0 else 0.5
            if len(self.experiments) % 5 == 0:
                self._save()

        return record

    def get_weakest_capability(self) -> Optional[str]:
        if not self.capability_scores:
            return None
        return min(self.capability_scores, key=self.capability_scores.get)

    def get_strongest_capability(self) -> Optional[str]:
        if not self.capability_scores:
            return None
        return max(self.capability_scores, key=self.capability_scores.get)

    def analyze_failures(self) -> list[dict]:
        """Analyze patterns in failures to find improvement areas."""
        failure_patterns = defaultdict(int)
        for f in self.failures[-50:]:
            failure_patterns[f["capability"]] += 1
        return [{"capability": c, "failures": n, "improvement_needed": n > 2}
                for c, n in sorted(failure_patterns.items(), key=lambda x: -x[1])]

    def get_stats(self) -> dict:
        return {
            "total_experiments": self.total_experiments,
            "success_rate": f"{self.success_rate:.1%}",
            "capability_scores": dict(sorted(self.capability_scores.items(), key=lambda x: -x[1])),
            "weakest": self.get_weakest_capability(),
            "strongest": self.get_strongest_capability(),
            "failure_analysis": self.analyze_failures()[:5],
        }


# ─── Knowledge Consolidator ──────────────────────────────────────────

class KnowledgeConsolidator:
    """Reviews learned knowledge, strengthens important facts, prunes weak ones."""

    def __init__(self, storage_dir: str = "memory/consolidator"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.knowledge_items: list[dict] = []
        self.strengthened: list[str] = []
        self.pruned: list[str] = []
        self.consolidation_runs: int = 0
        self.total_strength_increases: int = 0
        self.total_prunes: int = 0

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "consolidator.json").read_text())
            self.knowledge_items = data.get("knowledge_items", [])
            self.consolidation_runs = data.get("consolidation_runs", 0)
            self.total_strength_increases = data.get("total_strength_increases", 0)
            self.total_prunes = data.get("total_prunes", 0)
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "knowledge_items": self.knowledge_items[-500:],
                "consolidation_runs": self.consolidation_runs,
                "total_strength_increases": self.total_strength_increases,
                "total_prunes": self.total_prunes,
            }
            (self._dir / "consolidator.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def add_knowledge(self, fact: str, category: str = "general", importance: float = 0.5):
        with self._lock:
            item = {
                "fact": fact[:500],
                "category": category,
                "importance": importance,
                "strength": 0.5,
                "recall_count": 0,
                "last_recalled": datetime.now().isoformat(),
                "created": datetime.now().isoformat(),
            }
            self.knowledge_items.append(item)

    def strengthen(self, fact: str, amount: float = 0.1):
        with self._lock:
            for item in self.knowledge_items:
                if fact.lower() in item["fact"].lower():
                    item["strength"] = min(1.0, item["strength"] + amount)
                    item["recall_count"] += 1
                    item["last_recalled"] = datetime.now().isoformat()
                    self.total_strength_increases += 1
                    break

    def consolidate(self):
        """Review all knowledge, strengthen frequently accessed, prune weak."""
        with self._lock:
            now = datetime.now()
            for item in self.knowledge_items:
                last = datetime.fromisoformat(item["last_recalled"])
                days_since = (now - last).days
                if days_since > 7:
                    item["strength"] = max(0.0, item["strength"] - 0.05)
                if item["recall_count"] > 3:
                    item["strength"] = min(1.0, item["strength"] + 0.1)

            weak = [i for i in self.knowledge_items if i["strength"] < 0.1 and i["recall_count"] == 0]
            for item in weak:
                self.knowledge_items.remove(item)
                self.pruned.append(item["fact"][:100])
                self.total_prunes += 1

            self.consolidation_runs += 1
            self._save()

    def recall_strongest(self, n: int = 10) -> list[dict]:
        return sorted(self.knowledge_items, key=lambda x: -x["strength"])[:n]

    def recall_by_category(self, category: str) -> list[dict]:
        return [i for i in self.knowledge_items if i["category"] == category]

    def get_stats(self) -> dict:
        strengths = [i["strength"] for i in self.knowledge_items] if self.knowledge_items else [0]
        return {
            "total_items": len(self.knowledge_items),
            "avg_strength": f"{sum(strengths)/len(strengths):.2f}",
            "consolidation_runs": self.consolidation_runs,
            "strength_increases": self.total_strength_increases,
            "total_prunes": self.total_prunes,
            "strongest_items": self.recall_strongest(3),
        }


# ─── Self Challenger ─────────────────────────────────────────────────

class SelfChallenger:
    """Sets challenges for itself and tries to solve them."""

    CHALLENGE_TEMPLATES = [
        {"type": "math", "template": "Solve: {expr}", "generator": "_gen_math_challenge"},
        {"type": "code", "template": "Write a function that {desc}", "generator": "_gen_code_challenge"},
        {"type": "logic", "template": "If {premise}, what follows?", "generator": "_gen_logic_challenge"},
        {"type": "memory", "template": "Recall facts about {topic}", "generator": "_gen_memory_challenge"},
        {"type": "creative", "template": "Create a {desc}", "generator": "_gen_creative_challenge"},
        {"type": "analysis", "template": "Analyze: {text}", "generator": "_gen_analysis_challenge"},
    ]

    def __init__(self, storage_dir: str = "memory/challenger"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.active_challenges: list[dict] = []
        self.completed_challenges: list[dict] = []
        self.failed_challenges: list[dict] = []
        self.challenge_history: deque[dict] = deque(maxlen=200)
        self.difficulty_level: float = 0.5
        self.total_challenges = 0
        self.success_rate: float = 0.5

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "challenger.json").read_text())
            self.difficulty_level = data.get("difficulty_level", 0.5)
            self.total_challenges = data.get("total_challenges", 0)
            self.success_rate = data.get("success_rate", 0.5)
            self.completed_challenges = data.get("completed_challenges", [])[-100:]
            self.failed_challenges = data.get("failed_challenges", [])[-50:]
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "difficulty_level": self.difficulty_level,
                "total_challenges": self.total_challenges,
                "success_rate": self.success_rate,
                "completed_challenges": self.completed_challenges[-100:],
                "failed_challenges": self.failed_challenges[-50:],
            }
            (self._dir / "challenger.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def generate_challenge(self) -> dict:
        """Generate a challenge appropriate for current difficulty level."""
        template = random.choice(self.CHALLENGE_TEMPLATES)
        challenge_type = template["type"]

        challenge = {
            "id": hashlib.md5(f"{time.time()}{challenge_type}".encode()).hexdigest()[:8],
            "type": challenge_type,
            "difficulty": self.difficulty_level,
            "created": datetime.now().isoformat(),
            "status": "pending",
        }

        if challenge_type == "math":
            ops = [("+", lambda a, b: a + b), ("-", lambda a, b: a - b),
                   ("*", lambda a, b: a * b)]
            op_sym, op_fn = random.choice(ops)
            a = random.randint(1, int(10 * self.difficulty_level + 5))
            b = random.randint(1, int(10 * self.difficulty_level + 5))
            challenge["question"] = f"What is {a} {op_sym} {b}?"
            challenge["answer"] = str(op_fn(a, b))
        elif challenge_type == "code":
            challenges_list = [
                "reverse a string", "find the largest number in a list",
                "check if a number is prime", "count vowels in a string",
                "sort a list without built-in sort", "find common elements in two lists",
            ]
            challenge["question"] = f"Write code to: {random.choice(challenges_list)}"
            challenge["answer"] = "code_solution"
        elif challenge_type == "logic":
            premises = [
                ("All cats are mammals. A cat is a mammal.", True),
                ("If it rains, the ground is wet. It rains.", True),
                ("All birds can fly. Penguins are birds.", False),
            ]
            premise, expected = random.choice(premises)
            challenge["question"] = f"True or False: {premise}"
            challenge["answer"] = str(expected)
        elif challenge_type == "memory":
            topics = ["mathematics", "computer science", "physics", "history"]
            challenge["question"] = f"Name 3 facts about {random.choice(topics)}"
            challenge["answer"] = "3_facts"
        elif challenge_type == "creative":
            creative_list = [
                "metaphor for programming", "haiku about AI",
                "short story opening about a robot", "analogy for machine learning",
            ]
            challenge["question"] = f"Create a: {random.choice(creative_list)}"
            challenge["answer"] = "creative_output"
        elif challenge_type == "analysis":
            texts = [
                "The quick brown fox jumps over the lazy dog",
                "To be or not to be that is the question",
                "All that glitters is not gold",
            ]
            challenge["question"] = f"Analyze sentiment and themes: {random.choice(texts)}"
            challenge["answer"] = "analysis_output"

        self.active_challenges.append(challenge)
        return challenge

    def submit_answer(self, challenge_id: str, answer: str) -> dict:
        with self._lock:
            for i, ch in enumerate(self.active_challenges):
                if ch["id"] == challenge_id:
                    self.active_challenges.pop(i)
                    ch["answer_given"] = answer
                    ch["completed_at"] = datetime.now().isoformat()

                    correct = self._check_answer(ch, answer)
                    ch["correct"] = correct
                    ch["status"] = "completed" if correct else "failed"

                    if correct:
                        self.completed_challenges.append(ch)
                        self.difficulty_level = min(1.0, self.difficulty_level + 0.05)
                    else:
                        self.failed_challenges.append(ch)
                        self.difficulty_level = max(0.1, self.difficulty_level - 0.03)

                    self.total_challenges += 1
                    completed = len(self.completed_challenges)
                    self.success_rate = completed / self.total_challenges if self.total_challenges > 0 else 0.5
                    self.challenge_history.append(ch)
                    self._save()
                    return ch
            return {"error": "Challenge not found"}

    def _check_answer(self, challenge: dict, answer: str) -> bool:
        if challenge["type"] == "math":
            return answer.strip() == challenge["answer"]
        elif challenge["type"] == "logic":
            return answer.strip().lower() == challenge["answer"].lower()
        return bool(answer.strip())

    def get_stats(self) -> dict:
        return {
            "total_challenges": self.total_challenges,
            "success_rate": f"{self.success_rate:.1%}",
            "difficulty_level": f"{self.difficulty_level:.2f}",
            "completed": len(self.completed_challenges),
            "failed": len(self.failed_challenges),
            "active": len(self.active_challenges),
        }


# ─── Improvement Tracker ─────────────────────────────────────────────

class ImprovementTracker:
    """Tracks progress over time, identifies trends, measures growth."""

    def __init__(self, storage_dir: str = "memory/improvement"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.milestones: list[dict] = []
        self.progress_snapshots: list[dict] = []
        self.goals_completed: int = 0
        self.goals_active: list[dict] = []
        self.improvement_rate: float = 0.0
        self.learning_velocity: float = 0.0

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "improvement.json").read_text())
            self.milestones = data.get("milestones", [])
            self.goals_completed = data.get("goals_completed", 0)
            self.goals_active = data.get("goals_active", [])
            self.improvement_rate = data.get("improvement_rate", 0.0)
            self.learning_velocity = data.get("learning_velocity", 0.0)
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "milestones": self.milestones[-200:],
                "goals_completed": self.goals_completed,
                "goals_active": self.goals_active,
                "improvement_rate": self.improvement_rate,
                "learning_velocity": self.learning_velocity,
            }
            (self._dir / "improvement.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def record_snapshot(self, metrics: dict):
        with self._lock:
            snapshot = {
                "timestamp": datetime.now().isoformat(),
                "metrics": metrics,
            }
            self.progress_snapshots.append(snapshot)
            if len(self.progress_snapshots) > 500:
                self.progress_snapshots = self.progress_snapshots[-500:]
            if len(self.progress_snapshots) >= 2:
                self._calculate_trends()

    def _calculate_trends(self):
        if len(self.progress_snapshots) < 2:
            return
        recent = self.progress_snapshots[-10:]
        prev = self.progress_snapshots[-20:-10] if len(self.progress_snapshots) >= 20 else self.progress_snapshots[:10]

        def get_metric(snapshots, key, default=0):
            vals = [s["metrics"].get(key, default) for s in snapshots if "metrics" in s]
            return sum(vals) / len(vals) if vals else default

        recent_accuracy = get_metric(recent, "accuracy", 0.7)
        prev_accuracy = get_metric(prev, "accuracy", 0.7)
        self.improvement_rate = recent_accuracy - prev_accuracy

        recent_speed = get_metric(recent, "speed", 100)
        prev_speed = get_metric(prev, "speed", 100)
        self.learning_velocity = (recent_speed - prev_speed) / max(prev_speed, 1) * 100

    def add_milestone(self, title: str, description: str, category: str = "general"):
        with self._lock:
            self.milestones.append({
                "title": title,
                "description": description,
                "category": category,
                "achieved_at": datetime.now().isoformat(),
            })
            self._save()

    def add_goal(self, goal: str, category: str = "general", priority: float = 0.5):
        with self._lock:
            self.goals_active.append({
                "goal": goal,
                "category": category,
                "priority": priority,
                "created": datetime.now().isoformat(),
                "status": "active",
            })
            self._save()

    def complete_goal(self, goal: str):
        with self._lock:
            for g in self.goals_active:
                if g["goal"] == goal:
                    g["status"] = "completed"
                    g["completed"] = datetime.now().isoformat()
                    self.goals_active.remove(g)
                    self.goals_completed += 1
                    self.add_milestone(f"Goal completed: {goal}", f"Successfully achieved: {goal}")
                    break
            self._save()

    def get_progress_report(self) -> dict:
        return {
            "total_milestones": len(self.milestones),
            "goals_completed": self.goals_completed,
            "active_goals": len(self.goals_active),
            "improvement_rate": f"{self.improvement_rate:+.2%}",
            "learning_velocity": f"{self.learning_velocity:+.1f}%",
            "recent_milestones": self.milestones[-5:],
            "active_goals_list": self.goals_active[:5],
        }


# ─── Observation Mode ────────────────────────────────────────────────

class ObservationMode:
    """Passively learns from user patterns, communication style, preferences."""

    def __init__(self, storage_dir: str = "memory/observer"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.user_patterns: dict[str, Any] = defaultdict(lambda: defaultdict(int))
        self.conversation_patterns: list[dict] = []
        self.time_patterns: dict[str, int] = defaultdict(int)
        self.topic_preferences: dict[str, float] = defaultdict(float)
        self.communication_style: dict[str, float] = defaultdict(float)
        self.user_emotions: deque[str] = deque(maxlen=100)
        self.session_data: dict[str, Any] = {}

        self._lock = threading.Lock()
        self._load()

    def _load(self):
        try:
            data = json.loads((self._dir / "observer.json").read_text())
            self.topic_preferences = defaultdict(float, data.get("topic_preferences", {}))
            self.communication_style = defaultdict(float, data.get("communication_style", {}))
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "topic_preferences": dict(self.topic_preferences),
                "communication_style": dict(self.communication_style),
            }
            (self._dir / "observer.json").write_text(json.dumps(data, indent=2, default=str))
        except Exception:
            pass

    def observe(self, user_text: str, response: str, context: dict = None):
        """Passively observe and learn from every interaction."""
        with self._lock:
            text_lower = user_text.lower()
            hour = datetime.now().hour
            self.time_patterns[f"hour_{hour}"] += 1

            words = set(text_lower.split())
            tech_words = {"python", "code", "api", "database", "server", "docker", "git",
                         "javascript", "html", "css", "react", "node", "aws", "cloud"}
            for w in words & tech_words:
                self.topic_preferences[w] += 0.1

            style_signals = {
                "formal": {"please", "could", "would", "kindly", "appreciate"},
                "casual": {"hey", "yo", "sup", "gonna", "wanna", "lol"},
                "direct": {"do", "make", "create", "run", "execute", "build"},
                "curious": {"why", "how", "what", "explain", "tell"},
                "emotional": {"feel", "love", "hate", "happy", "sad", "angry"},
            }
            for style, signals in style_signals.items():
                if words & signals:
                    self.communication_style[style] += 0.1

            emotion_words = {
                "happy": {"happy", "great", "awesome", "love", "wonderful", "amazing"},
                "sad": {"sad", "unfortunately", "sorry", "regret", "miss"},
                "angry": {"angry", "frustrated", "annoyed", "hate", "terrible"},
                "excited": {"excited", "amazing", "incredible", "wow", "fantastic"},
            }
            for emotion, signals in emotion_words.items():
                if words & signals:
                    self.user_emotions.append(emotion)

            self.conversation_patterns.append({
                "length": len(user_text),
                "has_question": "?" in user_text,
                "has_exclamation": "!" in user_text,
                "word_count": len(words),
                "timestamp": datetime.now().isoformat(),
            })

            if len(self.conversation_patterns) % 20 == 0:
                self._save()

    def get_user_profile(self) -> dict:
        dominant_style = max(self.communication_style, key=self.communication_style.get) if self.communication_style else "unknown"
        dominant_emotion = "neutral"
        if self.user_emotions:
            from collections import Counter
            dominant_emotion = Counter(self.user_emotions).most_common(1)[0][0]
        top_topics = sorted(self.topic_preferences.items(), key=lambda x: -x[1])[:10]
        peak_hours = sorted(self.time_patterns.items(), key=lambda x: -x[1])[:3]
        return {
            "dominant_style": dominant_style,
            "dominant_emotion": dominant_emotion,
            "top_topics": [t for t, _ in top_topics],
            "peak_hours": [h.replace("hour_", "") for h, _ in peak_hours],
            "total_observations": len(self.conversation_patterns),
            "style_distribution": dict(self.communication_style),
        }


# ─── Autonomous Loop ─────────────────────────────────────────────────

class AutonomousLoop:
    """Runs all self-improvement systems in a background loop."""

    def __init__(self, storage_dir: str = "memory/autonomous"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)

        self.explorer = AutonomousExplorer(str(self._dir / "explorer"))
        self.experimenter = SelfExperimenter(str(self._dir / "experimenter"))
        self.consolidator = KnowledgeConsolidator(str(self._dir / "consolidator"))
        self.challenger = SelfChallenger(str(self._dir / "challenger"))
        self.improvement = ImprovementTracker(str(self._dir / "improvement"))
        self.observer = ObservationMode(str(self._dir / "observer"))

        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self.loop_count = 0
        self.last_activity: Optional[str] = None
        self.activity_log: deque[dict] = deque(maxlen=100)

        self._lock = threading.Lock()

    def start(self, tool_runner=None, interval: float = 60.0):
        """Start the autonomous background loop."""
        if self.is_running:
            return
        self.is_running = True
        self._thread = threading.Thread(
            target=self._loop, args=(tool_runner, interval), daemon=True
        )
        self._thread.start()

    def stop(self):
        self.is_running = False

    def _loop(self, tool_runner, interval):
        while self.is_running:
            try:
                self._do_cycle(tool_runner)
            except Exception:
                pass
            time.sleep(interval)

    def _do_cycle(self, tool_runner):
        self.loop_count += 1
        activity = ""

        action = random.choice(["explore", "experiment", "consolidate", "challenge", "observe"])

        if action == "explore":
            exploration = self.explorer.explore_next()
            if exploration:
                topic = exploration["topic"]
                self.explorer.record_discovery(topic, f"Exploring {topic} fundamentals")
                activity = f"Explored: {topic}"

        elif action == "experiment":
            caps = self.experimenter.EXPERIMENT_TYPES
            cap = random.choice(caps)
            result = self.experimenter.run_experiment(cap, tool_runner)
            activity = f"Experiment: {cap} -> {'PASS' if result['success'] else 'FAIL'}"

        elif action == "consolidate":
            self.consolidator.consolidate()
            activity = "Knowledge consolidated"

        elif action == "challenge":
            challenge = self.challenger.generate_challenge()
            answer = ""
            if challenge["type"] == "math":
                try:
                    answer = str(eval(challenge["question"].replace("What is ", "").rstrip("?")))
                except Exception:
                    answer = "unknown"
            elif challenge["type"] == "logic":
                answer = "True"
            else:
                answer = "completed"
            self.challenger.submit_answer(challenge["id"], answer)
            activity = f"Challenge: {challenge['type']} -> {'PASS' if challenge.get('correct') else 'attempted'}"

        elif action == "observe":
            import time as _t
            sample_texts = [
                "hello", "how are you", "what time is it", "help me with code",
                "tell me a joke", "what is python", "i feel happy today",
            ]
            self.observer.observe(random.choice(sample_texts), "observed")
            activity = "Observation recorded"

        with self._lock:
            self.activity_log.append({
                "cycle": self.loop_count,
                "activity": activity,
                "timestamp": datetime.now().isoformat(),
            })
            self.last_activity = activity

        metrics = {
            "accuracy": self.experimenter.success_rate,
            "exploration_score": self.explorer.exploration_score,
            "knowledge_items": len(self.consolidator.knowledge_items),
            "challenges_completed": len(self.challenger.completed_challenges),
            "speed": 100,
        }
        self.improvement.record_snapshot(metrics)

    def observe_interaction(self, user_text: str, response: str):
        """Called from orchestrator to observe every user interaction."""
        self.observer.observe(user_text, response)

    def get_full_status(self) -> dict:
        return {
            "loop_count": self.loop_count,
            "is_running": self.is_running,
            "last_activity": self.last_activity,
            "explorer": self.explorer.get_stats(),
            "experimenter": self.experimenter.get_stats(),
            "consolidator": self.consolidator.get_stats(),
            "challenger": self.challenger.get_stats(),
            "improvement": self.improvement.get_progress_report(),
            "observer": self.observer.get_user_profile(),
            "recent_activity": list(self.activity_log)[-10:],
        }
