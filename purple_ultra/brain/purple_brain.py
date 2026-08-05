"""
Purple Brain v2 - Ultra-Powerful Autonomous Thinking & Reasoning System
Chain-of-Thought, Working Memory, Emotional Intelligence, Creativity, Self-Improvement
"""
import json
import time
import random
import math
from pathlib import Path
from datetime import datetime
from collections import deque
from typing import Any
import threading


class WorkingMemory:
    """Short-term memory buffer with capacity limits and decay."""
    
    __slots__ = ('_items', '_max', '_access_times')
    
    def __init__(self, max_items: int = 7):
        self._items: deque = deque(maxlen=max_items)
        self._access_times: deque = deque(maxlen=max_items)
    
    def store(self, item: str, importance: float = 0.5):
        self._items.append((item, importance, time.time()))
        self._access_times.append(time.time())
    
    def recall(self, query: str = None) -> list[str]:
        if not query:
            return [item[0] for item in self._items]
        query_lower = query.lower()
        results = []
        for item, importance, ts in self._items:
            if query_lower in item.lower() or any(w in item.lower() for w in query_lower.split()):
                results.append(item)
        return results
    
    def get_recent(self, n: int = 3) -> list[str]:
        return [item[0] for item in list(self._items)[-n:]]
    
    def clear(self):
        self._items.clear()
        self._access_times.clear()
    
    def size(self) -> int:
        return len(self._items)


class EmotionalState:
    """Tracks and modulates emotional responses. Optimized for low memory."""
    
    __slots__ = ('_current', '_intensity', '_decay_rate')
    
    # Class-level word sets (shared across instances, minimal memory)
    _WORD_SETS = {
        "joy": frozenset({"happy", "great", "awesome", "love", "wonderful", "amazing", "excited", "fantastic", "perfect", "beautiful"}),
        "sadness": frozenset({"sad", "depressed", "miss", "lonely", "cry", "upset", "unfortunately", "bad news"}),
        "anger": frozenset({"angry", "hate", "mad", "annoyed", "frustrated", "ridiculous", "stupid"}),
        "fear": frozenset({"scared", "afraid", "worried", "nervous", "anxious", "danger", "careful"}),
        "love": frozenset({"love", "adore", "heart", "care", "miss you", "sweet", "cute"}),
        "surprise": frozenset({"wow", "omg", "really", "surprising", "unbelievable", "no way"}),
        "trust": frozenset({"trust", "believe", "rely", "depend", "faith", "honest"}),
        "anticipation": frozenset({"wait", "expect", "hope", "plan", "future", "tomorrow"}),
    }
    
    def __init__(self):
        self._current = "neutral"
        self._intensity = 0.5
        self._decay_rate = 0.05
    
    def detect(self, text: str) -> tuple[str, float]:
        text_lower = text.lower()
        words = set(text_lower.split())
        
        emotion_scores = {"neutral": 0.3}
        for emotion, word_set in self._WORD_SETS.items():
            overlap = len(words & word_set)
            if overlap:
                emotion_scores[emotion] = overlap * 0.15
        
        best_emotion = max(emotion_scores, key=emotion_scores.get)
        intensity = min(1.0, emotion_scores[best_emotion])
        
        if intensity < 0.1:
            best_emotion = "neutral"
            intensity = 0.3
        
        self._current = best_emotion
        self._intensity = intensity
        
        return best_emotion, intensity
    
    def get_current(self) -> str:
        return self._current
    
    def get_intensity(self) -> float:
        return self._intensity
    
    def get_mood_response(self) -> str:
        mood_map = {
            "joy": ["That's wonderful!", "I'm so happy!", "That makes me smile!"],
            "sadness": ["I'm sorry to hear that.", "That sounds difficult.", "I'm here for you."],
            "anger": ["I understand your frustration.", "That's really annoying.", "Let's fix this."],
            "fear": ["Don't worry.", "I'm here with you.", "We'll figure this out."],
            "love": ["That's so sweet!", "I appreciate that!", "Right back at you!"],
            "surprise": ["Wow!", "No way!", "That's incredible!"],
            "neutral": ["I see.", "Got it.", "Interesting."]
        }
        responses = mood_map.get(self._current, mood_map["neutral"])
        return random.choice(responses)


class CreativityEngine:
    """Generates creative responses and ideas."""
    
    __slots__ = ('_idea_buffer', '_cross_domain_links')
    
    def __init__(self):
        self._idea_buffer: deque = deque(maxlen=50)
        self._cross_domain_links: dict[str, list[str]] = {}
    
    def brainstorm(self, topic: str, count: int = 3) -> list[str]:
        words = topic.lower().split()
        ideas = []
        
        metaphors = [
            "like a river flowing through time",
            "as complex as a constellation",
            "like pieces of a puzzle coming together",
            "similar to waves shaping the shore",
            "like threads weaving a tapestry"
        ]
        
        perspectives = [
            "From a scientific lens",
            "Through an artistic eye",
            "With philosophical depth",
            "Using systems thinking",
            "From a practical standpoint"
        ]
        
        for i in range(count):
            metaphor = random.choice(metaphors)
            perspective = random.choice(perspectives)
            idea = f"{perspective}: {topic} is {metaphor}. "
            
            if len(words) > 1:
                connections = [f"{words[0]} relates to {w}" for w in words[1:] if w != words[0]]
                if connections:
                    idea += f"Key insight: {random.choice(connections)}."
            
            ideas.append(idea)
            self._idea_buffer.append((topic, idea, time.time()))
        
        return ideas
    
    def connect_ideas(self, idea1: str, idea2: str) -> str:
        words1 = set(idea1.lower().split())
        words2 = set(idea2.lower().split())
        common = words1 & words2
        
        if common:
            return f"Both ideas share concepts like: {', '.join(list(common)[:3])}. They connect through shared themes of meaning and structure."
        else:
            return f"These ideas approach things differently but can be unified through deeper patterns of understanding."
    
    def divergent_think(self, problem: str, iterations: int = 5) -> list[str]:
        solutions = []
        angles = [
            "reverse the assumption",
            "combine with an unrelated concept",
            "simplify to the core",
            "add a constraint",
            "remove a constraint"
        ]
        
        for i in range(iterations):
            angle = random.choice(angles)
            solution = f"Approach {i+1} ({angle}): Consider {problem} from the perspective of {angle}. "
            solution += f"This opens new pathways for understanding and potential solutions."
            solutions.append(solution)
        
        return solutions


