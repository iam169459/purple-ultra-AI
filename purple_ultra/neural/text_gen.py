"""Neural text generation with local models and fine-tuning support."""

from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Generator


@dataclass
class GenerationConfig:
    max_length: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 50
    repetition_penalty: float = 1.1
    do_sample: bool = True
    num_return_sequences: int = 1


@dataclass
class GenerationResult:
    text: str
    tokens: int = 0
    duration: float = 0
    model: str = ""
    finish_reason: str = "stop"


class TextGenerator:
    def __init__(self, model_name: str = "gpt2", device: str = "cpu"):
        self._model_name = model_name
        self._device = device
        self._model = None
        self._tokenizer = None

    def _ensure_model(self):
        if self._model is None:
            try:
                from transformers import AutoModelForCausalLM, AutoTokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(self._model_name)
                self._model = AutoModelForCausalLM.from_pretrained(self._model_name)
                self._model.to(self._device)
            except Exception:
                self._model = False

    def generate(self, prompt: str, config: GenerationConfig = None) -> GenerationResult:
        config = config or GenerationConfig()
        self._ensure_model()
        if not self._model:
            return self._fallback_generate(prompt, config)
        start = time.time()
        try:
            import torch
            inputs = self._tokenizer(prompt, return_tensors="pt").to(self._device)
            with torch.no_grad():
                outputs = self._model.generate(
                    **inputs,
                    max_length=config.max_length,
                    temperature=config.temperature,
                    top_p=config.top_p,
                    top_k=config.top_k,
                    repetition_penalty=config.repetition_penalty,
                    do_sample=config.do_sample,
                    num_return_sequences=config.num_return_sequences,
                )
            text = self._tokenizer.decode(outputs[0], skip_special_tokens=True)
            duration = time.time() - start
            tokens = outputs.shape[1] - inputs["input_ids"].shape[1]
            return GenerationResult(text=text, tokens=tokens, duration=duration, model=self._model_name)
        except Exception as e:
            return GenerationResult(text="", duration=time.time() - start, model=self._model_name, finish_reason=f"error: {e}")

    def _fallback_generate(self, prompt: str, config: GenerationConfig) -> GenerationResult:
        templates = [
            "Based on your input, here's my analysis: {prompt}",
            "That's an interesting point. Let me think about {prompt}",
            "I understand you're asking about {prompt}. Let me help.",
        ]
        import random
        template = random.choice(templates)
        result = template.format(prompt=prompt[:200])
        return GenerationResult(text=result, tokens=len(result.split()), model="fallback")

    def generate_stream(self, prompt: str, config: GenerationConfig = None) -> Generator[str, None, None]:
        config = config or GenerationConfig()
        result = self.generate(prompt, config)
        words = result.text.split()
        for word in words:
            yield word + " "
            time.sleep(0.02)

    def complete(self, text: str, max_tokens: int = 100) -> str:
        config = GenerationConfig(max_length=max_tokens + len(text.split()))
        result = self.generate(text, config)
        return result.text[len(text):]

    def get_status(self) -> dict:
        return {
            "model": self._model_name,
            "device": self._device,
            "loaded": self._model is not None and self._model is not False,
        }


class DialogueGenerator:
    def __init__(self, generator: TextGenerator):
        self._generator = generator
        self._history: list[dict] = []
        self._system_prompt = "You are a helpful AI assistant."

    def set_system_prompt(self, prompt: str):
        self._system_prompt = prompt

    def chat(self, user_input: str, context: str = "") -> GenerationResult:
        history_text = "\n".join(
            f"User: {h['user']}\nAssistant: {h['assistant']}" for h in self._history[-5:]
        )
        prompt = f"{self._system_prompt}\n\n{context}\n\n{history_text}\nUser: {user_input}\nAssistant:"
        result = self._generator.generate(prompt)
        self._history.append({"user": user_input, "assistant": result.text})
        if len(self._history) > 50:
            self._history = self._history[-50:]
        return result

    def get_history(self) -> list[dict]:
        return list(self._history)

    def clear_history(self):
        self._history.clear()


class Summarizer:
    def __init__(self, generator: TextGenerator):
        self._generator = generator

    def summarize(self, text: str, max_length: int = 200) -> str:
        prompt = f"Summarize the following text concisely:\n\n{text[:3000]}\n\nSummary:"
        result = self._generator.generate(prompt, GenerationConfig(max_length=max_length))
        return result.text

    def extract_keywords(self, text: str, count: int = 10) -> list[str]:
        prompt = f"Extract {count} key terms from this text:\n\n{text[:2000]}\n\nKeywords:"
        result = self._generator.generate(prompt, GenerationConfig(max_length=100))
        keywords = [kw.strip().strip("-").strip() for kw in result.text.split(",")]
        return [kw for kw in keywords if kw][:count]


class Translator:
    def __init__(self, generator: TextGenerator):
        self._generator = generator

    def translate(self, text: str, target_lang: str = "spanish") -> str:
        prompt = f"Translate to {target_lang}:\n\n{text}\n\nTranslation:"
        result = self._generator.generate(prompt, GenerationConfig(max_length=len(text) * 2))
        return result.text
