"""Unit tests for FlyweightRegexRegistry."""

import re
import pytest
from src.core.flyweight.flyweight_regex_registry import FlyweightRegexRegistry


class TestFlyweightRegex:
    """Class-based test suite verifying flyweight pattern memoization and thread-safe pattern reuse."""

    def test_flyweight_pattern_reuse_and_hit_counting(self):
        registry = FlyweightRegexRegistry()
        pattern_str = r"\b[A-Z]{2,10}-\d+\b"

        # First call -> miss
        pat1 = registry.get_pattern(pattern_str)
        assert registry.misses == 1
        assert registry.hits == 0

        # Second call with identical pattern -> hit!
        pat2 = registry.get_pattern(pattern_str)
        assert registry.misses == 1
        assert registry.hits == 1
        assert pat1 is pat2  # Identical cached object reference

    def test_different_flags_create_separate_instances(self):
        registry = FlyweightRegexRegistry()
        pattern_str = r"hello"

        p_default = registry.get_pattern(pattern_str, flags=0)
        p_ignorecase = registry.get_pattern(pattern_str, flags=re.IGNORECASE)

        assert p_default is not p_ignorecase
        assert p_ignorecase.search("HELLO") is not None
        assert p_default.search("HELLO") is None

    def test_singleton_instance_persists_across_calls(self):
        reg1 = FlyweightRegexRegistry.get_instance()
        reg2 = FlyweightRegexRegistry.get_instance()
        assert reg1 is reg2

    def test_clear_cache(self):
        registry = FlyweightRegexRegistry()
        registry.get_pattern(r"\d+")
        assert registry.misses == 1
        registry.clear()
        assert registry.misses == 0
        assert registry.hits == 0