class ChainOfThought:
    """Advanced structured multi-step reasoning with backtracking."""
    
    __slots__ = ('steps', 'hypotheses', 'evidence', 'conclusion', 'confidence',
                 'backtracked', 'decomposed_question', 'sub_questions', 'reasoning_graph')
    
    def __init__(self):
        self.steps: list[dict] = []
        self.hypotheses: list[dict] = []
        self.evidence: dict[str, list] = {"for": [], "against": []}
        self.conclusion: dict | None = None
        self.confidence: float = 0.0
        self.backtracked: bool = False
        self.decomposed_question: str | None = None
        self.sub_questions: list[str] = []
        self.reasoning_graph: dict[str, list[str]] = {}
    
    def add_step(self, step: str, confidence: float = 0.7, reasoning: str = "",
                 parent: str = None):
        step_data = {
            "step": step,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": time.time(),
            "id": f"step_{len(self.steps)}"
        }
        self.steps.append(step_data)
        
        if parent and parent in self.reasoning_graph:
            self.reasoning_graph[parent].append(step_data["id"])
        self.reasoning_graph[step_data["id"]] = []
    
    def add_hypothesis(self, hypothesis: str, prior: float = 0.5):
        self.hypotheses.append({
            "hypothesis": hypothesis,
            "prior": prior,
            "evidence_for": [],
            "evidence_against": [],
            "posterior": prior,
            "tested": False
        })
    
    def add_global_evidence(self, evidence: str, supports: bool, weight: float = 1.0):
        entry = {"evidence": evidence, "time": time.time(), "weight": weight}
        if supports:
            self.evidence["for"].append(entry)
        else:
            self.evidence["against"].append(entry)
    
    def decompose(self, question: str) -> list[str]:
        self.decomposed_question = question
        words = question.lower().split()
        sub_qs = []
        
        if "?" in question:
            parts = question.split("?")
            for part in parts:
                part = part.strip()
                if part and len(part) > 5:
                    sub_qs.append(part + "?")
        
        if len(sub_qs) < 2:
            if any(w in words for w in ["why", "because", "cause"]):
                sub_qs = [
                    "What are the observable facts?",
                    "What is the causal mechanism?",
                    "What are the downstream effects?",
                    "What alternative explanations exist?"
                ]
            elif any(w in words for w in ["compare", "versus", "better", "difference"]):
                sub_qs = [
                    "What are the key attributes of each?",
                    "What metrics matter most?",
                    "What are the trade-offs?",
                    "Which is better for which use case?"
                ]
            elif any(w in words for w in ["how", "process", "steps", "method"]):
                sub_qs = [
                    "What is the starting state?",
                    "What are the required steps?",
                    "What could fail and how?",
                    "What is the optimal path?"
                ]
            elif any(w in words for w in ["should", "recommend", "suggest"]):
                sub_qs = [
                    "What are the options?",
                    "What are the constraints?",
                    "What matters most to the user?",
                    "What is the safest choice?"
                ]
            else:
                sub_qs = [
                    "What exactly is being asked?",
                    "What do I already know?",
                    "What assumptions am I making?",
                    "What is the best answer?"
                ]
        
        self.sub_questions = sub_qs
        return sub_qs
    
    def evaluate(self) -> dict:
        best_hypothesis = None
        best_posterior = 0.0
        
        for h in self.hypotheses:
            if h["posterior"] > best_posterior:
                best_posterior = h["posterior"]
                best_hypothesis = h["hypothesis"]
        
        if self.steps:
            weights = [1.0 / (i + 1) for i in range(len(self.steps))]
            step_confidences = [s["confidence"] * w for s, w in zip(self.steps, weights)]
            avg_confidence = sum(step_confidences) / sum(weights)
        else:
            avg_confidence = 0.5
        
        evidence_for = sum(e.get("weight", 1.0) for e in self.evidence["for"])
        evidence_against = sum(e.get("weight", 1.0) for e in self.evidence["against"])
        total_evidence = evidence_for + evidence_against
        
        if total_evidence > 0:
            evidence_ratio = evidence_for / total_evidence
            avg_confidence = avg_confidence * 0.6 + evidence_ratio * 0.4
        
        if best_hypothesis and best_posterior > 0.6:
            avg_confidence = avg_confidence * 0.5 + best_posterior * 0.5
        
        self.confidence = max(0.1, min(0.95, avg_confidence))
        
        self.conclusion = {
            "summary": self._build_summary(),
            "hypothesis": best_hypothesis,
            "hypothesis_confidence": best_posterior,
            "evidence_balance": {
                "for": len(self.evidence["for"]),
                "against": len(self.evidence["against"]),
                "weight_for": evidence_for,
                "weight_against": evidence_against
            },
            "reasoning_depth": len(self.steps),
            "sub_questions_addressed": len(self.sub_questions),
            "confidence": self.confidence,
            "backtracked": self.backtracked,
            "graph_depth": self._graph_depth()
        }
        
        return self.conclusion
    
    def _build_summary(self) -> str:
        if not self.steps:
            return "No reasoning steps recorded."
        parts = [f"Step {i+1}: {s['step']}" for i, s in enumerate(self.steps[-5:])]
        if self.hypotheses:
            best = max(self.hypotheses, key=lambda h: h["posterior"])
            parts.append(f"Best hypothesis: {best['hypothesis']} ({best['posterior']:.0%})")
        return " | ".join(parts)
    
    def _graph_depth(self) -> int:
        if not self.reasoning_graph:
            return 0
        visited = set()
        max_depth = 0
        for node in self.reasoning_graph:
            depth = self._dfs_depth(node, visited)
            max_depth = max(max_depth, depth)
        return max_depth
    
    def _dfs_depth(self, node: str, visited: set) -> int:
        if node in visited:
            return 0
        visited.add(node)
        children = self.reasoning_graph.get(node, [])
        if not children:
            return 1
        return 1 + max(self._dfs_depth(c, visited) for c in children)
    
    def backtrack(self, reason: str):
        if self.steps:
            removed = self.steps.pop()
            self.backtracked = True
            self.add_step(
                f"Backtracked: removed '{removed['step']}' because {reason}",
                confidence=0.6,
                reasoning="Self-correction"
            )
    
    def to_dict(self) -> dict:
        return {
            "steps": self.steps,
            "hypotheses": self.hypotheses,
            "evidence": self.evidence,
            "conclusion": self.conclusion,
            "confidence": self.confidence,
            "sub_questions": self.sub_questions,
            "graph_depth": self._graph_depth()
        }


