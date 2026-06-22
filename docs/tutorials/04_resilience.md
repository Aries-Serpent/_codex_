# Tutorial 04 — Building Resilient ML Services

**Last Updated:** 2026-06-22

**Estimated time:** 25 minutes  
**Prerequisites:** Python 3.10+, `_codex_` on `PYTHONPATH`

---

## Why resilience matters in ML services

ML services in production routinely call:

- **Feature stores** — can time out under load
- **External APIs** — third-party rate limits, temporary outages
- **Model registries** — network blips during weight downloads
- **Monitoring endpoints** — non-critical but noisy when they fail

Without protection, a single failing dependency can cascade into a full service
outage.  The `codex.resilience` module provides three complementary primitives
that compose together for production-grade fault tolerance:

| Primitive | Role |
|-----------|------|
| `CircuitBreaker` | Stops hammering a failing service; auto-recovers |
| `retry_with_backoff` | Handles transient failures with exponential backoff |
| `GracefulDegradation` | Returns a safe fallback instead of crashing |

---

## Part 1 — `CircuitBreaker`

The circuit breaker implements the classic three-state pattern:

```
CLOSED ──(N failures)──► OPEN ──(timeout elapsed)──► HALF_OPEN
  ▲                                                       │
  └─────────────────(M successes)────────────────────────┘
```

- **CLOSED** — normal operation; failures are counted.
- **OPEN** — calls are rejected immediately with `CircuitOpenError` until
  the recovery timeout elapses.
- **HALF_OPEN** — a limited trial: consecutive successes close the circuit;
  any failure re-opens it.

### Decorator pattern

```python
from codex.resilience import CircuitBreaker, CircuitOpenError
import requests

# One circuit breaker per downstream service
feature_store_cb = CircuitBreaker(
    failure_threshold=3,    # open after 3 consecutive failures
    recovery_timeout=30,    # wait 30 s before trying again
    success_threshold=2,    # close after 2 successes in HALF_OPEN
    name="feature_store",
)

def get_features(user_id: str) -> dict:
    try:
        return feature_store_cb.call(
            requests.get,
            f"https://features.internal/user/{user_id}",
            timeout=2,
        ).json()
    except CircuitOpenError as exc:
        # Circuit is open — use a cached or default value
        print(f"Feature store unavailable (retry in ~{exc.retry_after:.0f}s)")
        return {"user_id": user_id, "segment": "default"}
    except requests.RequestException:
        # Network error — circuit breaker has already incremented failure count
        return {"user_id": user_id, "segment": "default"}
```

## Checking the state

```python
from codex.resilience import CircuitState

print(feature_store_cb.state)         # CircuitState.CLOSED
print(feature_store_cb.state.value)   # "closed"

if feature_store_cb.state is CircuitState.OPEN:
    print("Circuit is open — skipping call")
```

### Manual reset

Useful during incident recovery:

```python
feature_store_cb.reset()   # force back to CLOSED
```

---

## Part 2 — `retry_with_backoff`

Use `retry_with_backoff` for **transient** failures — network blips, HTTP 429
rate limits, or temporary service unavailability where the call *will* succeed
if you try again in a moment.

The delay before attempt *n* (0-indexed) follows:

```
delay = min(base_delay × 2ⁿ + jitter, max_delay)
```

### Decorator usage

```python
from codex.resilience import retry_with_backoff, RetryExhausted

@retry_with_backoff(
    max_retries=4,
    base_delay=0.5,     # 0.5 s, 1 s, 2 s, 4 s + jitter
    max_delay=10.0,
    jitter=0.2,
    exceptions=(IOError, TimeoutError),   # only retry these
)
def download_model_weights(uri: str) -> bytes:
    response = requests.get(uri, timeout=10)
    response.raise_for_status()
    return response.content


try:
    weights = download_model_weights("https://registry.internal/models/v3.pt")
except RetryExhausted as exc:
    print(f"Download failed after {exc.attempts} attempts: {exc.__cause__}")
    weights = load_from_local_cache()
```

### Direct wrapper (no decorator)

When you can't or don't want to decorate the function, wrap it inline:

```python
from codex.resilience import retry_with_backoff

retried_get = retry_with_backoff(max_retries=3, base_delay=1.0)(requests.get)

try:
    resp = retried_get("https://api.example.com/v1/predict", json=payload, timeout=5)
except RetryExhausted:
    resp = None
```

---

## Part 3 — `GracefulDegradation`

`GracefulDegradation` wraps non-critical code paths so that failures return a
safe fallback value instead of raising an exception.

### Decorator pattern

```python
from codex.resilience import GracefulDegradation

@GracefulDegradation(fallback={"explanation": "unavailable"})
def get_explanation(prediction_id: str) -> dict:
    """Fetch a costly SHAP explanation from the interpretability service."""
    return interpretability_api.explain(prediction_id)


# If the interpretability API is down, returns {"explanation": "unavailable"}
# instead of crashing
explanation = get_explanation("pred_abc123")
```

## Context manager pattern

Use the context manager when the degraded block is more complex than a single
function call:

```python
from codex.resilience import GracefulDegradation

with GracefulDegradation(fallback=0.5) as dg:
    dg.result = fetch_dynamic_threshold_from_config_service()

threshold = dg.result   # 0.5 if the config service was unreachable
```

### No fallback — convert to `DegradationError`

If you want to re-raise failures as a clean application error instead of a
raw library exception:

```python
from codex.resilience import GracefulDegradation, DegradationError

with GracefulDegradation() as dg:
    dg.result = critical_operation()
# raises DegradationError(original=<original exception>) on failure
```

---

## Part 4 — Combining All Three

The three primitives are designed to be layered.  Here is a production pattern
for a model inference endpoint that calls an external feature store:

```python
from codex.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    GracefulDegradation,
    retry_with_backoff,
    RetryExhausted,
)

# ── One circuit breaker per downstream service ────────────────────────────────
_cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60, name="feature_store")

# ── Retry for transient network errors ────────────────────────────────────────
@retry_with_backoff(max_retries=3, base_delay=0.5, exceptions=(IOError, TimeoutError))
def _fetch_features_raw(user_id: str) -> dict:
    return _cb.call(requests.get, f"https://features.svc/user/{user_id}", timeout=2).json()

# ── Graceful degradation if everything fails ──────────────────────────────────
@GracefulDegradation(fallback={"segment": "unknown", "tier": "free"})
def fetch_features(user_id: str) -> dict:
    try:
        return _fetch_features_raw(user_id)
    except (CircuitOpenError, RetryExhausted) as exc:
        raise RuntimeError(f"Feature store unavailable: {exc}") from exc


# ── Inference endpoint ────────────────────────────────────────────────────────
def predict(user_id: str) -> dict:
    features = fetch_features(user_id)   # always returns, even on full outage
    prediction = model.predict(features)
    return {"prediction": prediction, "features_source": "live" if features.get("tier") != "unknown" else "fallback"}
```

**What this buys you:**

1. Transient errors (network blip) → retried up to 3 times with backoff.
2. Sustained failure → circuit opens after 5 failures, saving downstream quota.
3. Circuit still open or all retries exhausted → `GracefulDegradation` returns
   a default feature set so inference can still proceed.
4. After 60 s, the circuit enters HALF_OPEN and automatically probes recovery.

---

## Testing Resilience Patterns

```python
import pytest
from unittest.mock import patch, MagicMock
from codex.resilience import CircuitBreaker, CircuitOpenError

def test_circuit_opens_after_threshold():
    cb = CircuitBreaker(failure_threshold=2, recovery_timeout=9999)
    failing = MagicMock(side_effect=IOError("down"))

    for _ in range(2):
        with pytest.raises(IOError):
            cb.call(failing)

    with pytest.raises(CircuitOpenError):
        cb.call(failing)   # third call → circuit is open
```

---

## Summary

| Situation | Tool |
|-----------|------|
| External service is flaky but usually recovers in < 1 s | `retry_with_backoff` |
| External service is down for minutes | `CircuitBreaker` |
| Non-critical path that should never crash the main flow | `GracefulDegradation` |
| All of the above in production | Layer all three |

---

> **See also:**  
> `src/codex/resilience/circuit_breaker.py` · `src/codex/resilience/retry.py` ·
> `src/codex/resilience/degradation.py`
>
> [← Tutorial 03 — Continuous Learning](03_continuous_learning.md)
