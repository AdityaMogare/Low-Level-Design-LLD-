# Sliding Window Metrics

Stream counting and aggregation over sliding windows (time- or count-based).

## Problems Covered

| # | Problem | Module | LC |
|---|---|---|---|
| 4 | API hit counter (last 5 min) | `hit_counter.py`, `manager.py` | 362 |
| 6 | Max in moving time window | `max_sliding_window.py` | 239 |
| 7 | Moving average last N readings | `moving_average.py` | 346 |
| 10 | Max price in last K ticks | `ticker_max.py` | — |

## Architecture

```
TimeSeriesCounter (ABC)
└── HitCounter  → TimestampWindow (from common/)

StreamAggregator (ABC)
├── MaxSlidingWindow  → monotonic deque (time window)
├── MovingAverage     → deque + running sum (count window)
└── TickerMax         → monotonic deque (count window)

HitCounterManager → per-key HitCounter registry
```

## Run Tests

```bash
cd src
python -m unittest sliding_window_metrics.test_sliding_window_metrics -v
```

Time is mocked via `unittest.mock.patch` on `time.monotonic`. No `time.sleep()`.
