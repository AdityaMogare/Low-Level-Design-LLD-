# Low-Level Design (LLD) Practice

Interview-oriented machine-coding problems, one domain per package under `src/`.

## Strategy

1. **Constraint analysis** — concurrency, memory, extensibility.
2. **Pattern identification** — Strategy, Factory, Observer, etc., only when they earn their keep.
3. **Architecture first** — entities, interfaces, then implementations.
4. **Implementation** — production-shaped, thread-safe where required.
5. **Tests** — edge cases, isolation, concurrency; mock time, never sleep.

## Sliding Window / Time Track

| # | Problem | Package | LC | Status |
|---|---|---|---|---|
| 1 | Sliding-window rate limiter | `rate_limiter/` | — | Done |
| 2 | Token bucket | `rate_limiter/` | — | Done |
| 3 | Leaky bucket | `rate_limiter/` | — | Done |
| 4 | API hit counter (last 5 min) | `sliding_window_metrics/` | 362 | Done |
| 5 | Per-user quota per endpoint | `rate_limiter/` | — | Done |
| 6 | Max in moving window | `sliding_window_metrics/` | 239 | Done |
| 7 | Moving average last N | `sliding_window_metrics/` | 346 | Done |
| 8 | Debounce / throttle | `event_shaping/` | — | Done |
| 9 | Logger dedup 10s | `rate_limiter/` | 359 | Done |
| 10 | Stock ticker max K ticks | `sliding_window_metrics/` | — | Done |

## Other Domains

| Package | Focus | Status |
|---|---|---|
| [`src/parking_lot/`](src/parking_lot/) | Physical systems / allocation | Placeholder |
| [`src/splitwise/`](src/splitwise/) | Ledger / graph settle-up | Placeholder |

## Run All Tests

```bash
cd src
python -m unittest discover -v
```

## Layout

```
├── README.md
├── .gitignore
├── requirements.txt
└── src/
    ├── common/                  # Shared TimestampWindow primitive
    ├── rate_limiter/            # Admission control (#1–3, #5, #9)
    ├── sliding_window_metrics/  # Counters & aggregators (#4, #6, #7, #10)
    ├── event_shaping/           # Debounce / throttle (#8)
    ├── parking_lot/
    └── splitwise/
```
