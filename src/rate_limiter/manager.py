"""Per-user rate-limiter manager with thread-safe factory creation."""

from __future__ import annotations

import threading
from typing import Any

from .interfaces import RateLimiter, RateLimiterType
from .leaky_bucket import LeakyBucketRateLimiter
from .sliding_window import SlidingWindowRateLimiter
from .token_bucket import TokenBucketRateLimiter


class RateLimiterManager:
    """
    Context/client: owns one limiter instance per user_id.

    Creation uses double-checked locking so concurrent first-access for the
    same user does not race on the registry map.
    """

    def __init__(self, limiter_type: RateLimiterType, **config: Any) -> None:
        self._limiter_type = limiter_type
        self._config = config
        self._limiters: dict[str, RateLimiter] = {}
        self._registry_lock = threading.Lock()

    def get_limiter(self, user_id: str) -> RateLimiter:
        limiter = self._limiters.get(user_id)
        if limiter is not None:
            return limiter

        with self._registry_lock:
            limiter = self._limiters.get(user_id)
            if limiter is None:
                limiter = self._create_limiter()
                self._limiters[user_id] = limiter
            return limiter

    def allow_request(self, user_id: str) -> bool:
        return self.get_limiter(user_id).allow_request()

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
