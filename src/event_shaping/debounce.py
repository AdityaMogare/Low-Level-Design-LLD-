"""Debounce: execute only after events stop for a quiet period (trailing edge)."""

from __future__ import annotations

import threading
import time

from .interfaces import EventGate


class DebounceGate(EventGate):
    """
    Allow execution only when `quiet_period_seconds` have passed since the
    last call — typical search-box / resize debounce semantics.

    State: last_event_time — O(1).
    """

    def __init__(self, quiet_period_seconds: float) -> None:
        if quiet_period_seconds <= 0:
            raise ValueError("quiet_period_seconds must be positive")
        self._quiet_period_seconds = quiet_period_seconds
        self._last_event_time: float | None = None
        self._lock = threading.Lock()

    def should_execute(self, timestamp: float | None = None) -> bool:
        with self._lock:
            now = time.monotonic() if timestamp is None else timestamp
            if self._last_event_time is None:
                self._last_event_time = now
                return False
            if (now - self._last_event_time) >= self._quiet_period_seconds:
                self._last_event_time = now
                return True
            self._last_event_time = now
            return False

    def reset(self) -> None:
        with self._lock:
            self._last_event_time = None
