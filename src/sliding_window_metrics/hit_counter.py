"""API hit counter: hits in the last N seconds (LC 362)."""

from __future__ import annotations

import threading
import time

from common.timestamp_window import TimestampWindow

from .interfaces import TimeSeriesCounter


class HitCounter(TimeSeriesCounter):
    """
    Count hits in a rolling time window.

    State: TimestampWindow — O(hits in window).
    """

    def __init__(self, window_size_seconds: float) -> None:
        self._window = TimestampWindow(window_size_seconds)
        self._lock = threading.Lock()

    def record_hit(self, timestamp: float | None = None) -> None:
        with self._lock:
            now = time.monotonic() if timestamp is None else timestamp
            self._window.record(now)

    def count_in_window(self, timestamp: float | None = None) -> int:
        with self._lock:
            now = time.monotonic() if timestamp is None else timestamp
            self._window.evict_expired(now)
            return self._window.count()
