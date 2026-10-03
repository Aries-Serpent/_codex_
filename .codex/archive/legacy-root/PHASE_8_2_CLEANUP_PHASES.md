# Phase 8.2 Workstream 3 — Cleanup Execution Schedule

**Document:** `.codex/PHASE_8_2_CLEANUP_PHASES.md`  
**Authority:** @mbaetiong (D-tier autonomous)  
**Status:** WS3 Handoff Package / Execution Authorization  
**Timeline:** Weeks 2-5, Days 1-24 (Phase 1-4 batched execution)  
**Last Updated:** 2026-07-03

---

## 📋 Executive Summary

This document specifies the **detailed week-by-week execution schedule for WS3 (Cleanup Execution)**, coordinating cleanup categories A-D into 4 phased waves across Weeks 2-5 with daily task breakdowns, git commit boundaries per category, verification checkpoints, and safety gates.

### Execution Strategy Overview

| Phase | Category | Priority | Duration | Key Task | Batch Commits | Risk Level |
|-------|----------|----------|----------|----------|---------------|-|
| **Phase 1** | A: Venvs | P0 | 1-2 hrs | `git rm --cached` venv files + .gitignore hardening | 1 commit | Low |
| **Phase 2** | B+C: Reports+Root | P1 | 4-6 hrs | Archive reports to `.codex/archive/phase-reports/`, move root clutter to `.codex/reports/` | 2 commits | Medium |
| **Phase 3** | C: Orphan Audit | P1 | 2-3 hrs | Audit orphaned structures, execute cleanup decisions | 1-2 commits | Medium |
| **Phase 4** | D: Config Consolidation | P2 | 2-3 hrs | Consolidate config roots, audit legacy imports, standardize | 2 commits | Medium-High |
| **TOTAL** | — | — | **9-14 hrs** | Repository cleanup (17,100 → ~16,000 files) | **6-7 commits** | — |

**Pre-execution Gates:**
- ✅ Track 8.3 case-collision fixes MUST complete before Phase 2 bulk moves (prerequisite validation)
- ✅ All 3 planning deliverables reviewed and approved
- ✅ Safety procedures verified and documented

---

## 🔧 Phase 1: Venv Untracking (P0 Priority)

**Category:** A — Venvs  
**Timeline:** Week 2, Days 1-3 (1-2 hours total)  
**Objective:** Remove 715 committed venv files from git tracking, apply .gitignore hardening  
**Target Reduction:** 50 MB saved, 713 files untracked

### Day 1: Plan Review & Staging

**Tasks:**
1. ✓ **Pre-execution validation** (15 min)
   - Confirm no active venv in use during this phase
   - Verify git status is clean (no pending changes)
   - Confirm venv directories exist: `venv_test/` (511 files), `.venv_ci/` (202 files)
   - Size check: `du -sh venv_test/ .venv_ci/` → expect ~50 MB total

2. ✓ **Create execution branch** (5 min)
   - Branch: `cleanup/phase-1-venv-untracking`
   - Base: main
   - Purpose: Isolated venv cleanup track

3. ✓ **Generate cleanup plan** (10 min)
   - List affected files: `git ls-files venv_test/ .venv_ci/ | wc -l` → expect ~713 files
   - Verify no imports reference venv paths (grep `from venv_`, `import venv_` in src/ tests/)
   - Confirm .gitignore template ready for venv patterns

4. ✓ **Commit: Plan + Safety Check** (5 min)
   - Message: `phase-1: Plan venv untracking (715 files, 50 MB)`
   - Files: cleanup plan log, pre-execution checklist

**Output:** Execution branch created, plan validated, safety gates passed

### Day 2: Execute Venv Removal

