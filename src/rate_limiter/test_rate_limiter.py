"""Unit tests for the rate-limiter trio. Time is always mocked — never sleep."""

from __future__ import annotations

import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from rate_limiter.dedup_logger import DedupLogger
from rate_limiter.interfaces import RateLimiterType
from rate_limiter.leaky_bucket import LeakyBucketRateLimiter
from rate_limiter.manager import RateLimiterManager
from rate_limiter.sliding_window import SlidingWindowRateLimiter
from rate_limiter.token_bucket import TokenBucketRateLimiter


class SlidingWindowTests(unittest.TestCase):
    @patch("rate_limiter.sliding_window.time.monotonic")
    def test_burst_up_to_limit_then_rejects(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 100.0
        limiter = SlidingWindowRateLimiter(max_requests=3, window_size_seconds=10.0)

        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

    @patch("rate_limiter.sliding_window.time.monotonic")
    def test_expired_timestamps_free_capacity(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 100.0
        limiter = SlidingWindowRateLimiter(max_requests=2, window_size_seconds=5.0)

        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

        mock_monotonic.return_value = 105.1
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

    @patch("rate_limiter.sliding_window.time.monotonic")
    def test_partial_window_expiry(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 100.0
        limiter = SlidingWindowRateLimiter(max_requests=2, window_size_seconds=10.0)
        self.assertTrue(limiter.allow_request())

        mock_monotonic.return_value = 105.0
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

        # First request at t=100 expires; second at t=105 remains.
        mock_monotonic.return_value = 110.1
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())


class TokenBucketTests(unittest.TestCase):
    @patch("rate_limiter.token_bucket.time.monotonic")
    def test_burst_consumes_capacity(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1.0)

        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

    @patch("rate_limiter.token_bucket.time.monotonic")
    def test_lazy_refill_restores_tokens(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate=1.0)

        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

        mock_monotonic.return_value = 2.0
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

    @patch("rate_limiter.token_bucket.time.monotonic")
    def test_refill_never_exceeds_capacity(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        limiter = TokenBucketRateLimiter(capacity=2, refill_rate=10.0)

        self.assertTrue(limiter.allow_request())
        mock_monotonic.return_value = 100.0
        # Even after a long idle period, only capacity tokens exist.
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())


class LeakyBucketTests(unittest.TestCase):
    @patch("rate_limiter.leaky_bucket.time.monotonic")
    def test_burst_fills_queue_then_rejects(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        limiter = LeakyBucketRateLimiter(capacity=3, drain_rate=1.0)

        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

    @patch("rate_limiter.leaky_bucket.time.monotonic")
    def test_drain_frees_capacity(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        limiter = LeakyBucketRateLimiter(capacity=2, drain_rate=1.0)

        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

        mock_monotonic.return_value = 2.0
        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

    @patch("rate_limiter.leaky_bucket.time.monotonic")
    def test_partial_drain(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        limiter = LeakyBucketRateLimiter(capacity=2, drain_rate=2.0)

        self.assertTrue(limiter.allow_request())
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())

        # 0.5s * 2 req/s = 1 request drained.
        mock_monotonic.return_value = 0.5
        self.assertTrue(limiter.allow_request())
        self.assertFalse(limiter.allow_request())


class CompositeKeyTests(unittest.TestCase):
    @patch("rate_limiter.sliding_window.time.monotonic")
    def test_endpoints_are_isolated_per_user(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        manager = RateLimiterManager(
            RateLimiterType.SLIDING_WINDOW,
            max_requests=1,
            window_size_seconds=10.0,
        )

        self.assertTrue(manager.allow_request("alice", "/api/a"))
        self.assertFalse(manager.allow_request("alice", "/api/a"))
        self.assertTrue(manager.allow_request("alice", "/api/b"))
        self.assertTrue(manager.allow_request("bob", "/api/a"))


class DedupLoggerTests(unittest.TestCase):
    @patch("rate_limiter.dedup_logger.time.monotonic")
    def test_suppresses_duplicate_within_cooldown(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        logger = DedupLogger(cooldown_seconds=10.0)

        self.assertTrue(logger.should_log("error: timeout"))
        self.assertFalse(logger.should_log("error: timeout"))
        mock_monotonic.return_value = 9.9
        self.assertFalse(logger.should_log("error: timeout"))
        mock_monotonic.return_value = 10.0
        self.assertTrue(logger.should_log("error: timeout"))

    @patch("rate_limiter.dedup_logger.time.monotonic")
    def test_different_messages_independent(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        logger = DedupLogger(cooldown_seconds=10.0)

        self.assertTrue(logger.should_log("msg-a"))
        self.assertTrue(logger.should_log("msg-b"))
        self.assertFalse(logger.should_log("msg-a"))
        self.assertFalse(logger.should_log("msg-b"))


class ManagerIsolationTests(unittest.TestCase):
    @patch("rate_limiter.token_bucket.time.monotonic")
    def test_users_are_isolated(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        manager = RateLimiterManager(
            RateLimiterType.TOKEN_BUCKET,
            capacity=1,
            refill_rate=1.0,
        )

        self.assertTrue(manager.allow_request("alice"))
        self.assertFalse(manager.allow_request("alice"))
        self.assertTrue(manager.allow_request("bob"))
        self.assertFalse(manager.allow_request("bob"))

    def test_same_user_returns_same_limiter_instance(self) -> None:
        manager = RateLimiterManager(
            RateLimiterType.SLIDING_WINDOW,
            max_requests=5,
            window_size_seconds=1.0,
        )
        first = manager.get_limiter("user-1")
        second = manager.get_limiter("user-1")
        self.assertIs(first, second)


class ConcurrencyTests(unittest.TestCase):
    def test_sliding_window_never_over_admits_under_load(self) -> None:
        # Wide window so wall-clock duration of the test cannot expire entries.
        max_requests = 50
        limiter = SlidingWindowRateLimiter(
            max_requests=max_requests,
            window_size_seconds=3600.0,
        )
        workers = 32
        attempts_per_worker = 20

        admitted = 0
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(limiter.allow_request)
                for _ in range(workers * attempts_per_worker)
            ]
            for future in as_completed(futures):
                if future.result():
                    admitted += 1

        self.assertEqual(admitted, max_requests)

    def test_manager_double_checked_locking_under_load(self) -> None:
        manager = RateLimiterManager(
            RateLimiterType.LEAKY_BUCKET,
            capacity=100,
            drain_rate=1.0,
        )
        user_id = "hot-user"

        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(manager.get_limiter, user_id) for _ in range(64)]
            limiters = [future.result() for future in as_completed(futures)]

        first = limiters[0]
        for limiter in limiters[1:]:
            self.assertIs(limiter, first)


if __name__ == "__main__":
    unittest.main()
