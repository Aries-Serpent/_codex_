# 🧹 PHASE 8.2 — CLEANUP STRATEGY & COORDINATION

**Workstream:** 8.2.2 — Repository Cleanup Strategy & Planning  
**Track:** 8.2 (Repository Cleanup & Organization) — Phase 8 Multi-Agent Deployment Campaign  
**Track Lead:** repository-organization-agent  
**Authority:** @mbaetiong (D-tier autonomy)  
**Input:** PHASE_8_2_STRUCTURE_AUDIT.md (WS 8.2.1)  
**Generated:** 2026-07-03  

---

## 1. STRATEGIC OVERVIEW

### Goal
Transform the repository from **17,100 files across 107 top-level dirs (25% bloat in `.codex/`, 4% in venvs)** to a clean, navigable structure with **≤10,000 tracked files**, **≤60 top-level dirs**, and consolidated report/archive taxonomy.

### Core Strategy: **Archive-First, Never Delete**
- All removals are **moves to archival locations**, never hard deletes (preserves auditability and recovery)
- Archival taxonomy is **unified & indexed** (addresses both 8.1 report-sprawl and 8.2 directory cleanup)
- Cleanup proceeds in **dependency-safe phases** (8.2 before 8.3 case-collision work)
- All changes **tracked in git** as commits and documented in action logs

### Three Operational Axes

| Axis | Volume | Target | Reduction |
|------|--------|--------|-----------|
| **Committed Environments** | 715 files (venv_test=511, .venv_ci=202, .mlruns=2) | Remove from tracking | ~4% of repo |
| **Report Consolidation** | 866 + 82 + 32 + 150 = 1,130 files (`.codex/` PHASE_*.md, root reports, build artifacts) | Archive & organize | ~6.6% of repo |
| **Directory Consolidation** | 7 config roots + case-variants + orphans (15+ dirs, <100 files total) | Merge/retire legacy, standardize structure | <1% files, ~10% top-level dirs |

---

## 2. UNIFIED ARCHIVAL TAXONOMY

### 2.1 Master Archival Index: `.codex/archive/INDEX.md`

**Location:** `.codex/archive/INDEX.md` (single source of truth)

**Structure:**
```
.codex/archive/
├── INDEX.md                          ← Master index (this file)
├── phase-history/                    ← Completed phase reports
│   ├── PHASE_1_REPORTS.md            ← Consolidated phase families
│   ├── PHASE_3_REPORTS.md
│   ├── PHASE_4_REPORTS.md
│   ├── ...
│   ├── PHASE_12_REPORTS.md
│   └── INVENTORY.jsonl               ← Searchable file listing
├── root-consolidation/               ← Root-level reports moved from repo root
│   ├── SECURITY_CLUSTER.md
│   ├── REMEDIATION_CLUSTER.md
│   ├── AUDIT_CLUSTER.md
│   ├── DOCUMENTATION_CLUSTER.md
│   ├── TERMINOLOGY_CLUSTER.md
│   └── SESSION_ARTIFACTS.md
├── config-legacy/                    ← Retired config roots
├── build-artifacts/                  ← Removed gitignored artifacts
└── temporary/                        ← Session/scratch artifacts (time-scoped purge)
```

### 2.2 Archival Categories & Retention

| Category | Destination | Retention | Rationale |
|----------|-------------|-----------|-----------|
| **Completed Phase Reports** | `.codex/archive/phase-history/` | Permanent | Auditability, historical reference |
| **Root-Level Reports** | `.codex/archive/root-consolidation/` | Permanent | Cleanup consolidation |
| **Config Legacy** | `.codex/archive/config-legacy/` | Permanent | Reference, dependency tracing |
| **Session Artifacts** | `.codex/archive/temporary/` | 90 days | Time-limited cleanup (with date markers) |
| **Build Artifacts** | Gitignore + remove from tracking | Regenerable | Never archived (size waste) |

### 2.3 Inventory Format (NDJSON)

**File:** `.codex/archive/INVENTORY.jsonl`

