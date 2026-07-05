"""Unit tests for debounce and throttle. Time is mocked — never sleep."""

from __future__ import annotations

import unittest
from concurrent.futures import ThreadPoolExecutor, as_completed
from unittest.mock import patch

from event_shaping.debounce import DebounceGate
from event_shaping.throttle import ThrottleGate


class DebounceTests(unittest.TestCase):
    @patch("event_shaping.debounce.time.monotonic")
    def test_fires_after_quiet_period(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        gate = DebounceGate(quiet_period_seconds=1.0)

        self.assertFalse(gate.should_execute())
        mock_monotonic.return_value = 0.5
        self.assertFalse(gate.should_execute())
        mock_monotonic.return_value = 1.6
        self.assertTrue(gate.should_execute())

    @patch("event_shaping.debounce.time.monotonic")
    def test_reset_clears_state(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        gate = DebounceGate(quiet_period_seconds=1.0)
        gate.should_execute()
        gate.reset()
        mock_monotonic.return_value = 5.0
        self.assertFalse(gate.should_execute())


class ThrottleTests(unittest.TestCase):
    @patch("event_shaping.throttle.time.monotonic")
    def test_leading_edge_at_most_once_per_interval(self, mock_monotonic) -> None:
        mock_monotonic.return_value = 0.0
        gate = ThrottleGate(interval_seconds=1.0)

        self.assertTrue(gate.should_execute())
        mock_monotonic.return_value = 0.3
        self.assertFalse(gate.should_execute())
        mock_monotonic.return_value = 0.9
        self.assertFalse(gate.should_execute())
        mock_monotonic.return_value = 1.0
        self.assertTrue(gate.should_execute())


class EventShapingConcurrencyTests(unittest.TestCase):
    @patch("event_shaping.throttle.time.monotonic", return_value=0.0)
    def test_throttle_never_over_fires_under_load(self, _mock_monotonic) -> None:
        gate = ThrottleGate(interval_seconds=3600.0)
        allowed = 0

        with ThreadPoolExecutor(max_workers=32) as executor:
            futures = [executor.submit(gate.should_execute) for _ in range(200)]
            for future in as_completed(futures):
                if future.result():
                    allowed += 1

        self.assertEqual(allowed, 1)


if __name__ == "__main__":
    unittest.main()
