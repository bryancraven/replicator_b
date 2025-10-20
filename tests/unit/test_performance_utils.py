#!/usr/bin/env python3
"""
Tests for performance utilities.

Tests the optimizations from the code quality audit (Fix H2).
"""

import pytest
from performance_utils import (
    ResourceCalculationCache,
    PerformanceProfiler,
    DebugMode,
    profiler,
    resource_cache,
)


class TestResourceCalculationCache:
    """Test LRU cache implementation (Fix H2)"""

    def test_cache_initialization(self):
        """Test cache is initialized correctly"""
        cache = ResourceCalculationCache(max_size=100)
        assert cache._max_size == 100
        assert cache._hits == 0
        assert cache._misses == 0

    def test_cache_miss(self):
        """Test cache miss increments miss counter"""
        cache = ResourceCalculationCache()
        result = cache.get("STEEL", 100)
        assert result is None
        assert cache._misses == 1
        assert cache._hits == 0

    def test_cache_hit(self):
        """Test cache hit increments hit counter"""
        cache = ResourceCalculationCache()
        requirements = {"IRON_ORE": 150, "COAL": 50}

        cache.set("STEEL", 100, requirements)
        result = cache.get("STEEL", 100)

        assert result == requirements
        assert cache._hits == 1
        assert cache._misses == 0

    def test_lru_eviction(self):
        """Test that LRU eviction works correctly"""
        cache = ResourceCalculationCache(max_size=3)

        # Fill cache
        cache.set("A", 1, {"result": 1})
        cache.set("B", 2, {"result": 2})
        cache.set("C", 3, {"result": 3})

        # Access A to make it recently used
        cache.get("A", 1)

        # Add D, should evict B (least recently used)
        cache.set("D", 4, {"result": 4})

        # B should be evicted
        assert cache.get("B", 2) is None  # Miss
        # A and C should still be there
        assert cache.get("A", 1) is not None  # Hit
        assert cache.get("C", 3) is not None  # Hit

    def test_cache_clear(self):
        """Test cache clear resets everything"""
        cache = ResourceCalculationCache()
        cache.set("STEEL", 100, {"IRON": 150})
        cache.get("STEEL", 100)

        cache.clear()

        assert len(cache._cache) == 0
        assert cache._hits == 0
        assert cache._misses == 0

    def test_cache_stats(self):
        """Test cache statistics reporting"""
        cache = ResourceCalculationCache(max_size=100)

        cache.set("A", 1, {"B": 1})
        cache.get("A", 1)  # Hit
        cache.get("B", 2)  # Miss

        stats = cache.get_stats()

        assert stats["size"] == 1
        assert stats["max_size"] == 100
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert stats["hit_rate"] == 0.5


class TestPerformanceProfiler:
    """Test performance profiler"""

    def test_profiler_disabled_by_default(self):
        """Test that profiler is disabled by default"""
        prof = PerformanceProfiler()
        assert prof._enabled is False

    def test_profiler_enable_disable(self):
        """Test enabling and disabling profiler"""
        prof = PerformanceProfiler()

        prof.enable()
        assert prof._enabled is True

        prof.disable()
        assert prof._enabled is False

    def test_profiler_records_when_enabled(self):
        """Test that profiler records stats when enabled"""
        prof = PerformanceProfiler()
        prof.enable()

        @prof.profile("test_func")
        def test_function():
            return 42

        test_function()
        test_function()

        stats = prof.get_stats()
        assert "test_func" in stats
        assert stats["test_func"].call_count == 2
        assert stats["test_func"].total_time > 0

    def test_profiler_no_overhead_when_disabled(self):
        """Test that disabled profiler has no overhead"""
        prof = PerformanceProfiler()
        # Profiler is disabled by default

        @prof.profile("test_func")
        def test_function():
            return 42

        test_function()

        stats = prof.get_stats()
        assert "test_func" not in stats  # Should not record


class TestDebugMode:
    """Test debug mode assertions"""

    def test_debug_mode_disabled_by_default(self):
        """Test that debug mode is disabled by default"""
        assert DebugMode.is_enabled() is False

    def test_debug_mode_enable_disable(self):
        """Test enabling and disabling debug mode"""
        DebugMode.enable(strict=False)
        assert DebugMode.is_enabled() is True

        DebugMode.disable()
        assert DebugMode.is_enabled() is False

    def test_assert_positive_passes(self):
        """Test that positive assertion passes for positive value"""
        DebugMode.enable(strict=False)
        try:
            # Should not raise
            DebugMode.assert_positive(10, "value")
        finally:
            DebugMode.disable()

    def test_assert_positive_fails_strict(self):
        """Test that positive assertion fails in strict mode"""
        DebugMode.enable(strict=True)
        try:
            with pytest.raises(AssertionError):
                DebugMode.assert_positive(-5, "value")
        finally:
            DebugMode.disable()

    def test_assert_range_passes(self):
        """Test range assertion with valid value"""
        DebugMode.enable(strict=False)
        try:
            DebugMode.assert_range(5, 0, 10, "value")
        finally:
            DebugMode.disable()

    def test_assert_range_fails_strict(self):
        """Test range assertion fails in strict mode"""
        DebugMode.enable(strict=True)
        try:
            with pytest.raises(AssertionError):
                DebugMode.assert_range(15, 0, 10, "value")
        finally:
            DebugMode.disable()


class TestGlobalInstances:
    """Test global instances work correctly"""

    def test_global_resource_cache_exists(self):
        """Test global resource_cache instance exists"""
        assert resource_cache is not None
        assert isinstance(resource_cache, ResourceCalculationCache)

    def test_global_profiler_exists(self):
        """Test global profiler instance exists"""
        assert profiler is not None
        assert isinstance(profiler, PerformanceProfiler)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
