"""Neural reasoning engine with logical inference, probabilistic reasoning, and causal analysis."""

from __future__ import annotations

import time
import math
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from enum import Enum
from collections import defaultdict


class InferenceType(Enum):
    FORWARD = "forward"
    BACKWARD = "backward"
    BIDIRECTIONAL = "bidirectional"
    ABDUCTIVE = "abductive"


class LogicType(Enum):
    PROPOSITIONAL = "propositional"
    PREDICATE = "predicate"
    FUZZY = "fuzzy"
    BAYESIAN = "bayesian"
    NEURAL_SYMBOLIC = "neural_symbolic"


@dataclass
class Proposition:
    name: str
    value: bool
    confidence: float = 1.0
    evidence: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


@dataclass
class Rule:
    name: str
    premises: list[str]
    conclusion: str
    confidence: float = 0.9
    rule_type: str = "implication"
    metadata: dict = field(default_factory=dict)


@dataclass
class InferenceResult:
    query: str
    conclusion: str
    confidence: float
    inference_type: InferenceType
    steps: list[dict] = field(default_factory=list)
    evidence: list[str] = field(default_factory=list)
    duration: float = 0.0


@dataclass
class CausalNode:
    name: str
    causes: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    probability: float = 0.5
    interventions: dict[str, float] = field(default_factory=dict)


@dataclass
class BayesianNode:
    name: str
    parents: list[str] = field(default_factory=list)
    children: list[str] = field(default_factory=list)
    cpt: dict[str, float] = field(default_factory=dict)
    evidence: dict[str, bool] = field(default_factory=dict)


class PropositionalLogic:
    def __init__(self):
        self._propositions: dict[str, Proposition] = {}
        self._rules: list[Rule] = []
        self._inference_cache: dict[str, InferenceResult] = {}

    def add_proposition(self, name: str, value: bool, confidence: float = 1.0):
        self._propositions[name] = Proposition(name=name, value=value, confidence=confidence)

    def add_rule(self, name: str, premises: list[str], conclusion: str, confidence: float = 0.9):
        self._rules.append(Rule(name=name, premises=premises, conclusion=conclusion, confidence=confidence))

    def forward_chaining(self) -> list[InferenceResult]:
        results = []
        changed = True
        while changed:
            changed = False
            for rule in self._rules:
                if rule.conclusion not in self._propositions:
                    all_premises_met = all(
                        self._propositions.get(p, Proposition(name=p, value=False)).value
                        for p in rule.premises
                    )
                    if all_premises_met:
                        confidence = rule.confidence * min(
                            self._propositions.get(p, Proposition(name=p, value=False)).confidence
                            for p in rule.premises
                        )
                        self.add_proposition(rule.conclusion, True, confidence)
                        results.append(InferenceResult(
                            query=rule.name,
                            conclusion=rule.conclusion,
                            confidence=confidence,
                            inference_type=InferenceType.FORWARD,
                            steps=[{"rule": rule.name, "premises": rule.premises}],
                        ))
                        changed = True
        return results

    def backward_chaining(self, goal: str, visited: set = None) -> Optional[InferenceResult]:
        if visited is None:
            visited = set()
        if goal in visited:
            return None
        visited.add(goal)
        if goal in self._propositions and self._propositions[goal].value:
            return InferenceResult(
                query=goal,
                conclusion=goal,
                confidence=self._propositions[goal].confidence,
                inference_type=InferenceType.BACKWARD,
                evidence=[f"Already established: {goal}"],
            )
        for rule in self._rules:
            if rule.conclusion == goal:
                sub_results = []
                all_proven = True
                for premise in rule.premises:
                    sub = self.backward_chaining(premise, visited.copy())
                    if sub:
                        sub_results.append(sub)
                    else:
                        all_proven = False
                        break
                if all_proven:
                    confidence = rule.confidence * min(r.confidence for r in sub_results) if sub_results else rule.confidence
                    return InferenceResult(
                        query=goal,
                        conclusion=goal,
                        confidence=confidence,
                        inference_type=InferenceType.BACKWARD,
                        steps=[{"rule": rule.name, "sub_results": len(sub_results)}],
                        evidence=[r.conclusion for r in sub_results],
                    )
        return None

    def deductive_reasoning(self, premises: list[str]) -> InferenceResult:
        start = time.time()
        conclusion_parts = []
        total_confidence = 1.0
        for p in premises:
            prop = self._propositions.get(p)
            if prop:
                conclusion_parts.append(f"{p}={prop.value}")
                total_confidence *= prop.confidence
            else:
                conclusion_parts.append(f"{p}=unknown")
                total_confidence *= 0.5
        return InferenceResult(
            query=" + ".join(premises),
            conclusion=" AND ".join(conclusion_parts),
            confidence=total_confidence,
            inference_type=InferenceType.FORWARD,
            duration=time.time() - start,
        )


