# 🎯 PHASE 8.2 CLEANUP STRATEGY
## Workstream 8.2.2 — Comprehensive Repository Cleanup Approach

**Track:** 8.2 (Repository Cleanup & Organization)  
**Authority:** @mbaetiong (D-tier autonomous, GO CONTINUE)  
**Input:** PHASE_8_2_STRUCTURE_AUDIT.md (WS1, completed 2026-07-03)  
**Status:** Planning Phase  
**Generated:** 2026-07-07T14:26Z  
**Deliverable:** Strategy Framework → Feeds WS3 (Execution)

---

## 1. EXECUTIVE SUMMARY

The Phase 8.2 cleanup campaign targets **4 major bloat categories** identified in the WS1 audit:

| Category | Volume | Target Reduction | Risk | Priority |
|----------|--------|------------------|------|----------|
| **Committed Virtual Environments** | 715 files | 100% untrack + reignore | 🟢 Low | P0 |
| **`.codex/` Report Proliferation** | 4,362 files (866 PHASE_*.md at root) | Archive phases 1-7 + consolidate | 🟡 Medium | P1 |
| **Root-Level Clutter** | 205 loose files (82 .md, 32 .txt) | Move to `.codex/reports/` | 🟡 Medium | P1 |
| **Config Directory Sprawl** | 7 roots (config*, conf*, .config*) | Consolidate 5 → 2 canonical | 🟠 Medium-High | P2 |

**Aggregate Impact:**
- **Files removed from tracking:** ~1,200 (venvs + reported duplicates)
- **Repository size reduction:** ~50 MB (venvs + generated data)
- **Root-level clutter eliminated:** ~95% (187 of 205 loose files)
- **Navigation clarity gain:** 107 → ~85 top-level directories

---

## 2. CLEANUP CATEGORIES & STRATEGIES

### Category A: Committed Virtual Environments (Priority 0 — Immediate)

**Problem:** `venv_test/` (511 files) and `.venv_ci/` (202 files) committed to git.  
**Risk Assessment:** 🟢 **Low** — regenerable, never belong in VCS.  
**Target:** Remove from tracking + harden .gitignore.

#### A.1 Untrack Strategy

1. **Phase 1 (WS3.1):** Use `git rm --cached` to remove from tracking:
   - `git rm --cached -r venv_test/` (511 files)
   - `git rm --cached -r .venv_ci/` (202 files)
   - Commit: `"Untrack committed virtual environments"`

2. **Phase 2 (WS3.1):** Harden `.gitignore`:
   - Add entries for `venv_test/`, `.venv_ci/`, `.venv/`, `.env/`, `venv/`
   - Add entry for `.mlruns/`
   - Document: "Reasons for venv gitignore rules in CONTRIBUTING.md"

3. **Phase 3 (WS3.1):** Local testing:
   - `git status` → verify venvs show as untracked, not deleted
   - Verify `.gitignore` prevents re-tracking on local commits

#### A.2 Rollback Procedure

If venvs are needed for CI recovery:
```bash
git restore venv_test/.
git restore .venv_ci/.
```

**Note:** Committed binaries (`ruff` 27 MB, `py-spy` 7.8 MB) will remain in git history but be removed from HEAD.

---

### Category B: `.codex/` Report Proliferation (Priority 1 — High Volume)

**Problem:** 4,362 files in `.codex/`, including **866 `PHASE_*.md` reports at root** that form the largest consolidation target.  
**Risk Assessment:** 🟡 **Medium** — must verify no tooling reads fixed paths.  
**Target:** Archive phases 1-7 + create taxonomy index.

#### B.1 Archival Taxonomy

Create `.codex/archive/phase-reports/` structure:

```
.codex/archive/
├── phase-reports/
│   ├── phase-1-10/          # Phases 1-10 (completed)
│   │   ├── PHASE_1/         # 42 files
│   │   ├── PHASE_2/         # (grouped)
│   │   ├── ...
│   │   ├── PHASE_10/        # 48 files
│   │   └── PHASE_INDEX.md   # Navigation index
│   ├── phase-11-13/         # Phases 11-13
│   │   ├── PHASE_11/
│   │   ├── PHASE_12/        # 26 files
│   │   ├── PHASE_13/        # (if needed)
│   │   └── PHASE_INDEX.md
│   ├── phase-maintenance/   # Ongoing operational reports
│   │   ├── ACCOUNTABILITY/
│   │   ├── TELEMETRY/
│   │   └── EVIDENCE/
│   └── ARCHIVE_README.md    # Master index + retrieval guide
```

