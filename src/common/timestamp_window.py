"""Rolling timestamp window: evict expired entries from the left of a deque."""

from __future__ import annotations

from collections import deque


class TimestampWindow:
    """
    O(N) storage for timestamps still inside the window.

    Used by sliding-window rate limiters, hit counters, and dedup loggers.
    """

    def __init__(self, window_size_seconds: float) -> None:
        if window_size_seconds <= 0:
            raise ValueError("window_size_seconds must be positive")
        self._window_size_seconds = window_size_seconds
        self._timestamps: deque[float] = deque()

    @property
    def window_size_seconds(self) -> float:
        return self._window_size_seconds

    def evict_expired(self, now: float) -> None:
        cutoff = now - self._window_size_seconds
        while self._timestamps and self._timestamps[0] <= cutoff:
            self._timestamps.popleft()

    def count(self) -> int:
        return len(self._timestamps)

    def add(self, timestamp: float) -> None:
        self._timestamps.append(timestamp)

    def try_add(self, now: float, max_count: int) -> bool:
        """Evict, reject if at capacity, otherwise record `now`."""
        self.evict_expired(now)
        if len(self._timestamps) >= max_count:
            return False
        self._timestamps.append(now)
        return True

    def record(self, now: float) -> None:
        """Evict expired entries and append `now` (no capacity limit)."""
        self.evict_expired(now)
        self._timestamps.append(now)
