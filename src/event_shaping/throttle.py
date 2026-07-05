"""Throttle: execute at most once per interval (leading edge)."""

from __future__ import annotations

import threading
import time

from .interfaces import EventGate


class ThrottleGate(EventGate):
    """
    Allow execution at most once every `interval_seconds` — leading-edge throttle.

    State: last_execution_time — O(1).
    """

    def __init__(self, interval_seconds: float) -> None:
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self._interval_seconds = interval_seconds
        self._last_execution_time: float | None = None
        self._lock = threading.Lock()

    def should_execute(self, timestamp: float | None = None) -> bool:
        with self._lock:
            now = time.monotonic() if timestamp is None else timestamp
            if self._last_execution_time is None:
                self._last_execution_time = now
                return True
            if (now - self._last_execution_time) >= self._interval_seconds:
                self._last_execution_time = now
                return True
            return False
