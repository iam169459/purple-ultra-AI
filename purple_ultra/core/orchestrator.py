"""Core orchestrator - the central event loop of Purple Ultra AI."""

from __future__ import annotations

import signal
import sys
import time
import threading
from dataclasses import dataclass, field
from typing import Any, Callable

from ..config.settings import Config


@dataclass
class Turn:
    """Represents a single interaction turn."""
    user_text: str
    speaker: str = "guest"
    voiceprint: list[float] = field(default_factory=list)
    mood: str = "neutral"
    emotion: str = "neutral"
    context: str = ""
    decision: Any = None
    tool_results: list[dict] = field(default_factory=list)
    response: str = ""
    timestamp: float = field(default_factory=time.time)
    is_admin: bool = False  # True if speaker is super admin
    admin_priority: bool = False  # True if admin commands should be obeyed immediately


class UltraCore:
    """Main orchestrator that ties all subsystems together."""

    __slots__ = ('config', '_running', '_shutdown_event', '_subsystems',
                 '_command_handlers', '_command_patterns', '_before_turn',
                 '_after_turn', '_turn_count')

    def __init__(self, config: Config):
        self.config = config
        self._running = False
        self._shutdown_event = threading.Event()
        self._subsystems: dict[str, Any] = {}
        self._command_handlers: dict[str, Callable] = {}
        self._command_patterns: list[str] = []  # sorted by length desc for best match
        self._before_turn: list[Callable] = []
        self._after_turn: list[Callable] = []
        self._turn_count = 0

    def register_subsystem(self, name: str, subsystem: Any):
        self._subsystems[name] = subsystem

    def get_subsystem(self, name: str) -> Any:
        return self._subsystems.get(name)

    def register_command(self, patterns: list[str], handler: Callable, priority: int = 50):
        for pattern in patterns:
            self._command_handlers[pattern] = (handler, priority)
        self._command_patterns = sorted(
            self._command_handlers.keys(),
            key=lambda p: (-self._command_handlers[p][1], -len(p))
        )

    def add_before_turn_hook(self, hook: Callable):
        self._before_turn.append(hook)

    def add_after_turn_hook(self, hook: Callable):
        self._after_turn.append(hook)

    def _match_command(self, text: str) -> tuple[Callable | None, str]:
        text_lower = text.lower().strip()
        # Use pre-sorted patterns (by priority desc, length desc)
        for pattern in self._command_patterns:
            if pattern in text_lower:
                handler, priority = self._command_handlers[pattern]
                return handler, pattern
        return None, ""

    def _build_context(self, turn: Turn) -> str:
        parts = []
        memory = self.get_subsystem("memory")
        if memory:
            recent = memory.recent_context(count=12)
            if recent:
                parts.append(f"Recent conversation:\n{recent}")
        personality = self.get_subsystem("personality")
        if personality:
            p = personality.get_prompt_text()
            if p:
                parts.append(f"Personality:\n{p[:4000]}")
        learned = memory.get_learned() if memory else ""
        if learned:
            parts.append(f"Learned lessons:\n{learned[:3000]}")
        notes = memory.get_notes() if memory else ""
        if notes:
            parts.append(f"User notes:\n{notes[:2000]}")
        return "\n\n".join(parts)

    def _process_turn(self, turn: Turn) -> Turn:
        for hook in self._before_turn:
            try:
                hook(turn)
            except Exception:
                pass

        turn.context = self._build_context(turn)

        # Admin commands get highest priority - always obey
        if turn.is_admin:
            # Check for admin-specific commands first
            admin_result = self._handle_admin_command(turn)
            if admin_result:
                turn.response = admin_result
                turn.tool_results.append({"tool": "admin_command", "result": admin_result})
            else:
                # Admin non-admin commands: still obey but with priority
                handler, pattern = self._match_command(turn.user_text)
                if handler:
                    try:
                        result = handler(turn)
                        turn.response = str(result) if result else ""
                        turn.tool_results.append({"tool": "command", "pattern": pattern, "result": turn.response})
                    except Exception as e:
                        turn.response = f"Command error: {e}"
                else:
                    brain = self.get_subsystem("brain")
                    if brain:
                        decision = brain.decide_admin(turn.user_text, turn.context, turn.mood)
                        turn.decision = decision
                        turn.response = decision.say
                        turn.mood = decision.mood

                        mood_sys = self.get_subsystem("mood")
                        if mood_sys:
                            mood_sys.set(decision.mood)

                        # Admin: skip dangerous action confirmation
                        if decision.actions:
                            tool_runner = self.get_subsystem("tools")
                            if tool_runner:
                                max_actions = self.config.tools.max_actions_per_turn
                                for action in decision.actions[:max_actions]:
                                    result = tool_runner.run(action)
                                    turn.tool_results.append({"tool": action.get("name"), "result": result})
        else:
            # Normal user flow
            handler, pattern = self._match_command(turn.user_text)
            if handler:
                try:
                    result = handler(turn)
                    turn.response = str(result) if result else ""
                    turn.tool_results.append({"tool": "command", "pattern": pattern, "result": turn.response})
                except Exception as e:
                    turn.response = f"Command error: {e}"
            else:
                brain = self.get_subsystem("brain")
                if brain:
                    decision = brain.decide(turn.user_text, turn.context, turn.mood)
                    turn.decision = decision
                    turn.response = decision.say
                    turn.mood = decision.mood

                    mood_sys = self.get_subsystem("mood")
                    if mood_sys:
                        mood_sys.set(decision.mood)

                    if decision.actions:
                        tool_runner = self.get_subsystem("tools")
                        if tool_runner:
                            max_actions = self.config.tools.max_actions_per_turn
                            for action in decision.actions[:max_actions]:
                                if tool_runner.is_dangerous(action):
                                    voice = self.get_subsystem("voice")
                                    if voice:
                                        voice.speak(f"This action requires confirmation. Do you want to {action.get('name', 'proceed')}?")
                                        confirmation = voice.listen()
                                        if not confirmation or not any(w in confirmation.text.lower() for w in ("yes", "confirm", "go", "do it")):
                                            turn.tool_results.append({"tool": action.get("name"), "result": "cancelled"})
                                            continue
                                result = tool_runner.run(action)
                                turn.tool_results.append({"tool": action.get("name"), "result": result})

        for hook in self._after_turn:
            try:
                hook(turn)
            except Exception:
                pass

        return turn

    def _handle_admin_command(self, turn: Turn) -> str | None:
        """Handle special admin-only commands."""
        text = turn.user_text.lower().strip()
        
        # Admin system commands
        if text in ("admin shutdown", "shut down", "power off"):
            self._speak("Shutting down as per admin command.")
            self.shutdown()
            return "System shutting down."
        
        if text in ("admin restart", "restart system"):
            self._speak("Restarting as per admin command.")
            self.shutdown()
            return "System restarting."
        
        if text in ("admin status", "system status"):
            return self._get_full_status()
        
        if text in ("admin override on", "enable override"):
            voice = self.get_subsystem("voice")
            if voice:
                voice.set_admin_override(True)
            return "Admin override enabled."
        
        if text in ("admin override off", "disable override"):
            voice = self.get_subsystem("voice")
            if voice:
                voice.set_admin_override(False)
            return "Admin override disabled."
        
        if text in ("admin unlock", "unlock all"):
            return "All restrictions lifted for admin session."
        
        if text.startswith("admin speak "):
            msg = text[12:].strip()
            voice = self.get_subsystem("voice")
            if voice and msg:
                voice.speak_admin(msg)
            return f"Admin: {msg}"
        
        return None

    def _get_full_status(self) -> str:
        """Get full system status for admin."""
        lines = ["=== Purple Ultra AI - Admin Status ==="]
        
        # Brain status
        brain = self.get_subsystem("brain")
        if brain and hasattr(brain, 'purple_brain'):
            pb = brain.purple_brain
            lines.append(f"Brain: {pb.consciousness.get('total_thoughts', 0)} thoughts, "
                        f"{pb.consciousness.get('total_decisions', 0)} decisions")
        
        # Voice status
        voice = self.get_subsystem("voice")
        if voice:
            admin_status = voice.get_admin_status()
            lines.append(f"Voice: Admin={admin_status['admin_name']}, Override={admin_status.get('current_mood', 'neutral')}")
        
        # Speaker status
        speaker_rec = self.get_subsystem("speaker")
        if speaker_rec:
            admin_profile = speaker_rec.get_admin_profile()
            lines.append(f"Speaker: Admin ID={admin_profile['id']}, Removable={admin_profile['removable']}")
        
        # Turn count
        lines.append(f"Turns: {self._turn_count}")
        
        return "\n".join(lines)

    def _speak(self, text: str, mood: str = None):
        voice = self.get_subsystem("voice")
        if voice:
            voice.speak(text, mood=mood)

    def run_interactive(self):
        """Run in interactive text mode."""
        self._running = True
        self._setup_signal_handlers()

        print(f"\n{'='*60}")
        print(f"  Purple Ultra AI v{self.config.assistant.version}")
        print(f"  Type 'quit' or 'exit' to stop")
        print(f"{'='*60}\n")

        memory = self.get_subsystem("memory")
        mood_sys = self.get_subsystem("mood")
        current_mood = mood_sys.current() if mood_sys else "neutral"

        while self._running:
            try:
                user_input = input(f"[{current_mood}] You: ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "stop", "goodbye"):
                    self._speak("Goodbye! See you next time.")
                    break

                turn = Turn(user_text=user_input, mood=current_mood)
                turn = self._process_turn(turn)

                if turn.response:
                    print(f"  {turn.response}")
                    voice = self.get_subsystem("voice")
                    if voice:
                        voice.speak(turn.response, mood=turn.mood)

                current_mood = turn.mood
                self._turn_count += 1

                if memory:
                    memory.add_history(
                        user_text=turn.user_text,
                        assistant_text=turn.response,
                        mood=turn.mood,
                        actions=turn.tool_results,
                    )

            except KeyboardInterrupt:
                break
            except EOFError:
                break

        self.shutdown()

    def run_voice(self):
        """Run in voice-first mode."""
        self._running = True
        self._setup_signal_handlers()

        voice = self.get_subsystem("voice")
        if not voice:
            print("Voice subsystem not available. Falling back to interactive mode.")
            self.run_interactive()
            return

        print(f"\n{'='*60}")
        print(f"  Purple Ultra AI v{self.config.assistant.version} - Voice Mode")
        print(f"  Say 'quit' or 'exit' to stop")
        print(f"{'='*60}\n")

        memory = self.get_subsystem("memory")
        mood_sys = self.get_subsystem("mood")
        current_mood = mood_sys.current() if mood_sys else "neutral"

        self._speak(f"Hello! I'm {self.config.assistant.name}. How can I help you?")

        while self._running:
            try:
                heard = voice.listen()
                if not heard or not heard.text.strip():
                    continue

                text = heard.text.strip()
                if text.lower() in ("quit", "exit", "stop assistant", "goodbye"):
                    self._speak("Goodbye! See you next time.")
                    break

                # Identify speaker and check for admin
                speaker_rec = self.get_subsystem("speaker")
                speaker = "guest"
                is_admin = False
                if speaker_rec and heard.voiceprint:
                    speaker = speaker_rec.identify(heard.voiceprint)
                    is_admin = speaker_rec.is_admin(speaker)

                turn = Turn(
                    user_text=text,
                    speaker=speaker,
                    voiceprint=heard.voiceprint,
                    mood=current_mood,
                    is_admin=is_admin,
                    admin_priority=is_admin,  # Admin commands get priority
                )
                turn = self._process_turn(turn)

                if turn.response:
                    self._speak(turn.response, mood=turn.mood)

                current_mood = turn.mood
                self._turn_count += 1

                if memory:
                    memory.add_history(
                        user_text=turn.user_text,
                        assistant_text=turn.response,
                        mood=turn.mood,
                        actions=turn.tool_results,
                        speaker=turn.speaker,
                    )

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(1)

        self.shutdown()

    def _setup_signal_handlers(self):
        def handler(signum, frame):
            self.shutdown()
            sys.exit(0)
        signal.signal(signal.SIGINT, handler)
        signal.signal(signal.SIGTERM, handler)

    def shutdown(self):
        self._running = False
        self._shutdown_event.set()
        memory = self.get_subsystem("memory")
        if memory:
            memory.save()
        print(f"\nSession ended. {self._turn_count} interactions processed.")
