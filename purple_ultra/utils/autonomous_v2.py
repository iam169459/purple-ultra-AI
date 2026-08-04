"""Autonomous intelligence engine - optimized for maximum speed."""

from __future__ import annotations

import time
import hashlib
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Optional
from enum import IntEnum
from collections import defaultdict
import json


class AnalysisType(IntEnum):
    SENTIMENT = 0
    INTENT = 1
    ENTITY = 2
    TOPIC = 3
    URGENCY = 4
    LEARNING = 5
    PATTERN = 6


@dataclass(slots=True)
class AnalysisResult:
    analysis_type: AnalysisType
    confidence: float
    data: tuple
    timestamp: float = field(default_factory=time.time)


@dataclass(slots=True)
class KnowledgeItem:
    category: str
    content: str
    confidence: float
    importance: float
    access_count: int = 0


@dataclass(slots=True)
class Skill:
    domain: str
    proficiency: float = 0.0
    use_count: int = 0
    success_rate: float = 0.5


_POSITIVE = frozenset({"good", "great", "excellent", "happy", "love", "like", "wonderful", "amazing", "fantastic", "perfect", "best", "beautiful", "thanks", "awesome", "nice", "brilliant", "superb", "outstanding"})
_NEGATIVE = frozenset({"bad", "terrible", "hate", "dislike", "awful", "horrible", "worst", "ugly", "sad", "angry", "frustrated", "broken", "failed", "error", "wrong", "poor", "useless"})
_URGENT = frozenset({"urgent", "asap", "immediately", "emergency", "critical", "important", "now", "quickly", "hurry", "deadline", "fast", "rush"})
_QWORDS = frozenset({"what", "how", "why", "when", "where", "who", "which", "can", "could", "would"})
_CMDWORDS = frozenset({"do", "make", "create", "generate", "write", "run", "execute", "start", "stop", "delete", "add", "update", "change"})
_REQWORDS = frozenset({"please", "help", "need", "want", "require", "looking"})
_CMPWORDS = frozenset({"problem", "issue", "error", "bug", "broken", "failed"})
_TECHWORDS = frozenset({"python", "code", "programming", "software", "ai", "machine", "learning", "neural", "network", "data", "algorithm", "api", "database", "server", "cloud", "javascript", "computer", "hardware"})
_SCIWORDS = frozenset({"research", "study", "experiment", "hypothesis", "theory", "evidence", "scientific"})
_BUSWORDS = frozenset({"market", "sales", "revenue", "customer", "product", "strategy", "profit", "company", "business"})
_HLTWORDS = frozenset({"health", "medical", "doctor", "patient", "treatment", "disease", "medicine"})
_EDUWORDS = frozenset({"learn", "teach", "student", "school", "university", "course", "education"})
_CRDWORDS = frozenset({"art", "music", "design", "creative", "write", "story", "paint", "dance"})
_QIND = frozenset({"how", "why", "explain", "tell", "teach", "learn", "understand"})
_CIND = frozenset({"confused", "unclear", "complicated", "difficult", "hard"})
_CRIND = frozenset({"interesting", "wonder", "curious", "explore", "discover"})
_PSIND = frozenset({"solve", "fix", "debug", "trouble", "issue", "problem", "challenge"})


