# Rate Limiter (LLD)

Implement three classic algorithms behind a shared strategy interface, with a per-user manager for concurrent clients.

## Algorithms

| Strategy | Core idea | Memory |
|---|---|---|
| **Sliding Window** | Deque of timestamps; drop expired entries before admit | O(N) in-window requests |
| **Token Bucket** | Tokens + last refill; lazy refill from elapsed time | O(1) |
| **Leaky Bucket** | Queue water-level; lazy drain at constant rate | O(1) |

## 5-Step Breakdown

### 1. Constraint Analysis

- **Sliding Window** stores every in-window timestamp → memory grows with burst size; eviction is O(expired) amortized.
- **Token / Leaky Bucket** keep scalar state only → O(1) memory, but lose exact per-request history.
- Mutable fields (`timestamps`, `tokens` / `queue_size`, clocks) are protected by a per-limiter `threading.Lock`.
- The manager registry (`user_id → limiter`) is protected by double-checked locking on a registry lock.

### 2. Pattern Identification

- **Strategy:** `RateLimiter` ABC; each algorithm is a concrete strategy with `allow_request() -> bool`.
- **Factory / Manager:** `RateLimiterManager` creates the configured strategy per user and isolates quotas.

### 3. Architecture

```
RateLimiter (ABC)
├── SlidingWindowRateLimiter  (max_requests, window_size_seconds, timestamps)
├── TokenBucketRateLimiter    (capacity, refill_rate, tokens, last_refill_time)
└── LeakyBucketRateLimiter    (capacity, drain_rate, queue_size, last_drain_time)

RateLimiterManager
└── user_id → RateLimiter instance (lazy, thread-safe create)
```

### 4. Implementation Map

| File | Role |
|---|---|
| `interfaces.py` | `RateLimiter` ABC, `RateLimiterType` |
| `sliding_window.py` | Deque timestamp strategy |
| `token_bucket.py` | Lazy-refill token strategy |
| `leaky_bucket.py` | Lazy-drain queue strategy |
| `manager.py` | Per-user factory/context |
| `test_rate_limiter.py` | Burst, refill/drain, isolation, concurrency |

### 5. Testing

```bash
cd src
python -m unittest rate_limiter.test_rate_limiter -v
```

Time is advanced with `unittest.mock.patch` on `time.monotonic`. No `time.sleep()`.
