"""Neural network core engine with advanced architectures, GPU acceleration, and model management."""

from __future__ import annotations

import os
import json
import time
import math
import threading
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Callable, Optional
from enum import Enum
from collections import defaultdict


class DeviceType(Enum):
    CPU = "cpu"
    CUDA = "cuda"
    MPS = "mps"
    UNKNOWN = "unknown"


@dataclass
class ModelInfo:
    name: str
    path: str
    model_type: str
    device: str
    parameters: int = 0
    memory_mb: float = 0
    loaded: bool = False
    load_time: float = 0
    last_used: float = 0
    version: str = "1.0"


@dataclass
class TensorShape:
    batch: int = 1
    seq_len: int = 1
    hidden: int = 768
    heads: int = 12

    def total_elements(self) -> int:
        return self.batch * self.seq_len * self.hidden

    def __repr__(self) -> str:
        return f"[{self.batch}, {self.seq_len}, {self.hidden}, {self.heads}]"


class DeviceManager:
    def __init__(self):
        self._device = DeviceType.CPU
        self._gpu_name = ""
        self._gpu_memory = 0
        self._compute_capabilities = {}
        self._detect_device()

    def _detect_device(self):
        try:
            import torch
            if torch.cuda.is_available():
                self._device = DeviceType.CUDA
                self._gpu_name = torch.cuda.get_device_name(0)
                self._gpu_memory = torch.cuda.get_device_properties(0).total_memory / (1024**2)
                self._compute_capabilities = {
                    "major": torch.cuda.get_device_capability(0)[0],
                    "minor": torch.cuda.get_device_capability(0)[1],
                    "multi_processor_count": torch.cuda.get_device_properties(0).multi_processor_count,
                }
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                self._device = DeviceType.MPS
                self._gpu_name = "Apple Silicon GPU"
                self._gpu_memory = 16000
                self._compute_capabilities = {"unified_memory": True, "neural_engine": True}
            else:
                self._device = DeviceType.CPU
        except ImportError:
            self._device = DeviceType.CPU

    @property
    def device(self) -> str:
        return self._device.value

    @property
    def gpu_name(self) -> str:
        return self._gpu_name

    @property
    def gpu_memory_mb(self) -> float:
        return self._gpu_memory

    @property
    def capabilities(self) -> dict:
        return self._compute_capabilities

    def get_torch_device(self):
        try:
            import torch
            if self._device == DeviceType.CUDA:
                return torch.device("cuda")
            elif self._device == DeviceType.MPS:
                return torch.device("mps")
            return torch.device("cpu")
        except ImportError:
            return None

    def get_optimal_dtype(self):
        try:
            import torch
            if self._device == DeviceType.CUDA:
                return torch.float16
            elif self._device == DeviceType.MPS:
                return torch.float16
            return torch.float32
        except ImportError:
            return None

    def get_max_batch_size(self, model_memory_mb: float) -> int:
        if self._gpu_memory > 0:
            available = self._gpu_memory * 0.8
            return max(1, int(available / model_memory_mb))
        return 1


class ModelRegistry:
    def __init__(self, models_dir: str = "models"):
        self._models_dir = Path(models_dir)
        self._models_dir.mkdir(parents=True, exist_ok=True)
        self._registry_file = self._models_dir / "registry.json"
        self._models: dict[str, ModelInfo] = {}
        self._loaded_models: dict[str, Any] = {}
        self._lock = threading.Lock()
        self._load_registry()

    def _load_registry(self):
        if self._registry_file.exists():
            try:
                data = json.loads(self._registry_file.read_text())
                for name, info in data.items():
                    self._models[name] = ModelInfo(**info)
            except Exception:
                pass

    def _save_registry(self):
        try:
            data = {}
            for name, info in self._models.items():
                data[name] = {
                    "name": info.name,
                    "path": info.path,
                    "model_type": info.model_type,
                    "device": info.device,
                    "parameters": info.parameters,
                    "memory_mb": info.memory_mb,
                    "loaded": False,
                    "load_time": info.load_time,
                    "last_used": info.last_used,
                    "version": info.version,
                }
            self._registry_file.write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def register_model(self, name: str, path: str, model_type: str, device: str = "cpu", parameters: int = 0):
        self._models[name] = ModelInfo(
            name=name, path=path, model_type=model_type,
            device=device, parameters=parameters,
        )
        self._save_registry()

    def load_model(self, name: str) -> Any:
        with self._lock:
            if name in self._loaded_models:
                self._loaded_models[name]["last_used"] = time.time()
                return self._loaded_models[name]["model"]
            info = self._models.get(name)
            if not info:
                return None
            try:
                model = self._load_model_from_path(info)
                if model:
                    self._loaded_models[name] = {
                        "model": model,
                        "info": info,
                        "last_used": time.time(),
                    }
                    info.loaded = True
                    info.load_time = time.time()
                    return model
            except Exception:
                pass
            return None

    def _load_model_from_path(self, info: ModelInfo):
        path = Path(info.path)
        if info.model_type == "sentence_transformer":
            from sentence_transformers import SentenceTransformer
            return SentenceTransformer(str(path))
        elif info.model_type == "whisper":
            from faster_whisper import WhisperModel
            return WhisperModel(str(path), device="cpu", compute_type="int8")
        elif info.model_type == "pytorch":
            import torch
            return torch.load(str(path), map_location="cpu")
        elif info.model_type == "onnx":
            try:
                import onnxruntime as ort
                return ort.InferenceSession(str(path))
            except ImportError:
                return None
        elif info.model_type == "huggingface":
            from transformers import AutoModel, AutoTokenizer
            tokenizer = AutoTokenizer.from_pretrained(str(path))
            model = AutoModel.from_pretrained(str(path))
            return {"model": model, "tokenizer": tokenizer}
        return None

    def unload_model(self, name: str) -> bool:
        with self._lock:
            if name in self._loaded_models:
                del self._loaded_models[name]
                if name in self._models:
                    self._models[name].loaded = False
                return True
            return False

    def get_model(self, name: str) -> Any:
        if name in self._loaded_models:
            return self._loaded_models[name]["model"]
        return self.load_model(name)

    def list_models(self) -> list[dict]:
        return [
            {
                "name": info.name,
                "type": info.model_type,
                "device": info.device,
                "loaded": info.loaded,
                "parameters": info.parameters,
                "memory_mb": info.memory_mb,
            }
            for info in self._models.values()
        ]

    def get_loaded_count(self) -> int:
        return len(self._loaded_models)

    def get_total_memory(self) -> float:
        return sum(m["info"].memory_mb for m in self._loaded_models.values())

    def unload_all(self):
        with self._lock:
            self._loaded_models.clear()
            for info in self._models.values():
                info.loaded = False


