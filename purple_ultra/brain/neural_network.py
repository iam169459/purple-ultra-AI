"""Neural Network - Pure Python implementation for Purple Ultra AI.

Multi-layer perceptron with:
- Forward/backward propagation
- Multiple activation functions
- Weight initialization strategies
- Learning rate scheduling
- Model persistence (save/load)
- No external dependencies - 100% pure Python
"""

import json
import math
import os
import random
from dataclasses import dataclass, field
from typing import Optional


# ═══════════════════════════════════════════════════════════════════════════
#  ACTIVATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

class Activation:
    """Collection of activation functions and their derivatives."""

    @staticmethod
    def sigmoid(x: float) -> float:
        x = max(-500.0, min(500.0, x))
        return 1.0 / (1.0 + math.exp(-x))

    @staticmethod
    def sigmoid_derivative(x: float) -> float:
        s = Activation.sigmoid(x)
        return s * (1.0 - s)

    @staticmethod
    def relu(x: float) -> float:
        return max(0.0, x)

    @staticmethod
    def relu_derivative(x: float) -> float:
        return 1.0 if x > 0 else 0.0

    @staticmethod
    def tanh(x: float) -> float:
        return math.tanh(x)

    @staticmethod
    def tanh_derivative(x: float) -> float:
        t = math.tanh(x)
        return 1.0 - t * t

    @staticmethod
    def leaky_relu(x: float, alpha: float = 0.01) -> float:
        return x if x > 0 else alpha * x

    @staticmethod
    def leaky_relu_derivative(x: float, alpha: float = 0.01) -> float:
        return 1.0 if x > 0 else alpha

    @staticmethod
    def swish(x: float) -> float:
        return x * Activation.sigmoid(x)

    @staticmethod
    def swish_derivative(x: float) -> float:
        s = Activation.sigmoid(x)
        return s + x * s * (1.0 - s)

    @staticmethod
    def gelu(x: float) -> float:
        return 0.5 * x * (1.0 + math.tanh(math.sqrt(2.0 / math.pi) * (x + 0.044715 * x**3)))

    @staticmethod
    def linear(x: float) -> float:
        return x

    @staticmethod
    def linear_derivative(x: float) -> float:
        return 1.0

    @staticmethod
    def softmax(values: list[float]) -> list[float]:
        max_v = max(values)
        exps = [math.exp(v - max_v) for v in values]
        total = sum(exps)
        return [e / total for e in exps]

    ACTIVATIONS = {
        "sigmoid": (sigmoid, sigmoid_derivative),
        "relu": (relu, relu_derivative),
        "tanh": (tanh, tanh_derivative),
        "leaky_relu": (leaky_relu, leaky_relu_derivative),
        "swish": (swish, swish_derivative),
        "gelu": (gelu, swish_derivative),
        "linear": (linear, linear_derivative),
    }


# ═══════════════════════════════════════════════════════════════════════════
#  WEIGHT INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════

class WeightInit:
    """Weight initialization strategies."""

    @staticmethod
    def random(fan_in: int, fan_out: int) -> list[list[float]]:
        scale = math.sqrt(2.0 / fan_in)
        return [[random.gauss(0, scale) for _ in range(fan_out)] for _ in range(fan_in)]

    @staticmethod
    def xavier(fan_in: int, fan_out: int) -> list[list[float]]:
        scale = math.sqrt(2.0 / (fan_in + fan_out))
        return [[random.gauss(0, scale) for _ in range(fan_out)] for _ in range(fan_in)]

    @staticmethod
    def he(fan_in: int, fan_out: int) -> list[list[float]]:
        scale = math.sqrt(2.0 / fan_in)
        return [[random.gauss(0, scale) for _ in range(fan_out)] for _ in range(fan_in)]

    @staticmethod
    def small_random(fan_in: int, fan_out: int) -> list[list[float]]:
        return [[random.uniform(-0.1, 0.1) for _ in range(fan_out)] for _ in range(fan_in)]


