# Phase 12.3 — Observability Stack Architecture

**Status:** ✅ Implemented  
**Phase:** 12.3 — Agent Observability & Telemetry  
**Package:** `src/codex/observability/`  
**Depends on:** Phase 11.2 (Routing Rules), Phase 11.3 (Health Monitoring)

---

## Overview

The Codex agent ecosystem requires end-to-end visibility into the behavior of
100+ specialized agents, the orchestrator routing layer, and the CI/CD pipeline
they collectively manage.  Phase 12.3 delivers a **three-pillar observability
stack** — _Logs_, _Metrics_, and _Traces_ — implemented as a new Python package
(`src/codex/observability/`) that builds on existing infrastructure in
`src/codex/monitoring/` and `src/codex/logging/` without duplicating any of it.

### Why Observability Matters Here

- **100+ agents** means debugging a single failure requires correlating events
  across many components that may execute in parallel or in sequence.
- **Phase 11.3 health monitoring** can detect _that_ something is wrong, but
  observability tells you _why_ and _where_.
- **Phase 11.2 routing decisions** happen at sub-second latency; without a
  routing log, miscategorised tasks are silent failures.
- **SLO compliance** (see `PHASE_12_3_SLO_DEFINITIONS.md`) requires real-time
  data that only a live metrics pipeline can provide.

---

## Observability Architecture

```mermaid
flowchart TD
    subgraph Agents["Agent Ecosystem (100+ agents)"]
        A1[orchestrator-agent]
        A2[ci-auto-healer-agent]
        A3[unified-coverage-agent]
        AN[... other agents ...]
    end

    subgraph Observability["src/codex/observability/"]
        OL[ObservabilityLogger\nlogging.py]
        MC[MetricsCollector\nmetrics.py]
    end

    subgraph Existing["Existing Infrastructure"]
        SL[codex.logging.session_logger\nSQLite session_events]
        OH[codex.monitoring.otel_metrics\nHistogram registry]
        HM[Phase 11.3 Health Monitor\nscripts/ci/phase_11_3_health_monitor.py]
        RR[Phase 11.2 Routing Rules\n.codex/PHASE_11_2_ROUTING_RULES_QUICK.md]
    end

    subgraph Export["Export / Consumption"]
        PR[Prometheus Text\nexport_prometheus_format()]
        DB[(SQLite\nsession_events table)]
        PY[Python logging\nstdout / log files]
        DS[Dashboards\nGrafana / custom]
    end

    Agents -->|record_agent_execution| MC
    Agents -->|log_agent_action| OL
    Agents -->|log_routing_decision| OL
    OL -->|log_event| SL
    OL --> PY
    MC -->|observe| OH
    MC --> PR
    SL --> DB
    PR --> DS
    HM -->|circuit-breaker events| OL
    RR -->|routing chosen_agent| OL
```

---

## Package Structure

```
src/codex/observability/
├── __init__.py      — Package init; exports ObservabilityLogger, MetricsCollector
├── logging.py       — ObservabilityLogger: structured log emission
└── metrics.py       — MetricsCollector: in-memory metrics with Prometheus export
```

---

## Logging Schema and Data Model

Every event emitted by `ObservabilityLogger` conforms to the following JSON
schema:

```json
{
  "timestamp":  "2024-01-15T12:34:56.789Z",
  "session_id": "abc-123-def-456",
  "agent_id":   "ci-auto-healer-agent",
  "action":     "route_task",
  "status":     "success",
  "latency_ms": 342.5,
  "error":      null,
  "metadata": {
    "task_type": "fix_ci_failure",
    "confidence": 0.97
  }
}
```

| Field        | Type           | Description                                              |
|-------------|----------------|----------------------------------------------------------|
| `timestamp`  | ISO-8601 UTC   | When the event was recorded                              |
| `session_id` | string         | Owning Copilot session or workflow run ID                |
| `agent_id`   | string         | Agent that performed the action                          |
| `action`     | string         | Short slug: `route_task`, `execute_task`, `health_check` |
| `status`     | string enum    | `success`, `failure`, `error`, `debug`, `info`           |
| `latency_ms` | float or null  | Wall-clock execution time in milliseconds                |
| `error`      | string or null | Error message if `status == "error"`                     |
| `metadata`   | object         | Arbitrary additional context (agent-specific)            |

### Log Levels Mapping

