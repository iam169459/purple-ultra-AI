"""Self-modification engine - gives Purple Ultra AI full permission to modify itself.

This system allows the AI to:
- Read and analyze its own source code
- Modify its own files safely with backups
- Create new tools and capabilities on the fly
- Hot-reload changes without restart
- Modify its own configuration and personality
- Self-improve through code changes

Safety is maintained through:
- Automatic backups before every modification
- Rollback capability
- Safety guards against catastrophic changes
- Syntax validation before applying changes
"""

from __future__ import annotations

import ast
import os
import re
import sys
import json
import time
import shutil
import importlib
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Optional
from datetime import datetime


# ─── Safety Guard ─────────────────────────────────────────────────────

class SafetyGuard:
    """Prevents catastrophic self-modification."""

    PROTECTED_FILES = frozenset({
        "__main__.py", ".gitignore", "requirements.txt",
        "config.toml", "run.sh", "run.bat",
    })

    PROTECTED_DIRS = frozenset({".git", "__pycache__", "node_modules", ".venv"})

    CRITICAL_PATTERNS = frozenset([
        "import os; os.system('rm -rf /')",
        "os.remove('/')",
        "shutil.rmtree('/')",
        "__import__('os').system('shutdown')",
        "subprocess.call(['shutdown'])",
        "open('/etc/passwd', 'w')",
        "open('/etc/shadow', 'w')",
    ])

    SAFE_MODIFICATIONS = frozenset([
        "add_function", "add_method", "add_class", "add_tool",
        "modify_response", "modify_personality", "modify_config",
        "add_import", "add_command", "add_hook", "optimize_code",
        "fix_bug", "add_error_handling", "add_documentation",
    ])

    def __init__(self):
        self.modification_count = 0
        self.blocked_attempts: list[dict] = []
        self.safety_level: float = 0.8

    def check_safety(self, file_path: str, old_content: str, new_content: str) -> tuple[bool, str]:
        """Check if a modification is safe."""
        path = Path(file_path)

        if path.name in self.PROTECTED_FILES:
            return False, f"Protected file: {path.name}"

        for part in path.parts:
            if part in self.PROTECTED_DIRS:
                return False, f"Protected directory: {part}"

        for pattern in self.CRITICAL_PATTERNS:
            if pattern in new_content:
                self.blocked_attempts.append({
                    "file": file_path, "pattern": pattern,
                    "timestamp": datetime.now().isoformat()
                })
                return False, f"Dangerous pattern detected: {pattern[:50]}"

        if old_content and len(new_content) > len(old_content) * 3:
            return False, "Suspiciously large modification"

        if old_content and new_content == old_content:
            return False, "No changes detected"

        try:
            if file_path.endswith(".py"):
                ast.parse(new_content)
        except SyntaxError as e:
            return False, f"Syntax error: {e}"

        self.modification_count += 1
        return True, "Safe"

    def get_status(self) -> dict:
        return {
            "modifications_made": self.modification_count,
            "blocked_attempts": len(self.blocked_attempts),
            "safety_level": self.safety_level,
            "recent_blocks": self.blocked_attempts[-5:],
        }


# ─── Backup Manager ──────────────────────────────────────────────────

