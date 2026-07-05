# Event Shaping

Debounce and throttle for rapidly firing events.

## Problems Covered

| # | Problem | Module |
|---|---|---|
| 8 | Debounce / throttle | `debounce.py`, `throttle.py` |

## Semantics

- **DebounceGate** — trailing edge: fires only after `quiet_period_seconds` with no new events.
- **ThrottleGate** — leading edge: at most one execution per `interval_seconds`.

## Run Tests

```bash
cd src
python -m unittest event_shaping.test_event_shaping -v
```

Time is mocked via `unittest.mock.patch` on `time.monotonic`. No `time.sleep()`.
