# Gap 31 — Graceful Degradation: Evidence

## Status: ✅ Implemented

**Date:** 2025-07-13
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Implementation Summary

### Module: `src/codex/resilience/degradation.py`

| Component | Description |
|-----------|-------------|
| `GracefulDegradation` | Decorator + context manager for failure-safe code |
| `DegradationError` | Raised when a failure occurs and no fallback is set |

### GracefulDegradation Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `fallback` | *(none)* | Value or zero-arg callable returned on failure; absent → `DegradationError` |
| `exceptions` | `(Exception,)` | Tuple of exception types to catch |
| `logger_name` | `None` | Logger name (defaults to module logger) |

### Usage Patterns

**Decorator (static fallback)**
```python
@GracefulDegradation(fallback=0)
def fetch_metric() -> int:
    return remote_api.get()
```

**Decorator (callable fallback)**
```python
@GracefulDegradation(fallback=lambda: cache.get("last_known"))
def fetch_value():
    return live_service.fetch()
```

**Context manager**
```python
with GracefulDegradation(fallback="N/A") as dg:
    dg.result = risky_call()
value = dg.result  # "N/A" if risky_call() raised
```

**No fallback (strict mode)**
```python
@GracefulDegradation()
def critical_path():
    return must_succeed()
# → raises DegradationError wrapping the original exception
```

### Key Design Decisions

- **Falsy fallback values** (`0`, `False`, `None`, `""`, `[]`) work correctly
  because the sentinel is a private `object()` instance, not `None`.
- **Callable fallback** is called lazily at failure time — useful for cache
  lookups or dynamic defaults.
- **`DegradationError.original`** always carries the underlying exception for
  logging/debugging.
- **Exception filtering** via `exceptions=` parameter allows targeting only
  specific failure types (e.g. `(requests.ConnectionError,)`).
- **Context manager suppression**: returns `True` from `__exit__` to suppress
  the matched exception; non-matching types propagate normally.

---

## Test Coverage: `tests/unit/test_degradation.py`

| # | Test | Description |
|---|------|-------------|
| 1 | `test_decorator_returns_real_value_on_success` | Success path — real value returned |
| 2 | `test_decorator_returns_fallback_on_exception` | Static fallback on exception |
| 3 | `test_decorator_invokes_callable_fallback` | Callable fallback is called |
| 4 | `test_decorator_no_fallback_raises_degradation_error` | No fallback → DegradationError with `.original` |
| 5 | `test_context_manager_captures_result_on_success` | CM success — result captured |
| 6 | `test_context_manager_sets_fallback_on_exception` | CM failure — fallback set |
| 7 | `test_context_manager_no_fallback_raises_degradation_error` | CM no fallback → DegradationError |
| 8 | `test_non_matching_exception_propagates` | Non-matching type not caught (decorator) |
| 9 | `test_context_manager_non_matching_exception_propagates` | Non-matching type not caught (CM) |
| 10 | `test_degradation_error_is_exception` | `DegradationError` subclasses `Exception` |
| 11–15 | `test_falsy_fallback_values_are_returned` | Parametrized: `0`, `False`, `None`, `""`, `[]` all work |

**Total: 15 tests, all passing**

---

## Test Run Output

```
tests/unit/test_degradation.py ...............  [15 passed]
```

---

## Integration Points

`GracefulDegradation` is available from `src/codex/resilience/__init__.py`
and can wrap any monitoring/alerting call where failure should not crash the
main workflow:

```python
from codex.resilience import GracefulDegradation

class TrainingAlertManager:
    def dispatch(self, event):
        with GracefulDegradation(fallback=False) as dg:
            dg.result = self._fan_out(event)
        return dg.result
```

Or as a decorator on the performance monitor:

```python
from codex.resilience import GracefulDegradation

@GracefulDegradation(fallback=None)
def record_metric(name: str, value: float) -> None:
    prometheus_gauge.labels(name).set(value)
```
