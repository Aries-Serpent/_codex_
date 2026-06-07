# ADR-002: Three-Layer Resilience: Circuit Breaker + Retry + Graceful Degradation

**Status:** Accepted
**Date:** 2025-01-15
**Deciders:** codex-ml platform team
**Technical Story:** Gap 29/30/31 — resilience layer for ML inference and external service calls

---

## Context

The _codex_ ML platform makes runtime calls to external services: model-serving
endpoints, feature stores, A/B experiment APIs, and downstream enrichment APIs.
These calls exhibit the following failure modes in production:

1. **Transient failures** — network hiccups, brief endpoint restarts, or momentary
   overload that resolve within seconds.
2. **Sustained failures** — a dependency enters a degraded state for minutes or
   longer (rolling deployment, region failover, capacity event).
3. **Cascading failures** — upstream slowness causes the caller to hold open
   connections, consuming thread pool and memory, which then causes the caller's
   own latency to spike and triggers failures in its callers.
4. **Silent quality degradation** — when a dependency is unavailable, the system
   must continue returning useful (possibly lower-quality) responses rather than
   hard-failing.

A single fault-tolerance mechanism cannot address all four modes simultaneously.
Timeout-only approaches do not prevent cascading failures from consuming
resources. Simple retry loops without back-off worsen congestion. Accepting
failures silently degrades user experience invisibly.

---

## Decision

We adopt a **three-layer composable resilience pattern** implemented as three
independent Python classes that can be stacked in any order:

### Layer 1: CircuitBreaker — prevents cascading failures

The circuit breaker monitors call outcomes at the service boundary and transitions
through three states:

```
CLOSED → (failure_threshold exceeded) → OPEN → (timeout elapsed) → HALF-OPEN
HALF-OPEN → (probe success) → CLOSED
HALF-OPEN → (probe failure) → OPEN
```

- In `OPEN` state, calls fail fast without hitting the downstream service, giving
  it time to recover.
- The `HALF-OPEN` probe allows graceful recovery without requiring manual
  intervention.
- Configurable `failure_threshold`, `recovery_timeout`, and `success_threshold`
  (number of consecutive successes in HALF-OPEN required to reset to CLOSED).

### Layer 2: RetryWithBackoff — handles transient failures

Exponential back-off with full jitter is applied to transient failures:

```
sleep = min(base * 2^attempt, max_delay) * random(0, 1)
```

Jitter is critical: without it, multiple callers retrying simultaneously after a
common failure create a thundering-herd that prevents recovery. Full jitter
distributes retry storms across the recovery window.

Configurable `max_attempts`, `base_delay`, `max_delay`, and an `exceptions`
whitelist so only known-transient exceptions are retried (not programming errors).

### Layer 3: GracefulDegradation — maintains service continuity

When a feature group or downstream call is unavailable, `GracefulDegradation`
returns a typed fallback value instead of propagating an exception:

- Fallback values are typed and domain-specific (e.g., neutral feature vector,
  default probability, cached last-known-good response).
- Degradation events are logged and counted so on-call engineers are alerted
  even when end-users experience no hard failure.

### Composition

The layers are designed to compose without coupling:

```
CircuitBreaker(service_boundary)
  └── RetryWithBackoff(individual_call)
        └── GracefulDegradation(feature_group)
```

The circuit breaker wraps the entire service boundary. Retry wraps each individual
RPC/HTTP call within that boundary. Graceful degradation wraps the feature group
or model prediction block that may rely on the call's result.

---

## Consequences

**Positive:**
- Each layer is independently testable and replaceable; swapping the retry policy
  does not require changes to circuit-breaker or degradation logic.
- The three layers address all four failure modes identified in the context.
- Full jitter prevents retry storms in multi-instance deployments.
- Typed fallbacks make graceful degradation explicit and verifiable in tests.

**Negative / Trade-offs:**
- Three layers add wrapping overhead; developers must understand which layer to
  apply at which abstraction boundary.
- Circuit breaker state is **per-process** in the current implementation; a
  multi-replica deployment will have independent breaker states. Shared state
  (e.g., Redis-backed breaker) is not implemented and would require additional
  infrastructure.
- Graceful degradation hides real errors from end-users; monitoring and alerting
  must be in place or silent degradation accumulates undetected.

---

## Alternatives Considered

| Alternative | Reason Rejected |
|---|---|
| **Timeout-only** | Does not prevent cascading failures; a slow dependency still consumes caller threads while waiting for timeouts to fire. |
| **Bulkhead pattern** | Isolates resource pools (thread pools, connection pools) per downstream service. Valuable but complementary — it does not handle transient failures or quality degradation. Left for a future ADR. |
| **Single retry without circuit breaker** | Retry alone worsens congestion during sustained outages; without a fast-fail mechanism, every call during an outage waits for `max_attempts × timeout`. |
| **Hystrix / Resilience4j (JVM library)** | Platform is Python; JVM libraries are not applicable. The implementation mirrors Hystrix semantics in idiomatic Python. |
