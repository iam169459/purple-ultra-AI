"""Camera access and face recognition system."""

from __future__ import annotations

import os
import time
import json
from pathlib import Path
import numpy as np


class CameraAccess:
    def __init__(self, memory_dir: str = "memory"):
        self._faces_dir = Path(memory_dir) / "faces"
        self._faces_dir.mkdir(parents=True, exist_ok=True)
        self._known_faces: dict[str, list[np.ndarray]] = {}
        self._load_faces()

    def _load_faces(self):
        faces_file = self._faces_dir / "faces.json"
        if faces_file.exists():
            try:
                data = json.loads(faces_file.read_text())
                for name, encodings in data.items():
                    self._known_faces[name] = [np.array(e) for e in encodings]
            except Exception:
                pass

    def _save_faces(self):
        faces_file = self._faces_dir / "faces.json"
        data = {name: [enc.tolist() for enc in encs] for name, encs in self._known_faces.items()}
        faces_file.write_text(json.dumps(data, indent=2))

    def take_photo(self) -> str:
        try:
            photo_dir = Path("data/photos")
            photo_dir.mkdir(parents=True, exist_ok=True)
            filename = photo_dir / f"photo_{int(time.time())}.jpg"
            import platform
            if platform.system() == "Darwin":
                import subprocess
                subprocess.run(["imagesnap", str(filename)], check=True, capture_output=True, timeout=10)
                return str(filename)
            return ""
        except Exception:
            return ""

    def detect_faces(self, image_path: str = None) -> list[dict]:
        try:
            import cv2
            if image_path:
                img = cv2.imread(image_path)
            else:
                cap = cv2.VideoCapture(0)
                ret, img = cap.read()
                cap.release()
                if not ret:
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
            return [{"name": "unknown", "location": None, "confidence": 0}]
        except Exception:
            return []

    def _encode_face(self, face_img) -> np.ndarray:
        try:
            resized = cv2.resize(face_img, (100, 100))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            return gray.flatten().astype(float) / 255.0
        except Exception:
            return np.array([])

    def _identify_face(self, encoding) -> str:
        if len(encoding) == 0:
            return "unknown"
        best_name = "unknown"
        best_dist = float("inf")
        for name, encodings in self._known_faces.items():
            for known_enc in encodings:
                if len(known_enc) == len(encoding):
                    dist = np.linalg.norm(encoding - known_enc)
                    if dist < best_dist:
                        best_dist = dist
                        best_name = name
        if best_dist < 0.4:
            return best_name
        return "unknown"

    def learn_face(self, name: str, image_path: str = None) -> str:
        try:
            import cv2
            if image_path:
                img = cv2.imread(image_path)
            else:
                cap = cv2.VideoCapture(0)
                ret, img = cap.read()
                cap.release()
                if not ret:
                    return "Failed to capture image"
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
            self._save_faces()
            return f"Learned face: {name}"
        except ImportError:
            return "OpenCV not available"
        except Exception as e:
            return f"Error: {e}"

    def forget_face(self, name: str) -> str:
        if name in self._known_faces:
            del self._known_faces[name]
            self._save_faces()
            return f"Forgot {name}"
        return f"No face found for {name}"

    def list_known_faces(self) -> list[str]:
        return list(self._known_faces.keys())