```json
{
  "archived_at": "2026-07-03T14:00Z",
  "original_path": ".codex/PHASE_7A_WAVE2_SUMMARY.md",
  "archive_path": ".codex/archive/phase-history/PHASE_7A/PHASE_7A_WAVE2_SUMMARY.md",
  "category": "phase-history",
  "phase_family": "PHASE_7A",
  "file_size_kb": 42,
  "purpose": "Phase 7A wave 2 completion summary",
  "references": ["PHASE_7A_INDEX.md", "cognitive_brain/status/..."]
}
```

### 2.4 Coordination with Track 8.1 (Report Consolidation)

**Track 8.1 Scope:** Consolidate `docs/` content and generated reports into unified documentation structure.  
**Track 8.2 Scope:** Archive historical phase reports and root-level operational artifacts.

**Shared Taxonomy:**
- **Single master index** at `.codex/archive/INDEX.md` lists both 8.1-owned (content) and 8.2-owned (operational) archives
- **No double-moves:** 8.1 consolidates docs in-place; 8.2 moves only *operational* reports (not content)
- **Cross-reference:** Both tracks update the master index with retrieval guides

---

## 3. CLEANUP SEQUENCING

### 3.1 Phase Dependency Diagram

```
[PHASE_8_2_STRUCTURE_AUDIT] ← Complete (WS 8.2.1)
          ↓
[PHASE_8_2_CLEANUP_STRATEGY] ← This document (WS 8.2.2)
          ↓
        ╔═════════════════════════════════════════════════╗
        ║       BATCH A: Pre-Execution Validation        ║
        ║  (Import traces, cross-references, rollback)   ║
        ╚═════════════════════════════════════════════════╝
          ↓
        ╔═════════════════════════════════════════════════╗
        ║      BATCH 0: Committed Venvs (Low Risk)      ║
        ║   - Untrack .venv_ci/, venv_test/, .mlruns/   ║
        ║   - Harden .gitignore                          ║
        ║   - No code impact, ~715 files cleaned         ║
        ╚═════════════════════════════════════════════════╝
          ↓
        ╔═════════════════════════════════════════════════╗
        ║   BATCH 1: Build Artifacts & Backups          ║
        ║   - Gitignore __pycache__/, *.pyc (32)        ║
        ║   - Remove .bak/.orig/.pr5000 (7 files)       ║
        ║   - Delete docs-data/generated/* (regenerable) ║
        ║   - No code impact, ~150 files cleaned        ║
        ╚═════════════════════════════════════════════════╝
          ↓ [8.2 → 8.3 handoff: directory structure stable now]
          ↓
        ╔═════════════════════════════════════════════════╗
        ║   BATCH 2: Root Consolidation (Medium Risk)   ║
        ║   - Move root PHASE_*.md/txt (44 files)       ║
        ║   - Move SECURITY_*, AUDIT_*, etc. (70 files) ║
        ║   - Move session artifacts (sess_001, etc.)    ║
        ║   - Requires reference verification (docs?)    ║
        ║   - ~114 files, validate→archive→git commit   ║
        ╚═════════════════════════════════════════════════╝
          ↓
        ╔═════════════════════════════════════════════════╗
        ║   BATCH 3: .codex/ Phase Reports (High Vol.)  ║
        ║   - Archive completed phases (1–7A: ~600 files)║
        ║   - Keep active phases (8+) at top-level       ║
        ║   - Verify no tooling reads fixed paths        ║
        ║   - Archive via nested dirs + index            ║
        ║   - Largest single reduction: ~600 files       ║
        ╚═════════════════════════════════════════════════╝
          ↓
        ╔═════════════════════════════════════════════════╗
        ║  BATCH 4: Legacy/Config Consolidation         ║
        ║  (Post 8.3 case-collision work)               ║
        ║   - config_legacy/, config_experiments/       ║
        ║   - yaml_legacy/, .config.legacy/             ║
        ║   - .CODEX/, XX.codex/ stray imports          ║
        ║   - Requires 8.3 to de-collide first (safety) ║
        ║   - Archive + .gitignore orphans              ║
        ║   - ~15 dirs, <100 files, high dependency risk║
        ╚═════════════════════════════════════════════════╝
          ↓
        ╔═════════════════════════════════════════════════╗
        ║ VALIDATION: Post-cleanup structure audit      ║
        ║ - Verify directory standards applied          ║
        ║ - Test archive indexes are accurate           ║
        ║ - Confirm imports still resolve               ║
        ║ - Check no broken references in active code   ║
        ╚═════════════════════════════════════════════════╝
```

