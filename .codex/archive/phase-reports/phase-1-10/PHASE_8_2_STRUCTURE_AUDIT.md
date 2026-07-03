# 📊 PHASE 8.2 — REPOSITORY STRUCTURE AUDIT

**Workstream:** 8.2.1 — Repository Structure Audit
**Track:** 8.2 (Repository Cleanup & Organization) — Phase 8 Multi-Agent Deployment Campaign
**Track Lead:** repository-organization-agent
**Authority:** @mbaetiong (D-tier autonomy) — GO CONTINUE on all gates
**Branch:** `copilot/deploy-phase-8-agents`
**Report Type:** Audit only (no files deleted, moved, or modified)
**Generated:** 2026-07-03T01:36Z
**Feeds:** Workstream 8.2.2 (Cleanup Strategy & Planning)

---

## 1. EXECUTIVE SUMMARY

This audit performs a complete structural inventory of the `Aries-Serpent/_codex_` repository. The repository is **large and structurally bloated**, with **17,100 files on disk** (17,081 git-tracked) across **1,804 directories** and **107 top-level directories**.

### Headline Findings

| Signal | Value | Assessment |
|--------|-------|------------|
| Total files on disk (excl. `.git`) | 17,100 | 🔴 Very large |
| Git-tracked files | 17,081 | 🔴 Very large |
| Top-level directories | 107 | 🔴 Excessive — poor navigability |
| Top-level loose files | 205 | 🔴 Root clutter |
| `.codex/` total files | 4,362 | 🔴 Dominant bloat source (25% of repo) |
| `.codex/` root-level `PHASE_*.md` reports | 866 | 🔴 Severe report proliferation |
| `.codex/` `.md` files (recursive) | 3,802 | 🔴 Report sprawl |
| Committed virtual environments | 713 files (`venv_test`=511, `.venv_ci`=202) | 🔴 Should never be tracked |
| Root-level `.md` files | 82 | 🟠 Root report clutter |
| Root-level `.txt` files | 32 | 🟠 Root report/log clutter |
| Backup/orig files (`.bak`/`.orig`/`.pr5000`/`.backup-*`) | 7 | 🟡 Low-risk quick wins |
| `__pycache__` dirs / `.pyc` files (excl. venvs) | 11 / 32 | 🟡 Build artifacts, should be gitignored |
| Duplicate/legacy directory clusters | 7+ clusters | 🟠 Confusing, consolidation needed |

### Top 3 Bloat Drivers
1. **`.codex/` report proliferation** — 4,362 files, of which **866 are `PHASE_*.md` reports at the top level of `.codex/`** and 3,802 markdown files recursively. This single directory is the largest and highest-value cleanup target.
2. **Committed virtual environments** — `venv_test/` (511 files) and `.venv_ci/` (202 files) are fully git-tracked, including binaries (`ruff` at 27 MB-scale KB blocks, `py-spy`). These should be `.gitignore`d and removed from tracking.
3. **Root-directory clutter** — 205 loose files at repo root including 82 `.md` and 32 `.txt` status/phase/remediation reports that belong in `.codex/` or an archive.

### Overall Risk Posture
Cleanup is **high-value and largely low-risk**, because the bulk of the bloat is generated reports, historical phase artifacts, backups, and committed environments — none of which are source-of-truth code. The primary risk is accidental removal of a report referenced by tooling or another workstream; mitigated by archival-not-deletion and dependency checks in Workstream 8.2.2.

---

## 2. TOP-LEVEL DIRECTORY MAP & PURPOSES

The repository has **107 top-level directories**. Below is the file-count-ranked map with inferred purposes. (Counts exclude `.git`.)

### 2.1 Major / Active Directories

