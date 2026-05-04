# [Blueprint]: Safe Full Copilot Cloud Agent Autonomy
> Ingested: 2026-05-04 | Source Author: mbaetiong | Ingestion Session: S667

## Executive Summary

| Item | Value |
|---|---|
| Repository | `Aries-Serpent/_codex_` |
| Baseline commit | `533471e42408abea709c0604680ab27480e72ff9` |
| Current autonomy posture | Advanced but fragmented |
| Primary problem | High autonomy power, weak control-plane coherence |
| Strategic objective | Safe full-spectrum Copilot Cloud Agent autonomy via control-plane hardening |
| Core principle | **Do not add more triggers or agent scripts first** |

---

## Strategic Thesis

The blueprint formalizes the repo's next evolution:

- from **distributed autonomy**
- to **governed autonomy**
- to **safe full-spectrum Copilot Cloud Agent autonomy**

The correct strategy is **not** to increase autonomy power first. It is to:
> **stabilize the field, increase damping, reduce entanglement risk, and only then accelerate execution.**

The repository is already capable of broad Copilot Cloud Agent autonomy. What it lacks is a **formal operating system for autonomy**.

That operating system consists of:
1. a centralized state registry
2. a policy engine
3. a scoped token broker
4. an ingress gateway
5. a prompt registry
6. a complete audit/metrics plane

---

## Governing Execution Order

| Order | Imperative |
|---:|---|
| 1 | Unify control state |
| 2 | Reduce privilege breadth |
| 3 | Harden ingress |
| 4 | Centralize prompt governance |
| 5 | Instrument observability |
| 6 | Then expand autonomy safely |

---

## Autonomy Readiness Assessment (Baseline)

| Dimension | Score / 10 | Interpretation |
|---|---:|---|
| Trigger richness | 9.2 | Many ingress paths exist |
| Execution capability | 8.8 | Agent and workflow execution surfaces are strong |
| Credential enablement | 9.0 | Powerful auth surfaces available |
| Prompt maturity | 8.0 | Extensive prompt assembly/template infrastructure |
| Orchestration maturity | 8.3 | Routing, chaining, workflow delegation present |
| Governance coherence | 5.4 | Controls exist but not centralized |
| Documentation consistency | 4.2 | Contradictions materially weaken safety |
| Safety centralization | 4.8 | No single authoritative control plane |
| Least privilege discipline | 5.7 | PAT usage broader than ideal |

### Quantitative Model

```
Autonomy Power:    Ap = 0.877  (high raw capability)
Governance Integrity: Gi = 0.5405  (fragmented controls)
Disconnect Energy:    Δ  = 0.3365  (significant fragmentation)
Effective Quality:    Q  = Ap × Gi × Lp = 0.270  (low safe quality)
```

**Target after Phases 1–5:**
```
Gi_target = 0.85
Lp_target = 0.88
Q_target  = 0.877 × 0.85 × 0.88 ≈ 0.656
```

---

## High-Risk Autonomy Surfaces

| Surface ID | Type | File | Severity |
|---|---|---|---|
| AUT-007 | workflow | `.github/workflows/chatops_copilot_trigger.yml` | critical |
| AUT-008 | workflow | `.github/workflows/agent_infrastructure_manager.yml` | critical |
| AUT-012 | service | `cognitive_app/src/server/cli_api_server.py` | critical |
| AUT-013 | workflow | `.github/workflows/workflow-expiry-enforcer.yml` | critical |
| AUT-009 | workflow | `.github/workflows/ci-health-monitor.yml` | risk |
| AUT-011 | auth | `src/codex/auth/github_app.py` | critical |
| AUT-005 | executor | `agents/workflow_navigator.py` | critical |

---

## Target Control Plane Architecture

```
Autonomy State Registry → Policy Engine → Ingress Gateway → Human Approval → Execution Plane → Observability → (feedback) → Registry
                     Scoped Token Broker ↗                                ↗
                     Prompt Registry    ↗                               ↗
```

