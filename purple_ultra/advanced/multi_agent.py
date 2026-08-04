"""Multi-agent system with collaborative AI agents."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any
from enum import Enum
from collections import deque


class AgentRole(Enum):
    COORDINATOR = "coordinator"
    RESEARCHER = "researcher"
    CODER = "coder"
    ANALYZER = "analyzer"
    PLANNER = "planner"
    EXECUTOR = "executor"
    CRITIC = "critic"
    SUMMARIZER = "summarizer"
    TRANSLATOR = "translator"
    SPECIALIST = "specialist"


class AgentState(Enum):
    IDLE = "idle"
    THINKING = "thinking"
    WORKING = "working"
    WAITING = "waiting"
    ERROR = "error"


@dataclass
class AgentMessage:
    sender: str
    receiver: str
    content: str
    msg_type: str = "info"
    priority: int = 5
    timestamp: float = field(default_factory=time.time)
    msg_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])


@dataclass
class AgentTask:
    task_id: str
    description: str
    assigned_to: str = ""
    status: str = "pending"
    result: str = ""
    dependencies: list[str] = field(default_factory=list)
    priority: int = 5
    created_at: float = field(default_factory=time.time)
    completed_at: float = 0


class AIAgent:
    def __init__(self, name: str, role: AgentRole, capabilities: list[str] = None):
        self.name = name
        self.role = role
        self.capabilities = capabilities or []
        self.state = AgentState.IDLE
        self.memory: deque = deque(maxlen=100)
        self.knowledge: dict[str, Any] = {}
        self._message_queue: deque[AgentMessage] = deque()
        self._task_history: list[AgentTask] = []
        self._performance_metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_completion_time": 0,
            "success_rate": 0,
        }

    def receive_message(self, message: AgentMessage):
        self._message_queue.append(message)

    def process_messages(self) -> list[AgentMessage]:
        responses = []
        while self._message_queue:
            msg = self._message_queue.popleft()
            response = self._handle_message(msg)
            if response:
                responses.append(response)
        return responses

    def _handle_message(self, message: AgentMessage) -> AgentMessage | None:
        self.memory.append({"type": "received", "content": message.content, "time": time.time()})
        if message.msg_type == "task":
            return AgentMessage(
                sender=self.name, receiver=message.sender,
                content=f"Received task: {message.content}",
                msg_type="ack",
            )
        return None

    def execute_task(self, task: AgentTask, context: dict = None) -> str:
        self.state = AgentState.WORKING
        task.assigned_to = self.name
        task.status = "in_progress"
        start_time = time.time()
        try:
            result = self._process_task(task, context or {})
            task.result = result
            task.status = "completed"
            task.completed_at = time.time()
            self._performance_metrics["tasks_completed"] += 1
            elapsed = task.completed_at - start_time
            count = self._performance_metrics["tasks_completed"]
            self._performance_metrics["avg_completion_time"] = (
                self._performance_metrics["avg_completion_time"] * (count - 1) + elapsed
            ) / count
            self.state = AgentState.IDLE
        except Exception as e:
            task.result = f"Error: {e}"
            task.status = "failed"
            self._performance_metrics["tasks_failed"] += 1
            self.state = AgentState.ERROR
        self._task_history.append(task)
        return task.result

    def _process_task(self, task: AgentTask, context: dict) -> str:
        return f"Agent {self.name} processed: {task.description[:100]}"

    def collaborate(self, other_agents: list[AIAgent], message: str) -> list[AgentMessage]:
        responses = []
        for agent in other_agents:
            if agent.name != self.name:
                msg = AgentMessage(sender=self.name, receiver=agent.name, content=message, msg_type="collab")
                agent.receive_message(msg)
                agent_responses = agent.process_messages()
                responses.extend(agent_responses)
        return responses

    def get_metrics(self) -> dict:
        total = self._performance_metrics["tasks_completed"] + self._performance_metrics["tasks_failed"]
        self._performance_metrics["success_rate"] = (
            self._performance_metrics["tasks_completed"] / total if total > 0 else 0
        )
        return dict(self._performance_metrics)


class AgentTeam:
    def __init__(self, name: str):
        self.name = name
        self.agents: dict[str, AIAgent] = {}
        self._shared_memory: list[dict] = []
        self._task_queue: list[AgentTask] = []
        self._completed_tasks: list[AgentTask] = []
        self._communication_log: list[AgentMessage] = []

    def add_agent(self, agent: AIAgent):
        self.agents[agent.name] = agent

    def remove_agent(self, name: str):
        if name in self.agents:
            del self.agents[name]

    def assign_task(self, task: AgentTask, agent_name: str = None) -> str:
        if agent_name and agent_name in self.agents:
            task.assigned_to = agent_name
            self._task_queue.append(task)
            return f"Task assigned to {agent_name}"
        best_agent = self._find_best_agent(task)
        if best_agent:
            task.assigned_to = best_agent.name
            self._task_queue.append(task)
            return f"Task assigned to {best_agent.name}"
        return "No suitable agent found"

    def _find_best_agent(self, task: AgentTask) -> AIAgent | None:
        best = None
        best_score = -1
        for agent in self.agents.values():
            if agent.state == AgentState.IDLE:
                score = len(set(task.description.lower().split()) & set(agent.capabilities))
                metrics = agent.get_metrics()
                score += metrics["success_rate"] * 10
                if score > best_score:
                    best_score = score
                    best = agent
        return best

    def process_queue(self) -> list[str]:
        results = []
        for task in list(self._task_queue):
            if task.status == "pending" and task.assigned_to:
                agent = self.agents.get(task.assigned_to)
                if agent and agent.state == AgentState.IDLE:
                    result = agent.execute_task(task)
                    results.append(f"{task.assigned_to}: {result[:200]}")
                    if task.status == "completed":
                        self._completed_tasks.append(task)
                        self._task_queue.remove(task)
        return results

    def broadcast(self, message: str, sender: str = "coordinator") -> list[AgentMessage]:
        responses = []
        for name, agent in self.agents.items():
            if name != sender:
                msg = AgentMessage(sender=sender, receiver=name, content=message, msg_type="broadcast")
                agent.receive_message(msg)
        for agent in self.agents.values():
            agent_responses = agent.process_messages()
            responses.extend(agent_responses)
        self._communication_log.extend(responses)
        return responses

    def get_status(self) -> dict:
        return {
            "team": self.name,
            "agents": len(self.agents),
            "idle": sum(1 for a in self.agents.values() if a.state == AgentState.IDLE),
            "working": sum(1 for a in self.agents.values() if a.state == AgentState.WORKING),
            "queue_size": len(self._task_queue),
            "completed": len(self._completed_tasks),
        }

    def get_agent_metrics(self) -> dict:
        return {name: agent.get_metrics() for name, agent in self.agents.items()}


class MultiAgentSystem:
    def __init__(self):
        self.teams: dict[str, AgentTeam] = {}
        self._global_memory: list[dict] = []
        self._coordination_log: list[dict] = []

    def create_team(self, name: str) -> AgentTeam:
        team = AgentTeam(name)
        self.teams[name] = team
        return team

    def get_team(self, name: str) -> AgentTeam | None:
        return self.teams.get(name)

    def coordinate_teams(self, message: str) -> dict:
        results = {}
        for name, team in self.teams.items():
            responses = team.broadcast(message)
            results[name] = len(responses)
        self._coordination_log.append({"message": message, "results": results, "time": time.time()})
        return results

    def get_status(self) -> dict:
        total_agents = sum(len(t.agents) for t in self.teams.values())
        total_tasks = sum(len(t._task_queue) for t in self.teams.values())
        return {
            "teams": len(self.teams),
            "total_agents": total_agents,
            "pending_tasks": total_tasks,
            "global_memory": len(self._global_memory),
        }
