# ADR: Introduce Intent Validation & Plan of Action Approval Gate

## Status
Accepted — 2025-10-26

## Context
Repeated workstreams benefited from an explicit alignment gate before implementation:
clear articulation of goals, constraints, risks, deliverables, and acceptance criteria.
We also need local-only quality gates to preserve contributor velocity without requiring CI.

## Decision
- Add a reusable **Intent Validation & Plan of Action** template (`docs/templates/intent_validation_gate.md`).
- Establish **local-only** gating via:
  - Fence integrity validator (`tools/validate_fences.py`).
  - Codex evaluator & rubric (`tools/codex_evaluator.py`, `manifests/codex_eval_rules.v3.json`).
  - Pre-commit hooks configured for local runs only.

## Consequences
**Positive**
- Better alignment and auditability of decisions.
- Safer message/patch quality with deterministic local checks.

**Neutral/Trade-offs**
- Slight upfront overhead to run gates locally.

**Negative Risks & Mitigations**
- False positives in strict checks → Provide clear override flags and documentation.

## Rollback
- Remove added scripts and hooks in a single revert; docs can remain with “Superseded” note for traceability.