class KnowledgeGraph:
    __slots__ = ('_nodes', '_categories', '_dir')

    def __init__(self, storage_dir: str = "memory/knowledge"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._nodes: dict[str, KnowledgeItem] = {}
        self._categories: dict[str, list[str]] = defaultdict(list)
        self._load()

    def _load(self):
        f = self._dir / "graph.json"
        if f.exists():
            try:
                data = json.loads(f.read_text())
                for k, v in data.get("nodes", {}).items():
                    self._nodes[k] = KnowledgeItem(**v)
                self._categories = defaultdict(list, data.get("categories", {}))
            except Exception:
                pass

    def add(self, category: str, content: str, confidence: float = 0.8, importance: float = 0.5) -> str:
        cid = f"{category}_{hash(content[:64].encode()) & 0xFFFFFFFF:08x}"
        if cid in self._nodes:
            n = self._nodes[cid]
            if confidence > n.confidence:
                n.confidence = confidence
            n.access_count += 1
            return cid
        self._nodes[cid] = KnowledgeItem(category, content[:200], confidence, importance)
        self._categories[category].append(cid)
        return cid

    def stats(self) -> tuple[int, int]:
        return len(self._nodes), len(self._categories)


class SkillManager:
    __slots__ = ('_skills', '_dir')

    def __init__(self, storage_dir: str = "memory/skills"):
        self._dir = Path(storage_dir)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._skills: dict[str, Skill] = {}
        self._load()

    def _load(self):
        f = self._dir / "skills.json"
        if f.exists():
            try:
                data = json.loads(f.read_text())
                for k, v in data.items():
                    self._skills[k] = Skill(**v)
            except Exception:
                pass

    def learn(self, domain: str) -> str:
        sid = f"{domain}_{hash(domain.encode()) & 0xFFFF:04x}"
        if sid in self._skills:
            s = self._skills[sid]
            s.use_count += 1
            s.proficiency = min(1.0, s.proficiency + 0.1 * (1 - s.proficiency))
            return sid
        self._skills[sid] = Skill(domain)
        return sid

    def stats(self) -> tuple[int, int]:
        return len(self._skills), len(set(s.domain for s in self._skills.values()))


class PatternDetector:
    __slots__ = ('_freq',)

    def __init__(self):
        self._freq: dict[str, int] = defaultdict(int)

    def detect(self, text: str) -> Optional[str]:
        words = text.lower().split()
        for i in range(len(words) - 1):
            bg = f"{words[i]} {words[i+1]}"
            self._freq[bg] += 1
            if self._freq[bg] == 3:
                return bg
        return None


class AutonomousEngine:
    __slots__ = ('kg', 'skills', 'patterns', '_cache', '_enabled', '_lock',
                 '_analysis_count', '_learn_count')

    def __init__(self, config: dict = None):
        config = config or {}
        self.kg = KnowledgeGraph(config.get("knowledge_dir", "memory/knowledge"))
        self.skills = SkillManager(config.get("skills_dir", "memory/skills"))
        self.patterns = PatternDetector()
        self._cache: dict[int, tuple] = {}
        self._enabled = True
        self._lock = threading.Lock()
        self._analysis_count = 0
        self._learn_count = 0

    def auto_analyze(self, text: str, context: dict = None) -> list[AnalysisResult]:
        if not self._enabled or len(text) < 3:
            return []

        text_lower = text.lower()
        words = set(text_lower.split())
        h = hash(text_lower) & 0xFFFFFFFF

        if h in self._cache:
            return self._cache[h]

        results = []
        ts = time.time()

        pc = len(words & _POSITIVE)
        nc = len(words & _NEGATIVE)
        tc = pc + nc
        if tc:
            sc = (pc - nc) / tc
            sl = "positive" if sc > 0.2 else ("negative" if sc < -0.2 else "neutral")
        else:
            sc, sl = 0.0, "neutral"
        results.append(AnalysisResult(AnalysisType.SENTIMENT, abs(sc) if tc else 0.5, (sc, sl)))

        qi = bool(words & _QWORDS or "?" in text)
        ci = bool(words & _CMDWORDS)
        ri = bool(words & _REQWORDS)
        co = bool(words & _CMPWORDS)
        intent = "question" if qi else ("command" if ci else ("complaint" if co else ("request" if ri else "unknown")))
        conf = 0.8 if qi or ci else (0.6 if ri or co else 0.3)
        results.append(AnalysisResult(AnalysisType.INTENT, conf, (intent,)))

        es = []
        tl = text_lower
        if "@" in text:
            at = tl.find("@")
            sp = tl.rfind(" ", 0, at)
            ep = tl.find(" ", at)
            if sp >= 0 and ep >= 0:
                es.append(("email", text[sp+1:ep]))
        for w in text.split():
            if w and w[0].isupper() and len(w) > 1 and not w.isupper():
                es.append(("name", w))
        results.append(AnalysisResult(AnalysisType.ENTITY, min(1.0, len(es) * 0.3 + 0.3), tuple(es)))

        topic = "general"
        tc2 = 0
        if words & _TECHWORDS:
            topic, tc2 = "technology", len(words & _TECHWORDS)
        elif words & _SCIWORDS:
            topic, tc2 = "science", len(words & _SCIWORDS)
        elif words & _BUSWORDS:
            topic, tc2 = "business", len(words & _BUSWORDS)
        elif words & _HLTWORDS:
            topic, tc2 = "health", len(words & _HLTWORDS)
        elif words & _EDUWORDS:
            topic, tc2 = "education", len(words & _EDUWORDS)
        elif words & _CRDWORDS:
            topic, tc2 = "creative", len(words & _CRDWORDS)
        results.append(AnalysisResult(AnalysisType.TOPIC, min(1.0, tc2 * 0.3 + 0.4), (topic,)))

        us = sum(1 for w in _URGENT if w in tl) + ("!" in text)
        ul = "high" if us >= 3 else ("medium" if us >= 1 else "low")
        results.append(AnalysisResult(AnalysisType.URGENCY, 0.9 if us >= 3 else (0.7 if us >= 1 else 0.5), (ul, us)))

        lo = []
        if words & _QIND:
            lo.append("question")
        if words & _CIND:
            lo.append("confusion")
        if words & _CRIND:
            lo.append("curiosity")
        if words & _PSIND:
            lo.append("problem_solving")
        lc = min(1.0, len(lo) * 0.3 + 0.4) if lo else 0.3
        results.append(AnalysisResult(AnalysisType.LEARNING, lc, tuple(lo)))

        pat = self.patterns.detect(text)
        if pat:
            results.append(AnalysisResult(AnalysisType.PATTERN, 0.7, (pat,)))

        self.kg.add(topic, text, min(1.0, tc2 * 0.2 + 0.5))
        self.skills.learn(topic)

        with self._lock:
            self._analysis_count += 1
            self._learn_count += 1

        self._cache[h] = results
        if len(self._cache) > 5000:
            keys = list(self._cache.keys())[:2500]
            for k in keys:
                del self._cache[k]

        return results

    def auto_learn(self, text: str, source: str = "interaction") -> dict:
        results = self.auto_analyze(text)
        topic = "general"
        for r in results:
            if r.analysis_type == AnalysisType.TOPIC:
                topic = r.data[0]
                break
        return {"analyses": len(results), "topic": topic, "knowledge": self.kg.stats()[0]}

    def get_status(self) -> dict:
        kn, kc = self.kg.stats()
        sn, sd = self.skills.stats()
        return {
            "enabled": self._enabled,
            "analyses": self._analysis_count,
            "learnings": self._learn_count,
            "knowledge_items": kn,
            "knowledge_categories": kc,
            "skills": sn,
            "skill_domains": sd,
            "cache_size": len(self._cache),
        }

    def shutdown(self):
        pass