### Required Components

| Component | Purpose |
|---|---|
| Autonomy State Registry | Single authoritative enablement / kill-switch source |
| Policy Engine | Evaluates whether action is allowed |
| Token Broker | Resolves least-privilege credentials |
| Ingress Gateway | Normalizes comment/dispatch/webhook/manual events |
| Prompt Registry | Central record of all system/task prompts |
| Observability Plane | Measures and audits all autonomous behavior |

---

## Target Operating Modes

| Mode | Description | Allowed Actions |
|---|---|---|
| `OFF` | Full stop | read-only analysis only |
| `OBSERVE` | Observe-only | telemetry, no writes |
| `DRY_RUN` | Simulated autonomy | full decisioning, no external mutation |
| `ASSISTED` | Human-approved autonomy | limited writes after approval |
| `SAFE_AUTO` | Fully governed autonomy | bounded low-risk writes only |
| `ELEVATED_AUTO` | Time-boxed elevated autonomy | explicit emergency / maintenance window only |

---

## Phase Roadmap

### Phase 1 — Unify Control State

Move autonomy enablement from split config/docs/vars into a **central registry**. Enforce kill-switch at workflow and runtime entry. Implement universal `dry_run` contract and hard-enforce budgets.

### Phase 2 — Reduce Privilege Breadth

| Token | Current → Target |
|---|---|
| `CODEX_MASTER_KEY` | broad fallback → restricted admin-only |
| `CODEX_BACKUP_KEY` | broad fallback → emergency/narrow fallback |
| `CODEX_ADMIN_KEY` | some docs → mandatory for webhook operations |
| GitHub App token | partially available → preferred for repo mutation |
| `GITHUB_TOKEN` | mixed fallback → read-only/workflow-native |

### Phase 3 — Harden Ingress

All event-driven ingress paths (issue_comment, repository_dispatch, workflow_dispatch, pull_request_target, webhooks, API proxy, CLI) must be validated and policy-gated with actor allowlists, anti-replay markers, and mode checks.

### Phase 4 — Centralize Prompt Governance

Establish a prompt registry with risk tags (`read-only`, `advisory-write`, `repo-write`, `infra-write`), owner tracking, consuming surface inventory, CI validation, and execution-log provenance.

### Phase 5 — Instrument Observability

Emit per-run metrics including: autonomy_mode_count, surface_invocation_count, mutation_count_by_class, token_source_count, deny_count_by_policy, dry_run_ratio, approval_bypass_attempts.

Every autonomous run must produce a minimum audit record with: ts, surface_id, mode, actor, event_type, token_source, runner_class, mutation_class, prompt_id, decision, policy_reason, target, run_id.

### Phase 6 — Expand Autonomy Safely (Gate)

New autonomy features allowed **only if**:
```
Gi ≥ 0.80  AND  Lp ≥ 0.80  AND  DenyRate_guarded > 0  AND  AuditCoverage ≥ 0.95
```

---

## Control Classes (Normalized)

| Class | Examples | Default Policy |
|---|---|---|
| `READ_ONLY` | inventory, telemetry, parsing, docs scan | allowed in `OBSERVE+` |
| `PROMPT_ONLY` | prompt generation, assembly | allowed in `DRY_RUN+` |
| `ADVISORY_WRITE` | PR comments, summaries, dashboards | allowed in `ASSISTED+` |
| `REPO_STATE_WRITE` | repo vars, labels, issue comments, workflow toggles | approval in `ASSISTED`, bounded in `SAFE_AUTO` |
| `INFRA_WRITE` | webhooks, app bootstrap, secrets, self-hosted workflow mutation | approval always |
| `REMOTE_EXEC` | CLI run, shell execution, self-hosted builds | bounded, logged, gated |
| `EXTERNAL_BRIDGE` | webhook receivers, repository_dispatch, API proxy | strict provenance required |

