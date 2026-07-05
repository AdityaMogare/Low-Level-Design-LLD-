"""Logger that suppresses duplicate messages within a cooldown window (LC 359)."""

from __future__ import annotations

import threading
import time


class DedupLogger:
    """
    Skip logging the same message if it was seen within `cooldown_seconds`.

    State: HashMap<message, last_seen_time> — O(unique messages).
    """

    def __init__(self, cooldown_seconds: float = 10.0) -> None:
        if cooldown_seconds <= 0:
            raise ValueError("cooldown_seconds must be positive")
        self._cooldown_seconds = cooldown_seconds
        self._last_seen: dict[str, float] = {}
        self._lock = threading.Lock()

    def should_log(self, message: str) -> bool:
        with self._lock:
            now = time.monotonic()
            last = self._last_seen.get(message)
            if last is not None and (now - last) < self._cooldown_seconds:
                return False
            self._last_seen[message] = now
            return True
