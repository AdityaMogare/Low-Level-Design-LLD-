"""Monotonic deque for max-in-window queries (LC 239)."""

from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass

from .interfaces import StreamAggregator


@dataclass(frozen=True)
class _WindowEntry:
    value: float
    timestamp: float


class MaxSlidingWindow(StreamAggregator):
    """
    Max value of a metric stream over a rolling time window.

    State: monotonic deque of (value, timestamp) — O(window entries).
    """

    def __init__(self, window_size_seconds: float) -> None:
        if window_size_seconds <= 0:
            raise ValueError("window_size_seconds must be positive")
        self._window_size_seconds = window_size_seconds
        self._entries: deque[_WindowEntry] = deque()
        self._lock = threading.Lock()

    def add(self, value: float) -> None:
        with self._lock:
            now = time.monotonic()
            self._evict_expired(now)
            while self._entries and self._entries[-1].value <= value:
                self._entries.pop()
            self._entries.append(_WindowEntry(value=value, timestamp=now))

    def aggregate(self) -> float:
        with self._lock:
            self._evict_expired(time.monotonic())
            if not self._entries:
                raise ValueError("no values in window")
            return self._entries[0].value

    def _evict_expired(self, now: float) -> None:
        cutoff = now - self._window_size_seconds
        while self._entries and self._entries[0].timestamp <= cutoff:
            self._entries.popleft()