### 3.2 Risk Mitigation: Order Rationale

1. **Batch 0 first (venvs):** Zero code impact, largest file count reduction, no dependencies.
2. **Batch 1 next (artifacts):** Low-risk, regenerable, prepare directory for consolidation.
3. **Batch 2 before 8.3 (root reports):** Stabilize root directory before case-collision work starts.
4. **Batch 3 after Batch 2 (codex phase reports):** Largest consolidation, but lower risk once root is clean.
5. **Batch 4 after 8.3 (legacy configs):** Deferred until after case-collision de-duplication to avoid churn.

---

## 4. DEPENDENCY & REFERENCE VALIDATION (Batch A)

Before executing any moves, validate that no active tooling or code depends on fixed paths:

### 4.1 Import Tracing Requirements

| Target | Validation Task | Owner | Before Batch |
|--------|-----------------|-------|--------------|
| `yaml_legacy/`, `config_legacy/` | Scan codebase for `from yaml_legacy import`, `from config_legacy import` | Search agent | Batch 4 |
| `.CODEX/`, `XX.codex/` | Grep for direct path references to these dirs | Grep tool | Batch 4 |
| Root PHASE_*.md files | Search docs, issues, workflows for hardcoded links to root reports | GitHub search | Batch 2 |
| `.codex/PHASE_*.md` (before archival) | Check if dashboards, action logs, or agents query specific paths | Code review | Batch 3 |

### 4.2 Git History Preservation

All moved files are tracked as **renames** in git, preserving full blame/history:
```bash
git mv old_path new_path
git commit -m "Archive: Move PHASE_7A_* to .codex/archive/phase-history/"
```

No hard deletes; full recovery possible via `git log --follow`.

### 4.3 Rollback Procedures

Each batch includes a **rollback commit** template:
```bash
# If Batch N fails or causes regressions:
git log --oneline --grep="Batch N:" | head -1
git revert -n <commit_sha>  # Preserve history; don't delete
git commit -m "Rollback Batch N: <reason>"
```

---

## 5. ROOT DECLUTTER BATCHING (Batch 2 Detail)

### 5.1 Root Files: Pre vs Post Cleanup

**Pre-cleanup root:** 205 loose files (82 `.md`, 32 `.txt`, others).

**Post-cleanup root:** Canonical docs only (~20 files):
- `README.md`, `LICENSE`, `SECURITY.md`, `CONTRIBUTING.md`
- `CHANGELOG.md`, `CITATION.cff`
- `pyproject.toml`, `setup.py`, `Makefile`, `Cargo.toml` (build configs)
- `mkdocs.yml`, `pytest.ini`, `.gitignore` (project configs)
- Core docs: `.codex/archive/deprecated/CLAUDE.md`, `.codex/archive/deprecated/GEMINI.md` (model specifications)

**Archived from root (via git mv → archive):**
- **PHASE_* cluster (44):** `.codex/archive/root-consolidation/PHASE_CLUSTER.md`
- **SECURITY_* cluster (8):** `.codex/archive/root-consolidation/SECURITY_CLUSTER.md`
- **SEMGREP_* cluster (3):** `.codex/archive/root-consolidation/SECURITY_CLUSTER.md` (consolidated)
- **REMEDIATION_* cluster (5):** `.codex/archive/root-consolidation/REMEDIATION_CLUSTER.md`
- **AUDIT_* cluster (6):** `.codex/archive/root-consolidation/AUDIT_CLUSTER.md`
- **DOCUMENTATION_* cluster (5):** `.codex/archive/root-consolidation/DOCUMENTATION_CLUSTER.md`
- **TERMINOLOGY_* cluster (3):** `.codex/archive/root-consolidation/TERMINOLOGY_CLUSTER.md`
- **Session/Scratch (sess_001, cost_estimate.json, decision_history.json, etc.):** `.codex/archive/temporary/`