| Dir | Files | Inferred Purpose |
|-----|------:|------------------|
| `.codex/` | 4,362 | Agent operational store: phase reports, plans, sessions, cognitive_brain, accountability, action logs. **Primary bloat source.** |
| `tests/` | 3,125 | Test suite (pytest). Core, keep. |
| `.github/` | 2,236 | GitHub config: workflows, actions, agent definitions, templates. **Out of scope for modification this campaign.** |
| `docs/` | 1,912 | Project documentation (mkdocs). Core (content owned by Track 8.1). |
| `src/` | 1,479 | Primary source code (`src/codex/...`, src-layout). Core, keep. |
| `scripts/` | 973 | Automation, CI, maintenance, and remediation scripts. Core but likely contains dead scripts. |
| `tools/` | 334 | Developer/CI tooling utilities. Keep; review for overlap with `scripts/`. |
| `cognitive_app/` | 208 | Cognitive Brain application (frontend/backend, incl. `.tsx`). Keep. |
| `configs/` | 203 | Hydra/project configuration. Core config root. |
| `reports/` | 133 | Generated analysis/audit reports. Review for archival. |
| `misc/` | 121 | Catch-all incl. `repo-owner-review/` offload store. Review. |
| `docs-data/` | 108 | Generated docs index (`docs.sqlite`, `*.jsonl`). Build artifact — should be gitignored. |
| `archive/` | 108 | Existing archival area. Consolidation target/destination. |
| `workbench/` | 107 | Scratch/experimental working area. High dead-code likelihood. |
| `services/` | 62 | Service modules. Review. |
| `agents/` | 58 | Agent definitions/specs. Keep, cross-ref `.github` agents. |
| `examples/` | 53 | Usage examples. Keep. |

### 2.2 Committed Environments (should NOT be tracked)

| Dir | Files | Purpose / Issue |
|-----|------:|-----------------|
| `venv_test/` | 507 (511 tracked) | 🔴 Committed Python virtualenv. Remove from tracking, gitignore. |
| `.venv_ci/` | 198 (202 tracked) | 🔴 Committed CI virtualenv incl. binaries (`ruff`, `py-spy`). Remove from tracking, gitignore. |
| `.mlruns/` | 2 | MLflow run store. Should be gitignored. |

### 2.3 Config Directory Sprawl (7 overlapping config roots)

`config/` (3), `config_legacy/` (3), `config_experiments/` (3), `configs/` (203), `conf/` (41), `.config/` (13), `.config.legacy/` (2)

- **Issue:** Seven distinct configuration roots with overlapping intent. `configs/` and `conf/` appear active; `config_legacy/`, `config_experiments/`, `.config.legacy/` are candidates for consolidation/archival.

### 2.4 Duplicate / Look-alike Directory Clusters

| Cluster | Members | Issue |
|---------|---------|-------|
| Codex stores | `.codex/` (4,362), `.CODEX/` (1 — `AGENT_MEMORY.DB`), `XX.codex/` (1 — `agent_memory.dbXX`) | 🔴 `.CODEX/` and `XX.codex/` look like stray/renamed leftovers. |
| Docs | `docs/` (1,912), `.docs/` (1 — only `.gitkeep`), `docs-data/` (108) | 🟠 `.docs/` is an empty placeholder. |
| Prompts | `prompts/` (17), `PROMPTS/` (2) | 🟠 Case-variant duplication. |
| Scripts | `scripts/` (973), `.scripts/` (1) | 🟠 `.scripts/` near-empty. |
| Reports | `reports/` (133), `.reports/` (6) | 🟠 Split report locations. |
| Legacy | `yaml_legacy/` (1 — `__init__.py`), `config_legacy/` (3), `.config.legacy/` (2) | 🟠 Legacy shims — verify no live imports before removal. |

### 2.5 Smaller Directories (specialized, mostly keep)