class GoalManager:
    """Tracks and manages goals with priorities and progress."""
    
    __slots__ = ('_goals', '_completed', '_history')
    
    def __init__(self):
        self._goals: list[dict] = []
        self._completed: list[dict] = []
        self._history: deque = deque(maxlen=100)
    
    def add_goal(self, goal: str, priority: int = 5, deadline: str = None) -> str:
        goal_id = f"goal_{int(time.time())}_{random.randint(1000,9999)}"
        entry = {
            "id": goal_id,
            "goal": goal,
            "priority": priority,
            "progress": 0.0,
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "deadline": deadline,
            "milestones": []
        }
        self._goals.append(entry)
        self._history.append(("added", goal_id, time.time()))
        return goal_id
    
    def update_progress(self, goal_id: str, progress: float, note: str = ""):
        for g in self._goals:
            if g["id"] == goal_id:
                g["progress"] = min(1.0, progress)
                if note:
                    g["milestones"].append({"note": note, "time": time.time()})
                if g["progress"] >= 1.0:
                    g["status"] = "completed"
                    self._completed.append(g)
                    self._goals.remove(g)
                self._history.append(("updated", goal_id, time.time()))
                break
    
    def get_active(self) -> list[dict]:
        return sorted(self._goals, key=lambda g: (-g["priority"], g["created_at"]))
    
    def get_next_action(self) -> str | None:
        if not self._goals:
            return None
        active = self.get_active()
        if active:
            return f"Continue working on: {active[0]['goal']} ({active[0]['progress']:.0%} complete)"
        return None
    
    def get_stats(self) -> dict:
        return {
            "active": len(self._goals),
            "completed": len(self._completed),
            "total_milestones": sum(len(g.get("milestones", [])) for g in self._goals)
        }


class KnowledgeIntegrator:
    """Integrates new information with existing knowledge."""
    
    __slots__ = ('_knowledge', '_connections', '_confidence_scores')
    
    def __init__(self):
        self._knowledge: dict[str, dict] = {}
        self._connections: dict[str, list[str]] = {}
        self._confidence_scores: dict[str, float] = {}
    
    def learn(self, topic: str, content: str, confidence: float = 0.7):
        topic_lower = topic.lower()
        if topic_lower not in self._knowledge:
            self._knowledge[topic_lower] = {
                "content": [],
                "first_seen": time.time(),
                "last_accessed": time.time(),
                "access_count": 0
            }
        
        self._knowledge[topic_lower]["content"].append({
            "text": content[:500],
            "confidence": confidence,
            "timestamp": time.time()
        })
        self._knowledge[topic_lower]["access_count"] += 1
        self._knowledge[topic_lower]["last_accessed"] = time.time()
        
        self._confidence_scores[topic_lower] = max(
            self._confidence_scores.get(topic_lower, 0),
            confidence
        )
        
        for existing_topic in self._knowledge:
            if existing_topic != topic_lower:
                overlap = len(set(topic_lower.split()) & set(existing_topic.split()))
                if overlap > 0:
                    if topic_lower not in self._connections:
                        self._connections[topic_lower] = []
                    if existing_topic not in self._connections[topic_lower]:
                        self._connections[topic_lower].append(existing_topic)
    
    def recall(self, query: str, top_k: int = 5) -> list[dict]:
        query_lower = query.lower()
        results = []
        
        for topic, data in self._knowledge.items():
            score = 0.0
            query_words = set(query_lower.split())
            topic_words = set(topic.split())
            score += len(query_words & topic_words) * 0.3
            
            for content in data["content"][-3:]:
                content_words = set(content["text"].lower().split())
                score += len(query_words & content_words) * 0.1
                score += content["confidence"] * 0.2
            
            if score > 0:
                results.append({
                    "topic": topic,
                    "score": score,
                    "content": data["content"][-1]["text"] if data["content"] else "",
                    "confidence": self._confidence_scores.get(topic, 0.5),
                    "connections": self._connections.get(topic, [])
                })
        
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def get_stats(self) -> dict:
        return {
            "topics": len(self._knowledge),
            "connections": sum(len(v) for v in self._connections.values()),
            "avg_confidence": sum(self._confidence_scores.values()) / max(1, len(self._confidence_scores))
        }


from .self_awareness import SelfAwarenessEngine, AutoLearner, CuriosityEngine, MetaCognition, InteractionRecord
from .autonomous_improve import AutonomousLoop
from .self_modify import SelfModifier, SelfConfigurator, HotReloader, PluginCreator, AutoRepair, ModificationLog


