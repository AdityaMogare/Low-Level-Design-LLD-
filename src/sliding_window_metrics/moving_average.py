"""Moving average of the last N readings (LC 346)."""

from __future__ import annotations

import threading
from collections import deque

from .interfaces import StreamAggregator


class MovingAverage(StreamAggregator):
    """
    Fixed-size count window: average of the last `window_size` values.

    State: circular buffer via deque + running sum — O(window_size).
    """

    def __init__(self, window_size: int) -> None:
        if window_size <= 0:
            raise ValueError("window_size must be positive")
        self._window_size = window_size
        self._values: deque[float] = deque()
        self._running_sum = 0.0
        self._lock = threading.Lock()

    def add(self, value: float) -> None:
        with self._lock:
            self._values.append(value)
            self._running_sum += value
            if len(self._values) > self._window_size:
                self._running_sum -= self._values.popleft()

    def aggregate(self) -> float:
        with self._lock:
            if not self._values:
                raise ValueError("no values recorded")
            return self._running_sum / len(self._values)
