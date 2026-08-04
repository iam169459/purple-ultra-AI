"""Neural recommendation engine."""

from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import dataclass, field
import numpy as np


@dataclass
class Recommendation:
    item: str
    score: float
    reason: str = ""
    category: str = ""


class NeuralRecommender:
    def __init__(self, memory_dir: str = "memory"):
        self._data_dir = Path(memory_dir)
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._interactions: list[dict] = []
        self._item_embeddings: dict[str, list[float]] = {}
        self._user_preferences: dict[str, float] = {}
        self._load()

    def _load(self):
        try:
            interactions_file = self._data_dir / "recommendations.json"
            if interactions_file.exists():
                data = json.loads(interactions_file.read_text())
                self._interactions = data.get("interactions", [])
                self._item_embeddings = data.get("embeddings", {})
                self._user_preferences = data.get("preferences", {})
        except Exception:
            pass

    def _save(self):
        try:
            data = {
                "interactions": self._interactions[-1000:],
                "embeddings": self._item_embeddings,
                "preferences": self._user_preferences,
            }
            (self._data_dir / "recommendations.json").write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def record_interaction(self, item: str, rating: float = 1.0, category: str = ""):
        self._interactions.append({
            "item": item,
            "rating": rating,
            "category": category,
            "timestamp": time.time(),
        })
        if item not in self._item_embeddings:
            self._item_embeddings[item] = self._text_to_embedding(item)
        if category:
            self._user_preferences[category] = self._user_preferences.get(category, 0) + rating
        self._save()

    def _text_to_embedding(self, text: str) -> list[float]:
        vocab_size = 5000
        embedding = [0.0] * 64
        for word in text.lower().split():
            idx = hash(word) % vocab_size
            embedding[idx % 64] += 1.0
        norm = np.linalg.norm(embedding)
        return [e / norm for e in embedding] if norm > 0 else embedding

    def recommend(self, context: str = "", count: int = 5) -> list[Recommendation]:
        if not self._interactions:
            return []
        context_emb = np.array(self._text_to_embedding(context)) if context else np.zeros(64)
        item_scores = {}
        for interaction in self._interactions:
            item = interaction["item"]
            rating = interaction["rating"]
            if item not in self._item_embeddings:
                self._item_embeddings[item] = self._text_to_embedding(item)
            item_emb = np.array(self._item_embeddings[item])
            similarity = float(np.dot(context_emb, item_emb) / (np.linalg.norm(context_emb) * np.linalg.norm(item_emb) + 1e-10))
            score = rating * 0.5 + similarity * 0.5
            if item not in item_scores or score > item_scores[item]:
                item_scores[item] = score
        sorted_items = sorted(item_scores.items(), key=lambda x: -x[1])
        return [
            Recommendation(item=item, score=score, reason="Based on your preferences")
            for item, score in sorted_items[:count]
        ]

    def recommend_by_category(self, category: str, count: int = 5) -> list[Recommendation]:
        category_items = [
            i for i in self._interactions if i.get("category") == category
        ]
        if not category_items:
            return []
        item_scores = {}
        for item in category_items:
            name = item["item"]
            rating = item["rating"]
            if name not in item_scores or rating > item_scores[name]:
                item_scores[name] = rating
        sorted_items = sorted(item_scores.items(), key=lambda x: -x[1])
        return [
            Recommendation(item=name, score=score, category=category)
            for name, score in sorted_items[:count]
        ]

    def get_trending(self, count: int = 10) -> list[Recommendation]:
        recent = [i for i in self._interactions if time.time() - i["timestamp"] < 86400]
        if not recent:
            return []
        item_counts = {}
        for interaction in recent:
            item = interaction["item"]
            item_counts[item] = item_counts.get(item, 0) + 1
        sorted_items = sorted(item_counts.items(), key=lambda x: -x[1])
        return [
            Recommendation(item=item, score=count, reason="Trending")
            for item, count in sorted_items[:count]
        ]

    def get_preferences(self) -> dict:
        return dict(sorted(self._user_preferences.items(), key=lambda x: -x[1]))

    def clear_history(self):
        self._interactions.clear()
        self._item_embeddings.clear()
        self._user_preferences.clear()
        self._save()

    def get_stats(self) -> dict:
        return {
            "total_interactions": len(self._interactions),
            "unique_items": len(self._item_embeddings),
            "categories": len(self._user_preferences),
        }
