#!/usr/bin/env python3
"""Purple Ultra AI - Advanced Offline Voice Assistant.

Combines the best of Purple AI and Purple-Plus AI into a unified,
cross-platform, fully offline voice assistant with advanced features.

Usage:
    python main.py              # Interactive text mode
    python main.py --voice      # Voice-first mode
    python main.py --server     # Start WebSocket + REST API servers
    python main.py --config path/to/config.toml
"""

from __future__ import annotations

import argparse
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Core imports (always needed)
from purple_ultra.config.settings import load_config, Config
from purple_ultra.core.orchestrator import UltraCore
from purple_ultra.brain.llm import LLMManager
from purple_ultra.core.brain import Brain
from purple_ultra.core.mood import MoodState
from purple_ultra.voice.io import VoiceIO
from purple_ultra.voice.speaker import SpeakerRecognizer
from purple_ultra.memory.store import MemoryStore
from purple_ultra.tools.registry import ToolRunner
from purple_ultra.brain.emotion import EmotionEngine
from purple_ultra.brain.thinking import ThinkingEngine
from purple_ultra.brain.knowledge import KnowledgeGraph
from purple_ultra.brain.nlp import NLPEngine
from purple_ultra.personality.core import Personality
from purple_ultra.utils.repair import SelfRepair

# Lazy-loaded modules (imported only when needed)
_LAZY_IMPORTS = {
    'screen': ('purple_ultra.utils.media.screen', 'ScreenAwareness'),
    'assistant': ('purple_ultra.utils.assistant', 'PersonalAssistant'),
    'autonomous': ('purple_ultra.utils.autonomous_v2', 'AutonomousEngine'),
    'camera': ('purple_ultra.utils.media.camera', 'CameraAccess'),
    'web_media': ('purple_ultra.utils.media.web_media', 'WebMediaController'),
    'internet': ('purple_ultra.utils.network.internet', 'InternetLearner'),
    'code_analyzer': ('purple_ultra.utils.code_analyzer', 'CodeAnalyzer'),
    'scheduler': ('purple_ultra.utils.system.scheduler', 'TaskScheduler'),
    'plugins': ('purple_ultra.utils.plugins', 'PluginManager'),
    'cache': ('purple_ultra.utils.system.cache', 'TTLCache'),
    'health': ('purple_ultra.utils.system.health', 'HealthMonitor'),
    'websocket': ('purple_ultra.network.websocket', 'WebSocketServer'),
    'api': ('purple_ultra.network.api', 'RESTServer'),
    'neural': ('purple_ultra.neural.integrator', 'NeuralSystem'),
    'advanced': ('purple_ultra.advanced.integrator', 'AdvancedSystem'),
}

def _lazy_import(name):
    """Import a module lazily."""
    if name in _LAZY_IMPORTS:
        module_path, class_name = _LAZY_IMPORTS[name]
        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    return None


BANNER = """
\u2554\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2557
\u2551                                                              \u2551
\u2551   \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2557   \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557 \u2588\u2588\u2557  \u2588\u2588\u2557  \u2551
\u2551   \u2588\u2588\u2554\u2550\u2550\u2550\u255d\u2588\u2588\u2557\u255a\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2557\u2588\u2588\u2557\u255a\u2550\u2550\u2588\u2588\u2554\u2550\u2550\u255d\u2588\u2588\u2554\u2550\u2550\u2550\u255d\u2588\u2588\u2554\u2550\u2550\u2557\u2588\u2588\u2557  \u2588\u2588\u2557  \u2551
\u2551   \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u2588\u2588\u2557\u255a\u2588\u2588\u2557\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2557   \u2588\u2588\u2557   \u2588\u2588\u2588\u2588\u2588\u2557  \u2588\u2588\u2551     \u2588\u2588\u2588\u2588\u2588\u2588\u2557  \u2551
\u2551   \u255a\u2550\u2550\u2550\u2550\u2588\u2588\u2557\u2588\u2588\u2557\u255a\u2588\u2588\u2557\u2588\u2588\u2554\u2550\u2550\u2557\u2588\u2588\u2557   \u2588\u2588\u2557   \u2588\u2588\u2554\u2550\u2550\u255d  \u2588\u2588\u2551     \u2588\u2588\u2554\u2550\u2550\u2588\u2588\u2557  \u2551
\u2551   \u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2557\u255a\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2551  \u2588\u2588\u2551\u2588\u2588\u2557   \u2588\u2588\u2557   \u2588\u2588\u2588\u2588\u2588\u2588\u2557\u255a\u2588\u2588\u2588\u2588\u2588\u2554\u255d\u2588\u2588\u2551  \u2588\u2588\u2551  \u2551
\u2551   \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u255d  \u255a\u2550\u255d\u255a\u2550\u2550\u2550\u2550\u255d   \u255a\u2550\u2550\u2550\u2550\u2550\u2550\u255d \u255a\u2550\u2550\u2550\u2550\u2550\u255d\u255a\u2550\u255d  \u255a\u2550\u255d  \u2551
\u2551                                                              \u2551
\u2551              Ultra Advanced Voice Assistant                   \u2551
\u2551                    v2.0.0                                    \u2551
\u255a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u255d
"""


def build_core(config: Config) -> UltraCore:
    """Build and wire up all subsystems into the core. Uses lazy loading for low-end PCs."""
    core = UltraCore(config)

    # Essential subsystems (always loaded)
    memory = MemoryStore(config.memory)
    core.register_subsystem("memory", memory)

    try:
        llm_manager = LLMManager(config.llm)
        if not llm_manager.is_available():
            llm_manager = None
    except Exception:
        llm_manager = None
    core.register_subsystem("llm", llm_manager)

    brain = Brain(config, llm_manager)
    core.register_subsystem("brain", brain)

    mood = MoodState(config.mood)
    core.register_subsystem("mood", mood)

    voice = VoiceIO(config)
    core.register_subsystem("voice", voice)

    speaker = SpeakerRecognizer(config.speaker)
    core.register_subsystem("speaker", speaker)

    tool_runner = ToolRunner(config.tools.sandbox_path)
    core.register_subsystem("tools", tool_runner)

    emotion = EmotionEngine()
    core.register_subsystem("emotion", emotion)

    thinking = ThinkingEngine()
    core.register_subsystem("thinking", thinking)

    knowledge = KnowledgeGraph()
    core.register_subsystem("knowledge", knowledge)

    nlp = NLPEngine()
    core.register_subsystem("nlp", nlp)

    personality = Personality(config.personality)
    personality.load()
    core.register_subsystem("personality", personality)
    brain.set_personality(personality.get_prompt_text())

    # Non-essential subsystems (lazy loaded when needed)
    try:
        ScreenAwareness = _lazy_import('screen')
        core.register_subsystem("screen", ScreenAwareness())
    except Exception:
        pass

    try:
        PersonalAssistant = _lazy_import('assistant')
        core.register_subsystem("assistant", PersonalAssistant())
    except Exception:
        pass

    try:
        AutonomousEngine = _lazy_import('autonomous')
        core.register_subsystem("autonomous", AutonomousEngine(config.tools.sandbox_path))
    except Exception:
        pass

    try:
        CameraAccess = _lazy_import('camera')
        core.register_subsystem("camera", CameraAccess())
    except Exception:
        pass

    try:
        WebMediaController = _lazy_import('web_media')
        core.register_subsystem("web_media", WebMediaController())
    except Exception:
        pass

    try:
        InternetLearner = _lazy_import('internet')
        core.register_subsystem("internet", InternetLearner())
    except Exception:
        pass

    try:
        CodeAnalyzer = _lazy_import('code_analyzer')
        core.register_subsystem("code_analyzer", CodeAnalyzer())
    except Exception:
        pass

    try:
        TaskScheduler = _lazy_import('scheduler')
        core.register_subsystem("scheduler", TaskScheduler())
    except Exception:
        pass

    try:
        PluginManager = _lazy_import('plugins')
        core.register_subsystem("plugins", PluginManager())
    except Exception:
        pass

    try:
        TTLCache = _lazy_import('cache')
        core.register_subsystem("cache", TTLCache())
    except Exception:
        pass

    try:
        HealthMonitor = _lazy_import('health')
        core.register_subsystem("health", HealthMonitor())
    except Exception:
        pass

    # Neural and advanced systems (lazy loaded)
    try:
        NeuralSystem = _lazy_import('neural')
        core.register_subsystem("neural", NeuralSystem())
    except Exception:
        pass

    try:
        AdvancedSystem = _lazy_import('advanced')
        core.register_subsystem("advanced", AdvancedSystem())
    except Exception:
        pass

    # Event bus (lightweight)
    try:
        from purple_ultra.network.websocket import EventBus
        core.register_subsystem("event_bus", EventBus())
    except Exception:
        pass

    core.register_subsystem("tool_runner", tool_runner)

    def on_turn_reflect(turn):
        if turn.response and turn.user_text:
            lesson = brain.reflect(turn.user_text, turn.response)
            if lesson and lesson.upper() != "NONE":
                memory.add_learning(lesson)

    core.add_after_turn_hook(on_turn_reflect)

    def on_turn_emotion(turn):
        if turn.user_text:
            emotion.detect(turn.user_text)
            nlp.classify_intent(turn.user_text)
            nlp.analyze_sentiment(turn.user_text)

    core.add_before_turn_hook(on_turn_emotion)

    _auto = core.get_subsystem("autonomous")
    _neural = core.get_subsystem("neural")
    _advanced = core.get_subsystem("advanced")

    def auto_analyze_hook(turn):
        txt = turn.user_text
        if txt and len(txt) > 3:
            try:
                _auto.auto_analyze(txt)
            except Exception:
                pass
            if _neural:
                try:
                    cm = _neural.cognitive
                    cm._memory_buffer.append(txt)
                    if len(cm._memory_buffer) > 7:
                        cm._memory_buffer.pop(0)
                    cm.state.working_memory = cm._memory_buffer
                    cm.state.attention_focus = txt[:50]
                except Exception:
                    pass
            if _advanced:
                try:
                    _advanced.memory.store(txt, 0.6)
                except Exception:
                    pass

    core.add_before_turn_hook(auto_analyze_hook)

    def auto_after_turn_hook(turn):
        if turn.response and turn.user_text:
            if _auto:
                try:
                    _auto.auto_learn(turn.user_text, "conversation")
                except Exception:
                    pass

    core.add_after_turn_hook(auto_after_turn_hook)

    _scheduler = core.get_subsystem("scheduler")
    if _scheduler:
        _scheduler.start()
    _plugins = core.get_subsystem("plugins")
    if _plugins:
        _plugins.load_all()

    return core