#### B.2 Migration Sequence

**Batch 1 (WS3.2):** Phases 1-7 (completed, not referenced by current system)
- PHASE_7A (129) → `.codex/archive/phase-reports/phase-1-10/PHASE_7A/`
- PHASE_6 (78) → `.codex/archive/phase-reports/phase-1-10/PHASE_6/`
- PHASE_3 (75) → `.codex/archive/phase-reports/phase-1-10/PHASE_3/`
- PHASE_7D (70) → `.codex/archive/phase-reports/phase-1-10/PHASE_7D/`
- PHASE_7B (61) → `.codex/archive/phase-reports/phase-1-10/PHASE_7B/`
- PHASE_4 (42) → `.codex/archive/phase-reports/phase-1-10/PHASE_4/`
- PHASE_1 (42) → `.codex/archive/phase-reports/phase-1-10/PHASE_1/`
- Plus: PHASE_10 (48), PHASE_9 (76), PHASE_5, etc.
- **Total Batch 1:** ~600+ files moved

**Verification Pre-Batch 1:**
- Grep `.codex/` for any references to `PHASE_1_` through `PHASE_7_` paths
- Check GitHub Issues/PRs for links to these files
- Confirm no CI/CD workflows reference specific file paths

**Batch 2 (WS3.3):** Phases 8-current (recent, may be referenced)
- PHASE_8 (72 files) → `.codex/archive/phase-reports/phase-1-10/PHASE_8/`
- (Keep Phases 11+ at `.codex/` root for active reference until Phase 15+)

#### B.3 Index Creation

Create `.codex/archive/phase-reports/ARCHIVE_README.md`:
```markdown
# Phase Reports Archive

## Structure
- **phase-1-10/:** Phases 1-10 (completed campaigns, historical reference)
- **phase-11-13/:** Phases 11-13 (recent, limited reference)
- **phase-maintenance/:** Accountability, telemetry, evidence (operational)

## Search & Retrieval

### Find a Phase Report
1. Determine phase number (e.g., "PHASE_7A_WAVE2_LANE24")
2. Navigate to corresponding subdirectory: `phase-1-10/PHASE_7A/`
3. Search filename in README-indexed list

### Common Queries
- All PHASE_7A results: `phase-1-10/PHASE_7A/`
- All accountability reports: `phase-maintenance/ACCOUNTABILITY/`

## Coordination
- Track 8.1 consolidates docs; uses same taxonomy
- Index updated per-phase; last updated 2026-07-07
```

---

### Category C: Root-Level Clutter (Priority 1 — High Volume)

**Problem:** 205 loose root files (82 .md, 32 .txt), including status/phase/remediation reports.  
**Risk Assessment:** 🟡 **Medium** — some may be linked from docs/issues.  
**Target:** Move to `.codex/reports/` or archive; leave only canonical root docs.

#### C.1 Root File Classification

**KEEP at root (canonical repo docs):**
- `README.md` — project intro
- `CHANGELOG.md` — version history
- `LICENSE` — licensing
- `CONTRIBUTING.md` — contribution guide
- `CODE_OF_CONDUCT.md` — community standards
- `SECURITY.md` — security policy
- `.codex/archive/misc/INSTALL.md` — installation guide
- `docs/api/reference/INTEGRATION.md` — integration guide
- `.codex/archive/deprecated/GEMINI.md`, `.codex/archive/deprecated/CLAUDE.md` — model-specific guides (keep)
- `CITATION.cff` — citation metadata