`conf/`(41), `manifests/`(33), `artifacts/`(33), `patches/`(26), `audio_cleaner_v1/`(21), `data/`(19), `security-suite-artifacts/`(18), `prompts/`(17), `db/`(16), `cli/`(16), `schemas/`(15), `apps/`(15), `docker/`(14), `training/`(13), `.config/`(13), `infrastructure/`(12), `codex_digest/`(12), `benchmarks/`(12), `analysis/`(12), `monitoring/`(11), `coverage_tests/`(11), `codex_utils/`(11), `templates/`(10), plus ~60 directories with ≤10 files each (e.g. `codex_ml`, `codex_addons`, `codex_regression`, `rust_swarm`, `deploy`, `copilot`, `tokenization`, `memory`, `mappings`, `k8s`, `guides`, `cognitive`).

### 2.6 Near-empty / Orphan-suspect single-file directories

`assets/`, `actions/`, `ops/`, `omegaconf/`, `experiments/`, `detectors/`, `benches/`, `implementation_completed/`, `sentencepiece/`, `semgrep/`, `transformers/`, `yaml_legacy/`, `.build/`, `.codeql/`, `.docs/`, `.scripts/`, `.CODEX/`, `XX.codex/`, `.vscode/` — each contains exactly 1 file. These warrant purpose verification in 8.2.2 (some are legit shims like `omegaconf`/`transformers` stubs; others are stray).

---

## 3. DEAD / TEMPORARY / DEBUG FILE INVENTORY

Scans exclude `.git/`, `.venv_ci/`, and `venv_test/` unless noted.

### 3.1 Backup / superseded files (7 — quick-win candidates)

| File | Type |
|------|------|
| `src/codex/github/mcp_poster.py.bak` | Source backup (⚠️ inside `src/`) |
| `.mutmut.ini.bak` | Config backup |
| `CHANGELOG.md.pr5000` | PR-suffixed leftover |
| `CODEX_MANIFEST.json.pr5000` | PR-suffixed leftover |
| `pyproject.toml.backup-day2` | Dated config backup |
| `tests/smoke/conftest.py.orig` | Merge `.orig` leftover (⚠️ inside `tests/`) |
| `.codex/archive/OLD_ACCOUNTABILITY_REPORT_66K.md.bak` | Already in archive |

### 3.2 Build artifacts (should be gitignored, not tracked)

| Pattern | Count | Notes |
|---------|------:|-------|
| `__pycache__/` dirs | 11 | Excl. venvs |
| `*.pyc` files | 32 | Excl. venvs |
| `*.py,cover` | 13 | Coverage annotation artifacts |
| `docs-data/` generated (`docs.sqlite`, `*.jsonl`) | ~108 | Regenerable index |

### 3.3 Temp / scratch patterns

| Pattern | Count |
|---------|------:|
| `*.tmp` | 0 |
| `*.debug` | 0 |
| `*.swp` / `*.swo` / `*~` | 0 |
| `*.rej` | 0 |
| `*.log` (excl. venvs) | 3 |

Root-level logs: `phase_9_2_coverage_run.log`, `phase_9_2_initial_test_run.log`, plus `gh_output.txt`, `mutmut_output.txt`, `mypy_output.txt`, `mypy_error_analysis.txt`, `coverage-report.txt`, `test_execution_log.txt`, `test_results.txt` — captured tool output that belongs in `.codex/` or should be removed.

### 3.4 Root-level scratch / session files

`sess_001`, `cost_estimate.json`, `decision_history.json` — session-scoped scratch artifacts sitting at repo root.

### 3.5 Disabled workflow/source files (15 `.disabled`)

15 `*.disabled` files, primarily under `.github/workflows/` and `.github/_workflows_disabled/` (e.g. `ci.yml.disabled`, `tests.yml.disabled`, `security.yml.disabled`).
> ⚠️ **Out of scope:** These are GitHub Actions workflow files. Per campaign constraints this workstream will **not** create or modify workflow files. Flagged for the workflow-owning track only.

### 3.6 Legacy shim modules (verify before touching)

