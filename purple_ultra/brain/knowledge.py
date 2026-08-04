"""Knowledge graph for storing and querying facts and relationships."""

from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class KnowledgeNode:
    id: str
    content: str
    node_type: str = "fact"
    confidence: float = 0.7
    connections: list[str] = field(default_factory=list)
    timestamp: float = 0.0


class KnowledgeGraph:
    """Stores facts, relationships, and queries them."""

    def __init__(self, storage_dir: str = "memory/knowledge"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._nodes: dict[str, KnowledgeNode] = {}
        self._load()

    def _load(self):
        path = self._dir / "graph.json"
        if path.exists():
            try:
                data = json.loads(path.read_text())
                for k, v in data.items():
                    self._nodes[k] = KnowledgeNode(**v)
            except Exception:
                pass

    def _save(self):
        data = {k: {"id": n.id, "content": n.content, "node_type": n.node_type,
                     "confidence": n.confidence, "connections": n.connections,
                     "timestamp": n.timestamp}
                for k, n in self._nodes.items()}
        (self._dir / "graph.json").write_text(json.dumps(data, indent=2))

    def add_fact(self, fact: str, node_type: str = "fact") -> str:
        node_id = f"node_{len(self._nodes)}"
        node = KnowledgeNode(
            id=node_id,
            content=fact,
            node_type=node_type,
            timestamp=time.time()
        )
        self._nodes[node_id] = node
        self._save()
        return node_id

    def query(self, query: str, top_k: int = 5) -> list[dict]:
        query_lower = query.lower()
        results = []
        for node in self._nodes.values():
            score = 0
            query_words = set(query_lower.split())
            content_words = set(node.content.lower().split())
            overlap = len(query_words & content_words)
            score = overlap / max(len(query_words), 1)
            if score > 0.1:
                results.append({"id": node.id, "content": node.content, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def get_stats(self) -> dict:
        return {"total_nodes": len(self._nodes)}
