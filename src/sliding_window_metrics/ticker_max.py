"""Max price over the last K ticks (count-based sliding window)."""

from __future__ import annotations

import threading
from collections import deque
from dataclasses import dataclass

from .interfaces import StreamAggregator


@dataclass(frozen=True)
class _TickEntry:
    value: float
    index: int


class TickerMax(StreamAggregator):
    """
    Max value over the last `window_size` ticks (not time-based).

    Same monotonic-deque pattern as MaxSlidingWindow, evicted by index.
    """

    def __init__(self, window_size: int) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        self._window_size = window_size
        self._entries: deque[_TickEntry] = deque()
        self._tick_index = 0
        self._lock = threading.Lock()

    def add(self, value: float) -> None:
        with self._lock:
            self._tick_index += 1
            min_index = self._tick_index - self._window_size
            while self._entries and self._entries[0].index <= min_index:
                self._entries.popleft()
            while self._entries and self._entries[-1].value <= value:
                self._entries.pop()
            self._entries.append(_TickEntry(value=value, index=self._tick_index))

    def aggregate(self) -> float:
        with self._lock:
            if not self._entries:
                raise ValueError("no ticks recorded")
            return self._entries[0].value
