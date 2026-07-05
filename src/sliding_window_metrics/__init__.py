"""Sliding-window stream metrics: hit counter, max, moving average, ticker."""

from .hit_counter import HitCounter
from .interfaces import StreamAggregator, TimeSeriesCounter
from .manager import HitCounterManager, MetricsRegistry
from .max_sliding_window import MaxSlidingWindow
from .moving_average import MovingAverage
from .ticker_max import TickerMax

__all__ = [
    "TimeSeriesCounter",
    "StreamAggregator",
    "HitCounter",
    "HitCounterManager",
    "MetricsRegistry",
    "MaxSlidingWindow",
    "MovingAverage",
    "TickerMax",
]
