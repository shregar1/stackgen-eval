"""Flyweight Regex Registry providing thread-safe memoized compiled patterns."""

import re
import threading
from typing import Dict, Pattern, Tuple


class FlyweightRegexRegistry:
    """
    Flyweight Pattern: Centralized cache of immutable precompiled regular expressions.
    Eliminates redundant re.compile overhead across high-throughput evaluation loops.
    """

    _instance = None
    _lock = threading.Lock()

    def __init__(self):
        self._cache: Dict[Tuple[str, int], Pattern] = {}
        self._access_lock = threading.Lock()
        self.hits: int = 0
        self.misses: int = 0

    @classmethod
    def get_instance(cls) -> "FlyweightRegexRegistry":
        """Singleton accessor for global flyweight registry."""
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    def get_pattern(self, pattern_str: str, flags: int = 0) -> Pattern:
        """Retrieve precompiled pattern or compile and cache if absent."""
        key = (pattern_str, flags)
        with self._access_lock:
            if key in self._cache:
                self.hits += 1
                return self._cache[key]

            self.misses += 1
            compiled = re.compile(pattern_str, flags)
            self._cache[key] = compiled
            return compiled

    def clear(self) -> None:
        """Reset the flyweight cache."""
        with self._access_lock:
            self._cache.clear()
            self.hits = 0
            self.misses = 0