`yaml_legacy/__init__.py`, `config_legacy/` (`errors.py`, `__init__.py`, `README.md`), `.config.legacy/` (`README.md`, `INVENTORY.txt`) — potential import shims; require import cross-reference in 8.2.2 before any removal.

---

## 4. DUPLICATE-CLUSTER REPORT

### 4.1 `.codex/` PHASE report proliferation (SEVERE)

**866** `PHASE_*.md` files reside at the **top level** of `.codex/` (before subdirectories). By phase family:

| Family | Count | Family | Count |
|--------|------:|--------|------:|
| PHASE_7A | 129 | PHASE_4 | 42 |
| PHASE_6 | 78 | PHASE_1 | 42 |
| PHASE_9 | 76 | PHASE_12 | 26 |
| PHASE_3 | 75 | PHASE_11 | 15 |
| PHASE_8 | 72 | PHASE_6A | 11 |
| PHASE_7D | 70 | PHASE_7C | 6 |
| PHASE_7B | 61 | PHASE_6B / PHASE_5A / PHASE_5B | 5 each |
| PHASE_10 | 48 | PHASE_5C / PHASE_5 | 4 each |

These are historical completion/summary/progress reports for prior phases. They form the single largest consolidation cluster and are strong archival candidates (phases 1–7 are complete).

### 4.2 `.codex/` subdirectory distribution

| Subdir | Files | Subdir | Files |
|--------|------:|--------|------:|
| `archive/` | 478 | `evidence/` | 36 |
| `cognitive_brain/` | 302 | `prompts/` | 34 |
| `reports/` | 262 | `accountability_chunks/` | 32 |
| `plans/` | 144 | `validation/` | 31 |
| `sessions/` | 91 | `qa_walkthrough/` | 29 |
| `docs/` | 91 | `templates/` | 21 |
| `status/` | 55 | `pending_ops/` | 21 |

`.codex/` totals **3,802 markdown files** recursively — indicating report content dominates this store.

### 4.3 Root-level report clusters

- **44** `PHASE_*` files at repo root (`.md`/`.txt`/`.json`), e.g. `PHASE_10_1_FINAL_REPORT.md`, `PHASE_3_TEAM_4_*` (6 variants), `PHASE_9_2_LANE_*`.
- **Security/Semgrep/Remediation cluster** at root: `SECURITY_FIXES_SUMMARY.txt`, `SECURITY_MONITORING_PLAN.md`, `SECURITY_REMEDIATION_GUIDE.md`, `SECURITY_REMEDIATION_PHASE1_REPORT.md`, `SEMGREP_M01_REMEDIATION_SUMMARY.md`, `SEMGREP_REMEDIATION_REPORT.md`, `SEMGREP_TRIAGE_REPORT.md`, `remediation_plan_sbom.md`, `remediation_plan_secrets.md`, `remediation_plan_semgrep.md`, `REMEDIATION_CHECKPOINT.txt`, `REMEDIATION_PHASE_3_FINAL_RESULTS.txt`.
- **Audit/Documentation cluster** at root: `AUDIT_COMPLETION_SUMMARY.txt`, `AUDIT_SUMMARY.txt`, `audit_summary.json`, `DOCUMENTATION_AUDIT_*` (5 variants), `DOCUMENTATION_UPDATE*` (4 variants), `TERMINOLOGY_*` (3 variants).

### 4.4 Duplicated `.pr5000` manifest pair

`CHANGELOG.md` + `CHANGELOG.md.pr5000` and `CODEX_MANIFEST.json` + `CODEX_MANIFEST.json.pr5000` — original vs PR-branch snapshot duplicates.

---

## 5. FILE-DISTRIBUTION STATISTICS

### 5.1 By file type (top types; excl. `.git`, `.venv_ci`, `venv_test`, `.mlruns`)

