"""Neural embeddings for semantic memory search and similarity matching."""

from __future__ import annotations

import json
import time
import hashlib
import numpy as np
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field


@dataclass
class EmbeddingEntry:
    text: str
    embedding: list[float]
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    id: str = ""


class EmbeddingEngine:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", cache_dir: str = "models/embeddings"):
        self._model_name = model_name
        self._cache_dir = Path(cache_dir)
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._index: list[EmbeddingEntry] = []
        self._index_file = self._cache_dir / "embedding_index.json"
        self._load_index()

    def _ensure_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self._model_name)
            except ImportError:
                self._model = False

    def _load_index(self):
        if self._index_file.exists():
            try:
                data = json.loads(self._index_file.read_text())
                for entry in data:
                    self._index.append(EmbeddingEntry(
                        text=entry["text"],
                        embedding=entry["embedding"],
                        metadata=entry.get("metadata", {}),
                        timestamp=entry.get("timestamp", 0),
                        id=entry.get("id", ""),
                    ))
            except Exception:
                pass

    def _save_index(self):
        try:
            data = [
                {
                    "text": e.text,
                    "embedding": e.embedding,
                    "metadata": e.metadata,
                    "timestamp": e.timestamp,
                    "id": e.id,
                }
                for e in self._index[-10000:]
            ]
            self._index_file.write_text(json.dumps(data))
        except Exception:
            pass

    def embed(self, text: str) -> list[float]:
        self._ensure_model()
        if not self._model:
            return self._fallback_embed(text)
        try:
            embedding = self._model.encode(text)
            return embedding.tolist()
        except Exception:
            return self._fallback_embed(text)

    def _fallback_embed(self, text: str) -> list[float]:
        words = text.lower().split()
        vocab_size = 10000
        embedding = [0.0] * 128
        for word in words:
            idx = int(hashlib.md5(word.encode()).hexdigest(), 16) % vocab_size
            np_idx = idx % 128
            embedding[np_idx] += 1.0
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = [e / norm for e in embedding]
        return embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self._ensure_model()
        if not self._model:
            return [self._fallback_embed(t) for t in texts]
        try:
            embeddings = self._model.encode(texts)
            return [e.tolist() for e in embeddings]
        except Exception:
            return [self._fallback_embed(t) for t in texts]

    def add(self, text: str, metadata: dict = None) -> str:
        embedding = self.embed(text)
        entry_id = hashlib.md5(text.encode()).hexdigest()[:12]
        entry = EmbeddingEntry(
            text=text,
            embedding=embedding,
            metadata=metadata or {},
            id=entry_id,
        )
        self._index.append(entry)
        if len(self._index) % 100 == 0:
            self._save_index()
        return entry_id

    def search(self, query: str, top_k: int = 5, threshold: float = 0.3) -> list[dict]:
        query_embedding = self.embed(query)
        results = []
        query_vec = np.array(query_embedding)
        for entry in self._index:
            entry_vec = np.array(entry.embedding)
            similarity = self._cosine_similarity(query_vec, entry_vec)
            if similarity >= threshold:
                results.append({
                    "text": entry.text,
                    "score": float(similarity),
                    "metadata": entry.metadata,
                    "id": entry.id,
                })
        results.sort(key=lambda x: -x["score"])
        return results[:top_k]

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def remove(self, entry_id: str) -> bool:
        original_len = len(self._index)
        self._index = [e for e in self._index if e.id != entry_id]
        return len(self._index) < original_len

    def clear(self):
        self._index.clear()
        self._save_index()

    def size(self) -> int:
        return len(self._index)

    def get_stats(self) -> dict:
        return {
            "total_entries": len(self._index),
            "model": self._model_name,
            "model_loaded": self._model is not None and self._model is not False,
            "embedding_dim": len(self._index[0].embedding) if self._index else 0,
        }


class SemanticMemory:
    def __init__(self, embedding_engine: EmbeddingEngine, memory_file: str = "memory/semantic_neural.json"):
        self._engine = embedding_engine
        self._file = Path(memory_file)
        self._file.parent.mkdir(parents=True, exist_ok=True)
        self._entries: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self._file.exists():
            try:
                self._entries = json.loads(self._file.read_text())
            except Exception:
                pass

    def _save(self):
        try:
            self._file.write_text(json.dumps(self._entries, indent=2))
        except Exception:
            pass

    def store(self, key: str, value: str, category: str = "general"):
        self._entries[key] = {
            "value": value,
            "category": category,
            "timestamp": time.time(),
        }
        self._engine.add(f"{key}: {value}", metadata={"key": key, "category": category})
        self._save()

    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        return self._engine.search(query, top_k=top_k)

    def get_by_category(self, category: str) -> list[dict]:
        return [
            {"key": k, **v}
            for k, v in self._entries.items()
            if v.get("category") == category
        ]

    def delete(self, key: str) -> bool:
        if key in self._entries:
            del self._entries[key]
            self._save()
            return True
        return False

    def get_all(self) -> dict:
        return dict(self._entries)