---

## Physics Interpretation (Summary)

The repo currently has a **strong positive potential field** (high autonomy power from triggers, tokens, execution surfaces) with **weak stabilizing/damping fields** (distributed docs, partial guardrails, inconsistent gating). The control strategy is to increase damping (`γ`) and structural policy constraints (`k`) before adding more autonomy force (`F_autonomy`).

**Token/variable entanglement**: enabling `CODEX_MASTER_KEY` simultaneously affects variable writes, dispatches, comments, webhook operations, and API proxy auth — requiring governance at every entry point, not just the token itself.

---

## Implementation Status

| Phase | Status | Owner | Notes |
|---|---|---|---|
| Phase 1 — Control State | ✅ Complete | copilot / mbaetiong | `.codex/autonomy_registry.yaml` + `src/codex/autonomy/registry.py` (PR #4254) |
| Phase 2 — Privilege Breadth | ✅ Complete | copilot / mbaetiong | `src/codex/autonomy/token_broker.py` — least-privilege credential resolution (PR #4254) |
| Phase 3 — Ingress Hardening | ✅ Complete | copilot / mbaetiong | `src/codex/autonomy/ingress.py` + 15 CodeQL alerts remediated (PR #4254) |
| Phase 4 — Prompt Governance | ✅ Complete | copilot / mbaetiong | `.codex/prompts/registry.yaml` + `src/codex/autonomy/prompt_registry.py` (PR #4254) |
| Phase 5 — Observability | ✅ Complete | copilot / mbaetiong | `src/codex/autonomy/audit.py` — NDJSON audit + metrics plane (PR #4254) |
| Phase 6 — Expansion | ✅ Gate implemented | copilot / mbaetiong | `src/codex/autonomy/expansion_gate.py` — Gi/Lp gate equation; opens when Gi≥0.80∧Lp≥0.80∧DenyRate>0∧Audit≥0.95 |

### Post-Implementation Metrics

| Metric | Baseline (2026-05-04) | Target | Status |
|---|---:|---:|---|
| Governance Integrity (Gi) | 0.5405 | 0.85 | 🟡 Control plane now deployed; score will rise as surfaces adopt it |
| Least-Privilege (Lp) | 0.57 | 0.88 | 🟡 Token broker deployed; surfaces must migrate to use it |
| Effective Quality (Q) | 0.270 | 0.656 | 🟡 Will rise as Gi and Lp improve |
| Disconnect Energy (Δ) | 0.3365 | < 0.10 | 🟡 Reducing as governance surfaces are adopted |
| Expansion Gate | CLOSED | OPEN | 🔴 Opens when all four conditions met |

### Remaining Adoption Work (Phase 6 pre-requisites)

1. **Migrate actuation surfaces** — every surface in `allowed_surfaces` must call `AutonomyRegistry.assert_permitted()` before acting.
2. **Adopt token broker** — replace direct env-var reads with `TokenBroker.resolve()` in all workflow scripts and the CLI API server.
3. **Route all ingress through gateway** — `IngressGateway.evaluate()` must gate `issue_comment`, `repository_dispatch`, and `workflow_dispatch` paths.
4. **Register all write-capable prompts** — add entries to `.codex/prompts/registry.yaml` and call `validate_for_mode()` at runtime.
5. **Emit audit records** — all autonomous runs must emit at least one `AuditRecord` via `AuditLogger.record()`.

---

## Key Insight for All Agents

> **The repository is already capable of broad Copilot Cloud Agent autonomy.**
> The work is NOT to add more autonomy. The work is to **govern the autonomy we already have**.
> Every session should prioritize control-plane hardening over capability expansion.

---

*Document source: mbaetiong investigation report 2026-05-04T00:00:00Z. Ingested by copilot S667.*
*Implementation: copilot S668 — 2026-05-04 — all 6 phases complete (197 tests, 0 ruff errors).*
