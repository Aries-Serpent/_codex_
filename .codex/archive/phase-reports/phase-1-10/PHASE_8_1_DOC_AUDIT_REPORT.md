# 📄 PHASE 8.1 — DOCUMENTATION AUDIT REPORT (Workstream 8.1.1)

**Track:** 8.1 — Documentation Remediation
**Track Lead:** unified-doc-agent (Track 8.1 lead session)
**Authority:** @mbaetiong (D-tier autonomy, GO CONTINUE on all gates)
**Branch:** `copilot/deploy-phase-8-agents`
**Repository:** Aries-Serpent/_codex_
**Generated:** 2026-07-03T01:36Z
**Workstream:** 8.1.1 Documentation Audit Phase (Weeks 1-2)
**Feeds Into:** Workstream 8.1.2 Remediation Planning

---

## 1. EXECUTIVE SUMMARY

This report delivers a repository-wide audit of documentation for the Aries-Serpent/_codex_
codebase. Scanning was performed with `find`, `grep`, `git`, and a sampled Python link
validator. **All statistics below are grounded in live scans of the working tree**; no
placeholders are used.

### Headline Findings

| Signal | Value | Assessment |
|--------|-------|-----------|
| Total Markdown files (`.md`) | **7,411** | Very large surface; unmanageable without automation |
| Total plain-text docs (`.txt`) | **194** | Legacy/report artifacts |
| reStructuredText (`.rst`) | **0** | Not used |
| Docs with pre-2026-04-03 embedded dates (stale proxy) | **3,463 (~47%)** | 🔴 High stale-content risk |
| `PHASE_*/WAVE_*/GATE_*` prefixed reports | **1,547** | 🔴 Severe report sprawl / duplication |
| Sampled broken relative-link rate | **~8–10%** | 🟠 Meaningful link rot (with FP caveat) |
| Duplicate `README.md` basenames | **224** | 🟠 Navigation fragmentation |
| Root-directory doc clutter (`.md`+`.txt`) | **120 files** | 🟠 Poor top-level organization |

### Top-Line Conclusions

1. **Volume is the primary risk.** With 7,411 Markdown files, the biggest problem is not
   individual broken docs but the sheer sprawl of point-in-time status reports
   (`PHASE_*`, `WAVE_*`, `GATE_*`, `*_COMPLETION_*`, `*_SUMMARY_*`, `*_FINAL_*`). These
   dominate the corpus and are inherently stale the moment they are written.
2. **Git-history staleness detection is not viable in this checkout.** The repository has
   only **3 commits, all dated 2026-07-03**, and all filesystem mtimes are the checkout
   time. Commit-date staleness cannot distinguish real document age (see §3). A
   **content-embedded-date proxy** was used instead.
3. **Link rot is real but modest**, estimated at ~8–10% of relative links in sampled docs,
   concentrated in archived and report directories. Automated counts include some false
   positives from code-fence content (see §4).
4. **Consolidation is the highest-leverage remediation** — the report families and duplicate
   READMEs/INDEXes should be the primary target of Workstream 8.1.4.

---

## 2. DOCUMENTATION INVENTORY STATISTICS

### 2.1 Corpus Totals

| File type | Count | Method |
|-----------|-------|--------|
| `*.md` (excl. `.git`, `node_modules`) | 7,411 | `find … -name '*.md'` |
| `*.txt` | 194 | `find … -name '*.txt'` |
| `*.rst` | 0 | `find … -name '*.rst'` |

### 2.2 Markdown Distribution by Top-Level Directory

| Directory | `.md` files | % of corpus | Notes |
|-----------|------------:|------------:|-------|
| `.codex/` | 3,801 | 51.3% | Agent reports, plans, sessions, cognitive_brain |
| `docs/` | 1,800 | 24.3% | The canonical documentation tree (MkDocs) |
| `.github/` | 1,188 | 16.0% | Agent specs, copilot-prompts, workflow docs |
| `reports/` | 128 | 1.7% | Generated audit/report output |
| `archive/` | 91 | 1.2% | Superseded content |
| `<repo root>` | 83 | 1.1% | Top-level clutter (see §5.3) |
| `workbench/` | 77 | 1.0% | Scratch/working docs |
| `misc/` | 56 | 0.8% | Uncategorized |
| `scripts/` | 21 | 0.3% | Script-adjacent docs |
| `cognitive_app/`, `agents/` | 20 each | 0.5% | App + agent docs |
| `src/` | 17 | 0.2% | In-tree module docs |
| Others (prompts, tests, tools, apps, guides, …) | ~110 | ~1.5% | Long tail |

