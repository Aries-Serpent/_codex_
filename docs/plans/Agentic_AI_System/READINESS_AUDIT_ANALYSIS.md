# Soft → GROUNDED Conversion: Readiness Audit Analysis

> **Generated:** 2026-03-02 | **Repo:** Aries-Serpent/_codex_
> **Source Document:** [`soft_to_GROUNDED.md`](soft_to_GROUNDED.md)
> **Purpose:** Audit challenges, assess groundwork, score readiness, and parse into Copilot agent work units

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Challenge Analysis](#challenge-analysis)
3. [Groundwork Assessment](#groundwork-assessment)
4. [Readiness Implementation Score](#readiness-implementation-score)
5. [Expected Execution Timeline](#expected-execution-timeline)
6. [Parsed Implementation Plan for Iterative Copilot Coding Agent Sessions](#parsed-implementation-plan)

---

## Executive Summary

The `soft_to_GROUNDED.md` document is a comprehensive deep research output spanning 4 chunks,
8 research domains (D1–D8), and 7 implementation phases (Phase 0–6). It proposes transforming the
`_codex_` repository's agent behavioral enforcement from predominantly **soft** (text-based, passively
bypassed) to **GROUNDED** (structurally enforced CI gates that require conscious override to bypass).

**Key Deliverables Across All Phases:**
- `AGENT_REGISTRY.yaml` — Centralized agent catalog (Microsoft AgentSchema)
- `CODEX_MANIFEST.json` — Root discovery index with integrity hashing
- `AgentHandoffManifest v1.1` — Structured agent-to-agent delegation protocol
- FAISS + SQLite unified agent memory corpus
- E→D tiered autonomy transition gate system
- Self-healing CI enforcement gap detection loop
- Policy-as-Code validation infrastructure

**Current Repository State:** The repository has extensive existing infrastructure (91 workflows,
128 registered agents per `AGENT_REGISTRY.yaml` v1.7.0, comprehensive accountability reporting) but lacks the structural registry at root level,
manifest, and gate system described in the plan. The planning is thorough and research-validated;
the codebase needs targeted preparation before execution can begin.

**Readiness Score: 68/100** — Ready for Phase 0 execution with minor preparation.

---

## Challenge Analysis

### C-1: Agent Count Discrepancy (Impact: Medium)

| Aspect | Document States | Actual Repo |
|--------|----------------|-------------|
| Agent definitions | 193 agents | 372 `.md` files across `.github/agents/**`; 128 registered in `.github/agents/AGENT_REGISTRY.yaml` v1.7.0 |
| Active workflows | ~90 workflows | 91 `.yml` files in `.github/workflows/` |

**Challenge:** The document references 193 agents throughout, but the repo contains 372 agent
`.md` files spread across nested subdirectories, with 128 formally registered in the existing
`.github/agents/AGENT_REGISTRY.yaml`. This discrepancy (372 files vs. 128 registered vs. 193
referenced in the plan) must be resolved in Phase 0 — likely many files are sub-components,
templates, or archived agents not yet tagged. The Phase 0 frequency audit (Task 2) must establish
the canonical active agent count before a root-level registry can be built.

**Mitigation:** Phase 0 Task 2 (`agent_frequency_audit.py`) explicitly addresses this by
scanning for actual activation frequency. Inactive/archived agents can be tagged
`enforcement_tier: "ARCHIVED"` in the registry rather than excluded.

---

### C-2: No Existing Registry or Manifest Infrastructure (Impact: High)

The following critical files referenced throughout the document **do not exist yet** in their plan-specified form:

| File | Referenced In | Current Status |
|------|--------------|----------------|
| `AGENT_REGISTRY.yaml` (root-level, plan schema) | Phases 1–6 | ⚠️ `.github/agents/AGENT_REGISTRY.yaml` exists (128 agents, v1.7.0) — Phase 1 must extend or migrate this to the root-level format |
| `CODEX_MANIFEST.json` | Phases 1–6 | ❌ Does not exist |
| `scripts/ci/generate_manifest.py` | Phases 1, 3, 5 | ❌ Does not exist |
| `.codex/schemas/AgentRegistrySchema.json` | Phase 1 | ❌ Does not exist |
| `.codex/schemas/CodexManifestSchema.json` | Phase 1 | ❌ Does not exist |
| `.codex/schemas/AgentHandoffManifest_v1.1.json` | Phase 2 | ❌ Does not exist |
| `scripts/ci/workflow_compliance_scan.py` | Phase 0 | ❌ Does not exist |
| `scripts/ci/build_embeddings.py` | Phase 3 | ❌ Does not exist |

**Note on AGENT_REGISTRY.yaml:** The existing `.github/agents/AGENT_REGISTRY.yaml` (128 agents,
Microsoft AgentSchema–inspired, v1.7.0) is a strong foundation. Phase 1 should extend this
registry rather than create a duplicate — either by migrating it to the root or expanding its
schema to include the plan's `enforcement_tier`, `autonomy_model`, and `handoff_protocol` fields.

**Challenge:** All downstream phases (1–6) depend on Phase 0 and Phase 1 artifacts.
The registry is the foundation — errors in its structure cascade through every subsequent phase.

**Mitigation:** Phase 0 creates the audit baseline; Phase 1 creates the registry. The document
provides exact code patterns for each file, reducing implementation ambiguity.

---

### C-3: `cognitive-preflight` Integration Point (Impact: High)

The document references `cognitive-preflight` as the primary Tier-1 gate mechanism
(REQ-1 through REQ-N). This appears to be a job within `agent-auth-delegation.yml` rather
than a standalone workflow.

**Challenge:** Adding new REQ-N gates (REQ-9 for manifest integrity, REQ-10 for corpus health)
requires modifying `agent-auth-delegation.yml`, which is a critical-path workflow. Regressions
in this workflow could block all agent delegation.

**Mitigation:**
- New gates start as **Tier-2 canary** (`::warning::` not `exit 1`)
- 2-sprint observation period before promotion to Tier-1
- Each REQ-N addition is a separate commit with YAML parse verification

---

### C-4: Security Surface — Context Injection (Impact: Critical)

Domain 8 of the research identifies **context injection attacks** as the #1 new risk introduced
by `CODEX_MANIFEST.json` and `agent_context.json` injection (CVE-2025-55319, CVE-2025-61260).

**Challenge:** The manifest becomes a new attack vector if not properly hardened. The
`sanitize_for_injection()` function and `INJECTION_BLOCKLIST` are described but not yet
implemented. This must be in place **before** any manifest data is injected into agent context.

**Mitigation:** The document specifies:
- `SAFE_INJECTION_FIELDS` allowlist (7 fields only)
- `INJECTION_BLOCKLIST` regex patterns (7 patterns)
- `integrity_sha256` tamper detection
- CODEOWNERS protection for manifest and registry files

---

### C-5: Dependency Installation for Phase 3 (Impact: Medium)

Phase 3 requires `sentence-transformers` (~80MB model download) and `faiss-cpu` for the
FAISS index builder. While both are used elsewhere in the codebase (RAG modules), the CI
runner needs explicit installation.

**Challenge:** The `build_embeddings.py` script requires model download on first run. CI
runners may have network restrictions or timeout issues.

**Mitigation:**
- Model `all-MiniLM-L6-v2` is only ~80MB
- The nightly rebuild workflow (`embedding-index-rebuild.yml`) allows up to 15 minutes
- The FAISS index binary is git-ignored; only metadata JSON is committed

---

### C-6: Workflow Cascade Risk (Impact: High)

Repository memory confirms a March 2026 incident where `workflow_run: ["*"]` wildcards
caused 12,272 queued runs. Adding new workflows (4 planned) increases cascade risk if
concurrency controls are not applied consistently.

**Challenge:** New workflows (`agent-handoff-gate.yml`, `e-to-d-transition-gate.yml`,
`embedding-index-rebuild.yml`, `actionlint-audit.yml`) must all have branch-scoped
concurrency groups and `timeout-minutes` on every job.

**Mitigation:** Phase 0's `workflow_compliance_scan.py` will establish the baseline
cascade risk count. The document includes concurrency patterns for every new workflow.

---

### C-7: Phase Ordering Dependencies (Impact: Medium)

```
Phase 0 ──► Phase 1 ──► Phase 2 ──┬──► Phase 4 ──► Phase 6
                         Phase 3 ──┘        │
                                    Phase 5 ◄┘
```

Phases 2 and 3 can run in parallel after Phase 1. Phase 4 needs Phase 1 + 2 complete.
Phase 5 needs Phase 3 + 4 signals. Phase 6 is the final hardening pass.

**Challenge:** If Phase 3 (embedding corpus) is slow, Phase 4 (E→D transition gate)
can proceed with degraded routing (zero-session baseline) but won't have full semantic
search capability until Phase 3 completes.

**Mitigation:** Risk R-15 in the document explicitly addresses this with a degraded
fallback mode for Phase 4.

---

### C-8: Human Approval Gates (Impact: Low)

Each phase completion gate requires `mbaetiong approval received before Phase N+1 begins`.
This is a deliberate safety control, not a blocker — but it means phases cannot be
auto-chained without human review.

**Mitigation:** This is by design. The Copilot Coding Agent completes each phase and
posts the completion gate checklist; the human approves before the next phase starts.

---

## Groundwork Assessment

### Required Preparation Before Phase 0 Execution

| # | Groundwork Item | Status | Priority | Effort |
|---|----------------|--------|----------|--------|
| G-1 | Confirm active agent count (372 files; 128 in AGENT_REGISTRY.yaml → reconcile with doc's 193) | ⚠️ Partially done (registry exists, reconciliation needed) | **P0** | 1 session |
| G-2 | Create `docs/audits/` directory | ❌ Not started | **P0** | Trivial |
| G-3 | Verify `jsonschema` importable in current Python env | ✅ In pyproject.toml | Done | — |
| G-4 | Verify `pyyaml` importable in current Python env | ✅ In pyproject.toml | Done | — |
| G-5 | Confirm `agent-auth-delegation.yml` structure (locate cognitive-preflight job) | ❌ Not inspected | **P0** | 1 hour |
| G-6 | Confirm `.github/CODEOWNERS` has correct format for new entries | ✅ Exists (234 lines) | Done | — |
| G-7 | Confirm `CHANGELOG.md` format for new Phase entries | ✅ Exists at root | Done | — |
| G-8 | Confirm `AGENT_ACCOUNTABILITY_REPORT.md` W-NNN format | ✅ Exists | Needs format check | 30 min |
| G-9 | Ensure no merge conflicts with `main` branch | ❌ Not checked | **P0** | Variable |
| G-10 | Assess `.github/agents/AGENT_REGISTRY.yaml` (v1.7.0, 128 agents) and determine extend vs. migrate strategy for Phase 1 | ❌ Not started | **P0** | 1 session |

### Existing Infrastructure That Supports Execution

| Infrastructure | Status | Supports Phase(s) |
|---------------|--------|-------------------|
| `agent-auth-delegation.yml` (cognitive-preflight host) | ✅ Exists | All (REQ-N gates) |
| `ci-health-monitor.yml` | ✅ Exists | Phase 5 (self-healing loop) |
| `copilot-agent-vars-bootstrap.yml` | ✅ Exists | Phase 1 (manifest injection) |
| `session-watchdog.yml` | ✅ Exists | All (timebox enforcement) |
| `token-probe.yml` | ✅ Exists | All (token health) |
| `self_healing_ci.yml` + `iterative-self-healing-ci.yml` | ✅ Exist | Phase 5 (self-healing extension) |
| `chatops_copilot_trigger.yml` | ✅ Exists | Phase 5 (session close hook) |
| `.codex/docs/GROUNDED_VS_SOFT_ENFORCEMENT.md` | ✅ Exists | All (enforcement tier reference) |
| `.codex/docs/AGENT_HANDOFF_PROTOCOL.md` | ✅ Exists | Phase 2 (protocol documentation) |
| `.codex/schemas/` directory | ✅ Exists (2 schemas) | Phase 1 (schema home) |
| `docs/architecture/` directory | ✅ Exists (13 files) | Phase 0 (transition map home) |
| `.github/CODEOWNERS` | ✅ Exists (234 lines) | Phase 1 (security entries) |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | ✅ Exists | All (W-NNN tracking) |
| `CHANGELOG.md` | ✅ Exists | All (phase entries) |
| FAISS/sentence-transformers in codebase | ✅ Used in RAG modules | Phase 3 (patterns available) |
| `jsonschema` dependency | ✅ In pyproject.toml | Phases 1, 2 (schema validation) |
| `pyyaml` dependency | ✅ In pyproject.toml | Phases 0, 1 (YAML parsing) |
| `sqlite3` | ✅ Python stdlib | Phases 3, 4, 5 |

---

## Readiness Implementation Score

### Scoring Methodology

Each dimension is scored on its scale based on the ratio of existing infrastructure
to required infrastructure for Phase 0 execution readiness. A score of 100 means
all prerequisites are met and execution can begin immediately.

### Dimension Scores

| # | Dimension | Weight | Score | Max | Details |
|---|-----------|--------|-------|-----|---------|
| D1 | **CI/CD Workflow Foundation** | 20 | 16 | 20 | 91 workflows exist; 8 key workflows confirmed present; needs 4 new workflows (Phase 2–6 scope, not Phase 0 blockers) |
| D2 | **Agent Ecosystem Maturity** | 20 | 12 | 20 | 128 agents in AGENT_REGISTRY.yaml (v1.7.0); 372 total .md files across nested dirs; count discrepancy with doc's 193 still to reconcile; no GROUNDED registry schema yet (Phase 1 scope) |
| D3 | **Enforcement Architecture** | 15 | 9 | 15 | GROUNDED_VS_SOFT doc exists; enforcement tiers documented; cognitive-preflight in agent-auth-delegation; no REQ-9/10 gates yet |
| D4 | **Data Infrastructure** | 10 | 6 | 10 | FAISS/sentence-transformers used in RAG modules; sqlite3 available; no unified corpus yet (Phase 3 scope) |
| D5 | **Security Posture** | 10 | 6 | 10 | CODEOWNERS exists (234 lines); no agentic-specific entries yet; no injection hardening (Phase 1 scope) |
| D6 | **Documentation & Audit Trail** | 15 | 12 | 15 | Accountability report exists; CHANGELOG exists; architecture docs exist; no audits/ directory yet (Phase 0 scope) |
| D7 | **Dependencies & Tooling** | 10 | 7 | 10 | jsonschema + pyyaml available; faiss-cpu/sentence-transformers installable; no actionlint/semgrep (Phase 5–6 scope) |
| | **TOTAL** | **100** | **68** | **100** | |

### Readiness Score: **68 / 100**

```
██████████████████████████████████░░░░░░░░░░░░░░░░  68%
```

### Score Interpretation

| Range | Meaning | Our Status |
|-------|---------|------------|
| 90–100 | Execution-ready — begin immediately | — |
| 75–89 | Ready with minor prep — 1 session prep needed | — |
| **60–74** | **Ready for Phase 0 — groundwork items addressable in Phase 0 itself** | **← We are here (68)** |
| 40–59 | Significant gaps — multiple prep sessions needed | — |
| 0–39 | Major infrastructure missing — plan revision needed | — |

**Verdict:** The repository is **ready to begin Phase 0 execution**. The gaps identified
(missing registry, manifest, audit scripts) are exactly what Phase 0 and Phase 1 create.
No blocking infrastructure deficiencies prevent starting.

---

## Expected Execution Timeline

### Phase Duration Estimates

| Phase | Name | Est. Sessions | Est. Calendar Days | Dependencies | Confidence |
|-------|------|:------------:|:------------------:|-------------|:----------:|
| **Phase 0** | Baseline Audit | 2–3 | 3–5 days | None | ✅ High |
| **Phase 1** | Agent Registry & Discovery | 3–4 | 5–7 days | Phase 0 gate + owner approval | ✅ High |
| **Phase 2** | Handoff Protocol + Top-20 | 4–5 | 7–10 days | Phase 1 gate + owner approval | 🟡 Medium |
| **Phase 3** | Memory Corpus (FAISS+SQLite) | 2–3 | 3–5 days | Phase 1 (parallel with Phase 2) | ✅ High |
| **Phase 4** | E→D Transition Gate | 2–3 | 3–5 days | Phase 1 + Phase 2 | 🟡 Medium |
| **Phase 5** | Self-Healing & Auto-Docs | 3–4 | 5–7 days | Phase 3 + Phase 4 | 🟡 Medium |
| **Phase 6** | Final Hardening & Guide | 2–3 | 3–5 days | Phase 5 | ✅ High |

### Timeline Summary

```
Week 1          Week 2          Week 3          Week 4          Week 5          Week 6
─────────────── ─────────────── ─────────────── ─────────────── ─────────────── ───────────
▓▓▓▓░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░
Phase 0          ▓▓▓▓▓▓▓▓░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░
                 Phase 1         ▓▓▓▓▓▓▓▓▓▓░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░
                                 Phase 2 ────────►▓▓▓▓░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░
                                 Phase 3 ─► ▓▓▓▓▓░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░
                                                   Phase 4 ▓▓▓▓▓▓░░ ░░░░░░░░░░░░░░░ ░░░░░░░░░░
                                                            Phase 5  ▓▓▓▓▓▓▓▓░░░░░░░ ░░░░░░░░░░
                                                                                Phase 6 ▓▓▓▓▓▓░░
```

**Estimated Total: 5–7 weeks** (including human approval gates between phases)

**Earliest Phase 0 start:** Immediate (this session or next)
**Earliest Phase 6 completion:** ~Week 6 from Phase 0 start (~mid-April 2026)

### Key Milestones

| Milestone | Target Date | Deliverable |
|-----------|-------------|-------------|
| Phase 0 Complete | Week 1 end | `WORKFLOW_COMPLIANCE_MATRIX.md`, `AGENTIC_BASELINE_AUDIT_v2.md`, `E_TO_D_TRANSITION_MAP.md` |
| Phase 1 Complete | Week 2 end | `AGENT_REGISTRY.yaml`, `CODEX_MANIFEST.json`, `generate_manifest.py`, REQ-9 gate |
| Phase 2+3 Complete | Week 4 end | Handoff protocol + top-20 consolidation + FAISS corpus |
| Phase 4 Complete | Week 5 start | E→D transition gate system |
| Phase 5 Complete | Week 5 end | Self-healing enforcement gap loop |
| Phase 6 Complete | Week 6 | Final hardening, `AGENTIC_REPO_SYSTEM_GUIDE.md` |

---

## Parsed Implementation Plan

### Structure for Iterative Copilot Coding Agent Sessions

Each phase below is broken into **atomic work units** (WU) sized for a single Copilot
Coding Agent session (~1–2 hours of focused work). Each WU has clear inputs, outputs,
and verification criteria.

---

### 🔷 PHASE 0 — Baseline Audit (3 Work Units)

#### WU-0.1: Workflow Compliance Scan

**Objective:** Create and run the workflow compliance scanning script.

**Inputs:**
- `.github/workflows/*.yml` (all matching files; currently 91)
- Pattern from `soft_to_GROUNDED.md` Domain 7

**Tasks:**
1. Create `docs/audits/` directory
2. Create `scripts/ci/workflow_compliance_scan.py` (Python script using `pyyaml`)
3. Run script → generate `docs/audits/WORKFLOW_COMPLIANCE_MATRIX.md`
4. Record KPI baselines (GROUNDED/PARTIAL/SOFT counts, cascade risks)

**Outputs:**
- `scripts/ci/workflow_compliance_scan.py`
- `docs/audits/WORKFLOW_COMPLIANCE_MATRIX.md`

**Verification:**
- Matrix covers all workflow files in `.github/workflows/` (use `glob("*.yml")` count at runtime, not a hard-coded number)
- KPI counts are real numbers (not placeholders)

---

#### WU-0.2: Agent Frequency Audit & Classification

**Objective:** Determine active agent count, rank by activation frequency, classify enforcement tiers.

**Inputs:**
- `.github/agents/**/*.md` (recursive; 372 files across nested subdirectories)
- `.github/agents/AGENT_REGISTRY.yaml` (128 formally registered agents, v1.7.0)
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- `.github/workflows/*.yml` (agent name references)

**Tasks:**
1. Create `scripts/ci/agent_frequency_audit.py`
2. Scan all sources for agent activation mentions
3. Deduplicate and establish canonical active agent count
4. Classify each agent: `enforcement_tier`, `handoff_protocol`
5. Flag top-20 by frequency for Phase 2 consolidation
6. Create `docs/audits/AGENTIC_BASELINE_AUDIT_v2.md` with all classifications

**Outputs:**
- `scripts/ci/agent_frequency_audit.py`
- `docs/audits/AGENTIC_BASELINE_AUDIT_v2.md`

**Verification:**
- Agent count reconciled (document's 193 vs. actual)
- Top-20 list based on data (not guessed)
- All KPI baselines filled with real numbers

---

#### WU-0.3: Architecture Map & Phase 0 Completion

**Objective:** Create E→D transition map, complete KPI baselines, update accountability.

**Inputs:**
- Phase 0 audit data from WU-0.1 and WU-0.2
- FSM diagram from `soft_to_GROUNDED.md` Domain 5

**Tasks:**
1. Create `docs/architecture/E_TO_D_TRANSITION_MAP.md` with Mermaid FSM diagram
2. Complete KPI baseline table in `AGENTIC_BASELINE_AUDIT_v2.md`
3. Add W-NNN entries to `AGENT_ACCOUNTABILITY_REPORT.md`
4. Add Phase 0 entry to `CHANGELOG.md`

**Outputs:**
- `docs/architecture/E_TO_D_TRANSITION_MAP.md`
- Updated `AGENTIC_BASELINE_AUDIT_v2.md` (KPI section)
- Updated `AGENT_ACCOUNTABILITY_REPORT.md`
- Updated `CHANGELOG.md`

**Verification:**
- All 9 Phase 0 completion gate conditions met
- Ready for owner approval to proceed to Phase 1

---

### 🔷 PHASE 1 — Agent Registry & Discovery (4 Work Units)

#### WU-1.1: JSON Schema Definitions + generate_manifest.py

**Objective:** Create the schema validation infrastructure and the central manifest generator.

**Tasks:**
1. Create `.codex/schemas/AgentRegistrySchema.json` (JSON Schema draft-07)
2. Create `.codex/schemas/CodexManifestSchema.json` (JSON Schema draft-07)
3. Create `scripts/ci/generate_manifest.py` with all 10 functions from the document
4. Run `generate_manifest.py` → verify initial `CODEX_MANIFEST.json`
5. Test `--verify-integrity` and `--dump-safe-injection` modes

**Outputs:**
- `.codex/schemas/AgentRegistrySchema.json`
- `.codex/schemas/CodexManifestSchema.json`
- `scripts/ci/generate_manifest.py`
- `CODEX_MANIFEST.json` (initial, 0 agents)

**Verification:**
- Schemas validate as valid JSON Schema draft-07
- `CODEX_MANIFEST.json` has `integrity_sha256` field
- 3 consecutive runs produce identical output (determinism)
- `--dump-safe-injection` contains only `SAFE_INJECTION_FIELDS`

---

#### WU-1.2: AGENT_REGISTRY.yaml — Build Full Registry

**Objective:** Create the complete agent registry from Phase 0 audit data.

**Tasks:**
1. Extend `.github/agents/AGENT_REGISTRY.yaml` (or migrate to root-level `AGENT_REGISTRY.yaml`) with GROUNDED schema fields
2. For each active agent (from Phase 0 frequency audit):
   - Populate `name`, `role`, `enforcement_tier`, `primary_workflow`
   - Set `autonomy_model: "E"` for all
   - Set `handoff_protocol` from Phase 0 classification
   - Set `activation_frequency_rank` from Phase 0 data
   - Flag top-20: `consolidation_priority: true`
3. Validate against `AgentRegistrySchema.json`

**Decision point (resolve in Phase 0):** Determine whether to:
- **Option A (extend):** Add new fields to existing `.github/agents/AGENT_REGISTRY.yaml` in-place
- **Option B (migrate):** Create root-level `AGENT_REGISTRY.yaml` and cross-reference the existing one

**Outputs:**
- `AGENT_REGISTRY.yaml` (all agents registered, with GROUNDED schema fields)

**Verification:**
- `total_agents` matches actual list length
- All entries pass schema validation
- Top-20 agents have `consolidation_priority: true`
- No duplicate registry with identical data exists

---

#### WU-1.3: REQ-9 Gate + CODEOWNERS Security

**Objective:** Add manifest integrity verification to the cognitive-preflight pipeline.

**Tasks:**
1. Add REQ-9 step to `agent-auth-delegation.yml` (Tier-2 canary: `::warning::`)
2. Verify YAML still parses after modification
3. Add Phase 1 CODEOWNERS entries for registry, manifest, schemas, agents
4. Regenerate `CODEX_MANIFEST.json` with full registry

**Outputs:**
- Updated `agent-auth-delegation.yml` (REQ-9 added)
- Updated `.github/CODEOWNERS` (Phase 1 entries)
- Updated `CODEX_MANIFEST.json` (full registry)

**Verification:**
- REQ-9 emits `::warning::` on corrupted manifest; passes on valid
- YAML parses correctly
- CODEOWNERS entries are syntactically valid

---

#### WU-1.4: Manifest Injection + Phase 1 Completion

**Objective:** Wire manifest into agent context and complete Phase 1 accountability.

**Tasks:**
1. Add manifest injection step to `copilot-agent-vars-bootstrap.yml`
2. Verify `agent_context.json` receives safe manifest fields only
3. Add W-NNN entries to `AGENT_ACCOUNTABILITY_REPORT.md`
4. Add Phase 1 entry to `CHANGELOG.md`
5. Verify all Phase 1 completion gate conditions

**Outputs:**
- Updated `copilot-agent-vars-bootstrap.yml`
- Updated `AGENT_ACCOUNTABILITY_REPORT.md`
- Updated `CHANGELOG.md`

**Verification:**
- All 12 Phase 1 completion gate conditions met
- `agent_context.json` contains only safe fields (no executable content)

---

### 🔷 PHASE 2 — Handoff Protocol + Top-20 (3 Work Units)

#### WU-2.1: Handoff Schema + Validation Script

**Tasks:**
1. Create `.codex/schemas/AgentHandoffManifest_v1.1.json`
2. Create `scripts/ci/validate_handoff_manifest.py`
3. Create test fixtures: `tests/fixtures/valid_handoff.json`, `tests/fixtures/invalid_handoff.json`
4. Validate both fixtures through the validator

---

#### WU-2.2: Handoff Gate Workflow + Phase 2+3 Bridge

**Tasks:**
1. Create `.github/workflows/agent-handoff-gate.yml` (Tier-2 canary)
2. Create `scripts/ci/handoff_context_population.py` (with Phase 3 stub)
3. Add CODEOWNERS entry for handoff gate
4. Validate workflow YAML

---

#### WU-2.3: Top-20 Consolidation (Batched)

**Tasks:**
1. Update top-20 agent `.md` files with structured handoff instructions
2. Update `AGENT_REGISTRY.yaml` entries: `handoff_protocol: "structured"`
3. Identify overlapping agents → add `aliases` field
4. Regenerate manifest, update accountability report + changelog
5. Verify Phase 2 completion gate

---

### 🔷 PHASE 3 — Memory Corpus (2 Work Units) [Parallel with Phase 2]

#### WU-3.1: Embedding Index Builder

**Tasks:**
1. Create `scripts/ci/build_embeddings.py` (FAISS + sentence-transformers)
2. Create `scripts/ci/query_corpus.py` (semantic + SQLite hybrid)
3. Create `.codex/embeddings/` directory
4. Add `.codex/embeddings/codex_index.faiss` to `.gitignore`
5. Test build and query locally

---

#### WU-3.2: Nightly Rebuild Workflow + Corpus Pruning

**Tasks:**
1. Create `.github/workflows/embedding-index-rebuild.yml` (nightly 2AM UTC)
2. Create `scripts/ci/prune_corpus.py` (90-day retention)
3. Add REQ-10 to cognitive-preflight (Tier-2 corpus health warning)
4. Update accountability report + changelog

---

### 🔷 PHASE 4 — E→D Transition Gate (2 Work Units)

#### WU-4.1: Transition Gate Workflow

**Tasks:**
1. Create `.github/workflows/e-to-d-transition-gate.yml` (5-condition FSM check)
2. Create `scripts/ci/orchestrator_routing.py` (FAISS→capability_tags routing)
3. Create `.github/agents/orchestrator-agent.md` (orchestrator definition)
4. Add CODEOWNERS entry

---

#### WU-4.2: Autonomy Demotion + Phase 4 Completion

**Tasks:**
1. Create autonomy demotion script (Phase 4+5 bridge)
2. Update all 193+ `AGENT_REGISTRY.yaml` entries with `role` tags
3. Add `operating_model` step to cognitive-preflight
4. Update accountability report + changelog

---

### 🔷 PHASE 5 — Self-Healing & Auto-Documentation (2 Work Units)

#### WU-5.1: Auto-Promotion + Auto-Accountability

**Tasks:**
1. Create `scripts/ci/auto_promote_tier.py` (dry-run REQ-N stub generator)
2. Create `scripts/ci/auto_append_accountability.py` (W-NNN auto-append)
3. Extend `ci-health-monitor.yml` with enforcement gap scan
4. Extend `generate_manifest.py` with `--update-enforcement-doc`

---

#### WU-5.2: KPI Dashboard + Phase 5 Completion

**Tasks:**
1. Add KPI dashboard comment injection to `ci-health-monitor.yml`
2. Wire autonomy demotion to violation threshold
3. Test full self-healing loop (gap detection → issue creation)
4. Update accountability report + changelog

---

### 🔷 PHASE 6 — Final Hardening (2 Work Units)

#### WU-6.1: Governance Tooling

**Tasks:**
1. Create `.github/workflows/actionlint-audit.yml` (permanent workflow linting)
2. Create `.codex/policies/semgrep/soft_enforcement.yaml` (Semgrep rules)
3. Create `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` (canonical operating guide)

---

#### WU-6.2: Final KPI Report + Completion

**Tasks:**
1. Create `docs/audits/AGENTIC_FINAL_KPI_REPORT.md` (Phase 0 repeat + delta)
2. Run full compliance scan → compare with Phase 0 baseline
3. Final accountability report + changelog entries
4. Verify all Phase 6 completion gate conditions

---

### Work Unit Summary

| Phase | Work Units | Est. Sessions | Key Deliverables |
|-------|:----------:|:-------------:|-----------------|
| Phase 0 | 3 | 2–3 | Compliance matrix, agent audit, E→D map |
| Phase 1 | 4 | 3–4 | Registry, manifest, generate_manifest.py, REQ-9 |
| Phase 2 | 3 | 4–5 | Handoff schema, gate workflow, top-20 consolidation |
| Phase 3 | 2 | 2–3 | FAISS builder, query module, nightly rebuild |
| Phase 4 | 2 | 2–3 | Transition gate, orchestrator routing |
| Phase 5 | 2 | 3–4 | Auto-promotion, self-healing loop |
| Phase 6 | 2 | 2–3 | actionlint, Semgrep, final guide |
| **Total** | **18** | **18–25** | Complete Soft→GROUNDED conversion |

---

## Risk Register Summary

| Risk | Severity | Phase | Mitigation Available |
|------|----------|-------|:-------------------:|
| R-11: Context injection via CODEX_MANIFEST.json | **Critical** | 1+ | ✅ integrity_sha256 + allowlist |
| R-12: Prompt injection via prior_context[] | **Critical** | 3+ | ✅ 300-char limit + blocklist |
| R-01: Premature E→D activation | High | 4 | ✅ 5-condition Tier-1 block |
| R-02: Top-20 consolidation errors | High | 2 | ✅ Alias-first, never delete |
| R-09: Orchestrator cascade | High | 4 | ✅ 1 max + 3 concurrent limit |
| R-13: Registry tampering | High | 1+ | ✅ integrity hash + CODEOWNERS |
| R-14: Malicious agent definitions | High | 2+ | ✅ Semgrep + CODEOWNERS |
| R-06: Canary PR comment noise | Medium | All | ✅ SHA-dedup + cooldown |

All critical and high risks have documented mitigation strategies in the source document.

---

## Recommendation

**Proceed to Phase 0 execution.** The repository has sufficient infrastructure to begin.
The readiness score of 68/100 reflects that gaps exist, but those gaps are exactly what
the phased plan addresses. No blocking prerequisites remain.

**Suggested first Copilot Coding Agent session:** WU-0.1 (Workflow Compliance Scan) —
this is the lowest-risk, highest-value starting point that produces immediate baseline data.

---

*Generated: 2026-03-02 | Source: [`soft_to_GROUNDED.md`](soft_to_GROUNDED.md)*
*Analysis performed against: Aries-Serpent/_codex_ repository at HEAD*