class NeuralEngine:
    def __init__(self, models_dir: str = "models"):
        self.device_manager = DeviceManager()
        self.model_registry = ModelRegistry(models_dir)
        self._inference_count = 0
        self._total_inference_time = 0.0
        self._attention_cache: dict[str, Any] = {}
        self._gradient_accumulator: dict[str, Any] = {}
        self._optimizer_states: dict[str, Any] = {}

    def get_status(self) -> dict:
        return {
            "device": self.device_manager.device,
            "gpu_name": self.device_manager.gpu_name,
            "gpu_memory_mb": self.device_manager.gpu_memory_mb,
            "capabilities": self.device_manager.capabilities,
            "loaded_models": self.model_registry.get_loaded_count(),
            "total_memory_mb": self.model_registry.get_total_memory(),
            "inference_count": self._inference_count,
            "avg_inference_ms": (self._total_inference_time / self._inference_count * 1000) if self._inference_count > 0 else 0,
            "attention_cache_size": len(self._attention_cache),
        }

    def track_inference(self, duration: float):
        self._inference_count += 1
        self._total_inference_time += duration

    def create_attention_cache(self, key: str, max_size: int = 1000):
        self._attention_cache[key] = {
            "keys": [],
            "values": [],
            "max_size": max_size,
            "access_count": 0,
            "last_access": time.time(),
        }

    def update_attention_cache(self, key: str, k: Any, v: Any):
        if key not in self._attention_cache:
            self.create_attention_cache(key)
        cache = self._attention_cache[key]
        cache["keys"].append(k)
        cache["values"].append(v)
        cache["access_count"] += 1
        cache["last_access"] = time.time()
        if len(cache["keys"]) > cache["max_size"]:
            cache["keys"].pop(0)
            cache["values"].pop(0)

    def get_attention_cache(self, key: str) -> dict:
        return self._attention_cache.get(key, {})

    def init_optimizer(self, model_name: str, lr: float = 0.001, weight_decay: float = 0.01):
        self._optimizer_states[model_name] = {
            "lr": lr,
            "weight_decay": weight_decay,
            "momentum": {},
            "velocity": {},
            "step": 0,
            "t": 0,
        }

    def adam_update(self, model_name: str, param_name: str, grad: Any, t: int = None):
        if model_name not in self._optimizer_states:
            self.init_optimizer(model_name)
        state = self._optimizer_states[model_name]
        if t is None:
            state["step"] += 1
            t = state["step"]
        state["t"] = t
        beta1, beta2, eps = 0.9, 0.999, 1e-8
        m = state["momentum"].get(param_name, 0)
        v = state["velocity"].get(param_name, 0)
        m = beta1 * m + (1 - beta1) * grad
        v = beta2 * v + (1 - beta2) * (grad ** 2)
        state["momentum"][param_name] = m
        state["velocity"][param_name] = v
        m_hat = m / (1 - beta1 ** t)
        v_hat = v / (1 - beta2 ** t)
        update = state["lr"] * m_hat / (math.sqrt(v_hat) + eps)
        return grad - update * state["weight_decay"]

    def get_optimizer_state(self, model_name: str) -> dict:
        return self._optimizer_states.get(model_name, {})
