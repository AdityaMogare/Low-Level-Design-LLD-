"""Core contracts for rate-limiting strategies."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum


class RateLimiterType(Enum):
    SLIDING_WINDOW = "sliding_window"
    TOKEN_BUCKET = "token_bucket"
    LEAKY_BUCKET = "leaky_bucket"


class RateLimiter(ABC):
    """Strategy interface: decide whether a single request may proceed."""

    @abstractmethod
    def allow_request(self) -> bool:
        """Return True if the request is admitted, False if it is rate-limited."""
