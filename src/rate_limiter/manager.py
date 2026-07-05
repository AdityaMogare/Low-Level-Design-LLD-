"""Per-user rate-limiter manager with thread-safe factory creation."""

from __future__ import annotations

import threading
from typing import Any

from .interfaces import RateLimiter, RateLimiterType
from .leaky_bucket import LeakyBucketRateLimiter
from .sliding_window import SlidingWindowRateLimiter
from .token_bucket import TokenBucketRateLimiter


def composite_key(user_id: str, endpoint: str) -> str:
    """Build an isolation key for per-user, per-endpoint quotas."""
    return f"{user_id}:{endpoint}"


class RateLimiterManager:
    """
    Context/client: owns one limiter instance per registry key.

    Pass `endpoint` to isolate quotas per API route (row 5).
    Creation uses double-checked locking for concurrent first-access.
    """

    def __init__(self, limiter_type: RateLimiterType, **config: Any) -> None:
        self._limiter_type = limiter_type
        self._config = config
        self._limiters: dict[str, RateLimiter] = {}
        self._registry_lock = threading.Lock()

    def get_limiter(self, user_id: str, endpoint: str | None = None) -> RateLimiter:
        key = self._registry_key(user_id, endpoint)
        limiter = self._limiters.get(key)
        if limiter is not None:
            return limiter

        with self._registry_lock:
            limiter = self._limiters.get(key)
            if limiter is None:
                limiter = self._create_limiter()
                self._limiters[key] = limiter
            return limiter

    def allow_request(self, user_id: str, endpoint: str | None = None) -> bool:
        return self.get_limiter(user_id, endpoint).allow_request()

    @staticmethod
    def _registry_key(user_id: str, endpoint: str | None) -> str:
        if endpoint is None:
            return user_id
        return composite_key(user_id, endpoint)

    def _create_limiter(self) -> RateLimiter:
        if self._limiter_type is RateLimiterType.SLIDING_WINDOW:
            return SlidingWindowRateLimiter(
                max_requests=self._config["max_requests"],
                window_size_seconds=self._config["window_size_seconds"],
            )
        if self._limiter_type is RateLimiterType.TOKEN_BUCKET:
            return TokenBucketRateLimiter(
                capacity=self._config["capacity"],
                refill_rate=self._config["refill_rate"],
            )
        if self._limiter_type is RateLimiterType.LEAKY_BUCKET:
            return LeakyBucketRateLimiter(
                capacity=self._config["capacity"],
                drain_rate=self._config["drain_rate"],
            )
        raise ValueError(f"Unsupported limiter type: {self._limiter_type}")
