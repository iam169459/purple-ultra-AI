"""Advanced reasoning with Tree-of-Thought and Graph-of-Thought."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
import math


@dataclass
class ThoughtNode:
    content: str
    score: float = 0.5
    depth: int = 0
    parent: str = ""
    children: list[str] = field(default_factory=list)
    visited: bool = False
    metadata: dict = field(default_factory=dict)


class TreeOfThought:
    def __init__(self, max_depth: int = 5, branch_factor: int = 3):
        self._max_depth = max_depth
        self._branch_factor = branch_factor
        self._nodes: dict[str, ThoughtNode] = {}
        self._root: str = ""
        self._best_path: list[str] = []

    def solve(self, problem: str, think_func=None) -> dict:
        self._nodes.clear()
        root = ThoughtNode(content=problem, depth=0)
        self._root = "root"
        self._nodes["root"] = root
        self._expand_node("root", think_func)
        best_leaf = self._find_best_leaf()
        path = self._trace_path(best_leaf)
        return {
            "solution": self._nodes[best_leaf].content if best_leaf else problem,
            "path": [self._nodes[n].content for n in path],
            "score": self._nodes[best_leaf].score if best_leaf else 0,
            "nodes_explored": len(self._nodes),
        }

    def _expand_node(self, node_id: str, think_func=None):
        node = self._nodes[node_id]
        if node.depth >= self._max_depth:
            return
        thoughts = self._generate_thoughts(node.content, think_func)
        for i, thought in enumerate(thoughts[:self._branch_factor]):
            child_id = f"{node_id}_{i}"
            child = ThoughtNode(
                content=thought, depth=node.depth + 1, parent=node_id,
            )
            child.score = self._evaluate_thought(thought, node.score)
            self._nodes[child_id] = child
            node.children.append(child_id)
            if child.score > 0.7 and child.depth < self._max_depth:
                self._expand_node(child_id, think_func)

    def _generate_thoughts(self, content: str, think_func=None) -> list[str]:
        if think_func:
            try:
                return think_func(content)
            except Exception:
                pass
        words = content.split()
        if len(words) < 5:
            return [content + " because it's logical", content + " based on evidence"]
        mid = len(words) // 2
        return [
            " ".join(words[:mid]) + " therefore " + " ".join(words[mid:]),
            " ".join(words[mid:]) + " given that " + " ".join(words[:mid]),
            "Consider: " + content + " from multiple angles",
        ]

    def _evaluate_thought(self, thought: str, parent_score: float) -> float:
        score = parent_score
        if len(thought) > 50:
            score += 0.1
        if any(word in thought.lower() for word in ["because", "therefore", "evidence", "logic"]):
            score += 0.1
        if "?" in thought:
            score -= 0.1
        words = set(thought.lower().split())
        if len(words) < len(thought.split()) * 0.7:
            score += 0.05
        return max(0, min(1, score))

    def _find_best_leaf(self) -> str | None:
        leaves = [nid for nid, node in self._nodes.items() if not node.children]
        if not leaves:
            return self._root
        return max(leaves, key=lambda nid: self._nodes[nid].score)

    def _trace_path(self, node_id: str) -> list[str]:
        path = []
        current = node_id
        while current:
            path.append(current)
            current = self._nodes[current].parent if current in self._nodes else ""
        return list(reversed(path))

    def get_stats(self) -> dict:
        return {
            "total_nodes": len(self._nodes),
            "max_depth": max((n.depth for n in self._nodes.values()), default=0),
            "best_score": max((n.score for n in self._nodes.values()), default=0),
        }


class GraphOfThought:
    def __init__(self):
        self._nodes: dict[str, ThoughtNode] = {}
        self._edges: list[tuple[str, str, float]] = []
        self._clusters: list[list[str]] = []

    def add_thought(self, thought: str, score: float = 0.5, metadata: dict = None) -> str:
        node_id = f"thought_{len(self._nodes)}"
        node = ThoughtNode(content=thought, score=score, metadata=metadata or {})
        self._nodes[node_id] = node
        return node_id

    def connect(self, from_id: str, to_id: str, strength: float = 1.0):
        if from_id in self._nodes and to_id in self._nodes:
            self._edges.append((from_id, to_id, strength))
            self._nodes[from_id].children.append(to_id)

    def solve(self, problem: str) -> dict:
        root_id = self.add_thought(problem, 1.0)
        related = self._find_related(problem)
        for thought, score in related:
            tid = self.add_thought(thought, score)
            self.connect(root_id, tid, score)
        self._cluster_thoughts()
        best_cluster = self._find_best_cluster()
        synthesis = self._synthesize_cluster(best_cluster)
        return {
            "synthesis": synthesis,
            "thoughts_used": len(best_cluster),
            "avg_score": sum(self._nodes[t].score for t in best_cluster) / len(best_cluster) if best_cluster else 0,
        }

    def _find_related(self, problem: str) -> list[tuple[str, float]]:
        words = set(problem.lower().split())
        related = [
            (f"Perspective 1: Consider {problem} from a practical standpoint", 0.7),
            (f"Perspective 2: Analyze {problem} theoretically", 0.65),
            (f"Perspective 3: Evaluate {problem} based on evidence", 0.8),
            (f"Perspective 4: Think about {problem} creatively", 0.6),
            (f"Perspective 5: Apply {problem} to real scenarios", 0.75),
        ]
        return related

    def _cluster_thoughts(self):
        visited = set()
        for node_id in self._nodes:
            if node_id not in visited:
                cluster = self._bfs_cluster(node_id, visited)
                if len(cluster) > 1:
                    self._clusters.append(cluster)

    def _bfs_cluster(self, start: str, visited: set) -> list[str]:
        cluster = []
        queue = [start]
        while queue:
            node_id = queue.pop(0)
            if node_id in visited:
                continue
            visited.add(node_id)
            cluster.append(node_id)
            if node_id in self._nodes:
                for child in self._nodes[node_id].children:
                    if child not in visited:
                        queue.append(child)
        return cluster

    def _find_best_cluster(self) -> list[str]:
        if not self._clusters:
            return list(self._nodes.keys())
        return max(self._clusters, key=lambda c: sum(self._nodes[n].score for n in c if n in self._nodes))

    def _synthesize_cluster(self, cluster: list[str]) -> str:
        thoughts = [self._nodes[n].content for n in cluster if n in self._nodes]
        if not thoughts:
            return ""
        return " | ".join(thoughts[:5])

    def get_stats(self) -> dict:
        return {
            "nodes": len(self._nodes),
            "edges": len(self._edges),
            "clusters": len(self._clusters),
        }


class MetacognitiveReasoner:
    def __init__(self):
        self._reasoning_history: list[dict] = []
        self._strategy_scores: dict[str, float] = {
            "tree_of_thought": 0.7,
            "graph_of_thought": 0.7,
            "chain_of_thought": 0.8,
            "beam_search": 0.6,
            "greedy": 0.5,
        }

    def select_strategy(self, problem: str) -> str:
        problem_complexity = self._assess_complexity(problem)
        if problem_complexity > 0.8:
            return "tree_of_thought"
        elif problem_complexity > 0.6:
            return "graph_of_thought"
        elif problem_complexity > 0.4:
            return "chain_of_thought"
        else:
            return "greedy"

    def _assess_complexity(self, problem: str) -> float:
        words = problem.split()
        score = 0.0
        if len(words) > 20:
            score += 0.3
        if "?" in problem:
            score += 0.2
        if any(w in problem.lower() for w in ["why", "how", "explain", "analyze"]):
            score += 0.3
        if any(w in problem.lower() for w in ["compare", "contrast", "evaluate"]):
            score += 0.2
        return min(1.0, score)

    def reflect(self, problem: str, solution: str, strategy: str):
        self._reasoning_history.append({
            "problem": problem[:100],
            "solution": solution[:200],
            "strategy": strategy,
            "timestamp": time.time(),
        })
        if len(self._reasoning_history) > 100:
            self._reasoning_history = self._reasoning_history[-100:]

    def get_performance(self) -> dict:
        strategy_counts = {}
        for entry in self._reasoning_history:
            s = entry["strategy"]
            strategy_counts[s] = strategy_counts.get(s, 0) + 1
        return {
            "total_problems": len(self._reasoning_history),
            "strategy_usage": strategy_counts,
            "strategy_scores": dict(self._strategy_scores),
        }
