"""Neural integrator - ties all neural components together with advanced thinking capabilities."""

from __future__ import annotations

from typing import Any

from .core import NeuralEngine, DeviceManager, ModelRegistry
from .embeddings import EmbeddingEngine, SemanticMemory
from .text_gen import TextGenerator, DialogueGenerator, Summarizer, Translator
from .voice import NeuralVoiceSynth
from .speech import NeuralSpeechRecognizer
from .vision import NeuralImageRecognizer, FaceRecognizer
from .classifier import NeuralSentimentClassifier, NeuralIntentClassifier, NeuralNER
from .recommender import NeuralRecommender
from .anomaly import NeuralAnomalyDetector, PatternDetector
from .training import NeuralTrainingPipeline
from .thinking import NeuralAttention, ChainOfThought, CognitiveModel, ThinkingMode
from .reasoning import NeuralReasoningEngine, LogicType, InferenceType
from .planning import AdaptivePlanner, ActionLibrary, Goal, GoalPriority, Action


class NeuralSystem:
    """Unified neural system integrating all neural capabilities with advanced thinking."""

    def __init__(self, config: dict = None):
        config = config or {}

        self.core = NeuralEngine(models_dir=config.get("models_dir", "models"))

        self.embeddings = EmbeddingEngine(
            model_name=config.get("embedding_model", "all-MiniLM-L6-v2"),
            cache_dir=config.get("embedding_cache", "models/embeddings"),
        )
        self.semantic_memory = SemanticMemory(self.embeddings)

        self.text_generator = TextGenerator(
            model_name=config.get("text_model", "gpt2"),
            device=self.core.device_manager.device,
        )
        self.dialogue = DialogueGenerator(self.text_generator)
        self.summarizer = Summarizer(self.text_generator)
        self.translator = Translator(self.text_generator)

        self.voice = NeuralVoiceSynth(model_dir=config.get("voice_dir", "models/voice"))
        self.speech = NeuralSpeechRecognizer(
            model_name=config.get("whisper_model", "Systran/faster-whisper-small.en"),
            device=self.core.device_manager.device,
        )

        self.vision = NeuralImageRecognizer(model_dir=config.get("vision_dir", "models/vision"))
        self.face_recognizer = FaceRecognizer(faces_dir=config.get("faces_dir", "memory/faces"))

        self.sentiment = NeuralSentimentClassifier()
        self.intent = NeuralIntentClassifier()
        self.ner = NeuralNER()

        self.recommender = NeuralRecommender(memory_dir=config.get("memory_dir", "memory"))
        self.anomaly_detector = NeuralAnomalyDetector()
        self.pattern_detector = PatternDetector()

        self.training = NeuralTrainingPipeline(training_dir=config.get("training_dir", "training"))

        self.attention = NeuralAttention(
            dim=config.get("attention_dim", 768),
            num_heads=config.get("attention_heads", 12),
        )
        self.chain_of_thought = ChainOfThought(
            max_depth=config.get("cot_depth", 10),
            min_confidence=config.get("cot_min_confidence", 0.3),
        )
        self.cognitive = CognitiveModel()

        self.reasoning = NeuralReasoningEngine()
        self.planner = AdaptivePlanner()
        self.action_library = ActionLibrary()
        self._setup_default_actions()

    def _setup_default_actions(self):
        actions = [
            ("search", "Search for information", ["has_query"], ["has_results"], 0.5, 2.0),
            ("analyze", "Analyze data or code", ["has_data"], ["has_analysis"], 1.0, 5.0),
            ("create", "Create new content", ["has_idea"], ["has_content"], 1.5, 10.0),
            ("communicate", "Send message or response", ["has_recipient", "has_message"], ["message_sent"], 0.3, 1.0),
            ("learn", "Learn from experience", ["has_experience"], ["knowledge_gained"], 0.8, 3.0),
            ("decide", "Make a decision", ["has_options"], ["decision_made"], 0.6, 2.0),
            ("plan", "Create a plan", ["has_goal"], ["has_plan"], 0.7, 3.0),
            ("execute", "Execute an action", ["has_plan", "preconditions_met"], ["action_completed"], 1.0, 5.0),
        ]
        for name, desc, pre, eff, cost, dur in actions:
            action = Action(
                action_id=name,
                name=name,
                description=desc,
                preconditions=pre,
                effects=eff,
                cost=cost,
                duration=dur,
            )
            self.action_library.register_action(action)

    def think(self, problem: str, mode: str = "deliberate", max_steps: int = None) -> dict:
        thinking_mode = ThinkingMode(mode) if mode in [m.value for m in ThinkingMode] else ThinkingMode.DELIBERATE
        chain = self.chain_of_thought.solve(problem, max_steps=max_steps, mode=thinking_mode)
        return {
            "chain_id": chain.chain_id,
            "solution": chain.get_final_answer(),
            "confidence": chain.total_confidence,
            "steps": len(chain.steps),
            "trace": chain.get_reasoning_trace(),
            "duration": chain.end_time - chain.start_time if chain.end_time else 0,
        }

    def reason(self, problem: str, logic_type: str = "propositional") -> dict:
        lt = LogicType(logic_type) if logic_type in [l.value for l in LogicType] else LogicType.PROPOSITIONAL
        result = self.reasoning.reason(problem, logic_type=lt)
        return {
            "query": result.query,
            "conclusion": result.conclusion,
            "confidence": result.confidence,
            "logic_type": logic_type,
            "duration": result.duration,
        }

    def plan(self, goal_name: str, description: str = "", effects: list[str] = None,
             preconditions: list[str] = None, priority: str = "medium") -> dict:
        priority_map = {"CRITICAL": GoalPriority.CRITICAL, "HIGH": GoalPriority.HIGH, 
                       "MEDIUM": GoalPriority.MEDIUM, "LOW": GoalPriority.LOW}
        goal_priority = priority_map.get(priority.upper(), GoalPriority.MEDIUM)
        goal = Goal(
            goal_id=goal_name.lower().replace(" ", "_"),
            name=goal_name,
            description=description,
            priority=goal_priority,
            desired_effects=effects or [],
            preconditions=preconditions or [],
        )
        result = self.planner.plan_and_execute(goal)
        return {
            "goal": goal_name,
            "status": result.get("status", "unknown"),
            "results": result.get("results", []),
            "plan_stats": self.planner.get_stats(),
        }

    def self_attention(self, sequence: list[str]) -> dict:
        embeddings = {}
        for token in sequence:
            emb = self.embeddings.encode(token)
            if hasattr(emb, 'tolist'):
                emb = emb.tolist()
            embeddings[token] = emb
        return self.attention.self_attention(sequence, embeddings)

    def cross_attention(self, query: str, contexts: list[str]) -> list[dict]:
        embeddings = {}
        all_texts = [query] + contexts
        for text in all_texts:
            emb = self.embeddings.encode(text)
            if hasattr(emb, 'tolist'):
                emb = emb.tolist()
            embeddings[text] = emb
        results = self.attention.cross_attention(query, contexts, embeddings)
        return [{"key": r.key, "weight": r.weight, "context": r.context} for r in results]

    def cognitive_reflect(self) -> dict:
        return self.cognitive.metacognitive_reflect()

    def learn_action(self, action_name: str, success: bool, duration: float = 0.0):
        if success:
            self.planner.record_success(action_name, duration)

    def get_thinking_status(self) -> dict:
        return {
            "attention": {
                "dim": self.attention.dim,
                "heads": self.attention.num_heads,
                "cache_size": len(self.attention._attention_cache),
            },
            "chain_of_thought": self.chain_of_thought.get_stats(),
            "cognitive": self.cognitive.get_stats(),
            "reasoning": self.reasoning.get_stats(),
            "planning": self.planner.get_stats(),
        }

    def get_status(self) -> dict:
        return {
            "core": self.core.get_status(),
            "embeddings": self.embeddings.get_stats(),
            "semantic_memory": {"entries": self.semantic_memory._engine.size() if hasattr(self.semantic_memory, '_engine') else 0},
            "text_generator": self.text_generator.get_status(),
            "voice": self.voice.get_status(),
            "speech": self.speech.get_status(),
            "vision": self.vision.get_status(),
            "anomaly": self.anomaly_detector.get_stats(),
            "recommender": self.recommender.get_stats(),
            "training": self.training.get_status(),
            "thinking": self.get_thinking_status(),
        }

    def shutdown(self):
        self.core.model_registry.unload_all()
