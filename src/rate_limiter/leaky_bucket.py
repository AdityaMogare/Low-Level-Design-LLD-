"""Leaky-bucket rate limiter: queue requests and drain at a constant rate."""

from __future__ import annotations

import threading
import time

from .interfaces import RateLimiter


class LeakyBucketRateLimiter(RateLimiter):
    """
    Queue up to `capacity` requests; drain at `drain_rate` requests/second.

    State (O(1) water-level model):
        capacity, drain_rate, queue_size, last_drain_time, lock

    Drain is applied lazily from elapsed monotonic time before each admission.
    """

    def __init__(self, capacity: float, drain_rate: float) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if drain_rate <= 0:
            raise ValueError("drain_rate must be positive")

        self._capacity = float(capacity)
        self._drain_rate = float(drain_rate)
        self._queue_size = 0.0
        self._last_drain_time = time.monotonic()
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        with self._lock:
            self._drain()
            if self._queue_size >= self._capacity:
                return False
            self._queue_size += 1.0
            return True

    def _drain(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_drain_time
        if elapsed <= 0:
            return
        leaked = elapsed * self._drain_rate
        self._queue_size = max(0.0, self._queue_size - leaked)
        self._last_drain_time = now