**Tasks:**
1. ✓ **Remove venv_test/** (20 min)
   ```bash
   git rm --cached -r venv_test/
   # Expected: 511 files removed from index, kept in working directory
   git status | grep deleted | wc -l  # Verify ~511 deletions
   ```

2. ✓ **Remove .venv_ci/** (15 min)
   ```bash
   git rm --cached -r .venv_ci/
   # Expected: 202 files removed from index, kept in working directory
   git status | grep deleted | wc -l  # Verify ~202 deletions
   ```

3. ✓ **Update .gitignore** (10 min)
   - Add hardening patterns:
     ```
     # Virtual environments
     /venv/
     /venv_test/
     /.venv/
     /.venv_ci/
     /env/
     **/venv/
     **/env/
     ```
   - Verify patterns with: `git check-ignore -v venv_test/ .venv_ci/`

4. ✓ **Commit: Venv removal + .gitignore hardening** (5 min)
   - Message: `phase-1: Remove venvs from tracking + .gitignore hardening (713 files, 50 MB)`
   - Files: venv_test/, .venv_ci/, .gitignore
   - Verify commit size: `git diff-tree --name-count -r HEAD~1 HEAD | head -5`

**Output:** 713 files untracked, .gitignore hardened, committed (1 commit total)

### Day 3: Verification & Completion

**Tasks:**
1. ✓ **Verify untracking** (10 min)
   ```bash
   git ls-files venv_test/ .venv_ci/ | wc -l  # Expect 0 (no files in index)
   ls -d venv_test/ .venv_ci/ 2>/dev/null | wc -l  # Expect 2 (directories still on disk)
   ```

2. ✓ **Confirm size reduction** (5 min)
   ```bash
   git count-objects -v | grep size-pack
   # Expect: New index smaller by ~50 MB
   ```

3. ✓ **Validate .gitignore patterns** (5 min)
   ```bash
   git check-ignore -v venv_test/ .venv_ci/ | grep -c venv/
   # Expect: Both directories matched by .gitignore patterns
   ```

4. ✓ **Check for stray artifacts** (5 min)
   - Grep for venv references: `grep -r "venv_test\|\.venv_ci" src/ tests/ --include="*.py" | head -10`
   - Verify none found (expect 0 matches or only documentation references)

5. ✓ **Merge to main** (5 min)
   - Command: `git merge --no-ff cleanup/phase-1-venv-untracking`
   - Commit message: `Merge phase-1: Venv untracking complete (713 files untracked)`

**Output:** Phase 1 complete, verified, main branch updated (1 commit)

---

## 📦 Phase 2: Report Archival + Root Clutter Consolidation (P1 Priority)

**Category:** B + C — Reports + Root Declutter  
**Timeline:** Week 3, Days 1-6 (4-6 hours total)  
**Objective:** Archive 600+ `.codex/` phase reports, consolidate 95 root .md/.txt files to organized subdirectories  
**Target Reduction:** ~850 files reorganized, root clutter ~95% eliminated

### Pre-Execution Dependency Check

**⚠️ Gate:** Track 8.3 case-collision fixes MUST be complete before Phase 2 execution
- Verify `.CODEX/` → `.codex/` normalization complete
- Verify `XX.codex/` remediation complete
- Verify `PROMPTS/` → `prompts/` consolidation complete
- Confirm no pending case-sensitive directory moves (would conflict with Phase 2 moves)

### Day 1: Archival Structure Setup

**Tasks:**
1. ✓ **Create archive directory structure** (10 min)
   ```bash
   mkdir -p .codex/archive/phase-reports/phase-1-10
   mkdir -p .codex/archive/phase-reports/phase-11-13
   mkdir -p .codex/archive/phase-reports/phase-maintenance
   git add .codex/archive/
   git commit -m "phase-2: Create archival directory structure"
   ```

2. ✓ **Create ARCHIVE_README.md** (15 min)
   - Location: `.codex/archive/phase-reports/ARCHIVE_README.md`
   - Content sections:
     - Overview: Archive purpose, consolidation timeline
     - Structure: Directory organization (phase-1-10, phase-11-13, phase-maintenance)
     - Inventory: File count by phase (600+ files)
     - Retrieval guide: How to access archived reports
     - Compliance: Retention policy (permanent)
     - Index: Master list of archived files with dates

3. ✓ **Create root consolidation directories** (10 min)
   ```bash
   mkdir -p .codex/reports/phase-history
   mkdir -p .codex/reports/security
   mkdir -p .codex/reports/remediation
   mkdir -p .codex/reports/audit
   mkdir -p .codex/reports/documentation
   git add .codex/reports/
   git commit -m "phase-2: Create root consolidation directory structure"
   ```

4. ✓ **Commit: Archive setup** (5 min)
   - Message: `phase-2-a: Create archival and consolidation directories`
   - Status: Phase 2a complete, ready for file moves

**Output:** Directory structure created, ARCHIVE_README template prepared

### Day 2-3: Move Phase Reports to Archive

**Tasks:**
1. ✓ **Move Phase 1-7 reports to phase-1-10/** (30 min)
   - Target reports: PHASE_1_*.md, PHASE_2_*.md, ..., PHASE_7_*.md (600+ files)
   - Command:
     ```bash
     git mv PHASE_[1-7]_*.md .codex/archive/phase-reports/phase-1-10/
     ```
   - Expected: ~600 files moved

2. ✓ **Move Phase 11-13 active reports to phase-11-13/** (20 min)
   - Target reports: PHASE_11_*.md, PHASE_12_*.md, PHASE_13_*.md (100+ files)
   - Command:
     ```bash
     git mv PHASE_{11,12,13}_*.md .codex/archive/phase-reports/phase-11-13/
     ```

3. ✓ **Move accountability + evidence to phase-maintenance/** (15 min)
   - Target files: AUDIT_*.md, ENERGY_CONVERSION_*.md, QUANTUM_*.md, etc.
   - Command:
     ```bash
     git mv *_DEPRECATION.md *_INTEGRATION_GUIDE.md AUDIT_*.md \
       .codex/archive/phase-reports/phase-maintenance/
     ```

4. ✓ **Update ARCHIVE_README.md** (10 min)
   - Add full inventory section with file counts per phase
   - Add retrieval timestamps and organization metadata
   - Add cross-reference index linking to Track 8.1 consolidation

5. ✓ **Commit: Phase reports archived** (5 min)
   - Message: `phase-2-b: Archive 600+ phase reports to .codex/archive/phase-reports/`
   - Verify: `git status | grep renamed | wc -l` → expect ~700+ renames

**Output:** Phase reports archived (600+ files moved, 1 commit)

### Day 4-5: Move Root Clutter to Consolidation Directories

**Tasks:**
1. ✓ **Move phase-history reports** (15 min)
   - Target files: PHASE_*.md, WAVE_*.md, TRACK_*.md, STREAM_*.md (82 .md files)
   - Destination: `.codex/reports/phase-history/`
   - Command:
     ```bash
     git mv PHASE_*.txt WAVE_*.md TRACK_*.md STREAM_*.md \
       .codex/reports/phase-history/
     ```

2. ✓ **Move security reports** (10 min)
   - Target files: SECURITY_*.md, REMEDIATION_*.md, SECURITY_*.txt (25 files)
   - Destination: `.codex/reports/security/`
   - Command:
     ```bash
     git mv SECURITY_*.md SECURITY_*.txt REMEDIATION_*.md \
       .codex/reports/security/
     ```

3. ✓ **Move audit + compliance reports** (10 min)
   - Target files: AUDIT_*.md, *_AUDIT_*.md, *_COMPLIANCE_*.md, REMEDIATION_*.txt (15 files)
   - Destination: `.codex/reports/audit/`
   - Command:
     ```bash
     git mv AUDIT_*.md *_AUDIT_*.md *COMPLIANCE*.md \
       .codex/reports/audit/
     ```

4. ✓ **Move documentation reports** (10 min)
   - Target files: DOCUMENTATION_*.md, *_DOCUMENTATION_*.md (20 files)
   - Destination: `.codex/reports/documentation/`
   - Command:
     ```bash
     git mv DOCUMENTATION_*.md *_DOCUMENTATION_*.md \
       .codex/reports/documentation/
     ```

5. ✓ **Commit: Root clutter consolidated** (5 min)
   - Message: `phase-2-c: Consolidate 95 root files to .codex/reports/ subdirectories (phase-history, security, remediation, audit, documentation)`
   - Verify: `git status | grep renamed | wc -l` → expect ~95 renames

**Output:** Root clutter consolidated (95 files moved, 1 commit)

### Day 6: Link Verification & Documentation Updates

**Tasks:**
1. ✓ **Pre-move reference audit** (20 min)
   - Grep hardcoded paths in source:
     ```bash
     grep -r "PHASE_.*\.md\|SECURITY_.*\.md\|REMEDIATION_" src/ tests/ --include="*.py" --include="*.sh"
     ```
   - GitHub Actions workflow path references:
     ```bash
     grep -r "PHASE_\|SECURITY_\|REMEDIATION_" .github/workflows/ --include="*.yml"
     ```
   - CI/CD configuration hardcoded paths: `grep -r "phase-reports\|PHASE_" .codex/ | grep -v "PHASE_8_2"`

2. ✓ **Fix broken documentation links** (20 min)
   - Update internal references: `grep -r "PHASE_.*\.md" docs/ | head -20`
   - Rebase navigation links in TABLE_OF_CONTENTS (if exists)
   - Update CI/CD path references to point to new archive locations:
     ```
     OLD: PHASE_1_AGENTS_AUDIT.json
     NEW: .codex/archive/phase-reports/phase-1-10/PHASE_1_AGENTS_AUDIT.json
     ```

3. ✓ **Verify no broken anchors** (10 min)
   ```bash
   # Find markdown links to archived files
   grep -r "\[.*\](.*PHASE_" README.md docs/ 2>/dev/null | head -10
   # Verify all links point to new archive paths
   ```

4. ✓ **Create REPORTS_INDEX.md** (15 min)
   - Location: `.codex/reports/README.md`
   - Content: Index of all consolidated root reports by category
   - Add quick-access links to phase-history/, security/, remediation/, audit/, documentation/
   - Include retrieval guide for archived reports

5. ✓ **Commit: Documentation + link updates** (5 min)
   - Message: `phase-2-d: Update documentation links, add reports index`
   - Verify: No broken links in rendered markdown

**Output:** Link verification complete, documentation updated (1 commit)

---

## 🔍 Phase 3: Orphan Directory & Single-File Audit (P1 Priority)

**Category:** C — Orphan Cleanup  
**Timeline:** Week 4, Days 1-3 (2-3 hours total)  
**Objective:** Identify and clean orphaned single-file directories, residual artifacts  
**Target:** ~50 directories consolidated, ~20 files archived

### Day 1: Audit & Categorization

**Tasks:**
1. ✓ **Identify single-file directories** (20 min)
   ```bash
   find . -maxdepth 2 -type d -not -path './.git*' -not -path './src/*' -not -path './tests/*' | \
   while read dir; do
     count=$(find "$dir" -type f 2>/dev/null | wc -l)
     if [ "$count" -eq 1 ]; then echo "$dir"; fi
   done | sort
   ```
   - Expected: ~30-50 single-file directories

2. ✓ **Categorize cleanup decisions** (20 min)
   - Move to `.codex/archive/`: Deprecated configs, old test data
   - Consolidate to subdirectories: Related single files
   - Delete: Temporary build artifacts, cache files (if not source-of-truth)

3. ✓ **Audit import dependencies** (15 min)
   ```bash
   for file in $(find . -maxdepth 2 -type f); do
     grep -r "$(basename $file)" src/ tests/ --include="*.py" --include="*.sh" || true
   done | grep -v Binary | wc -l
   # Expect low match count for orphaned files
   ```

4. ✓ **Commit: Audit plan** (5 min)
   - Message: `phase-3-a: Audit orphaned structures and cleanup decisions`

**Output:** Orphaned structures identified, cleanup plan documented

### Day 2-3: Execute Orphan Cleanup

**Tasks:**
1. ✓ **Move deprecated configs** (15 min)
   ```bash
   git mv config_legacy/ .codex/archive/legacy-configs/
   # Expect: ~5-10 files moved
   ```

2. ✓ **Consolidate single-file directories** (20 min)
   - Move related single files to parent directories or `misc/`
   - Example:
     ```bash
     git mv orphan_dir/file.txt misc/archived-orphans/
     # For each orphaned single-file dir
     ```

3. ✓ **Delete temporary artifacts** (10 min)
   ```bash
   # Only delete if NOT source-of-truth and NOT referenced
   git rm -r build-temp/ cache-temp/ __pycache__/ .pytest_cache/
   ```

4. ✓ **Commit: Orphan cleanup** (5 min)
   - Message: `phase-3-b: Clean up 50 orphaned directories and single-file artifacts`
   - Verify: Directory count reduction: `find . -maxdepth 1 -type d | wc -l` → expect ~20 fewer

**Output:** Orphaned structures cleaned up (1-2 commits)

---

## ⚙️ Phase 4: Config Consolidation (P2 Priority)

**Category:** D — Config Consolidation  
**Timeline:** Week 5, Days 1-4 (2-3 hours total)  
**Objective:** Consolidate 7 overlapping config roots to 2 canonical locations, audit legacy imports  
**Target:** 5 config directories eliminated, 2 canonical roots: `config/` + `.config/`

### Pre-Execution: Legacy Import Audit

**Tasks:**
1. ✓ **Audit all config imports** (20 min)
   ```bash
   grep -r "from config\|import config\|from configs\|import configs\|from conf\|import conf" \
     src/ tests/ --include="*.py" | \
   awk -F: '{print $2}' | sort | uniq -c | sort -rn
   # Expected: Track usage across config/, configs/, conf/, omegaconf/
   ```

2. ✓ **Identify canonical mapping** (15 min)
   - Mapping decision:
     - `config/` ← primary canonical (Python modules)
     - `.config/` ← secondary canonical (user configs, secrets, environment)
     - `configs/` → merge into `config/`
     - `conf/` → merge into `config/`
     - `omegaconf/` → reference external (Hydra, not consolidate)
     - `conftest.py` → pytest config (keep in src/tests/)

3. ✓ **Plan import rewriting** (10 min)
   ```bash
   # Track all imports that will change
   grep -r "from configs\|from conf import" src/ tests/ | wc -l
   # Expected: 10-30 imports to rewrite
   ```

### Day 1: Audit & Import Planning

**Tasks:**
1. ✓ **Create import rewriting plan** (20 min)
   - Document each file requiring import changes
   - Example mappings:
     ```
     from configs.app import AppConfig     → from config.app import AppConfig
     from conf.database import DbConfig    → from config.database import DbConfig
     from configurations import ...        → from config import ...
     ```

2. ✓ **Commit: Config consolidation plan** (5 min)
   - Message: `phase-4-a: Plan config consolidation (7 roots → 2 canonical, 10-30 imports to update)`

### Day 2: Merge Config Directories

**Tasks:**
1. ✓ **Move configs/ → config/** (15 min)
   ```bash
   # Move contents of configs/ into config/
   for file in configs/*; do
     [ -f "$file" ] && git mv "$file" config/"$(basename $file)"
   done
   # Remove empty configs/ directory
   git rm -r configs/
   ```

2. ✓ **Move conf/ → config/** (10 min)
   ```bash
   # Move contents of conf/ into config/
   for file in conf/*; do
     [ -f "$file" ] && git mv "$file" config/"$(basename $file)"
   done
   # Remove empty conf/ directory
   git rm -r conf/
   ```

3. ✓ **Organize .config/ for user configs** (10 min)
   - Move environment-specific configs to `.config/`:
     ```bash
     mkdir -p .config/environments
     git mv config/local.* .config/environments/ 2>/dev/null || true
     git mv config/dev.* .config/environments/ 2>/dev/null || true
     git mv config/prod.* .config/environments/ 2>/dev/null || true
     ```

4. ✓ **Commit: Config directory consolidation** (5 min)
   - Message: `phase-4-b: Consolidate config directories (configs/ + conf/ → config/)`
   - Verify: `ls -d config/ .config/ | wc -l` → expect 2

**Output:** Config directories merged (1 commit)

### Day 3: Update Imports

**Tasks:**
1. ✓ **Rewrite Python imports** (20 min)
   ```bash
   # Update all "from configs" → "from config"
   find src/ tests/ -name "*.py" -exec sed -i 's/from configs\./from config./g' {} \;
   find src/ tests/ -name "*.py" -exec sed -i 's/import configs\./import config./g' {} \;
   
   # Update all "from conf" → "from config" (except conftest)
   find src/ tests/ -name "*.py" -not -name "conftest.py" \
     -exec sed -i 's/from conf\./from config./g' {} \;
   ```

2. ✓ **Audit import changes** (10 min)
   ```bash
   git diff --name-only | grep ".py" | wc -l
   # Expected: 10-30 files modified
   git diff | grep "^[-+].*from config\|^[-+].*import config" | head -20
   # Verify imports updated correctly
   ```

3. ✓ **Commit: Import updates** (5 min)
   - Message: `phase-4-c: Update imports (configs/ conf/ → config/)`
   - Verify: `python -m py_compile src/**/*.py` → no import errors

### Day 4: Verification & Completion

**Tasks:**
1. ✓ **Run import tests** (15 min)
   ```bash
   pytest tests/ -k "test_config" -v
   # Expected: All config-related tests pass
   ```

2. ✓ **Verify no legacy imports remain** (10 min)
   ```bash
   grep -r "from configs\|from conf " src/ tests/ --include="*.py" | wc -l
   # Expected: 0 matches
   ```

3. ✓ **Clean up legacy roots** (10 min)
   ```bash
   # Verify config/, configs/, conf/ directory status
   ls -d config/ configs/ conf/ 2>/dev/null | wc -l
   # Expected: 1 (only config/ remains, unless custom modules)
   ```

4. ✓ **Standardize .gitignore for configs** (10 min)
   - Add patterns for local configs:
     ```
     # Config files
     .config/local/*
     .config/secrets/*
     config/.env.local
     config/.env.*.local
     ```

5. ✓ **Commit: Config consolidation complete** (5 min)
   - Message: `phase-4-d: Config consolidation complete (7 roots → 2 canonical, all imports updated)`

6. ✓ **Merge Phase 4 to main** (5 min)
   - Command: `git merge --no-ff cleanup/phase-4-config-consolidation`
   - Commit message: `Merge phase-4: Config consolidation complete`

**Output:** Config consolidation complete, all imports verified (1-2 commits)

---

## ✅ Phase Completion & WS3 Success Criteria

### Success Metrics

| Phase | Category | Expected Reduction | Commits | Status |
|-------|----------|-------------------|---------|--------|
| **Phase 1** | Venvs | 713 files, 50 MB | 1 | On Schedule |
| **Phase 2** | Reports + Root | 850 files | 3 | On Schedule |
| **Phase 3** | Orphans | 50 dirs, 20 files | 1-2 | On Schedule |
| **Phase 4** | Configs | 5 dirs eliminated | 2 | On Schedule |
| **TOTAL** | — | **~1,200 files** | **6-7 commits** | **On Track** |

### Final Validation Checklist

- [ ] Phase 1 complete: Venvs untracked, .gitignore hardened, 50 MB saved
- [ ] Phase 2 complete: Reports archived (`.codex/archive/phase-reports/`), root clutter consolidated (`.codex/reports/`)
- [ ] Phase 3 complete: Orphaned structures cleaned up, 50 directories consolidated
- [ ] Phase 4 complete: Config consolidated (7 → 2), all imports updated, legacy roots removed
- [ ] All 6-7 commits present and verified
- [ ] Total reduction: 17,100 → ~16,000 files (6.5% decrease)
- [ ] Zero broken links in documentation
- [ ] Zero import errors in codebase
- [ ] All safety gates passed

### Post-Phase Coordination

1. **Track 8.1 Integration:** Coordinate archival taxonomy sharing (`.codex/archive/phase-reports/` used by both 8.1 and 8.2)
2. **QA Walkthrough:** Update codebase_map.json with new directory structure (107 → 85 directories)
3. **CI/CD Updates:** Verify hardcoded paths in workflows updated to archive locations
4. **Documentation Refresh:** Rebase all references to archived phase reports

---

## 🚦 WS3 Execution Status

**Current Status:** ✅ Execution plan ready for @mbaetiong authorization  
**Timeline:** Weeks 2-5, Days 1-24  
**Resource Requirement:** Single operator, ~9-14 hours distributed execution  
**Risk Mitigation:** All 4 safety gates + rollback procedures in place

**Next Step:** Submit complete WS3 handoff package for go/no-go decision

---

**Maintained by:** Phase 8.2 Track 8.2 Workstream 2  
**Version:** 1.0.0  
**Last Updated:** 2026-07-03
