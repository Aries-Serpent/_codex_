# Gap 29 — Circuit Breakers: Evidence

## Status: ✅ Implemented

**Date:** 2025-07-13
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Implementation Summary

### Module: `src/codex/resilience/circuit_breaker.py`

Implements the classic three-state circuit-breaker pattern:

| Component | Description |
|-----------|-------------|
| `CircuitState` | Enum with values `CLOSED`, `OPEN`, `HALF_OPEN` |
| `CircuitBreaker` | Thread-safe circuit breaker class |
| `CircuitOpenError` | Exception raised when circuit is OPEN; carries `retry_after` |

### CircuitBreaker Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `failure_threshold` | `5` | Consecutive failures to open the circuit |
| `recovery_timeout` | `60.0` | Seconds in OPEN state before probing (→ HALF_OPEN) |
| `success_threshold` | `2` | Consecutive successes in HALF_OPEN to close circuit |
| `name` | `"circuit_breaker"` | Label used in log messages |

### State Machine

```
CLOSED  ──(failures >= threshold)──→  OPEN
  ↑                                     │
  │                              (recovery_timeout elapsed)
  │                                     ↓
  └──(successes >= success_threshold)── HALF_OPEN
                                         │
                              (any failure)──→ OPEN
```

### Key Design Decisions

- **Thread-safe**: all state mutations protected by `threading.Lock`
- **Non-blocking I/O**: the wrapped function is called *outside* the lock
- **Auto-transition**: `OPEN → HALF_OPEN` happens lazily on the next `state` access or `call()`
- **Failure reset**: a success in CLOSED state resets the failure counter
- **Re-raise**: original exceptions are always re-raised so callers can distinguish failure types
- **Invalid args**: `ValueError` on non-positive thresholds/timeouts at construction time

---

## Test Coverage: `tests/unit/test_circuit_breaker.py`

| # | Test | Description |
|---|------|-------------|
| 1 | `test_initial_state_is_closed` | Default state is CLOSED |
| 2 | `test_success_keeps_circuit_closed` | 10 successes — stays CLOSED |
| 3 | `test_failures_below_threshold_keep_circuit_closed` | 4/5 failures — stays CLOSED |
| 4 | `test_failures_at_threshold_open_circuit` | 3/3 failures — OPENS |
| 5 | `test_open_circuit_raises_circuit_open_error` | Subsequent calls → CircuitOpenError |
| 6 | `test_circuit_open_error_has_retry_after` | `retry_after` is populated and ≤ recovery_timeout |
| 7 | `test_circuit_open_error_is_exception` | `CircuitOpenError` is an `Exception` subclass |
| 8 | `test_open_transitions_to_half_open_after_timeout` | OPEN → HALF_OPEN after 50ms timeout |
| 9 | `test_half_open_closes_after_consecutive_successes` | HALF_OPEN → CLOSED after 2 successes |
| 10 | `test_half_open_failure_reopens_circuit` | Failure in HALF_OPEN → back to OPEN |
| 11 | `test_reset_closes_open_circuit` | `reset()` returns to CLOSED |
| 12 | `test_reset_allows_calls_again` | Calls succeed after reset |
| 13 | `test_success_resets_failure_count_in_closed` | Success clears the failure counter |
| 14–16 | `test_invalid_constructor_raises_value_error` | Parametrized: 3 invalid arg combinations |
| 17 | `test_concurrent_calls_do_not_corrupt_state` | 50 threads — no state corruption |

**Total: 17 tests, all passing**

---

## Test Run Output

```
tests/unit/test_circuit_breaker.py .................  [17 passed]
```

---

## Integration Points

The `CircuitBreaker` is exported from `src/codex/resilience/__init__.py` and
can be applied as an optional wrapper around any external HTTP client calls,
for example in `src/codex/alerting/slack.py`:

```python
from codex.resilience import CircuitBreaker, CircuitOpenError

_cb = CircuitBreaker(name="slack_webhook", failure_threshold=5, recovery_timeout=60)

def send(self, event):
    try:
        return _cb.call(self._post_to_slack, event)
    except CircuitOpenError:
        logger.warning("Slack webhook circuit is open — skipping alert")
        return False
```
