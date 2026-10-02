# 🗂️ Track 8.2 WS3 Execution Brief — Repository Cleanup & Directory Standardization

**Authority:** @mbaetiong (D-tier autonomous, GO CONTINUE)  
**Priority:** 🟡 **THIRD** (after Tracks 8.3 + 8.1 complete)  
**Timeline:** 2026-07-08T09:00Z → 2026-07-08T18:00Z (9-hour execution window, coordinated post-8.1)  
**Status:** Ready for execution upon Track 8.1 completion

---

## 📋 Executive Summary

Track 8.2 executes a phased cleanup strategy to remove temporary artifacts, standardize directory structure, and enforce final repository hygiene standards. This work depends on Tracks 8.3 (filenames stable) and 8.1 (doc structure final) to avoid rework.

**Key Deliverables:**
- ✅ Venv cleanup (remove stale virtual environments)
- ✅ Report cleanup (archive/delete temporary build reports)
- ✅ Root cleanup (organize root-level files per standards)
- ✅ `.codex/` standardization (final structure audit)
- ✅ Repository cleanup manifest created

---

## 🎯 Execution Objective

**Primary Goal:** Execute 4-day cleanup phased roadmap (from CLEANUP_PHASES.md) to standardize repository structure and remove technical debt.

**Success Criteria:**
- ✅ All venv cleanup phases completed
- ✅ Report artifacts archived or deleted per retention policy
- ✅ Root directory reorganized per DIRECTORY_STANDARDS.md
- ✅ `.codex/` directory structure finalized
- ✅ Repository size reduced by 10-20% (target: <2 GB)
- ✅ Cleanup manifest created documenting all changes

---

## 📊 Planning Reference Documents

**Primary Sources:**
- `.codex/PHASE_8_2_CLEANUP_STRATEGY.md` (17.5 KB, phased cleanup approach)
- `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md` (19.6 KB, final repo structure design)
- `.codex/PHASE_8_2_CLEANUP_PHASES.md` (21.8 KB, Days 1-4 execution schedule)

**Supporting Docs:**
- `.codex/PHASE_8_2_ROUTING_RULES.json` (file disposition rules)
- `.codex/PHASE_8_2_TRIAGE_DASHBOARD.md` (decision tree)

---

## 🚀 Execution Workflow (Agent Handoff)

### Agent Assignment
**Primary Agents:** `unified-governance-gate` + `repository-hygiene-agent`  
**Supporting Agents:** `root-organizer-agent`, `reference-updater-agent`

### Workflow Steps

#### Step 1: Load Cleanup Planning (15 min)
1. Read CLEANUP_STRATEGY.md for cleanup philosophy and phases
2. Read CLEANUP_PHASES.md for Days 1-4 detailed schedule
3. Read DIRECTORY_STANDARDS.md for final structure specification
4. Load ROUTING_RULES.json for file disposition decisions

#### Step 2: Phase 1 — Virtual Environment Cleanup (Day 1, 90 min)
**Target:** Remove stale Python virtual environments

**Actions:**
```bash
# Find all venv directories
find . -maxdepth 3 -name "venv" -o -name ".venv" -o -name "env" | grep -v node_modules

# Identify candidates for deletion (older than 30 days)
find . -maxdepth 3 -name "venv" -type d -mtime +30

# Document before deletion
ls -la [venv_path] > .codex/cleanup_manifest_phase1.txt

# Remove identified venv directories
rm -rf [venv_path]
```

**Validation:**
```bash
# Verify no venv directories remain
find . -maxdepth 3 \( -name "venv" -o -name ".venv" \) -type d | wc -l
# Should be 0
```

**Success Criteria for Phase 1:**
- [ ] All stale venv directories identified
- [ ] Pre-deletion inventory documented
- [ ] All targeted venvs deleted
- [ ] Disk space freed: estimated 500 MB - 1 GB

#### Step 3: Phase 2 — Report Cleanup (Day 2, 120 min)
**Target:** Archive or delete temporary build/test reports

**From CLEANUP_STRATEGY.md, identify:**
- Old test reports (>30 days old)
- Temporary CI logs (>7 days old)
- Build artifacts (>14 days old)
- Temporary data files (>90 days old)

**Actions:**
```bash
# Archive old reports to separate directory
mkdir -p .codex/archives/reports/
find . -name "*_report*.json" -mtime +30 -exec mv {} .codex/archives/reports/ \;
find . -name "*_report*.txt" -mtime +30 -exec mv {} .codex/archives/reports/ \;

# Delete temporary CI logs
find .codex -name "*_ci_log*.txt" -mtime +7 -delete

# Document cleanup
git add .codex/archives/
echo "Phase 2: Report cleanup completed $(date)" >> .codex/cleanup_manifest_phase2.txt
```

