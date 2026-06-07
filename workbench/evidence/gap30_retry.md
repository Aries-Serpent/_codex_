# Gap 30 — Exponential Backoff Retry Logic

**Status:** ✅ Implemented
**Date:** 2025-01-01
**Branch:** `copilot/explore-codebase-and-create-plan`

---

## Summary

Implemented a production-grade exponential backoff retry utility as
`src/codex/resilience/retry.py`, wired it into the Slack alerting channel's
HTTP webhook POST, exported it through the `codex.resilience` package, and
verified with 9 unit tests (all passing, all mocking `time.sleep`).

---

## Files Changed

| File | Change |
|------|--------|
| `src/codex/resilience/retry.py` | **New** — `retry_with_backoff` decorator + `RetryExhausted` exception |
| `src/codex/resilience/__init__.py` | **Updated** — exports `retry_with_backoff` and `RetryExhausted` |
| `src/codex/alerting/slack.py` | **Updated** — webhook POST wrapped with `_retry_send` (3 retries, 1–30 s backoff) |
| `tests/unit/test_retry.py` | **New** — 9 unit tests, all `time.sleep`-mocked |

---

## Public API

```python
from codex.resilience import retry_with_backoff, RetryExhausted
# or directly:
from codex.resilience.retry import retry_with_backoff, RetryExhausted
```

### `retry_with_backoff(max_retries, base_delay, max_delay, jitter, exceptions)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_retries` | `int` | `3` | Extra attempts after first failure |
| `base_delay` | `float` | `1.0` | Initial delay in seconds |
| `max_delay` | `float` | `60.0` | Upper cap on computed delay |
| `jitter` | `float` | `0.1` | Max random jitter added to each delay |
| `exceptions` | `tuple[type[Exception], ...]` | `(Exception,)` | Exception types to retry on |

Returns a decorator. Works as both a decorator and a direct call wrapper.

**Delay formula:**

```
delay = min(base_delay * 2**attempt + random.uniform(0, jitter), max_delay)
```

### `RetryExhausted`

Raised when all attempts are exhausted. Attributes:

- `attempts` — total number of attempts made (= `max_retries + 1`)
- `__cause__` — last exception that caused the failure

---

## Usage Examples

```python
# --- Decorator usage ---
@retry_with_backoff(max_retries=3, base_delay=0.5)
def call_api() -> dict:
    return requests.get("https://api.example.com").json()

# --- Direct wrapper ---
result = retry_with_backoff(max_retries=2)(my_func)(arg1, arg2)

# --- Catching exhaustion ---
try:
    call_api()
except RetryExhausted as exc:
    logger.error("All retries failed: %s", exc.__cause__)
```

---

## Wired Integration — `SlackChannel.send()`

`src/codex/alerting/slack.py` now wraps its `urllib.request.urlopen` call
with a module-level `_retry_send` decorator configured for:

```python
_retry_send = retry_with_backoff(
    max_retries=3,
    base_delay=1.0,
    max_delay=30.0,
    jitter=0.25,
    exceptions=(urllib.error.URLError,),
)
```

Transient network errors (`URLError`) are retried up to 3 extra times.
After all retries, `RetryExhausted` is caught and logged as a warning
(channel returns `False`, not crashing the training pipeline).

---

## Test Results

```
tests/unit/test_retry.py .........                         [100%]
9 passed, 1 warning in 0.27s
```

Tests cover:

| # | Test | What it verifies |
|---|------|-----------------|
| 1 | `test_succeeds_on_first_attempt` | No sleep called when function succeeds immediately |
| 2 | `test_retries_and_eventually_succeeds` | Function is called 3× when first 2 attempts fail |
| 3 | `test_raises_retry_exhausted_when_all_retries_fail` | `RetryExhausted` raised; `__cause__` is the original error |
| 4 | `test_backoff_delays_follow_exponential_formula` | `sleep` called with `base * 2**attempt` (jitter=0) |
| 5 | `test_max_delay_cap_is_respected` | `sleep` never exceeds `max_delay` |
| 6 | `test_non_retryable_exception_propagates_immediately` | Exceptions outside `exceptions` tuple skip retries |
| 7 | `test_retry_exhausted_attempts_count` | `RetryExhausted.attempts == max_retries + 1` |
| 8 | `test_decorator_preserves_function_metadata` | `functools.wraps` preserves `__name__` and `__doc__` |
| 9 | `test_jitter_adds_noise_within_bounds` | Sleep value in `[base_delay, base_delay + jitter]` range |