| Ext | Count | Ext | Count |
|-----|------:|-----|------:|
| `.md` | 7,411 | `.tsx` | 132 |
| `.py` | 6,179 | `.jsonl` | 122 |
| `.yml` | 589 | `.meta` | 82 |
| `.json` | 566 | `.mmd` | 54 |
| `.yaml` | 350 | `.gitkeep` | 36 |
| `.sh` | 216 | `.pyc` | 32 |
| `.txt` | 183 | `.ts` | 28 |

> **Key insight:** Markdown (7,411) **exceeds** Python (6,179). For a codebase, documentation/report files being the #1 file type by a wide margin confirms report proliferation is the dominant structural issue.

### 5.2 By directory (top file-count contributors)

`.codex/`=4,362 · `tests/`=3,125 · `.github/`=2,236 · `docs/`=1,912 · `src/`=1,479 · `scripts/`=973 · `venv_test/`=507 · `tools/`=334 · `cognitive_app/`=208 · `configs/`=203 · `.venv_ci/`=198.

These 11 directories account for the overwhelming majority of the 17,100 files.

### 5.3 Largest tracked files (KB)

| Size (KB) | File |
|----------:|------|
| 27,248 | `.venv_ci/bin/ruff` (committed binary) |
| 23,212 | `docs-data/generated/docs.sqlite` (generated) |
| 20,564 | `.codex/sbom/sbom_base-phase2-build.json` |
| 20,512 | `docs-data/relationships.jsonl` (generated) |
| 18,128 | `docs-data/blocks.jsonl` (generated) |
| 17,072 | `.codex/sbom/sbom_local-codex-env-phase2-build.json` |
| 10,540 | `.codex/sbom/sbom_ci-phase2-build.json` |
| 7,892 | `.venv_ci/bin/py-spy` (committed binary) |
| 4,148 | `.codex/archive/OLD_ACCOUNTABILITY_REPORT_66K.md.bak` |

> Committed binaries (`ruff`, `py-spy`) and regenerable generated data dominate the size profile — all removable from tracking without source loss.

---

## 6. RISK ASSESSMENT

| Cleanup Category | Volume | Removal Risk | Rationale |
|------------------|-------:|:------------:|-----------|
| Committed virtualenvs (`venv_test/`, `.venv_ci/`, `.mlruns/`) | 715 files | 🟢 Low | Regenerable; never belong in VCS. Only risk = local dev friction; mitigate via `.gitignore` + docs. |
| Backup/orig/`.pr5000` files | 7 | 🟢 Low | Superseded snapshots. `src/` and `tests/` ones need a 2-second diff check first. |
| Build artifacts (`__pycache__`, `.pyc`, `.py,cover`, `docs-data/generated/*`) | ~150+ | 🟢 Low | Fully regenerable. |
| Root loose reports (`.md`/`.txt`/`.log`) | ~114 | 🟡 Medium | Archive not delete; some may be linked from docs or issues. Verify references. |
| `.codex/` PHASE_*.md historical reports | 866 | 🟡 Medium | Move to `.codex/archive/`; confirm no tooling (dashboards, action logs, agents) reads specific paths. |
| Duplicate/legacy dirs (`.CODEX/`, `XX.codex/`, `.docs/`, `config_legacy/`, `yaml_legacy/`, etc.) | ~15 dirs | 🟠 Medium-High | Legacy shims may still be imported. **Requires import cross-reference before any action.** |
| `.disabled` workflow files | 15 | ⛔ Out of scope | Workflow files — not touched by this track. |
| `src/`, `tests/`, `docs/`, `configs/`, `scripts/` core code | ~7,600 | 🔴 High | Source-of-truth. Dead-code removal requires import/usage tracing (deferred to 8.2.2/8.2.3). |

**Session constraint honored:** No files were deleted, moved, or modified. No workflow files created/modified. Only this single report was produced.

---

## 7. PRIORITIZED CLEANUP RECOMMENDATIONS (→ Workstream 8.2.2)

