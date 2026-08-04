"""Plugin system with hot-reloading and dynamic tool registration."""

from __future__ import annotations

import importlib
import importlib.util
import json
import time
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class PluginMeta:
    name: str
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    enabled: bool = True
    path: str = ""
    loaded_at: float = 0.0


class PluginBase:
    def __init__(self):
        self.name = ""
        self.version = "1.0.0"
        self._initialized = False

    def initialize(self, context: dict):
        self._initialized = True

    def shutdown(self):
        pass

    def get_tools(self) -> list[dict]:
        return []

    def get_commands(self) -> list[dict]:
        return []

    def get_hooks(self) -> dict[str, list[Callable]]:
        return {}


class PluginManager:
    def __init__(self, plugins_dir: str = "plugins"):
        self._plugins_dir = Path(plugins_dir)
        self._plugins_dir.mkdir(parents=True, exist_ok=True)
        self._plugins: dict[str, PluginBase] = {}
        self._meta: dict[str, PluginMeta] = {}
        self._watch_thread: threading.Thread | None = None
        self._watching = False
        self._file_mtimes: dict[str, float] = {}
        self._hooks: dict[str, list[Callable]] = {
            "before_command": [],
            "after_command": [],
            "before_turn": [],
            "after_turn": [],
            "on_message": [],
            "on_tool_call": [],
        }

    def load_plugin(self, plugin_path: Path) -> bool:
        try:
            spec = importlib.util.spec_from_file_location(
                f"purple_ultra.plugins.{plugin_path.stem}",
                str(plugin_path),
            )
            if not spec or not spec.loader:
                return False
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "Plugin"):
                plugin_class = module.Plugin
                if issubclass(plugin_class, PluginBase):
                    plugin = plugin_class()
                    meta = PluginMeta(
                        name=plugin.name or plugin_path.stem,
                        version=plugin.version,
                        path=str(plugin_path),
                        loaded_at=time.time(),
                    )
                    self._plugins[meta.name] = plugin
                    self._meta[meta.name] = meta
                    context = {"plugins": self, "tools": None, "memory": None, "brain": None}
                    plugin.initialize(context)
                    return True
        except Exception:
            pass
        return False

    def load_all(self):
        for py_file in self._plugins_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            self.load_plugin(py_file)
        for json_file in self._plugins_dir.glob("*.json"):
            try:
                manifest = json.loads(json_file.read_text())
                plugin_path = Path(json_file.parent) / manifest.get("entry", f"{json_file.stem}.py")
                if plugin_path.exists():
                    self.load_plugin(plugin_path)
            except Exception:
                pass

    def unload_plugin(self, name: str) -> bool:
        if name in self._plugins:
            try:
                self._plugins[name].shutdown()
            except Exception:
                pass
            del self._plugins[name]
            if name in self._meta:
                del self._meta[name]
            return True
        return False

    def reload_plugin(self, name: str) -> bool:
        if name in self._meta:
            path = Path(self._meta[name].path)
            self.unload_plugin(name)
            return self.load_plugin(path)
        return False

    def register_hook(self, hook_name: str, callback: Callable):
        if hook_name in self._hooks:
            self._hooks[hook_name].append(callback)

    def trigger_hook(self, hook_name: str, *args, **kwargs):
        for callback in self._hooks.get(hook_name, []):
            try:
                callback(*args, **kwargs)
            except Exception:
                pass

    def get_plugin(self, name: str) -> PluginBase | None:
        return self._plugins.get(name)

    def list_plugins(self) -> list[dict]:
        return [
            {
                "name": meta.name,
                "version": meta.version,
                "author": meta.author,
                "description": meta.description,
                "enabled": meta.enabled,
                "loaded_at": meta.loaded_at,
            }
            for meta in self._meta.values()
        ]

    def get_all_tools(self) -> list[dict]:
        tools = []
        for plugin in self._plugins.values():
            try:
                tools.extend(plugin.get_tools())
            except Exception:
                pass
        return tools

    def start_watcher(self):
        self._watching = True
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._watch_thread.start()

    def stop_watcher(self):
        self._watching = False

    def _watch_loop(self):
        while self._watching:
            for py_file in self._plugins_dir.glob("*.py"):
                mtime = py_file.stat().st_mtime
                path_str = str(py_file)
                if path_str in self._file_mtimes:
                    if mtime > self._file_mtimes[path_str]:
                        for name, meta in self._meta.items():
                            if meta.path == path_str:
                                self.reload_plugin(name)
                                break
                self._file_mtimes[path_str] = mtime
            time.sleep(2)

    def create_plugin_template(self, name: str) -> str:
        template = f'''"""Plugin: {name}"""

from purple_ultra.utils.plugins import PluginBase


class Plugin(PluginBase):
    def __init__(self):
        super().__init__()
        self.name = "{name}"
        self.version = "1.0.0"

    def initialize(self, context):
        super().initialize(context)
        # Plugin initialization code here
        pass

    def shutdown(self):
        # Plugin cleanup code here
        pass

    def get_tools(self):
        return [
            {{
                "name": "my_tool",
                "description": "My custom tool",
                "params": {{"input": "string"}},
                "handler": self._my_tool,
            }}
        ]

    def _my_tool(self, input: str = "") -> str:
        return f"Processed: {{input}}"
'''
        plugin_path = self._plugins_dir / f"{name}.py"
        plugin_path.write_text(template)
        return str(plugin_path)

    def get_status(self) -> dict:
        return {
            "total_plugins": len(self._plugins),
            "plugins": self.list_plugins(),
            "watching": self._watching,
        }
