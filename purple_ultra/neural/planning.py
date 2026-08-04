"""Neural planning engine with goal decomposition, action sequencing, and adaptive replanning."""

from __future__ import annotations

import time
import math
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from enum import Enum
from collections import defaultdict


class PlanStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    REPLANNING = "replanning"


class GoalPriority(Enum):
    CRITICAL = 4
    HIGH = 3
    MEDIUM = 2
    LOW = 1


@dataclass
class Action:
    action_id: str
    name: str
    description: str
    preconditions: list[str] = field(default_factory=list)
    effects: list[str] = field(default_factory=list)
    cost: float = 1.0
    duration: float = 0.0
    parameters: dict[str, Any] = field(default_factory=dict)
    status: PlanStatus = PlanStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    retry_count: int = 0
    max_retries: int = 3


@dataclass
class Goal:
    goal_id: str
    name: str
    description: str
    priority: GoalPriority = GoalPriority.MEDIUM
    preconditions: list[str] = field(default_factory=list)
    desired_effects: list[str] = field(default_factory=list)
    deadline: Optional[float] = None
    status: PlanStatus = PlanStatus.PENDING
    sub_goals: list[str] = field(default_factory=list)
    progress: float = 0.0


@dataclass
class Plan:
    plan_id: str
    goal: Goal
    actions: list[Action] = field(default_factory=list)
    status: PlanStatus = PlanStatus.PENDING
    total_cost: float = 0.0
    estimated_duration: float = 0.0
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    replan_count: int = 0
    metadata: dict = field(default_factory=dict)


@dataclass
class WorldState:
    facts: dict[str, bool] = field(default_factory=dict)
    variables: dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

    def add_fact(self, fact: str, value: bool = True):
        self.facts[fact] = value
        self.timestamp = time.time()

    def check_fact(self, fact: str) -> bool:
        return self.facts.get(fact, False)

    def apply_effects(self, effects: list[str]):
        for effect in effects:
            if effect.startswith("not_"):
                self.facts[effect[4:]] = False
            else:
                self.facts[effect] = True
        self.timestamp = time.time()

    def clone(self) -> WorldState:
        return WorldState(
            facts=self.facts.copy(),
            variables=self.variables.copy(),
            timestamp=self.timestamp,
        )


class ActionLibrary:
    def __init__(self):
        self._actions: dict[str, Action] = {}
        self._templates: dict[str, dict] = {}

    def register_action(self, action: Action):
        self._actions[action.action_id] = action

    def register_template(self, name: str, template: dict):
        self._templates[name] = template

    def get_action(self, action_id: str) -> Optional[Action]:
        return self._actions.get(action_id)

    def find_actions_for_goal(self, goal: Goal) -> list[Action]:
        matching = []
        for action in self._actions.values():
            if any(effect in goal.desired_effects for effect in action.effects):
                matching.append(action)
            elif any(premise in goal.preconditions for premise in action.preconditions):
                matching.append(action)
        return sorted(matching, key=lambda a: a.cost)

    def create_action_from_template(self, template_name: str, **params) -> Optional[Action]:
        template = self._templates.get(template_name)
        if not template:
            return None
        action_id = hashlib.md5(f"{template_name}_{time.time()}".encode()).hexdigest()[:8]
        return Action(
            action_id=action_id,
            name=template.get("name", template_name),
            description=template.get("description", ""),
            preconditions=template.get("preconditions", []),
            effects=template.get("effects", []),
            cost=template.get("cost", 1.0),
            duration=template.get("duration", 0.0),
            parameters=params,
        )

    def list_actions(self) -> list[dict]:
        return [
            {
                "id": a.action_id,
                "name": a.name,
                "cost": a.cost,
                "effects": a.effects,
            }
            for a in self._actions.values()
        ]


