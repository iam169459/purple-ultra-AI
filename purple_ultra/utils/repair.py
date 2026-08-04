"""Self-repair and autonomous improvement system."""

from __future__ import annotations

import os
import json
from pathlib import Path
from dataclasses import dataclass


@dataclass
class RepairResult:
    file: str
    issue: str
    fixed: bool
    details: str = ""


class SelfRepair:
    """Scans and fixes common issues."""

    def __init__(self):
        self.repairs: list[RepairResult] = []

    def auto_fix_all(self) -> dict:
        fixes = []
        
        # Ensure required directories exist
        required_dirs = ["memory", "memory/brain", "memory/backups"]
        for d in required_dirs:
            path = Path(d)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                fixes.append(RepairResult(d, "missing_dir", True, "Created directory"))
        
        # Check consciousness file
        cons_path = Path("memory/brain/consciousness.json")
        if cons_path.exists():
            try:
                json.loads(cons_path.read_text())
            except Exception as e:
                fixes.append(RepairResult(str(cons_path), "corrupt_json", False, str(e)))
        
        self.repairs.extend(fixes)
        return {"fixes": fixes, "total": len(fixes)}

    def get_stats(self) -> dict:
        return {"total_repairs": len(self.repairs)}