### Priority 0 — Immediate quick wins (low risk, high impact)
1. **Untrack committed environments.** Remove `venv_test/` (511), `.venv_ci/` (202), `.mlruns/` (2) from git; add to `.gitignore`. Removes committed binaries (`ruff`, `py-spy`) and ~715 files.
2. **Remove backup/orig/`.pr5000` leftovers** (7 files) after diff verification of the `src/` and `tests/` ones.
3. **Gitignore + untrack build artifacts** — `__pycache__/`, `*.pyc` (32), `*.py,cover` (13), `docs-data/generated/*` (regenerable index incl. 23 MB `docs.sqlite`).

### Priority 1 — Report consolidation (highest volume driver)
4. **Archive completed-phase `.codex/PHASE_*.md` reports** (866 files). Move Phases 1–7 families (~600+ files: 7A=129, 6=78, 3=75, 7D=70, 7B=61, etc.) to `.codex/archive/phase-history/` with an index. Verify no tooling reads fixed paths first.
5. **Consolidate root-level reports** — relocate 82 root `.md` + 32 root `.txt` (PHASE_*, SECURITY_*, SEMGREP_*, REMEDIATION_*, AUDIT_*, DOCUMENTATION_*, TERMINOLOGY_* clusters) into `.codex/reports/` or archive, leaving only canonical root docs (README, LICENSE, SECURITY.md, CONTRIBUTING, CHANGELOG, etc.).
6. **Remove root scratch/log files** — `phase_9_2_*.log`, `gh_output.txt`, `mutmut_output.txt`, `mypy_output.txt`, `test_results.txt`, `sess_001`, `cost_estimate.json`, `decision_history.json`.

### Priority 2 — Directory consolidation (needs dependency checks)
7. **Resolve codex-store duplicates** — investigate `.CODEX/` (`AGENT_MEMORY.DB`) and `XX.codex/` (`agent_memory.dbXX`); consolidate into `.codex/` or remove stray leftovers.
8. **Consolidate config sprawl** — merge/retire `config_legacy/`, `config_experiments/`, `.config.legacy/`, `yaml_legacy/` after tracing live imports; document canonical config roots (`configs/`, `conf/`).
9. **Collapse case-variant / placeholder dirs** — `PROMPTS/`→`prompts/`, `.scripts/`→`scripts/`, `.reports/`→`reports/`, remove empty `.docs/`.
10. **Review single-file/orphan-suspect dirs** (~19) for purpose; retire true orphans.

### Priority 3 — Deeper analysis (defer to 8.2.2/8.2.3 with tooling)
11. **Dead-code trace** in `src/`, `scripts/`, `tools/`, `workbench/` via import-graph + git-last-modified analysis (out of scope for this audit-only session).
12. **Duplicate-implementation detection** across `scripts/` vs `tools/` and utility modules.

### Out of Scope (flag only)
- 15 `.disabled` workflow files under `.github/` — refer to the workflow-owning track; this campaign does not modify workflow files.
- `docs/` content quality — owned by Track 8.1.

---

## 8. SUCCESS CRITERIA STATUS (Workstream 8.2.1)

| Criterion | Status |
|-----------|:------:|
| 100% of top-level directories mapped (107/107) | ✅ |
| Dead/temp/debug files identified with counts + examples | ✅ |
| Duplicate clusters documented + quantified | ✅ |
| File-distribution statistics produced | ✅ |
| Risk assessment completed | ✅ |
| Prioritized recommendations feeding 8.2.2 | ✅ |
| Audit report generated in `.codex/` | ✅ (`.codex/PHASE_8_2_STRUCTURE_AUDIT.md`) |
| No files deleted/moved/modified; no workflow changes | ✅ Constraints honored |

---

*Report generated 2026-07-03T01:36Z by repository-organization-agent (Track 8.2 lead) under D-tier autonomy. Audit-only session — one deliverable produced, no repository mutations. Handoff → Workstream 8.2.2 (Cleanup Strategy & Planning).*
