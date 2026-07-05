"""Unit tests for sliding-window metrics. Time is mocked — never sleep."""

from __future__ import annotations

import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from sliding_window_metrics.hit_counter import HitCounter
from sliding_window_metrics.manager import HitCounterManager
from sliding_window_metrics.max_sliding_window import MaxSlidingWindow
from sliding_window_metrics.moving_average import MovingAverage
from sliding_window_metrics.ticker_max import TickerMax


class HitCounterTests(unittest.TestCase):
    @patch("sliding_window_metrics.hit_counter.time.monotonic")
    def test_counts_hits_in_window(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        counter = HitCounter(window_size_seconds=300.0)

        counter.record_hit()
        counter.record_hit()
        self.assertEqual(counter.count_in_window(), 2)

        mock_monotonic.return_value = 301.0
        self.assertEqual(counter.count_in_window(), 0)

    @patch("sliding_window_metrics.hit_counter.time.monotonic")
    def test_partial_expiry(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 100.0
        counter = HitCounter(window_size_seconds=60.0)
        counter.record_hit(100.0)

        mock_monotonic.return_value = 130.0
        counter.record_hit(130.0)
        self.assertEqual(counter.count_in_window(130.0), 2)

        mock_monotonic.return_value = 161.0
        self.assertEqual(counter.count_in_window(161.0), 1)


class HitCounterManagerTests(unittest.TestCase):
    @patch("sliding_window_metrics.hit_counter.time.monotonic")
    def test_keys_are_isolated(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        manager = HitCounterManager(window_size_seconds=300.0)

        manager.record_hit("api-a")
        manager.record_hit("api-a")
        manager.record_hit("api-b")

        self.assertEqual(manager.count_in_window("api-a"), 2)
        self.assertEqual(manager.count_in_window("api-b"), 1)


class MaxSlidingWindowTests(unittest.TestCase):
    @patch("sliding_window_metrics.max_sliding_window.time.monotonic")
    def test_max_in_time_window(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        window = MaxSlidingWindow(window_size_seconds=10.0)

        window.add(1.0)
        window.add(3.0)
        window.add(2.0)
        self.assertEqual(window.aggregate(), 3.0)

        mock_monotonic.return_value = 5.0
        window.add(4.0)
        self.assertEqual(window.aggregate(), 4.0)

        mock_monotonic.return_value = 11.0
        self.assertEqual(window.aggregate(), 4.0)

    @patch("sliding_window_metrics.max_sliding_window.time.monotonic")
    def test_expired_max_evicted(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        window = MaxSlidingWindow(window_size_seconds=5.0)
        window.add(10.0)

        mock_monotonic.return_value = 6.0
        window.add(3.0)
        self.assertEqual(window.aggregate(), 3.0)


class MovingAverageTests(unittest.TestCase):
    def test_average_of_last_n(self) -> None:
        avg = MovingAverage(window_size=3)
        avg.add(1.0)
        self.assertEqual(avg.aggregate(), 1.0)
        avg.add(2.0)
        self.assertEqual(avg.aggregate(), 1.5)
        avg.add(3.0)
        self.assertEqual(avg.aggregate(), 2.0)
        avg.add(4.0)
        self.assertEqual(avg.aggregate(), 3.0)


class TickerMaxTests(unittest.TestCase):
    def test_max_over_last_k_ticks(self) -> None:
        ticker = TickerMax(window_size=3)
        ticker.add(1.0)
        ticker.add(5.0)
        ticker.add(3.0)
        self.assertEqual(ticker.aggregate(), 5.0)

        ticker.add(2.0)
        self.assertEqual(ticker.aggregate(), 5.0)

        ticker.add(8.0)
        self.assertEqual(ticker.aggregate(), 8.0)


class MetricsConcurrencyTests(unittest.TestCase):
    def test_hit_counter_thread_safe(self) -> None:
        counter = HitCounter(window_size_seconds=3600.0)
        workers = 16
        hits_per_worker = 25

        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(counter.record_hit)
                for _ in range(workers * hits_per_worker)
            ]
            for future in as_completed(futures):
                future.result()

        self.assertEqual(counter.count_in_window(), workers * hits_per_worker)


if __name__ == "__main__":
    unittest.main()
