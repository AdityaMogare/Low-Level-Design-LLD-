"""Sliding-window rate limiter: deque of request timestamps."""

from __future__ import annotations

import threading
import time

from common.timestamp_window import TimestampWindow

from .interfaces import RateLimiter


class SlidingWindowRateLimiter(RateLimiter):
    """
    Admit at most `max_requests` within any rolling window of `window_size_seconds`.

    State (O(N) where N = admitted requests still inside the window):
        max_requests, window, lock
    """

    def __init__(self, max_requests: int, window_size_seconds: float) -> None:
        if max_requests <= 0:
            raise ValueError("max_requests must be positive")

        self._max_requests = max_requests
        self._window = TimestampWindow(window_size_seconds)
        self._lock = threading.Lock()

    def allow_request(self) -> bool:
        with self._lock:
            return self._window.try_add(time.monotonic(), self._max_requests)