| Status value | Python log level | Use case                                     |
|-------------|-----------------|----------------------------------------------|
| `"success"` | `INFO`          | Normal task completion                        |
| `"failure"` | `WARNING`       | Task failed but system remains operational    |
| `"error"`   | `ERROR`         | Unexpected error; may require intervention    |
| `"debug"`   | `DEBUG`         | Verbose diagnostic information                |

### Output Formats

`ObservabilityLogger` supports three output formats:

- **`"json"`** (default): One JSON object per line; machine-parseable.
- **`"text"`**: Human-readable single-line format for developer terminals.
- **`"both"`**: Both formats emitted simultaneously.

---

## Metrics Catalog

All metrics are collected by `MetricsCollector` with a configurable sliding
window (default: last 1 000 executions per agent).

### Per-Agent Metrics

| Metric                | Unit   | Description                                         | Alert Threshold       |
|-----------------------|--------|-----------------------------------------------------|-----------------------|
| `latency_p50_ms`      | ms     | Median execution latency                            | > 10 000 ms           |
| `latency_p95_ms`      | ms     | 95th-percentile execution latency                   | > 20 000 ms           |
| `latency_p99_ms`      | ms     | 99th-percentile execution latency                   | > 30 000 ms (SLO)     |
| `latency_mean_ms`     | ms     | Mean execution latency                              | Informational         |
| `latency_min_ms`      | ms     | Minimum observed latency                            | Informational         |
| `latency_max_ms`      | ms     | Maximum observed latency                            | Informational         |
| `success_rate`        | [0,1]  | Fraction of executions that succeeded               | < 0.98 (error budget) |
| `error_rate`          | [0,1]  | Fraction of executions that failed                  | > 0.02 (SLO)          |
| `throughput_per_min`  | req/min| Executions per minute over last 60 s                | < 0.1 (idle alert)    |
| `total_executions`    | count  | Lifetime execution count (never resets)             | Informational         |
| `window_executions`   | count  | Executions within the current window                | Informational         |

### Ecosystem-Wide Metrics

| Metric                | Unit   | Description                                         | Alert Threshold       |
|-----------------------|--------|-----------------------------------------------------|-----------------------|
| `total_tasks_executed`| count  | Lifetime tasks across all agents                    | Informational         |
| `active_agents`       | count  | Agents with ≥1 execution in window                 | < 1 (critical)        |
| `failed_agents`       | count  | Agents with `error_rate > 0` in window              | > 10 (warning)        |
| `routing_accuracy`    | [0,1]  | Fraction of routing decisions that were accurate    | < 0.90 (warning)      |

---

## Trace Collection Strategy

Phase 12.3 implements **structured trace correlation** without requiring the
full OpenTelemetry SDK (which is an optional heavy dependency).

**Correlation strategy:**

1. Every `log_agent_action` call includes a `session_id` that groups all events
   belonging to one Copilot session or workflow run.
2. `metadata` can include `trace_id` and `span_id` fields for manual trace
   propagation when debugging complex multi-agent flows.
3. `log_routing_decision` records both the chosen agent and alternatives,
   enabling reconstruction of the full routing decision tree from logs.
4. When the full OpenTelemetry SDK is available, the `ObservabilityLogger` can
   be extended to emit OTLP spans — the JSON schema is intentionally
   OTEL-compatible.

**Future migration path:** Replace `_build_record()` with an OTEL Span factory.
No call-site changes required.

---

## Dashboard Design

### Key Panels (Grafana or equivalent)

1. **Agent Health Overview** — Table: all agents × `success_rate`, `latency_p99_ms`,
   `throughput_per_min`. Red rows when `error_rate > 0.02`.
2. **Latency Heatmap** — Histogram of `latency_p99_ms` across all agents over time.
   SLO line at 30 000 ms.
3. **Error Rate Time-Series** — Rolling 5-minute error rate. Alert band at 2 %.
4. **Routing Accuracy** — Single-stat panel: `routing_accuracy` percentage.
   Green > 95 %, Yellow 90–95 %, Red < 90 %.
5. **Throughput** — Stacked bar chart: `throughput_per_min` per agent over last hour.
6. **Top Failing Agents** — Ranked list by `error_rate`, updated every 60 s.
7. **Active Agent Count** — Time-series of `active_agents`. Drop below 5 = alert.

### Interpreting Metrics

- A sudden spike in `latency_p99_ms` without a corresponding rise in
  `error_rate` usually indicates resource contention (CPU/network), not a
  software bug.
