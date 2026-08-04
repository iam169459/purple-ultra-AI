"""Reinforcement learning from human feedback (RLHF)."""

from __future__ import annotations

import json
import time
import math
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class FeedbackEntry:
    prompt: str
    response: str
    rating: float
    category: str = ""
    comment: str = ""
    timestamp: float = field(default_factory=time.time)
    model_version: str = "1.0"


@dataclass
class RewardModel:
    weights: dict[str, float] = field(default_factory=dict)
    bias: float = 0.0
    learning_rate: float = 0.01
    trained: bool = False


class RLHFSystem:
    def __init__(self, memory_dir: str = "memory/rlhf"):
        self._dir = Path(memory_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._feedback: list[FeedbackEntry] = []
        self._reward_model = RewardModel()
        self._preference_pairs: list[dict] = []
        self._training_history: list[dict] = []
        self._reward_history: list[float] = []
        self._load()

    def _load(self):
        try:
            fb_file = self._dir / "feedback.json"
            if fb_file.exists():
                data = json.loads(fb_file.read_text())
                for item in data:
                    self._feedback.append(FeedbackEntry(**item))
            rm_file = self._dir / "reward_model.json"
            if rm_file.exists():
                data = json.loads(rm_file.read_text())
                self._reward_model = RewardModel(**data)
        except Exception:
            pass

    def _save(self):
        try:
            fb_data = [
                {"prompt": f.prompt, "response": f.response, "rating": f.rating,
                 "category": f.category, "comment": f.comment, "timestamp": f.timestamp,
                 "model_version": f.model_version}
                for f in self._feedback[-5000:]
            ]
            (self._dir / "feedback.json").write_text(json.dumps(fb_data, indent=2))
            rm_data = {
                "weights": self._reward_model.weights,
                "bias": self._reward_model.bias,
                "learning_rate": self._reward_model.learning_rate,
                "trained": self._reward_model.trained,
            }
            (self._dir / "reward_model.json").write_text(json.dumps(rm_data, indent=2))
        except Exception:
            pass

    def add_feedback(self, prompt: str, response: str, rating: float, category: str = "", comment: str = ""):
        entry = FeedbackEntry(
            prompt=prompt, response=response, rating=rating,
            category=category, comment=comment,
        )
        self._feedback.append(entry)
        self._reward_history.append(rating)
        self._update_reward_model(entry)
        self._save()

    def _update_reward_model(self, entry: FeedbackEntry):
        features = self._extract_features(entry.prompt, entry.response)
        prediction = self._predict_reward(features)
        error = entry.rating - prediction
        for key, value in features.items():
            if key not in self._reward_model.weights:
                self._reward_model.weights[key] = 0.0
            self._reward_model.weights[key] += self._reward_model.learning_rate * error * value
        self._reward_model.bias += self._reward_model.learning_rate * error
        self._reward_model.trained = True

    def _extract_features(self, prompt: str, response: str) -> dict[str, float]:
        features = {}
        features["prompt_length"] = len(prompt) / 100
        features["response_length"] = len(response) / 100
        features["length_ratio"] = len(response) / (len(prompt) + 1)
        positive_words = {"good", "great", "helpful", "accurate", "clear", "excellent"}
        negative_words = {"bad", "wrong", "incorrect", "confusing", "poor"}
        response_words = set(response.lower().split())
        features["positive_words"] = len(response_words & positive_words)
        features["negative_words"] = len(response_words & negative_words)
        features["has_code"] = 1.0 if "```" in response or "def " in response or "class " in response else 0.0
        features["has_list"] = 1.0 if response.count("\n-") > 0 or response.count("\n*") > 0 else 0.0
        features["question_marks"] = response.count("?") / 10
        features["exclamation_marks"] = response.count("!") / 10
        return features

    def _predict_reward(self, features: dict[str, float]) -> float:
        prediction = self._reward_model.bias
        for key, value in features.items():
            prediction += self._reward_model.weights.get(key, 0) * value
        return max(0, min(5, prediction))

    def predict_reward(self, prompt: str, response: str) -> float:
        features = self._extract_features(prompt, response)
        return self._predict_reward(features)

    def add_preference(self, prompt: str, chosen: str, rejected: str):
        self._preference_pairs.append({
            "prompt": prompt,
            "chosen": chosen,
            "rejected": rejected,
            "timestamp": time.time(),
        })
        self._save()

    def optimize_response(self, prompt: str, responses: list[str]) -> str:
        if not responses:
            return ""
        scores = [(r, self.predict_reward(prompt, r)) for r in responses]
        scores.sort(key=lambda x: -x[1])
        return scores[0][0]

    def get_feedback_stats(self) -> dict:
        if not self._feedback:
            return {"total": 0, "avg_rating": 0, "distribution": {}}
        ratings = [f.rating for f in self._feedback]
        distribution = {}
        for r in ratings:
            bucket = int(r)
            distribution[bucket] = distribution.get(bucket, 0) + 1
        return {
            "total": len(self._feedback),
            "avg_rating": sum(ratings) / len(ratings),
            "min_rating": min(ratings),
            "max_rating": max(ratings),
            "distribution": distribution,
            "categories": len(set(f.category for f in self._feedback if f.category)),
        }

    def get_trend(self, window: int = 10) -> list[float]:
        if len(self._reward_history) < window:
            return self._reward_history
        return self._reward_history[-window:]

    def get_top_feedback(self, count: int = 10) -> list[dict]:
        sorted_feedback = sorted(self._feedback, key=lambda x: -x.rating)
        return [
            {"prompt": f.prompt[:100], "rating": f.rating, "category": f.category}
            for f in sorted_feedback[:count]
        ]

    def train_preference_model(self) -> dict:
        if len(self._preference_pairs) < 10:
            return {"error": "Need at least 10 preference pairs"}
        correct = 0
        for pair in self._preference_pairs:
            score_chosen = self.predict_reward(pair["prompt"], pair["chosen"])
            score_rejected = self.predict_reward(pair["prompt"], pair["rejected"])
            if score_chosen > score_rejected:
                correct += 1
        accuracy = correct / len(self._preference_pairs)
        self._training_history.append({
            "accuracy": accuracy,
            "pairs": len(self._preference_pairs),
            "timestamp": time.time(),
        })
        return {"accuracy": accuracy, "pairs": len(self._preference_pairs)}