**Observation:** Two-thirds of all documentation lives in `.codex/` (51%) and `docs/` (24%).
`.codex/` is dominated by machine/agent-generated reports rather than user-facing docs.

### 2.3 `.codex/` Sub-breakdown (3,801 files)

| Subdir | Files | Subdir | Files |
|--------|------:|--------|------:|
| `<.codex root>` | 2,351 | `sessions/` | 36 |
| `archive/` | 428 | `prompts/` | 33 |
| `cognitive_brain/` | 291 | `accountability_chunks/` | 32 |
| `reports/` | 236 | `status/` | 21 |
| `plans/` | 137 | `qa_walkthrough/` | 14 |
| `docs/` | 91 | `release/` | 11 |

The **2,351 files at the `.codex/` root** are the single biggest unstructured pile in the repo.

### 2.4 `docs/` Sub-breakdown (1,800 files)

| Subdir | Files | Subdir | Files |
|--------|------:|--------|------:|
| `<docs root>` | 289 | `security/` | 49 |
| `archive/` | 108 | `status_updates/` | 43 |
| `plans/` | 94 | `accountability/` | 36 |
| `ops/` | 73 | `testing/` | 32 |
| `guides/` | 72 | `capabilities/` | 31 |
| `validation/` | 69 | `admin/` | 30 |
| `templates/` | 61 | `reference/` | 29 |
| `cognitive_brain/` | 53 | `arch/` | 29 |

### 2.5 `.github/` Sub-breakdown (1,188 files)

| Subdir | Files | Notes |
|--------|------:|-------|
| `copilot-prompts/` | 391 | Prompt library |
| `agents/` | 331 | Custom agent specifications |
| `workflows/` | 106 | Workflow-adjacent `.md` (docs, not YAML) |
| `<.github root>` | 96 | |
| `prompts/` | 76 | |
| `docs/` | 64 | |
| `workflow-archive/` | 42 | Superseded |

### 2.6 Categorization by Document Type

| Category | Count | Detection |
|----------|------:|-----------|
| README files | 226 | `-iname readme.md` |
| INDEX files | 126 | duplicate-basename scan |
| Agent-named docs (`*AGENT*.md`) | 334 | filename match |
| Point-in-time status reports (`PHASE_*/WAVE_*/GATE_*`) | 1,547 | filename prefix |
| `*REPORT*` docs | 656 | filename match |
| `*SUMMARY*` docs | 585 | filename match |
| `*FINAL*` docs | 302 | filename match |
| `*COMPLETE*` docs | 302 | filename match |
| `*COMPLETION*` docs | 287 | filename match |
| `*VALIDATION*` docs | 169 | filename match |
| `*AUDIT*` docs | 119 | filename match |
| `*REMEDIATION*` docs | 103 | filename match |
| Stub docs (< 200 bytes) | 41 | `find -size -200c` |
| Docs mentioning "deprecat*" | 725 | `grep -li deprecat` |

> Category counts overlap (a file may be both `PHASE_*` and `*REPORT*`); they characterize
> the corpus rather than partition it.

### 2.7 Site Configuration

- `mkdocs.yml` present (8,265 bytes) — MkDocs site build configured.
- `docs/index.md` present — site landing page exists.

---

## 3. STALE-CONTENT INVENTORY

### 3.1 Methodological Constraint (Critical)

The task requested `git log`-based staleness (docs not modified since ~2026-04-03).
**This is not achievable in the current checkout:**

- `git log --oneline | wc -l` → **3 commits total**, all dated **2026-07-03**.
- All Markdown filesystem mtimes fall in **2026-07** (checkout time): 7,412/7,412 files.

The git history is compressed/squashed at import, so commit timestamps and file mtimes are
**uniform and cannot serve as an age signal.** This is itself a **finding**: the repository
lacks the git provenance needed for automated freshness gating — a dependency for
Workstream 8.1.5 automation.

### 3.2 Proxy Method: Content-Embedded Dates

As a substitute, docs were scanned for ISO dates embedded *in their content* that predate
the 90-day threshold (2026-04-03): pattern `(2024|2025)-MM-DD` and `2026-0[1-3]-DD`.

- **3,463 Markdown files (~47% of the corpus) contain at least one embedded date older than
  90 days**, strongly suggesting the documented events/state are stale.

### 3.3 Stale-Proxy Distribution by Directory

| Directory | Stale-proxy docs | Directory total | Stale share |
|-----------|-----------------:|----------------:|------------:|
| `.codex/` | 1,465 | 3,801 | 38.5% |
| `docs/` | 840 | 1,800 | 46.7% |
| `.github/` | 791 | 1,188 | 66.6% |
| `reports/` | 115 | 128 | 89.8% |
| `archive/` | 76 | 91 | 83.5% |
| `workbench/` | 45 | 77 | 58.4% |
| `misc/` | 44 | 56 | 78.6% |
| `<repo root>` | 20 | 83 | 24.1% |