- An `error_rate` spike accompanied by unchanged `latency` suggests a logic
  error or API breakage, not infrastructure.
- A drop in `throughput_per_min` to zero while `active_agents` remains
  nonzero indicates agents are receiving no work (routing gap) rather than
  being down.

---

## Integration with Phase 11.3 Health Monitoring

Phase 11.3 (`scripts/ci/phase_11_3_health_monitor.py`) monitors workflow-level
health via circuit-breaker patterns.  The observability stack integrates as
follows:

- **Health monitor → ObservabilityLogger**: The health monitor emits
  `log_workflow_event()` calls when it detects failures, enabling correlation
  with agent-level metrics.
- **MetricsCollector → health thresholds**: `error_rate` and `latency_p99_ms`
  feed into Phase 11.3 circuit-breaker thresholds.  When `error_rate > 0.05`
  for an agent, the circuit opens and routing skips that agent.
- **Shared session_id**: Both systems use the same `session_id` as the
  correlation key, enabling full end-to-end event chains in SQLite.

---

## Integration with Phase 11.2 Routing

Every routing decision emitted by the Phase 11.2 orchestrator is recorded via
`log_routing_decision()`, which captures:

- The task description/type
- The chosen agent and its confidence score
- All alternative agents considered
- The routing decision latency

This enables post-hoc analysis of routing accuracy and drift over time.

---

## Alert Thresholds and Escalation

| Condition                          | Severity | Action                                    |
|------------------------------------|----------|-------------------------------------------|
| `error_rate > 0.05` for any agent  | CRITICAL | Open circuit breaker; page on-call        |
| `error_rate > 0.02` for any agent  | WARNING  | Log alert; add to weekly SLO report       |
| `latency_p99_ms > 30 000` (30 s)  | WARNING  | Log slow-agent alert                      |
| `routing_accuracy < 0.90`          | WARNING  | Review routing rules; retrain if needed   |
| `active_agents < 2`                | CRITICAL | Escalate to human immediately             |
| `failed_agents > 10`               | WARNING  | Investigate systemic issue                |

---

## Usage Examples

### Basic Agent Logging

```python
from codex.observability import ObservabilityLogger

obs = ObservabilityLogger(session_id="session-abc-123", output_format="json")

# Log a successful action
obs.log_agent_action(
    "ci-auto-healer-agent",
    "fix_workflow",
    "success",
    latency_ms=4200.0,
    metadata={"workflow": "ci-tests.yml", "fix_pattern": "RP-001"},
)

# Log a routing decision
obs.log_routing_decision(
    task="fix_import_error",
    chosen_agent="ci-importerror-agent",
    confidence=0.94,
    alternatives=["ci-testing-agent", "ci-auto-healer-agent"],
    latency_ms=75.2,
)

# Log a workflow event
obs.log_workflow_event(
    "21731917109",
    "job_failed",
    {"job": "test-suite", "step": "pytest", "exit_code": 1},
)
```

### Metrics Collection

```python
from codex.observability import MetricsCollector

collector = MetricsCollector(window_size=1000)

# Record executions
collector.record_agent_execution("orchestrator", duration_ms=350.0, success=True)
collector.record_agent_execution("ci-auto-healer", duration_ms=8400.0, success=True)
collector.record_agent_execution("ci-auto-healer", duration_ms=2100.0, success=False)

# Get per-agent snapshot
m = collector.get_agent_metrics("ci-auto-healer")
print(f"P99 latency: {m.latency_p99_ms:.1f} ms")
print(f"Error rate:  {m.error_rate:.1%}")

# Ecosystem summary
summary = collector.get_ecosystem_summary()
print(f"Active agents: {summary['active_agents']}")
print(f"Routing accuracy: {summary['routing_accuracy']:.1%}")

# Export for scraping
print(collector.export_prometheus_format())
```

---

## Design Decisions

1. **No prometheus_client dependency**: Prometheus format is generated manually.
   This avoids pulling in a heavy optional dependency and keeps the package
   importable in all environments.
2. **Sliding window, not time-based**: A fixed-size deque (not a time-based
   ring buffer) is used because execution frequency varies wildly across agents.
   Throughput-per-minute is still computed correctly from timestamps.
3. **Graceful degradation**: Both `ObservabilityLogger` and `MetricsCollector`
   continue to work if `codex.logging` or `codex.monitoring` are unavailable.
4. **Thread-safety via `threading.Lock`**: All shared state is protected.
   No global state is modified.