# ═══════════════════════════════════════════════════════════════════════════
#  PERCEPTRON LAYER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class PerceptronLayer:
    """Single neural network layer with weights, biases, and activation."""
    weights: list[list[float]]
    biases: list[float]
    activation_name: str = "relu"
    _activation: callable = field(default=None, repr=False)
    _activation_deriv: callable = field(default=None, repr=False)
    _last_input: list[float] = field(default_factory=list, repr=False)
    _last_z: list[float] = field(default_factory=list, repr=False)
    _last_a: list[float] = field(default_factory=list, repr=False)
    _velocity_w: list[list[float]] = field(default_factory=list, repr=False)
    _velocity_b: list[float] = field(default_factory=list, repr=False)

    def __post_init__(self):
        self._activation, self._activation_deriv = Activation.ACTIVATIONS.get(
            self.activation_name, Activation.ACTIVATIONS["relu"]
        )

    @property
    def input_size(self) -> int:
        return len(self.weights) if self.weights else 0

    @property
    def output_size(self) -> int:
        return len(self.biases) if self.biases else 0

    def forward(self, x: list[float]) -> list[float]:
        self._last_input = x[:]
        self._last_z = []
        self._last_a = []
        output = []
        for j in range(self.output_size):
            z = self.biases[j]
            for i in range(len(x)):
                z += x[i] * self.weights[i][j]
            self._last_z.append(z)
            a = self._activation(z)
            self._last_a.append(a)
            output.append(a)
        return output

    def backward(self, output_gradient: list[float], learning_rate: float) -> list[float]:
        input_gradient = [0.0] * self.input_size
        dw = [[0.0] * self.output_size for _ in range(self.input_size)]
        db = [0.0] * self.output_size

        for j in range(self.output_size):
            dz = output_gradient[j] * self._activation_deriv(self._last_z[j])
            db[j] = dz
            for i in range(self.input_size):
                dw[i][j] = self._last_input[i] * dz
                input_gradient[i] += self.weights[i][j] * dz

        if not self._velocity_w:
            self._velocity_w = [[0.0] * self.output_size for _ in range(self.input_size)]
            self._velocity_b = [0.0] * self.output_size

        momentum = 0.9
        for i in range(self.input_size):
            for j in range(self.output_size):
                self._velocity_w[i][j] = momentum * self._velocity_w[i][j] - learning_rate * dw[i][j]
                self.weights[i][j] += self._velocity_w[i][j]
        for j in range(self.output_size):
            self._velocity_b[j] = momentum * self._velocity_b[j] - learning_rate * db[j]
            self.biases[j] += self._velocity_b[j]

        return input_gradient


# ═══════════════════════════════════════════════════════════════════════════
#  MULTI-LAYER PERCEPTRON
# ═══════════════════════════════════════════════════════════════════════════

