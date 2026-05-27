# Agent Orchestration — Compliance Specification

**Version**: 1.0  
**Created**: 2026-05-27  
**Owner**: `orchestrator-agent`  
**Compliance log**: [`../../reports/orchestration/orchestration_compliance.log.md`](../../reports/orchestration/orchestration_compliance.log.md)  
**OKR tracking**: [`../../reports/orchestration/OKR_TRACKING.md`](../../reports/orchestration/OKR_TRACKING.md)  
**SLO reference**: [`../observability/SLO_DEFINITIONS.md`](../observability/SLO_DEFINITIONS.md)

---

## Purpose

This document specifies how the Codex platform's multi-agent orchestration layer
maintains compliance: what is logged, what policy gates are enforced, how failures
are handled, and who is responsible for each aspect.

---

## Compliance Obligations

### 1. Logging
Every dispatched agent task **must** produce a JSONL entry in
`reports/orchestration/orchestration_compliance.log.md` containing:

- `timestamp`, `agent_id`, `task_type`, `status`, `policy_gate`, `duration_s`, `session_id`

The entry is written by the calling workflow (`cognitive-action-decision.yml`) or
by the `orchestrator-agent` itself.

### 2. Policy Gates

| Gate | Enforced by | Behaviour on fail |
|------|-------------|-------------------|
| `owner-approval-guard` | `owner-approval-guard` agent | Block task, log as `blocked` |
| `unified-governance-gate` | `unified-governance-gate` agent | Block task, log as `blocked` |
| `deferral-language-gate` | `.github/workflows/deferral-language-gate.yml` | Block PR, log as `blocked` |
| `workflow-compliance-gate` | `.github/workflows/workflow-compliance-gate.yml` | Block PR |
| `import-linter` | `.github/workflows/import-linter.yml` | Block PR |

### 3. Deterministic Fallbacks

Every orchestrated workflow must define an explicit fallback:

| Failure mode | Fallback |
|-------------|---------|
| Agent timeout | Retry once; then log `fail` and create a GitHub issue |
| Policy block | Log `blocked`; alert `@mbaetiong` for P1 tasks |
| Unhandled exception | Log `fail`; delegate to `ci-auto-healer-agent` |
| Silent failure (no output) | Treated as `fail`; alert `orchestrator-agent` |

### 4. Audit Review

- `orchestrator-agent` reviews the compliance log **weekly**.
- `session-analysis-agent` performs monthly audit.
- Compliance log entries are **append-only**; never delete rows.

---

## Allowed Failure Modes

The following outcomes are considered **expected** (not SLO breaches):

| Scenario | `status` | Notes |
|----------|----------|-------|
| Governance gate blocks a policy-violating task | `blocked` | Not a failure |
| Agent skips work due to no-op (unchanged files) | `ok` | Log with note |
| Scheduled agent deferred by concurrency limit | `fail` | Retry within 24 h |

---

## Prohibited Behaviours

- Agents **must not** self-approve their own policy gate checks.
- Orchestrator **must not** bypass `owner-approval-guard` for P1 tasks.
- Compliance log **must not** be modified retroactively.