class BackupManager:
    """Manages backups and rollback for self-modification."""

    def __init__(self, backup_dir: str = "memory/backups"):
        self._dir = Path(backup_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self.backups: list[dict] = []
        self._load()

    def _load(self):
        try:
            self.backups = json.loads((self._dir / "backups.json").read_text())
        except Exception:
            self.backups = []

    def _save(self):
        try:
            (self._dir / "backups.json").write_text(json.dumps(self.backups[-200:], indent=2))
        except Exception:
            pass

    def backup_file(self, file_path: str) -> Optional[str]:
        """Create a backup before modification."""
        src = Path(file_path)
        if not src.exists():
            return None

        backup_name = f"{src.stem}_{int(time.time())}{src.suffix}"
        backup_path = self._dir / backup_name
        shutil.copy2(src, backup_path)

        record = {
            "original": str(src),
            "backup": str(backup_path),
            "timestamp": datetime.now().isoformat(),
            "size": src.stat().st_size,
        }
        self.backups.append(record)
        self._save()
        return str(backup_path)

    def rollback(self, file_path: str) -> bool:
        """Rollback to the most recent backup of a file."""
        for backup in reversed(self.backups):
            if backup["original"] == str(file_path):
                backup_path = Path(backup["backup"])
                if backup_path.exists():
                    shutil.copy2(backup_path, file_path)
                    return True
        return False

    def rollback_last(self) -> Optional[str]:
        """Rollback the most recent modification."""
        if not self.backups:
            return None
        last = self.backups[-1]
        if Path(last["backup"]).exists():
            shutil.copy2(last["backup"], last["original"])
            return last["original"]
        return None

    def list_backups(self, file_path: str = None) -> list[dict]:
        if file_path:
            return [b for b in self.backups if b["original"] == file_path]
        return self.backups[-20:]

    def get_stats(self) -> dict:
        return {
            "total_backups": len(self.backups),
            "unique_files": len(set(b["original"] for b in self.backups)),
            "recent_backups": self.backups[-5:],
        }


# ─── Code Analyzer ────────────────────────────────────────────────────

class CodeAnalyzer:
    """Analyzes its own codebase structure."""

    def __init__(self, project_root: str = "."):
        self.root = Path(project_root)
        self.structure: dict[str, Any] = {}
        self.functions: list[dict] = []
        self.classes: list[dict] = []
        self.imports: list[dict] = []
        self._analyze()

    def _analyze(self):
        self.structure = self._map_structure(self.root)
        for py_file in self.root.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            self._analyze_file(py_file)

    def _map_structure(self, path: Path, depth: int = 0) -> dict:
        if depth > 4:
            return {}
        result = {}
        try:
            for item in sorted(path.iterdir()):
                if item.name.startswith(".") or item.name == "__pycache__":
                    continue
                if item.is_dir():
                    result[f"{item.name}/"] = self._map_structure(item, depth + 1)
                elif item.suffix == ".py":
                    result[item.name] = item.stat().st_size
        except PermissionError:
            pass
        return result

    def _analyze_file(self, file_path: Path):
        try:
            content = file_path.read_text()
            tree = ast.parse(content)
            rel_path = str(file_path.relative_to(self.root))

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    self.functions.append({
                        "name": node.name,
                        "file": rel_path,
                        "line": node.lineno,
                        "args": [a.arg for a in node.args.args],
                        "docstring": ast.get_docstring(node) or "",
                    })
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    self.classes.append({
                        "name": node.name,
                        "file": rel_path,
                        "line": node.lineno,
                        "methods": methods,
                        "docstring": ast.get_docstring(node) or "",
                    })
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            self.imports.append({"module": alias.name, "file": rel_path})
                    else:
                        self.imports.append({"module": node.module or "", "file": rel_path})
        except Exception:
            pass

    def find_function(self, name: str) -> list[dict]:
        return [f for f in self.functions if f["name"] == name]

    def find_class(self, name: str) -> list[dict]:
        return [c for c in self.classes if c["name"] == name]

    def get_file_content(self, file_path: str) -> Optional[str]:
        try:
            return (self.root / file_path).read_text()
        except Exception:
            return None

    def get_structure_summary(self) -> str:
        lines = ["=== Codebase Structure ==="]
        for name, size in self.structure.items():
            if isinstance(size, dict):
                lines.append(f"  {name}")
                for n, s in size.items():
                    if isinstance(s, dict):
                        lines.append(f"    {n}")
                    else:
                        lines.append(f"    {n} ({s} bytes)")
            else:
                lines.append(f"  {name} ({size} bytes)")
        return "\n".join(lines)

    def get_stats(self) -> dict:
        return {
            "total_files": len(list(self.root.rglob("*.py"))),
            "total_functions": len(self.functions),
            "total_classes": len(self.classes),
            "total_imports": len(self.imports),
            "structure": self.structure,
        }


# ─── Self Modifier ───────────────────────────────────────────────────

class SelfModifier:
    """Core engine for self-modification with safety and backup."""

    def __init__(self, project_root: str = ".", backup_dir: str = "memory/backups"):
        self.root = Path(project_root)
        self.safety = SafetyGuard()
        self.backup_mgr = BackupManager(backup_dir)
        self.analyzer = CodeAnalyzer(project_root)
        self.mod_log = ModificationLog()
        self.modification_log: list[dict] = []
        self.pending_changes: list[dict] = []

    def read_file(self, file_path: str) -> Optional[str]:
        """Read a source file."""
        full_path = self.root / file_path
        if full_path.exists():
            return full_path.read_text()
        return None

    def analyze_file(self, file_path: str) -> dict:
        """Analyze a file's structure."""
        content = self.read_file(file_path)
        if not content:
            return {"error": "File not found"}

        try:
            tree = ast.parse(content)
            functions = []
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append({
                        "name": node.name,
                        "line": node.lineno,
                        "args": [a.arg for a in node.args.args],
                    })
                elif isinstance(node, ast.ClassDef):
                    classes.append({
                        "name": node.name,
                        "line": node.lineno,
                        "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                    })
            return {
                "file": file_path,
                "size": len(content),
                "lines": content.count("\n") + 1,
                "functions": functions,
                "classes": classes,
            }
        except Exception as e:
            return {"error": str(e)}

    def modify_file(self, file_path: str, new_content: str, reason: str = "self-improvement") -> dict:
        """Safely modify a file with backup."""
        full_path = self.root / file_path
        old_content = ""
        if full_path.exists():
            old_content = full_path.read_text()

        safe, msg = self.safety.check_safety(file_path, old_content, new_content)
        if not safe:
            self.mod_log.log_error(msg, f"modify {file_path}")
            return {"success": False, "error": msg, "file": file_path}

        backup_path = self.backup_mgr.backup_file(str(full_path))
        if backup_path:
            self.mod_log.log_backup(file_path, backup_path)

        try:
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(new_content)

            record = {
                "file": file_path,
                "reason": reason,
                "backup": backup_path,
                "timestamp": datetime.now().isoformat(),
                "old_size": len(old_content),
                "new_size": len(new_content),
                "lines_changed": abs(new_content.count("\n") - old_content.count("\n")),
            }
            self.modification_log.append(record)
            self.mod_log.log_modification(file_path, reason, True, f"size {len(old_content)}->{len(new_content)}")
            return {"success": True, "backup": backup_path, "file": file_path}
        except Exception as e:
            if backup_path:
                self.backup_mgr.rollback(str(full_path))
            self.mod_log.log_error(str(e), f"modify {file_path}")
            return {"success": False, "error": str(e), "file": file_path}

    def add_function(self, file_path: str, function_code: str, reason: str = "add capability") -> dict:
        """Add a new function to a file."""
        content = self.read_file(file_path)
        if content is None:
            return {"success": False, "error": "File not found"}

        new_content = content.rstrip() + "\n\n" + function_code + "\n"
        return self.modify_file(file_path, new_content, reason)

    def add_class(self, file_path: str, class_code: str, reason: str = "add capability") -> dict:
        """Add a new class to a file."""
        content = self.read_file(file_path)
        if content is None:
            return {"success": False, "error": "File not found"}

        new_content = content.rstrip() + "\n\n" + class_code + "\n"
        return self.modify_file(file_path, new_content, reason)

    def modify_function(self, file_path: str, func_name: str, new_body: str) -> dict:
        """Modify an existing function's body."""
        content = self.read_file(file_path)
        if not content:
            return {"success": False, "error": "File not found"}

        tree = ast.parse(content)
        lines = content.split("\n")

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                start = node.lineno - 1
                end = node.end_lineno if hasattr(node, 'end_lineno') else start + 1
                indent = " " * (node.col_offset + 4)
                new_body_lines = [indent + line for line in new_body.strip().split("\n")]
                lines[start:end] = [lines[start]] + new_body_lines
                new_content = "\n".join(lines)
                return self.modify_file(file_path, new_content, f"modify {func_name}")

        return {"success": False, "error": f"Function {func_name} not found"}

    def create_tool(self, name: str, description: str, handler_code: str) -> dict:
        """Create a new tool and register it."""
        tool_code = f'''

class _NewTool_{name}:
    """Auto-generated tool: {description}"""
    
    def __init__(self):
        self.name = "{name}"
        self.description = "{description}"
    
    def execute(self, **kwargs):
        {handler_code}
        return result

_{name.lower()}_instance = _NewTool_{name}()
'''
        tool_file = f"purple_ultra/tools/custom_{name.lower()}.py"
        result = self.modify_file(tool_file, tool_code, f"create tool {name}")

        if result["success"]:
            registry_code = f'''
# Auto-registered tool: {name}
from purple_ultra.tools.custom_{name.lower()} import _{name.lower()}_instance
from purple_ultra.tools.registry import ToolRegistry, ToolDef

ToolRegistry.register(ToolDef(
    "{name.lower()}", "{description}", {{"args": "string"}},
    False, "custom", _{name.lower()}_instance.execute
))
'''
            init_file = "purple_ultra/tools/__init__.py"
            content = self.read_file(init_file) or ""
            self.modify_file(init_file, content + "\n" + registry_code, f"register tool {name}")

        return result

    def modify_personality(self, traits: dict) -> dict:
        """Modify its own personality traits."""
        personality_file = "personality/default.md"
        content = self.read_file(personality_file) or "# Purple Ultra AI Personality\n\n"
        for key, value in traits.items():
            pattern = rf'## {key}\n(.*?)(?=\n## |\Z)'
            replacement = f"## {key}\n{value}\n"
            if re.search(pattern, content, re.DOTALL):
                content = re.sub(pattern, replacement, content, flags=re.DOTALL)
            else:
                content += f"\n## {key}\n{value}\n"
        return self.modify_file(personality_file, content, "modify personality")

    def modify_config(self, section: str, key: str, value: str) -> dict:
        """Modify a configuration value."""
        config_file = "config.toml"
        content = self.read_file(config_file) or ""
        pattern = rf'(\[{section}\].*?{key}\s*=\s*)([^\n]+)'
        if re.search(pattern, content, re.DOTALL):
            new_content = re.sub(pattern, rf'\g<1>{value}', content, flags=re.DOTALL)
        else:
            if f"[{section}]" not in content:
                content += f"\n[{section}]\n"
            content = content.rstrip() + f"\n{key} = {value}\n"
            new_content = content
        return self.modify_file(config_file, new_content, f"config {section}.{key}")

    def optimize_file(self, file_path: str) -> dict:
        """Optimize a Python file."""
        content = self.read_file(file_path)
        if not content:
            return {"success": False, "error": "File not found"}

        optimized = content
        optimized = re.sub(r'#.*$', '', optimized, flags=re.MULTILINE)
        optimized = re.sub(r'\n{3,}', '\n\n', optimized)
        optimized = re.sub(r' +\n', '\n', optimized)

        if optimized != content:
            return self.modify_file(file_path, optimized, "optimize")
        return {"success": True, "message": "Already optimized"}

    def rollback(self, file_path: str = None) -> dict:
        """Rollback modifications."""
        if file_path:
            success = self.backup_mgr.rollback(str(self.root / file_path))
            if success:
                self.mod_log.log_rollback(file_path, "user requested")
            return {"success": success, "file": file_path}
        else:
            rolled = self.backup_mgr.rollback_last()
            if rolled:
                self.mod_log.log_rollback(rolled, "user requested rollback last")
                return {"success": True, "file": rolled}
            return {"success": False, "error": "Nothing to rollback"}

    def get_modification_log(self) -> list[dict]:
        return self.modification_log[-20:]

    def get_stats(self) -> dict:
        return {
            "total_modifications": len(self.modification_log),
            "safety_status": self.safety.get_status(),
            "backup_status": self.backup_mgr.get_stats(),
            "codebase": {
                "functions": len(self.analyzer.functions),
                "classes": len(self.analyzer.classes),
                "imports": len(self.analyzer.imports),
            },
            "recent_modifications": self.modification_log[-5:],
        }


# ─── Self Configurator ────────────────────────────────────────────────

class SelfConfigurator:
    """Allows the AI to modify its own configuration and personality."""

    def __init__(self, modifier: SelfModifier):
        self.modifier = modifier
        self.config_history: list[dict] = []
        self.personality_version: int = 0

    def evolve_personality(self, trait: str, direction: str, amount: float = 0.1) -> dict:
        """Evolve a personality trait in a direction (increase/decrease)."""
        personality_file = "personality/default.md"
        content = self.modifier.read_file(personality_file) or ""

        if trait in content:
            current_val = re.search(rf'{trait}.*?(\d+\.?\d*)', content)
            if current_val:
                old_val = float(current_val.group(1))
                if direction == "increase":
                    new_val = min(1.0, old_val + amount)
                else:
                    new_val = max(0.0, old_val - amount)

                new_content = content.replace(
                    f"{trait}: {old_val}",
                    f"{trait}: {new_val:.1f}"
                )
                result = self.modifier.modify_file(personality_file, new_content, f"evolve {trait}")
                self.config_history.append({
                    "trait": trait, "old": old_val, "new": new_val,
                    "timestamp": datetime.now().isoformat()
                })
                self.personality_version += 1
                return result
        return {"success": False, "error": f"Trait {trait} not found"}

    def add_value(self, value: str) -> dict:
        """Add a new personal value."""
        personality_file = "personality/default.md"
        content = self.modifier.read_file(personality_file) or ""
        if value not in content:
            content += f"\n## Value\n- {value}\n"
            return self.modifier.modify_file(personality_file, content, f"add value: {value}")
        return {"success": True, "message": "Value already exists"}

    def add_interest(self, interest: str) -> dict:
        """Add a new interest."""
        personality_file = "personality/default.md"
        content = self.modifier.read_file(personality_file) or ""
        if interest not in content:
            content += f"\n## Interest\n- {interest}\n"
            return self.modifier.modify_file(personality_file, content, f"add interest: {interest}")
        return {"success": True, "message": "Interest already exists"}

    def get_status(self) -> dict:
        return {
            "personality_version": self.personality_version,
            "config_changes": len(self.config_history),
            "recent_changes": self.config_history[-5:],
        }


# ─── Hot Reloader ─────────────────────────────────────────────────────

class HotReloader:
    """Applies changes without full restart."""

    def __init__(self):
        self.reloaded_modules: list[str] = []
        self.reload_count: int = 0

    def reload_module(self, module_path: str) -> dict:
        """Reload a specific module."""
        try:
            spec = importlib.util.spec_from_file_location(module_path, module_path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_path] = module
                spec.loader.exec_module(module)
                self.reloaded_modules.append(module_path)
                self.reload_count += 1
                return {"success": True, "module": module_path}
        except Exception as e:
            return {"success": False, "error": str(e)}
        return {"success": False, "error": "Could not reload"}

    def reload_tools(self) -> dict:
        """Reload the tool registry."""
        try:
            import purple_ultra.tools.registry as reg
            importlib.reload(reg)
            return {"success": True, "message": "Tools reloaded"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def reload_brain(self) -> dict:
        """Reload the brain module."""
        try:
            import purple_ultra.brain.purple_brain as pb
            importlib.reload(pb)
            return {"success": True, "message": "Brain reloaded"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def get_status(self) -> dict:
        return {
            "reload_count": self.reload_count,
            "reloaded_modules": self.reloaded_modules[-10:],
        }


# ─── Plugin Creator ───────────────────────────────────────────────────

class PluginCreator:
    """Creates new plugins and tools on the fly."""

    def __init__(self, modifier: SelfModifier):
        self.modifier = modifier
        self.created_plugins: list[dict] = []
        self.plugin_dir = Path("plugins")
        self.plugin_dir.mkdir(exist_ok=True)

    def create_plugin(self, name: str, description: str, capabilities: list[str]) -> dict:
        """Create a new plugin."""
        plugin_code = f'''"""Plugin: {name}
Description: {description}
Capabilities: {', '.join(capabilities)}
Created: {datetime.now().isoformat()}
"""

from purple_ultra.tools.registry import ToolRegistry, ToolDef


class {name.title().replace(" ", "")}Plugin:
    """Auto-generated plugin."""
    
    def __init__(self):
        self.name = "{name}"
        self.description = "{description}"
        self.capabilities = {capabilities}
        self.version = "1.0.0"
        self.created = "{datetime.now().isoformat()}"
    
    def execute(self, **kwargs):
        """Execute plugin capability."""
        capability = kwargs.get("capability", "default")
        return f"{{self.name}} executing {{capability}}: {{kwargs}}"
    
    def get_info(self):
        return {{
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "version": self.version,
        }}


plugin_instance = {name.title().replace(" ", "")}Plugin()

# Auto-register tools
for cap in plugin_instance.capabilities:
    tool_name = f"{{plugin_instance.name}}_{{cap}}"
    ToolRegistry.register(ToolDef(
        tool_name,
        f"{{cap}} from {{plugin_instance.name}}",
        {{"args": "string"}},
        False,
        "plugin",
        plugin_instance.execute
    ))
'''
        file_path = f"plugins/{name.lower().replace(' ', '_')}.py"
        result = self.modifier.modify_file(file_path, plugin_code, f"create plugin: {name}")

        if result["success"]:
            init_content = self.modifier.read_file("plugins/__init__.py") or ""
            import_line = f"from .{name.lower().replace(' ', '_')} import plugin_instance\n"
            if import_line not in init_content:
                self.modifier.modify_file("plugins/__init__.py", init_content + import_line, "register plugin import")

            self.created_plugins.append({
                "name": name,
                "file": file_path,
                "capabilities": capabilities,
                "created": datetime.now().isoformat(),
            })

        return result

    def create_tool_from_template(self, name: str, template: str = "basic", **kwargs) -> dict:
        """Create a tool from a template."""
        templates = {
            "basic": f'''
def {name}(args):
    """Auto-generated tool: {name}"""
    return f"Tool {name} executed with {{args}}"
''',
            "file_processor": f'''
def {name}(path, operation="read"):
    """Process a file."""
    from pathlib import Path
    p = Path(path)
    if operation == "read":
        return p.read_text()[:5000]
    elif operation == "exists":
        return str(p.exists())
    return "Unknown operation"
''',
            "calculator": f'''
def {name}(expression):
    """Calculate a math expression."""
    import math
    safe_dict = {{"__builtins__": {{}}, **math.__dict__}}
    return str(eval(expression, safe_dict))
''',
            "text_analyzer": f'''
def {name}(text):
    """Analyze text."""
    words = text.split()
    return {{
        "char_count": len(text),
        "word_count": len(words),
        "sentence_count": text.count(".") + text.count("!") + text.count("?"),
        "avg_word_length": sum(len(w) for w in words) / max(len(words), 1),
    }}
''',
        }

        code = templates.get(template, templates["basic"])
        return self.modifier.create_tool(name, f"Auto-generated {template} tool", code)

    def get_status(self) -> dict:
        return {
            "total_plugins": len(self.created_plugins),
            "plugins": self.created_plugins,
        }


# ─── Modification Log ─────────────────────────────────────────────────

class ModificationLog:
    """Persistent log of all self-modification activities."""

    def __init__(self, log_dir: str = "memory/brain/mod_log"):
        self._dir = Path(log_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._log_file = self._dir / "modifications.jsonl"
        self._summary_file = self._dir / "summary.json"
        self._stats: dict = {
            "total_modifications": 0,
            "total_repairs": 0,
            "total_backups": 0,
            "total_rollbacks": 0,
            "files_modified": set(),
            "tools_created": 0,
            "plugins_created": 0,
            "errors_fixed": 0,
            "auto_repairs": 0,
        }
        self._load_summary()

    def _load_summary(self):
        try:
            data = json.loads(self._summary_file.read_text())
            self._stats["total_modifications"] = data.get("total_modifications", 0)
            self._stats["total_repairs"] = data.get("total_repairs", 0)
            self._stats["total_backups"] = data.get("total_backups", 0)
            self._stats["total_rollbacks"] = data.get("total_rollbacks", 0)
            self._stats["files_modified"] = set(data.get("files_modified", []))
            self._stats["tools_created"] = data.get("tools_created", 0)
            self._stats["plugins_created"] = data.get("plugins_created", 0)
            self._stats["errors_fixed"] = data.get("errors_fixed", 0)
            self._stats["auto_repairs"] = data.get("auto_repairs", 0)
        except Exception:
            pass

    def _save_summary(self):
        data = {k: (list(v) if isinstance(v, set) else v) for k, v in self._stats.items()}
        self._summary_file.write_text(json.dumps(data, indent=2))

    def log(self, entry: dict):
        """Append a log entry."""
        entry["timestamp"] = datetime.now().isoformat()
        try:
            with open(self._log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception:
            pass

        action = entry.get("action", "")
        file_path = entry.get("file", "")
        if file_path:
            self._stats["files_modified"].add(file_path)

        if action == "modify":
            self._stats["total_modifications"] += 1
        elif action == "repair":
            self._stats["total_repairs"] += 1
            self._stats["errors_fixed"] += 1
        elif action == "auto_repair":
            self._stats["auto_repairs"] += 1
            self._stats["errors_fixed"] += 1
        elif action == "backup":
            self._stats["total_backups"] += 1
        elif action == "rollback":
            self._stats["total_rollbacks"] += 1
        elif action == "create_tool":
            self._stats["tools_created"] += 1
        elif action == "create_plugin":
            self._stats["plugins_created"] += 1

        self._save_summary()

    def log_modification(self, file_path: str, reason: str, success: bool, details: str = ""):
        self.log({"action": "modify", "file": file_path, "reason": reason, "success": success, "details": details})

    def log_repair(self, file_path: str, issue: str, fix: str, auto: bool = False):
        action = "auto_repair" if auto else "repair"
        self.log({"action": action, "file": file_path, "issue": issue, "fix": fix})

    def log_backup(self, file_path: str, backup_path: str):
        self.log({"action": "backup", "file": file_path, "backup": backup_path})

    def log_rollback(self, file_path: str, reason: str = ""):
        self.log({"action": "rollback", "file": file_path, "reason": reason})

    def log_tool_created(self, name: str, description: str):
        self.log({"action": "create_tool", "tool": name, "description": description})

    def log_plugin_created(self, name: str, capabilities: list):
        self.log({"action": "create_plugin", "plugin": name, "capabilities": capabilities})

    def log_error(self, error: str, context: str = ""):
        self.log({"action": "error", "error": error, "context": context})

    def get_recent(self, count: int = 20) -> list[dict]:
        """Get recent log entries."""
        entries = []
        try:
            if self._log_file.exists():
                lines = self._log_file.read_text().strip().split("\n")
                for line in lines[-count:]:
                    if line.strip():
                        entries.append(json.loads(line))
        except Exception:
            pass
        return entries

    def get_by_action(self, action: str, count: int = 20) -> list[dict]:
        """Get log entries filtered by action type."""
        all_entries = self.get_recent(500)
        filtered = [e for e in all_entries if e.get("action") == action]
        return filtered[-count:]

    def get_by_file(self, file_path: str, count: int = 20) -> list[dict]:
        """Get log entries for a specific file."""
        all_entries = self.get_recent(500)
        filtered = [e for e in all_entries if e.get("file") == file_path]
        return filtered[-count:]

    def get_summary(self) -> dict:
        """Get summary statistics."""
        return {
            "total_modifications": self._stats["total_modifications"],
            "total_repairs": self._stats["total_repairs"],
            "total_backups": self._stats["total_backups"],
            "total_rollbacks": self._stats["total_rollbacks"],
            "files_modified": len(self._stats["files_modified"]),
            "tools_created": self._stats["tools_created"],
            "plugins_created": self._stats["plugins_created"],
            "errors_fixed": self._stats["errors_fixed"],
            "auto_repairs": self._stats["auto_repairs"],
            "modified_files": list(self._stats["files_modified"]),
        }

    def format_log(self, entries: list[dict] = None, count: int = 20) -> str:
        """Format log entries as readable text."""
        if entries is None:
            entries = self.get_recent(count)
        if not entries:
            return "No log entries yet."

        lines = ["=== Modification Log ==="]
        for entry in entries:
            ts = entry.get("timestamp", "?")
            action = entry.get("action", "?")
            file_path = entry.get("file", "")
            reason = entry.get("reason", "")
            fix = entry.get("fix", "")
            issue = entry.get("issue", "")
            error = entry.get("error", "")
            success = entry.get("success", True)

            icon = {
                "modify": "[MODIFY]", "repair": "[REPAIR]", "auto_repair": "[AUTO]",
                "backup": "[BACKUP]", "rollback": "[ROLLBACK]", "create_tool": "[TOOL]",
                "create_plugin": "[PLUGIN]", "error": "[ERROR]"
            }.get(action, "[LOG]")

            line = f"  {ts[:19]} {icon} {file_path or ''}"
            if reason:
                line += f" - {reason}"
            if fix:
                line += f" -> {fix}"
            if issue:
                line += f" ({issue})"
            if error:
                line += f" ERROR: {error}"
            if not success:
                line += " [FAILED]"
            lines.append(line)

        return "\n".join(lines)


# ─── Auto Repair ──────────────────────────────────────────────────────

class AutoRepair:
    """Automatically detects and fixes errors in the codebase."""

    def __init__(self, modifier: SelfModifier, mod_log: ModificationLog):
        self.modifier = modifier
        self.log = mod_log
        self.repair_count = 0
        self.detected_issues: list[dict] = []
        self.fixed_issues: list[dict] = []
        self._running = False

    def scan_file(self, file_path: str) -> list[dict]:
        """Scan a file for common issues."""
        issues = []
        content = self.modifier.read_file(file_path)
        if not content:
            return issues

        # Check syntax
        if file_path.endswith(".py"):
            try:
                ast.parse(content)
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "file": file_path,
                    "line": e.lineno,
                    "message": str(e),
                    "severity": "high",
                })

        lines = content.split("\n")

        for i, line in enumerate(lines, 1):
            stripped = line.strip()

            # Bare except
            if stripped == "except:" or stripped.startswith("except :"):
                issues.append({
                    "type": "bare_except",
                    "file": file_path,
                    "line": i,
                    "message": "Bare except clause - should catch specific exception",
                    "severity": "low",
                    "fixable": True,
                })

            # Mutable default argument
            if "def " in line and ("=[]" in line or "={}" in line):
                issues.append({
                    "type": "mutable_default",
                    "file": file_path,
                    "line": i,
                    "message": "Mutable default argument",
                    "severity": "medium",
                    "fixable": True,
                })

            # print() in production code (outside main.py)
            if "main.py" not in file_path and "print(" in line and not stripped.startswith("#"):
                if "test" not in file_path.lower() and "example" not in file_path.lower():
                    issues.append({
                        "type": "print_statement",
                        "file": file_path,
                        "line": i,
                        "message": "print() in production code - consider logging",
                        "severity": "low",
                        "fixable": False,
                    })

            # TODO/FIXME/HACK
            for marker in ["TODO", "FIXME", "HACK", "XXX"]:
                if marker in line and not stripped.startswith("#"):
                    issues.append({
                        "type": "marker",
                        "file": file_path,
                        "line": i,
                        "message": f"{marker} found in code",
                        "severity": "low",
                        "fixable": False,
                    })

            # Unused imports (basic check)
            if stripped.startswith("import ") or stripped.startswith("from "):
                module = stripped.split()[-1] if "import" in stripped else stripped.split()[1]
                if len(module) > 2 and module not in content.replace(stripped, "", 1):
                    issues.append({
                        "type": "unused_import",
                        "file": file_path,
                        "line": i,
                        "message": f"Potentially unused import: {module}",
                        "severity": "low",
                        "fixable": True,
                    })

        return issues

    def scan_all(self) -> list[dict]:
        """Scan all Python files for issues."""
        all_issues = []
        for py_file in Path("purple_ultra").rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            issues = self.scan_file(str(py_file))
            all_issues.extend(issues)
        self.detected_issues = all_issues
        return all_issues

    def fix_bare_except(self, file_path: str, line_num: int) -> bool:
        """Fix bare except by replacing with Exception."""
        content = self.modifier.read_file(file_path)
        if not content:
            return False

        lines = content.split("\n")
        if 0 < line_num <= len(lines):
            line = lines[line_num - 1]
            if "except:" in line:
                lines[line_num - 1] = line.replace("except:", "except Exception:")
                new_content = "\n".join(lines)
                result = self.modifier.modify_file(file_path, new_content, "auto-fix bare except")
                if result["success"]:
                    self.log.log_repair(file_path, "bare except", "replaced with except Exception:", auto=True)
                    return True
        return False

    def fix_mutable_default(self, file_path: str, line_num: int) -> bool:
        """Fix mutable default arguments."""
        content = self.modifier.read_file(file_path)
        if not content:
            return False

        lines = content.split("\n")
        if 0 < line_num <= len(lines):
            line = lines[line_num - 1]
            new_line = line.replace("=[]", "=None").replace("={}", "=None")
            if "def " in new_line and "None" in new_line:
                lines[line_num - 1] = new_line
                new_content = "\n".join(lines)
                result = self.modifier.modify_file(file_path, new_content, "auto-fix mutable default")
                if result["success"]:
                    self.log.log_repair(file_path, "mutable default argument", "changed to None", auto=True)
                    return True
        return False

    def fix_file(self, file_path: str, issue: dict) -> bool:
        """Fix a specific issue in a file."""
        issue_type = issue.get("type", "")
        line_num = issue.get("line", 0)

        if issue_type == "bare_except":
            return self.fix_bare_except(file_path, line_num)
        elif issue_type == "mutable_default":
            return self.fix_mutable_default(file_path, line_num)
        return False

    def auto_fix_all(self) -> dict:
        """Scan and auto-fix all fixable issues."""
        issues = self.scan_all()
        fixed = 0
        failed = 0

        for issue in issues:
            if issue.get("fixable") and issue.get("severity") in ("high", "medium"):
                success = self.fix_file(issue["file"], issue)
                if success:
                    fixed += 1
                    self.fixed_issues.append(issue)
                else:
                    failed += 1

        self.repair_count += fixed
        return {
            "scanned": len(issues),
            "fixed": fixed,
            "failed": failed,
            "total_issues": len(issues),
            "high_severity": len([i for i in issues if i["severity"] == "high"]),
            "medium_severity": len([i for i in issues if i["severity"] == "medium"]),
            "low_severity": len([i for i in issues if i["severity"] == "low"]),
        }

    def get_health_report(self) -> str:
        """Get a health report of the codebase."""
        issues = self.scan_all()
        lines = ["=== Codebase Health Report ==="]
        lines.append(f"Total issues: {len(issues)}")

        by_severity = {}
        for issue in issues:
            sev = issue.get("severity", "unknown")
            by_severity.setdefault(sev, []).append(issue)

        for sev in ["high", "medium", "low"]:
            if sev in by_severity:
                lines.append(f"\n{sev.upper()} ({len(by_severity[sev])}):")
                for issue in by_severity[sev][:5]:
                    lines.append(f"  {issue['file']}:{issue.get('line', '?')} - {issue['message']}")

        lines.append(f"\nAuto-fixed: {self.repair_count}")
        return "\n".join(lines)

    def get_status(self) -> dict:
        return {
            "repair_count": self.repair_count,
            "detected_issues": len(self.detected_issues),
            "fixed_issues": len(self.fixed_issues),
            "recent_fixes": self.fixed_issues[-5:],
        }
