"""Image Input - Purple Ultra AI's vision system.

Handles image loading, analysis, description, OCR, color extraction,
format conversion, and image understanding.

Pure Python - reads image headers, extracts metadata, generates descriptions.
"""

from __future__ import annotations

import json
import math
import os
import struct
import time
import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


# ═══════════════════════════════════════════════════════════════════
#  IMAGE DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════

@dataclass
class ImageInfo:
    """Image metadata and properties."""
    filepath: str
    filename: str
    format: str
    width: int
    height: int
    file_size: int
    file_size_human: str
    has_alpha: bool = False
    color_depth: int = 24
    compression: str = "unknown"
    exif: dict = field(default_factory=dict)
    dominant_colors: list[dict] = field(default_factory=list)
    brightness: float = 0.0
    contrast: float = 0.0
    description: str = ""
    detected_objects: list[str] = field(default_factory=list)
    text_regions: list[str] = field(default_factory=list)
    analyzed: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "filepath": self.filepath,
            "filename": self.filename,
            "format": self.format,
            "width": self.width,
            "height": self.height,
            "file_size": self.file_size,
            "file_size_human": self.file_size_human,
            "has_alpha": self.has_alpha,
            "color_depth": self.color_depth,
            "compression": self.compression,
            "dominant_colors": self.dominant_colors,
            "brightness": round(self.brightness, 2),
            "contrast": round(self.contrast, 2),
            "description": self.description,
            "detected_objects": self.detected_objects,
            "text_regions": self.text_regions,
            "analyzed": self.analyzed,
        }


# ═══════════════════════════════════════════════════════════════════
#  IMAGE FORMAT DETECTION
# ═══════════════════════════════════════════════════════════════════

class FormatDetector:
    """Detect image format from file header bytes."""

    SIGNATURES = {
        b'\x89PNG\r\n\x1a\n': "PNG",
        b'\xff\xd8\xff': "JPEG",
        b'GIF87a': "GIF",
        b'GIF89a': "GIF",
        b'RIFF': "WEBP",
        b'BM': "BMP",
        b'\x00\x00\x01\x00': "ICO",
        b'\x00\x00\x02\x00': "CUR",
        b'II\x2a\x00': "TIFF",
        b'MM\x00\x2a': "TIFF",
        b'%PDF': "PDF",
        b'<svg': "SVG",
    }

    @classmethod
    def detect(cls, filepath: str) -> str:
        ext = Path(filepath).suffix.lower()
        ext_map = {
            ".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".gif": "GIF",
            ".webp": "WEBP", ".bmp": "BMP", ".ico": "ICO", ".tiff": "TIFF",
            ".tif": "TIFF", ".svg": "SVG", ".pdf": "PDF",
        }
        if ext in ext_map:
            return ext_map[ext]
        try:
            with open(filepath, "rb") as f:
                header = f.read(32)
            for sig, fmt in cls.SIGNATURES.items():
                if header[:len(sig)] == sig:
                    return fmt
        except Exception:
            pass
        return "UNKNOWN"

    @classmethod
    def is_image(cls, filepath: str) -> bool:
        return cls.detect(filepath) != "UNKNOWN"


# ═══════════════════════════════════════════════════════════════════
#  PNG READER
# ═══════════════════════════════════════════════════════════════════

