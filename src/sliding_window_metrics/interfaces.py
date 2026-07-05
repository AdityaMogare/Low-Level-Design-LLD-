"""Contracts for stream metrics over sliding windows."""

from __future__ import annotations

from abc import ABC, abstractmethod


class TimeSeriesCounter(ABC):
    """Record events and count how many fall inside a rolling time window."""

    @abstractmethod
    def record_hit(self, timestamp: float | None = None) -> None:
        """Record an event at `timestamp` (defaults to now)."""

    @abstractmethod
    def count_in_window(self, timestamp: float | None = None) -> int:
        """Return the number of events in the window ending at `timestamp`."""


class StreamAggregator(ABC):
    """Maintain a scalar aggregate over a sliding stream of numeric values."""

    @abstractmethod
    def add(self, value: float) -> None:
        """Ingest the next reading."""

    @abstractmethod
    def aggregate(self) -> float:
        """Return the current aggregate (max, average, etc.)."""
