# ADR-0001: Distributed Tracing Strategy

**Last Updated:** 2026-06-22

**Date:** 2026-06-05
**Status:** Deferred
**Deciders:** Platform team
**Gap Reference:** Gap 16 (workbench/gap_backlog_prioritized.md)

## Context

The _codex_ ML training platform runs multi-step pipelines (data preparation → training →
evaluation → export) across multiple services (CLI, REST API, orchestrator, LLM clients).
As the system scales, diagnosing latency and correlating failures across service boundaries
requires end-to-end request tracing.

OpenTelemetry (OTEL) is the industry-standard vendor-neutral tracing framework offering:
- Automatic instrumentation for Python HTTP clients, gRPC, and common frameworks
- Exporters to Jaeger, Zipkin, OTLP collectors, and cloud providers
- Native integration with Prometheus metrics (implemented in Gap 14)

## Decision

**Distributed tracing implementation is deferred** pending infrastructure prerequisites:

1. **No OTEL collector deployed** — No Jaeger, Zipkin, or OTLP endpoint is configured in
   current CI or production environments.
2. **No trace storage backend** — No Tempo, Jaeger, or equivalent service to receive traces.
3. **No service mesh** — Services communicate directly; sidecar proxies that auto-inject
   trace context are not present.
4. **Priority ordering** — Alerting (Gap 12/13) and dashboards (Gap 15) are prerequisites
   for meaningful trace-based observability.

## Considered Options

### Option A: Full OTEL instrumentation now (rejected)
- Requires a running collector not available in CI
- Tests need a mock exporter; risk of flaky CI
- **Verdict:** Premature

### Option B: OTEL SDK with NOOP exporter (deferred)
- SDK installed; spans silently discarded unless `OTEL_EXPORTER_OTLP_ENDPOINT` set
- Viable once Gap 15 dashboards and collector decision are made
- **Verdict:** Implement when infrastructure is ready

### Option C: Document and provide no-op stub (chosen)
- This ADR captures the decision and re-evaluation triggers
- `opentelemetry-sdk` added to `requirements-optional.txt` as opt-in
- `src/codex_ml/observability/tracing.py` provides a thin no-op stub
- **Verdict:** Adopted

## Consequences

**Positive:**
- No new infrastructure dependencies in CI
- Decision captured; easy to activate by setting `OTEL_EXPORTER_OTLP_ENDPOINT`
- Stub module ready for drop-in replacement

**Negative:**
- No cross-service trace correlation until infrastructure is provisioned

## Re-evaluation Triggers

Revisit when any of the following are true:
- An OTEL-compatible collector (Jaeger, Tempo, OTLP) is deployed to production or CI
- Gap 15 (Grafana dashboards) is complete and an observability stack owner is assigned
- More than 3 latency-related production incidents occur in a quarter
- Service mesh or sidecar proxies are introduced

## Implementation Notes (when undeferred)

1. Add to `requirements.txt` (move from optional):
   ```
   opentelemetry-sdk>=1.24
   opentelemetry-instrumentation-requests>=0.45b0
   opentelemetry-exporter-otlp-proto-grpc>=1.24
   ```
2. Replace stub in `src/codex_ml/observability/tracing.py` with real `TracerProvider`
3. Instrument: `train_loop.py`, `orchestrator.py`, `llm_client.py`, REST API routes
4. Set env: `OTEL_SERVICE_NAME=codex-ml`, `OTEL_EXPORTER_OTLP_ENDPOINT=<collector>`