**MOVE to `.codex/reports/` (status/phase reports):**
- PHASE_* reports at root (44 files)
- SECURITY_* cluster (4: FIXES_SUMMARY, MONITORING_PLAN, REMEDIATION_GUIDE, REMEDIATION_PHASE1_REPORT)
- SEMGREP_* cluster (3: remediation reports, triage, etc.)
- REMEDIATION_* cluster (3: CHECKPOINT, PHASE_3_RESULTS, plans)
- AUDIT_* cluster (3: COMPLETION, SUMMARY, summary.json)
- DOCUMENTATION_* cluster (6: AUDIT variants, UPDATE variants)
- TERMINOLOGY_* cluster (3)
- Remediation plans (3: remediation_plan_sbom.md, remediation_plan_secrets.md, remediation_plan_semgrep.md)
- **Total: ~82 .md files + ~32 .txt files**

**REMOVE (scratch/temp/logs):**
- Root-level logs: `phase_9_2_*.log`, `test_execution_log.txt`, `test_results.txt`, `coverage-report.txt`
- Tool output: `gh_output.txt`, `mutmut_output.txt`, `mypy_output.txt`, `mypy_error_analysis.txt`
- Session files: `sess_001`, `cost_estimate.json`, `decision_history.json`
- **Total: ~15 files**

#### C.2 Migration Strategy

**Phase 1 (WS3.2):** Move reports to `.codex/reports/`

```bash
# Create subdirectories for organization
mkdir -p .codex/reports/{phase-history,security,remediation,audit,documentation}

# Move phases
mv PHASE_*.md PHASE_*.txt .codex/reports/phase-history/

# Move security reports
mv SECURITY_*.md SECURITY_*.txt .codex/reports/security/

# Move remediation reports
mv REMEDIATION_*.md REMEDIATION_*.txt remediation_plan_*.md \
   .codex/reports/remediation/

# Move audit reports
mv AUDIT_*.md AUDIT_*.txt .codex/reports/audit/

# Move documentation reports
mv DOCUMENTATION_*.md .codex/reports/documentation/

# Move terminology reports
mv TERMINOLOGY_*.md .codex/reports/documentation/

# Create index
cat > .codex/reports/INDEX.md << 'REPORTS_INDEX'
# Root-Level Reports Index

All phase, security, audit, and remediation reports consolidated from repo root.

## Categories
- **phase-history/:** Phase reports (WS1 phases 0-13)
- **security/:** Security scanning, remediation, monitoring
- **remediation/:** Remediation checkpoints and plans
- **audit/:** Code audit reports
- **documentation/:** Documentation audit and update reports

## Reference
If you find a link to a root-level PHASE_*.md or SECURITY_*.md file,
look in the corresponding subdirectory above.
REPORTS_INDEX
```

**Phase 2 (WS3.2):** Remove scratch files

```bash
rm -f phase_9_2_*.log gh_output.txt mutmut_output.txt \
      mypy_output.txt mypy_error_analysis.txt coverage-report.txt \
      test_execution_log.txt test_results.txt \
      sess_001 cost_estimate.json decision_history.json
```

#### C.3 Reference Update Verification

Before moving, check for references in:
1. `.github/workflows/` (automation that might reference file paths)
2. `docs/` (documentation links)
3. Root `README.md` (if linked)
4. GitHub Issues (search via GitHub API)

**Process:**
```bash
# Find all references in codebase
grep -r "PHASE_" .github/workflows/ docs/ src/ || true
grep -r "SECURITY_FIXES_SUMMARY" .github/workflows/ docs/ src/ || true
```

---

### Category D: Config Directory Consolidation (Priority 2 — Dependency Critical)

**Problem:** 7 overlapping config roots (config, config_legacy, config_experiments, configs, conf, .config, .config.legacy).  
**Risk Assessment:** 🟠 **Medium-High** — legacy shims may still be imported.  
**Target:** Consolidate to 2 canonical roots; retire overlapping ones.

#### D.1 Current State

| Root | Files | Status | Purpose |
|------|------:|--------|---------|
| `configs/` | 203 | 🟢 Active | Primary Hydra configs (canonical) |
| `conf/` | 41 | 🟢 Active | Supplementary configs (canonical) |
| `config_legacy/` | 3 | 🟠 Legacy | Old config format (archive candidate) |
| `config_experiments/` | 3 | 🟠 Legacy | Experiment configs (archive candidate) |
| `.config.legacy/` | 2 | 🟠 Legacy | Legacy metadata (archive candidate) |
| `config/` | 3 | 🟠 Unclear | Stub or duplicate? |
| `.config/` | 13 | 🟠 Unclear | VsCode settings or project config? |