### 3.4 Most-Referenced Stale Date Tokens

| Date token | Occurrences | Interpretation | <!-- pragma: allowlist secret -->
|-----------|------------:|----------------|
| 2026-01-23 | 4,860 | Dominant historical "as-of" date across reports |
| 2026-02-17 | 320 | |
| 2026-02-04 | 268 | |
| 2026-02-10 | 240 | |
| 2025-09-17 | 208 | Oldest high-frequency token | <!-- pragma: allowlist secret -->
| 2025-12-29 | 169 | |

**Interpretation:** `reports/` (89.8%) and `archive/` (83.5%) are almost entirely stale by
design (they are historical). The concerning stale populations are in `docs/` (840 files,
46.7%) and `.github/` (791 files, 66.6%), where users expect current content.

---

## 4. LINK-VALIDATION FINDINGS (Sample-Based)

### 4.1 Method

A Python validator extracted Markdown links `[text](target)`, filtered to **relative**
links (excluding `http(s)://`, `mailto:`, `tel:`, `#anchors`, `data:`), and checked target
existence relative to both the file's directory and the repo root. Two independent random
samples were run.

| Sample | Files sampled | Total links | Relative links | Broken | Files w/ ≥1 broken | Broken rate (relative) |
|--------|--------------:|------------:|---------------:|-------:|-------------------:|-----------------------:|
| Seed 42 | 800 | 1,530 | 543 | 44 | 18 | 8.1% |
| Seed 7 | 1,000 | 2,201 | 742 | 77 | 29 | 10.4% |
| **Combined** | **1,800** | **3,731** | **1,285** | **121** | **47** | **~9.4%** |

### 4.2 Coverage Caveat

The `os.walk` traversal enumerated **6,225** files and **excluded `.github/`** (1,188 files;
its path matches the `.git` filter). The link sample therefore covers the `.codex/`, `docs/`,
`reports/`, `archive/`, root, and other trees but **not `.github/` agent/prompt docs**. A
follow-up pass covering `.github/` is recommended in 8.1.3.

### 4.3 False-Positive Note

Automated extraction captured some non-links from inside code fences (e.g. regex fragments
`[^"\']+`, `state["inputs"]`, `blob:https://…`). These inflate raw broken counts; the
true broken rate after code-fence filtering is likely **somewhat below 9%**. Manual review
is required before treating individual hits as defects (mitigates Brief Risk 1).

### 4.4 Representative Broken Links (real defects)

| Source doc | Broken target |
|-----------|----------------|
| `.codex/DATA_AGGREGATION_INTEGRATION_GUIDE.md` | `./workflow_pattern_library.py`, `./rapid_delegation_engine.py`, `./collect_telemetry.py` |
| `.codex/archive/phases/PHASE_5_LANE_5.5A_CACHE_REPORT.md` | `./CACHE_ARCHITECTURE.md`, `../src/codex/ci/cache_manager.py`, `../src/cache/redis_cache.py` |
| `.codex/cognitive_brain/PRODUCTION_RAG_COGNITIVE_BRAIN_STATUS.md` | `../docs/RAG_QUICKSTART.md`, `../docs/RAG_ENHANCEMENT_PLANSETS.md` |
| `TERMINOLOGY_CONSISTENCY_AUDIT_REPORT.md` | `../TERMINOLOGY_GLOSSARY.md` (missing glossary) |
| `TERMINOLOGY_CONSISTENCY_IMPLEMENTATION_CHECKLIST.md` | `../TERMINOLOGY_GLOSSARY.md`, `../docs/TERMINOLOGY_GLOSSARY.md` |
| `.codex/SUCCESS_CRITERIA_BY_ENVIRONMENT.md` | `./verification-checklists/VERIFICATION_CHECKLIST_{DEV,STAGING,PRODUCTION}.md` |
| `.codex/PHASE_9_2_AUTOFIX_PATTERNS.md` | `/docs/old-api-reference.md`, `/docs/api-reference.md` |
| `docs/plans/README.md` | `./plans/PLAN_TITLE.md`, `./plans/archive/PLAN_TITLE.md` |
| `.codex/README_DISCUSSION_4872_MASTER_INDEX.md` | `SESSION_ANALYSIS_SUMMARY_20260619.md` |
| `archive/phases/PHASE_4_ITERATION_IMPROVEMENT_SUMMARY.md` | `coverage_validation_report.md`, `htmlcov/phase4_complete/index.html` |

