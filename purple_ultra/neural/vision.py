"""Neural image recognition and description."""

from __future__ import annotations

import json
import time
from pathlib import Path
from dataclasses import dataclass, field
import numpy as np


@dataclass
class ImageResult:
    labels: list[dict]
    description: str = ""
    objects: list[dict] = field(default_factory=list)
    faces: list[dict] = field(default_factory=list)
    scene: str = ""
    confidence: float = 0.0


class NeuralImageRecognizer:
    def __init__(self, model_dir: str = "models/vision"):
        self._model_dir = Path(model_dir)
        self._model_dir.mkdir(parents=True, exist_ok=True)
        self._model = None
        self._feature_extractor = None
        self._labels: list[str] = []

    def _ensure_model(self):
        if self._model is None:
            try:
                from transformers import pipeline
                self._model = pipeline("image-classification", model="google/vit-base-patch16-224")
            except Exception:
                self._model = False

    def recognize(self, image_path: str) -> ImageResult:
        self._ensure_model()
        if not self._model:
            return self._fallback_recognize(image_path)
        try:
            results = self._model(image_path)
            labels = [{"label": r["label"], "score": r["score"]} for r in results[:5]]
            top_label = labels[0]["label"] if labels else "unknown"
            return ImageResult(
                labels=labels,
                description=f"I can see: {top_label}",
                scene=top_label,
                confidence=labels[0]["score"] if labels else 0,
            )
        except Exception:
            return self._fallback_recognize(image_path)

    def _fallback_recognize(self, image_path: str) -> ImageResult:
        try:
            from PIL import Image
            img = Image.open(image_path)
            width, height = img.size
            mode = img.mode
            labels = [
                {"label": "image", "score": 0.9},
                {"label": f"{width}x{height}", "score": 0.8},
                {"label": mode, "score": 0.7},
            ]
            return ImageResult(
                labels=labels,
                description=f"Image: {width}x{height}, {mode} mode",
                scene="image",
                confidence=0.7,
            )
        except Exception:
            return ImageResult(labels=[], description="Cannot analyze image")

    def describe(self, image_path: str) -> str:
        result = self.recognize(image_path)
        if result.labels:
            labels = ", ".join(f"{l['label']} ({l['score']:.0%})" for l in result.labels[:3])
            return f"I see: {labels}"
        return "I cannot identify what's in this image"

    def detect_objects(self, image_path: str) -> list[dict]:
        try:
            from PIL import Image
            img = Image.open(image_path)
            objects = []
            width, height = img.size
            pixels = np.array(img)
            if len(pixels.shape) == 3:
                avg_color = pixels.mean(axis=(0, 1))
                if avg_color[2] > avg_color[0] and avg_color[2] > avg_color[1]:
                    objects.append({"object": "blue region", "confidence": 0.5})
                if avg_color[0] > avg_color[1] and avg_color[0] > avg_color[2]:
                    objects.append({"object": "red region", "confidence": 0.5})
            return objects
        except Exception:
            return []

    def compare_images(self, image_path1: str, image_path2: str) -> dict:
        try:
            from PIL import Image
            img1 = Image.open(image_path1).resize((64, 64))
            img2 = Image.open(image_path2).resize((64, 64))
            arr1 = np.array(img1).flatten().astype(float)
            arr2 = np.array(img2).flatten().astype(float)
            similarity = float(np.dot(arr1, arr2) / (np.linalg.norm(arr1) * np.linalg.norm(arr2) + 1e-10))
            return {
                "similarity": similarity,
                "same_content": similarity > 0.9,
                "match_percentage": similarity * 100,
            }
        except Exception:
            return {"similarity": 0, "same_content": False, "match_percentage": 0}

    def extract_text(self, image_path: str) -> str:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img)
            return text.strip()
        except ImportError:
            return "OCR not available (install pytesseract)"
        except Exception:
            return ""

    def get_status(self) -> dict:
        return {
            "model_loaded": self._model is not None and self._model is not False,
            "model_dir": str(self._model_dir),
        }


class FaceRecognizer:
    def __init__(self, faces_dir: str = "memory/faces"):
        self._faces_dir = Path(faces_dir)
        self._faces_dir.mkdir(parents=True, exist_ok=True)
        self._known_faces: dict[str, list[list[float]]] = {}
        self._load()

    def _load(self):
        faces_file = self._faces_dir / "faces.json"
        if faces_file.exists():
            try:
                data = json.loads(faces_file.read_text())
                for name, encodings in data.items():
                    self._known_faces[name] = [np.array(e).tolist() for e in encodings]
            except Exception:
                pass

    def _save(self):
        try:
            data = {name: encs for name, encs in self._known_faces.items()}
            (self._faces_dir / "faces.json").write_text(json.dumps(data, indent=2))
        except Exception:
            pass

    def detect_faces(self, image_path: str) -> list[dict]:
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                return []
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            results = []
            for (x, y, w, h) in faces:
                face_img = img[y:y+h, x:x+w]
                encoding = self._encode_face(face_img)
                name = self._identify_face(encoding)
                results.append({
                    "name": name,
                    "location": {"x": int(x), "y": int(y), "w": int(w), "h": int(h)},
                    "confidence": 0.9,
                })
            return results
        except ImportError:
            return []
        except Exception:
            return []

    def _encode_face(self, face_img) -> list[float]:
        try:
            import cv2
            resized = cv2.resize(face_img, (100, 100))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            return (gray.flatten().astype(float) / 255.0).tolist()
        except Exception:
            return []

    def _identify_face(self, encoding: list[float]) -> str:
        if not encoding or not self._known_faces:
            return "unknown"
        best_name = "unknown"
        best_dist = float("inf")
        emb = np.array(encoding)
        for name, encodings in self._known_faces.items():
            for known in encodings:
                known_arr = np.array(known)
                if len(known_arr) == len(emb):
                    dist = np.linalg.norm(emb - known_arr)
                    if dist < best_dist:
                        best_dist = dist
                        best_name = name
        return best_name if best_dist < 0.4 else "unknown"

    def learn_face(self, name: str, image_path: str) -> str:
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                return "Cannot read image"
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            if len(faces) == 0:
                return "No face detected"
            x, y, w, h = faces[0]
            face_img = img[y:y+h, x:x+w]
            encoding = self._encode_face(face_img)
            if name not in self._known_faces:
                self._known_faces[name] = []
            self._known_faces[name].append(encoding)
            if len(self._known_faces[name]) > 5:
                self._known_faces[name] = self._known_faces[name][-5:]
            self._save()
            return f"Learned face: {name}"
        except ImportError:
            return "OpenCV not available"
        except Exception as e:
            return f"Error: {e}"

    def list_faces(self) -> list[str]:
        return list(self._known_faces.keys())