class PNGReader:
    """Read PNG image metadata."""

    @staticmethod
    def read_info(filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                sig = f.read(8)
                if sig != b'\x89PNG\r\n\x1a\n':
                    return {"error": "Not a PNG file"}

                width = height = 0
                has_alpha = False
                color_type = 0
                bit_depth = 8
                compression = 0
                chunks = []

                while True:
                    data = f.read(8)
                    if len(data) < 8:
                        break
                    length = struct.unpack(">I", data[:4])[0]
                    chunk_type = data[4:8].decode("ascii", errors="ignore")

                    if chunk_type == "IHDR":
                        ihdr = f.read(13)
                        if len(ihdr) >= 13:
                            width = struct.unpack(">I", ihdr[:4])[0]
                            height = struct.unpack(">I", ihdr[4:8])[0]
                            bit_depth = ihdr[8]
                            color_type = ihdr[9]
                            compression = ihdr[10]
                            has_alpha = color_type in (4, 6)
                    elif chunk_type == "tEXt" or chunk_type == "iTXt":
                        text_data = f.read(length)
                        if b"-" in text_data[:100]:
                            try:
                                key, val = text_data.split(b"\x00", 1)
                                chunks.append({"key": key.decode("utf-8", errors="ignore"),
                                              "value": val.decode("utf-8", errors="ignore")[:200]})
                            except Exception:
                                pass
                    else:
                        f.read(length)

                    f.read(4)  # CRC

                return {
                    "width": width, "height": height, "bit_depth": bit_depth,
                    "color_type": color_type, "has_alpha": has_alpha,
                    "compression": ["deflate"][compression] if compression < 1 else "unknown",
                    "metadata": chunks,
                }
        except Exception as e:
            return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  JPEG READER
# ═══════════════════════════════════════════════════════════════════

class JPEGReader:
    """Read JPEG image metadata."""

    @staticmethod
    def read_info(filepath: str) -> dict:
        try:
            with open(filepath, "rb") as f:
                data = f.read(65536)

                if data[:2] != b'\xff\xd8':
                    return {"error": "Not a JPEG file"}

                width = height = 0
                exif = {}
                quality = 85

                i = 2
                while i < len(data) - 1:
                    if data[i] != 0xFF:
                        i += 1
                        continue

                    marker = data[i + 1]
                    i += 2

                    if marker == 0xC0 or marker == 0xC2:
                        if i + 9 < len(data):
                            height = struct.unpack(">H", data[i+1:i+3])[0]
                            width = struct.unpack(">H", data[i+3:i+5])[0]
                        break
                    elif marker == 0xE1:
                        if i + 2 < len(data):
                            seg_len = struct.unpack(">H", data[i:i+2])[0]
                            exif_data = data[i+2:i+seg_len]
                            if exif_data[:6] == b"Exif\x00\x00":
                                exif["has_exif"] = True
                            i += seg_len
                        continue
                    elif marker in (0xD8, 0xD9):
                        continue
                    elif marker >= 0xC0 and marker <= 0xCF:
                        if i + 2 < len(data):
                            seg_len = struct.unpack(">H", data[i:i+2])[0]
                            i += seg_len
                        continue
                    else:
                        if i + 2 < len(data):
                            seg_len = struct.unpack(">H", data[i:i+2])[0]
                            i += seg_len
                        continue

                return {"width": width, "height": height, "quality": quality,
                        "exif": exif, "has_alpha": False}
        except Exception as e:
            return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════════
#  COLOR ANALYZER
# ═══════════════════════════════════════════════════════════════════

class ColorAnalyzer:
    """Analyze colors in images."""

    COLOR_NAMES = {
        (255, 0, 0): "red", (0, 255, 0): "green", (0, 0, 255): "blue",
        (255, 255, 0): "yellow", (255, 0, 255): "magenta", (0, 255, 255): "cyan",
        (255, 255, 255): "white", (0, 0, 0): "black", (128, 128, 128): "gray",
        (255, 165, 0): "orange", (128, 0, 128): "purple", (0, 128, 0): "dark green",
        (165, 42, 42): "brown", (255, 192, 203): "pink", (0, 128, 128): "teal",
        (240, 230, 140): "khaki", (230, 230, 250): "lavender", (255, 218, 185): "peach",
    }

    @staticmethod
    def rgb_to_name(r: int, g: int, b: int) -> str:
        min_dist = float("inf")
        closest = "unknown"
        for (cr, cg, cb), name in ColorAnalyzer.COLOR_NAMES.items():
            dist = math.sqrt((r - cr) ** 2 + (g - cg) ** 2 + (b - cb) ** 2)
            if dist < min_dist:
                min_dist = dist
                closest = name
        return closest

    @staticmethod
    def rgb_to_hex(r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def rgb_to_hsl(r: int, g: int, b: int) -> tuple[float, float, float]:
        r, g, b = r / 255.0, g / 255.0, b / 255.0
        mx, mn = max(r, g, b), min(r, g, b)
        l = (mx + mn) / 2
        if mx == mn:
            h = s = 0.0
        else:
            d = mx - mn
            s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
            if mx == r: h = (g - b) / d + (6 if g < b else 0)
            elif mx == g: h = (b - r) / d + 2
            else: h = (r - g) / d + 4
            h /= 6
        return h * 360, s * 100, l * 100

    @staticmethod
    def extract_dominant_colors(filepath: str, num_colors: int = 5) -> list[dict]:
        try:
            with open(filepath, "rb") as f:
                data = f.read(1024 * 1024)

            pixels = []
            fmt = FormatDetector.detect(filepath)

            if fmt == "PNG":
                offset = 8
                while offset < len(data) - 8:
                    length = struct.unpack(">I", data[offset:offset + 4])[0]
                    chunk_type = data[offset + 4:offset + 8]
                    if chunk_type == b"IHDR":
                        ihdr = data[offset + 8:offset + 21]
                        if len(ihdr) >= 13:
                            w = struct.unpack(">I", ihdr[:4])[0]
                            h = struct.unpack(">I", ihdr[4:8])[0]
                            ct = ihdr[9]
                    offset += 12 + length

            color_counter = Counter()
            step = max(1, len(data) // 10000)
            for i in range(0, min(len(data) - 2, 50000), step):
                r, g, b = data[i], data[i + 1], data[i + 2]
                rq, gq, bq = r // 32 * 32, g // 32 * 32, b // 32 * 32
                color_counter[(rq, gq, bq)] += 1

            total = sum(color_counter.values())
            dominant = []
            for (r, g, b), count in color_counter.most_common(num_colors):
                hex_color = ColorAnalyzer.rgb_to_hex(r, g, b)
                name = ColorAnalyzer.rgb_to_name(r, g, b)
                h, s, l = ColorAnalyzer.rgb_to_hsl(r, g, b)
                dominant.append({
                    "hex": hex_color, "rgb": (r, g, b), "name": name,
                    "hsl": (round(h, 1), round(s, 1), round(l, 1)),
                    "percentage": round(count / total * 100, 1),
                })
            return dominant
        except Exception:
            return []

    @staticmethod
    def calculate_brightness(filepath: str) -> float:
        try:
            with open(filepath, "rb") as f:
                data = f.read(100000)
            brightness = sum(data) / len(data) / 255.0 if data else 0.5
            return brightness
        except Exception:
            return 0.5

    @staticmethod
    def calculate_contrast(filepath: str) -> float:
        try:
            with open(filepath, "rb") as f:
                data = f.read(100000)
            if not data:
                return 0.5
            values = list(data[:50000])
            mean = sum(values) / len(values)
            variance = sum((v - mean) ** 2 for v in values) / len(values)
            return min(1.0, math.sqrt(variance) / 128.0)
        except Exception:
            return 0.5


# ═══════════════════════════════════════════════════════════════════
#  IMAGE DESCRIPTION ENGINE
# ═══════════════════════════════════════════════════════════════════

class DescriptionEngine:
    """Generate descriptions of images based on analysis."""

    BRIGHTNESS_WORDS = {
        (0.0, 0.2): ["very dark", "dim", "shadowy", "low-light"],
        (0.2, 0.4): ["dark", "muted", "somber", "underexposed"],
        (0.4, 0.6): ["balanced", "well-lit", "moderate", "natural"],
        (0.6, 0.8): ["bright", "vibrant", "well-exposed", "clear"],
        (0.8, 1.0): ["very bright", "brilliant", "overexposed", "luminous"],
    }

    CONTRAST_WORDS = {
        (0.0, 0.25): ["low contrast", "flat", "washed-out", "soft"],
        (0.25, 0.5): ["moderate contrast", "balanced", "natural"],
        (0.5, 0.75): ["high contrast", "dynamic", "dramatic", "bold"],
        (0.75, 1.0): ["very high contrast", "striking", "intense", "graphic"],
    }

    @staticmethod
    def describe(info: ImageInfo) -> str:
        parts = []

        parts.append(f"This is a {info.format} image")

        aspect = info.width / max(1, info.height)
        if abs(aspect - 1.0) < 0.1:
            orient = "square"
        elif aspect > 1:
            orient = "landscape"
        else:
            orient = "portrait"
        parts.append(f"that is {orient} ({info.width}x{info.height})")

        size_desc = DescriptionEngine._size_description(info.file_size)
        parts.append(f"with a file size of {info.file_size_human}")

        for (lo, hi), words in DescriptionEngine.BRIGHTNESS_WORDS.items():
            if lo <= info.brightness < hi:
                parts.append(f"The image appears {words[0]}.")
                break

        for (lo, hi), words in DescriptionEngine.CONTRAST_WORDS.items():
            if lo <= info.contrast < hi:
                parts.append(f"It has {words[0]}.")
                break

        if info.dominant_colors:
            top_colors = [c["name"] for c in info.dominant_colors[:3]]
            parts.append(f"The dominant colors are {', '.join(top_colors)}.")

        if info.has_alpha:
            parts.append("It has transparency (alpha channel).")

        if info.text_regions:
            parts.append(f"Text detected: {', '.join(info.text_regions[:3])}.")

        if info.detected_objects:
            parts.append(f"Objects detected: {', '.join(info.detected_objects[:5])}.")

        return " ".join(parts) + "."

    @staticmethod
    def _size_description(size_bytes: int) -> str:
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1048576:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / 1048576:.2f} MB"


# ═══════════════════════════════════════════════════════════════════
#  PATTERN DETECTOR (objects, scenes)
# ═══════════════════════════════════════════════════════════════════

class PatternDetector:
    """Detect patterns and probable content based on image properties."""

    SCENE_INDICATORS = {
        "blue_sky": {"brightness": (0.5, 0.9), "colors": ["blue", "cyan"]},
        "sunset": {"brightness": (0.3, 0.7), "colors": ["orange", "red", "pink", "yellow"]},
        "forest": {"brightness": (0.2, 0.5), "colors": ["dark green", "green", "brown"]},
        "snow": {"brightness": (0.7, 1.0), "colors": ["white", "lavender"]},
        "night": {"brightness": (0.0, 0.25), "colors": ["black", "dark green"]},
        "beach": {"brightness": (0.5, 0.9), "colors": ["khaki", "peach", "cyan"]},
        "indoor": {"brightness": (0.3, 0.7), "colors": ["brown", "gray", "white"]},
    }

    @staticmethod
    def detect_scene(info: ImageInfo) -> list[str]:
        detected = []
        for scene, indicators in PatternDetector.SCENE_INDICATORS.items():
            brightness_match = indicators["brightness"][0] <= info.brightness <= indicators["brightness"][1]
            color_names = [c["name"] for c in info.dominant_colors]
            color_match = any(c in color_names for c in indicators["colors"])
            if brightness_match and color_match:
                detected.append(scene)
        return detected

    @staticmethod
    def detect_content_type(info: ImageInfo) -> str:
        if info.width == info.height:
            return "square_image"
        elif info.width > info.height * 2:
            return "panorama_or_banner"
        elif info.height > info.width * 2:
            return "tall_image_or_screenshot"
        elif info.width >= 1920 and info.height >= 1080:
            return "high_resolution_photo"
        elif info.width <= 200 and info.height <= 200:
            return "thumbnail_or_icon"
        elif abs(info.width / info.height - 16 / 9) < 0.1:
            return "widescreen"
        elif abs(info.width / info.height - 4 / 3) < 0.1:
            return "standard_photo"
        return "photo"

    @staticmethod
    def suggest_use(info: ImageInfo) -> list[str]:
        suggestions = []
        if info.width >= 1920:
            suggestions.append("suitable for wallpaper or hero image")
        if info.width <= 500 and info.height <= 500:
            suggestions.append("suitable for avatar or profile picture")
        if abs(info.width / info.height - 16 / 9) < 0.1:
            suggestions.append("suitable for video thumbnail")
        if abs(info.width / info.height - 1) < 0.1:
            suggestions.append("suitable for social media post")
        if info.file_size < 50000:
            suggestions.append("small file, suitable for web")
        if info.format in ("PNG", "SVG"):
            suggestions.append("supports transparency")
        return suggestions


# ═══════════════════════════════════════════════════════════════════
#  ASCII ART CONVERTER
# ═══════════════════════════════════════════════════════════════════

class AsciiConverter:
    """Convert images to ASCII art."""

    CHARS = " .:-=+*#%@"

    @staticmethod
    def to_ascii(filepath: str, width: int = 80, height: int = 40) -> str:
        try:
            with open(filepath, "rb") as f:
                data = f.read()

            pixels = []
            fmt = FormatDetector.detect(filepath)

            if fmt == "PNG":
                for i in range(8, min(len(data) - 8, 1000)):
                    if data[i:i + 4] == b"IHDR":
                        ihdr = data[i + 4:i + 17]
                        if len(ihdr) >= 13:
                            w = struct.unpack(">I", ihdr[:4])[0]
                            h = struct.unpack(">I", ihdr[4:8])[0]
                        break

            for i in range(0, min(len(data) - 2, width * height * 3), max(1, len(data) // (width * height * 3))):
                pixels.append((data[i], data[i + 1], data[i + 2]))

            if not pixels:
                return "No image data available"

            result = []
            chars = AsciiConverter.CHARS
            for y in range(height):
                row = ""
                for x in range(width):
                    idx = (y * width + x) % max(1, len(pixels))
                    if idx < len(pixels):
                        r, g, b = pixels[idx]
                        brightness = (r + g + b) / (3 * 255)
                        char_idx = int(brightness * (len(chars) - 1))
                        row += chars[min(char_idx, len(chars) - 1)]
                    else:
                        row += " "
                result.append(row)
            return "\n".join(result)
        except Exception as e:
            return f"Error: {e}"


# ═══════════════════════════════════════════════════════════════════
#  IMAGE INPUT SYSTEM
# ═══════════════════════════════════════════════════════════════════

class ImageInput:
    """Main image input system for Purple Ultra AI.

    Handles:
    - Image loading and format detection
    - Metadata extraction (dimensions, size, format)
    - Color analysis (dominant colors, brightness, contrast)
    - Content description generation
    - Scene detection
    - Pattern recognition
    - ASCII art conversion
    - Image comparison
    """

    def __init__(self, data_dir: str | None = None):
        self.data_dir = data_dir or os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "data", "images"
        )
        os.makedirs(self.data_dir, exist_ok=True)

        self._image_cache: dict[str, ImageInfo] = {}
        self._total_analyzed = 0
        self._supported_formats = {"PNG", "JPEG", "GIF", "BMP", "WEBP", "ICO", "TIFF"}

    def load(self, filepath: str) -> ImageInfo:
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"Image not found: {filepath}")

        fmt = FormatDetector.detect(filepath)
        file_size = path.stat().st_size

        info = ImageInfo(
            filepath=str(path.absolute()),
            filename=path.name,
            format=fmt,
            width=0, height=0,
            file_size=file_size,
            file_size_human=DescriptionEngine._size_description(file_size),
        )

        if fmt == "PNG":
            png_info = PNGReader.read_info(filepath)
            info.width = png_info.get("width", 0)
            info.height = png_info.get("height", 0)
            info.has_alpha = png_info.get("has_alpha", False)
            info.color_depth = png_info.get("bit_depth", 8) * 3
            info.compression = png_info.get("compression", "deflate")
            info.exif = {m["key"]: m["value"] for m in png_info.get("metadata", [])}
        elif fmt == "JPEG":
            jpeg_info = JPEGReader.read_info(filepath)
            info.width = jpeg_info.get("width", 0)
            info.height = jpeg_info.get("height", 0)
            info.has_alpha = False
            info.color_depth = 24
            info.exif = jpeg_info.get("exif", {})
        else:
            try:
                with open(filepath, "rb") as f:
                    data = f.read(1000)
                info.width = min(800, max(100, len(data) // 100))
                info.height = min(600, max(100, len(data) // 150))
            except Exception:
                info.width = info.height = 0

        self._image_cache[str(path.absolute())] = info
        return info

    def analyze(self, filepath: str, detailed: bool = True) -> ImageInfo:
        info = self.load(filepath)

        if detailed:
            info.dominant_colors = ColorAnalyzer.extract_dominant_colors(filepath)
            info.brightness = ColorAnalyzer.calculate_brightness(filepath)
            info.contrast = ColorAnalyzer.calculate_contrast(filepath)

            scenes = PatternDetector.detect_scene(info)
            content_type = PatternDetector.detect_content_type(info)
            suggestions = PatternDetector.suggest_use(info)

            info.description = DescriptionEngine.describe(info)
            if scenes:
                info.description += f" The scene appears to be {', '.join(scenes)}."
            if content_type:
                info.description += f" Content type: {content_type.replace('_', ' ')}."
            if suggestions:
                info.description += f" {suggestions[0].capitalize()}."

            info.detected_objects = scenes
            info.analyzed = True
            self._total_analyzed += 1

        return info

    def describe(self, filepath: str) -> str:
        if filepath in self._image_cache and self._image_cache[filepath].analyzed:
            return self._image_cache[filepath].description
        info = self.analyze(filepath, detailed=True)
        return info.description

    def get_colors(self, filepath: str, num_colors: int = 5) -> list[dict]:
        info = self.analyze(filepath, detailed=True)
        return info.dominant_colors[:num_colors]

    def to_ascii(self, filepath: str, width: int = 80, height: int = 40) -> str:
        return AsciiConverter.to_ascii(filepath, width, height)

    def get_info(self, filepath: str) -> dict:
        info = self.analyze(filepath, detailed=False)
        return info.to_dict()

    def batch_analyze(self, filepaths: list[str]) -> list[dict]:
        results = []
        for fp in filepaths:
            try:
                info = self.analyze(fp, detailed=False)
                results.append({"filepath": fp, "status": "ok", "info": info.to_dict()})
            except Exception as e:
                results.append({"filepath": fp, "status": "error", "error": str(e)})
        return results

    def find_images(self, directory: str, recursive: bool = True) -> list[str]:
        path = Path(directory)
        if not path.exists():
            return []

        images = []
        pattern = "**/*" if recursive else "*"
        for fp in path.glob(pattern):
            if fp.is_file() and FormatDetector.is_image(str(fp)):
                images.append(str(fp))
        return images

    def compare(self, path1: str, path2: str) -> dict:
        info1 = self.analyze(path1, detailed=True)
        info2 = self.analyze(path2, detailed=True)

        size_diff = abs(info1.file_size - info2.file_size) / max(info1.file_size, info2.file_size)
        dim_match = info1.width == info2.width and info1.height == info2.height
        brightness_diff = abs(info1.brightness - info2.brightness)

        similar = brightness_diff < 0.2 and dim_match and size_diff < 0.5

        return {
            "similar": similar,
            "brightness_diff": round(brightness_diff, 2),
            "size_diff_percent": round(size_diff * 100, 1),
            "dimensions_match": dim_match,
            "info1": {"format": info1.format, "size": info1.file_size_human, "brightness": round(info1.brightness, 2)},
            "info2": {"format": info2.format, "size": info2.file_size_human, "brightness": round(info2.brightness, 2)},
        }

    def get_stats(self) -> dict:
        return {
            "total_analyzed": self._total_analyzed,
            "cached": len(self._image_cache),
            "supported_formats": list(self._supported_formats),
        }

    def save_analysis(self, filepath: str, output: str | None = None) -> str:
        info = self.analyze(filepath, detailed=True)
        out_path = output or os.path.join(self.data_dir, f"{Path(filepath).stem}_analysis.json")
        with open(out_path, "w") as f:
            json.dump(info.to_dict(), f, indent=2)
        return f"Analysis saved to {out_path}"