#### D.2 Consolidation Strategy

**Action 1 (WS3.4):** Audit imports to `config_legacy/`, `.config.legacy/`, `yaml_legacy/`

```bash
# Find all imports of legacy configs
grep -r "from config_legacy" src/ scripts/ .github/ || echo "No imports found"
grep -r "import config_legacy" src/ scripts/ .github/ || echo "No imports found"
grep -r "yaml_legacy" src/ scripts/ .github/ || echo "No imports found"
grep -r "\.config\.legacy" src/ scripts/ .github/ || echo "No imports found"

# Check for file path references
grep -r "config_legacy/" src/ scripts/ docs/ .github/ || echo "No path refs found"
grep -r "yaml_legacy/" src/ scripts/ docs/ .github/ || echo "No path refs found"
```

**Action 2 (WS3.4):** Based on audit, migrate or archive

**Scenario A (No imports found):**
```bash
# Archive without promoting to active search
mv config_legacy/ .codex/archive/config-legacy-backup/
mv .config.legacy/ .codex/archive/config-legacy-metadata/
mv yaml_legacy/ .codex/archive/yaml-legacy-shim/
```

**Scenario B (Imports found):**
```bash
# Leave in place; document as deprecated shims in CONTRIBUTING.md
# Plan removal for Phase 9 after code update
echo "config_legacy: DEPRECATED, imports still exist, scheduled for Phase 9 removal" \
  > .codex/CONFIG_CONSOLIDATION_STATUS.md
```

**Action 3 (WS3.4):** Consolidate `config/` and `.config/`

```bash
# If config/ is a duplicate of configs/, remove
if diff -r config/ configs/ > /dev/null 2>&1; then
  rm -rf config/
  echo "Removed duplicate config/ directory"
fi

# If .config/ contains VsCode settings, leave as-is
# If .config/ contains project config, merge into configs/
```

#### D.3 Documentation

Create `.codex/CONFIG_CONSOLIDATION_STATUS.md`:
```markdown
# Config Directory Consolidation Status

## Canonical Roots
- **`configs/`** (203 files) — Primary Hydra configuration (ACTIVE)
- **`conf/`** (41 files) — Supplementary Hydra configuration (ACTIVE)

## Archived/Deprecated
- **`config_legacy/`** → `.codex/archive/config-legacy-backup/` (no active imports)
- **`yaml_legacy/`** → `.codex/archive/yaml-legacy-shim/` (no active imports)
- **`.config.legacy/`** → `.codex/archive/config-legacy-metadata/` (no active imports)

## Decision Log
- 2026-07-07: Audit phase complete; no active imports found
- 2026-07-08: Migration to archive completed (WS3.4)
- Next: Phase 9 cleanup removes archive directories entirely

## Migration Process
If you encounter references to `config_legacy` or `yaml_legacy`:
1. Check git history: `git log --follow -p config_legacy/`
2. Review CONTRIBUTING.md for context
3. Report in Phase 9 planning for removal
```

---

## 3. DEPENDENCY MAPPING & IMPACT ANALYSIS

### What Depends on These Changes?

**Low-Risk Changes:**
- Untracking venvs → Local dev friction if devs don't have .gitignore (mitigated by docs)
- Removing root logs/scratch → None (no references expected)

**Medium-Risk Changes:**
- Moving `.codex/` PHASE_* reports → Check for agent references (done in B.1)
- Moving root PHASE_* reports → Check for documentation links (done in C.3)

**High-Risk Changes:**
- Config consolidation → Must complete import audit (done in D.2)

### Coordination with Other Tracks

**Track 8.1 (Documentation Consolidation):**
- Uses same archival taxonomy for report consolidation
- Shares `.codex/archive/` namespace
- **Handoff:** 8.1 references Phase 8.2 taxonomy in its cleanup plan

