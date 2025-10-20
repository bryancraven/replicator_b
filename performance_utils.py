#!/usr/bin/env python3
"""
Performance utilities for factory simulation

This module provides caching, profiling, and optimization utilities.
"""

from typing import Dict, Any, Callable, Optional, TypeVar, Generic
from functools import lru_cache, wraps
from dataclasses import dataclass
import time
import logging

T = TypeVar('T')
R = TypeVar('R')

logger = logging.getLogger(__name__)


# ===============================================================================
# CACHING UTILITIES
# ===============================================================================

class ResourceCalculationCache:
    """
    Cache for expensive resource requirement calculations with proper LRU eviction.

    This cache stores results of recursive resource calculations to avoid
    redundant computation. Uses OrderedDict for efficient LRU implementation.
    """

    def __init__(self, max_size: int = 1000):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of cached entries
        """
        from collections import OrderedDict
        self._cache: OrderedDict[tuple, Dict[Any, float]] = OrderedDict()
        self._max_size = max_size
        self._hits = 0
        self._misses = 0

    def get(self, resource: Any, quantity: int) -> Optional[Dict[Any, float]]:
        """
        Get cached calculation result.

        Args:
            resource: Resource type
            quantity: Quantity requested

        Returns:
            Cached requirements dict or None if not cached
        """
        key = (resource, quantity)
        if key in self._cache:
            self._hits += 1
            # Move to end to mark as recently used (LRU)
            self._cache.move_to_end(key)
            return self._cache[key].copy()
        else:
            self._misses += 1
            return None

    def set(self, resource: Any, quantity: int, requirements: Dict[Any, float]) -> None:
        """
        Cache a calculation result with proper LRU eviction.

        Args:
            resource: Resource type
            quantity: Quantity requested
            requirements: Calculated requirements
        """
        key = (resource, quantity)

        # If key exists, update and move to end
        if key in self._cache:
            self._cache[key] = requirements.copy()
            self._cache.move_to_end(key)
        else:
            # If at capacity, remove least recently used (first item)
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)  # Remove first (oldest) item

            # Add new item (will be at end)
            self._cache[key] = requirements.copy()

    def clear(self) -> None:
        """Clear all cached entries"""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": hit_rate
        }


# ===============================================================================
# PERFORMANCE PROFILING
# ===============================================================================

@dataclass
class ProfileStats:
    """Statistics for a profiled function"""
    call_count: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0


class PerformanceProfiler:
    """Profile function execution times"""

    def __init__(self):
        self._stats: Dict[str, ProfileStats] = {}
        self._enabled = False

    def enable(self):
        """Enable profiling"""
        self._enabled = True

    def disable(self):
        """Disable profiling"""
        self._enabled = False

    def profile(self, func_name: Optional[str] = None):
        """
        Decorator to profile a function.

        Args:
            func_name: Optional custom name for the function

        Example:
            >>> profiler = PerformanceProfiler()
            >>> profiler.enable()
            >>> @profiler.profile()
            ... def expensive_function():
            ...     # Do work
            ...     pass
        """
        def decorator(func: Callable) -> Callable:
            name = func_name or f"{func.__module__}.{func.__name__}"

            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self._enabled:
                    return func(*args, **kwargs)

                start_time = time.perf_counter()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    elapsed = time.perf_counter() - start_time
                    self._record(name, elapsed)

            return wrapper
        return decorator

    def _record(self, func_name: str, elapsed_time: float):
        """Record execution time"""
        if func_name not in self._stats:
            self._stats[func_name] = ProfileStats()

        stats = self._stats[func_name]
        stats.call_count += 1
        stats.total_time += elapsed_time
        stats.min_time = min(stats.min_time, elapsed_time)
        stats.max_time = max(stats.max_time, elapsed_time)
        stats.avg_time = stats.total_time / stats.call_count

    def get_stats(self) -> Dict[str, ProfileStats]:
        """Get profiling statistics"""
        return self._stats.copy()

    def print_stats(self, top_n: int = 10):
        """Print profiling statistics"""
        if not self._stats:
            print("No profiling data collected")
            return

        print("\n" + "=" * 80)
        print("PERFORMANCE PROFILING RESULTS")
        print("=" * 80)

        # Sort by total time
        sorted_stats = sorted(
            self._stats.items(),
            key=lambda x: x[1].total_time,
            reverse=True
        )

        print(f"\n{'Function':<40} {'Calls':<8} {'Total(s)':<10} {'Avg(ms)':<10} {'Min(ms)':<10} {'Max(ms)':<10}")
        print("-" * 80)

        for func_name, stats in sorted_stats[:top_n]:
            print(
                f"{func_name:<40} {stats.call_count:<8} "
                f"{stats.total_time:<10.3f} "
                f"{stats.avg_time * 1000:<10.3f} "
                f"{stats.min_time * 1000:<10.3f} "
                f"{stats.max_time * 1000:<10.3f}"
            )

        print("=" * 80)

    def reset(self):
        """Reset all profiling data"""
        self._stats.clear()


# ===============================================================================
# RUNTIME ASSERTIONS
# ===============================================================================

class DebugMode:
    """
    Debug mode with runtime assertions and invariant checking.

    Use this to enable expensive runtime checks during development and testing.
    """

    _enabled = False
    _strict = False

    @classmethod
    def enable(cls, strict: bool = False):
        """
        Enable debug mode.

        Args:
            strict: If True, assertion failures raise exceptions.
                   If False, they only log warnings.
        """
        cls._enabled = True
        cls._strict = strict
        logger.info("Debug mode enabled (strict=%s)", strict)

    @classmethod
    def disable(cls):
        """Disable debug mode"""
        cls._enabled = False
        logger.info("Debug mode disabled")

    @classmethod
    def is_enabled(cls) -> bool:
        """Check if debug mode is enabled"""
        return cls._enabled

    @classmethod
    def assert_positive(cls, value: float, name: str):
        """Assert that a value is positive"""
        if not cls._enabled:
            return

        if value <= 0:
            msg = f"Assertion failed: {name} must be positive, got {value}"
            if cls._strict:
                raise AssertionError(msg)
            else:
                logger.warning(msg)

    @classmethod
    def assert_range(cls, value: float, min_val: float, max_val: float, name: str):
        """Assert that a value is within range"""
        if not cls._enabled:
            return

        if not (min_val <= value <= max_val):
            msg = f"Assertion failed: {name} must be in [{min_val}, {max_val}], got {value}"
            if cls._strict:
                raise AssertionError(msg)
            else:
                logger.warning(msg)

    @classmethod
    def assert_resource_balance(cls, produced: float, consumed: float, tolerance: float = 0.01):
        """Assert resource conservation (within tolerance)"""
        if not cls._enabled:
            return

        if abs(produced - consumed) > tolerance:
            msg = f"Resource balance violation: produced={produced}, consumed={consumed}"
            if cls._strict:
                raise AssertionError(msg)
            else:
                logger.warning(msg)

    @classmethod
    def assert_energy_conservation(cls, generated: float, consumed: float, stored: float):
        """Assert energy conservation"""
        if not cls._enabled:
            return

        total_available = generated + stored
        if consumed > total_available * 1.01:  # 1% tolerance
            msg = (
                f"Energy conservation violation: "
                f"consumed={consumed}, available={total_available} "
                f"(generated={generated}, stored={stored})"
            )
            if cls._strict:
                raise AssertionError(msg)
            else:
                logger.warning(msg)

    @classmethod
    def check_invariant(cls, condition: bool, message: str):
        """Check a general invariant"""
        if not cls._enabled:
            return

        if not condition:
            msg = f"Invariant violation: {message}"
            if cls._strict:
                raise AssertionError(msg)
            else:
                logger.warning(msg)


# ===============================================================================
# GLOBAL INSTANCES
# ===============================================================================

# Global resource calculation cache
resource_cache = ResourceCalculationCache(max_size=1000)

# Global performance profiler
profiler = PerformanceProfiler()


# ===============================================================================
# CONVENIENCE DECORATORS
# ===============================================================================

def cached_resource_calculation(func: Callable) -> Callable:
    """
    Decorator to cache resource calculations.

    Example:
        >>> @cached_resource_calculation
        ... def calculate_requirements(resource, quantity):
        ...     # Expensive calculation
        ...     return requirements
    """
    @wraps(func)
    def wrapper(resource, quantity, *args, **kwargs):
        # Try cache first
        cached_result = resource_cache.get(resource, quantity)
        if cached_result is not None:
            return cached_result

        # Calculate and cache
        result = func(resource, quantity, *args, **kwargs)
        resource_cache.set(resource, quantity, result)
        return result

    return wrapper


def profile_performance(func_name: Optional[str] = None):
    """
    Decorator to profile function performance.

    Example:
        >>> @profile_performance("my_function")
        ... def my_function():
        ...     # Do work
        ...     pass
    """
    return profiler.profile(func_name)


if __name__ == "__main__":
    # Demonstration
    print("Performance Utilities Demonstration")
    print("=" * 60)

    # Test caching
    print("\n1. Resource Calculation Cache:")
    cache = ResourceCalculationCache(max_size=5)

    cache.set("STEEL", 100, {"IRON_ORE": 150, "COAL": 50})
    result = cache.get("STEEL", 100)
    print(f"  Cached result: {result}")
    print(f"  Cache stats: {cache.get_stats()}")

    # Test profiling
    print("\n2. Performance Profiling:")
    profiler.enable()

    @profiler.profile("test_function")
    def slow_function():
        time.sleep(0.01)
        return "done"

    for _ in range(10):
        slow_function()

    profiler.print_stats()

    # Test debug mode
    print("\n3. Debug Mode Assertions:")
    DebugMode.enable(strict=False)

    DebugMode.assert_positive(10, "value")
    DebugMode.assert_range(5, 0, 10, "value")
    DebugMode.check_invariant(True, "This should pass")

    print("\n✅ All performance utilities working correctly!")