class Planner:
    def __init__(self, action_library: ActionLibrary = None):
        self.action_library = action_library or ActionLibrary()
        self._plans: dict[str, Plan] = {}
        self._plan_history: list[dict] = []

    def create_plan(self, goal: Goal, world_state: WorldState) -> Plan:
        plan_id = hashlib.md5(f"{goal.goal_id}_{time.time()}".encode()).hexdigest()[:12]
        plan = Plan(
            plan_id=plan_id,
            goal=goal,
            status=PlanStatus.IN_PROGRESS,
            start_time=time.time(),
        )
        plan.actions = self._decompose_goal(goal, world_state)
        plan.total_cost = sum(a.cost for a in plan.actions)
        plan.estimated_duration = sum(a.duration for a in plan.actions)
        self._plans[plan_id] = plan
        return plan

    def _decompose_goal(self, goal: Goal, world_state: WorldState) -> list[Action]:
        actions = []
        for effect in goal.desired_effects:
            if not world_state.check_fact(effect):
                matching_actions = [
                    a for a in self.action_library._actions.values()
                    if effect in a.effects
                ]
                if matching_actions:
                    best_action = min(matching_actions, key=lambda a: a.cost)
                    actions.append(Action(
                        action_id=best_action.action_id,
                        name=best_action.name,
                        description=best_action.description,
                        preconditions=best_action.preconditions,
                        effects=best_action.effects,
                        cost=best_action.cost,
                        duration=best_action.duration,
                    ))
                else:
                    actions.append(Action(
                        action_id=hashlib.md5(f"create_{effect}".encode()).hexdigest()[:8],
                        name=f"achieve_{effect}",
                        description=f"Create action to achieve {effect}",
                        effects=[effect],
                        cost=2.0,
                    ))
        for precond in goal.preconditions:
            if not world_state.check_fact(precond):
                actions.insert(0, Action(
                    action_id=hashlib.md5(f"setup_{precond}".encode()).hexdigest()[:8],
                    name=f"establish_{precond}",
                    description=f"Establish precondition {precond}",
                    effects=[precond],
                    cost=1.5,
                ))
        return actions

    def execute_plan(self, plan_id: str, world_state: WorldState) -> dict:
        plan = self._plans.get(plan_id)
        if not plan:
            return {"error": "Plan not found"}
        results = []
        for action in plan.actions:
            if action.status == PlanStatus.COMPLETED:
                continue
            preconditions_met = all(world_state.check_fact(p) for p in action.preconditions)
            if not preconditions_met:
                action.status = PlanStatus.FAILED
                results.append({"action": action.name, "status": "failed", "reason": "preconditions not met"})
                continue
            action.status = PlanStatus.IN_PROGRESS
            action.start_time = time.time()
            world_state.apply_effects(action.effects)
            action.status = PlanStatus.COMPLETED
            action.end_time = time.time()
            results.append({"action": action.name, "status": "completed", "duration": action.end_time - action.start_time})
        plan.status = PlanStatus.COMPLETED
        plan.end_time = time.time()
        self._plan_history.append({
            "plan_id": plan_id,
            "goal": plan.goal.name,
            "actions_completed": sum(1 for a in plan.actions if a.status == PlanStatus.COMPLETED),
            "total_actions": len(plan.actions),
            "duration": plan.end_time - plan.start_time,
        })
        return {"plan_id": plan_id, "results": results, "status": plan.status.value}

    def replan(self, plan_id: str, world_state: WorldState, reason: str = "") -> Plan:
        old_plan = self._plans.get(plan_id)
        if not old_plan:
            return None
        old_plan.status = PlanStatus.REPLANNING
        new_goal = old_plan.goal
        new_goal.status = PlanStatus.PENDING
        new_plan = self.create_plan(new_goal, world_state)
        new_plan.replan_count = old_plan.replan_count + 1
        new_plan.metadata["replan_reason"] = reason
        new_plan.metadata["original_plan"] = plan_id
        return new_plan

    def get_plan(self, plan_id: str) -> Optional[Plan]:
        return self._plans.get(plan_id)

    def get_stats(self) -> dict:
        plans = list(self._plans.values())
        return {
            "total_plans": len(plans),
            "completed": sum(1 for p in plans if p.status == PlanStatus.COMPLETED),
            "in_progress": sum(1 for p in plans if p.status == PlanStatus.IN_PROGRESS),
            "failed": sum(1 for p in plans if p.status == PlanStatus.FAILED),
            "replanned": sum(1 for p in plans if p.replan_count > 0),
            "avg_actions_per_plan": sum(len(p.actions) for p in plans) / max(1, len(plans)),
        }


class AdaptivePlanner:
    def __init__(self):
        self.planner = Planner()
        self.world_state = WorldState()
        self._learning_rate = 0.1
        self._action_performance: dict[str, list[float]] = defaultdict(list)
        self._replan_threshold = 0.3

    def plan_and_execute(self, goal: Goal) -> dict:
        plan = self.planner.create_plan(goal, self.world_state)
        result = self.planner.execute_plan(plan.plan_id, self.world_state)
        if result.get("status") != "completed":
            failed_actions = [r for r in result.get("results", []) if r.get("status") == "failed"]
            if failed_actions:
                self._learn_from_failure(plan, failed_actions)
                new_plan = self.planner.replan(plan.plan_id, self.world_state, reason=str(failed_actions))
                if new_plan:
                    result = self.planner.execute_plan(new_plan.plan_id, self.world_state)
        return result

    def _learn_from_failure(self, plan: Plan, failures: list[dict]):
        for failure in failures:
            action_name = failure.get("action", "")
            self._action_performance[action_name].append(0.0)
            if len(self._action_performance[action_name]) > 100:
                self._action_performance[action_name].pop(0)

    def record_success(self, action_name: str, duration: float = 0.0):
        performance = max(0.0, 1.0 - duration / 10.0)
        self._action_performance[action_name].append(performance)

    def get_action_reliability(self, action_name: str) -> float:
        history = self._action_performance.get(action_name, [])
        if not history:
            return 0.5
        return sum(history) / len(history)

    def optimize_plan(self, plan: Plan) -> Plan:
        for action in plan.actions:
            reliability = self.get_action_reliability(action.name)
            if reliability < self._replan_threshold:
                action.cost *= 1.5
        plan.actions.sort(key=lambda a: a.cost)
        plan.total_cost = sum(a.cost for a in plan.actions)
        return plan

    def get_stats(self) -> dict:
        planner_stats = self.planner.get_stats()
        return {
            **planner_stats,
            "world_facts": len(self.world_state.facts),
            "action_reliability": {
                name: self.get_action_reliability(name)
                for name in list(self._action_performance.keys())[:10]
            },
        }
