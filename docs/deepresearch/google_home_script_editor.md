# DeepResearch: Google Home Script Editor — Automations, Templates, and File Formats

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [2. Repository Mapping](#2-repository-mapping)
- [3. Top 5 Workflows from Design to Production](#3-top-5-workflows-from-design-to-production)
  - [Workflow 1 — Schema Discovery and Template Extraction](#workflow-1--schema-discovery-and-template-extraction)
  - [Workflow 2 — Schema and Template Design with Validation](#workflow-2--schema-and-template-design-with-validation)
  - [Workflow 3 — Cognitive Pattern Recording for Automation Failures](#workflow-3--cognitive-pattern-recording-for-automation-failures)
  - [Workflow 4 — Template Validation and Production Gate](#workflow-4--template-validation-and-production-gate)
  - [Workflow 5 — Production Rollout with RAG-Assisted Context](#workflow-5--production-rollout-with-rag-assisted-context)
- [4. Top 5 Custom Agents to Design or Enhance](#4-top-5-custom-agents-to-design-or-enhance)
  - [Agent 1 — `google-home-script-agent` *(New)*](#agent-1--google-home-script-agent-new)
  - [Agent 2 — `energy-conversion-agent` *(Enhance)*](#agent-2--energy-conversion-agent-enhance)
  - [Agent 3 — `smart-home-template-guardian` *(New)*](#agent-3--smart-home-template-guardian-new)
  - [Agent 4 — `cognitive-home-automation-agent` *(New)*](#agent-4--cognitive-home-automation-agent-new)
  - [Agent 5 — `rag-home-knowledge-agent` *(New)*](#agent-5--rag-home-knowledge-agent-new)
- [5. Top 5 Conceptual Usages and Integrations](#5-top-5-conceptual-usages-and-integrations)
  - [Integration 1 — Pattern DB as Automation Failure Historian](#integration-1--pattern-db-as-automation-failure-historian)
  - [Integration 2 — YAML Strict Gate for Template Deployments](#integration-2--yaml-strict-gate-for-template-deployments)
  - [Integration 3 — Deepresearch Index as Automation Template Library](#integration-3--deepresearch-index-as-automation-template-library)
  - [Integration 4 — Energy Conversion Agent as Home Energy Optimizer](#integration-4--energy-conversion-agent-as-home-energy-optimizer)
  - [Integration 5 — RAG-Powered Automation Authoring Assistant](#integration-5--rag-powered-automation-authoring-assistant)
- [6. Relevant Repo Files and Docs](#6-relevant-repo-files-and-docs)
- [7. Constraints, Limitations, and Workarounds](#7-constraints-limitations-and-workarounds)
- [8. Recommended Next Actions](#8-recommended-next-actions)
- [Sources](#sources)

> **Generated:** 2026-03-25 | **Author:** Copilot Coding Agent (S192) | **PR:** #3741
> **Roles:** [Primary: Research Integrator], [Secondary: Agent Designer] ⚡ Energy: 8
> **Linked Agent:** `.github/agents/energy-conversion-agent.md` (cross-domain automation patterns)
> **Index:** `docs/deepresearch/INDEX.md`

---

## 1. Executive Summary

Google Home's **Script Editor** (launched 2024–2025) enables power users to write
**YAML-based automation scripts** directly in the Google Home app.  These scripts
use a structured `metadata` + `automations` schema with typed `starters`, optional
`condition` blocks, and `actions`.  As of 2025 the platform supports ~20 device
traits, Gemini-AI cognitive routines, Matter local control, and is in active staged
rollout.

**How this connects to `_codex_`**: The repository's cognitive brain, CI pattern
knowledge graph, agent framework, and RAG pipeline all exhibit structural patterns
— schema-driven automation, YAML validation gates, template reuse, and contextual
decision logic — that directly map to Google Home automation design.  Applying
`_codex_` conventions to this domain yields five reusable workflows, five custom
agents, and five cognitive-brain integration points documented below.

---

## 2. Repository Mapping

| Google Home Concept | `_codex_` Equivalent | File(s) |
|---|---|---|
| YAML automation schema | workflow YAML (`pre-merge-validation.yml`) | `.github/workflows/pre-merge-validation.yml` |
| `starters` (event triggers) | workflow `on:` triggers | all `.github/workflows/*.yml` |
| `condition` block (guard logic) | `check_only`/`dry_run` guard pattern | `scripts/ci/auto_fix_common_issues.py:1194` |
| `actions` (command dispatch) | `ci_pattern_pipeline.py` stages | `scripts/ci/ci_pattern_pipeline.py` |
| Template library | `auto_fix_common_issues.py` pattern map | `scripts/ci/auto_fix_common_issues.py:1242` |
| Automation indexing | deepresearch index | `docs/deepresearch/INDEX.md` |
| Cognitive routines (Gemini) | cognitive brain + `high_recurrence()` | `scripts/ci/pattern_recorder.py:310` |
| Cross-home pattern detection | cross-PR correlation | `scripts/ci/pattern_recorder.py` (Phase 8 P1) |
| Energy/device state tracking | energy-conversion-agent | `.github/agents/energy-conversion-agent.md` |
| Template validation | pre-commit hooks + ruff | `.pre-commit-config.yaml` |

---

## 3. Top 5 Workflows from Design to Production

### Workflow 1 — Schema Discovery and Template Extraction

| Attribute | Value |
|---|---|
| **Purpose** | Discover supported device traits and action types; extract reusable YAML automation templates |
| **Phase** | Discovery / Research |
| **Inputs** | `developers.home.google.com/automations/schema`, device trait list, user environment |
| **Outputs** | Template library (YAML files), `docs/deepresearch/google_home_templates/` |
| **Dependencies** | Google Home Developer API access, `scripts/ci/check_docs_index.py` for indexing |
| **Repo Convention** | Templates stored under `docs/deepresearch/`, auto-indexed by `check_docs_index.py --generate` |
| **Relevant Files** | `docs/deepresearch/INDEX.md`, `scripts/ci/check_docs_index.py:88-149` |

**YAML Template Example:**
```yaml
metadata:
  name: Night Mode
  description: Turn off all lights and lock front door at 23:00.
automations:
  - starters:
      - type: time.schedule
        at: "23:00"
    actions:
      - type: device.command.OnOff
        devices: [Living Room Light, Bedroom Light]
        on: false
      - type: device.command.LockUnlock
        devices: [Front Door Lock]
        lock: true
```

---

### Workflow 2 — Schema and Template Design with Validation

| Attribute | Value |
|---|---|
| **Purpose** | Design normalized YAML templates with linting/schema validation before deployment |
| **Phase** | Schema design / Validation |
| **Inputs** | Draft YAML scripts, device trait schema JSON |
| **Outputs** | Validated YAML templates, lint report |
| **Dependencies** | `yamllint`, `jsonschema`, Google Home schema spec |
| **Repo Convention** | Pre-commit YAML check (`.pre-commit-config.yaml`); CI schema validation step |
| **Relevant Files** | `.pre-commit-config.yaml`, `scripts/ci/auto_fix_common_issues.py` (Pattern 3: YAML Indentation) |

The repo's Pattern 3 ("YAML Indentation") already detects YAML structure issues.
A Google Home schema validator would extend this with trait-level type checking.

---

### Workflow 3 — Cognitive Pattern Recording for Automation Failures

| Attribute | Value |
|---|---|
| **Purpose** | Record which automation templates fail most often and why; build a CI-like pattern knowledge graph |
| **Phase** | Integration / Testing |
| **Inputs** | Automation execution logs, error codes, device trait failures |
| **Outputs** | Pattern DB entries (SQLite), `high_recurrence()` table, trend chart |
| **Dependencies** | `scripts/ci/pattern_recorder.py`, `_open_db()`, `cross_pr_correlation()` |
| **Repo Convention** | Phase 6-7 pattern recording pipeline; `CODEX_DB_PATH` env var |
| **Relevant Files** | `scripts/ci/pattern_recorder.py`, `CODEX_MANIFEST.json` (`ci_patterns` key) |

This workflow maps directly to the `_codex_` pattern knowledge graph.  Each
Google Home automation failure would be recorded as a pattern occurrence with a
`git_sha`-equivalent run ID, enabling `cross_pr_correlation()` to detect
automations that fail repeatedly across multiple home deployments.

---

### Workflow 4 — Template Validation and Production Gate

| Attribute | Value |
|---|---|
| **Purpose** | Gate automation deployment behind a strict validation check analogous to `ci_pattern_pipeline --strict` |
| **Phase** | Validation / Production gate |
| **Inputs** | Validated YAML templates, device availability checks |
| **Outputs** | Pass/Fail gate; annotated GitHub Actions step summary |
| **Dependencies** | `scripts/ci/ci_pattern_pipeline.py --strict`, `.github/workflows/pre-merge-validation.yml` |
| **Repo Convention** | S191: strict gate step in pre-merge-validation.yml |
| **Relevant Files** | `.github/workflows/pre-merge-validation.yml:41-58`, `scripts/ci/ci_pattern_pipeline.py` |

The strict gate pattern (`--check-only --strict`, exits 1 on any remaining
auto-fixable issue) directly models Google Home template validation: a template
is "production-ready" only when it passes device availability check + schema lint
+ action completeness check.

---

### Workflow 5 — Production Rollout with RAG-Assisted Context

| Attribute | Value |
|---|---|
| **Purpose** | Use RAG to surface relevant past automation patterns and known device limitations during authoring |
| **Phase** | Production rollout / Maintenance |
| **Inputs** | User intent (natural language), RAG index of validated templates, device KB |
| **Outputs** | Suggested automation YAML, confidence score, known-failure warnings |
| **Dependencies** | `src/codex/api/rag_api.py`, `_ensure_subpath()` path guard, `RAG_FILES_BASE_DIR` |
| **Repo Convention** | S187: RAG `/rag/build` path-traversal guard; `Optional[str]=None` provider field |
| **Relevant Files** | `src/codex/api/rag_api.py:32-38,242-244`, `.github/agents/ci-pattern-guardian.md` |

---

## 4. Top 5 Custom Agents to Design or Enhance

### Agent 1 — `google-home-script-agent` *(New)*

| Attribute | Value |
|---|---|
| **Role** | Author, validate, and deploy Google Home YAML automations |
| **Primary** | Generate syntactically-valid YAML from natural language intent; validate against Google Home schema |
| **Secondary** | Record failed automation patterns to `pattern_recorder.py`; surface `cross_pr_correlation()` warnings |
| **Capabilities** | YAML generation, schema validation, template library search, `check_docs_index.py` auto-index |
| **Repo Alignment** | Follows agent front-matter convention (`name`, `description`, `version`, `updated`, `cognitive_integration_level`) |
| **Type** | New agent |
| **File** | `.github/agents/google-home-script-agent.md` |

---

### Agent 2 — `energy-conversion-agent` *(Enhance)*

| Attribute | Value |
|---|---|
| **Role** | Extend existing G2E simulation to cover smart-home energy grid integration |
| **Primary** | Model smart-home loads (lights, HVAC, locks) as G2E consumption nodes |
| **Secondary** | Use Google Home Script Editor starters (e.g. `device.state.EnergyStorage`) to trigger PD optimization |
| **Capabilities** | Add `google_home_device_loads` module; parse Google Home energy-reporting traits |
| **Repo Alignment** | Existing agent at `.github/agents/energy-conversion-agent.md` (v1.2.0); enhance to v1.3.0 |
| **Type** | Enhancement of `.github/agents/energy-conversion-agent.md` |
| **Enhancement** | Add "Smart Home Energy Integration" section; map `device.command.OnOff` to load-shedding PD setpoints |

---

### Agent 3 — `smart-home-template-guardian` *(New)*

| Attribute | Value |
|---|---|
| **Role** | Enforce template quality gates for all Google Home YAML automations in the repository |
| **Primary** | Lint YAML structure, validate device trait names against schema, enforce `metadata.name` uniqueness |
| **Secondary** | Run pre-commit checks; record Pattern 3 (YAML Indentation) violations to pattern DB |
| **Capabilities** | `yamllint`, `jsonschema`, Pattern 3 auto-detection, `check_docs_index.py` integration |
| **Repo Alignment** | Follows `.pre-commit-config.yaml` hook pattern; uses `auto_fix_common_issues.py` Pattern 3 |
| **Type** | New agent |
| **File** | `.github/agents/smart-home-template-guardian.md` |

---

### Agent 4 — `cognitive-home-automation-agent` *(New)*

| Attribute | Value |
|---|---|
| **Role** | Map cognitive brain objectives to Google Home automation patterns |
| **Primary** | Query `pattern_recorder.high_recurrence()` to identify home automation patterns that should be automated |
| **Secondary** | Use `cross_pr_correlation()` to detect recurring home-state failures across multiple sessions |
| **Capabilities** | SQLite pattern DB queries, `dashboard_generator._generate_ci_pattern_trend_section()`, GitHub Issue creation |
| **Repo Alignment** | Phase 8 P1 cross-PR correlation; `CODEX_MANIFEST.json ci_patterns` key |
| **Type** | New agent |
| **File** | `.github/agents/cognitive-home-automation-agent.md` |

---

### Agent 5 — `rag-home-knowledge-agent` *(New)*

| Attribute | Value |
|---|---|
| **Role** | Manage a RAG index of validated Google Home YAML templates and device KB |
| **Primary** | Build and maintain `/rag/build` index of Google Home template library |
| **Secondary** | Serve template suggestions via `/rag/query`; apply path-traversal guard via `_ensure_subpath()` |
| **Capabilities** | RAG index management, `rag_api.py` integration, `RAG_FILES_BASE_DIR` sandboxing |
| **Repo Alignment** | `src/codex/api/rag_api.py:32-38,242-244` S187 path guard; `Optional[str]=None` provider field |
| **Type** | New agent |
| **File** | `.github/agents/rag-home-knowledge-agent.md` |

---

## 5. Top 5 Conceptual Usages and Integrations

### Integration 1 — Pattern DB as Automation Failure Historian

**Cognitive brain objective:** Self-healing CI → Self-healing automation
**Concept:** Each Google Home automation run = one CI job. Failures are
structured pattern occurrences.  `pattern_recorder.record_from_report()` ingests
structured failure logs, building a rolling 7-day trend and `high_recurrence()`
table.  `cross_pr_correlation()` flags automations that fail in ≥3 distinct home
deployments.

**Operational value:** Identifies fragile automations before they affect production.
**Repo reference:** `scripts/ci/pattern_recorder.py`, `CODEX_MANIFEST.json ci_patterns`

---

### Integration 2 — YAML Strict Gate for Template Deployments

**Cognitive brain objective:** Pre-merge gate → Pre-deploy gate
**Concept:** Adapt `ci_pattern_pipeline.py --strict` to act as a pre-deployment
gate for Google Home automations.  Any automation with detected schema errors
(Pattern 3: YAML Indentation) or unknown device traits (new Pattern 19) blocks
deployment.

**File format relevance:** Google Home YAML uses identical indentation and
block structure as GitHub Actions workflows — the same ruff/yamllint toolchain applies.

**Repo reference:** `.github/workflows/pre-merge-validation.yml:41-58`, `scripts/ci/ci_pattern_pipeline.py`

---

### Integration 3 — Deepresearch Index as Automation Template Library

**Cognitive brain objective:** Knowledge graph → Indexed template library
**Concept:** `docs/deepresearch/INDEX.md` and `check_docs_index.py --generate`
provide auto-indexing for any YAML template collection.  Google Home templates
committed under `docs/deepresearch/google_home_templates/` would be
auto-discovered and indexed.

**Operational value:** Enables RAG-based template retrieval and citation in
agent responses.

**Repo reference:** `docs/deepresearch/INDEX.md`, `scripts/ci/check_docs_index.py:88-149`

---

### Integration 4 — Energy Conversion Agent as Home Energy Optimizer

**Cognitive brain objective:** G2E optimization → Smart home load management
**Concept:** The `energy-conversion-agent` models gas-to-electric conversion
efficiency.  Google Home's `device.state.EnergyStorage` and
`device.command.OnOff` traits can be used as real-time load inputs.
The agent's PID controller setpoints become automation actions in YAML.

**File format relevance:** Agent output maps to `actions[].type: device.command.BrightnessAbsolute`
or `device.command.ThermostatTemperatureSetpoint` — enabling closed-loop
energy optimization via Google Home.

**Repo reference:** `.github/agents/energy-conversion-agent.md`, `ARCHITECTURE.md`

---

### Integration 5 — RAG-Powered Automation Authoring Assistant

**Cognitive brain objective:** RAG knowledge retrieval → Context-aware YAML generation
**Concept:** The `/rag/build` + `/rag/query` endpoints serve as the backbone for
an authoring assistant that retrieves the closest matching validated template,
applies it to the user's device list, and returns a deployable YAML.

**Security note:** The `_ensure_subpath()` guard (S187) must be applied to all
template file paths to prevent path traversal when loading templates from disk.

**Operational value:** Reduces authoring time; surfaces known-good templates and
known-limitation warnings in one query.

**Repo reference:** `src/codex/api/rag_api.py:32-38,242-244`, `.github/agents/rag-home-knowledge-agent.md`

---

## 6. Relevant Repo Files and Docs

| File | Role in this Domain |
|---|---|
| `docs/deepresearch/INDEX.md` | Template library index — auto-generated by `check_docs_index.py` |
| `docs/deepresearch/manifest_validation.md` | Shows the existing deepresearch convention (manifest + OpenAPI) |
| `.github/agents/energy-conversion-agent.md` | Energy domain agent — extends to smart-home energy integration |
| `.github/agents/ci-pattern-guardian.md` | Pattern pipeline agent — maps to automation failure detection |
| `scripts/ci/pattern_recorder.py` | Core pattern DB — adapts to automation failure recording |
| `scripts/ci/ci_pattern_pipeline.py` | Strict validation gate — adapts to automation deployment gate |
| `scripts/ci/auto_fix_common_issues.py` | Pattern 3 (YAML Indentation) directly applies to Google Home YAML |
| `src/codex/api/rag_api.py` | RAG API with path guard — template retrieval backend |
| `CODEX_MANIFEST.json` (`ci_patterns` key) | Knowledge graph export — include Google Home patterns here |
| `.pre-commit-config.yaml` | YAML lint and validation hooks — apply same config to template dirs |
| `.github/workflows/pre-merge-validation.yml` | Strict gate workflow — adapt for template deployment gate |

---

## 7. Constraints, Limitations, and Workarounds

| Constraint | Impact | Workaround |
|---|---|---|
| Google Home YAML requires `metadata.name` to be unique per home | Template library cannot have duplicate names | Add a name-uniqueness validator to Pattern 3 extension |
| Some device traits not yet supported (thermostat, full camera, advanced lighting) | Templates using unsupported traits will fail silently | Maintain a `known_unsupported_traits.yaml` allowlist; add to pre-deploy gate |
| iOS users must use Google Home for web for scripted automations | Limits mobile-first deployment workflows | Provide a web-based YAML editor backed by the RAG authoring agent |
| No native import/export of YAML from Google Home UI | Manual copy-paste required for template reuse | Commit templates to `docs/deepresearch/google_home_templates/`; use RAG agent for retrieval |
| `_ensure_subpath()` requires explicit `RAG_FILES_BASE_DIR` | Default CWD may not cover template library locations | Set `RAG_FILES_BASE_DIR=docs/deepresearch/google_home_templates` in CI environment |
| Pattern DB (SQLite) lives only on the runner — lost between CI jobs | Cross-run pattern correlation requires persistence | Phase 8 P2: snapshot DB to workflow artifact (GitHub Actions `upload-artifact`) |
| Gemini AI cognitive routines are in staged rollout | Not universally available | Design agents to degrade gracefully; fall back to static YAML templates |
| ⚠ **Gap:** No existing Google Home schema validator in `_codex_` | Templates cannot be programmatically validated today | P1: add `docs/deepresearch/google_home_schema.json` + integrate into Pattern 3 extension |

---

## 8. Recommended Next Actions

| Priority | Action | Owner | Repo File(s) |
|---|---|---|---|
| P1 | Add `docs/deepresearch/google_home_templates/` directory with 5 starter templates | CI agent | `docs/deepresearch/INDEX.md` |
| P1 | Create `.github/agents/google-home-script-agent.md` (see §4 Agent 1) | Agent designer | `.github/agents/` |
| P1 | Extend Pattern 3 with Google Home device-trait validation (new Pattern 19) | `auto_fix_common_issues.py` | `scripts/ci/auto_fix_common_issues.py` |
| P2 | Enhance `energy-conversion-agent.md` v1.2 → v1.3: add smart-home energy integration section | Agent designer | `.github/agents/energy-conversion-agent.md` |
| P2 | Add `google_home_schema.json` to deepresearch as schema reference | Research agent | `docs/deepresearch/` |
| P2 | Snapshot pattern SQLite DB to GitHub Actions artifact (Phase 8 P2) | CI engineer | `.github/workflows/pre-merge-validation.yml` |
| P3 | Create `cognitive-home-automation-agent.md` leveraging `cross_pr_correlation()` | Agent designer | `.github/agents/` |
| P3 | Integrate `cross_pr_correlation()` results into `iterative-self-healing-ci.yml` escalation comment | CI engineer | `.github/workflows/iterative-self-healing-ci.yml` |

---

## Sources

- Google Home Developer docs: `developers.home.google.com/automations/schema` — YAML automation schema reference
- Google Support: `support.google.com/googlenest/answer/13460475` — Script Editor guide
- Google Support: `support.google.com/googlenest/answer/13323253` — Advanced home automations
- Community template collection: `github.com/Ryan-Adams57/Google-Home-YAML-Automation-Collection`
- 9to5Google (2025-09-11): New automation editor rollout
- Android Police: Expanded condition/capabilities report
- Gadget Hacks: Script Editor production analysis

---

*Generated by Copilot Coding Agent S192 | Session-linked to PR #3741 | Phase 8 deepresearch deliverable*