class BayesianNetwork:
    def __init__(self):
        self._nodes: dict[str, BayesianNode] = {}
        self._inference_cache: dict[str, dict] = {}

    def add_node(self, name: str, parents: list[str] = None, cpt: dict[str, float] = None):
        self._nodes[name] = BayesianNode(
            name=name,
            parents=parents or [],
            cpt=cpt or {},
        )
        for p in (parents or []):
            if p in self._nodes:
                self._nodes[p].children.append(name)

    def set_evidence(self, node: str, value: bool):
        if node in self._nodes:
            self._nodes[node].evidence[node] = value

    def clear_evidence(self):
        for node in self._nodes.values():
            node.evidence.clear()

    def compute_prior(self, node: str) -> float:
        if node not in self._nodes:
            return 0.5
        bn = self._nodes[node]
        if not bn.parents:
            return bn.cpt.get("true", 0.5)
        parent_values = tuple(self._nodes[p].evidence.get(p, False) for p in bn.parents)
        key = str(parent_values)
        return bn.cpt.get(key, 0.5)

    def compute_posterior(self, node: str, evidence: dict[str, bool] = None) -> float:
        if evidence:
            for k, v in evidence.items():
                self.set_evidence(k, v)
        prior = self.compute_prior(node)
        likelihood = 1.0
        for child in self._nodes.get(node, BayesianNode(name=node)).children:
            child_prior = self.compute_prior(child)
            likelihood *= child_prior if self._nodes[child].evidence.get(child, False) else (1 - child_prior)
        posterior = (likelihood * prior) / max(0.001, likelihood * prior + (1 - likelihood) * (1 - prior))
        return posterior

    def query(self, node: str, evidence: dict[str, bool] = None) -> dict:
        start = time.time()
        posterior = self.compute_posterior(node, evidence)
        return {
            "node": node,
            "posterior": posterior,
            "prior": self.compute_prior(node),
            "evidence": evidence or {},
            "duration": time.time() - start,
        }


class CausalEngine:
    def __init__(self):
        self._nodes: dict[str, CausalNode] = {}
        self._interventions: list[dict] = []

    def add_node(self, name: str, causes: list[str] = None, effects: list[str] = None, probability: float = 0.5):
        self._nodes[name] = CausalNode(
            name=name,
            causes=causes or [],
            effects=effects or [],
            probability=probability,
        )

    def add_causal_link(self, cause: str, effect: str, strength: float = 0.5):
        if cause in self._nodes:
            self._nodes[cause].effects.append(effect)
        if effect in self._nodes:
            self._nodes[effect].causes.append(cause)
            self._nodes[effect].interventions[cause] = strength

    def intervene(self, node: str, value: float) -> dict:
        if node not in self._nodes:
            return {"error": f"Node {node} not found"}
        original_prob = self._nodes[node].probability
        self._nodes[node].probability = value
        cascaded_effects = []
        for effect_name in self._nodes[node].effects:
            effect_node = self._nodes[effect_name]
            intervention_strength = effect_node.interventions.get(node, 0.5)
            new_prob = effect_node.probability * (1 + intervention_strength * (value - original_prob))
            new_prob = max(0.0, min(1.0, new_prob))
            cascaded_effects.append({
                "node": effect_name,
                "old_probability": effect_node.probability,
                "new_probability": new_prob,
            })
            effect_node.probability = new_prob
        self._interventions.append({
            "node": node,
            "value": value,
            "original": original_prob,
            "effects": cascaded_effects,
            "timestamp": time.time(),
        })
        return {
            "intervention": node,
            "value": value,
            "original_probability": original_prob,
            "effects": cascaded_effects,
        }

    def counterfactual(self, node: str, actual_value: float, counter_value: float) -> dict:
        actual = self.intervene(node, actual_value)
        counter = self.intervene(node, counter_value)
        return {
            "actual": actual,
            "counterfactual": counter,
            "difference": counter.get("effects", []) and actual.get("effects", []),
        }

    def get_causal_graph(self) -> dict:
        nodes = {}
        for name, node in self._nodes.items():
            nodes[name] = {
                "causes": node.causes,
                "effects": node.effects,
                "probability": node.probability,
            }
        return {"nodes": nodes, "interventions": len(self._interventions)}

    def get_stats(self) -> dict:
        return {
            "total_nodes": len(self._nodes),
            "total_interventions": len(self._interventions),
            "avg_probability": sum(n.probability for n in self._nodes.values()) / max(1, len(self._nodes)),
        }