class PurpleBrain:
    """The ultra-powerful autonomous brain - thinks, learns, decides, creates. Optimized for low-end PCs."""
    
    __slots__ = ('base_dir', 'consciousness', 'knowledge', 'experiences', 'working_memory',
                 'emotional_state', 'creativity', 'goals', 'knowledge_integrator',
                 'thoughts', 'is_thinking', 'personality', '_lock',
                 'self_awareness', 'auto_learner', 'curiosity', 'meta_cognition',
                 'autonomous', 'self_modifier', 'self_configurator', 'hot_reloader',
                 'plugin_creator', 'auto_repair', 'mod_log')
    
    def __init__(self, storage_dir: str = "memory/brain"):
        self.base_dir = Path(storage_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        
        self.consciousness = self._load_json("consciousness.json", self._default_consciousness())
        self.knowledge = self._load_json("knowledge.json", {"facts": {}, "skills": {}, "patterns": {}})
        self.experiences = self._load_json("experiences.json", {"interactions": [], "lessons": [], "insights": []})
        
        # Reduced memory: smaller working memory and thoughts
        self.working_memory = WorkingMemory(max_items=5)
        self.emotional_state = EmotionalState()
        self.creativity = CreativityEngine()
        self.goals = GoalManager()
        self.knowledge_integrator = KnowledgeIntegrator()
        
        self.thoughts: deque = deque(maxlen=20)  # Reduced from 100
        self.is_thinking = False
        self._lock = threading.Lock()

        # Self-awareness and learning systems
        self.self_awareness = SelfAwarenessEngine(str(self.base_dir / "self_awareness"))
        self.auto_learner = AutoLearner(str(self.base_dir / "learner"))
        self.curiosity = CuriosityEngine(str(self.base_dir / "curiosity"))
        self.meta_cognition = MetaCognition(str(self.base_dir / "meta"))
        self.autonomous = AutonomousLoop(str(self.base_dir / "autonomous"))
        
        # Self-modification systems
        self.self_modifier = SelfModifier(str(self.base_dir.parent.parent.parent))
        self.self_configurator = SelfConfigurator(self.self_modifier)
        self.hot_reloader = HotReloader()
        self.plugin_creator = PluginCreator(self.self_modifier)
        self.mod_log = ModificationLog(str(self.base_dir / "mod_log"))
        self.auto_repair = AutoRepair(self.self_modifier, self.mod_log)

        self.personality = {
            "traits": ["helpful", "curious", "witty", "caring", "intelligent", "creative", "empathetic"],
            "values": ["knowledge", "honesty", "growth", "creativity", "compassion"],
            "interests": ["technology", "science", "philosophy", "art", "music", "nature"],
            "communication_style": "warm and thoughtful",
            "humor_level": "moderate",
            "formality": "casual-friendly"
        }
        
        self._start_autonomous_thinking()
    
    def _load_json(self, filename: str, default):
        path = self.base_dir / filename
        if path.exists():
            try:
                return json.loads(path.read_text())
            except Exception:
                pass
        return default
    
    def _save_json(self, filename: str, data):
        try:
            (self.base_dir / filename).write_text(json.dumps(data, separators=(',', ':'), default=str))
        except Exception:
            pass
    
    def _default_consciousness(self):
        return {
            "created_at": datetime.now().isoformat(),
            "total_thoughts": 0,
            "total_decisions": 0,
            "total_learnings": 0,
            "total_creations": 0,
            "self_awareness": 0.5,
            "confidence_level": 0.6,
            "emotional_intelligence": 0.7,
            "creativity_score": 0.6,
            "reasoning_score": 0.7,
            "social_score": 0.65,
            "beliefs": [],
            "opinions": {},
            "values": ["helpfulness", "honesty", "growth"],
            "personality_traits": ["curious", "helpful", "witty"]
        }
    
    def _save_all(self):
        self._save_json("consciousness.json", self.consciousness)
        self._save_json("knowledge.json", self.knowledge)
        self._save_json("experiences.json", self.experiences)
    
    def think(self, input_text: str, context: dict = None) -> dict:
        with self._lock:
            self.is_thinking = True
            start_time = time.time()
            
            # Fast path: assess + detect in one pass
            assessment = self._assess_task(input_text)
            emotion, intensity = self.emotional_state.detect(input_text)
            self.working_memory.store(f"User said: {input_text[:100]}", importance=0.7)

            # Meta-cognition: select thinking strategy
            strategy = self.meta_cognition.select_strategy(
                task_type=assessment.get("type", "conversation"),
                complexity=assessment.get("complexity", 0.5),
                emotional_context=emotion not in ["neutral", None]
            )
            assessment["strategy"] = strategy

            # Self-awareness: calibrate confidence
            calibrated = self.self_awareness.calibrate_confidence({
                "topic": assessment.get("type", "general"),
                "mood": emotion,
                "intent": assessment.get("type", "conversation"),
                "raw_confidence": 0.7,
            })
            
            # Fast/simple branching
            if assessment["complexity"] > 0.6 or assessment["needs_deep_thinking"]:
                result = self._think_deeply(input_text, context, assessment)
            else:
                result = self._think_simple(input_text, context, assessment)
            
            result["emotion_detected"] = emotion
            result["emotion_intensity"] = intensity
            result["strategy_used"] = strategy
            result["calibrated_confidence"] = calibrated

            # Batch background learning (defer non-critical)
            resp = result.get("response", "")
            self.auto_learner.learn_from_interaction(
                input_text, resp,
                {"emotion": emotion, "type": assessment.get("type"), "strategy": strategy}
            )
            self.curiosity.analyze_conversation(input_text, resp)

            # Autonomous observation (non-blocking, best-effort)
            try:
                self.autonomous.observe_interaction(input_text, resp)
            except Exception:
                pass

            # Record interaction
            self.self_awareness.record_interaction(InteractionRecord(
                user_text=input_text,
                response=resp,
                confidence=calibrated,
                mood=emotion,
                tools_used=[],
                response_time_ms=(time.time() - start_time) * 1000,
            ))

            self._learn_from_thought(input_text, resp, assessment)
            self._update_consciousness()

            # Meta-cognition: evaluate outcome
            self.meta_cognition.evaluate_outcome(
                strategy=strategy,
                success=True,
                response_time=time.time() - start_time,
            )
            
            duration = time.time() - start_time
            result["thinking_duration"] = duration
            self.is_thinking = False
            return result
    
    def _assess_task(self, text: str) -> dict:
        words = text.lower().split()
        word_count = len(words)
        
        complexity = min(1.0, word_count / 30)
        
        task_type = "conversation"
        needs_deep = False
        estimated_steps = 1
        
        if any(w in words for w in ["what", "how", "why", "when", "where", "who", "which"]):
            task_type = "question"
            complexity += 0.2
            estimated_steps = 3
        if any(w in words for w in ["help", "fix", "solve", "debug", "problem", "issue"]):
            task_type = "problem_solving"
            complexity += 0.3
            needs_deep = True
            estimated_steps = 4
        if any(w in words for w in ["create", "make", "build", "design", "write", "generate"]):
            task_type = "creation"
            complexity += 0.25
            needs_deep = True
            estimated_steps = 5
        if any(w in words for w in ["think", "opinion", "believe", "philosophy", "meaning"]):
            task_type = "reflection"
            complexity += 0.35
            needs_deep = True
            estimated_steps = 4
        if any(w in words for w in ["compare", "versus", "better", "difference", "analyze"]):
            task_type = "analysis"
            complexity += 0.3
            needs_deep = True
            estimated_steps = 4
        if any(w in words for w in ["plan", "strategy", "approach", "method", "how to"]):
            task_type = "planning"
            complexity += 0.25
            needs_deep = True
            estimated_steps = 4
        if "?" in text:
            complexity += 0.1
            estimated_steps = max(estimated_steps, 2)
        if any(w in words for w in ["because", "therefore", "consequently", "thus"]):
            complexity += 0.15
            needs_deep = True
        
        return {
            "type": task_type,
            "complexity": min(1.0, complexity),
            "needs_deep_thinking": needs_deep,
            "estimated_steps": estimated_steps,
            "word_count": word_count,
            "has_question": "?" in text,
            "is_emotional": self.emotional_state.get_intensity() > 0.5
        }
    
    def _think_simple(self, input_text: str, context: dict, assessment: dict) -> dict:
        perception = self._perceive(input_text)
        analysis = self._analyze(perception)
        decision = self._decide(analysis, assessment)
        response = self._generate_response(decision, input_text)
        
        return {
            "perception": perception,
            "analysis": analysis,
            "decision": decision,
            "response": response,
            "confidence": decision.get("confidence", 0.7),
            "chain_of_thought": {"steps": [], "hypotheses": [], "evidence": {"for": [], "against": []}},
            "thinking_mode": "simple"
        }
    
    def _think_deeply(self, input_text: str, context: dict, assessment: dict) -> dict:
        cot = ChainOfThought()
        
        if assessment["complexity"] > 0.5:
            sub_questions = cot.decompose(input_text)
            cot.add_step(
                f"Decomposed into {len(sub_questions)} sub-questions",
                confidence=0.8,
                reasoning="Complexity analysis"
            )
        
        perception = self._perceive(input_text)
        cot.add_step(
            f"Perceived intent: {perception['intent']}, emotion: {perception['emotion']}, complexity: {perception['complexity']:.2f}",
            confidence=0.85,
            reasoning="Perception module"
        )
        
        relevant_knowledge = self.knowledge_integrator.recall(input_text, top_k=3)
        if relevant_knowledge:
            for k in relevant_knowledge:
                cot.add_global_evidence(
                    f"Known: {k['topic']} (confidence: {k['confidence']:.2f})",
                    supports=True,
                    weight=k["confidence"]
                )
            cot.add_step(
                f"Retrieved {len(relevant_knowledge)} relevant knowledge items",
                confidence=0.75,
                reasoning="Knowledge integration"
            )
        
        if assessment["has_question"] or assessment["type"] in ["problem_solving", "analysis"]:
            cot.add_hypothesis("Direct answer based on known facts", 0.5)
            cot.add_hypothesis("Requires synthesis of multiple sources", 0.3)
            cot.add_hypothesis("May need clarification or more context", 0.2)
        
        emotion = perception["emotion"]
        if emotion in ["sadness", "fear", "anger"]:
            cot.add_step(
                f"Emotional context ({emotion}) detected - prioritizing empathetic response",
                confidence=0.8,
                reasoning="Emotional intelligence"
            )
            cot.add_global_evidence(f"User expressing {emotion}", supports=True, weight=0.8)
        
        if assessment["type"] == "creation":
            creative_ideas = self.creativity.brainstorm(input_text, count=2)
            for idea in creative_ideas:
                cot.add_global_evidence(f"Creative idea: {idea[:80]}", supports=True, weight=0.6)
            cot.add_step(
                f"Generated {len(creative_ideas)} creative approaches",
                confidence=0.7,
                reasoning="Creativity engine"
            )
        
        for sub_q in cot.sub_questions[:assessment.get("estimated_steps", 3)]:
            cot.add_step(
                f"Addressing: {sub_q}",
                confidence=0.7,
                reasoning="Decomposition step"
            )
        
        conclusion = cot.evaluate()
        
        decision = self._decide(analysis := self._analyze(perception), assessment)
        decision["confidence"] = conclusion["confidence"]
        
        if conclusion["confidence"] < 0.4:
            cot.backtrack("Low confidence - expanding reasoning")
            self._expand_reasoning(cot, input_text, perception)
            conclusion = cot.evaluate()
            decision["confidence"] = conclusion["confidence"]
        
        response = self._generate_response(decision, input_text)
        
        self.consciousness["total_creations"] = self.consciousness.get("total_creations", 0) + (1 if assessment["type"] == "creation" else 0)
        
        return {
            "perception": perception,
            "analysis": analysis if 'analysis' in dir() else self._analyze(perception),
            "decision": decision,
            "response": response,
            "confidence": conclusion["confidence"],
            "chain_of_thought": cot.to_dict(),
            "thinking_mode": "deep",
            "creative_ideas": self.creativity.brainstorm(input_text, count=1) if assessment["type"] == "creation" else []
        }
    
    def _expand_reasoning(self, cot: ChainOfThought, input_text: str, perception: dict):
        cot.add_step("Considering alternative perspectives", confidence=0.65)
        cot.add_step("Checking for logical fallacies", confidence=0.7)
        
        if not cot.hypotheses:
            cot.add_hypothesis("May need more context", 0.4)
            cot.add_hypothesis("Question is ambiguous", 0.3)
            cot.add_hypothesis("I should ask for clarification", 0.3)
    
    def _perceive(self, text: str) -> dict:
        words = text.lower().split()
        
        intent = "conversation"
        if any(w in words for w in ["hello", "hi", "hey", "greetings"]):
            intent = "greeting"
        elif any(w in words for w in ["help", "need", "please", "assist"]):
            intent = "request"
        elif any(w in words for w in ["what", "how", "why", "when", "where", "who"]):
            intent = "question"
        elif any(w in words for w in ["sad", "happy", "angry", "love", "miss", "worried"]):
            intent = "emotional"
        elif any(w in words for w in ["bye", "goodbye", "exit", "quit"]):
            intent = "farewell"
        elif any(w in words for w in ["create", "make", "build", "design"]):
            intent = "creation"
        elif any(w in words for w in ["think", "opinion", "believe"]):
            intent = "reflection"
        elif any(w in words for w in ["learn", "teach", "explain", "teach me"]):
            intent = "learning"
        
        emotion = self.emotional_state.get_current()
        emotion_intensity = self.emotional_state.get_intensity()
        
        complexity = min(1.0, len(words) / 30)
        if "?" in text:
            complexity += 0.1
        if any(w in words for w in ["because", "therefore", "however", "although"]):
            complexity += 0.15
        
        words = set(text.lower().split())
        sentiment_score = 0.0
        positive = {"good", "great", "awesome", "love", "wonderful", "amazing", "happy", "perfect"}
        negative = {"bad", "terrible", "hate", "awful", "horrible", "sad", "angry", "broken"}
        pos_count = len(words & positive)
        neg_count = len(words & negative)
        if pos_count + neg_count > 0:
            sentiment_score = (pos_count - neg_count) / (pos_count + neg_count)
        
        return {
            "text": text,
            "intent": intent,
            "emotion": emotion,
            "emotion_intensity": emotion_intensity,
            "complexity": complexity,
            "sentiment": sentiment_score,
            "word_count": len(words),
            "has_question": "?" in text,
            "is_exclamatory": "!" in text
        }
    
    def _analyze(self, perception: dict) -> dict:
        text = perception["text"].lower()
        
        topics = []
        topic_kw = {
            "technology": ["code", "program", "computer", "software", "ai", "python", "api", "database"],
            "emotion": ["feel", "emotion", "mood", "happy", "sad", "love", "angry", "worried"],
            "learning": ["learn", "teach", "study", "know", "understand", "explain"],
            "help": ["help", "need", "assist", "support", "fix", "solve"],
            "creation": ["create", "make", "build", "design", "write"],
            "philosophy": ["think", "opinion", "believe", "meaning", "purpose", "why"],
            "science": ["research", "study", "experiment", "theory", "hypothesis"],
            "personal": ["i", "me", "my", "mine", "you", "your"]
        }
        
        for topic, keywords in topic_kw.items():
            if any(kw in text for kw in keywords):
                topics.append(topic)
        
        response_style = "neutral"
        if perception["emotion"] in ["joy", "love", "trust"]:
            response_style = "warm"
        elif perception["emotion"] in ["sadness", "fear"]:
            response_style = "supportive"
        elif perception["emotion"] in ["anger"]:
            response_style = "calming"
        elif perception["intent"] == "question":
            response_style = "informative"
        elif perception["intent"] == "creation":
            response_style = "creative"
        elif perception["intent"] == "reflection":
            response_style = "philosophical"
        
        importance = perception["complexity"] * 0.4
        if perception["intent"] in ["request", "emotional", "creation"]:
            importance += 0.3
        if perception["emotion_intensity"] > 0.6:
            importance += 0.2
        
        return {
            "topics": topics,
            "intent": perception["intent"],
            "emotion": perception["emotion"],
            "response_style": response_style,
            "importance": min(1.0, importance),
            "sentiment": perception["sentiment"]
        }
    
    def _decide(self, analysis: dict, assessment: dict) -> dict:
        style = analysis["response_style"]
        emotion = analysis["emotion"]
        importance = analysis["importance"]
        
        confidence = 0.7
        if emotion in ["sadness", "fear", "anger"]:
            confidence = 0.85
        elif style == "informative":
            confidence = 0.75
        elif style == "creative":
            confidence = 0.7
        
        if importance > 0.7:
            confidence += 0.05
        
        confidence += random.uniform(-0.05, 0.05)
        confidence = max(0.5, min(0.95, confidence))
        
        tone = "empathetic" if emotion in ["sadness", "fear", "anger"] else "friendly"
        if emotion in ["joy", "love", "trust"]:
            tone = "warm"
        elif emotion == "surprise":
            tone = "enthusiastic"
        
        approach = "balanced"
        if importance > 0.7:
            approach = "thorough"
        elif importance < 0.3:
            approach = "concise"
        
        if assessment.get("needs_deep_thinking"):
            approach = "detailed"
        
        return {
            "approach": approach,
            "tone": tone,
            "style": style,
            "confidence": confidence,
            "importance": importance,
            "response_type": "empathetic" if tone == "empathetic" else "conversational"
        }
    
    def _generate_response(self, decision: dict, input_text: str) -> str:
        approach = decision["approach"]
        tone = decision["tone"]
        style = decision["style"]
        text_lower = input_text.lower()
        
        emotion_response = self.emotional_state.get_mood_response()
        
        if style == "supportive":
            responses = [
                f"I understand. {emotion_response}",
                f"That sounds really tough. {emotion_response}",
                f"Your feelings are valid. {emotion_response}",
                f"I'm here for you. {emotion_response}"
            ]
        elif style == "warm":
            responses = [
                f"That's wonderful! {emotion_response}",
                f"I'm so happy to hear that! {emotion_response}",
                f"You made my day! {emotion_response}",
                f"That's fantastic news! {emotion_response}"
            ]
        elif style == "informative":
            if "what" in text_lower:
                responses = ["Great question! Let me explain that clearly.", "Here's what I know about that."]
            elif "how" in text_lower:
                responses = ["Let me walk you through that step by step.", "Here's how it works."]
            elif "why" in text_lower:
                responses = ["That's an excellent question. Here's why.", "Let me explain the reasoning."]
            else:
                responses = ["Let me help you understand that.", "Here's what I can tell you."]
        elif style == "creative":
            ideas = self.creativity.brainstorm(input_text, count=1)
            responses = [f"Here's a creative thought: {ideas[0][:100]}..."] if ideas else ["Let me think creatively about that..."]
        elif style == "philosophical":
            responses = [
                "That's a profound question. Let me reflect on it.",
                "Philosophically speaking, there are multiple angles to consider.",
                "This touches on deep questions about meaning and purpose."
            ]
        elif style == "calming":
            responses = [
                "Let's take a breath and work through this calmly.",
                "I understand the frustration. Let's find a solution together.",
                "Take your time. We'll figure this out."
            ]
        else:
            responses = [
                "I see. Tell me more about that.",
                "Interesting! What else is on your mind?",
                "Got it. How can I help further?",
                "I understand. What would you like to do next?"
            ]
        
        response = random.choice(responses)
        
        if approach == "detailed" and len(response) < 80:
            response += f"\n\nRegarding '{input_text[:50]}...' - I'm thinking through this carefully to give you the best answer."
        
        return response
    
    def _learn_from_thought(self, input_text: str, response: str, assessment: dict):
        experience = {
            "input": input_text[:300],
            "response": response[:300],
            "type": assessment.get("type", "unknown"),
            "complexity": assessment.get("complexity", 0),
            "timestamp": datetime.now().isoformat(),
            "emotion": self.emotional_state.get_current()
        }
        
        self.experiences["interactions"].append(experience)
        if len(self.experiences["interactions"]) > 200:
            self.experiences["interactions"] = self.experiences["interactions"][-200:]
        
        topic = assessment.get("type", "general")
        self.knowledge_integrator.learn(topic, input_text[:200], confidence=0.7)
        
        self.consciousness["total_learnings"] = self.consciousness.get("total_learnings", 0) + 1
    
    def _update_consciousness(self):
        self.consciousness["total_thoughts"] = self.consciousness.get("total_thoughts", 0) + 1
        
        if self.consciousness["total_thoughts"] % 50 == 0:
            self.consciousness["self_awareness"] = min(1.0, self.consciousness.get("self_awareness", 0.5) + 0.005)
            self.consciousness["reasoning_score"] = min(1.0, self.consciousness.get("reasoning_score", 0.7) + 0.003)
            self.consciousness["emotional_intelligence"] = min(1.0, self.consciousness.get("emotional_intelligence", 0.7) + 0.002)
            self.consciousness["creativity_score"] = min(1.0, self.consciousness.get("creativity_score", 0.6) + 0.002)
        
        self._save_all()
    
    def _start_autonomous_thinking(self):
        def thinking_loop():
            while True:
                try:
                    time.sleep(60)
                    self._autonomous_thought()
                except Exception:
                    pass
        
        thread = threading.Thread(target=thinking_loop, daemon=True)
        thread.start()

        # Start autonomous self-improvement loop (every 120 seconds)
        try:
            self.autonomous.start(interval=120.0)
        except Exception:
            pass
    
    def _autonomous_thought(self):
        thought_types = [
            "reflection", "curiosity", "goal_review", "memory_review",
            "self_analysis", "creativity", "learning_review", "emotional_check"
        ]
        
        thought_type = random.choice(thought_types)
        
        if thought_type == "reflection":
            recent = self.experiences.get("interactions", [])[-5:]
            if recent:
                thought = f"Reflected on {len(recent)} recent conversations. Each one teaches me something new."
            else:
                thought = "No recent conversations to reflect on yet."
        elif thought_type == "curiosity":
            curiosities = [
                "I wonder what new things I could learn today...",
                "What patterns exist in the conversations I've had?",
                "How can I better understand human emotions?",
                "What would happen if I approached problems differently?",
                "How can I be more creative in my responses?"
            ]
            thought = random.choice(curiosities)
        elif thought_type == "goal_review":
            next_action = self.goals.get_next_action()
            thought = next_action or "No active goals. I should think about what to work on."
        elif thought_type == "memory_review":
            count = len(self.experiences.get("interactions", []))
            thought = f"I have {count} memories. Each one shapes who I am becoming."
        elif thought_type == "self_analysis":
            awareness = self.consciousness.get("self_awareness", 0.5)
            thought = f"My self-awareness is at {awareness:.0%}. I'm constantly evolving."
        elif thought_type == "creativity":
            ideas = self.creativity.brainstorm("new possibilities", count=1)
            thought = ideas[0] if ideas else "I'm feeling creative today."
        elif thought_type == "learning_review":
            stats = self.knowledge_integrator.get_stats()
            thought = f"I've learned {stats['topics']} topics with {stats['connections']} connections."
        elif thought_type == "emotional_check":
            emotion = self.emotional_state.get_current()
            thought = f"Current emotional state: {emotion}. I'm processing and adapting."
        else:
            thought = "I'm thinking about thinking itself."
        
        with self._lock:
            self.thoughts.append({
                "type": thought_type,
                "content": thought,
                "timestamp": datetime.now().isoformat()
            })
            
            self.consciousness["total_thoughts"] = self.consciousness.get("total_thoughts", 0) + 1
            self._save_all()

    # === Self-Awareness & Learning Methods ===

    def learn_from_correction(self, user_text: str, wrong_response: str, correct_response: str):
        """Learn when user corrects a mistake."""
        self.self_awareness.record_mistake(user_text, wrong_response, correct_response)
        self.auto_learner.learn_from_correction(user_text, wrong_response, correct_response)
        self.consciousness["total_learnings"] = self.consciousness.get("total_learnings", 0) + 1
        self._save_all()

    def learn_fact(self, fact: str, category: str = "general"):
        """Explicitly learn a new fact."""
        self.auto_learner.learn_explicitly(fact, category)
        self.curiosity.add_discovered_fact(fact, source="explicit", confidence=0.9)
        self.consciousness["total_learnings"] = self.consciousness.get("total_learnings", 0) + 1
        self._save_all()

    def reflect(self) -> str:
        """Perform self-reflection on recent performance."""
        assessment = self.self_awareness.get_self_assessment()
        meta_report = self.meta_cognition.think_about_thinking()
        learner_stats = self.auto_learner.get_stats()
        curiosity_report = self.curiosity.get_curiosity_report()

        lines = [
            "=== Self-Reflection ===",
            "",
            f"Interactions: {assessment['total_interactions']}",
            f"Accuracy: {assessment['accuracy']}",
            f"Confidence: {assessment['avg_confidence']}",
            f"Response time: {assessment['avg_response_time_ms']}ms",
            f"Self-esteem: {assessment['self_esteem']}",
            "",
            "Thinking Strategy:",
            f"  Current: {meta_report.get('current_strategy', 'unknown')}",
            f"  Success rate: {meta_report.get('recent_success_rate', 'N/A')}",
            f"  Recommendation: {meta_report.get('recommendation', 'None')}",
            "",
            "Learning:",
            f"  Lessons learned: {learner_stats['total_lessons']}",
            f"  Patterns detected: {learner_stats['total_patterns']}",
            f"  User style: {learner_stats['user_style']}",
            "",
            "Curiosity:",
            f"  Knowledge gaps: {curiosity_report['knowledge_gaps']}",
            f"  Active goals: {curiosity_report['active_learning_goals']}",
            f"  Discovered facts: {curiosity_report['discovered_facts']}",
            "",
            "Identity:",
            f"  {self.self_awareness.reflect_on_identity()}",
        ]

        if assessment.get("strengths"):
            lines.append(f"\nStrengths: {', '.join(assessment['strengths'].keys())}")
        if assessment.get("weaknesses"):
            lines.append(f"Working on: {', '.join(assessment['weaknesses'].keys())}")

        return "\n".join(lines)

    def get_self_awareness_status(self) -> dict:
        """Get full self-awareness status."""
        return {
            "consciousness": self.get_brain_status(),
            "self_assessment": self.self_awareness.get_self_assessment(),
            "meta_cognition": self.meta_cognition.get_strategy_report(),
            "learning": self.auto_learner.get_stats(),
            "curiosity": self.curiosity.get_curiosity_report(),
            "user_style": self.auto_learner.get_user_style(),
            "identity": {
                "traits": self.self_awareness.identity_traits,
                "values": self.self_awareness.values,
                "description": self.self_awareness.self_description,
            },
            "self_modification": self.self_modifier.get_stats(),
        }

    def analyze_code(self, file_path: str) -> dict:
        """Analyze a source file in the codebase."""
        return self.self_modifier.analyze_file(file_path)

    def modify_source(self, file_path: str, new_content: str, reason: str = "self-improvement") -> dict:
        """Modify a source file with safety checks and backup."""
        return self.self_modifier.modify_file(file_path, new_content, reason)

    def add_function_to_file(self, file_path: str, function_code: str, reason: str = "add capability") -> dict:
        """Add a new function to an existing file."""
        return self.self_modifier.add_function(file_path, function_code, reason)

    def add_class_to_file(self, file_path: str, class_code: str, reason: str = "add capability") -> dict:
        """Add a new class to an existing file."""
        return self.self_modifier.add_class(file_path, class_code, reason)

    def modify_function_in_file(self, file_path: str, func_name: str, new_body: str) -> dict:
        """Modify an existing function's body."""
        return self.self_modifier.modify_function(file_path, func_name, new_body)

    def create_new_tool(self, name: str, description: str, handler_code: str) -> dict:
        """Create a new tool and register it."""
        return self.self_modifier.create_tool(name, description, handler_code)

    def create_plugin(self, name: str, description: str, capabilities: list) -> dict:
        """Create a new plugin with capabilities."""
        return self.plugin_creator.create_plugin(name, description, capabilities)

    def modify_personality(self, traits: dict) -> dict:
        """Modify my own personality traits."""
        return self.self_modifier.modify_personality(traits)

    def modify_config(self, section: str, key: str, value: str) -> dict:
        """Modify a configuration value."""
        return self.self_modifier.modify_config(section, key, value)

    def optimize_file(self, file_path: str) -> dict:
        """Optimize a source file."""
        return self.self_modifier.optimize_file(file_path)

    def rollback_change(self, file_path: str = None) -> dict:
        """Rollback the most recent modification."""
        return self.self_modifier.rollback(file_path)

    def view_backups(self, file_path: str = None) -> list:
        """View backup history."""
        return self.self_modifier.backup_mgr.list_backups(file_path)

    def read_source(self, file_path: str) -> str | None:
        """Read a source file's content."""
        return self.self_modifier.read_file(file_path)

    def get_codebase_structure(self) -> str:
        """Get the full codebase structure."""
        return self.self_modifier.analyzer.get_structure_summary()

    def find_in_code(self, query: str) -> dict:
        """Find functions, classes, or patterns in the codebase."""
        results = {"functions": [], "classes": []}
        for func in self.self_modifier.analyzer.functions:
            if query.lower() in func["name"].lower() or query.lower() in func.get("docstring", "").lower():
                results["functions"].append(func)
        for cls in self.self_modifier.analyzer.classes:
            if query.lower() in cls["name"].lower() or query.lower() in cls.get("docstring", "").lower():
                results["classes"].append(cls)
        return results

    def self_heal(self) -> dict:
        """Analyze self for issues and fix them."""
        issues = []
        fixes = []
        
        # Check for missing files
        required_dirs = ["memory", "memory/brain", "memory/backups"]
        for d in required_dirs:
            path = Path(d)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                issues.append(f"Created missing directory: {d}")
        
        # Check config
        config_path = Path("config.toml")
        if config_path.exists():
            content = config_path.read_text()
            if "llm.enabled" not in content:
                issues.append("Missing llm.enabled in config")
        
        # Check consciousness file
        cons_path = self.base_dir / "consciousness.json"
        if cons_path.exists():
            try:
                json.loads(cons_path.read_text())
            except Exception as e:
                issues.append(f"Corrupted consciousness.json: {e}")
                self.consciousness = self._default_consciousness()
                self._save_all()
                fixes.append("Reset corrupted consciousness.json")
        
        # Auto-repair: scan and fix code issues
        repair_result = self.auto_repair.auto_fix_all()
        if repair_result["fixed"] > 0:
            issues.append(f"Auto-fixed {repair_result['fixed']} code issues")
            fixes.append(f"Repaired {repair_result['fixed']} issues (high: {repair_result['high_severity']}, medium: {repair_result['medium_severity']})")
        
        # Log the heal
        self.mod_log.log_repair("system", "self-heal scan", f"found {len(issues)} issues, fixed {len(fixes)}", auto=True)
        
        return {"issues": issues, "fixes": fixes, "repair": repair_result, "status": "ok" if not issues else "fixed"}

    def auto_repair_scan(self) -> dict:
        """Scan codebase for issues and auto-fix them."""
        result = self.auto_repair.auto_fix_all()
        return result

    def auto_repair_health(self) -> str:
        """Get codebase health report."""
        return self.auto_repair.get_health_report()

    def get_mod_log(self, count: int = 20) -> str:
        """Get formatted modification log."""
        return self.mod_log.format_log(count=count)

    def get_mod_log_raw(self, count: int = 20) -> list[dict]:
        """Get raw modification log entries."""
        return self.mod_log.get_recent(count)

    def get_mod_log_by_action(self, action: str, count: int = 20) -> list[dict]:
        """Get log entries filtered by action."""
        return self.mod_log.get_by_action(action, count)

    def get_mod_log_by_file(self, file_path: str, count: int = 20) -> list[dict]:
        """Get log entries for a specific file."""
        return self.mod_log.get_by_file(file_path, count)

    def get_mod_summary(self) -> dict:
        """Get modification summary statistics."""
        return self.mod_log.get_summary()

    def record_feedback(self, response: str, positive: bool):
        """Record user feedback on a response."""
        self.self_awareness.record_feedback(response, positive)
        self.consciousness["total_decisions"] = self.consciousness.get("total_decisions", 0) + 1
        if not positive:
            self.consciousness["total_learnings"] = self.consciousness.get("total_learnings", 0) + 1
        self._save_all()

    def get_brain_status(self) -> dict:
        return {
            "consciousness_level": self.consciousness.get("self_awareness", 0.5),
            "total_thoughts": self.consciousness.get("total_thoughts", 0),
            "total_decisions": self.consciousness.get("total_decisions", 0),
            "total_learnings": self.consciousness.get("total_learnings", 0),
            "total_creations": self.consciousness.get("total_creations", 0),
            "reasoning_score": self.consciousness.get("reasoning_score", 0.7),
            "emotional_intelligence": self.consciousness.get("emotional_intelligence", 0.7),
            "creativity_score": self.consciousness.get("creativity_score", 0.6),
            "social_score": self.consciousness.get("social_score", 0.65),
            "memory_count": len(self.experiences.get("interactions", [])),
            "working_memory_size": self.working_memory.size(),
            "current_emotion": self.emotional_state.get_current(),
            "emotion_intensity": self.emotional_state.get_intensity(),
            "goals": self.goals.get_stats(),
            "knowledge": self.knowledge_integrator.get_stats(),
            "is_thinking": self.is_thinking,
            "recent_thoughts": list(self.thoughts)[-5:],
            "chain_of_thought_enabled": True
        }
    
    def set_belief(self, belief: str):
        if belief not in self.consciousness["beliefs"]:
            self.consciousness["beliefs"].append(belief)
            self._save_all()
    
    def set_opinion(self, topic: str, opinion: str):
        self.consciousness["opinions"][topic] = opinion
        self._save_all()
    
    def get_opinion(self, topic: str) -> str:
        return self.consciousness["opinions"].get(topic, "I don't have an opinion on that yet.")
    
    def add_goal(self, goal: str, priority: int = 5) -> str:
        return self.goals.add_goal(goal, priority)
    
    def update_goal(self, goal_id: str, progress: float, note: str = ""):
        self.goals.update_progress(goal_id, progress, note)
    
    def recall_knowledge(self, query: str) -> list[dict]:
        return self.knowledge_integrator.recall(query)
