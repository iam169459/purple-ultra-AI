"""Neural sentiment and intent classification."""

from __future__ import annotations

import json
import time
import re
from pathlib import Path
from dataclasses import dataclass, field
import numpy as np


@dataclass
class SentimentResult:
    label: str
    score: float
    scores: dict = field(default_factory=dict)
    tokens: int = 0


@dataclass
class IntentResult:
    intent: str
    confidence: float
    entities: dict = field(default_factory=dict)


class NeuralSentimentClassifier:
    def __init__(self, model_name: str = "distilbert-base-uncased-finetuned-sst-2-english"):
        self._model_name = model_name
        self._model = None
        self._tokenizer = None

    def _ensure_model(self):
        if self._model is None:
            try:
                from transformers import pipeline
                self._model = pipeline("sentiment-analysis", model=self._model_name)
            except Exception:
                self._model = False

    def classify(self, text: str) -> SentimentResult:
        self._ensure_model()
        if not self._model:
            return self._fallback_classify(text)
        try:
            result = self._model(text[:512])[0]
            label = result["label"].lower()
            score = result["score"]
            return SentimentResult(
                label=label,
                score=score,
                scores={label: score},
                tokens=len(text.split()),
            )
        except Exception:
            return self._fallback_classify(text)

    def _fallback_classify(self, text: str) -> SentimentResult:
        positive = {"good", "great", "awesome", "amazing", "love", "happy", "wonderful", "excellent", "perfect", "beautiful"}
        negative = {"bad", "terrible", "awful", "horrible", "hate", "sad", "angry", "worst", "ugly", "disgusting"}
        words = set(text.lower().split())
        pos = len(words & positive)
        neg = len(words & negative)
        total = pos + neg
        if total == 0:
            return SentimentResult(label="neutral", score=0.5, tokens=len(text.split()))
        score = pos / total if pos > neg else neg / total
        label = "positive" if pos > neg else "negative"
        return SentimentResult(label=label, score=score, tokens=len(text.split()))

    def classify_batch(self, texts: list[str]) -> list[SentimentResult]:
        return [self.classify(t) for t in texts]


class NeuralIntentClassifier:
    INTENTS = [
        "greeting", "farewell", "question", "request", "command",
        "information", "confirmation", "denial", "apology", "gratitude",
        "complaint", "compliment", "suggestion", "warning", "help",
    ]

    def __init__(self):
        self._examples: dict[str, list[str]] = {
            "greeting": ["hello", "hi", "hey", "good morning", "greetings"],
            "farewell": ["bye", "goodbye", "see you", "farewell", "exit"],
            "question": ["what", "why", "how", "when", "where", "who"],
            "request": ["please", "can you", "could you", "would you", "help me"],
            "command": ["do this", "run", "execute", "start", "stop", "open"],
            "information": ["tell me", "explain", "describe", "show me", "list"],
            "confirmation": ["yes", "yeah", "ok", "sure", "alright", "confirm"],
            "denial": ["no", "nope", "nah", "never", "cancel", "reject"],
            "apology": ["sorry", "apologize", "my bad", "excuse me", "pardon"],
            "gratitude": ["thank", "thanks", "appreciate", "grateful", "cheers"],
            "complaint": ["problem", "issue", "error", "broken", "wrong", "bug"],
            "compliment": ["good job", "amazing", "excellent", "perfect", "brilliant"],
            "suggestion": ["maybe", "perhaps", "suggest", "recommend", "try"],
            "warning": ["careful", "warning", "danger", "alert", "caution"],
            "help": ["help", "assist", "support", "guide", "tutorial"],
        }
        self._intent_embeddings: dict[str, list[float]] = {}
        self._build_embeddings()

    def _build_embeddings(self):
        for intent, examples in self._examples.items():
            embeddings = []
            for example in examples:
                emb = self._text_to_vector(example)
                embeddings.append(emb)
            if embeddings:
                mean_emb = np.mean(embeddings, axis=0)
                self._intent_embeddings[intent] = mean_emb.tolist()

    def _text_to_vector(self, text: str) -> np.ndarray:
        vocab_size = 5000
        vec = np.zeros(128)
        for word in text.lower().split():
            idx = hash(word) % vocab_size
            vec[idx % 128] += 1.0
        norm = np.linalg.norm(vec)
        return vec / norm if norm > 0 else vec

    def classify(self, text: str) -> IntentResult:
        text_emb = self._text_to_vector(text)
        best_intent = "unknown"
        best_score = 0.0
        for intent, intent_emb in self._intent_embeddings.items():
            intent_vec = np.array(intent_emb)
            similarity = float(np.dot(text_emb, intent_vec) / (np.linalg.norm(text_emb) * np.linalg.norm(intent_vec) + 1e-10))
            if similarity > best_score:
                best_score = similarity
                best_intent = intent
        if "?" in text and best_score < 0.5:
            best_intent = "question"
            best_score = 0.6
        return IntentResult(intent=best_intent, confidence=best_score)

    def add_example(self, intent: str, example: str):
        if intent not in self._examples:
            self._examples[intent] = []
        self._examples[intent].append(example)
        self._build_embeddings()


class NeuralNER:
    def __init__(self):
        self._patterns = {
            "TIME": [r"\b(\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)?)\b"],
            "DATE": [r"\b(\d{4}-\d{2}-\d{2})\b", r"\b(\d{1,2}/\d{1,2}/\d{2,4})\b"],
            "NUMBER": [r"\b(\d+(?:\.\d+)?)\b"],
            "EMAIL": [r"\b([\w.-]+@[\w.-]+\.\w+)\b"],
            "URL": [r"\b(https?://\S+)\b"],
            "PHONE": [r"\b(\+?\d{10,})\b"],
        }

    def extract(self, text: str) -> list[dict]:
        entities = []
        for label, patterns in self._patterns.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    entities.append({
                        "text": match.group(1),
                        "label": label,
                        "start": match.start(),
                        "end": match.end(),
                    })
        return entities

    def extract_by_type(self, text: str, entity_type: str) -> list[str]:
        entities = self.extract(text)
        return [e["text"] for e in entities if e["label"] == entity_type]
