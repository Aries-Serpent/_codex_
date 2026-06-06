# /// script
# dependencies = []
# requires-python = ">=3.10"
# description = "Runnable demo: CircuitBreaker, retry_with_backoff, GracefulDegradation"
# ///
"""Resilience Primitives Demo — Gap 44: Interactive Documentation.

Demonstrates:
  - CircuitBreaker: CLOSED → OPEN on failures → HALF_OPEN → CLOSED recovery
  - retry_with_backoff: succeeding after flaky initial calls
  - GracefulDegradation: decorator and context-manager fallback patterns

Run with:
    python docs/examples/resilience_demo.py
"""

from __future__ import annotations

import sys
import os

# Ensure the repo src is on the path when run directly
_REPO_ROOT = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.insert(0, os.path.join(_REPO_ROOT, "src"))

from codex.resilience import (
    CircuitBreaker,
    CircuitOpenError,
    GracefulDegradation,
    DegradationError,
    retry_with_backoff,
    RetryExhausted,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sep(title: str = "") -> None:
    if title:
        pad = (60 - len(title) - 2) // 2
        tail = 60 - pad - len(title) - 2
        print(f"{'=' * pad} {title} {'=' * tail}")
    else:
        print("=" * 60)


def _row(label: str, value: object) -> None:
    print(f"  {label:<32} {value}")


# ---------------------------------------------------------------------------
# Circuit Breaker demo
# ---------------------------------------------------------------------------

def demo_circuit_breaker() -> None:
    _sep("CIRCUIT BREAKER")

    # Create a breaker that trips after 3 consecutive failures
    cb = CircuitBreaker(
        failure_threshold=3,
        recovery_timeout=0.01,   # very short for demo purposes
        success_threshold=2,
        name="demo-service",
    )

    print(f"\n  Config: failure_threshold=3, recovery_timeout=0.01s, success_threshold=2")
    _row("Initial state", cb.state.name)

    # ---- Simulate healthy calls ----
    print("\n  [Phase 1] Healthy calls (circuit stays CLOSED)")
    for i in range(3):
        result = cb.call(lambda: "ok")
        print(f"    call {i+1}: result={result!r}  state={cb.state.name}")

    # ---- Simulate failing calls until circuit trips ----
    print("\n  [Phase 2] Failing calls (circuit should open after 3rd failure)")

    def _always_fail() -> None:
        raise ConnectionError("Service unavailable")

    for i in range(3):
        try:
            cb.call(_always_fail)
        except ConnectionError:
            print(f"    failure {i+1}: ConnectionError caught  state={cb.state.name}")

    _row("State after 3 failures", cb.state.name)

    # ---- Call when OPEN — should raise CircuitOpenError ----
    print("\n  [Phase 3] Call while OPEN (CircuitOpenError expected)")
    try:
        cb.call(lambda: "should not reach here")
    except CircuitOpenError as exc:
        print(f"    ✓ CircuitOpenError raised: {exc}")
    _row("State", cb.state.name)

    # ---- Wait for recovery timeout and let HALF_OPEN probe succeed ----
    import time
    time.sleep(0.02)   # wait for recovery_timeout to elapse
    print("\n  [Phase 4] Recovery: OPEN → HALF_OPEN → CLOSED")
    print(f"    State after timeout elapsed: {cb.state.name}")

    # Provide 2 successful calls to satisfy success_threshold
    for i in range(2):
        result = cb.call(lambda: "probe-ok")
        print(f"    success probe {i+1}: result={result!r}  state={cb.state.name}")

    _row("Final state", cb.state.name)
    _sep()


# ---------------------------------------------------------------------------
# Retry with backoff demo
# ---------------------------------------------------------------------------

def demo_retry() -> None:
    _sep("RETRY WITH BACKOFF")

    # A function that fails the first N times then succeeds
    call_count = [0]

    def _flaky_service() -> str:
        call_count[0] += 1
        if call_count[0] < 3:
            raise TimeoutError(f"Timeout on attempt {call_count[0]}")
        return f"success on attempt {call_count[0]}"

    print("\n  [Scenario A] Succeeds after 2 failures (max_retries=3, base_delay=0)")
    call_count[0] = 0

    @retry_with_backoff(max_retries=3, base_delay=0.0, jitter=0.0)
    def reliable_fetch() -> str:
        return _flaky_service()

    result = reliable_fetch()
    _row("Result", result)
    _row("Total calls made", call_count[0])

    # Scenario B: exhausted retries
    print("\n  [Scenario B] All retries exhausted → RetryExhausted raised")
    always_fail_count = [0]

    @retry_with_backoff(max_retries=2, base_delay=0.0, jitter=0.0)
    def always_fails() -> str:
        always_fail_count[0] += 1
        raise RuntimeError("permanent failure")

    try:
        always_fails()
    except RetryExhausted as exc:
        _row("RetryExhausted.attempts", exc.attempts)
        _row("Root cause", str(exc.__cause__))
        _row("Total calls made", always_fail_count[0])

    _sep()


# ---------------------------------------------------------------------------
# Graceful Degradation demo
# ---------------------------------------------------------------------------

def demo_graceful_degradation() -> None:
    _sep("GRACEFUL DEGRADATION")

    # ---- Decorator usage ----
    print("\n  [Mode 1] Decorator — returns fallback value on exception")

    @GracefulDegradation(fallback="N/A")
    def fetch_external_metric() -> str:
        raise ConnectionError("External API unreachable")

    @GracefulDegradation(fallback=0.0)
    def fetch_score() -> float:
        raise ValueError("Score service timeout")

    @GracefulDegradation(fallback={"status": "degraded"})
    def get_health() -> dict:
        raise RuntimeError("Health endpoint down")

    result_metric = fetch_external_metric()
    result_score = fetch_score()
    result_health = get_health()

    _row("fetch_external_metric()", result_metric)
    _row("fetch_score()", result_score)
    _row("get_health()", result_health)

    # A function that actually succeeds
    @GracefulDegradation(fallback="fallback-value")
    def working_function() -> str:
        return "real-value"

    _row("working_function()", working_function())

    # ---- Context manager usage ----
    print("\n  [Mode 2] Context manager — captures result or falls back")

    with GracefulDegradation(fallback=-1) as ctx:
        ctx.result = int("not-a-number")   # will raise ValueError
    _row("ctx.result (after ValueError)", ctx.result)

    with GracefulDegradation(fallback="fallback-response") as ctx2:
        ctx2.result = "computed-response"   # succeeds
    _row("ctx2.result (success path)", ctx2.result)

    # ---- No fallback — raises DegradationError ----
    print("\n  [Mode 3] No fallback set → DegradationError raised")

    @GracefulDegradation()
    def critical_fail() -> str:
        raise RuntimeError("critical subsystem error")

    try:
        critical_fail()
    except DegradationError as exc:
        print(f"    ✓ DegradationError raised")
        _row("original cause", str(exc.__cause__))

    _sep()


if __name__ == "__main__":
    _sep("RESILIENCE PRIMITIVES DEMO")
    print("  Module: codex.resilience")
    print("  Covers: CircuitBreaker / retry_with_backoff / GracefulDegradation")
    _sep()
    print()

    demo_circuit_breaker()
    print()
    demo_retry()
    print()
    demo_graceful_degradation()

    print()
    _sep("DEMO COMPLETE")
    print("  ✓ CircuitBreaker: CLOSED→OPEN→HALF_OPEN→CLOSED cycle passed")
    print("  ✓ retry_with_backoff: flaky-then-success + exhausted cases passed")
    print("  ✓ GracefulDegradation: decorator, context-manager, no-fallback passed")
    _sep()