class FuzzyLogic:
    def __init__(self):
        self._sets: dict[str, dict[str, float]] = {}
        self._rules: list[dict] = []

    def add_fuzzy_set(self, name: str, values: dict[str, float]):
        self._sets[name] = {k: max(0.0, min(1.0, v)) for k, v in values.items()}

    def add_rule(self, antecedent: str, consequent: str, operator: str = "AND"):
        self._rules.append({"antecedent": antecedent, "consequent": consequent, "operator": operator})

    def fuzzify(self, crisp_value: float, set_name: str) -> dict[str, float]:
        if set_name not in self._sets:
            return {}
        membership = {}
        for label, params in self._sets[set_name].items():
            if isinstance(params, dict):
                center = params.get("center", 0.5)
                width = params.get("width", 0.2)
                membership[label] = max(0.0, 1.0 - abs(crisp_value - center) / width)
            else:
                membership[label] = max(0.0, min(1.0, params))
        return membership

    def infer(self, inputs: dict[str, float]) -> dict[str, float]:
        results = {}
        for rule in self._rules:
            ant_val = inputs.get(rule["antecedent"], 0.5)
            if rule["operator"] == "AND":
                output_val = ant_val * 0.8
            elif rule["operator"] == "OR":
                output_val = max(ant_val, 0.6)
            else:
                output_val = ant_val
            results[rule["consequent"]] = max(results.get(rule["consequent"], 0), output_val)
        return results

    def defuzzify(self, output_set: str) -> float:
        if output_set not in self._sets:
            return 0.5
        total = 0.0
        weight_sum = 0.0
        for label, membership in self._sets[output_set].items():
            if isinstance(membership, dict):
                center = membership.get("center", 0.5)
            else:
                center = float(label) if label.replace(".", "").isdigit() else 0.5
            total += center * membership
            weight_sum += membership
        return total / max(0.001, weight_sum)


class NeuralReasoningEngine:
    def __init__(self):
        self.propositional = PropositionalLogic()
        self.bayesian = BayesianNetwork()
        self.causal = CausalEngine()
        self.fuzzy = FuzzyLogic()
        self._inference_history: list[dict] = []
        self._stats = defaultdict(int)

    def reason(self, problem: str, logic_type: LogicType = LogicType.PROPOSITIONAL,
               inference_type: InferenceType = InferenceType.FORWARD) -> InferenceResult:
        start = time.time()
        self._stats[logic_type.value] += 1
        if logic_type == LogicType.PROPOSITIONAL:
            result = self.propositional.deductive_reasoning([problem])
        elif logic_type == LogicType.BAYESIAN:
            query_result = self.bayesian.query(problem)
            result = InferenceResult(
                query=problem,
                conclusion=f"P({problem}) = {query_result['posterior']:.3f}",
                confidence=query_result["posterior"],
                inference_type=inference_type,
                duration=time.time() - start,
            )
        elif logic_type == LogicType.FUZZY:
            fuzzy_result = self.fuzzy.infer({"input": 0.5})
            result = InferenceResult(
                query=problem,
                conclusion=f"Fuzzy inference: {fuzzy_result}",
                confidence=0.6,
                inference_type=inference_type,
                duration=time.time() - start,
            )
        else:
            result = InferenceResult(
                query=problem,
                conclusion=f"Neural-symbolic reasoning for: {problem}",
                confidence=0.5,
                inference_type=inference_type,
                duration=time.time() - start,
            )
        self._inference_history.append({
            "problem": problem,
            "logic_type": logic_type.value,
            "confidence": result.confidence,
            "duration": result.duration,
        })
        return result

    def get_stats(self) -> dict:
        return {
            "logic_usage": dict(self._stats),
            "total_inferences": len(self._inference_history),
            "avg_confidence": sum(r["confidence"] for r in self._inference_history) / max(1, len(self._inference_history)),
            "avg_duration": sum(r["duration"] for r in self._inference_history) / max(1, len(self._inference_history)),
            "causal": self.causal.get_stats(),
        }