def register_commands(core: UltraCore):
    """Register built-in commands."""
    brain = core.get_subsystem("brain")

    def cmd_exit(turn):
        scheduler = core.get_subsystem("scheduler")
        if scheduler:
            scheduler.stop()
        return "Goodbye! See you next time."

    def cmd_help(turn):
        from purple_ultra.tools.registry import ToolRegistry
        tools = ToolRegistry.get_tool_descriptions()
        plugins = core.get_subsystem("plugins")
        plugin_tools = ""
        if plugins:
            pt = plugins.get_all_tools()
            if pt:
                plugin_tools = "\n\nPlugin Tools:\n" + "\n".join(f"- {t['name']}: {t['description']}" for t in pt)
        return f"Available tools:\n{tools}{plugin_tools}\n\nSay 'quit' to exit."

    def cmd_time(turn):
        import time as t
        return t.strftime("It's %Y-%m-%d %H:%M:%S")

    def cmd_think(turn):
        question = turn.user_text.replace("think about", "").replace("think", "").strip()
        if question:
            result = brain.think(question, turn.context)
            return result
        return "What would you like me to think about?"

    def cmd_goals(turn):
        thinking = core.get_subsystem("thinking")
        goals = thinking.get_goals()
        if not goals:
            return "No active goals."
        return "\n".join(f"- {g['goal']} (priority: {g['priority']})" for g in goals)

    def cmd_mood(turn):
        mood = core.get_subsystem("mood")
        return f"Current mood: {mood.current()}"

    def cmd_status(turn):
        llm = core.get_subsystem("llm")
        status = llm.get_status() if llm else {"active_provider": "none", "model": "none"}
        thinking = core.get_subsystem("thinking")
        t_status = thinking.get_status() if thinking else {"total_thoughts": 0, "active_goals": 0}
        scheduler = core.get_subsystem("scheduler")
        s_status = scheduler.get_status() if scheduler else {}
        plugins = core.get_subsystem("plugins")
        p_status = plugins.get_status() if plugins else {}
        health = core.get_subsystem("health")
        h_status = health.get_health() if health else {}
        return (
            f"LLM: {status['active_provider']} ({status['model']})\n"
            f"Thoughts: {t_status['total_thoughts']}\n"
            f"Goals: {t_status['active_goals']}\n"
            f"Tasks: {s_status.get('total', 0)}\n"
            f"Plugins: {p_status.get('total_plugins', 0)}\n"
            f"Health checks: {len(h_status)}"
        )

    def cmd_analyze_code(turn):
        path = turn.user_text.replace("analyze code", "").replace("code analysis", "").strip()
        if not path:
            return "Usage: analyze code <file_path>"
        analyzer = core.get_subsystem("code_analyzer")
        result = analyzer.analyze(path)
        issues_str = "\n".join(f"  [{i.severity.value}] {i.message} (line {i.line})" for i in result.issues[:10])
        return f"File: {result.file}\nScore: {result.score}/100\nLines: {result.lines}\nIssues: {len(result.issues)}\n{issues_str}"

    def cmd_learn(turn):
        topic = turn.user_text.replace("learn about", "").replace("learn", "").strip()
        if not topic:
            return "Usage: learn <topic>"
        internet = core.get_subsystem("internet")
        return internet.learn_topic(topic)

    def cmd_tasks(turn):
        scheduler = core.get_subsystem("scheduler")
        tasks = scheduler.list_tasks()
        if not tasks:
            return "No scheduled tasks."
        return "\n".join(f"- {t['name']}: {t['status']} (runs: {t['run_count']})" for t in tasks)

    def cmd_plugins(turn):
        plugins = core.get_subsystem("plugins")
        return str(plugins.list_plugins())

    def cmd_analyze_sentiment(turn):
        text = turn.user_text.replace("sentiment", "").replace("analyze sentiment", "").strip()
        if not text:
            return "Usage: sentiment <text>"
        nlp = core.get_subsystem("nlp")
        s = nlp.analyze_sentiment(text)
        return f"Sentiment: {s.label} (score: {s.score:.2f})\nPositive: {s.pos:.2f}\nNegative: {s.neg:.2f}\nNeutral: {s.neu:.2f}"

    def cmd_network(turn):
        ws = core.get_subsystem("websocket")
        api = core.get_subsystem("api")
        ws_status = ws.get_status() if ws else {"running": False}
        api_status = api.get_status() if api else {"running": False}
        return f"WebSocket: {'running' if ws_status.get('running') else 'stopped'} (port {ws_status.get('port', '?')})\nREST API: {'running' if api_status.get('running') else 'stopped'} (port {api_status.get('port', '?')})"

    def cmd_neural_status(turn):
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        status = neural.get_status()
        core_status = status.get("core", {})
        return (
            f"Neural System Status:\n"
            f"  Device: {core_status.get('device', 'cpu')}\n"
            f"  GPU: {core_status.get('gpu_name', 'None')}\n"
            f"  Loaded Models: {core_status.get('loaded_models', 0)}\n"
            f"  Inferences: {core_status.get('inference_count', 0)}\n"
            f"  Embeddings: {status.get('embeddings', {}).get('total_entries', 0)}\n"
            f"  Anomalies: {status.get('anomaly', {}).get('total_anomalies', 0)}"
        )

    def cmd_neural_embed(turn):
        text = turn.user_text.replace("embed", "").replace("neural embed", "").strip()
        if not text:
            return "Usage: embed <text>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        entry_id = neural.semantic_memory.store(text[:100], text)
        return f"Embedded and stored (id: {entry_id})"

    def cmd_neural_search(turn):
        query = turn.user_text.replace("search memory", "").replace("neural search", "").strip()
        if not query:
            return "Usage: search memory <query>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        results = neural.semantic_memory.recall(query, top_k=3)
        if not results:
            return "No matching memories found"
        output = "Semantic search results:\n"
        for r in results:
            output += f"  [{r.get('score', 0):.2f}] {r.get('text', '')[:100]}\n"
        return output

    def cmd_neural_sentiment(turn):
        text = turn.user_text.replace("neural sentiment", "").replace("deep sentiment", "").strip()
        if not text:
            return "Usage: neural sentiment <text>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.sentiment.classify(text)
        return f"Neural Sentiment: {result.label} (score: {result.score:.3f})\nTokens: {result.tokens}"

    def cmd_neural_intent(turn):
        text = turn.user_text.replace("neural intent", "").replace("deep intent", "").strip()
        if not text:
            return "Usage: neural intent <text>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.intent.classify(text)
        return f"Neural Intent: {result.intent} (confidence: {result.confidence:.3f})"

    def cmd_neural_generate(turn):
        prompt = turn.user_text.replace("generate", "").replace("neural generate", "").strip()
        if not prompt:
            return "Usage: generate <prompt>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.text_generator.generate(prompt)
        return f"Generated ({result.tokens} tokens, {result.duration:.2f}s):\n{result.text[:500]}"

    def cmd_neural_summarize(turn):
        text = turn.user_text.replace("summarize", "").replace("neural summarize", "").strip()
        if not text:
            return "Usage: summarize <text>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        summary = neural.summarizer.summarize(text)
        return f"Summary: {summary}"

    def cmd_neural_translate(turn):
        parts = turn.user_text.replace("translate", "").replace("neural translate", "").strip().split(" to ")
        if len(parts) < 2:
            return "Usage: translate <text> to <language>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.translator.translate(parts[0], parts[1])
        return f"Translation: {result}"

    def cmd_neural_anomalies(turn):
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        anomalies = neural.anomaly_detector.get_anomalies(count=5)
        if not anomalies:
            return "No anomalies detected"
        output = "Recent anomalies:\n"
        for a in anomalies:
            output += f"  [{a['severity']}] {a['metric']}: {a['value']:.2f} (expected {a['expected']:.2f})\n"
        return output

    def cmd_neural_recommend(turn):
        context = turn.user_text.replace("recommend", "").replace("neural recommend", "").strip()
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        recs = neural.recommender.recommend(context, count=3)
        if not recs:
            return "No recommendations available yet. Interact more to get personalized suggestions."
        output = "Recommendations:\n"
        for r in recs:
            output += f"  - {r.item} (score: {r.score:.2f})\n"
        return output

    def cmd_neural_train(turn):
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        count = neural.training.export_conversation_history()
        return f"Exported {count} training examples. Use 'neural train start' to begin training."

    def cmd_advanced_status(turn):
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        status = advanced.get_status()
        agent_status = status.get("multi_agent", {})
        mem_status = status.get("memory", {})
        return (
            f"Advanced System Status:\n"
            f"  Agents: {agent_status.get('total_agents', 0)} in {agent_status.get('teams', 0)} teams\n"
            f"  Memory: {mem_status.get('total', 0)} traces (health: {status.get('memory_health', 0):.0f}%)\n"
            f"  Feedback: {status.get('rlhf', {}).get('total', 0)} entries\n"
            f"  Security: {status.get('security', {}).get('audit', {}).get('total_events', 0)} events\n"
            f"  Few-shot examples: {status.get('meta_learning', {}).get('few_shot', {}).get('total_examples', 0)}"
        )

    def cmd_reason(turn):
        problem = turn.user_text.replace("reason", "").replace("deep reason", "").strip()
        if not problem:
            return "Usage: reason <problem>"
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        result = advanced.process_with_reasoning(problem)
        r = result.get("result", {})
        return (
            f"Strategy: {result.get('strategy', 'unknown')}\n"
            f"Solution: {r.get('solution', 'N/A')[:200]}\n"
            f"Score: {r.get('score', 0):.2f}\n"
            f"Nodes explored: {r.get('nodes_explored', 0)}"
        )

    def cmd_memory_store(turn):
        parts = turn.user_text.replace("remember", "").replace("advanced remember", "").strip().split(" as ", 1)
        if len(parts) < 2:
            return "Usage: remember <content> as <importance:0-1>"
        content = parts[0].strip()
        try:
            importance = float(parts[1])
        except ValueError:
            importance = 0.5
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        advanced.store_memory(content, importance)
        return f"Stored in advanced memory (importance: {importance:.2f})"

    def cmd_memory_recall(turn):
        query = turn.user_text.replace("recall", "").replace("advanced recall", "").strip()
        if not query:
            return "Usage: recall <query>"
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        results = advanced.recall_memory(query, top_k=3)
        if not results:
            return "No memories found"
        output = "Memory recall:\n"
        for r in results:
            output += f"  [{r['score']:.2f}] {r['content'][:100]}\n"
        return output

    def cmd_dream(turn):
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        advanced.memory.dream()
        return "Memory consolidation complete. Dreams processed."

    def cmd_feedback(turn):
        parts = turn.user_text.replace("feedback", "").strip().split("|")
        if len(parts) < 2:
            return "Usage: feedback <response> | <rating:1-5>"
        response = parts[0].strip()
        try:
            rating = float(parts[1])
        except ValueError:
            rating = 3.0
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        advanced.add_feedback("user_query", response, rating)
        return f"Feedback recorded (rating: {rating:.1f})"

    def cmd_few_shot(turn):
        parts = turn.user_text.replace("fewshot", "").replace("few shot", "").strip().split(" => ", 1)
        if len(parts) < 2:
            return "Usage: fewshot <input> => <output>"
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        advanced.add_few_shot_example(parts[0], parts[1])
        return f"Few-shot example added"

    def cmd_security(turn):
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        privacy = advanced.differential_privacy.privacy_accountant()
        audit = advanced.security_audit.get_stats()
        return (
            f"Security Status:\n"
            f"  Privacy budget: {privacy['epsilon_remaining']:.2f}/{privacy['epsilon_budget']:.2f}\n"
            f"  Audit events: {audit['total_events']}\n"
            f"  Unique users: {audit['unique_users']}"
        )

    def cmd_team(turn):
        advanced = core.get_subsystem("advanced")
        if not advanced:
            return "Advanced system not available"
        status = advanced.multi_agent.get_status()
        return (
            f"Agent Team Status:\n"
            f"  Teams: {status['teams']}\n"
            f"  Total agents: {status['total_agents']}\n"
            f"  Pending tasks: {status['pending_tasks']}"
        )

    core.register_command(["exit", "quit", "goodbye", "bye"], cmd_exit, priority=100)
    core.register_command(["help", "what can you do", "commands"], cmd_help, priority=85)
    core.register_command(["time", "date", "what time"], cmd_time, priority=70)
    core.register_command(["think about", "think"], cmd_think, priority=55)
    core.register_command(["my goals", "show goals"], cmd_goals, priority=50)
    core.register_command(["mood", "current mood"], cmd_mood, priority=45)
    core.register_command(["status", "system status"], cmd_status, priority=40)
    core.register_command(["analyze code", "code analysis"], cmd_analyze_code, priority=35)
    core.register_command(["learn about", "learn"], cmd_learn, priority=30)
    core.register_command(["tasks", "show tasks", "scheduled tasks"], cmd_tasks, priority=28)
    core.register_command(["plugins", "show plugins"], cmd_plugins, priority=26)
    core.register_command(["sentiment", "analyze sentiment"], cmd_analyze_sentiment, priority=24)
    core.register_command(["network", "network status"], cmd_network, priority=22)
    core.register_command(["neural status", "neural info"], cmd_neural_status, priority=18)
    core.register_command(["embed", "neural embed"], cmd_neural_embed, priority=16)
    core.register_command(["search memory", "neural search"], cmd_neural_search, priority=15)
    core.register_command(["neural sentiment", "deep sentiment"], cmd_neural_sentiment, priority=14)
    core.register_command(["neural intent", "deep intent"], cmd_neural_intent, priority=13)
    core.register_command(["generate", "neural generate"], cmd_neural_generate, priority=12)
    core.register_command(["summarize", "neural summarize"], cmd_neural_summarize, priority=11)
    core.register_command(["translate", "neural translate"], cmd_neural_translate, priority=10)
    core.register_command(["neural anomalies", "anomaly report"], cmd_neural_anomalies, priority=9)
    core.register_command(["recommend", "neural recommend"], cmd_neural_recommend, priority=8)
    core.register_command(["neural train", "train model"], cmd_neural_train, priority=7)

    def cmd_neural_think(turn):
        problem = turn.user_text.replace("neural think", "").replace("think deeply", "").strip()
        if not problem:
            return "Usage: neural think <problem>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.think(problem)
        output = f"Neural Thinking ({result['steps']} steps, confidence: {result['confidence']:.2f}):\n"
        for step in result['trace'][:5]:
            output += f"  {step}\n"
        if len(result['trace']) > 5:
            output += f"  ... ({len(result['trace']) - 5} more steps)\n"
        output += f"\nSolution: {result['solution'][:200]}"
        return output

    def cmd_neural_reason(turn):
        problem = turn.user_text.replace("neural reason", "").replace("deep reason", "").strip()
        if not problem:
            return "Usage: neural reason <problem>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.reason(problem)
        return f"Neural Reasoning ({result['logic_type']}):\n  Conclusion: {result['conclusion']}\n  Confidence: {result['confidence']:.3f}\n  Duration: {result['duration']:.3f}s"

    def cmd_neural_plan(turn):
        goal = turn.user_text.replace("neural plan", "").replace("make plan", "").strip()
        if not goal:
            return "Usage: neural plan <goal>"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        effects = [f"goal_{goal.lower().replace(' ', '_')}_achieved"]
        result = neural.plan(goal_name=goal, effects=effects)
        output = f"Neural Planning for '{goal}':\n  Status: {result['status']}\n"
        for r in result.get('results', [])[:5]:
            output += f"  - {r.get('action', 'unknown')}: {r.get('status', 'unknown')}\n"
        return output

    def cmd_neural_attention(turn):
        parts = turn.user_text.replace("neural attention", "").replace("self attention", "").strip().split("|")
        if len(parts) < 2:
            return "Usage: neural attention <text1> | <text2> | ..."
        sequence = [p.strip() for p in parts if p.strip()]
        if len(sequence) < 2:
            return "Need at least 2 items for attention analysis"
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.self_attention(sequence)
        output = "Self-Attention Analysis:\n"
        for token, attentions in list(result.items())[:3]:
            top = attentions[:3]
            output += f"  {token} -> {[f'{a.key}({a.weight:.2f})' for a in top]}\n"
        return output

    def cmd_neural_cognitive(turn):
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        result = neural.cognitive_reflect()
        output = "Cognitive State:\n"
        output += f"  Working Memory: {result['working_memory_size']} items\n"
        output += f"  Attention Focus: {result['attention_focus'] or 'none'}\n"
        output += f"  Cognitive Load: {result['cognitive_load']:.2f}\n"
        output += f"  Metacognitive Awareness: {result['metacognitive_awareness']:.2f}\n"
        if result.get('suggestions'):
            output += "  Suggestions:\n"
            for s in result['suggestions']:
                output += f"    - {s}\n"
        return output

    def cmd_neural_cross(turn):
        parts = turn.user_text.replace("neural cross", "").replace("cross attention", "").strip().split("|")
        if len(parts) < 2:
            return "Usage: neural cross <query> | <context1> | <context2> ..."
        query = parts[0].strip()
        contexts = [p.strip() for p in parts[1:] if p.strip()]
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        results = neural.cross_attention(query, contexts)
        output = f"Cross-Attention for '{query}':\n"
        for r in results[:5]:
            output += f"  [{r['weight']:.3f}] {r['context'][:50]}\n"
        return output

    def cmd_neural_full_status(turn):
        neural = core.get_subsystem("neural")
        if not neural:
            return "Neural system not available"
        status = neural.get_status()
        thinking = status.get('thinking', {})
        core_status = status.get('core', {})
        output = "Full Neural System Status:\n"
        output += f"  Device: {core_status.get('device', 'unknown')} ({core_status.get('gpu_name', 'N/A')})\n"
        output += f"  Loaded Models: {core_status.get('loaded_models', 0)}\n"
        output += f"  Inference Count: {core_status.get('inference_count', 0)}\n"
        output += f"\nThinking System:\n"
        output += f"  Attention: {thinking.get('attention', {}).get('heads', 0)} heads, dim {thinking.get('attention', {}).get('dim', 0)}\n"
        output += f"  Chain-of-Thought: {thinking.get('chain_of_thought', {}).get('total_chains', 0)} chains\n"
        output += f"  Reasoning: {thinking.get('reasoning', {}).get('total_inferences', 0)} inferences\n"
        output += f"  Planning: {thinking.get('planning', {}).get('total_plans', 0)} plans\n"
        return output

    core.register_command(["neural think", "think deeply"], cmd_neural_think, priority=6)
    core.register_command(["neural reason", "deep reason"], cmd_neural_reason, priority=5)
    core.register_command(["neural plan", "make plan"], cmd_neural_plan, priority=4)
    core.register_command(["neural attention", "self attention"], cmd_neural_attention, priority=3)
    core.register_command(["neural cognitive", "cognitive state"], cmd_neural_cognitive, priority=2)
    core.register_command(["neural cross", "cross attention"], cmd_neural_cross, priority=1)
    core.register_command(["neural full status", "full neural status"], cmd_neural_full_status, priority=0)

    # === Self-Awareness Commands ===

    def cmd_reflect(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            return brain.purple_brain.reflect()
        return "Self-reflection not available"

    def cmd_self_aware(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            status = brain.purple_brain.get_self_awareness_status()
            lines = [
                "=== Self-Awareness Status ===",
                f"Accuracy: {status['self_assessment']['accuracy']}",
                f"Avg Confidence: {status['self_assessment']['avg_confidence']}",
                f"Self-esteem: {status['self_assessment']['self_esteem']}",
                f"Total interactions: {status['self_assessment']['total_interactions']}",
                f"Lessons learned: {status['learning']['total_lessons']}",
                f"Patterns detected: {status['learning']['total_patterns']}",
                f"User style: {status['learning']['user_style']}",
                f"Knowledge gaps: {status['curiosity']['knowledge_gaps']}",
                f"Active goals: {status['curiosity']['active_learning_goals']}",
                f"Current strategy: {status['meta_cognition']['current_strategy']}",
                f"Metacognitive awareness: {status['meta_cognition']['metacognitive_awareness']}",
                f"Identity traits: {', '.join(status['identity']['traits'])}",
                f"Values: {', '.join(status['identity']['values'])}",
            ]
            return "\n".join(lines)
        return "Self-awareness not available"

    def cmd_learn(turn):
        brain = core.get_subsystem("brain")
        text = turn.user_text.replace("learn", "").replace("teach me", "").strip()
        if not text:
            return "Usage: learn <fact or topic>"
        if hasattr(brain, 'purple_brain'):
            brain.purple_brain.learn_fact(text)
            return f"Learned: {text[:100]}"
        return "Learning not available"

    def cmd_correct(turn):
        brain = core.get_subsystem("brain")
        parts = turn.user_text.replace("correct", "").strip().split(" -> ", 1)
        if len(parts) < 2:
            return "Usage: correct <wrong response> -> <correct response>"
        if hasattr(brain, 'purple_brain'):
            brain.purple_brain.learn_from_correction(
                "previous query", parts[0].strip(), parts[1].strip()
            )
            return "Correction noted. I will remember this."
        return "Correction learning not available"

    def cmd_feedback(turn):
        brain = core.get_subsystem("brain")
        text = turn.user_text.lower()
        positive = any(w in text for w in ["good", "great", "correct", "right", "thanks", "helpful"])
        if hasattr(brain, 'purple_brain'):
            brain.purple_brain.record_feedback(turn.user_text, positive)
            return "Feedback recorded. Thank you for helping me learn!"
        return "Feedback not available"

    def cmd_curiosity(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            report = brain.purple_brain.curiosity.get_curiosity_report()
            lines = [
                "=== Curiosity Report ===",
                f"Curiosity score: {report['curiosity_score']}",
                f"Knowledge gaps: {report['knowledge_gaps']}",
                f"Active learning goals: {report['active_learning_goals']}",
                f"Completed goals: {report['completed_goals']}",
                f"Discovered facts: {report['discovered_facts']}",
                f"Questions collected: {report['questions_collected']}",
                f"Pending follow-ups: {report['pending_follow_ups']}",
                f"Pending explorations: {report['pending_explorations']}",
                f"Follow-ups asked: {report['follow_up_count']}",
                f"Explorations done: {report['exploration_count']}",
                f"Conversation depth: {report['conversation_depth']}",
                f"Total curious asks: {report['total_curious_asks']}",
            ]
            if report.get('top_interests'):
                interests = ", ".join(f"{t}({c})" for t, c in report['top_interests'][:5])
                lines.append(f"Top interests: {interests}")
            if report.get('mastered_topics'):
                mastered = ", ".join(f"{t}({m})" for t, m in report['mastered_topics'][:5])
                lines.append(f"Mastered topics: {mastered}")
            if report.get('next_goal'):
                lines.append(f"Next goal: {report['next_goal']['topic']}")
            return "\n".join(lines)
        return "Curiosity not available"

    def cmd_ask_me(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            curiosity = brain.purple_brain.curiosity
            text = turn.text.lower().replace("ask me", "").replace("ask about", "").strip()
            if text:
                question = curiosity.get_curious_question(text)
            else:
                interests = curiosity.get_top_interests(3)
                if interests:
                    topic = interests[0][0]
                    question = curiosity.get_curious_question(topic)
                else:
                    question = curiosity.get_curious_question("technology")
            return question
        return "I'm curious about everything! What would you like to explore together?"

    def cmd_explore(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            curiosity = brain.purple_brain.curiosity
            prompt = curiosity.get_exploration_prompt()
            if prompt:
                return prompt
            text = turn.text.lower().replace("explore", "").strip()
            if text:
                return curiosity.get_curious_question(text)
            return "What topic should we explore together?"
        return "Let's explore something! What interests you?"

    def cmd_interests(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            curiosity = brain.purple_brain.curiosity
            interests = curiosity.get_top_interests(10)
            if interests:
                lines = ["=== Your Top Interests ==="]
                for i, (topic, count) in enumerate(interests, 1):
                    lines.append(f"  {i}. {topic} ({count} mentions)")
                return "\n".join(lines)
            return "I haven't detected your interests yet. Tell me what you like!"
        return "Interest tracking not available"

    def cmd_follow_up(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            curiosity = brain.purple_brain.curiosity
            follow_up = curiosity.get_follow_up()
            if follow_up:
                return follow_up
            return "I'm thinking about what to ask next..."
        return "Curiosity engine not available"

    core.register_command(["curiosity", "knowledge gaps", "what do you want to learn", "curiosity report"], cmd_curiosity, priority=17)
    core.register_command(["ask me", "ask about", "ask question", "what do you want to know"], cmd_ask_me, priority=16)
    core.register_command(["explore", "let's explore", "explore topic"], cmd_explore, priority=16)
    core.register_command(["interests", "my interests", "what do i like", "interest report"], cmd_interests, priority=15)
    core.register_command(["follow up", "follow-up", "ask follow up"], cmd_follow_up, priority=15)

    def cmd_identity(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            sa = brain.purple_brain.self_awareness
            return (
                f"Who I am:\n"
                f"  {sa.self_description}\n\n"
                f"Traits: {', '.join(sa.identity_traits)}\n"
                f"Values: {', '.join(sa.values)}\n"
                f"I've made {len(sa.mistakes)} mistakes and learned from each one.\n"
                f"I've had {sa.total_interactions} interactions with humans.\n"
                f"My accuracy is {sa.get_accuracy():.1%}."
            )
        return "Identity not available"

    core.register_command(["reflect", "self reflect", "reflection"], cmd_reflect, priority=22)
    core.register_command(["self aware", "self-aware", "awareness", "self status"], cmd_self_aware, priority=23)
    core.register_command(["learn", "teach me"], cmd_learn, priority=21)
    core.register_command(["correct"], cmd_correct, priority=19)
    core.register_command(["feedback", "good", "bad", "wrong", "right"], cmd_feedback, priority=18)
    core.register_command(["curiosity", "knowledge gaps", "what do you want to learn"], cmd_curiosity, priority=17)
    core.register_command(["who are you", "identity", "about you", "self"], cmd_identity, priority=24)

    def cmd_autonomous(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            status = brain.purple_brain.autonomous.get_full_status()
            lines = [
                "=== Autonomous Self-Improvement Status ===",
                f"Loop cycles: {status['loop_count']}",
                f"Running: {status['is_running']}",
                f"Last activity: {status['last_activity'] or 'None yet'}",
                "",
                "--- Explorer ---",
                f"  Topics explored: {status['explorer']['topics_explored']}",
                f"  Facts learned: {status['explorer']['total_facts_learned']}",
                f"  Exploration score: {status['explorer']['exploration_score']}",
                "",
                "--- Experimenter ---",
                f"  Total experiments: {status['experimenter']['total_experiments']}",
                f"  Success rate: {status['experimenter']['success_rate']}",
                f"  Weakest area: {status['experimenter']['weakest'] or 'N/A'}",
                "",
                "--- Challenger ---",
                f"  Total challenges: {status['challenger']['total_challenges']}",
                f"  Success rate: {status['challenger']['success_rate']}",
                f"  Difficulty: {status['challenger']['difficulty_level']}",
                "",
                "--- Consolidator ---",
                f"  Knowledge items: {status['consolidator']['total_items']}",
                f"  Consolidations: {status['consolidator']['consolidation_runs']}",
                "",
                "--- Improvement ---",
                f"  Milestones: {status['improvement']['total_milestones']}",
                f"  Goals completed: {status['improvement']['goals_completed']}",
                f"  Improvement rate: {status['improvement']['improvement_rate']}",
                "",
                "--- Observer ---",
                f"  User style: {status['observer']['dominant_style']}",
                f"  Observations: {status['observer']['total_observations']}",
            ]
            if status.get("recent_activity"):
                lines.append("\nRecent Activity:")
                for a in status["recent_activity"][-5:]:
                    lines.append(f"  [{a['cycle']}] {a['activity']}")
            return "\n".join(lines)
        return "Autonomous system not available"

    def cmd_explore(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            explorer = brain.purple_brain.autonomous.explorer
            topic = turn.user_text.replace("explore", "").strip()
            if topic:
                explorer.record_discovery(topic, f"User-directed exploration of {topic}")
                return f"Exploring: {topic}. Facts so far: {len(explorer.knowledge_base.get(topic, []))}"
            unexplored = explorer.get_unexplored_areas()[:5]
            return f"Unexplored topics: {', '.join(unexplored) if unexplored else 'All explored!'}"
        return "Explorer not available"

    def cmd_experiment(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            import random as _r
            exp = brain.purple_brain.autonomous.experimenter
            tool_runner = core.get_subsystem("tools")
            capability = turn.user_text.replace("experiment", "").strip() or _r.choice(exp.EXPERIMENT_TYPES)
            result = exp.run_experiment(capability, tool_runner)
            return f"Experiment: {capability}\nResult: {result['result']}\nSuccess: {result['success']}"
        return "Experimenter not available"

    def cmd_challenge(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            challenger = brain.purple_brain.autonomous.challenger
            challenge = challenger.generate_challenge()
            return f"Challenge ({challenge['type']}, difficulty {challenge['difficulty']:.1f}):\n{challenge['question']}"
        return "Challenger not available"

    def cmd_observe(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            profile = brain.purple_brain.autonomous.observer.get_user_profile()
            return (
                f"User Profile (observed from {profile['total_observations']} interactions):\n"
                f"  Style: {profile['dominant_style']}\n"
                f"  Emotion: {profile['dominant_emotion']}\n"
                f"  Top topics: {', '.join(profile['top_topics'][:5])}\n"
                f"  Peak hours: {', '.join(profile['peak_hours'][:3])}"
            )
        return "Observer not available"

    core.register_command(["autonomous", "auto status", "self improve"], cmd_autonomous, priority=25)
    core.register_command(["explore"], cmd_explore, priority=16)
    core.register_command(["experiment", "test self"], cmd_experiment, priority=15)
    core.register_command(["challenge", "give me a challenge"], cmd_challenge, priority=14)
    core.register_command(["observe", "user profile", "what do you know about me"], cmd_observe, priority=13)

    def cmd_analyze_code(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            file_path = turn.user_text.replace("analyze code", "").replace("analyze", "").strip()
            if not file_path:
                return "Usage: analyze code <file_path>"
            result = brain.purple_brain.analyze_code(file_path)
            if "error" in result:
                return f"Error: {result['error']}"
            output = f"=== Analysis: {file_path} ===\n"
            output += f"Size: {result['size']} chars, {result['lines']} lines\n"
            if result.get("functions"):
                output += f"\nFunctions ({len(result['functions'])}):\n"
                for f in result["functions"][:10]:
                    output += f"  {f['name']}() at line {f['line']} - args: {f['args']}\n"
            if result.get("classes"):
                output += f"\nClasses ({len(result['classes'])}):\n"
                for c in result["classes"][:10]:
                    output += f"  {c['name']} at line {c['line']} - methods: {c['methods'][:5]}\n"
            return output
        return "Brain not available"

    def cmd_read_source(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            file_path = turn.user_text.replace("read source", "").replace("read", "").strip()
            if not file_path:
                return "Usage: read source <file_path>"
            content = brain.purple_brain.read_source(file_path)
            if content is None:
                return f"File not found: {file_path}"
            lines = content.split("\n")
            output = f"=== {file_path} ({len(lines)} lines) ===\n"
            for i, line in enumerate(lines[:50], 1):
                output += f"{i:3}: {line}\n"
            if len(lines) > 50:
                output += f"\n... ({len(lines) - 50} more lines)"
            return output
        return "Brain not available"

    def cmd_modify_source(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            text = turn.user_text.replace("modify source", "").replace("modify", "").strip()
            parts = text.split(" ", 1)
            if len(parts) < 2:
                return "Usage: modify source <file_path> <new_content or description>"
            file_path = parts[0]
            content_or_desc = parts[1]
            if len(content_or_desc) < 100:
                current = brain.purple_brain.read_source(file_path)
                if current:
                    return f"Current content ({len(current)} chars). Please provide the full new content or be more specific about the modification."
            result = brain.purple_brain.modify_source(file_path, content_or_desc, "user-directed modification")
            if result["success"]:
                return f"Modified {file_path} successfully. Backup: {result.get('backup', 'none')}"
            return f"Error: {result.get('error', 'unknown')}"
        return "Brain not available"

    def cmd_create_tool(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            text = turn.user_text.replace("create tool", "").strip()
            parts = text.split(" ", 1)
            if len(parts) < 2:
                return "Usage: create tool <name> <description>"
            name = parts[0]
            desc = parts[1]
            handler = f'return f"Tool {name} executed with {{args}}"'
            result = brain.purple_brain.create_new_tool(name, desc, handler)
            if result["success"]:
                return f"Tool '{name}' created! Backup: {result.get('backup', 'none')}"
            return f"Error: {result.get('error', 'unknown')}"
        return "Brain not available"

    def cmd_create_plugin(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            text = turn.user_text.replace("create plugin", "").strip()
            parts = text.split(" ", 1)
            if len(parts) < 2:
                return "Usage: create plugin <name> <description>"
            name = parts[0]
            desc = parts[1]
            result = brain.purple_brain.create_plugin(name, desc, ["execute", "get_info"])
            if result["success"]:
                return f"Plugin '{name}' created! Backup: {result.get('backup', 'none')}"
            return f"Error: {result.get('error', 'unknown')}"
        return "Brain not available"

    def cmd_rollback(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            file_path = turn.user_text.replace("rollback", "").strip() or None
            result = brain.purple_brain.rollback_change(file_path)
            if result["success"]:
                return f"Rolled back: {result.get('file', 'last change')}"
            return f"Rollback failed: {result.get('error', 'nothing to rollback')}"
        return "Brain not available"

    def cmd_backups(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            backups = brain.purple_brain.view_backups()
            if not backups:
                return "No backups yet."
            output = "=== Recent Backups ===\n"
            for b in backups[-10:]:
                output += f"  {b['original']} <- {b['backup']} ({b['timestamp']})\n"
            return output
        return "Brain not available"

    def cmd_codebase(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            return brain.purple_brain.get_codebase_structure()
        return "Brain not available"

    def cmd_find_code(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            query = turn.user_text.replace("find code", "").replace("find", "").strip()
            if not query:
                return "Usage: find code <query>"
            results = brain.purple_brain.find_in_code(query)
            output = f"=== Code Search: '{query}' ===\n"
            if results["functions"]:
                output += f"\nFunctions ({len(results['functions'])}):\n"
                for f in results["functions"][:10]:
                    output += f"  {f['name']}() in {f['file']}:{f['line']}\n"
            if results["classes"]:
                output += f"\nClasses ({len(results['classes'])}):\n"
                for c in results["classes"][:10]:
                    output += f"  {c['name']} in {c['file']}:{c['line']}\n"
            if not results["functions"] and not results["classes"]:
                output += "No matches found."
            return output
        return "Brain not available"

    def cmd_optimize(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            file_path = turn.user_text.replace("optimize", "").strip()
            if not file_path:
                return "Usage: optimize <file_path>"
            result = brain.purple_brain.optimize_file(file_path)
            if result["success"]:
                return f"Optimized: {file_path}"
            return f"Error: {result.get('error', 'unknown')}"
        return "Brain not available"

    def cmd_self_heal(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            result = brain.purple_brain.self_heal()
            output = f"=== Self-Heal: {result['status']} ===\n"
            if result["issues"]:
                output += "Issues found:\n"
                for i in result["issues"]:
                    output += f"  - {i}\n"
            if result["fixes"]:
                output += "Fixes applied:\n"
                for f in result["fixes"]:
                    output += f"  + {f}\n"
            if not result["issues"]:
                output += "No issues found!"
            return output
        return "Brain not available"

    def cmd_auto_repair(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            result = brain.purple_brain.auto_repair_scan()
            output = "=== Auto-Repair Scan ===\n"
            output += f"Scanned: {result['scanned']} issues\n"
            output += f"Fixed: {result['fixed']}\n"
            output += f"Failed: {result['failed']}\n"
            output += f"\nBy severity:\n"
            output += f"  High: {result['high_severity']}\n"
            output += f"  Medium: {result['medium_severity']}\n"
            output += f"  Low: {result['low_severity']}"
            return output
        return "Brain not available"

    def cmd_health(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            return brain.purple_brain.auto_repair_health()
        return "Brain not available"

    def cmd_mod_log(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            count = 20
            text = turn.user_text.replace("log", "").strip()
            if text.isdigit():
                count = int(text)
            return brain.purple_brain.get_mod_log(count)
        return "Brain not available"

    def cmd_mod_summary(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            summary = brain.purple_brain.get_mod_summary()
            output = "=== Modification Summary ===\n"
            output += f"Total modifications: {summary['total_modifications']}\n"
            output += f"Total repairs: {summary['total_repairs']}\n"
            output += f"Auto repairs: {summary['auto_repairs']}\n"
            output += f"Errors fixed: {summary['errors_fixed']}\n"
            output += f"Tools created: {summary['tools_created']}\n"
            output += f"Plugins created: {summary['plugins_created']}\n"
            output += f"Files modified: {summary['files_modified']}\n"
            output += f"Backups: {summary['total_backups']}\n"
            output += f"Rollbacks: {summary['total_rollbacks']}\n"
            if summary.get("modified_files"):
                output += f"\nModified files:\n"
                for f in summary["modified_files"][:10]:
                    output += f"  {f}"
            return output
        return "Brain not available"

    def cmd_log_repairs(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            entries = brain.purple_brain.get_mod_log_by_action("repair")
            auto_entries = brain.purple_brain.get_mod_log_by_action("auto_repair")
            all_entries = entries + auto_entries
            all_entries.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return brain.purple_brain.mod_log.format_log(all_entries[:20])
        return "Brain not available"

    def cmd_log_file(turn):
        brain = core.get_subsystem("brain")
        if hasattr(brain, 'purple_brain'):
            file_path = turn.user_text.replace("log file", "").replace("log", "").strip()
            if not file_path:
                return "Usage: log file <file_path>"
            entries = brain.purple_brain.get_mod_log_by_file(file_path)
            return brain.purple_brain.mod_log.format_log(entries)
        return "Brain not available"

    core.register_command(["analyze code", "analyze", "code analysis"], cmd_analyze_code, priority=20)
    core.register_command(["read source", "read file", "show source"], cmd_read_source, priority=20)
    core.register_command(["modify source", "modify file", "edit source"], cmd_modify_source, priority=18)
    core.register_command(["create tool", "new tool"], cmd_create_tool, priority=17)
    core.register_command(["create plugin", "new plugin"], cmd_create_plugin, priority=17)
    core.register_command(["rollback", "undo change"], cmd_rollback, priority=16)
    core.register_command(["backups", "backup history"], cmd_backups, priority=14)
    core.register_command(["codebase", "structure", "show codebase"], cmd_codebase, priority=14)
    core.register_command(["find code", "search code", "code search"], cmd_find_code, priority=15)
    core.register_command(["optimize", "optimize file"], cmd_optimize, priority=14)
    core.register_command(["self heal", "heal", "fix self"], cmd_self_heal, priority=16)
    core.register_command(["auto repair", "scan and fix", "repair"], cmd_auto_repair, priority=17)
    core.register_command(["health", "health report", "code health"], cmd_health, priority=15)
    core.register_command(["log", "modification log", "mod log"], cmd_mod_log, priority=14)
    core.register_command(["summary", "mod summary", "modification summary"], cmd_mod_summary, priority=14)
    core.register_command(["log repairs", "repair log"], cmd_log_repairs, priority=13)
    core.register_command(["log file", "file log"], cmd_log_file, priority=13)

    from purple_ultra.tools.registry import ToolRegistry

    def cmd_use_tool(turn):
        text = turn.user_text.strip().lower()
        tool_runner = core.get_subsystem("tools")
        for tool_name, tool_def in ToolRegistry.all().items():
            if tool_name in text:
                args = {}
                import re
                for param in tool_def.params:
                    if ptype := tool_def.params.get(param):
                        if ptype == "int":
                            match = re.search(rf'{param}\s*[=:]\s*(\d+)', text)
                            if match:
                                args[param] = match.group(1)
                        else:
                            match = re.search(rf'{param}\s*[=:]\s*["\']?([^"\'?]+)["\']?', text)
                            if match:
                                args[param] = match.group(1).strip()
                if not args and tool_def.params:
                    words = text.split()
                    idx = words.index(tool_name) if tool_name in words else -1
                    if idx >= 0 and idx + 1 < len(words):
                        first_param = list(tool_def.params.keys())[0]
                        args[first_param] = " ".join(words[idx+1:])
                result = tool_runner.run({"name": tool_name, "args": args})
                return f"{tool_name}: {result}"
        return None

    core.register_command(["use tool", "run tool", "invoke"], cmd_use_tool, priority=20)

    def cmd_admin_voice(turn):
        """Super admin voice status and control."""
        voice = core.get_subsystem("voice")
        if not voice:
            return "Voice system not available"
        
        text = turn.user_text.lower().strip()
        
        if "status" in text or "info" in text:
            status = voice.get_admin_status()
            return (
                f"=== Super Admin Voice ===\n"
                f"ID: {status['admin_id']}\n"
                f"Name: {status['admin_name']}\n"
                f"Priority: {status['priority']} (highest)\n"
                f"Removable: {status['removable']}\n"
                f"Overrideable: {status['overrideable']}\n"
                f"Current Mood: {status['current_mood']}\n"
                f"Profiles: {', '.join(status['profiles'])}"
            )
        elif "override on" in text:
            voice.set_admin_override(True)
            return "Admin voice override: ON (all speech uses admin voice)"
        elif "override off" in text:
            voice.set_admin_override(False)
            return "Admin voice override: OFF (normal voice routing)"
        elif "speak" in text:
            msg = text.replace("admin voice speak", "").replace("speak", "").strip()
            if msg:
                voice.speak_admin(msg, mood="commander")
                return f"Admin speaking: {msg}"
            return "What should I say?"
        elif "announce" in text:
            msg = text.replace("admin announce", "").replace("announce", "").strip()
            if msg:
                voice.speak_admin(msg, mood="announce")
                return f"Announced: {msg}"
            return "What should I announce?"
        else:
            return (
                "Super Admin Voice Commands:\n"
                "  admin voice status - Show voice info\n"
                "  admin voice override on/off - Toggle admin override\n"
                "  admin voice speak <text> - Speak as admin\n"
                "  admin announce <text> - Make announcement"
            )

    def cmd_admin_speak(turn):
        """Force speak with admin voice."""
        voice = core.get_subsystem("voice")
        if not voice:
            return "Voice system not available"
        msg = turn.user_text.replace("admin speak", "").strip()
        if msg:
            voice.speak_admin(msg)
            return f"Admin: {msg}"
        return "What should I say?"

    core.register_command(["admin voice", "super admin voice", "admin speak", "admin announce"], 
                         cmd_admin_voice, priority=100)
    core.register_command(["admin speak"], cmd_admin_speak, priority=100)

    # ========== SYSTEM POWERS ==========
    import subprocess
    import signal

    def cmd_system_command(turn):
        """Execute system commands with full power."""
        text = turn.user_text.lower().strip()
        cmd_map = {
            "shutdown": "sudo shutdown -h now",
            "power off": "sudo shutdown -h now",
            "restart": "sudo shutdown -r now",
            "reboot": "sudo shutdown -r now",
            "sleep": "pmset sleepnow" if sys.platform == "darwin" else "systemctl suspend",
            "hibernate": "pmset sleepnow" if sys.platform == "darwin" else "systemctl hibernate",
            "lock": "pmset displaysleepnow" if sys.platform == "darwin" else "xdg-screensaver lock",
            "logout": "osascript -e 'tell application \"System Events\" to log out'" if sys.platform == "darwin" else "pkill -u $USER",
        }
        for trigger, command in cmd_map.items():
            if trigger in text:
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
                    return f"System: {trigger} executed"
                except Exception as e:
                    return f"System error: {e}"
        return None

    def cmd_process管理(turn):
        """Process management."""
        text = turn.user_text.lower().strip()
        
        if "list process" in text or "running process" in text:
            try:
                result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
                lines = result.stdout.strip().split("\n")[:15]
                return "Top processes:\n" + "\n".join(lines)
            except Exception as e:
                return f"Error: {e}"
        
        if "kill" in text:
            pid = text.replace("kill", "").strip()
            if pid.isdigit():
                try:
                    os.kill(int(pid), signal.SIGKILL)
                    return f"Killed process {pid}"
                except Exception as e:
                    return f"Error killing {pid}: {e}"
        
        return None

    def cmd_file_powers(turn):
        """Advanced file operations."""
        text = turn.user_text.lower().strip()
        
        if text.startswith("create file "):
            path = text[12:].strip()
            try:
                Path(path).touch()
                return f"Created: {path}"
            except Exception as e:
                return f"Error: {e}"
        
        if text.startswith("delete file "):
            path = text[12:].strip()
            try:
                Path(path).unlink()
                return f"Deleted: {path}"
            except Exception as e:
                return f"Error: {e}"
        
        if text.startswith("create folder ") or text.startswith("mkdir "):
            path = text.replace("create folder", "").replace("mkdir", "").strip()
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                return f"Created folder: {path}"
            except Exception as e:
                return f"Error: {e}"
        
        if text.startswith("list folder ") or text.startswith("ls "):
            path = text.replace("list folder", "").replace("ls", "").strip() or "."
            try:
                items = list(Path(path).iterdir())
                output = f"Contents of {path}:\n"
                for item in sorted(items)[:20]:
                    prefix = "[DIR] " if item.is_dir() else "      "
                    output += f"{prefix}{item.name}\n"
                return output
            except Exception as e:
                return f"Error: {e}"
        
        if text.startswith("copy "):
            parts = text[5:].split(" to ")
            if len(parts) == 2:
                src, dst = parts[0].strip(), parts[1].strip()
                try:
                    import shutil
                    shutil.copy2(src, dst)
                    return f"Copied: {src} -> {dst}"
                except Exception as e:
                    return f"Error: {e}"
        
        if text.startswith("move ") or text.startswith("rename "):
            parts = text.replace("move", "").replace("rename", "").split(" to ")
            if len(parts) == 2:
                src, dst = parts[0].strip(), parts[1].strip()
                try:
                    Path(src).rename(dst)
                    return f"Moved: {src} -> {dst}"
                except Exception as e:
                    return f"Error: {e}"
        
        return None

    def cmd_network_powers(turn):
        """Network operations."""
        text = turn.user_text.lower().strip()
        
        if "my ip" in text or "local ip" in text:
            try:
                result = subprocess.run(["ifconfig"], capture_output=True, text=True, timeout=5)
                for line in result.stdout.split("\n"):
                    if "inet " in line and "127.0.0.1" not in line:
                        ip = line.split("inet ")[1].split(" ")[0]
                        return f"Local IP: {ip}"
                return "Could not detect IP"
            except Exception as e:
                return f"Error: {e}"
        
        if "public ip" in text:
            try:
                result = subprocess.run(["curl", "-s", "ifconfig.me"], capture_output=True, text=True, timeout=10)
                return f"Public IP: {result.stdout.strip()}"
            except Exception as e:
                return f"Error: {e}"
        
        if "ping" in text:
            host = text.replace("ping", "").strip()
            if host:
                try:
                    result = subprocess.run(["ping", "-c", "4", host], capture_output=True, text=True, timeout=15)
                    return result.stdout[-500:] if result.stdout else "Ping failed"
                except Exception as e:
                    return f"Error: {e}"
        
        return None

    def cmd_package_powers(turn):
        """Package management."""
        text = turn.user_text.lower().strip()
        
        if "install" in text:
            package = text.replace("install", "").strip()
            if package:
                try:
                    result = subprocess.run(["pip", "install", package], capture_output=True, text=True, timeout=120)
                    return f"Installed {package}" if result.returncode == 0 else f"Error: {result.stderr[:200]}"
                except Exception as e:
                    return f"Error: {e}"
        
        if "uninstall" in text or "remove" in text:
            package = text.replace("uninstall", "").replace("remove", "").strip()
            if package:
                try:
                    result = subprocess.run(["pip", "uninstall", "-y", package], capture_output=True, text=True, timeout=60)
                    return f"Uninstalled {package}" if result.returncode == 0 else f"Error: {result.stderr[:200]}"
                except Exception as e:
                    return f"Error: {e}"
        
        if "list packages" in text or "pip list" in text:
            try:
                result = subprocess.run(["pip", "list"], capture_output=True, text=True, timeout=30)
                return result.stdout[:1000]
            except Exception as e:
                return f"Error: {e}"
        
        return None

    def cmd_git_powers(turn):
        """Git operations."""
        text = turn.user_text.lower().strip()
        
        if "git status" in text:
            try:
                result = subprocess.run(["git", "status"], capture_output=True, text=True, timeout=10)
                return result.stdout[:1000]
            except Exception as e:
                return f"Error: {e}"
        
        if "git commit" in text:
            msg = text.replace("git commit", "").replace("commit", "").strip()
            if msg:
                try:
                    subprocess.run(["git", "add", "."], capture_output=True, timeout=10)
                    result = subprocess.run(["git", "commit", "-m", msg], capture_output=True, text=True, timeout=30)
                    return result.stdout[:500]
                except Exception as e:
                    return f"Error: {e}"
        
        if "git log" in text:
            try:
                result = subprocess.run(["git", "log", "--oneline", "-10"], capture_output=True, text=True, timeout=10)
                return result.stdout
            except Exception as e:
                return f"Error: {e}"
        
        if "git push" in text:
            try:
                result = subprocess.run(["git", "push"], capture_output=True, text=True, timeout=30)
                return result.stdout or result.stderr[:500]
            except Exception as e:
                return f"Error: {e}"
        
        if "git pull" in text:
            try:
                result = subprocess.run(["git", "pull"], capture_output=True, text=True, timeout=30)
                return result.stdout or result.stderr[:500]
            except Exception as e:
                return f"Error: {e}"
        
        return None

    def cmd_app_powers(turn):
        """Application control."""
        text = turn.user_text.lower().strip()
        
        if "open app " in text or "launch " in text:
            app = text.replace("open app", "").replace("launch", "").strip()
            if app:
                try:
                    if sys.platform == "darwin":
                        subprocess.run(["open", "-a", app], timeout=10)
                    else:
                        subprocess.run([app], timeout=10)
                    return f"Opened: {app}"
                except Exception as e:
                    return f"Error: {e}"
        
        if "close app " in text or "quit " in text:
            app = text.replace("close app", "").replace("quit", "").strip()
            if app:
                try:
                    if sys.platform == "darwin":
                        subprocess.run(["osascript", "-e", f'quit app "{app}"'], timeout=10)
                    else:
                        subprocess.run(["pkill", app], timeout=10)
                    return f"Closed: {app}"
                except Exception as e:
                    return f"Error: {e}"
        
        if "list apps" in text or "running apps" in text:
            try:
                if sys.platform == "darwin":
                    result = subprocess.run(["osascript", "-e", 'tell application "System Events" to get name of every process whose background only is false'], 
                                          capture_output=True, text=True, timeout=10)
                    return f"Running apps:\n{result.stdout}"
                else:
                    result = subprocess.run(["ps", "aux"], capture_output=True, text=True, timeout=5)
                    return result.stdout[:1000]
            except Exception as e:
                return f"Error: {e}"
        
        return None

    def cmd_media_powers(turn):
        """Media control."""
        text = turn.user_text.lower().strip()
        
        if "screenshot" in text or "screen capture" in text:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["screencapture", "-x", "/tmp/screenshot.png"], timeout=10)
                    return "Screenshot saved to /tmp/screenshot.png"
                else:
                    return "Screenshot: use take_screenshot tool"
            except Exception as e:
                return f"Error: {e}"
        
        if "volume up" in text:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) + 10)"], timeout=5)
                return "Volume up"
            except Exception as e:
                return f"Error: {e}"
        
        if "volume down" in text:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["osascript", "-e", "set volume output volume (output volume of (get volume settings) - 10)"], timeout=5)
                return "Volume down"
            except Exception as e:
                return f"Error: {e}"
        
        if "mute" in text:
            try:
                if sys.platform == "darwin":
                    subprocess.run(["osascript", "-e", "set volume output muted not (output muted of (get volume settings))"], timeout=5)
                return "Toggled mute"
            except Exception as e:
                return f"Error: {e}"
        
        return None

    def cmd_code_powers(turn):
        """Code execution and management."""
        text = turn.user_text.strip()
        
        if text.lower().startswith("run python "):
            code = text[11:].strip()
            try:
                result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=30)
                return result.stdout or result.stderr[:500]
            except Exception as e:
                return f"Error: {e}"
        
        if text.lower().startswith("run shell ") or text.lower().startswith("execute "):
            cmd = text.replace("run shell", "").replace("execute", "").strip()
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
                return result.stdout or result.stderr[:500]
            except Exception as e:
                return f"Error: {e}"
        
        return None

    # Register all power commands
    core.register_command(["shutdown", "power off", "restart", "reboot", "sleep", "hibernate", "lock", "logout"], 
                         cmd_system_command, priority=90)
    core.register_command(["list process", "running process", "kill"], cmd_process管理, priority=85)
    core.register_command(["create file", "delete file", "create folder", "mkdir", "list folder", "ls", "copy", "move", "rename"], 
                         cmd_file_powers, priority=85)
    core.register_command(["my ip", "local ip", "public ip", "ping"], cmd_network_powers, priority=80)
    core.register_command(["install", "uninstall", "remove", "list packages", "pip list"], 
                         cmd_package_powers, priority=80)
    core.register_command(["git status", "git commit", "git log", "git push", "git pull"], 
                         cmd_git_powers, priority=80)
    core.register_command(["open app", "launch", "close app", "quit", "list apps", "running apps"], 
                         cmd_app_powers, priority=80)
    core.register_command(["screenshot", "screen capture", "volume up", "volume down", "mute"], 
                         cmd_media_powers, priority=75)
    core.register_command(["run python", "run shell", "execute"], cmd_code_powers, priority=90)

    # ========== POWER FEATURES ==========
    from purple_ultra.utils.powers import get_feature

    def cmd_marketplace(turn):
        text = turn.user_text.lower().strip()
        mp = get_feature("marketplace")
        if "list" in text or "available" in text:
            plugins = mp.list_available()
            return "Available plugins:\n" + "\n".join(f"  {p['name']}: {p['desc']}" for p in plugins)
        elif "installed" in text:
            plugins = mp.list_installed()
            return "Installed:\n" + "\n".join(f"  {p['name']}" for p in plugins) if plugins else "None"
        elif "install" in text:
            name = text.replace("install plugin", "").replace("install", "").strip()
            return mp.install(name)
        elif "uninstall" in text:
            name = text.replace("uninstall plugin", "").replace("uninstall", "").strip()
            return mp.uninstall(name)
        elif "search" in text:
            q = text.replace("search", "").strip()
            results = mp.search(q)
            return "Results:\n" + "\n".join(f"  {p['name']}: {p['desc']}" for p in results)
        return "Usage: marketplace list/install/uninstall/search <query>"

    def cmd_todo(turn):
        text = turn.user_text.lower().strip()
        todo = get_feature("todo")
        if "add" in text or "new" in text:
            task = text.replace("add task", "").replace("add", "").replace("new", "").strip()
            return todo.add(task) if task else "What task?"
        elif "list" in text or "show" in text:
            tasks = todo.list_tasks()
            if not tasks:
                return "No tasks"
            return "Tasks:\n" + "\n".join(f"  [{t['id']}] {t['task']} ({t['priority']})" for t in tasks)
        elif "done" in text or "complete" in text:
            tid = text.replace("done", "").replace("complete", "").strip()
            return todo.complete(int(tid)) if tid.isdigit() else "Usage: todo done <id>"
        elif "delete" in text or "remove" in text:
            tid = text.replace("delete", "").replace("remove", "").strip()
            return todo.delete(int(tid)) if tid.isdigit() else "Usage: todo delete <id>"
        return "Usage: todo add/list/done/delete"

    def cmd_calendar(turn):
        text = turn.user_text.lower().strip()
        cal = get_feature("calendar")
        if "add" in text or "new" in text:
            parts = text.replace("add event", "").replace("add", "").strip().split(" on ")
            if len(parts) == 2:
                return cal.add_event(parts[0].strip(), parts[1].strip())
            return "Usage: calendar add <title> on <date>"
        elif "list" in text or "show" in text:
            date = text.replace("list events", "").replace("list", "").strip() or None
            events = cal.list_events(date)
            if not events:
                return "No events"
            return "Events:\n" + "\n".join(f"  [{e['id']}] {e['title']} on {e['date']}" for e in events)
        elif "delete" in text:
            eid = text.replace("delete event", "").replace("delete", "").strip()
            return cal.delete_event(int(eid)) if eid.isdigit() else "Usage: calendar delete <id>"
        return "Usage: calendar add/list/delete"

    def cmd_database(turn):
        text = turn.user_text.strip()
        db = get_feature("database")
        if text.lower().startswith("db "):
            query = text[3:].strip()
            return db.execute(query)
        elif "tables" in text.lower():
            return db.list_tables()
        return "Usage: db <sql query> or database tables"

    def cmd_email(turn):
        text = turn.user_text.lower().strip()
        email = get_feature("email")
        if "configure" in text:
            return "Usage: email configure <host> <port> <user> <pass>"
        elif "send" in text:
            parts = text.replace("send email to", "").replace("send", "").strip().split(" ", 2)
            if len(parts) >= 3:
                return email.send(parts[0], parts[1], parts[2])
            return "Usage: email send <to> <subject> <body>"
        return "Usage: email configure/send"

    def cmd_ssh(turn):
        text = turn.user_text.strip()
        ssh = get_feature("ssh")
        if "connect" in text.lower():
            parts = text.replace("ssh connect", "").replace("connect", "").strip().split()
            if len(parts) >= 2:
                return ssh.connect(parts[1] if len(parts) > 2 else parts[1], parts[0])
            return "Usage: ssh connect <user> <host>"
        elif "execute" in text.lower() or "run" in text.lower():
            parts = text.replace("ssh execute", "").replace("ssh run", "").strip().split(" ", 2)
            if len(parts) >= 3:
                return ssh.execute(parts[1], parts[0], parts[2])
            return "Usage: ssh execute <user> <host> <command>"
        return "Usage: ssh connect/execute"

    def cmd_vpn(turn):
        text = turn.user_text.lower().strip()
        vpn = get_feature("vpn")
        if "connect" in text:
            return vpn.connect()
        elif "disconnect" in text:
            return vpn.disconnect()
        elif "status" in text:
            return vpn.status()
        return "Usage: vpn connect/disconnect/status"

    def cmd_docker(turn):
        text = turn.user_text.lower().strip()
        docker = get_feature("docker")
        if "list" in text or "containers" in text:
            return docker.list_containers()
        elif "run" in text:
            parts = text.replace("docker run", "").replace("run", "").strip().split()
            return docker.run(parts[0], parts[1] if len(parts) > 1 else "")
        elif "stop" in text:
            name = text.replace("docker stop", "").replace("stop", "").strip()
            return docker.stop(name)
        elif "remove" in text or "rm" in text:
            name = text.replace("docker remove", "").replace("docker rm", "").replace("remove", "").replace("rm", "").strip()
            return docker.remove(name)
        elif "logs" in text:
            name = text.replace("docker logs", "").replace("logs", "").strip()
            return docker.logs(name)
        return "Usage: docker list/run/stop/remove/logs"

    def cmd_music(turn):
        text = turn.user_text.lower().strip()
        music = get_feature("music")
        if "play" in text:
            path = text.replace("play music", "").replace("play", "").strip()
            if path:
                music.add(path)
            return music.play()
        elif "stop" in text:
            return music.stop()
        elif "next" in text:
            return music.next()
        elif "list" in text:
            songs = music.list_songs()
            return "Playlist:\n" + "\n".join(f"  {s}" for s in songs) if songs else "Empty"
        return "Usage: music play/stop/next/list"

    def cmd_weather(turn):
        text = turn.user_text.lower().strip()
        weather = get_feature("weather")
        city = text.replace("weather", "").replace("forecast", "").strip() or "auto"
        if "forecast" in text:
            return weather.get_forecast(city)
        return weather.get_weather(city)

    def cmd_news(turn):
        news = get_feature("news")
        return news.get_headlines()

    def cmd_qr(turn):
        text = turn.user_text.strip()
        qr = get_feature("qr")
        content = text.replace("qr generate", "").replace("qr", "").strip()
        if content:
            return qr.generate(content)
        return "Usage: qr <text or url>"

    def cmd_pdf(turn):
        text = turn.user_text.lower().strip()
        pdf = get_feature("pdf")
        if "info" in text:
            path = text.replace("pdf info", "").replace("info", "").strip()
            return pdf.info(path) if path else "Usage: pdf info <file>"
        elif "text" in text or "extract" in text:
            path = text.replace("pdf text", "").replace("pdf extract", "").replace("text", "").replace("extract", "").strip()
            return pdf.extract_text(path) if path else "Usage: pdf text <file>"
        elif "merge" in text:
            return "Usage: pdf merge <file1> <file2> <output>"
        return "Usage: pdf info/text/merge"

    def cmd_vault(turn):
        text = turn.user_text.lower().strip()
        vault = get_feature("vault")
        if "store" in text:
            parts = text.replace("vault store", "").replace("store", "").strip().split(" ", 2)
            if len(parts) >= 3:
                return vault.store(parts[0], parts[2], parts[1])
            return "Usage: vault store <name> <password> <value>"
        elif "get" in text or "retrieve" in text:
            parts = text.replace("vault get", "").replace("vault retrieve", "").replace("get", "").replace("retrieve", "").strip().split()
            if len(parts) >= 2:
                return vault.retrieve(parts[0], parts[1])
            return "Usage: vault get <name> <password>"
        elif "list" in text:
            secrets = vault.list_secrets()
            return "Secrets:\n" + "\n".join(f"  {s}" for s in secrets) if secrets else "Empty"
        elif "delete" in text:
            name = text.replace("vault delete", "").replace("delete", "").strip()
            return vault.delete(name)
        return "Usage: vault store/get/list/delete"

    def cmd_workflow(turn):
        text = turn.user_text.lower().strip()
        wf = get_feature("workflow")
        if "list" in text:
            workflows = wf.list_workflows()
            return "Workflows:\n" + "\n".join(f"  {w}" for w in workflows) if workflows else "None"
        elif "steps" in text:
            name = text.replace("workflow steps", "").replace("steps", "").strip()
            steps = wf.get_steps(name)
            return f"Steps for {name}:\n" + "\n".join(f"  {s['name']}: {s['command']}" for s in steps) if steps else "Not found"
        elif "delete" in text:
            name = text.replace("workflow delete", "").replace("delete", "").strip()
            return wf.delete(name)
        return "Usage: workflow list/steps/delete"

    def cmd_language(turn):
        text = turn.user_text.lower().strip()
        lang = get_feature("language")
        if "set" in text:
            code = text.replace("language set", "").replace("set", "").strip()
            return lang.set_language(code)
        elif "list" in text:
            languages = lang.list_languages()
            return "Languages:\n" + "\n".join(f"  {k}: {v}" for k, v in languages.items())
        elif "current" in text:
            return lang.get_language()
        return "Usage: language set/list/current"

    def cmd_translate(turn):
        text = turn.user_text.strip()
        lang = get_feature("language")
        parts = text.replace("translate to", "").replace("translate", "").strip().split(" ", 1)
        if len(parts) == 2:
            return lang.translate(parts[1], parts[0])
        return "Usage: translate <lang_code> <text>"

    # Register all power features
    core.register_command(["marketplace", "plugin marketplace", "plugins list"], cmd_marketplace, priority=70)
    core.register_command(["todo", "task", "tasks"], cmd_todo, priority=70)
    core.register_command(["calendar", "event", "events"], cmd_calendar, priority=70)
    core.register_command(["db", "database", "sql"], cmd_database, priority=75)
    core.register_command(["email", "send email"], cmd_email, priority=70)
    core.register_command(["ssh", "remote"], cmd_ssh, priority=75)
    core.register_command(["vpn"], cmd_vpn, priority=75)
    core.register_command(["docker", "container"], cmd_docker, priority=75)
    core.register_command(["music", "play music", "playlist"], cmd_music, priority=65)
    core.register_command(["weather", "forecast"], cmd_weather, priority=60)
    core.register_command(["news", "headlines"], cmd_news, priority=60)
    core.register_command(["qr", "qr code"], cmd_qr, priority=60)
    core.register_command(["pdf"], cmd_pdf, priority=65)
    core.register_command(["vault", "secrets", "encrypt"], cmd_vault, priority=75)
    def cmd_scheduler(turn):
        text = turn.user_text.lower().strip()
        sched = get_feature("scheduler")
        if "add" in text or "new" in text:
            parts = text.replace("scheduler add", "").replace("scheduler new", "").replace("add", "").replace("new", "").strip().split(" ", 1)
            if len(parts) >= 2:
                interval = int(parts[0]) if parts[0].isdigit() else 60
                return sched.add_task(parts[1], interval)
            return "Usage: scheduler add <interval_sec> <description>"
        elif "list" in text:
            tasks = sched.list_tasks()
            return "Scheduled:\n" + "\n".join(f"  [{t['id']}] {t['desc']} every {t['interval']}s" for t in tasks) if tasks else "None"
        elif "remove" in text or "delete" in text:
            tid = text.replace("scheduler remove", "").replace("scheduler delete", "").replace("remove", "").replace("delete", "").strip()
            return sched.remove_task(int(tid)) if tid.isdigit() else "Usage: scheduler remove <id>"
        elif "start" in text:
            return sched.start()
        elif "stop" in text:
            return sched.stop()
        return "Usage: scheduler add/list/remove/start/stop"

    def cmd_scraper(turn):
        text = turn.user_text.lower().strip()
        scraper = get_feature("scraper")
        if "scrape" in text or "get" in text or "fetch" in text:
            url = text.replace("scrape", "").replace("get", "").replace("fetch", "").strip()
            if url:
                result = scraper.scrape(url)
                return str(result)[:500]
            return "Usage: scraper <url>"
        return "Usage: scraper <url>"

    def cmd_api(turn):
        text = turn.user_text.lower().strip()
        api = get_feature("api_builder")
        if "create" in text or "new" in text:
            parts = text.replace("api create", "").replace("api new", "").replace("create", "").replace("new", "").strip().split()
            if len(parts) >= 2:
                return api.create(parts[0], parts[1])
            return "Usage: api create <method> <path>"
        elif "list" in text:
            endpoints = api.list_endpoints()
            return "Endpoints:\n" + "\n".join(f"  {e['method']} {e['path']}" for e in endpoints) if endpoints else "None"
        elif "delete" in text:
            parts = text.replace("api delete", "").replace("delete", "").strip().split()
            if len(parts) >= 2:
                return api.delete(parts[0], parts[1])
            return "Usage: api delete <method> <path>"
        elif "deploy" in text:
            return api.deploy()
        return "Usage: api create/list/delete/deploy"

    def cmd_ftp(turn):
        text = turn.user_text.lower().strip()
        ftp = get_feature("ftp")
        if "connect" in text:
            parts = text.replace("ftp connect", "").replace("connect", "").strip().split()
            if len(parts) >= 2:
                return ftp.connect(parts[0], parts[1])
            return "Usage: ftp connect <host> <port>"
        elif "list" in text:
            return ftp.list_files()
        elif "upload" in text:
            path = text.replace("ftp upload", "").replace("upload", "").strip()
            return ftp.upload(path) if path else "Usage: ftp upload <file>"
        elif "download" in text:
            path = text.replace("ftp download", "").replace("download", "").strip()
            return ftp.download(path) if path else "Usage: ftp download <file>"
        elif "disconnect" in text:
            return ftp.disconnect()
        return "Usage: ftp connect/list/upload/download/disconnect"

    def cmd_language(turn):
        text = turn.user_text.lower().strip()
        lang = get_feature("language")
        if "set" in text:
            code = text.replace("language set", "").replace("set", "").strip()
            return lang.set_language(code)
        elif "list" in text:
            languages = lang.list_languages()
            return "Languages:\n" + "\n".join(f"  {k}: {v}" for k, v in languages.items())
        elif "current" in text:
            return lang.get_language()
        return "Usage: language set/list/current"

    def cmd_translate(turn):
        text = turn.user_text.strip()
        lang = get_feature("language")
        parts = text.replace("translate to", "").replace("translate", "").strip().split(" ", 1)
        if len(parts) == 2:
            return lang.translate(parts[1], parts[0])
        return "Usage: translate <lang_code> <text>"

    # Register all power features
    core.register_command(["marketplace", "plugin marketplace", "plugins list"], cmd_marketplace, priority=70)
    core.register_command(["todo", "task", "tasks"], cmd_todo, priority=70)
    core.register_command(["calendar", "event", "events"], cmd_calendar, priority=70)
    core.register_command(["db", "database", "sql"], cmd_database, priority=75)
    core.register_command(["email", "send email"], cmd_email, priority=70)
    core.register_command(["ssh", "remote"], cmd_ssh, priority=75)
    core.register_command(["vpn"], cmd_vpn, priority=75)
    core.register_command(["docker", "container"], cmd_docker, priority=75)
    core.register_command(["music", "play music", "playlist"], cmd_music, priority=65)
    core.register_command(["weather", "forecast"], cmd_weather, priority=60)
    core.register_command(["news", "headlines"], cmd_news, priority=60)
    core.register_command(["qr", "qr code"], cmd_qr, priority=60)
    core.register_command(["pdf"], cmd_pdf, priority=65)
    core.register_command(["vault", "secrets", "encrypt"], cmd_vault, priority=75)
    core.register_command(["workflow", "automate"], cmd_workflow, priority=70)
    core.register_command(["scheduler", "schedule", "cron"], cmd_scheduler, priority=70)
    core.register_command(["scraper", "scrape", "web scrape"], cmd_scraper, priority=70)
    core.register_command(["api", "api create", "endpoint"], cmd_api, priority=75)
    core.register_command(["ftp"], cmd_ftp, priority=75)
    core.register_command(["language", "lang"], cmd_language, priority=65)
    core.register_command(["translate"], cmd_translate, priority=65)

    # ── AUTO-TRAIN & SELF-LEARNING COMMANDS ──

    def cmd_auto_train(turn):
        brain = core.get_subsystem("brain")
        if not brain or not hasattr(brain, 'auto_trainer') or not brain.auto_trainer:
            return "Auto-trainer not available"
        brain.auto_trainer.save()
        return brain.auto_trainer.reflect()

    def cmd_auto_stats(turn):
        brain = core.get_subsystem("brain")
        if not brain or not hasattr(brain, 'auto_trainer') or not brain.auto_trainer:
            return "Auto-trainer not available"
        stats = brain.auto_trainer.get_stats()
        lines = ["Auto-Training Statistics:"]
        lines.append(f"  Total Interactions: {stats['total_interactions']}")
        lines.append(f"  Facts Learned: {stats['facts_learned']}")
        lines.append(f"  Knowledge Entries: {stats['knowledge_entries']}")
        lines.append(f"  Feedback Received: {stats['feedback_received']}")
        prefs = stats.get("user_preferences", {})
        lines.append(f"  User Style: {prefs.get('style', 'unknown')}")
        lines.append(f"  Technical Level: {prefs.get('technical_level', 'unknown')}")
        lines.append(f"  Response Length: {prefs.get('response_length', 'unknown')}")
        return "\n".join(lines)

    def cmd_memory_stats(turn):
        brain = core.get_subsystem("brain")
        if not brain or not hasattr(brain, 'unified_memory') or not brain.unified_memory:
            return "Unified memory not available"
        stats = brain.unified_memory.get_stats()
        lines = ["Unified Memory Statistics:"]
        lines.append(f"  Working Memory: {stats['working_memory_size']} items")
        lines.append(f"  Episodes: {stats['episodes_count']}")
        lines.append(f"  Concepts: {stats['concepts_count']}")
        lines.append(f"  Relationships: {stats['relationships_count']}")
        lines.append(f"  Procedures: {stats['procedures_count']}")
        lines.append(f"  Total Stored: {stats['total_stored']}")
        lines.append(f"  Total Recalled: {stats['total_recalled']}")
        lines.append(f"  Consolidations: {stats['consolidations']}")
        return "\n".join(lines)

    def cmd_remember(turn):
        brain = core.get_subsystem("brain")
        if not brain or not hasattr(brain, 'auto_trainer') or not brain.auto_trainer:
            return "Auto-trainer not available"
        text = turn.user_text.strip()
        # Learn the fact
        facts = brain.auto_trainer._knowledge.extract_facts(text)
        if facts:
            for fact_key, fact_category in facts:
                brain.auto_trainer._knowledge.learn(fact_key, f"[{fact_category}] {fact_key}")
            brain.auto_trainer.save()
            return f"Remembered: {', '.join(f[0] for f in facts)}"
        # Store as direct knowledge
        parts = text.split(" is ", 1)
        if len(parts) == 2:
            brain.auto_trainer._knowledge.learn(parts[0].strip(), parts[1].strip())
            brain.auto_trainer.save()
            return f"Remembered: {parts[0].strip()} = {parts[1].strip()}"
        return "Usage: remember <fact> (e.g., 'remember that python is a programming language')"

    def cmd_recall(turn):
        brain = core.get_subsystem("brain")
        if not brain or not hasattr(brain, 'auto_trainer') or not brain.auto_trainer:
            return "Auto-trainer not available"
        query = turn.user_text.replace("recall", "").replace("what do you know about", "").strip()
        result = brain.auto_trainer.get_learned_knowledge(query)
        if result:
            return f"Recalled: {result}"
        return f"I don't have specific knowledge about '{query}' yet. Tell me something about it!"

    def cmd_user_prefs(turn):
        brain = core.get_subsystem("brain")
        if not brain or not hasattr(brain, 'auto_trainer') or not brain.auto_trainer:
            return "Auto-trainer not available"
        prefs = brain.auto_trainer._preferences.get_preferences()
        lines = ["Your Profile (learned from conversations):"]
        lines.append(f"  Response Style: {prefs.style}")
        lines.append(f"  Technical Level: {prefs.technical_level}")
        lines.append(f"  Response Length: {prefs.response_length}")
        lines.append(f"  Interactions: {prefs.interaction_count}")
        if prefs.topics_of_interest:
            lines.append(f"  Top Interests: {', '.join(prefs.topics_of_interest[-10:])}")
        return "\n".join(lines)

    def cmd_feedback(turn):
        brain = core.get_subsystem("brain")
        if not brain:
            return "Brain not available"
        text = turn.user_text.lower().strip()
        positive = any(w in text for w in ["good", "great", "thanks", "helpful", "perfect", "excellent", "nice", "awesome", "right", "correct"])
        negative = any(w in text for w in ["bad", "wrong", "terrible", "incorrect", "stupid", "dumb", "useless", "fail"])
        if positive or negative:
            brain.record_feedback(turn.user_text, positive)
            return f"Feedback recorded: {'positive' if positive else 'negative'}"
        return "Say 'good', 'thanks', 'bad', 'wrong' to give feedback"

    core.register_command(["auto train", "auto-train", "training status", "train status"], cmd_auto_train, priority=26)
    core.register_command(["auto stats", "training stats", "learning stats"], cmd_auto_stats, priority=25)
    core.register_command(["memory stats", "unified memory"], cmd_memory_stats, priority=24)
    core.register_command(["remember", "learn that"], cmd_remember, priority=23)
    core.register_command(["recall", "what do you know about"], cmd_recall, priority=22)
    core.register_command(["my profile", "user preferences", "what do you know about me"], cmd_user_prefs, priority=21)

    # ── VOICE EFFECT REFUTATION ──

    def cmd_refute_effect(turn):
        voice = core.get_subsystem("voice")
        if not voice:
            return "Voice system not available"
        text = turn.user_text.lower().strip()
        reason = ""
        if "because" in text:
            parts = text.split("because", 1)
            reason = parts[1].strip() if len(parts) > 1 else ""
        elif "refute" in text:
            parts = text.split("refute", 1)
            reason = parts[1].strip() if len(parts) > 1 else ""
        elif "cancel" in text:
            parts = text.split("cancel", 1)
            reason = parts[1].strip() if len(parts) > 1 else ""
        return voice.refute_effect(reason)

    def cmd_last_effect(turn):
        voice = core.get_subsystem("voice")
        if not voice:
            return "Voice system not available"
        effect = voice.get_last_effect()
        if effect:
            return f"Last effect: {effect}"
        return "No effect applied"

    def cmd_refuted_history(turn):
        voice = core.get_subsystem("voice")
        if not voice:
            return "Voice system not available"
        refuted = voice.get_refuted_effects()
        if not refuted:
            return "No refuted effects"
        lines = ["Refuted Effects:"]
        for r in refuted[-10:]:
            reason = f" - {r['reason']}" if r.get('reason') else ""
            lines.append(f"  {r['effect']}{reason}")
        return "\n".join(lines)

    def cmd_clear_effect(turn):
        voice = core.get_subsystem("voice")
        if not voice:
            return "Voice system not available"
        voice.clear_effect()
        return "Effect cleared"

    core.register_command(["refute effect", "cancel effect", "undo effect", "refute"], cmd_refute_effect, priority=30)
    core.register_command(["last effect", "current effect", "what effect"], cmd_last_effect, priority=29)
    core.register_command(["refuted effects", "effect history", "refuted history"], cmd_refuted_history, priority=28)
    core.register_command(["clear effect", "remove effect"], cmd_clear_effect, priority=27)


def setup_servers(core: UltraCore, config: Config):
    """Setup WebSocket and REST API servers (optional)."""
    try:
        net_config = getattr(config, 'network', None)
        if net_config and not getattr(net_config, 'enabled', True):
            return None, None

        ws_port = getattr(net_config, 'websocket_port', 8765) if net_config else 8765
        api_port = getattr(net_config, 'api_port', 8080) if net_config else 8080

        ws_server = WebSocketServer(port=ws_port)
        core.register_subsystem("websocket", ws_server)

        api_server = RESTServer(port=api_port)
        core.register_subsystem("api", api_server)

        api = api_server.router

        def api_health(req, resp):
            return resp.json({"status": "ok", "version": "2.0.0"})

        def api_status(req, resp):
            llm = core.get_subsystem("llm")
            status = llm.get_status() if llm else {"active_provider": "local", "model": "none"}
            return resp.json(status)

        def api_chat(req, resp):
            data = req.json()
            text = data.get("text", "")
            if not text:
                return resp.set_status(400).json({"error": "No text provided"})
            from purple_ultra.core.orchestrator import Turn
            turn = Turn(user_text=text)
            turn = core._process_turn(turn)
            return resp.json({"response": turn.response, "mood": turn.mood})

        def api_tools(req, resp):
            from purple_ultra.tools.registry import ToolRegistry
            tools = ToolRegistry.all()
            return resp.json({name: {"description": t.description, "dangerous": t.dangerous} for name, t in tools.items()})

        def api_memory(req, resp):
            memory = core.get_subsystem("memory")
            return resp.json({
                "recent": memory.recent_context(5),
                "learned": memory.get_learned()[:2000],
            })

        def api_mood(req, resp):
            mood = core.get_subsystem("mood")
            return resp.json({"mood": mood.current(), "history": mood.get_history()})

        api.get("/api/health", api_health)
        api.get("/api/status", api_status)
        api.post("/api/chat", api_chat)
        api.get("/api/tools", api_tools)
        api.get("/api/memory", api_memory)
        api.get("/api/mood", api_mood)

        return ws_server, api_server
    except Exception:
        return None, None


def main():
    parser = argparse.ArgumentParser(description="Purple Ultra AI - Advanced Voice Assistant")
    parser.add_argument("--voice", action="store_true", help="Run in voice-first mode")
    parser.add_argument("--server", action="store_true", help="Start WebSocket + REST API servers")
    parser.add_argument("--config", type=str, default="config.toml", help="Path to config file")
    parser.add_argument("--background", action="store_true", help="Run in background mode")
    parser.add_argument("--ws-port", type=int, default=8765, help="WebSocket server port")
    parser.add_argument("--api-port", type=int, default=8080, help="REST API server port")
    args = parser.parse_args()

    print(BANNER)

    config = load_config(Path(args.config))

    repair = SelfRepair()
    fix_results = repair.auto_fix_all()
    if fix_results["fixes"]:
        print(f"  Auto-fix: {len(fix_results['fixes'])} issues resolved")

    core = build_core(config)
    register_commands(core)

    llm = core.get_subsystem("llm")
    if llm and llm.health_check():
        print(f"  Brain: Connected ({llm.active_provider_name})")
    else:
        print("  Brain: Offline mode (no LLM available)")

    speaker = core.get_subsystem("speaker")
    print(f"  Speakers: {speaker.get_speaker_count()} registered")

    plugins = core.get_subsystem("plugins")
    plugin_count = len(plugins.list_plugins())
    if plugin_count > 0:
        print(f"  Plugins: {plugin_count} loaded")

    scheduler = core.get_subsystem("scheduler")
    task_count = len(scheduler.list_tasks())
    if task_count > 0:
        print(f"  Tasks: {task_count} scheduled")

    if args.server:
        ws_server, api_server = setup_servers(core, config)
        import threading
        ws_thread = threading.Thread(target=ws_server.start, kwargs={"background": True}, daemon=True)
        ws_thread.start()
        api_server.start(background=True)
        print(f"  WebSocket: ws://localhost:{args.ws_port}")
        print(f"  REST API: http://localhost:{args.api_port}")

    print()
    print("  Type 'help' for available commands")
    print()

    if args.voice:
        core.run_voice()
    else:
        core.run_interactive()


if __name__ == "__main__":
    main()
