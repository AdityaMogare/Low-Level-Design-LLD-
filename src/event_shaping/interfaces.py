"""Contracts for debounce and throttle event gates."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EventGate(ABC):
    """Decide whether a rapidly firing event should execute now."""

    @abstractmethod
    def should_execute(self, timestamp: float | None = None) -> bool:
        """Return True if the event should proceed at `timestamp` (defaults to now)."""
