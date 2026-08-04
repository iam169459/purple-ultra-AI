"""Advanced NLP with intent classification, NER, and sentiment analysis."""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class Intent:
    name: str
    confidence: float
    entities: dict = field(default_factory=dict)


@dataclass
class Entity:
    text: str
    label: str
    start: int
    end: int
    confidence: float = 1.0


@dataclass
class Sentiment:
    label: str
    score: float
    pos: float = 0.0
    neg: float = 0.0
    neu: float = 0.0


class NLPEngine:
    INTENT_PATTERNS = {
        "greeting": (r"\b(hello|hi|hey|greetings|good\s*(morning|afternoon|evening))\b", 0.9),
        "farewell": (r"\b(bye|goodbye|see\s*you|farewell|exit|quit)\b", 0.9),
        "question": (r"\?$", 0.8),
        "request_help": (r"\b(help|assist|support|how\s*(do|can|to)|what\s*(can|do))\b", 0.85),
        "set_reminder": (r"\b(remind|reminder|remember\s*to|don't\s*forget)\b", 0.8),
        "create_task": (r"\b(task|todo|to-do|add\s*task|create\s*task|schedule)\b", 0.8),
        "search": (r"\b(search|look\s*up|find|google|browse|query)\b", 0.85),
        "play_media": (r"\b(play|listen|watch|stream|video|music|song|movie)\b", 0.8),
        "open_app": (r"\b(open|launch|start|run)\s+(app|application)\b", 0.8),
        "take_photo": (r"\b(photo|picture|camera|capture|selfie)\b", 0.75),
        "screenshot": (r"\b(screenshot|screen\s*shot|capture\s*screen|grab\s*screen)\b", 0.9),
        "system_info": (r"\b(system|info|status|battery|network|disk|cpu|memory)\b", 0.7),
        "time_date": (r"\b(time|date|day|today|now|clock|what\s*(time|date))\b", 0.85),
        "tell_joke": (r"\b(joke|funny|humor|laugh|make\s*me\s*laugh)\b", 0.8),
        "compliment": (r"\b(compliment|praise|good\s*job|well\s*done|amazing|awesome)\b", 0.7),
        "translate": (r"\b(translate|translation|language|spanish|french|chinese|bangla|hindi)\b", 0.8),
        "calculate": (r"\b(calculate|compute|math|solve|equation|\d+\s*[+\-*/]\s*\d+)\b", 0.8),
        "code": (r"\b(code|program|function|class|python|javascript|debug|fix\s*bug)\b", 0.75),
        "email": (r"\b(email|mail|send\s*email|write\s*email|inbox)\b", 0.8),
        "weather": (r"\b(weather|forecast|temperature|rain|snow|sunny|cloudy)\b", 0.8),
        "news": (r"\b(news|headlines|current\s*events|what's\s*happening)\b", 0.75),
        "shutdown": (r"\b(shutdown|shut\s*down|turn\s*off|power\s*off|sleep)\b", 0.85),
        "volume": (r"\b(volume|loud|quiet|mute|unmute|softer|louder)\b", 0.8),
    }

    POSITIVE_WORDS = {
        "good", "great", "awesome", "excellent", "amazing", "wonderful", "fantastic",
        "love", "like", "happy", "glad", "nice", "perfect", "best", "beautiful",
        "brilliant", "outstanding", "superb", "terrific", "fabulous", "marvelous",
        "thank", "thanks", "appreciate", "grateful", "pleased", "delighted",
        "excited", "thrilled", "overjoyed", "elated", "ecstatic", "blissful",
        "yes", "yeah", "yep", "sure", "okay", "ok", "alright", "fine",
    }
    NEGATIVE_WORDS = {
        "bad", "terrible", "awful", "horrible", "worst", "hate", "dislike",
        "sad", "unhappy", "depressed", "miserable", "gloomy", "mournful",
        "angry", "furious", "mad", "annoyed", "frustrated", "irritated",
        "disappointed", "letdown", "unfortunate", "regret", "sorry", "apologize",
        "no", "nah", "nope", "never", "nothing", "nobody", "nowhere",
        "fail", "failure", "error", "wrong", "broken", "problem", "issue",
    }

    def classify_intent(self, text: str) -> Intent:
        text_lower = text.lower().strip()
        best_intent = "unknown"
        best_confidence = 0.0
        for intent_name, (pattern, base_conf) in self.INTENT_PATTERNS.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                if base_conf > best_confidence:
                    best_intent = intent_name
                    best_confidence = base_conf
        if best_confidence < 0.5 and "?" in text:
            best_intent = "question"
            best_confidence = 0.7
        return Intent(name=best_intent, confidence=best_confidence)

    def extract_entities(self, text: str) -> list[Entity]:
        entities = []
        time_pattern = r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b"
        for match in re.finditer(time_pattern, text):
            entities.append(Entity(text=match.group(1), label="TIME", start=match.start(), end=match.end()))
        date_pattern = r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}/\d{1,2}/\d{2,4})\b"
        for match in re.finditer(date_pattern, text):
            entities.append(Entity(text=match.group(1), label="DATE", start=match.start(), end=match.end()))
        number_pattern = r"\b(\d+(?:\.\d+)?)\b"
        for match in re.finditer(number_pattern, text):
            entities.append(Entity(text=match.group(1), label="NUMBER", start=match.start(), end=match.end()))
        quoted_pattern = r'"([^"]+)"'
        for match in re.finditer(quoted_pattern, text):
            entities.append(Entity(text=match.group(1), label="QUOTED", start=match.start(), end=match.end()))
        app_names = [
            "safari", "chrome", "firefox", "spotify", "slack", "discord",
            "vscode", "xcode", "terminal", "finder", "itunes", "netflix",
            "youtube", "maps", "photos", "messages", "mail", "calendar",
        ]
        text_lower = text.lower()
        for app in app_names:
            if app in text_lower:
                idx = text_lower.index(app)
                entities.append(Entity(text=app, label="APP", start=idx, end=idx + len(app)))
        return entities

    def analyze_sentiment(self, text: str) -> Sentiment:
        words = set(re.findall(r"\b\w+\b", text.lower()))
        pos_count = len(words & self.POSITIVE_WORDS)
        neg_count = len(words & self.NEGATIVE_WORDS)
        total = pos_count + neg_count
        if total == 0:
            return Sentiment(label="neutral", score=0.5, pos=0.33, neg=0.33, neu=0.34)
        pos_score = pos_count / total
        neg_score = neg_count / total
        if pos_score > neg_score:
            label = "positive"
            score = 0.5 + (pos_score - neg_score) * 0.5
        elif neg_score > pos_score:
            label = "negative"
            score = 0.5 - (neg_score - pos_score) * 0.5
        else:
            label = "neutral"
            score = 0.5
        return Sentiment(
            label=label,
            score=score,
            pos=pos_score,
            neg=neg_score,
            neu=1 - pos_score - neg_score,
        )

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) <= max_sentences:
            return text
        scored = []
        for sent in sentences:
            words = set(sent.lower().split())
            score = len(words & self.POSITIVE_WORDS) + len(words & self.NEGATIVE_WORDS)
            score += len(sent.split()) * 0.1
            scored.append((score, sent))
        scored.sort(key=lambda x: -x[0])
        top = [s for _, s in scored[:max_sentences]]
        return ". ".join(top) + "."

    def detect_language(self, text: str) -> str:
        bangla_chars = len(re.findall(r"[\u0980-\u09FF]", text))
        arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
        chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
        total = len(text)
        if total == 0:
            return "unknown"
        if bangla_chars / total > 0.3:
            return "bangla"
        if arabic_chars / total > 0.3:
            return "arabic"
        if chinese_chars / total > 0.3:
            return "chinese"
        return "english"