**Deleted from tracking (not archived; fully regenerable):**
- Log/output files: `*.log`, `*_output.txt`, `test_results.txt`, `coverage-report.txt`

### 5.2 Reference Check Before Archive

Before Batch 2, search for hardcoded references to root files:
```bash
# Example: Check for links to PHASE_10_1_FINAL_REPORT.md
git log --all --grep="PHASE_10_1" | head -5
grep -r "PHASE_10_1_FINAL_REPORT" docs/ .github/ src/ || echo "No references found"
```

**If references found:**
1. Update links to new archive path
2. Leave originals as **symlinks** (temporary backward compat, remove in next phase)
3. Document in MIGRATION_NOTES.md

---

## 6. `.CODEX/` PHASE REPORT CONSOLIDATION (Batch 3 Detail)

### 6.1 Current State: 866 Files at `.codex/` Top Level

By phase family (complete phases targeted for archival):

| Phase | Count | Target |
|-------|------:|--------|
| PHASE_7A | 129 | Archive |
| PHASE_6 | 78 | Archive |
| PHASE_3 | 75 | Archive |
| PHASE_7D | 70 | Archive |
| PHASE_7B | 61 | Archive |
| PHASE_2 | 48 | Archive |
| PHASE_4 | 42 | Archive |
| PHASE_1 | 42 | Archive |
| **Subtotal (Phases 1–7)** | **~615** | **Archive** |
| PHASE_8 | 72 | Keep (active) |
| PHASE_9 | 76 | Keep (active) |
| PHASE_10 | 48 | Keep (maybe archive) |
| PHASE_11 | 15 | Keep (active) |
| PHASE_12 | 26 | Keep (active) |
| Other/Newer | 80 | Keep (active) |
| **Subtotal (Phases 8+)** | **~317** | **Keep** |

### 6.2 Archive Structure: Nested Phase Families

```
.codex/archive/phase-history/
├── PHASE_1/
│   ├── PHASE_1_AGENTS_AUDIT.json
│   ├── PHASE_1_AGENTS_AUDIT.md
│   └── ...
├── PHASE_2/
│   ├── PHASE_2_TRACK_4_EXECUTION_COMPLETE.md
│   └── ...
├── PHASE_3/
├── PHASE_4/
├── PHASE_5/
├── PHASE_6/
├── PHASE_7A/
├── PHASE_7B/
├── PHASE_7C/
├── PHASE_7D/
├── INVENTORY.jsonl  ← Full searchable index
└── RETRIEVAL_GUIDE.md
```

### 6.3 Retrieval & Search Interface

**Archive Index:** `.codex/archive/phase-history/INVENTORY.jsonl`
```json
{
  "original_path": ".codex/PHASE_7A_WAVE2_LANE24_COMPLETION_SUMMARY.txt",
  "archive_path": ".codex/archive/phase-history/PHASE_7A/PHASE_7A_WAVE2_LANE24_COMPLETION_SUMMARY.txt",
  "phase_family": "PHASE_7A",
  "keywords": ["wave2", "lane24", "completion", "summary"],
  "size_kb": 8,
  "archived_at": "2026-07-03"
}
```

**Retrieval CLI example:**
```bash
# Find all PHASE_7A reports
jq 'select(.phase_family == "PHASE_7A") | {original: .original_path, archive: .archive_path}' \
  .codex/archive/phase-history/INVENTORY.jsonl

# Find reports mentioning "lane 24"
jq 'select(.keywords[] | contains("lane24"))' \
  .codex/archive/phase-history/INVENTORY.jsonl
```

### 6.4 Verification: No Hardcoded Paths

Before archiving 866 files, verify that no active code reads them at fixed paths:

**Search scope:**
- Cognitive Brain agents in `.github/actions/`
- Action logs in `.codex/action_log.ndjson`
- Dashboards in `.codex/reports/`
- Scripts in `scripts/` that generate reports

