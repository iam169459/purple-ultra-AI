"""Advanced security with differential privacy and encryption."""

from __future__ import annotations

import hashlib
import json
import time
import secrets
import math
from pathlib import Path
from dataclasses import dataclass
import numpy as np


@dataclass
class PrivacyBudget:
    epsilon: float = 1.0
    delta: float = 1e-5
    used_epsilon: float = 0.0


class DifferentialPrivacy:
    def __init__(self, epsilon: float = 1.0, delta: float = 1e-5):
        self._budget = PrivacyBudget(epsilon=epsilon, delta=delta)
        self._noise_scale = 1.0 / epsilon

    def add_noise(self, value: float, sensitivity: float = 1.0) -> float:
        if self._budget.used_epsilon >= self._budget.epsilon:
            return value
        noise = np.random.laplace(0, sensitivity * self._noise_scale)
        self._budget.used_epsilon += 0.01
        return value + noise

    def add_noise_to_vector(self, vector: list[float], sensitivity: float = 1.0) -> list[float]:
        return [self.add_noise(v, sensitivity) for v in vector]

    def add_noise_to_dict(self, data: dict, sensitivity: float = 1.0) -> dict:
        noisy = {}
        for key, value in data.items():
            if isinstance(value, (int, float)):
                noisy[key] = self.add_noise(float(value), sensitivity)
            else:
                noisy[key] = value
        return noisy

    def privacy_accountant(self) -> dict:
        return {
            "epsilon_budget": self._budget.epsilon,
            "epsilon_used": self._budget.used_epsilon,
            "epsilon_remaining": self._budget.epsilon - self._budget.used_epsilon,
            "delta": self._budget.delta,
            "privacy_loss": self._budget.used_epsilon / self._budget.epsilon if self._budget.epsilon > 0 else 0,
        }

    def check_budget(self) -> bool:
        return self._budget.used_epsilon < self._budget.epsilon


class Encryption:
    @staticmethod
    def hash_data(data: str, algorithm: str = "sha256") -> str:
        h = hashlib.new(algorithm)
        h.update(data.encode())
        return h.hexdigest()

    @staticmethod
    def xor_encrypt(data: str, key: str) -> str:
        encrypted = []
        for i, char in enumerate(data):
            encrypted_char = ord(char) ^ ord(key[i % len(key)])
            encrypted.append(format(encrypted_char, "02x"))
        return "".join(encrypted)

    @staticmethod
    def xor_decrypt(encrypted: str, key: str) -> str:
        decrypted = []
        for i in range(0, len(encrypted), 2):
            char_code = int(encrypted[i:i+2], 16)
            decrypted_char = chr(char_code ^ ord(key[i // 2 % len(key)]))
            decrypted.append(decrypted_char)
        return "".join(decrypted)

    @staticmethod
    def generate_key(length: int = 32) -> str:
        return secrets.token_hex(length)

    @staticmethod
    def vigenere_encrypt(text: str, key: str) -> str:
        result = []
        key_idx = 0
        for char in text:
            if char.isalpha():
                shift = ord(key[key_idx % len(key)].lower()) - ord('a')
                if char.isupper():
                    result.append(chr((ord(char) - ord('A') + shift) % 26 + ord('A')))
                else:
                    result.append(chr((ord(char) - ord('a') + shift) % 26 + ord('a')))
                key_idx += 1
            else:
                result.append(char)
        return "".join(result)

    @staticmethod
    def vigenere_decrypt(text: str, key: str) -> str:
        result = []
        key_idx = 0
        for char in text:
            if char.isalpha():
                shift = ord(key[key_idx % len(key)].lower()) - ord('a')
                if char.isupper():
                    result.append(chr((ord(char) - ord('A') - shift) % 26 + ord('A')))
                else:
                    result.append(chr((ord(char) - ord('a') - shift) % 26 + ord('a')))
                key_idx += 1
            else:
                result.append(char)
        return "".join(result)


class SecureStorage:
    def __init__(self, storage_dir: str = "data/secure"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._key = Encryption.generate_key()
        self._entries: dict[str, dict] = {}
        self._load()

    def _load(self):
        secure_file = self._dir / "secure.json"
        if secure_file.exists():
            try:
                encrypted = secure_file.read_text()
                decrypted = Encryption.xor_decrypt(encrypted, self._key)
                self._entries = json.loads(decrypted)
            except Exception:
                pass

    def _save(self):
        try:
            data = json.dumps(self._entries)
            encrypted = Encryption.xor_encrypt(data, self._key)
            (self._dir / "secure.json").write_text(encrypted)
        except Exception:
            pass

    def store(self, key: str, value: Any, encrypt: bool = True):
        if encrypt:
            value = {"encrypted": True, "data": Encryption.xor_encrypt(json.dumps(value), self._key)}
        self._entries[key] = {"value": value, "timestamp": time.time()}
        self._save()

    def retrieve(self, key: str, decrypt: bool = True) -> Any:
        entry = self._entries.get(key)
        if not entry:
            return None
        value = entry["value"]
        if decrypt and isinstance(value, dict) and value.get("encrypted"):
            return json.loads(Encryption.xor_decrypt(value["data"], self._key))
        return value

    def delete(self, key: str) -> bool:
        if key in self._entries:
            del self._entries[key]
            self._save()
            return True
        return False

    def list_keys(self) -> list[str]:
        return list(self._entries.keys())


class SecurityAudit:
    def __init__(self):
        self._audit_log: list[dict] = []

    def log_access(self, resource: str, action: str, user: str = "system"):
        self._audit_log.append({
            "resource": resource,
            "action": action,
            "user": user,
            "timestamp": time.time(),
        })

    def check_rate_limit(self, user: str, max_requests: int = 100, window: float = 3600) -> bool:
        now = time.time()
        user_requests = [r for r in self._audit_log if r["user"] == user and now - r["timestamp"] < window]
        return len(user_requests) < max_requests

    def detect_anomalies(self) -> list[dict]:
        anomalies = []
        user_counts = {}
        for entry in self._audit_log:
            user = entry["user"]
            user_counts[user] = user_counts.get(user, 0) + 1
        for user, count in user_counts.items():
            if count > 100:
                anomalies.append({"user": user, "count": count, "type": "high_frequency"})
        return anomalies

    def get_audit_log(self, count: int = 50) -> list[dict]:
        return self._audit_log[-count:]

    def get_stats(self) -> dict:
        return {
            "total_events": len(self._audit_log),
            "unique_users": len(set(r["user"] for r in self._audit_log)),
            "unique_resources": len(set(r["resource"] for r in self._audit_log)),
        }