**Validation:**
```bash
# Verify archived reports are accessible
ls -la .codex/archives/reports/ | wc -l
# Should be 10-50 files

# Verify temporary logs deleted
find . -name "*_ci_log*.txt" | wc -l
# Should be 0
```

**Success Criteria for Phase 2:**
- [ ] Old reports archived to .codex/archives/
- [ ] Temporary CI logs deleted
- [ ] Build artifacts archived
- [ ] Cleanup documented with before/after counts

#### Step 4: Phase 3 — Root Directory Reorganization (Day 3, 90 min)
**Target:** Reorganize root-level files per DIRECTORY_STANDARDS.md

**From DIRECTORY_STANDARDS.md, expected root structure:**
```
_codex_/
├── .codex/              # All automation artifacts
├── .github/             # Workflows (no changes)
├── docs/                # Documentation (finalized by Track 8.1)
├── scripts/             # CLI scripts
├── src/                 # Source code
├── tests/               # Test files
├── pyproject.toml       # Python config
├── README.md            # Repository root doc
├── LICENSE              # License file
├── CONTRIBUTING.md      # Contributing guide
└── [deprecated files]   # To be archived
```

**Actions:**
```bash
# Identify root-level files needing reorganization
ls -la / | grep -E "\.(md|txt|json)$" | grep -v "^d"

# Per DIRECTORY_STANDARDS.md, move files to appropriate location
# Example: Move deprecated readme to docs/archive/
mkdir -p docs/archive/
mv OLD_README.md docs/archive/

# Update top-level references if moved
grep -r "OLD_README" . --include="*.md" | grep -v ".codex/" | grep -v "docs/archive/"
# Update references to point to new location
```

**Validation:**
```bash
# Verify structure matches DIRECTORY_STANDARDS.md
find . -maxdepth 1 -type f -name "*.md" | wc -l
# Should match specification (expect 4-5 root .md files)

# Verify no orphaned files
ls -la | grep -E "^-" | wc -l
# Should be minimal (LICENSE, README.md, maybe .gitignore variants)
```

**Success Criteria for Phase 3:**
- [ ] Root directory organized per standards
- [ ] Deprecated files archived or moved
- [ ] Cross-references updated
- [ ] Directory structure validated

#### Step 5: Phase 4 — `.codex/` Standardization (Day 4, 60 min)
**Target:** Final `.codex/` directory structure audit and consolidation

**Actions:**
```bash
# From DIRECTORY_STANDARDS.md, verify .codex/ structure
# Expected categories:
# - Phase 8 planning docs (finalized, keep)
# - Execution reports (keep, archive if >30 days old)
# - Temporary agent outputs (delete if >14 days old)
# - Build artifacts (move to .codex/archives/)

# Identify orphaned files
find .codex/ -type f -mtime +30 | head -20

# Archive temporary agent outputs
mkdir -p .codex/archives/temp_outputs/
find .codex -name "*_temp_*.json" -mtime +7 -exec mv {} .codex/archives/temp_outputs/ \;

# Remove obviously temporary files (*.tmp, *.bak)
find .codex -name "*.tmp" -delete
find .codex -name "*.bak" -delete
```

**Validation:**
```bash
# Verify .codex/ structure
ls -la .codex/ | grep "^d" | awk '{print $NF}' | sort

# Count files per category
echo "Phase execution reports:" && find .codex -name "PHASE_8_*_COMPLETION*.md" | wc -l
echo "Planning docs:" && find .codex -name "PHASE_8_*_STRATEGY.md" | wc -l
echo "Archived items:" && find .codex/archives -type f | wc -l
```

**Success Criteria for Phase 4:**
- [ ] `.codex/` structure standardized
- [ ] Temporary files archived or deleted
- [ ] Phase planning docs preserved
- [ ] Final structure matches DIRECTORY_STANDARDS.md

#### Step 6: Create Cleanup Manifest & Commit (30 min)
1. Consolidate all phase manifests into unified document
2. Calculate disk space freed
3. Create summary report

