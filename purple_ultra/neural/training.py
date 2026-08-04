"""Neural model training pipeline with export and LoRA support."""

from __future__ import annotations

import json
import time
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any


@dataclass
class TrainingConfig:
    base_model: str = "mlx-community/Qwen2.5-3B-Instruct-4bit"
    output_dir: str = "training/output"
    max_iterations: int = 200
    learning_rate: float = 1e-5
    batch_size: int = 4
    lora_rank: int = 8
    lora_alpha: int = 16
    lora_dropout: float = 0.05
    warmup_steps: int = 10
    save_steps: int = 50


@dataclass
class TrainingResult:
    success: bool
    output_dir: str = ""
    iterations: int = 0
    loss: float = 0.0
    duration: float = 0
    error: str = ""


class NeuralTrainingPipeline:
    def __init__(self, training_dir: str = "training"):
        self._training_dir = Path(training_dir)
        self._training_dir.mkdir(parents=True, exist_ok=True)
        self._output_dir = self._training_dir / "output"
        self._output_dir.mkdir(parents=True, exist_ok=True)
        self._data_dir = self._training_dir / "data"
        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._history: list[dict] = []

    def export_conversation_history(self, history_file: str = "memory/history.jsonl", output_file: str = None) -> int:
        if output_file is None:
            output_file = str(self._data_dir / "conversations.jsonl")
        history_path = Path(history_file)
        if not history_path.exists():
            return 0
        count = 0
        with open(history_path) as hf, open(output_file, "w") as of:
            for line in hf:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    user = entry.get("user", "")
                    assistant = entry.get("assistant", "")
                    if len(user) >= 10 and assistant:
                        row = {
                            "messages": [
                                {"role": "system", "content": "You are Purple Ultra, an advanced AI assistant."},
                                {"role": "user", "content": user},
                                {"role": "assistant", "content": assistant},
                            ]
                        }
                        of.write(json.dumps(row) + "\n")
                        count += 1
                except json.JSONDecodeError:
                    continue
        return count

    def add_training_example(self, user: str, assistant: str, output_file: str = None):
        if output_file is None:
            output_file = str(self._data_dir / "examples.jsonl")
        row = {
            "messages": [
                {"role": "system", "content": "You are Purple Ultra, an advanced AI assistant."},
                {"role": "user", "content": user},
                {"role": "assistant", "content": assistant},
            ]
        }
        with open(output_file, "a") as f:
            f.write(json.dumps(row) + "\n")

    def create_dataset(self, sources: list[str] = None) -> str:
        if sources is None:
            sources = [str(self._data_dir / "conversations.jsonl"), str(self._data_dir / "examples.jsonl")]
        output_file = str(self._data_dir / "dataset.jsonl")
        seen = set()
        count = 0
        with open(output_file, "w") as out:
            for source in sources:
                path = Path(source)
                if not path.exists():
                    continue
                with open(path) as f:
                    for line in f:
                        line = line.strip()
                        if not line:
                            continue
                        content_hash = hash(line)
                        if content_hash not in seen:
                            seen.add(content_hash)
                            out.write(line + "\n")
                            count += 1
        return output_file

    def train_mlx_lora(self, config: TrainingConfig = None) -> TrainingResult:
        config = config or TrainingConfig()
        dataset = self.create_dataset()
        start = time.time()
        cmd = [
            "python3", "-m", "mlx_lm.lora",
            "--model", config.base_model,
            "--train",
            "--data", dataset,
            "--output", str(self._output_dir),
            "--num-layers", "4",
            "--batch-size", str(config.batch_size),
            "--lr", str(config.learning_rate),
            "--iterations", str(config.max_iterations),
            "--lora-layers", str(config.lora_rank),
        ]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            duration = time.time() - start
            training_result = TrainingResult(
                success=result.returncode == 0,
                output_dir=str(self._output_dir),
                iterations=config.max_iterations,
                duration=duration,
                error=result.stderr if result.returncode != 0 else "",
            )
            self._history.append({
                "config": config.__dict__,
                "result": training_result.__dict__,
                "timestamp": time.time(),
            })
            return training_result
        except FileNotFoundError:
            return TrainingResult(success=False, error="mlx_lm not found. Install with: pip install mlx-lm")
        except subprocess.TimeoutExpired:
            return TrainingResult(success=False, error="Training timed out after 1 hour")

    def train_simple(self, data_file: str = None, epochs: int = 10) -> TrainingResult:
        if data_file is None:
            data_file = str(self._data_dir / "dataset.jsonl")
        path = Path(data_file)
        if not path.exists():
            return TrainingResult(success=False, error="No training data found")
        start = time.time()
        try:
            import torch
            from transformers import AutoModelForCausalLM, AutoTokenizer
            model_name = "gpt2"
            tokenizer = AutoTokenizer.from_pretrained(model_name)
            model = AutoModelForCausalLM.from_pretrained(model_name)
            total_loss = 0
            steps = 0
            with open(data_file) as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        messages = data.get("messages", [])
                        if len(messages) < 2:
                            continue
                        text = " ".join(m["content"] for m in messages)
                        inputs = tokenizer(text[:512], return_tensors="pt", truncation=True, max_length=512)
                        outputs = model(**inputs, labels=inputs["input_ids"])
                        total_loss += outputs.loss.item()
                        steps += 1
                    except Exception:
                        continue
            duration = time.time() - start
            avg_loss = total_loss / steps if steps > 0 else 0
            return TrainingResult(
                success=True,
                iterations=steps,
                loss=avg_loss,
                duration=duration,
            )
        except ImportError:
            return TrainingResult(success=False, error="PyTorch not installed")

    def list_checkpoints(self) -> list[dict]:
        checkpoints = []
        for item in self._output_dir.iterdir():
            if item.is_dir() and "adapter" in item.name:
                checkpoints.append({
                    "name": item.name,
                    "path": str(item),
                    "size": sum(f.stat().st_size for f in item.rglob("*") if f.is_file()),
                })
        return checkpoints

    def get_history(self) -> list[dict]:
        return self._history

    def get_status(self) -> dict:
        return {
            "training_dir": str(self._training_dir),
            "data_files": len(list(self._data_dir.glob("*.jsonl"))),
            "checkpoints": len(self.list_checkpoints()),
            "total_runs": len(self._history),
        }
