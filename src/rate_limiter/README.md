# Rate Limiter (LLD)

Admission control: three classic algorithms plus dedup logger and multi-endpoint quotas.

## Problems Covered

| # | Problem | Module | LC |
|---|---|---|---|
| 1 | Sliding-window rate limiter | `sliding_window.py` | — |
| 2 | Token bucket | `token_bucket.py` | — |
| 3 | Leaky bucket | `leaky_bucket.py` | — |
| 5 | Per-user quota per endpoint | `manager.py` (`endpoint` param) | — |
| 9 | Logger dedup within 10s | `dedup_logger.py` | 359 |

Shared primitive: `common/timestamp_window.py` (used by sliding window and hit counter).

## Architecture

```
RateLimiter (ABC)
├── SlidingWindowRateLimiter  → TimestampWindow
├── TokenBucketRateLimiter    → lazy refill
└── LeakyBucketRateLimiter    → lazy drain

RateLimiterManager → key = user_id or f"{user_id}:{endpoint}"
DedupLogger        → HashMap<message, last_seen>
```

## Run Tests

```bash
cd src
python -m unittest rate_limiter.test_rate_limiter -v
```

Time is mocked via `unittest.mock.patch` on `time.monotonic`. No `time.sleep()`.
