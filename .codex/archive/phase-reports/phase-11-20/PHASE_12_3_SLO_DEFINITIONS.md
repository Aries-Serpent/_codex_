# Phase 12.3 — SLO Definitions

**Status:** ✅ Defined  
**Phase:** 12.3 — Agent Observability & Telemetry  
**Authority:** D-tier (approved by @mbaetiong)  
**Last Updated:** Phase 12 implementation

---

## Overview

Service Level Objectives (SLOs) are the performance contracts for the Codex
agent ecosystem.  They define measurable targets, error budgets, and escalation
thresholds.  All SLOs are measured using data emitted by `MetricsCollector` and
`ObservabilityLogger` (see `PHASE_12_3_OBSERVABILITY_STACK.md`).

> **SLO vs SLA**: SLOs are internal targets.  SLAs are external commitments.
> All values here are SLOs — the internal bar we hold ourselves to.

---

## SLO Catalog

### SLO-1: Availability

> **Target: 99.95% uptime for core agents over any 30-day rolling window.**

**Scope:** Core agents — those listed in `AGENT_REGISTRY.yaml` with
`tier: core` or `tier: critical` — must be available to accept and process
tasks.

**Measurement:**
- An agent is considered "available" if it successfully processes at least one
  task within any 5-minute window during active CI hours (06:00–23:59 UTC
  Monday–Saturday).
- "Unavailable" windows are counted when `error_rate == 1.0` for 5 consecutive
  minutes OR the agent returns no `record_agent_execution` events for 10+
  minutes during an active push/PR event.
- Availability % = `(total_minutes - downtime_minutes) / total_minutes × 100`.

**Error Budget:**
- 30-day window = 43 200 minutes.
- 99.95% target = 21.6 minutes of allowable downtime per 30 days.
- At 99.9% (fallback warning threshold) = 43.2 minutes.

**Alert Thresholds:**
| Condition | Severity | Action |
|-----------|----------|--------|
| Downtime > 10 min in 30-day window | WARNING | Weekly SLO report note |
| Downtime > 15 min in 30-day window | CRITICAL | Immediate on-call page |
| Downtime > 21.6 min in 30-day window | SLO BREACH | Incident opened; post-mortem required |

**Phase 11.3 Integration:**
The Phase 11.3 circuit-breaker opens when an agent's consecutive failure count
exceeds `failure_threshold` (default: 3).  An open circuit == availability = 0
for that agent.  Circuit open time counts directly against the error budget.

---

### SLO-2: Latency (P99 Agent Task Execution)

> **Target: P99 latency < 30 000 ms (30 seconds) for all agent task executions.**

**Scope:** All agent executions recorded via
`MetricsCollector.record_agent_execution()`.  Excludes long-running background
tasks explicitly tagged with `metadata={"long_running": True}`.

**Measurement:**
- Computed from the sliding window (last 1 000 executions per agent).
- P99 = 99th percentile of `duration_ms` values in the window.
- SLO is evaluated per-agent and at the ecosystem aggregate level.
- Evaluation window: rolling 5-minute bucket for alerting; rolling 30-day for
  SLO compliance reports.

**Error Budget:**
- In a 30-day window with ~10 000 requests per agent, 1% = 100 requests allowed
  above 30 s.
- Ecosystem-wide: the sum of P99 violations across all core agents must not
  exceed 1% of total executions.

**Tiered Latency Targets:**

| Agent Tier     | P50 Target | P95 Target | P99 Target |
|----------------|-----------|-----------|-----------|
| Critical       | ≤ 5 000 ms  | ≤ 15 000 ms | ≤ 20 000 ms |
| Core           | ≤ 10 000 ms | ≤ 25 000 ms | ≤ 30 000 ms |
| Standard       | ≤ 30 000 ms | ≤ 60 000 ms | ≤ 120 000 ms |

**Alert Thresholds:**
| Condition | Severity | Action |
|-----------|----------|--------|
| P99 > 20 000 ms for critical agent | WARNING | Log + routing weight reduction |
| P99 > 30 000 ms for any core agent | WARNING | Log alert; flag in SLO report |
| P99 > 60 000 ms for any core agent | CRITICAL | Investigate immediately |
| P99 > 120 000 ms (2 min) for any agent | CRITICAL | Page on-call |

---

### SLO-3: Routing Decision Latency

> **Target: P99 routing decision latency < 800 ms.**

