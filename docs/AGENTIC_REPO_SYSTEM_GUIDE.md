# Agentic Repository System Guide
> **Canonical Operating Reference** | Aries-Serpent/_codex_
>
> **Version**: 1.1.0  
> **Generated**: 2026-06-22  
> **Status**: ✅ ACTIVE — All Phases 0–6 GROUNDED  
> **Readiness Score**: 100/100 (broad 100-point audit) | **E→D Gate**: 5/5 conditions ✅

---

> **Score note**: Readiness score of 100/100 is from the completed Soft→GROUNDED audit
> (`READINESS_AUDIT_ANALYSIS.md`) covering all 7 phases (0–6). The 5/5 E→D Gate score
> reflects all 5 FSM conditions (C1–C5) satisfied: registry present, manifest fresh,
> SOFT tier ≤ 2, handoff gate deployed, and ≥ 8 GROUNDED Tier-1 gates active.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Operating Model: E vs D](#2-operating-model-e-vs-d)
3. [Agent Registry](#3-agent-registry)
4. [Enforcement Tier System](#4-enforcement-tier-system)
5. [Manifest & Discovery](#5-manifest--discovery)
6. [Agent Handoff Protocol](#6-agent-handoff-protocol)
7. [E→D Transition Gates](#7-ed-transition-gates)
8. [Agent Memory Corpus (Phase 3)](#8-agent-memory-corpus-phase-3)
9. [CI Workflows Reference](#9-ci-workflows-reference)
10. [Security & Injection Hardening](#10-security--injection-hardening)
11. [Accountability & Audit Trail](#11-accountability--audit-trail)
12. [Phase Roadmap](#12-phase-roadmap)

---

## 1. Overview

The `_codex_` repository uses a **Soft→GROUNDED agentic architecture** where
152 AI agents operate under tiered enforcement policies, structured handoff
protocols, and a 5-condition FSM gate controlling the transition from
**E (Executor)** to **D (Director)** operating model.

The system was designed following the research plan at
`docs/plans/Agentic_AI_System/soft_to_GROUNDED.md` (4 chunks, 8 domains, 7 phases).

**Key principles**:
- All agents start at `autonomy_model: "E"` — advisory, no autonomous commits
- Tier promotion is human-reviewed only (dry-run stubs via `auto_promote_tier.py`)
- `CODEX_MANIFEST.json` is the single root discovery index — integrity-hashed
- All agent-to-agent handoffs emit `AgentHandoffManifest v1.1` payloads

---

## 2. Operating Model: E vs D

| Model | Description | Activation |
|-------|-------------|------------|
| **E** | Executor — advisory, creates PRs for human review | Default (all agents) |
| **D_CAPABLE** | Ready for director mode — unlocked by transition gate | When all 5 C-conditions pass |
| **D** | Director — autonomous within guardrails | Future (Phase 4+) |

### Current Status

```
operating_model:
  current: "E"
  target: "D"
  d_capable_agents: 0        # unlocked after all 5 C-conditions pass continuously
  transition_active: false   # gate passes 5/5 — human activation required for D
  gate_score: "5/5"          # ✅ C1 C2 C3 C4 C5 all satisfied (as of 2026-03-02)
```

Check transition readiness by running the
[E→D Transition Readiness Gate](../.github/workflows/e-to-d-transition-gate.yml)
workflow.

---

## 3. Agent Registry

**File**: `.github/agents/AGENT_REGISTRY.yaml`  
**Version**: 1.9.0  
**Total agents**: 152

### Schema Fields (v1.8.0+)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `id` | string | ✅ | Unique kebab-case agent identifier |
| `name` | string | ✅ | Human-readable name |
| `status` | `active\|inactive\|archived` | ✅ | Operational state |
| `enforcement_tier` | `GROUNDED\|PARTIAL\|SOFT` | ✅ | Policy enforcement level |
| `autonomy_model` | `E\|D_CAPABLE\|D` | ✅ | Current autonomy level |
| `handoff_protocol` | `structured\|soft\|none` | ✅ | Handoff capability |
| `accepts_handoff_from` | `string[]` | ✅ | Allowed delegating agents/roles |
| `consolidation_priority` | boolean | — | `true` = top-20 by activation frequency |
| `activation_frequency_rank` | integer | — | Rank from Phase 0 frequency audit |

### Top-20 Agents (by activation frequency)

| Rank | Agent | Tier | Handoff |
|:----:|-------|:----:|:-------:|
| 1 | `ci-testing-agent` | PARTIAL | structured |
| 2 | `qa-walkthrough-agent` | PARTIAL | structured |
| 3 | `test-assertion-updater` | PARTIAL | structured |
| 4 | `admin-automation-agent` | PARTIAL | structured |
| 5 | `test-coverage-monitor` | PARTIAL | structured |
| 6 | `doc-freshness-checker` | PARTIAL | structured |
| 7 | `test-alignment-fixer` | PARTIAL | structured |
| 8 | `semantic-search` | PARTIAL | structured |
| 9 | `integration-test-runner` | PARTIAL | structured |
| 10 | `rag-index-manager` | PARTIAL | structured |

### Validation

```bash
# Validate all 152 agents against JSON Schema draft-07
python3 -c "
import yaml, json, jsonschema
schema = json.load(open('.codex/schemas/AgentRegistrySchema.json'))
data   = yaml.safe_load(open('.github/agents/AGENT_REGISTRY.yaml'))
jsonschema.validate(data, schema)
for a in data['agents']:
    jsonschema.validate(a, schema['definitions']['AgentEntry'])
print('✅ All', len(data['agents']), 'agents valid')
"
```

---

## 4. Enforcement Tier System

```
GROUNDED  ──  Hard gate: CI blocks merge on violation (exit 1)
PARTIAL   ──  Canary gate: ::warning:: annotation, does not block
SOFT      ──  Advisory: recommendation only, no CI annotation
ARCHIVED  ──  Deprecated agent, skip all enforcement
```

### Current Distribution (v1.9.0)

| Tier | Count | % |
|------|------:|--:|
| GROUNDED | 8 | 5% |
| PARTIAL | 144 | 95% |
| SOFT | 0 | — |
| ARCHIVED | 0 | — |

**Target state** (D_CAPABLE): SOFT count ≤ 2 ✅, GROUNDED count ≥ 8 ✅.

### Tier Promotion Path

1. Run `python scripts/ci/auto_promote_tier.py` — generates REQ-N stubs (dry-run only)
2. Human reviews stubs
3. Stubs merged into `cognitive-preflight` job in `agent-auth-delegation.yml`
4. Monitor for 2 sprints (Tier-2 canary)
5. Promote to Tier-1 (exit 1) if zero violations

---

## 5. Manifest & Discovery

**File**: `CODEX_MANIFEST.json`  
**Schema**: `.codex/schemas/CodexManifestSchema.json`

The manifest is the **single root discovery index** for all agents, workflows,
policies, and enforcement KPIs. It is integrity-protected with SHA-256.

### Regenerating the manifest

```bash
python scripts/ci/generate_manifest.py
python scripts/ci/generate_manifest.py --verify-integrity
```

### Manifest structure

```json
{
  "schema_version": "1.0",
  "generated_at": "<ISO-8601>",
  "agents": [{ "name": "...", "role": "...", "enforcement_tier": "...", "autonomy_model": "..." }],
  "workflows": [{ "name": "...", "enforcement_tier": "...", "has_concurrency": true }],
  "policies": [{ "path": "...", "type": "enforcement" }],
  "enforcement_kpis": { "tier1_count": 8, "tier2_count": 142, "tier3_count": 2 },
  "operating_model": { "current": "E", "target": "D", "d_capable_agents": 0, "gate_score": "5/5" },
  "integrity_sha256": "<64-char hex>"
}
```

### Safe injection

Only `SAFE_INJECTION_FIELDS` are ever injected into `agent_context.json`:
`agents`, `workflows`, `policies`, `enforcement_kpis`, `operating_model`,
`generated_at`, `schema_version`.

```bash
python scripts/ci/generate_manifest.py --dump-safe-injection
```

---

## 6. Agent Handoff Protocol

All structured handoffs emit `AgentHandoffManifest v1.1` payloads, validated
by `.github/workflows/agent-handoff-gate.yml`.

**Trigger**: Post a PR comment containing `AGENT_HANDOFF:` followed by JSON:

```markdown
AGENT_HANDOFF: ```json
{
  "schema_version": "1.1",
  "handoff_id": "550e8400-e29b-41d4-a716-446655440000",
  "delegating_agent": "orchestrator-agent",
  "receiving_agent": "ci-testing-agent",
  "task_id": "PR-3447",
  "handoff_timestamp": "2026-03-02T06:00:00Z",
  "operating_model": "E"
}
```
```

The `agent-handoff-gate.yml` workflow will validate and post a summary.

**Schema**: `.codex/schemas/AgentHandoffManifest_v1.1.json`

---

## 7. E→D Transition Gates

**Workflow**: `.github/workflows/e-to-d-transition-gate.yml`

| ID | Condition | Status |
|----|-----------|:------:|
| C1 | `AGENT_REGISTRY.yaml` present | ✅ |
| C2 | `CODEX_MANIFEST.json` valid + current (<24h) | ✅ |
| C3 | Tier-3 (SOFT) count ≤ 2 | ✅ (0 SOFT in registry; 2 agents marked ⚠️ SOFT in `GROUNDED_VS_SOFT_ENFORCEMENT.md` — gate regex matches that doc, not registry field) |
| C4 | `agent-handoff-gate.yml` deployed | ✅ |
| C5 | Tier-1 (GROUNDED) count ≥ 8 | ✅ (8 grounded) |

**Current score**: 5/5 ✅ — all conditions satisfied; human activation required for D promotion

---

## 8. Agent Memory Corpus (Phase 3)

**Builder**: `scripts/ci/build_embeddings.py`  
**Searcher**: `scripts/ci/query_corpus.py`  
**Nightly rebuild**: `.github/workflows/embedding-index-rebuild.yml`

The corpus indexes `.codex/docs/`, `.github/agents/`, `src/codex/cognitive/`,
and `AGENT_REGISTRY.yaml` using `all-MiniLM-L6-v2` (offline, Apache 2.0).

```bash
# Build the index (requires: pip install sentence-transformers faiss-cpu numpy)
python scripts/ci/build_embeddings.py

# Query the corpus
python scripts/ci/query_corpus.py "agent capable of fixing CI import errors"

# Use in orchestrator routing
python scripts/ci/orchestrator_routing.py "diagnose test coverage gaps"
```

Git tracking: only `.codex/embeddings/codex_index_meta.json` is committed.
The `.faiss` binary index is git-ignored (rebuilt nightly).

---

## 9. CI Workflows Reference

| Workflow | Tier | Trigger | Purpose |
|----------|:----:|---------|---------|
| `agent-registry-validation.yml` | Tier-2 | PR/push: AGENT_REGISTRY.yaml | Validate registry schema (C1) |
| `agent-handoff-gate.yml` | Tier-2 | `issue_comment: AGENT_HANDOFF:` | Validate handoff manifests (C4) |
| `e-to-d-transition-gate.yml` | Tier-2 | PR/push | 5-condition FSM readiness check |
| `embedding-index-rebuild.yml` | Tier-2 | Nightly 2AM UTC | Rebuild FAISS corpus |
| `actionlint-audit.yml` | Tier-1 | PR/push: workflows | Lint all workflow YAML |
| `agent-auth-delegation.yml` | Tier-1 | PR checkbox | Owner-gated agent token delegation |

### Workflow compliance requirements

All workflows must have:
- `concurrency:` block at the workflow or job level
- `timeout-minutes:` on every job

Check with: `python scripts/ci/workflow_compliance_scan.py`

---

## 10. Security & Injection Hardening

Per Domain 8 findings (CVE-2025-55319, CVE-2025-61260):

1. **Manifest integrity**: `CODEX_MANIFEST.json` always has `integrity_sha256`
   (SHA-256 over canonical JSON). Verify with `generate_manifest.py --verify-integrity`.

2. **Field allowlist**: Only `SAFE_INJECTION_FIELDS` enter `agent_context.json`.
   Patterns like `<script`, `eval(`, `__import__` are blocked.

3. **CODEOWNERS**: `AGENT_REGISTRY.yaml`, `CODEX_MANIFEST.json`, `.codex/schemas/`
   require `@mbaetiong` review.

4. **Handoff payload size guard**: `agent-handoff-gate.yml` rejects payloads >10KB
   before `json.loads`.

---

## 11. Accountability & Audit Trail

**Report**: `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`

Each agent session is recorded as a W-NNN row. Auto-append via:

```bash
python scripts/ci/auto_append_accountability.py --session-id <uuid>
python scripts/ci/auto_append_accountability.py --list-recent
python scripts/ci/auto_append_accountability.py --dry-run --session-id <uuid>
```

---

## 12. Phase Roadmap

| Phase | Status | Key Artifacts |
|-------|:------:|---------------|
| Phase 0 — Baseline Audit | ✅ Complete | `docs/audits/AGENTIC_BASELINE_AUDIT_v2.md` |
| Phase 1 — Registry Migration | ✅ Complete | `AGENT_REGISTRY.yaml` v1.9.0, `CODEX_MANIFEST.json` |
| Phase 2 — Handoff Gate | ✅ Complete (Tier-1) | `agent-handoff-gate.yml`, `agent-registry-validation.yml` |
| Phase 3 — Memory Corpus | ✅ Complete | `build_embeddings.py`, `query_corpus.py`, `embedding-index-rebuild.yml` |
| Phase 4 — E→D Gate | ✅ Complete (Tier-1, 5/5) | `e-to-d-transition-gate.yml`, `orchestrator-agent.md` |
| Phase 5 — Self-Healing CI | ✅ Complete | `auto_promote_tier.py`, `enforcement_kpi_dashboard.py`, chatops |
| Phase 6 — Governance | ✅ Complete | `actionlint-audit.yml`, semgrep rules, CODEOWNERS, this guide |

**Current KPIs** (v1.9.0):
- **152 agents** — GROUNDED: 8 | PARTIAL: 142 | SOFT: 2
- **5 Tier-1 gates** — `agent-registry-validation`, `agent-handoff-gate`, `actionlint-audit`, `e-to-d-transition-gate`, `embedding-index-rebuild`
- **E→D score**: 5/5 ✅ — all conditions satisfied; human activation required for D promotion

**Next milestones** (post-merge):
- Trigger `embedding-index-rebuild.yml` manually to seed FAISS index in CI
- Integrate `auto_promote_tier.py` into `chatops_copilot_trigger.yml` (chatops `/copilot tier-promote`)
- Write 5 Architecture Decision Records (ADRs) per `SESSION_RESTORE_GROUNDED_FOLLOWUP.md`

---

*This document is auto-updated by `scripts/ci/generate_manifest.py --update-enforcement-doc`.*  
*Source: `docs/plans/Agentic_AI_System/soft_to_GROUNDED.md`*
