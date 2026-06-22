# Architecture Decision Records

**Last Updated:** 2026-06-22

This directory contains Architecture Decision Records (ADRs) for the _codex_ project.
ADRs capture significant architectural decisions, their context, and consequences.

ADRs follow the [MADR format](https://adr.github.io/madr/) (Markdown Any Decision Records)
with the following required sections: **Status**, **Date**, **Context**, **Decision**,
**Consequences**, and **Alternatives Considered**.

## Index

| ADR | Title | Status | Date |
|-----|-------|--------|------|
| [ADR-0001](ADR-0001-distributed-tracing.md) | Distributed Tracing Strategy | Deferred | 2026-06-05 |
| [ADR-001](ADR-001-drift-monitoring-approach.md) | Use PSI + KL-Divergence for Data Drift, JSD for Model Drift | Accepted | 2025-01-15 |
| [ADR-002](ADR-002-resilience-pattern.md) | Three-Layer Resilience: Circuit Breaker + Retry + Graceful Degradation | Accepted | 2025-01-15 |
| [ADR-003](ADR-003-continuous-learning-architecture.md) | Event-Driven Continuous Learning via Drift → Trigger → EvalGate → Promote | Accepted | 2025-01-15 |
| [ADR-004](ADR-004-testing-strategy.md) | Multi-Layer Testing: Unit + Integration + Regression + Property + Fuzz + Chaos | Accepted | 2025-01-15 |

## Status Definitions

| Status | Meaning |
|--------|---------|
| **Proposed** | Decision is under discussion; not yet binding |
| **Accepted** | Decision is in effect and implemented |
| **Deprecated** | Decision was accepted but has been superseded |
| **Deferred** | Decision is acknowledged but implementation is postponed |
| **Rejected** | Decision was considered but not adopted |

## How to Add a New ADR

1. Copy `docs/adr/ADR-001-drift-monitoring-approach.md` as a template.
2. Number sequentially (next available three-digit number).
3. Add an entry to the index table above.
4. Set status to `Proposed`; update to `Accepted` once the decision is ratified.
