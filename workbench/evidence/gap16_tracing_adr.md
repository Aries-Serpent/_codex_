# Gap 16 — Distributed Tracing ADR Evidence

**Status:** Deferred
**Date:** 2026-06-05

## Evidence Summary

- ADR location: `docs/adr/ADR-0001-distributed-tracing.md`
- Decision: Deferred — infrastructure not ready
- Stub: `src/codex_ml/observability/tracing.py`
- Optional dependency: `requirements-optional.txt` includes `opentelemetry-sdk>=1.24`

## Re-evaluation Triggers

- OTEL-compatible collector (Jaeger, Tempo, or OTLP) deployed to production or CI
- Gap 15 Grafana dashboards completed and an observability stack owner assigned
- More than 3 latency-related production incidents occur in a quarter
- Service mesh or sidecar proxies are introduced

## Notes

This gap is intentionally documented as a deferred architectural decision so Wave 4 ADR work
(Gap 45) can build on a recorded tracing strategy without introducing untestable infrastructure
assumptions into CI.
