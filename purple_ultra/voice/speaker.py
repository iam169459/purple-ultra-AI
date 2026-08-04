"""Speaker recognition using voiceprint feature matching."""

from __future__ import annotations

import json
import time
from pathlib import Path
import numpy as np

from ..config.settings import SpeakerConfig
from .super_admin import SUPER_ADMIN_ID, SUPER_ADMIN_NAME, is_super_admin


class SpeakerRecognizer:
    """Identifies speakers by voiceprint distance matching."""

    def __init__(self, config: SpeakerConfig):
        self.config = config
        self._profiles_file = Path(config.profiles_file)
        self._profiles: dict[str, list[list[float]]] = {}
        self._load()

    def _load(self):
        if self._profiles_file.exists():
            try:
                self._profiles = json.loads(self._profiles_file.read_text())
            except Exception:
                self._profiles = {}

    def _save(self):
        try:
            self._profiles_file.parent.mkdir(parents=True, exist_ok=True)
            self._profiles_file.write_text(json.dumps(self._profiles, indent=2))
        except Exception:
            pass

    def identify(self, voiceprint: list[float]) -> str:
        """Identify a speaker by their voiceprint. Returns name or 'guest'."""
        if not voiceprint or not self._profiles:
            return "guest"

        vp = np.array(voiceprint, dtype=float)
        best_name = "guest"
        best_distance = float("inf")

        for name, samples in self._profiles.items():
            if not samples:
                continue
            mean_vp = np.mean(samples, axis=0)
            distance = np.linalg.norm(vp - mean_vp)
            if distance < best_distance:
                best_distance = distance
                best_name = name

        if best_distance <= self.config.threshold:
            return best_name
        return "guest"

    def register(self, name: str, voiceprint: list[float]) -> str:
        """Register a voiceprint for a speaker."""
        if not voiceprint:
            return "Empty voiceprint"

        if name not in self._profiles:
            self._profiles[name] = []

        self._profiles[name].append(voiceprint)
        if len(self._profiles[name]) > self.config.max_samples:
            self._profiles[name] = self._profiles[name][-self.config.max_samples:]

        self._save()
        return f"Registered voiceprint for {name} ({len(self._profiles[name])} samples)"

    def forget(self, name: str) -> str:
        """Remove a speaker profile. Cannot remove super admin."""
        # Prevent removal of super admin
        if is_super_admin(name) or name == SUPER_ADMIN_ID or name == SUPER_ADMIN_NAME:
            return f"Cannot remove super admin voice - it is permanently embedded in the system."
        
        if name in self._profiles:
            del self._profiles[name]
            self._save()
            return f"Forgot {name}"
        return f"No profile found for {name}"

    def get_admin_profile(self) -> dict:
        """Get super admin profile info."""
        return {
            "id": SUPER_ADMIN_ID,
            "name": SUPER_ADMIN_NAME,
            "removable": False,
            "priority": 100,
        }

    def is_admin(self, speaker_id: str) -> bool:
        """Check if a speaker is the super admin."""
        return is_super_admin(speaker_id)

    def list_speakers(self) -> list[str]:
        return list(self._profiles.keys())

    def get_speaker_count(self) -> int:
        return len(self._profiles)

    def is_enrolled(self, name: str) -> bool:
        return name in self._profiles