class MultiLayerPerceptron:
    """Complete neural network with multiple layers, training, and persistence."""

    def __init__(self, layer_sizes: list[int], activations: list[str] | None = None,
                 learning_rate: float = 0.01, init_method: str = "he"):
        if len(layer_sizes) < 2:
            raise ValueError("Need at least input and output layers")

        self.layer_sizes = layer_sizes
        self.learning_rate = learning_rate
        self.init_method = init_method

        if activations is None:
            activations = ["relu"] * (len(layer_sizes) - 2) + ["sigmoid"]
        elif len(activations) != len(layer_sizes) - 1:
            raise ValueError(f"Need {len(layer_sizes)-1} activations, got {len(activations)}")

        self.activations = activations
        self.layers: list[PerceptronLayer] = []
        self._training_history: list[dict] = []
        self._total_forward_passes = 0
        self._total_backward_passes = 0

        init_fn = getattr(WeightInit, init_method, WeightInit.he)
        for i in range(len(layer_sizes) - 1):
            w = init_fn(layer_sizes[i], layer_sizes[i + 1])
            b = [0.0] * layer_sizes[i + 1]
            layer = PerceptronLayer(weights=w, biases=b, activation_name=activations[i])
            self.layers.append(layer)

    @property
    def total_params(self) -> int:
        total = 0
        for layer in self.layers:
            total += layer.input_size * layer.output_size + layer.output_size
        return total

    def forward(self, x: list[float]) -> list[float]:
        self._total_forward_passes += 1
        current = x
        for layer in self.layers:
            current = layer.forward(current)
        return current

    def backward(self, loss_gradient: list[float]) -> None:
        self._total_backward_passes += 1
        grad = loss_gradient
        for layer in reversed(self.layers):
            grad = layer.backward(grad, self.learning_rate)

    def train_step(self, x: list[float], y: list[float]) -> float:
        output = self.forward(x)
        loss = sum((o - t) ** 2 for o, t in zip(output, y)) / len(y)
        gradient = [(2.0 / len(y)) * (o - t) for o, t in zip(output, y)]
        self.backward(gradient)
        return loss

    def train(self, X: list[list[float]], y: list[list[float]], epochs: int = 100,
              batch_size: int = 32, verbose: bool = False) -> list[dict]:
        history = []
        n = len(X)

        for epoch in range(epochs):
            indices = list(range(n))
            random.shuffle(indices)
            epoch_loss = 0.0
            batches = 0

            for start in range(0, n, batch_size):
                batch_idx = indices[start:start + batch_size]
                batch_loss = 0.0
                gradients_sum = [0.0] * self.layers[-1].output_size

                for idx in batch_idx:
                    output = self.forward(X[idx])
                    loss = sum((o - t) ** 2 for o, t in zip(output, y[idx])) / len(y[idx])
                    batch_loss += loss
                    gradient = [(2.0 / len(y[idx])) * (o - t) for o, t in zip(output, y[idx])]
                    for k in range(len(gradients_sum)):
                        gradients_sum[k] += gradient[k]
                    self.backward(gradient)
                    batches += 1

                avg_loss = batch_loss / len(batch_idx)
                epoch_loss += avg_loss

            avg_epoch_loss = epoch_loss / max(1, n // batch_size)
            record = {"epoch": epoch + 1, "loss": avg_epoch_loss, "lr": self.learning_rate}
            history.append(record)
            self._training_history.append(record)

            if verbose and (epoch + 1) % max(1, epochs // 10) == 0:
                pass

        return history

    def predict(self, x: list[float]) -> list[float]:
        return self.forward(x)

    def predict_class(self, x: list[float]) -> int:
        output = self.forward(x)
        return output.index(max(output))

    def accuracy(self, X: list[list[float]], y: list[int]) -> float:
        correct = 0
        for x, label in zip(X, y):
            if self.predict_class(x) == label:
                correct += 1
        return correct / len(X) if X else 0.0

    def save(self, filepath: str) -> None:
        data = {
            "layer_sizes": self.layer_sizes,
            "activations": self.activations,
            "learning_rate": self.learning_rate,
            "init_method": self.init_method,
            "training_history": self._training_history[-100:],
            "total_forward_passes": self._total_forward_passes,
            "total_backward_passes": self._total_backward_passes,
            "layers": [
                {
                    "weights": layer.weights,
                    "biases": layer.biases,
                    "activation_name": layer.activation_name,
                }
                for layer in self.layers
            ],
        }
        os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load(cls, filepath: str) -> "MultiLayerPerceptron":
        with open(filepath) as f:
            data = json.load(f)

        nn = cls(
            layer_sizes=data["layer_sizes"],
            activations=data["activations"],
            learning_rate=data.get("learning_rate", 0.01),
            init_method=data.get("init_method", "he"),
        )
        nn._training_history = data.get("training_history", [])
        nn._total_forward_passes = data.get("total_forward_passes", 0)
        nn._total_backward_passes = data.get("total_backward_passes", 0)

        for i, layer_data in enumerate(data["layers"]):
            nn.layers[i].weights = layer_data["weights"]
            nn.layers[i].biases = layer_data["biases"]
            nn.layers[i].activation_name = layer_data.get("activation_name", "relu")
            nn.layers[i]._activation, nn.layers[i]._activation_deriv = Activation.ACTIVATIONS.get(
                nn.layers[i].activation_name, Activation.ACTIVATIONS["relu"]
            )

        return nn

    def get_info(self) -> dict:
        return {
            "layers": len(self.layers),
            "layer_sizes": self.layer_sizes,
            "total_params": self.total_params,
            "activations": self.activations,
            "learning_rate": self.learning_rate,
            "forward_passes": self._total_forward_passes,
            "backward_passes": self._total_backward_passes,
            "training_epochs": len(self._training_history),
        }


# ═══════════════════════════════════════════════════════════════════════════
#  BRAIN NEURAL NETWORK
# ═══════════════════════════════════════════════════════════════════════════

class BrainNeuralNetwork:
    """Specialized neural network for brain operations:
    - Intent classification
    - Response quality prediction
    - Pattern recognition
    - Knowledge association
    """

    INTENT_LABELS = [
        "greeting", "factual", "how_to", "why", "code", "math",
        "analysis", "explain", "create", "plan", "reflect", "empathy",
        "positive", "help", "self_ref", "time", "list", "advice",
    ]

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "neural"
        )
        os.makedirs(self.data_dir, exist_ok=True)

        self._intent_nn: MultiLayerPerceptron | None = None
        self._quality_nn: MultiLayerPerceptron | None = None
        self._pattern_nn: MultiLayerPerceptron | None = None
        self._word_to_idx: dict[str, int] = {}
        self._max_vocab = 500
        self._intent_training_data: list[tuple[list[float], list[float]]] = []
        self._quality_training_data: list[tuple[list[float], float]] = []
        self._pattern_cache: dict[str, list[float]] = {}
        self._total_trains = 0
        self._total_predictions = 0

        self._init_networks()
        self._load()

    def _text_to_features(self, text: str) -> list[float]:
        words = text.lower().split()
        features = [0.0] * self._max_vocab
        for word in words:
            if word not in self._word_to_idx:
                if len(self._word_to_idx) < self._max_vocab:
                    self._word_to_idx[word] = len(self._word_to_idx)
            if word in self._word_to_idx:
                idx = self._word_to_idx[word]
                features[idx] = 1.0
        return features

    def _init_networks(self):
        self._intent_nn = MultiLayerPerceptron(
            layer_sizes=[self._max_vocab, 64, 32, len(self.INTENT_LABELS)],
            activations=["relu", "relu", "softmax"],
            learning_rate=0.005,
        )
        self._quality_nn = MultiLayerPerceptron(
            layer_sizes=[self._max_vocab + 10, 32, 16, 1],
            activations=["relu", "relu", "sigmoid"],
            learning_rate=0.005,
        )
        self._pattern_nn = MultiLayerPerceptron(
            layer_sizes=[self._max_vocab, 48, 24, 8],
            activations=["relu", "relu", "linear"],
            learning_rate=0.003,
        )

    def classify_intent(self, text: str) -> tuple[str, float]:
        self._total_predictions += 1
        features = self._text_to_features(text)
        output = self._intent_nn.predict(features)
        max_val = max(output)
        max_idx = output.index(max_val)
        label = self.INTENT_LABELS[max_idx] if max_idx < len(self.INTENT_LABELS) else "unknown"
        return label, max_val

    def predict_quality(self, text: str, response: str, context: float = 0.5) -> float:
        self._total_predictions += 1
        text_features = self._text_to_features(text)
        resp_features = self._text_to_features(response)[:10]
        combined = text_features + resp_features
        output = self._quality_nn.predict(combined)
        return output[0]

    def encode_pattern(self, text: str) -> list[float]:
        features = self._text_to_features(text)
        output = self._pattern_nn.predict(features)
        return output

    def similarity(self, text1: str, text2: str) -> float:
        p1 = self.encode_pattern(text1)
        p2 = self.encode_pattern(text2)
        dot = sum(a * b for a, b in zip(p1, p2))
        norm1 = math.sqrt(sum(a * a for a in p1)) or 1.0
        norm2 = math.sqrt(sum(b * b for b in p2)) or 1.0
        return max(0.0, min(1.0, dot / (norm1 * norm2)))

    def train_intent(self, text: str, intent_label: str) -> bool:
        if intent_label not in self.INTENT_LABELS:
            return False
        features = self._text_to_features(text)
        target = [0.0] * len(self.INTENT_LABELS)
        target[self.INTENT_LABELS.index(intent_label)] = 1.0
        self._intent_nn.train_step(features, target)
        self._intent_training_data.append((features, target))
        self._total_trains += 1
        return True

    def train_quality(self, text: str, response: str, score: float) -> bool:
        text_features = self._text_to_features(text)
        resp_features = self._text_to_features(response)[:10]
        combined = text_features + resp_features
        self._quality_nn.train_step(combined, [max(0.0, min(1.0, score))])
        self._quality_training_data.append((combined, score))
        self._total_trains += 1
        return True

    def train_pattern(self, text: str) -> list[float]:
        features = self._text_to_features(text)
        self._pattern_nn.train_step(features, features[:8])
        self._total_trains += 1
        return self._pattern_nn.predict(features)

    def batch_train_intent(self, data: list[tuple[str, str]], epochs: int = 5) -> float:
        X = [self._text_to_features(t) for t, _ in data]
        y = []
        for _, label in data:
            target = [0.0] * len(self.INTENT_LABELS)
            if label in self.INTENT_LABELS:
                target[self.INTENT_LABELS.index(label)] = 1.0
            y.append(target)
        history = self._intent_nn.train(X, y, epochs=epochs, batch_size=16)
        return history[-1]["loss"] if history else 0.0

    def batch_train_quality(self, data: list[tuple[str, str, float]], epochs: int = 5) -> float:
        X = []
        y = []
        for text, resp, score in data:
            text_f = self._text_to_features(text)
            resp_f = self._text_to_features(resp)[:10]
            X.append(text_f + resp_f)
            y.append([max(0.0, min(1.0, score))])
        history = self._quality_nn.train(X, y, epochs=epochs, batch_size=16)
        return history[-1]["loss"] if history else 0.0

    def save(self) -> None:
        self._intent_nn.save(os.path.join(self.data_dir, "intent_nn.json"))
        self._quality_nn.save(os.path.join(self.data_dir, "quality_nn.json"))
        self._pattern_nn.save(os.path.join(self.data_dir, "pattern_nn.json"))
        meta = {
            "word_to_idx": self._word_to_idx,
            "total_trains": self._total_trains,
            "total_predictions": self._total_predictions,
        }
        with open(os.path.join(self.data_dir, "nn_meta.json"), "w") as f:
            json.dump(meta, f, indent=2)

    def _load(self) -> None:
        try:
            intent_path = os.path.join(self.data_dir, "intent_nn.json")
            if os.path.exists(intent_path):
                self._intent_nn = MultiLayerPerceptron.load(intent_path)
        except Exception:
            pass
        try:
            quality_path = os.path.join(self.data_dir, "quality_nn.json")
            if os.path.exists(quality_path):
                self._quality_nn = MultiLayerPerceptron.load(quality_path)
        except Exception:
            pass
        try:
            pattern_path = os.path.join(self.data_dir, "pattern_nn.json")
            if os.path.exists(pattern_path):
                self._pattern_nn = MultiLayerPerceptron.load(pattern_path)
        except Exception:
            pass
        try:
            meta_path = os.path.join(self.data_dir, "nn_meta.json")
            if os.path.exists(meta_path):
                with open(meta_path) as f:
                    meta = json.load(f)
                self._word_to_idx = meta.get("word_to_idx", {})
                self._total_trains = meta.get("total_trains", 0)
                self._total_predictions = meta.get("total_predictions", 0)
        except Exception:
            pass

    def get_info(self) -> dict:
        return {
            "vocab_size": len(self._word_to_idx),
            "total_trains": self._total_trains,
            "total_predictions": self._total_predictions,
            "intent_network": self._intent_nn.get_info(),
            "quality_network": self._quality_nn.get_info(),
            "pattern_network": self._pattern_nn.get_info(),
        }