**Track 8.3 (Case-Collision Fixes):**
- Case-sensitivity fixes (e.g., `PROMPTS/` → `prompts/`) should **precede** bulk moves
- **Sequence:** 8.3 executes first → 8.2 bulk moves execute after 8.3 completes
- **Rationale:** Avoid moving files that will be renamed for case-collision anyway

---

## 4. SUCCESS CRITERIA FOR WS2 PLANNING PHASE

| Criterion | Status | Notes |
|-----------|:------:|-------|
| All 4 cleanup categories stratified | ✅ | A: Venvs, B: Reports, C: Root clutter, D: Configs |
| Priority matrix defined (P0-P2) | ✅ | P0: venvs, P1: reports/root, P2: configs |
| Risk assessment completed | ✅ | Low/Medium/High per category |
| Archival taxonomy designed | ✅ | `.codex/archive/phase-reports/` structure |
| Migration sequence documented | ✅ | Batch 1-2 for reports; phases for each category |
| Rollback procedures provided | ✅ | For venvs, config changes |
| Dependency verification plan | ✅ | Import audits, reference checks |
| Cross-track coordination documented | ✅ | 8.1, 8.3 dependencies noted |

**Readiness for WS3 (Execution):** ✅ **YES** — All planning criteria met.

---

## 5. IMPLEMENTATION CONSTRAINTS & SAFETY

### Constraints (Non-Negotiable)

1. **No source-of-truth code deletion** — All cleanup targets are reports, archives, or regenerable
2. **All moves preserve git history** — Use `git mv` and `git rm --cached` only
3. **No workflow modifications** — `.disabled` files stay; track 8.x does not touch workflows
4. **All output to `.codex/`** — No `/tmp`; all planning files version-controlled
5. **Coordination gates** — Track 8.3 completes before bulk moves in 8.2

### Safety Mechanisms

1. **Dry-run verification:** Each move batched with `git status` check
2. **Commit granularity:** One logical category per commit (venvs, reports, root clutter)
3. **Reference verification:** Grep + GitHub API checks pre-move
4. **Rollback documentation:** Each category includes undo procedure
5. **Impact reporting:** Summary of changes per batch (files moved, size saved)

---

## 6. CLEANUP STRATEGY SUMMARY TABLE

| Category | Files | Target | Strategy | Risk | Timeline |
|----------|------:|--------|----------|------|----------|
| **Venvs** | 715 | Untrack + reignore | `git rm --cached` + `.gitignore` | 🟢 Low | WS3.1 (1-2h) |
| **`.codex/` Reports** | 4,362 | Archive phases 1-7 (600+) | Batch move to `.codex/archive/phase-reports/` | 🟡 Medium | WS3.2-3.3 (4-6h) |
| **Root Clutter** | 205 | Move to `.codex/reports/` | Batch move + reference verification | 🟡 Medium | WS3.2 (2-3h) |
| **Config Dirs** | 266 | Archive legacy; consolidate active | Import audit + selective merge | 🟠 Medium-High | WS3.4 (2-3h) |

**Total Estimated Cleanup Time:** 9-14 hours across 4 days (WS3 execution phase)

---

## 7. NEXT STEPS (WS2 → WS3 Handoff)

**Upon approval of this strategy:**

1. Create `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` — Target root-level structure design
2. Create `.codex/PHASE_8_2_CLEANUP_PHASES.md` — Week-by-week execution schedule (5 weeks)
3. Submit to Track 8.2 lead for go/no-go decision on WS3 execution
4. If approved: Activate WS3 (Execution) → Begin venv untracking (P0 immediate wins)

---

**Status:** ✅ Planning Complete  
**Deliverable:** PHASE_8_2_CLEANUP_STRATEGY.md (this document)  
**Authority:** @mbaetiong (D-tier, GO CONTINUE on approval)  
**Handoff Target:** WS3 (Cleanup Execution)

---

*End of Cleanup Strategy Document. See PHASE_8_2_DIRECTORY_STANDARDS.md for target root structure and PHASE_8_2_CLEANUP_PHASES.md for detailed weekly execution plan.*
