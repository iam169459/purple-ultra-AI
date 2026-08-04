"""Internet learning engine - learns from web sources."""

from __future__ import annotations

import json
import time
import re
from pathlib import Path
import urllib.request
import urllib.parse


class InternetLearner:
    def __init__(self, memory_dir: str = "data"):
        self._knowledge_dir = Path(memory_dir)
        self._knowledge_dir.mkdir(parents=True, exist_ok=True)
        self._knowledge_file = self._knowledge_dir / "learned_knowledge.json"
        self._knowledge: dict[str, dict] = {}
        self._load()

    def _load(self):
        if self._knowledge_file.exists():
            try:
                self._knowledge = json.loads(self._knowledge_file.read_text())
            except Exception:
                pass

    def _save(self):
        try:
            self._knowledge_file.write_text(json.dumps(self._knowledge, indent=2))
        except Exception:
            pass

    def learn_from_wikipedia(self, topic: str) -> str:
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(topic)}"
            req = urllib.request.Request(url, headers={"User-Agent": "PurpleUltra/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                summary = data.get("extract", "")
                if summary:
                    self._knowledge[topic.lower()] = {
                        "source": "wikipedia",
                        "content": summary[:2000],
                        "timestamp": time.time(),
                    }
                    self._save()
                    return summary[:1000]
            return f"No Wikipedia article found for: {topic}"
        except Exception as e:
            return f"Failed to learn from Wikipedia: {e}"

    def learn_from_duckduckgo(self, query: str) -> str:
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            req = urllib.request.Request(url, headers={"User-Agent": "PurpleUltra/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                abstract = data.get("Abstract", "")
                if abstract:
                    self._knowledge[query.lower()] = {
                        "source": "duckduckgo",
                        "content": abstract[:2000],
                        "timestamp": time.time(),
                    }
                    self._save()
                    return abstract[:1000]
                related = data.get("RelatedTopics", [])
                if related:
                    texts = [r.get("Text", "") for r in related[:3] if r.get("Text")]
                    if texts:
                        result = "\n".join(texts)
                        self._knowledge[query.lower()] = {
                            "source": "duckduckgo",
                            "content": result[:2000],
                            "timestamp": time.time(),
                        }
                        self._save()
                        return result[:1000]
            return f"No results for: {query}"
        except Exception as e:
            return f"Failed to search DuckDuckGo: {e}"

    def learn_from_brave(self, query: str, api_key: str = "") -> str:
        if not api_key:
            return "Brave API key required"
        try:
            url = f"https://api.search.brave.com/res/v1/web/search?q={urllib.parse.quote(query)}&count=3"
            req = urllib.request.Request(url, headers={
                "Accept": "application/json",
                "X-Subscription-Token": api_key,
            })
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                results = data.get("web", {}).get("results", [])
                texts = [r.get("description", "") for r in results[:3] if r.get("description")]
                if texts:
                    result = "\n".join(texts)
                    self._knowledge[query.lower()] = {
                        "source": "brave",
                        "content": result[:2000],
                        "timestamp": time.time(),
                    }
                    self._save()
                    return result[:1000]
            return f"No Brave results for: {query}"
        except Exception as e:
            return f"Failed to search Brave: {e}"

    def learn_topic(self, topic: str, sources: list[str] = None) -> str:
        if sources is None:
            sources = ["wikipedia", "duckduckgo"]
        results = []
        for source in sources:
            if source == "wikipedia":
                result = self.learn_from_wikipedia(topic)
            elif source == "duckduckgo":
                result = self.learn_from_duckduckgo(topic)
            else:
                continue
            if result and not result.startswith("Failed"):
                results.append(result)
        return "\n\n".join(results) if results else f"Could not learn about: {topic}"

    def recall_knowledge(self, topic: str) -> str:
        topic_lower = topic.lower()
        if topic_lower in self._knowledge:
            return self._knowledge[topic_lower]["content"]
        for key, data in self._knowledge.items():
            if topic_lower in key:
                return data["content"]
        return f"No knowledge found for: {topic}"

    def list_topics(self) -> list[str]:
        return list(self._knowledge.keys())

    def get_stats(self) -> dict:
        return {
            "total_topics": len(self._knowledge),
            "sources": list(set(d.get("source", "unknown") for d in self._knowledge.values())),
        }
