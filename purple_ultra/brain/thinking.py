"""Thinking engine with Chain-of-Thought reasoning, metacognition, and hypothesis evaluation."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ThoughtStep:
    step: str
    confidence: float = 0.7
    reasoning: str = ""
    timestamp: float = 0.0


@dataclass
class Hypothesis:
    statement: str
    prior: float = 0.5
    posterior: float = 0.5
    evidence: list = field(default_factory=list)
    status: str = "active"


class ChainOfThought:
    def __init__(self):
        self.steps: list[ThoughtStep] = []
        self.hypotheses: list[Hypothesis] = []
        self.conclusions: list[str] = []

    def add_step(self, step: str, confidence: float = 0.7, reasoning: str = ""):
        self.steps.append(ThoughtStep(step=step, confidence=confidence, reasoning=reasoning, timestamp=time.time()))

    def add_hypothesis(self, hypothesis: str, prior: float = 0.5):
        self.hypotheses.append(Hypothesis(statement=hypothesis, prior=prior, posterior=prior))

    def add_evidence(self, hypothesis_idx: int, evidence: str, supports: bool):
        if 0 <= hypothesis_idx < len(self.hypotheses):
            h = self.hypotheses[hypothesis_idx]
            h.evidence.append({"evidence": evidence, "supports": supports})
            if supports:
                h.posterior = min(h.posterior * 1.3, 0.99)
            else:
                h.posterior = max(h.posterior * 0.7, 0.01)

    def evaluate(self) -> dict:
        results = {"steps": [], "hypotheses": [], "conclusions": self.conclusions}
        for s in self.steps:
            results["steps"].append({"step": s.step, "confidence": s.confidence, "reasoning": s.reasoning})
        for h in self.hypotheses:
            results["hypotheses"].append({"statement": h.statement, "prior": h.prior, "posterior": h.posterior, "status": h.status})
        return results

    def backtrack(self, reason: str):
        if self.steps:
            self.steps.pop()
        self.conclusions.append(f"Backtracked: {reason}")

    def get_confidence(self) -> float:
        if not self.steps:
            return 0.5
        return sum(s.confidence for s in self.steps) / len(self.steps)

    def decompose(self, question: str):
        words = question.split()
        if len(words) > 10:
            self.add_step("Break down into sub-questions", 0.8)
            mid = len(words) // 2
            self.add_step(f"Consider first part: {' '.join(words[:mid])}", 0.7)
            self.add_step(f"Consider second part: {' '.join(words[mid:])}", 0.7)
        else:
            self.add_step(f"Analyze: {question}", 0.8)


class ThinkingEngine:
    def __init__(self, memory_dir: str = "memory"):
        self._data_dir = Path(memory_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._thoughts_file = self._data_dir / "thinking_history.json"
        self._goals_file = self._data_dir / "thinking_goals.json"
        self._thoughts: list[dict] = []
        self._goals: list[dict] = []
        self._load()

    def _load(self):
        try:
            if self._thoughts_file.exists():
                self._thoughts = json.loads(self._thoughts_file.read_text())
            if self._goals_file.exists():
                self._goals = json.loads(self._goals_file.read_text())
        except Exception:
            pass

    def _save(self):
        try:
            self._thoughts_file.write_text(json.dumps(self._thoughts[-200:], indent=2))
            self._goals_file.write_text(json.dumps(self._goals, indent=2))
        except Exception:
            pass

    def think(self, question: str, context: str = "") -> dict:
        chain = ChainOfThought()
        chain.decompose(question)
        chain.add_step("Evaluate confidence and context", 0.7)
        chain.add_hypothesis(f"User wants to know about: {question}", 0.6)
        result = chain.evaluate()
        self._thoughts.append({
            "question": question,
            "context": context[:200],
            "result": result,
            "timestamp": time.time(),
        })
        self._save()
        return result

    def think_deeply(self, question: str, context: str = "", depth: int = 3) -> dict:
        chain = ChainOfThought()
        chain.decompose(question)
        for i in range(depth):
            chain.add_step(f"Deep analysis pass {i+1}", max(0.5, 0.9 - i * 0.1))
            chain.add_hypothesis(f"Pass {i+1} consideration", 0.5 + i * 0.1)
        result = chain.evaluate()
        result["depth"] = depth
        return result

    def set_goal(self, goal: str, priority: int = 5):
        self._goals.append({
            "goal": goal,
            "priority": priority,
            "status": "active",
            "created": time.time(),
        })
        self._save()

    def get_goals(self) -> list[dict]:
        return [g for g in self._goals if g.get("status") == "active"]

    def complete_goal(self, goal: str):
        for g in self._goals:
            if g.get("goal") == goal:
                g["status"] = "completed"
                g["completed_at"] = time.time()
        self._save()

    def get_recent_thoughts(self, count: int = 5) -> list[dict]:
        return self._thoughts[-count:]

    def get_status(self) -> dict:
        return {
            "total_thoughts": len(self._thoughts),
            "active_goals": len(self.get_goals()),
            "last_thought": self._thoughts[-1] if self._thoughts else None,
        }