**File: `.codex/PHASE_8_2_CLEANUP_MANIFEST_FINAL.md`**
```markdown
# Cleanup Execution Manifest — Phase 8.2 WS3

**Execution Date:** 2026-07-08
**Total Execution Time:** 6 hours
**Authority:** @mbaetiong (D-tier autonomous)

## Phase Summary
- **Phase 1 (Venv):** X venvs removed, Y GB freed
- **Phase 2 (Reports):** X reports archived, Y deleted
- **Phase 3 (Root):** X files reorganized
- **Phase 4 (.codex/):** X files archived, Y cleaned

## Disk Space Impact
- Before: [SIZE_BEFORE]
- After: [SIZE_AFTER]
- Freed: [SIZE_FREED] (target: 10-20%)

## Files Changed
- Deleted: X files
- Moved/Archived: Y files
- Modified: Z files

## Final Directory Structure
✅ Matches DIRECTORY_STANDARDS.md specification
```

**Commit:**
```bash
git add .codex/PHASE_8_2_CLEANUP_MANIFEST_FINAL.md
git add .codex/archives/
git commit -m "refactor(cleanup): Phase 8.2 WS3 cleanup complete — venv/reports/root reorganization"
```

---

## 📋 Success Checklist

- [ ] Phase 1 (Venv): All stale venvs identified and removed
- [ ] Phase 2 (Reports): Old reports archived, CI logs deleted
- [ ] Phase 3 (Root): Root directory reorganized per standards
- [ ] Phase 4 (.codex/): Temporary files archived, structure standardized
- [ ] `.codex/PHASE_8_2_CLEANUP_MANIFEST_FINAL.md` created
- [ ] Disk space freed: 10-20% of original size
- [ ] Final structure validated against DIRECTORY_STANDARDS.md
- [ ] Single cleanup commit created with manifest

---

## ⚠️ Risk Mitigation

**Potential Issues:**
1. **Accidental deletion** — Use `git mv` for all reorganization; deletions only via `rm` with pre-deletion manifest
2. **Breaking references** — Update all cross-references before/after moving files
3. **Disk space calculations** — Use `du -sh` before/after each phase

**Rollback Plan (if needed):**
```bash
git reset --hard HEAD~5  # Revert cleanup phases
git clean -fd           # Remove orphaned files
# Restart with conservative scope (Phase 1 venv only)
```

---

## 🔄 Dependency Management

**REQUIRES COMPLETION OF:** Tracks 8.3 (filenames stable) + 8.1 (doc structure final)
- Reason: Cleanup must not interfere with active work

**PARALLEL WITH:** Track 8.4 (dependency standardization) — independent
- Reason: Different scope (venv/reports vs. dependencies)

**BEFORE:** Track 8.4 completion (if any dependency artifacts in root)
- Handoff: "Track 8.2 WS3 COMPLETE — repository structure standardized"

---

## 📊 Metrics & Reporting

**Expected Outputs:**
- Disk space freed: 500 MB - 2 GB (target 10-20%)
- Files removed/archived: 50-100+
- Phases executed: 4 of 4
- Execution time: 6-9 hours
- Completion time: 2026-07-08T17:00Z (estimated)

**Success Criteria Met When:**
- Cleanup manifest committed
- Directory structure validated
- Disk space target achieved
- All cross-references updated

---

## 🎯 Next Phase Handoff

**Upon Completion:**
1. Reply with execution summary
2. Include commit SHA: `git rev-parse HEAD`
3. Post status: "Track 8.2 WS3 COMPLETE — Repository structure standardized"
4. Include disk space freed and directory structure summary

**Expected Reply Format:**
```markdown
## Track 8.2 Execution Summary
- Phases Executed: 4 of 4
- Venvs Removed: X
- Reports Archived: Y
- Disk Space Freed: Z GB (10-20% target)
- Execution Time: N hours
- Commit SHA: [SHA]
- Status: ✅ COMPLETE / ⚠️ PARTIAL / ❌ ISSUES
- Directory Structure: ✅ Validated
- Ready for WS4: [YES / NO]
```

---

## 📞 Support & Escalation

**If stuck on:**
- Reference broken after move → Search for old path, update all references
- Disk space freed < target → Check for large temporary files in .codex/
- Orphaned files → Refer to ROUTING_RULES.json for disposition decision

**Escalation Point:**
- If cleanup would impact active workflows → Stop, document impact, escalate
- Authority: D-tier autonomous (GO CONTINUE unless escalation needed)

---

**Authority:** @mbaetiong D-tier autonomous  
**Entry Point:** `.codex/PHASE_8_WS2_SESSION_CONSOLIDATION_HANDOFF.md`  
**Status:** 🟢 **READY FOR AGENT ACTIVATION** (post-Track-8.1)
