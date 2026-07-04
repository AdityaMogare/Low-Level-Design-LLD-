"""Token-bucket rate limiter with lazy refill (no background timers)."""

from __future__ import annotations

import threading
import time

from .interfaces import RateLimiter


class TokenBucketRateLimiter(RateLimiter):
    """
    Burst up to `capacity` tokens; refill at `refill_rate` tokens/second.

    State (O(1)):
        capacity, refill_rate, tokens, last_refill_time, lock

    Refill is computed on each call from elapsed monotonic time.
    """

    def __init__(self, capacity: float, refill_rate: float) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")

        self._capacity = float(capacity)
        self._refill_rate = float(refill_rate)
        self._tokens = float(capacity)
        self._last_refill_time = time.monotonic()
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        with self._lock:
            self._refill()
            if self._tokens < 1.0:
                return False
            self._tokens -= 1.0
            return True

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill_time
        if elapsed <= 0:
            return
        self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
        self._last_refill_time = now
