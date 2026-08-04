"""Advanced system integrator - ties all advanced capabilities together."""

from __future__ import annotations

from .multi_agent import MultiAgentSystem, AIAgent, AgentRole
from .memory import HierarchicalMemory, MemoryReplay
from .rlhf import RLHFSystem
from .reasoning import TreeOfThought, GraphOfThought, MetacognitiveReasoner
from .security import DifferentialPrivacy, Encryption, SecureStorage, SecurityAudit
from .optimization import ModelOptimizer, AutoMLEngine
from .streaming import StreamProcessor, WindowAggregator
from .meta_learning import FewShotLearner, MetaLearner, TransferLearner


class AdvancedSystem:
    """Unified advanced system integrating all next-generation capabilities."""

    def __init__(self, config: dict = None):
        config = config or {}

        self.multi_agent = MultiAgentSystem()
        self._setup_default_agents()

        self.memory = HierarchicalMemory(
            memory_dir=config.get("memory_dir", "memory/advanced")
        )
        self.memory_replay = MemoryReplay(self.memory)

        self.rlhf = RLHFSystem(
            memory_dir=config.get("rlhf_dir", "memory/rlhf")
        )

        self.tree_of_thought = TreeOfThought(
            max_depth=config.get("tot_depth", 5),
            branch_factor=config.get("tot_branch", 3),
        )
        self.graph_of_thought = GraphOfThought()
        self.metacognition = MetacognitiveReasoner()

        self.differential_privacy = DifferentialPrivacy(
            epsilon=config.get("privacy_epsilon", 1.0)
        )
        self.encryption = Encryption()
        self.secure_storage = SecureStorage(
            storage_dir=config.get("secure_dir", "data/secure")
        )
        self.security_audit = SecurityAudit()

        self.optimizer = ModelOptimizer(
            output_dir=config.get("optimized_dir", "models/optimized")
        )
        self.automl = AutoMLEngine()

        self.stream_processor = StreamProcessor()
        self.window_aggregator = WindowAggregator(
            window_size=config.get("window_size", 60)
        )

        self.few_shot = FewShotLearner(
            memory_dir=config.get("fewshot_dir", "memory/fewshot")
        )
        self.meta_learner = MetaLearner()
        self.transfer_learner = TransferLearner()

    def _setup_default_agents(self):
        coordinator = AIAgent("coordinator", AgentRole.COORDINATOR, ["planning", "coordination"])
        researcher = AIAgent("researcher", AgentRole.RESEARCHER, ["research", "analysis", "information"])
        coder = AIAgent("coder", AgentRole.CODER, ["coding", "programming", "debugging"])
        analyzer = AIAgent("analyzer", AgentRole.ANALYZER, ["analysis", "data", "statistics"])
        planner = AIAgent("planner", AgentRole.PLANNER, ["planning", "strategy", "organization"])
        executor = AIAgent("executor", AgentRole.EXECUTOR, ["execution", "implementation", "action"])
        critic = AIAgent("critic", AgentRole.CRITIC, ["review", "feedback", "evaluation"])
        summarizer = AIAgent("summarizer", AgentRole.SUMMARIZER, ["summarization", "compression"])

        team = self.multi_agent.create_team("main")
        for agent in [coordinator, researcher, coder, analyzer, planner, executor, critic, summarizer]:
            team.add_agent(agent)

    def process_with_reasoning(self, problem: str) -> dict:
        strategy = self.metacognition.select_strategy(problem)
        if strategy == "tree_of_thought":
            result = self.tree_of_thought.solve(problem)
        elif strategy == "graph_of_thought":
            result = self.graph_of_thought.solve(problem)
        else:
            result = {"solution": problem, "path": [problem], "score": 0.5, "nodes_explored": 1}
        self.metacognition.reflect(problem, result.get("solution", ""), strategy)
        return {"strategy": strategy, "result": result}

    def store_memory(self, content: str, importance: float = 0.5, emotion: str = "neutral"):
        self.memory.store(content, importance, emotion)
        self.security_audit.log_access("memory", "store")

    def recall_memory(self, query: str, top_k: int = 5) -> list[dict]:
        self.security_audit.log_access("memory", "recall")
        return self.memory.recall(query, top_k)

    def add_feedback(self, prompt: str, response: str, rating: float):
        self.rlhf.add_feedback(prompt, response, rating)

    def optimize_response(self, prompt: str, responses: list[str]) -> str:
        return self.rlhf.optimize_response(prompt, responses)

    def secure_store(self, key: str, value: Any):
        self.secure_storage.store(key, value)
        self.security_audit.log_access("secure_storage", "store")

    def secure_retrieve(self, key: str) -> Any:
        self.security_audit.log_access("secure_storage", "retrieve")
        return self.secure_storage.retrieve(key)

    def add_few_shot_example(self, input_text: str, output_text: str, category: str = "general"):
        self.few_shot.add_example(input_text, output_text, category)

    def predict_few_shot(self, input_text: str, category: str = None) -> str:
        return self.few_shot.predict(input_text, category)

    def coordinate_task(self, task: str) -> str:
        team = self.multi_agent.get_team("main")
        if team:
            from .multi_agent import AgentTask
            task_obj = AgentTask(task_id=f"task_{int(time.time())}", description=task)
            result = team.assign_task(task_obj)
            team.process_queue()
            return result
        return "No team available"

    def get_status(self) -> dict:
        return {
            "multi_agent": self.multi_agent.get_status(),
            "memory": self.memory.get_stats(),
            "memory_health": self.memory.get_health(),
            "rlhf": self.rlhf.get_feedback_stats(),
            "reasoning": {
                "tree_of_thought": self.tree_of_thought.get_stats(),
                "graph_of_thought": self.graph_of_thought.get_stats(),
                "metacognition": self.metacognition.get_performance(),
            },
            "security": {
                "privacy": self.differential_privacy.privacy_accountant(),
                "audit": self.security_audit.get_stats(),
            },
            "optimization": self.optimizer.get_stats(),
            "streaming": self.stream_processor.get_status(),
            "meta_learning": {
                "few_shot": self.few_shot.get_stats(),
                "meta": self.meta_learner.get_global_stats(),
                "transfer": self.transfer_learner.get_stats(),
            },
        }

    def shutdown(self):
        self.memory._save()
        self.rlhf._save()
        self.few_shot._save()
        self.secure_storage._save()
