"""Registry for per-key hit counters and stream aggregators."""

from __future__ import annotations

import threading
from typing import Callable, Generic, TypeVar

T = TypeVar("T")


class MetricsRegistry(Generic[T]):
    """Lazy, thread-safe factory: one metric instance per key."""

    def __init__(self, factory: Callable[[], T]) -> None:
        self._factory = factory
        self._instances: dict[str, T] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> T:
        instance = self._instances.get(key)
        if instance is not None:
            return instance

        with self._lock:
            instance = self._instances.get(key)
            if instance is None:
                instance = self._factory()
                self._instances[key] = instance
            return instance


class HitCounterManager:
    """Per-API-key hit counter (row 4 / LC 362)."""

    def __init__(self, window_size_seconds: float) -> None:
        from .hit_counter import HitCounter

        self._window_size_seconds = window_size_seconds
        self._registry: MetricsRegistry[HitCounter] = MetricsRegistry(
            lambda: HitCounter(self._window_size_seconds)
        )

    def record_hit(self, api_key: str, timestamp: float | None = None) -> None:
        self._registry.get(api_key).record_hit(timestamp)

    def count_in_window(self, api_key: str, timestamp: float | None = None) -> int:
        return self._registry.get(api_key).count_in_window(timestamp)