**Patterns observed:** (a) links to source `.py` files that moved/were removed;
(b) references to a `TERMINOLOGY_GLOSSARY.md` that does not exist; (c) template
placeholders (`PLAN_TITLE.md`, `{output_file}`) committed as literal links; (d) references
into deleted `htmlcov/`/coverage artifacts.

---

## 5. DUPLICATION & CONSISTENCY FINDINGS

### 5.1 Duplicate Basenames (same filename, many locations)

| Basename | Occurrences |
|----------|------------:|
| `README.md` | 224 |
| `INDEX.md` | 126 |
| `CHANGELOG.md` | 15 |
| `main.md` | 12 |
| `examples.md` | 10 |
| `advanced.md` | 8 |
| `.codex/archive/deprecated/AGENTS.md` | 8 |
| `IMPLEMENTATION_SUMMARY.md` | 5 |
| `ARCHITECTURE.md` / `architecture.md` | 5 / 5 |
| `CONTRIBUTING.md` | 5 |
| `_PHASE_OVERVIEW.md` | 4 |

224 READMEs and 126 INDEXes indicate a deeply nested tree where each folder re-documents
itself — a navigation and single-source-of-truth hazard. Note also **casing collisions**
(`ARCHITECTURE.md` vs `architecture.md`) that break on case-insensitive filesystems.

### 5.2 Point-in-Time Report Family Sprawl

Report families by prefix (filename count):

| Family | Files | Family | Files |
|--------|------:|--------|------:|
| `PHASE_7_*` | 291 | `PHASE_2_*` | 69 |
| `PHASE_9_*` | 149 | `PHASE_10_*` | 63 |
| `PHASE_5_*` | 127 | `PHASE_1_*` | 53 |
| `PHASE_6_*` | 114 | `PHASE_4_*` | 50 |
| `PHASE_3_*` | 103 | `SECURITY_*` | 49 |
| `PHASE_8_*` | 95 | `GATE_2_*` | 32 |
| `WAVE_2_*` | 91 | `PHASE_12_*` | 30 |
| `PHASE_11_*` | 32 | `DOCUMENTATION_*` | 24 |

**1,547** files carry a `PHASE_/WAVE_/GATE_` prefix. Cross-cutting report keywords:
`*REPORT*` 656, `*SUMMARY*` 585, `*FINAL*` 302, `*COMPLETE*` 302, `*COMPLETION*` 287.
This is the dominant consolidation target for Workstream 8.1.4.

### 5.3 Root-Directory Clutter

The repository root holds **120 top-level `.md`/`.txt` files** (83 `.md`), including many
one-off reports (`PHASE_*`, `SECURITY_*`, `SEMGREP_*`, `TERMINOLOGY_*`, `AUDIT_*`,
`REMEDIATION_*`). These should be relocated to `.codex/archive/` or `reports/`, leaving only
canonical entrypoints (`README.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CHANGELOG.md`,
`CODE_OF_CONDUCT.md`, `.codex/archive/deprecated/AGENTS.md`) at root.

### 5.4 Consistency Issues

- **Missing referenced glossary:** multiple docs link to `TERMINOLOGY_GLOSSARY.md` which does
  not exist — a terminology-consistency gap for the terminology-consistency-agent.
- **Template placeholders committed as content:** `PLAN_TITLE.md`, `{output_file}` appear as
  live links, indicating templates were copied without instantiation.
- **Casing collisions** (see §5.1) across duplicate architecture docs.
- **Stub docs (41 files < 200 bytes):** likely empty placeholders or orphaned index shells.

---

## 6. SEVERITY CLASSIFICATION

| Severity | Finding | Evidence | Impact |
|----------|---------|----------|--------|
| 🔴 **Critical** | No usable git provenance for freshness gating | 3 commits, uniform mtimes | Blocks 8.1.5 automation; needs alternate freshness signal |
| 🔴 **Critical** | Broken relative links to moved/removed code & missing files | ~9.4% of sampled relative links; concrete examples §4.4 | User-facing correctness; API/code drift |
| 🟠 **High** | Massive report sprawl (1,547 PHASE/WAVE/GATE + 656 REPORT etc.) | §2.6, §5.2 | Discoverability collapse; consolidation debt |
| 🟠 **High** | Stale content proxy ~47% of corpus; `docs/` 46.7%, `.github/` 66.6% | §3.3 | Users read outdated guidance |
| 🟠 **High** | 224 README + 126 INDEX duplicate basenames; casing collisions | §5.1 | No single source of truth; case-fs breakage |
| 🟡 **Medium** | Missing `TERMINOLOGY_GLOSSARY.md` referenced by multiple docs | §4.4, §5.4 | Terminology inconsistency |
| 🟡 **Medium** | 120 root-level doc files (clutter) | §5.3 | Poor first-impression navigation |
| 🟡 **Medium** | Template placeholders committed as live links | §5.4 | Broken links, unprofessional |
| 🟢 **Low** | 41 stub docs (< 200 bytes) | §2.6 | Minor cleanup |
| 🟢 **Low** | 194 legacy `.txt` reports | §2.1 | Archive/convert |

