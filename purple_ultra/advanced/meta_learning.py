"""Meta-learning and few-shot learning capabilities."""

from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import dataclass
import numpy as np


@dataclass
class FewShotExample:
    input_text: str
    output_text: str
    category: str = ""
    confidence: float = 1.0


class FewShotLearner:
    def __init__(self, memory_dir: str = "memory/fewshot"):
        self._dir = Path(memory_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._examples: dict[str, list[FewShotExample]] = {}
        self._patterns: dict[str, dict] = {}
        self._load()

    def _load(self):
        try:
            examples_file = self._dir / "examples.json"
            if examples_file.exists():
                data = json.loads(examples_file.read_text())
                for category, items in data.items():
                    self._examples[category] = [
                        FewShotExample(**item) for item in items
                    ]
        except Exception:
            pass

    def _save(self):
        try:
            data = {}
            for category, examples in self._examples.items():
                data[category] = [
                    {"input_text": e.input_text, "output_text": e.output_text,
                     "category": e.category, "confidence": e.confidence}
                    for e in examples
                ]
            (self._dir / "examples.json").write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def add_example(self, input_text: str, output_text: str, category: str = "general"):
        if category not in self._examples:
            self._examples[category] = []
        example = FewShotExample(input_text=input_text, output_text=output_text, category=category)
        self._examples[category].append(example)
        if len(self._examples[category]) > 50:
            self._examples[category] = self._examples[category][-50:]
        self._save()

    def predict(self, input_text: str, category: str = None, k: int = 3) -> str:
        candidates = []
        if category and category in self._examples:
            candidates = self._examples[category]
        else:
            for examples in self._examples.values():
                candidates.extend(examples)
        if not candidates:
            return ""
        scored = []
        for example in candidates:
            score = self._similarity(input_text, example.input_text)
            scored.append((score, example))
        scored.sort(key=lambda x: -x[0])
        top_k = scored[:k]
        if not top_k:
            return ""
        outputs = [ex.output_text for _, ex in top_k]
        scores = [s for s, _ in top_k]
        weights = np.array(scores) / sum(scores) if sum(scores) > 0 else np.ones(len(scores)) / len(scores)
        best_idx = np.argmax(weights)
        return outputs[best_idx]

    def _similarity(self, text1: str, text2: str) -> float:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1 & words2
        union = words1 | words2
        return len(intersection) / len(union) if union else 0

    def get_categories(self) -> list[str]:
        return list(self._examples.keys())

    def get_examples(self, category: str) -> list[dict]:
        return [
            {"input": e.input_text, "output": e.output_text}
            for e in self._examples.get(category, [])
        ]

    def get_stats(self) -> dict:
        total = sum(len(ex) for ex in self._examples.values())
        return {
            "total_examples": total,
            "categories": len(self._examples),
            "examples_per_category": {k: len(v) for k, v in self._examples.items()},
        }


class MetaLearner:
    def __init__(self):
        self._task_history: list[dict] = []
        self._learned_strategies: dict[str, dict] = {}
        self._performance_by_task: dict[str, list[float]] = {}

    def learn_from_task(self, task_type: str, strategy: str, performance: float):
        self._task_history.append({
            "task_type": task_type,
            "strategy": strategy,
            "performance": performance,
            "timestamp": time.time(),
        })
        if task_type not in self._performance_by_task:
            self._performance_by_task[task_type] = []
        self._performance_by_task[task_type].append(performance)
        if task_type not in self._learned_strategies:
            self._learned_strategies[task_type] = {}
        if strategy not in self._learned_strategies[task_type]:
            self._learned_strategies[task_type][strategy] = []
        self._learned_strategies[task_type][strategy].append(performance)

    def select_strategy(self, task_type: str) -> str:
        if task_type not in self._learned_strategies:
            return "default"
        strategies = self._learned_strategies[task_type]
        best_strategy = "default"
        best_avg = 0
        for strategy, performances in strategies.items():
            avg = sum(performances) / len(performances)
            if avg > best_avg:
                best_avg = avg
                best_strategy = strategy
        return best_strategy

    def predict_performance(self, task_type: str, strategy: str) -> float:
        if task_type in self._learned_strategies:
            if strategy in self._learned_strategies[task_type]:
                performances = self._learned_strategies[task_type][strategy]
                return sum(performances) / len(performances)
        if task_type in self._performance_by_task:
            all_perfs = self._performance_by_task[task_type]
            return sum(all_perfs) / len(all_perfs)
        return 0.5

    def adapt_to_new_task(self, new_task_type: str, similar_task: str = None) -> dict:
        if similar_task and similar_task in self._learned_strategies:
            self._learned_strategies[new_task_type] = dict(self._learned_strategies[similar_task])
            return {"adapted_from": similar_task, "strategies": len(self._learned_strategies[new_task_type])}
        self._learned_strategies[new_task_type] = {}
        return {"new_task": True, "strategies": 0}

    def get_task_performance(self, task_type: str) -> dict:
        if task_type not in self._performance_by_task:
            return {"task": task_type, "count": 0, "avg": 0}
        perfs = self._performance_by_task[task_type]
        return {
            "task": task_type,
            "count": len(perfs),
            "avg": sum(perfs) / len(perfs),
            "min": min(perfs),
            "max": max(perfs),
            "strategies": list(self._learned_strategies.get(task_type, {}).keys()),
        }

    def get_global_stats(self) -> dict:
        all_perfs = [p for perfs in self._performance_by_task.values() for p in perfs]
        return {
            "total_tasks": len(self._task_history),
            "unique_task_types": len(self._performance_by_task),
            "avg_performance": sum(all_perfs) / len(all_perfs) if all_perfs else 0,
            "strategies_learned": sum(len(s) for s in self._learned_strategies.values()),
        }


class TransferLearner:
    def __init__(self):
        self._source_knowledge: dict[str, dict] = {}
        self._transfer_history: list[dict] = []

    def store_knowledge(self, domain: str, knowledge: dict):
        self._source_knowledge[domain] = knowledge

    def transfer(self, source_domain: str, target_domain: str, mapping: dict = None) -> dict:
        if source_domain not in self._source_knowledge:
            return {"error": f"Source domain '{source_domain}' not found"}
        source_knowledge = self._source_knowledge[source_domain]
        if mapping:
            transferred = {mapping.get(k, k): v for k, v in source_knowledge.items()}
        else:
            transferred = dict(source_knowledge)
        self._transfer_history.append({
            "source": source_domain,
            "target": target_domain,
            "items_transferred": len(transferred),
            "timestamp": time.time(),
        })
        return {"transferred": len(transferred), "knowledge": transferred}

    def get_domains(self) -> list[str]:
        return list(self._source_knowledge.keys())

    def get_stats(self) -> dict:
        return {
            "domains": len(self._source_knowledge),
            "transfers": len(self._transfer_history),
            "total_knowledge": sum(len(k) for k in self._source_knowledge.values()),
        }