**Query example:**
```bash
grep -r "\.codex/PHASE_" .github/ scripts/ cognitive_app/ || echo "No hardcoded paths found"
grep -r "PHASE_[0-9]" .codex/action_log.ndjson | head -5
```

---

## 7. CONFIG DIRECTORY CONSOLIDATION (Batch 4 Detail)

### 7.1 Current State: 7 Config Roots

| Root | Files | Status | Plan |
|------|------:|--------|------|
| `configs/` | 203 | Active | **Keep** (primary) |
| `conf/` | 41 | Active | **Keep** (secondary Hydra) |
| `config_legacy/` | 3 | Legacy | **Archive** (trace imports) |
| `config_experiments/` | 3 | Experimental | **Archive** (low activity) |
| `.config/` | 13 | Mixed | **Review** (symlinks or merge?) |
| `.config.legacy/` | 2 | Legacy | **Remove** (archive + drop) |
| `yaml_legacy/` | 1 | Shim | **Trace** (check if imported) |

### 7.2 Import Tracing

Before archiving legacy configs:

```bash
# Check if yaml_legacy is imported anywhere
grep -r "from yaml_legacy" src/ scripts/ tests/ || echo "Not imported"
grep -r "import yaml_legacy" src/ scripts/ tests/ || echo "Not imported"

# Check if config_legacy is referenced
grep -r "config_legacy" src/ scripts/ tests/ || echo "Not referenced"

# Check .config references
grep -r "\.config/" src/ scripts/ || echo "Not referenced"
```

**Outcome:**
- **If imports found:** Keep as-is, document as legacy shim in `DIRECTORY_STANDARDS.md`
- **If no imports found:** Archive to `.codex/archive/config-legacy/`, remove from tracking

### 7.3 Post-Batch 4 Config Structure

```
configs/         ← Primary (Hydra configs)
├── version.yaml
├── config.yaml
├── logging.yaml
└── ...
conf/            ← Secondary (additional)
├── database.yaml
└── ...

.codex/archive/config-legacy/
├── config_legacy/  ← For reference/historical audit
├── config_experiments/
└── .config.legacy/
```

---

## 8. DIRECTORY STANDARDS (Live Document)

**Owned by:** WS 8.2.2 (outputs to separate `PHASE_8_2_DIRECTORY_STANDARDS.md`)

Key standards post-cleanup:

1. **Top-level directory limit:** ≤60 directories (was 107; target -47)
2. **Loose file limit:** ≤20 root files (was 205; target -185)
3. **.codex/ file limit:** ≤2,000 files (was 4,362; target ~50% reduction)
4. **Archival taxonomy:** Single unified index at `.codex/archive/INDEX.md`
5. **Config roots:** Primary (`configs/`, `conf/`); legacy in archive
6. **Case consistency:** No CAPS-variant pairs (PROMPTS/prompts, etc.)

---

## 9. SUCCESS METRICS

| Metric | Pre | Target | Success Criteria |
|--------|-----|--------|------------------|
| **Total tracked files** | 17,081 | ≤12,000 | ~30% reduction |
| **Top-level directories** | 107 | ≤60 | Cleaner navigation |
| **Loose root files** | 205 | ≤20 | Archive consolidation |
| **.codex/ files** | 4,362 | ≤2,500 | ~43% reduction via archival |
| **Committed venvs** | 715 | 0 | Full untracking |
| **Build artifacts tracked** | ~150 | 0 | Gitignore enforcement |
| **Archive index accuracy** | N/A | 100% | All moves logged + searchable |

---

## 10. TIMELINE & RESPONSIBILITIES

