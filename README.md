# Low-Level Design (LLD) Practice

Interview-oriented machine-coding problems, one domain per package under `src/`.

## Strategy

1. **Constraint analysis** — concurrency, memory, extensibility.
2. **Pattern identification** — Strategy, Factory, Observer, etc., only when they earn their keep.
3. **Architecture first** — entities, interfaces, then implementations.
4. **Implementation** — production-shaped, thread-safe where required.
5. **Tests** — edge cases, isolation, concurrency; mock time, never sleep.

## Domains

| Package | Focus | Status |
|---|---|---|
| [`src/rate_limiter/`](src/rate_limiter/) | Sliding Window, Token Bucket, Leaky Bucket | Implemented |
| [`src/parking_lot/`](src/parking_lot/) | Physical systems / allocation | Placeholder |
| [`src/splitwise/`](src/splitwise/) | Ledger / graph settle-up | Placeholder |

## Rate Limiter Quick Start

```bash
cd src
python -m unittest rate_limiter.test_rate_limiter -v
```

## Layout

```
├── README.md
├── .gitignore
├── requirements.txt
└── src/
    ├── rate_limiter/
    ├── parking_lot/
    └── splitwise/
```
