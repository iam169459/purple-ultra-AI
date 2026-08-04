"""Code analysis and auto-fix engine."""

from __future__ import annotations

import ast
from pathlib import Path
from dataclasses import dataclass


@dataclass
class CodeIssue:
    file: str
    line: int
    issue_type: str
    message: str
    severity: str = "low"


class CodeAnalyzer:
    """Analyzes Python code for issues."""

    def __init__(self):
        self.issues: list[CodeIssue] = []

    def analyze_file(self, file_path: str) -> list[CodeIssue]:
        issues = []
        try:
            content = Path(file_path).read_text()
            tree = ast.parse(content)
            
            lines = content.split("\n")
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                if stripped == "except:" or stripped.startswith("except :"):
                    issues.append(CodeIssue(file_path, i, "bare_except", "Bare except clause"))
        except SyntaxError as e:
            issues.append(CodeIssue(file_path, e.lineno or 0, "syntax_error", str(e), "high"))
        except Exception:
            pass
        
        self.issues.extend(issues)
        return issues

    def analyze_directory(self, directory: str) -> list[CodeIssue]:
        issues = []
        for py_file in Path(directory).rglob("*.py"):
            if "__pycache__" not in str(py_file):
                issues.extend(self.analyze_file(str(py_file)))
        return issues

    def get_stats(self) -> dict:
        return {"total_issues": len(self.issues)}
