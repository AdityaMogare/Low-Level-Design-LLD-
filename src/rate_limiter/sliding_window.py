"""Sliding-window rate limiter: deque of request timestamps."""

from __future__ import annotations

import threading
import time
from collections import deque

from .interfaces import RateLimiter


class SlidingWindowRateLimiter(RateLimiter):
    """
    Admit at most `max_requests` within any rolling window of `window_size_seconds`.

    State (O(N) where N = admitted requests still inside the window):
        max_requests, window_size_seconds, timestamps, lock
    """

    def __init__(self, max_requests: int, window_size_seconds: float) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")
        if window_size_seconds <= 0:
            raise ValueError("window_size_seconds must be positive")

        self._max_requests = max_requests
        self._window_size_seconds = window_size_seconds
        self._timestamps: deque[float] = deque()
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        with self._lock:
            now = time.monotonic()
            cutoff = now - self._window_size_seconds

            while self._timestamps and self._timestamps[0] <= cutoff:
                self._timestamps.popleft()

            if len(self._timestamps) >= self._max_requests:
                return False

            self._timestamps.append(now)
            return True