**Scope:** Time from task receipt to agent assignment, logged via
`ObservabilityLogger.log_routing_decision()` with the `latency_ms` field.

**Measurement:**
- Collect `latency_ms` from all `routing_decision` log records in the 5-minute
  evaluation window.
- Compute P99 across all routing decisions in the window.
- A missing `latency_ms` (None) is treated as a warning event, not a violation.

**Rationale:**
Routing decisions must be fast because they gate every agent execution.  An
800 ms P99 target ensures that even with 100+ agent registry lookups and
embedding similarity searches, routing does not become the system bottleneck.

**Error Budget:**
- 1% of routing decisions may exceed 800 ms.
- 0.1% of routing decisions may exceed 2 000 ms (hard cap).

**Alert Thresholds:**
| Condition | Severity | Action |
|-----------|----------|--------|
| P95 routing latency > 500 ms | WARNING | Investigate registry cache |
| P99 routing latency > 800 ms | WARNING | Log alert; review FAISS index |
| P99 routing latency > 2 000 ms | CRITICAL | Page on-call; disable non-critical routing |
| Routing `accuracy < 0.90` | WARNING | Review routing rules |

---

### SLO-4: Error Rate

> **Target: < 2% agent error rate over any 5-minute window.**

**Scope:** All executions recorded via `record_agent_execution()`, aggregated
per agent and ecosystem-wide.

**Measurement:**
- `error_rate` = `failed_executions / total_executions` in the 5-minute window.
- Computed via `MetricsCollector.get_agent_metrics(agent_id).error_rate`.
- Ecosystem error rate = total failures / total executions across all agents.

**Error Budget:**
- Over a 30-day window: ≤ 2% of all executions may fail.
- At 10 000 executions/day × 30 days = 300 000 total: ≤ 6 000 allowed failures.
- "Fast burn" alert: if 5-minute error rate > 5% (consuming budget 2.5× faster
  than allowed), fire an immediate alert.

**Alert Thresholds:**
| Condition | Severity | Action |
|-----------|----------|--------|
| Error rate > 1% (5-min window) for any agent | WARNING | Log; monitor trend |
| Error rate > 2% (5-min window) for any agent | WARNING | SLO burn-rate alert |
| Error rate > 5% (5-min window) | CRITICAL | Open circuit breaker; page |
| Ecosystem error rate > 2% | CRITICAL | Immediate investigation |

**Per-Agent Fast-Burn Formula:**
```
burn_rate = actual_error_rate / slo_error_budget_rate
           = actual_error_rate / 0.02

If burn_rate > 10 → consuming budget 10× too fast → alert within 5 min
If burn_rate > 5  → consuming budget 5× too fast  → alert within 30 min
```

---

### SLO-5: Recovery (MTTR)

> **Target: Mean Time to Recovery (MTTR) < 5 minutes for failed agents.**

**Scope:** The time from when an agent is marked as failed (circuit breaker
opens) to when it is restored to normal operation (circuit breaker closes or
agent successfully processes a task).

**Measurement:**
- MTTR is measured from the timestamp of the first `status="error"` log event
  for a run of consecutive failures, to the timestamp of the next
  `status="success"` event.
- Logged via `ObservabilityLogger.log_agent_action()` with `status="error"` and
  `status="success"` respectively.
- Monthly MTTR = `sum(recovery_times) / count(recovery_events)`.

**Error Budget:**
- In a 30-day window, the ecosystem may have up to 50 agent failure-recovery
  events at ≤ 5 min each = 250 minutes of total recovery time allowed.
- Any single recovery event exceeding 15 minutes is a breach regardless of the
  monthly average.

**Phase 11.3 Integration:**
The `phase_11_3_health_monitor.py` auto-healing loop is the primary recovery
mechanism.  The SLO is measured from circuit-open to circuit-close timestamps
emitted by that monitor.

**Alert Thresholds:**
| Condition | Severity | Action |
|-----------|----------|--------|
| Agent down for > 2 min | WARNING | Trigger auto-healer |
| Agent down for > 5 min | CRITICAL | Page on-call; escalate to human |
| MTTR trending > 5 min (7-day avg) | WARNING | Review auto-healer effectiveness |
| Any single MTTR > 15 min | CRITICAL | Post-mortem required |

---

## SLO Measurement Methodology

### Data Collection

All SLO measurements originate from two sources:

1. **`MetricsCollector`** — In-memory sliding window; used for real-time
   alerting and dashboard visualization.
2. **SQLite session_events** — Persisted via `ObservabilityLogger` with
   `persist_to_db=True`; used for historical SLO compliance reports.

### Evaluation Cadence

| SLO | Real-Time Window | Compliance Report Window |
|-----|-----------------|--------------------------|
| Availability | 5 min | 30 days |
| Latency P99 | 5 min (alerts) | 30 days |
| Routing Latency | 5 min | 7 days |
| Error Rate | 5 min | 30 days |
| MTTR | Per-event | 30 days |

### Weekly SLO Report

Generated every Monday at 09:00 UTC. Contents:

1. **SLO Compliance Summary**: Pass/Fail for each SLO with achieved vs. target.
2. **Error Budget Status**: Minutes/requests consumed vs. allowed.
3. **Top Violators**: Agents with worst SLO adherence.
4. **Trend Analysis**: 4-week rolling trend for each metric.
5. **Incident Log**: All SLO breaches and MTTR for the week.
6. **Recommendations**: Actions to prevent recurrence.

---

## Error Budget Calculation Examples

### Example 1: Availability Error Budget (30 days)

```
SLO target:        99.95%
Window:            30 days = 43 200 minutes
Allowed downtime:  43 200 × (1 - 0.9995) = 21.6 minutes
Consumed (week 1): 8 minutes
Remaining:         13.6 minutes
Burn rate:         8 / 21.6 = 37% of budget consumed in week 1
Status:            ✅ On track
```

### Example 2: Error Rate Budget (30 days)

```
SLO target:        2% error rate
Total executions:  250 000 (30-day estimate)
Allowed failures:  250 000 × 0.02 = 5 000
Actual failures:   1 200
Remaining budget:  3 800 failures
Burn rate:         1 200 / 5 000 = 24% consumed
Status:            ✅ On track
```

### Example 3: Error Budget Exhaustion Alert

```
5-minute window:
  - Total executions: 120
  - Failures:          9
  - Error rate:       7.5%
  - Burn rate:        7.5% / 2% = 3.75×

Action: WARNING — burning budget at 3.75× allowed rate.
        If sustained, 30-day budget exhausted in ~8 days instead of 30.
```

---

## SLO Review and Adjustment Process

SLOs are reviewed quarterly and may be tightened as the ecosystem matures:

| Metric | Current SLO | Phase 13 Target | Phase 14 Target |
|--------|------------|-----------------|-----------------|
| Availability | 99.95% | 99.97% | 99.99% |
| Latency P99 | 30 000 ms | 20 000 ms | 10 000 ms |
| Routing P99 | 800 ms | 500 ms | 200 ms |
| Error Rate | 2% | 1% | 0.5% |
| MTTR | 5 min | 3 min | 1 min |

---

## Integration with Phase 11.3 Circuit-Breaker Thresholds

Phase 11.3 circuit-breaker settings are calibrated to protect the SLO error
budget:

| Circuit-Breaker Parameter | Value | SLO Alignment |
|--------------------------|-------|---------------|
| `failure_threshold`      | 3 consecutive failures | Prevents error rate > 5% before circuit opens |
| `recovery_timeout`       | 60 seconds | Limits contribution to MTTR SLO |
| `half_open_max_calls`    | 2 | Minimizes re-failure risk during recovery |
| Observation window       | 5 minutes | Matches SLO error rate evaluation window |

The circuit-breaker is designed to open _before_ the error rate SLO is breached,
giving the auto-healer time to respond within the MTTR budget.

---

## Compliance Matrix

| SLO | Metric Source | Alert Tool | Report Cadence |
|-----|--------------|------------|----------------|
| SLO-1 Availability | `active_agents`, circuit-breaker state | `ObservabilityLogger.error()` | Weekly |
| SLO-2 Latency | `latency_p99_ms` per agent | Prometheus alert rule | Weekly |
| SLO-3 Routing | `routing_decision.latency_ms` | Log pattern monitor | Weekly |
| SLO-4 Error Rate | `error_rate` per agent | Fast-burn alert | Weekly |
| SLO-5 MTTR | `error` → `success` timestamp delta | Incident tracker | Weekly |

---

*Document maintained by Phase 12.3 observability infrastructure.*  
*Next review: Phase 13 planning — target SLO tightening scheduled.*