| Phase | Owner | Duration | Dependencies |
|-------|-------|----------|--------------|
| **WS 8.2.1** (Audit) | repo-org-agent | Complete | Input to 8.2.2 |
| **WS 8.2.2** (This: Strategy & Planning) | repo-org-agent | 1 day | Input from 8.2.1 |
| **Batch A** (Pre-execution validation) | Multi-agent (search, grep, review) | 1–2 days | Must complete before Batch 0 |
| **Batch 0** (Venvs) | ci-auto-healer or repo-org-agent | 2 hours | Batch A → start immediately |
| **Batch 1** (Artifacts) | repo-org-agent | 2 hours | Batch 0 complete |
| **Batch 2** (Root consolidation) | repo-org-agent | 4 hours | Batch A validation + Batch 1 complete |
| **→ 8.3 handoff** | repository-organization-agent | | Structure now stable |
| **Batch 3** (Phase reports) | repo-org-agent | 6 hours | Batch 2 complete |
| **Batch 4** (Legacy configs) | repo-org-agent | 4 hours | 8.3 case-collision complete |
| **Validation** | QA/testing agent | 4 hours | All batches complete |
| **WS 8.2.3** (Execution + Validation Report) | repo-org-agent | 2 days | All batches + validation |

---

## 11. COORDINATION WITH PARALLEL TRACKS

### 8.1 ↔ 8.2 (Report Consolidation & Archival)

- **8.1:** Consolidates `docs/` content and generated documentation
- **8.2:** Archives operational reports and phase artifacts

**Shared:** Single master index (`.codex/archive/INDEX.md`) lists both archival taxonomies.

**No double-moves:** 8.1 moves docs content in-place; 8.2 moves only operational/historical reports.

### 8.2 ↔ 8.3 (Directory Restructuring & Case-Collision De-duplication)

- **8.2 Batch 2 (Root consolidation) → complete before 8.3 starts** to stabilize root directory structure
- **8.3:** De-collides case-variant directories (PROMPTS/prompts, etc.)
- **8.2 Batch 4 (Legacy configs) → execute after 8.3 completes** to avoid churn

---

## 12. ROLLBACK & RECOVERY

### Standard Rollback Process

```bash
# If any batch causes issues:
git log --oneline --grep="Batch [0-4]:" | head -1
git revert -n <commit_sha>
git commit -m "Rollback Batch N: <specific reason>"
git push
```

**Data recovery:** All files remain in git history; `git log --follow <file>` traces full rename chain.

### Venv Recovery (Batch 0 Special Case)

If `.venv_ci/` or `venv_test/` are needed locally after untracking:

```bash
git checkout HEAD~1 -- .venv_ci/  # Restore from prior commit
rm -rf .venv_ci/                   # Then remove locally
# OR re-generate locally:
python -m venv .venv_ci
pip install -r requirements-dev.txt
```

---

## 13. SUCCESS CRITERIA (WS 8.2.2)

| Criterion | Delivered |
|-----------|-----------|
| ✅ Unified archival taxonomy designed | `.codex/archive/{phase-history, root-consolidation, config-legacy, temporary}` |
| ✅ Master index format defined | `.codex/archive/INDEX.md` + NDJSON inventory |
| ✅ Dependency validation checklist created | Batch A requirements (import tracing, reference checks) |
| ✅ Phased execution plan with batches | Batches 0–4 + validation + rollback procedures |
| ✅ Root declutter batching strategy | 114 files → archive clusters by category |
| ✅ Phase report consolidation strategy | 866 files → nested phase-family archive dirs + index |
| ✅ Config consolidation strategy | 7 roots → 2 active + legacy archive |
| ✅ Coordination with 8.1/8.3 documented | Shared index + execution sequencing |
| ✅ Success metrics defined | 8 quantifiable targets |
| ✅ Rollback procedures specified | Standard git revert + recovery paths |
| ✅ This document committed to `.codex/` | Ready for 8.2.3 execution |

---

## 14. NEXT STEPS (→ WS 8.2.3: Execution)

1. **Approve this strategy** (authority: @mbaetiong)
2. **Execute Batch A pre-execution validation** (dependencies & references)
3. **Execute Batch 0–4 in sequence** (with git commits, action logs)
4. **Generate archive indexes and retrieval guides**
5. **Validate post-cleanup structure** against standards
6. **Commit execution report** as `PHASE_8_2_EXECUTION_REPORT.md`

---

*Strategy & Planning document generated 2026-07-03 by repository-organization-agent (Track 8.2 lead) under D-tier autonomy. Ready for execution phase. Feeds WS 8.2.3 (Execution & Validation Report).*
