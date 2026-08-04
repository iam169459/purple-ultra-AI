"""Caching layer with TTL support and rate limiting."""

from __future__ import annotations

import time
import threading
from collections import OrderedDict
from typing import Any, Callable


class TTLCache:
    def __init__(self, max_size: int = 1000, default_ttl: float = 300):
        self._cache: OrderedDict[str, tuple[Any, float]] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key in self._cache:
                value, expiry = self._cache[key]
                if time.time() < expiry:
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return value
                else:
                    del self._cache[key]
            self._misses += 1
            return None

    def set(self, key: str, value: Any, ttl: float = None):
        with self._lock:
            if key in self._cache:
                del self._cache[key]
            elif len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
            expiry = time.time() + (ttl if ttl is not None else self._default_ttl)
            self._cache[key] = (value, expiry)

    def delete(self, key: str) -> bool:
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    def clear(self):
        with self._lock:
            self._cache.clear()

    def size(self) -> int:
        return len(self._cache)

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": self._hits / total if total > 0 else 0,
        }


class RateLimiter:
    def __init__(self, max_requests: int = 60, window: float = 60):
        self._max_requests = max_requests
        self._window = window
        self._requests: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str = "default") -> bool:
        with self._lock:
            now = time.time()
            if key not in self._requests:
                self._requests[key] = []
            self._requests[key] = [t for t in self._requests[key] if now - t < self._window]
            if len(self._requests[key]) < self._max_requests:
                self._requests[key].append(now)
                return True
            return False

    def wait_time(self, key: str = "default") -> float:
        with self._lock:
            now = time.time()
            if key not in self._requests or not self._requests[key]:
                return 0
            oldest = min(self._requests[key])
            return max(0, self._window - (now - oldest))

    def reset(self, key: str = None):
        with self._lock:
            if key:
                self._requests.pop(key, None)
            else:
                self._requests.clear()

    def stats(self) -> dict:
        with self._lock:
            return {
                "keys": len(self._requests),
                "total_requests": sum(len(v) for v in self._requests.values()),
                "window": self._window,
                "max_requests": self._max_requests,
            }


class Memoize:
    def __init__(self, func: Callable, ttl: float = 300):
        self._func = func
        self._cache = TTLCache(default_ttl=ttl)

    def __call__(self, *args, **kwargs):
        key = str(args) + str(kwargs)
        result = self._cache.get(key)
        if result is None:
            result = self._func(*args, **kwargs)
            self._cache.set(key, result)
        return result

    def invalidate(self):
        self._cache.clear()


def memoize(ttl: float = 300):
    def decorator(func: Callable) -> Memoize:
        return Memoize(func, ttl)
    return decorator