---

## 7. PRIORITIZED RECOMMENDATIONS (feeding Workstream 8.1.2)

### P0 — Enablers (do first; unblock automation)
1. **Establish a freshness signal that does not depend on squashed git history.** Options:
   adopt front-matter `last_reviewed:` metadata, or a manifest tracking real review dates.
   Without this, the Brief's "<5% stale" and CI freshness gate (8.1.5) are unmeasurable.
2. **Scope the audit target set.** Treat `reports/`, `archive/`, `.codex/archive/`, and
   `.codex/` root reports as **historical/immutable** and exclude them from freshness/link
   SLAs. Focus remediation on the **user-facing set**: `README.md`, `docs/` (esp.
   `docs/guides/`, `docs/reference/`, `docs/admin/`, `docs/index.md`), and `.github/agents/`.

### P1 — Critical fixes (8.1.3)
3. **Fix broken relative links** in the user-facing set first; prioritize code-target links
   (moved `.py` files) and the missing `TERMINOLOGY_GLOSSARY.md`. Run a full validator pass
   **including `.github/`** (excluded from this sample — §4.2), with code-fence filtering to
   suppress false positives.
4. **Remove/instantiate template placeholders** (`PLAN_TITLE.md`, `{output_file}`).

### P2 — Consolidation (8.1.4)
5. **Consolidate report families.** Move the 1,547 `PHASE_/WAVE_/GATE_` reports and
   `*REPORT/*SUMMARY/*FINAL/*COMPLETION*` docs under a dated `.codex/archive/` hierarchy;
   keep one living index per phase instead of hundreds of point-in-time snapshots.
6. **Rationalize the 224 READMEs / 126 INDEXes;** define which folders warrant an index and
   resolve `ARCHITECTURE.md` vs `architecture.md` casing collisions.
7. **De-clutter the repo root** (120 files → keep ~6 canonical entrypoints).

### P3 — Hygiene & enforcement (8.1.5)
8. Delete/merge 41 stub docs; convert or archive 194 `.txt` reports.
9. Once P0 freshness signal exists, wire link-validation + freshness checks into CI (per
   Brief 8.1.5) with the historical set excluded and manual-review whitelist for FPs.

---

## 8. SUCCESS-CRITERIA STATUS (Workstream 8.1.1)

| Brief Criterion | Status | Note |
|-----------------|--------|------|
| 100% of documentation scanned | ✅ Met | 7,411 `.md` + 194 `.txt` enumerated & categorized |
| Audit report generated | ✅ Met | This document |
| All links validated (results documented) | 🟡 Partial | Sample-based (1,800 files); `.github/` pending; full pass deferred to 8.1.3 |
| Code examples sampled | 🟡 Deferred | Not in this session's scope; flagged for 8.1.3 (doc-refactor-test-agent) |

---

## 9. METHODOLOGY & REPRODUCIBILITY

- **Inventory:** `find . -type f -name '*.md' -not -path '*/.git/*' -not -path '*/node_modules/*'`
  with `sed`/`sort`/`uniq -c` aggregation by directory and basename.
- **Type categorization:** filename pattern matches (`PHASE_*`, `*REPORT*`, `*AGENT*`, etc.).
- **Staleness:** `git log` (found 3 commits → unusable) + content-embedded ISO-date grep
  proxy `(2024|2025)-MM-DD | 2026-0[1-3]-DD`.
- **Link validation:** Python `os.walk` + regex `[text](target)` extraction, relative-target
  existence check against file dir and repo root; two random samples (seeds 42 & 7).
- **Known limitations:** git provenance squashed; `.github/` excluded from link sample;
  automated broken counts include code-fence false positives (manual review required).

---

**Report Status:** 🟢 COMPLETE — Workstream 8.1.1 audit deliverable
**Generated:** 2026-07-03T01:36Z
**Next Step:** Hand off to Workstream 8.1.2 (Remediation Planning) — `.codex/PHASE_8_1_REMEDIATION_PLAN.md`
**Escalation:** @mbaetiong (critical issues)
