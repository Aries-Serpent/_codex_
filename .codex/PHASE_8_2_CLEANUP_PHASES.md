# Phase 8 Track 8.2 WS2: Cleanup Execution Plan (PHASE_8_2_CLEANUP_PHASES.md)

**Document Version**: 1.0  
**Date**: 2026-01-26  
**Status**: Draft - Planning Phase  
**Audience**: Phase 8.2 Track 8.2 Execution Team (WS 8.2.3)

---

## Overview

This document provides **batch-by-batch execution procedures** for Phase 8.2 Track 8.2's cleanup strategy. It complements the strategic decisions in `PHASE_8_2_CLEANUP_STRATEGY.md` with concrete commands, validation steps, rollback procedures, and success criteria for each batch.

**Key References**:
- Strategy document: `.codex/PHASE_8_2_CLEANUP_STRATEGY.md`
- Directory standards (validation): `.codex/PHASE_8_2_DIRECTORY_STANDARDS.md`
- Structural audit (baseline): `.codex/PHASE_8_2_STRUCTURE_AUDIT.md`

---

## Batch Execution Sequence

### Batch 0: Virtual Environment Cleanup (~715 files, HIGHEST PRIORITY)

**Risk Level**: ✅ LOW (regenerable, zero code impact)  
**Dependencies**: None  
**Duration**: ~15 minutes  
**Target Reduction**: 715 files to gitignore

#### Batch 0.0: Identify venv Directories

**Command**:
```bash
find . -type d -name "__pycache__" -o \
    -type d -name "*.egg-info" -o \
    -type d -name ".pytest_cache" -o \
    -type d -name ".mypy_cache" -o \
    -type d -name "venv*" -o \
    -type d -name ".venv*" | head -20
```

**Expected Output**: List of 15-20 venv-related directories

**Files to Remove**:
- `venv_test/` — entire directory
- `.venv*/` patterns in project root
- Python cache directories: `__pycache__`, `*.egg-info`, `.pytest_cache`, `.mypy_cache`

#### Batch 0.1: Add .gitignore Rules

**Edit `.gitignore`** to include:
```gitignore
# Virtual environments
venv/
venv_*/
.venv/
.venv_*/
env/
env_*/

# Python build artifacts
*.egg-info/
dist/
build/

# Cache directories
__pycache__/
.pytest_cache/
.mypy_cache/
.coverage
*.pyc
*.pyo
```

#### Batch 0.2: Remove from Git Tracking

**Command**:
```bash
git rm -r venv_test/
git rm -r .venv* 2>/dev/null || true
git rm -r __pycache__ 2>/dev/null || true
git rm -r .pytest_cache 2>/dev/null || true
git rm -r .mypy_cache 2>/dev/null || true
git rm -r *.egg-info 2>/dev/null || true
```

**Commit**:
```bash
git commit -m "cleanup(batch-0): Remove virtual environment directories (~715 files)"
```

#### Batch 0.3: Regeneration Verification

**Post-Cleanup**:
```bash
# Regenerate venv if needed
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

**Validation**: Confirm code runs normally with fresh venv

---

### Batch 1: Build Artifacts & Temporary Outputs (~150 files)

**Risk Level**: ✅ LOW (regenerable from CI)  
**Dependencies**: None  
**Duration**: ~10 minutes  
**Target Reduction**: 150 files to gitignore or archive

#### Batch 1.0: Identify Artifact Directories

**Command**:
```bash
ls -la | grep -E "^d.*coverage|^d.*build|^d.*dist|^d.*tmp|^d.*artifact"
find . -maxdepth 2 -type d \( \
    -name "coverage*" -o \
    -name "build" -o \
    -name "dist" -o \
    -name "artifacts" -o \
    -name "tmp*" \) 2>/dev/null
```

**Expected**: `coverage_reports/`, `coverage.json`, build artifacts, test outputs

#### Batch 1.1: Archive or Remove

**Option A - Archive (Recommended)**:
```bash
mkdir -p .codex/archive/artifacts/coverage
mv coverage_reports/* .codex/archive/artifacts/coverage/
mv coverage.json .codex/archive/artifacts/coverage/
echo "Archived $(ls -1 .codex/archive/artifacts/coverage | wc -l) files"
```

**Option B - Add to .gitignore**:
```gitignore
# Build artifacts
build/
dist/
coverage/
coverage_reports/
coverage.json
*.coverage
htmlcov/
```

#### Batch 1.2: Commit

```bash
git add .gitignore
if [ -d ".codex/archive/artifacts" ]; then
    git add .codex/archive/artifacts/
    git commit -m "cleanup(batch-1): Archive build artifacts and coverage reports (~150 files)"
else
    git commit -m "cleanup(batch-1): Ignore build artifacts and coverage reports (~150 files)"
fi
```

---

### Batch 2: Root Directory Declutter (~114 files)

**Risk Level**: 🟡 MEDIUM (requires path validation, must complete BEFORE Batch 3)  
**Dependencies**: None (but must precede Batch 3 & Track 8.3)  
**Duration**: ~30 minutes  
**Target Reduction**: 114 files organized into 7 categories

#### Batch 2.0: Inventory Root Files

**Command**:
```bash
ls -la | grep "^-" | awk '{print $NF}' | head -30
```

**Expected**: Files like `CHANGELOG.md`, `PHASE_*.md`, `README.md`, etc.

#### Batch 2.1: Create Archive Categories

```bash
mkdir -p .codex/archive/root-consolidation/{phase-history,deprecated-reports,temp-outputs,root-docs}
```

#### Batch 2.2: Move Phase History Files

**Files to move**:
- `PHASE_*.md` (26+ files)
- `GATE_*.md` (4+ files)
- `*_COMPLETION*.md` (3+ files)
- `*_SUMMARY*.md` (5+ files)
- `*_REPORT*.md` (8+ files)

**Commands**:
```bash
# Phase history
git mv PHASE_*.md .codex/archive/root-consolidation/phase-history/
git mv GATE_*.md .codex/archive/root-consolidation/phase-history/
git mv *_COMPLETION*.md .codex/archive/root-consolidation/phase-history/
git mv *_SUMMARY*.md .codex/archive/root-consolidation/phase-history/
git mv *_REPORT*.md .codex/archive/root-consolidation/phase-history/
```

#### Batch 2.3: Move Deprecated/Temporary Files

**Files to move**:
- `*_DEPRECATED*.md`
- `*_LEGACY*.md`
- `CONVERSATION_SUMMARY*.md`
- `*_VALIDATION_*.md` (non-current)

**Commands**:
```bash
git mv *_DEPRECATED*.md .codex/archive/root-consolidation/deprecated-reports/ 2>/dev/null || true
git mv *_LEGACY*.md .codex/archive/root-consolidation/deprecated-reports/ 2>/dev/null || true
git mv CONVERSATION_SUMMARY*.md .codex/archive/root-consolidation/temp-outputs/ 2>/dev/null || true
```

#### Batch 2.4: Validation - Reference Check

**Before committing**, validate no code depends on these paths:

```bash
# Check for hardcoded references
grep -r "PHASE_.*\.md" src/ tests/ --exclude-dir=.git 2>/dev/null || echo "✓ No code refs to PHASE_*.md"
grep -r "GATE_.*\.md" src/ tests/ --exclude-dir=.git 2>/dev/null || echo "✓ No code refs to GATE_*.md"

# Check GitHub Actions references
grep -r "PHASE_.*\.md" .github/workflows/ 2>/dev/null || echo "✓ No workflow refs"
```

**Expected Result**: No matches (all references should be safe to move)

#### Batch 2.5: Create Root Archive Index

**File**: `.codex/archive/root-consolidation/INDEX.md`

```markdown
# Root Consolidation Archive Index

## Phase History (26+ files)
- `PHASE_*.md` — Phase tracking documents
- `GATE_*.md` — Gate completion reports
- Completion, summary, report files

## Deprecated Reports (8+ files)
- Deprecated analysis files
- Legacy implementation guides

## Temp Outputs (5+ files)
- Conversation summaries
- Temporary validation files

## Root Docs (10+ files)
- CITATION.cff
- SECURITY.md, CODE_OF_CONDUCT.md
- CHANGELOG.md (keep in root)

**Total**: 114 files organized
**Retrieval**: Use `git log --follow .codex/archive/root-consolidation/`
```

#### Batch 2.6: Commit

```bash
git add .codex/archive/root-consolidation/
git commit -m "cleanup(batch-2): Declutter root directory, move phase history & reports to archive (~114 files)"
```

#### Batch 2.7: Rollback Procedure

```bash
# If issues found, revert the batch
git revert HEAD --no-edit
# Files restore automatically via git history
```

---

### Batch 3: Phase Reports Consolidation (866 files - LARGEST)

**Risk Level**: 🟡 MEDIUM (large batch, but files are immutable reports)  
**Dependencies**: Batch 2 MUST complete first (shares archive directory)  
**Duration**: ~45 minutes  
**Target Reduction**: 866 phase report files organized in nested archive

#### Batch 3.0: Audit Phase Report Structure

**Command**:
```bash
find . -path "./.*" -prune -o -type f -name "*PHASE*REPORT*" -print | head -20
ls -la PHASE*_*.md | wc -l
```

**Expected**: 866+ report files across multiple PHASE directories

#### Batch 3.1: Create Nested Archive Structure

```bash
mkdir -p .codex/archive/phase-reports/{discovery,analysis,execution,validation}
# Optional: Create per-phase subdirs
mkdir -p .codex/archive/phase-reports/{phase-1-10,phase-11-20,phase-21-30}
```

#### Batch 3.2: Move Phase Reports

**Recommended**: Organize by phase range to keep archive navigable

```bash
# Move Phase 1-10 reports
git mv PHASE_{1..10}*.md .codex/archive/phase-reports/phase-1-10/ 2>/dev/null || true

# Move Phase 11-20 reports
git mv PHASE_{11..20}*.md .codex/archive/phase-reports/phase-11-20/ 2>/dev/null || true

# Move Phase 21+ reports
git mv PHASE_{21..30}*.md .codex/archive/phase-reports/phase-21-30/ 2>/dev/null || true

# Move generic phase reports
git mv PHASE_*_REPORT*.md .codex/archive/phase-reports/ 2>/dev/null || true
```

#### Batch 3.3: Generate NDJSON Archive Inventory

**File**: `.codex/archive/phase-reports/INVENTORY.ndjson`

**Format** (one JSON object per line):
```ndjson
{"original_path": "PHASE_1_REPORT.md", "archive_path": "phase-reports/phase-1-10/PHASE_1_REPORT.md", "category": "discovery", "phase": 1, "type": "report", "commit": "<hash>"}
{"original_path": "PHASE_2_ANALYSIS.md", "archive_path": "phase-reports/phase-1-10/PHASE_2_ANALYSIS.md", "category": "analysis", "phase": 2, "type": "analysis", "commit": "<hash>"}
```

**Generation**:
```bash
# Bash script to generate INVENTORY.ndjson
cat > .codex/archive/phase-reports/generate-inventory.sh << 'EOF'
#!/bin/bash
cd "$(dirname "$0")"
> INVENTORY.ndjson
find . -type f -name "*.md" | while read file; do
    original=$(basename "$file")
    archive_path="phase-reports/${file#./}"
    category=$(echo "$file" | grep -oE "(discovery|analysis|execution|validation|report)" | head -1 || echo "report")
    phase=$(echo "$file" | grep -oE "PHASE_[0-9]+" | grep -oE "[0-9]+" || echo "0")
    commit=$(git rev-parse HEAD 2>/dev/null || echo "pending")
    echo "{\"original_path\": \"$original\", \"archive_path\": \"$archive_path\", \"category\": \"$category\", \"phase\": $phase, \"type\": \"report\", \"commit\": \"$commit\"}" >> INVENTORY.ndjson
done
EOF
chmod +x .codex/archive/phase-reports/generate-inventory.sh
./.codex/archive/phase-reports/generate-inventory.sh
```

#### Batch 3.4: Create Retrieval Guide

**File**: `.codex/archive/phase-reports/RETRIEVAL_GUIDE.md`

```markdown
# Phase Reports Retrieval Guide

## Quick Search

### By Phase Number
```bash
jq 'select(.phase == 5)' < INVENTORY.ndjson
```

### By Category
```bash
jq 'select(.category == "discovery")' < INVENTORY.ndjson
```

### By File Pattern
```bash
grep "COMPLETION" INVENTORY.ndjson | jq '.archive_path'
```

## Restoration

To restore a specific phase report:
```bash
jq -r 'select(.original_path == "PHASE_5_REPORT.md") | .archive_path' < INVENTORY.ndjson | xargs -I {} git mv {} "$PWD/{}"
```

## Archive Statistics
- Total files: 866
- Date archived: [TIMESTAMP]
- Archive size: ~[SIZE]MB
- Retention policy: Permanent (reference only)

## See Also
- `PHASE_8_2_CLEANUP_STRATEGY.md` — rationale for archival
- `PHASE_8_2_DIRECTORY_STANDARDS.md` — archive retention policies
```

#### Batch 3.5: Commit

```bash
git add .codex/archive/phase-reports/
git commit -m "cleanup(batch-3): Archive phase reports to nested directory structure with NDJSON index (866 files)"
```

#### Batch 3.6: Rollback Procedure

```bash
# Full rollback: revert the batch
git revert HEAD --no-edit

# Selective rollback: restore specific phase range
git mv .codex/archive/phase-reports/phase-1-10/* .
git commit -m "cleanup(batch-3-rollback): Restore phase-1-10 reports"
```

---

### Batch 4: Legacy Configuration Consolidation (~15 config dirs, deferred)

**Risk Level**: 🔴 HIGHER (requires import validation, Track 8.3 must complete first)  
**Dependencies**: 
  - ✅ Batch 0, 1, 2, 3 must complete
  - ⏳ **Track 8.3 (case-collision fixes) must complete BEFORE executing Batch 4**
**Duration**: ~60 minutes  
**Target Reduction**: 7 config roots → 2 active + 1 archive

**STATUS**: ⏸️ DEFERRED — Execute after Track 8.3 completion

#### Batch 4.0: Pre-Execution Validation (when Track 8.3 is complete)

**Reference Checks**:
```bash
# Identify all imports of legacy config roots
grep -r "from yaml_legacy import\|from config_legacy import" src/ tests/ 2>/dev/null | tee config-refs.log

# Check action logs for dynamic config loading
grep "config_legacy\|yaml_legacy" .codex/action_log.ndjson 2>/dev/null | jq '.event' | sort -u

# Check agent references
grep -r "yaml_legacy\|config_legacy" agents/ 2>/dev/null | tee agent-config-refs.log
```

**Decision Gate**:
- If 0 references found → proceed with archival
- If > 5 references → escalate to Phase Lead (may require code refactor first)
- If 1-5 references → create refactor PRs in Track 8.1 before archival

#### Batch 4.1: Create Consolidation Plan

**File**: `.codex/archive/config-legacy/CONSOLIDATION_PLAN.md`

```markdown
# Config Consolidation Plan (Batch 4)

## Legacy Roots Identified (7 total)

| Root | Files | Status | Target |
|------|-------|--------|--------|
| `configs/` | ~40 | ACTIVE | Keep |
| `conf/` | ~15 | ACTIVE | Keep |
| `omegaconf/` | 1 | Stub | Archive |
| `yaml_legacy/` | 1 | Legacy | Archive |
| `config_legacy/` | ~8 | Legacy | Archive |
| `conftest.py` (root) | 1 | Pytest | Keep |
| `pyproject.toml` (root) | 1 | Active | Keep |

**Consolidation Target**: `configs/` as primary, `conf/` as secondary

## Pre-Execution Reference Validation

Completed: [YES/NO]
- [ ] Checked codebase for hardcoded imports
- [ ] Checked agents for dynamic config loading
- [ ] Checked action logs for config references
- [ ] Validated Track 8.3 completion (case fixes)
- [ ] All references either updated or plan created

**References Found**: [N]
**Refactor PRs**: [List]

## Archive Structure

```
.codex/archive/config-legacy/
├── yaml_legacy/          # Archived legacy YAML configs
├── config_legacy/        # Archived legacy config modules
├── omegaconf_stub/       # Single-file stub (reference only)
├── CONSOLIDATION_PLAN.md
├── MIGRATION_GUIDE.md    # How to update code to use configs/
└── INVENTORY.md
```

## Migration Path

For code currently importing from legacy roots:
```python
# Before
from yaml_legacy import load_config

# After (use primary config root)
from configs import load_config
```
```

#### Batch 4.2: Archive Legacy Configs

```bash
mkdir -p .codex/archive/config-legacy/{yaml_legacy,config_legacy,stubs}

# Move legacy YAML configs
git mv yaml_legacy/* .codex/archive/config-legacy/yaml_legacy/ 2>/dev/null || true

# Move legacy config modules
git mv config_legacy/* .codex/archive/config-legacy/config_legacy/ 2>/dev/null || true

# Move single-file stubs
git mv omegaconf .codex/archive/config-legacy/stubs/omegaconf_stub.txt 2>/dev/null || true
```

#### Batch 4.3: Commit

```bash
git add .codex/archive/config-legacy/
git commit -m "cleanup(batch-4): Consolidate legacy configs to archive after Track 8.3 completion (~15 files)"
```

**NOTE**: Do NOT execute until Track 8.3 case-collision work is complete to avoid directory churn.

---

## Post-Cleanup Validation Checklist

**After all batches complete**, validate against `PHASE_8_2_DIRECTORY_STANDARDS.md`:

### File Count Reduction

```bash
# Current state
git ls-files | wc -l  # Should be <= 12,000 (target from ~17,100)

# Archive preservation
find .codex/archive -type f | wc -l  # Should match ~1,000+ archived files
```

**Success Criteria**:
- ✅ File count: >= 4,000 reduction (30% minimum)
- ✅ Root directory: <= 40 top-level files (down from 114)
- ✅ Config roots: 2 active + 1 archive (down from 7)

### Directory Structure Validation

```bash
# Verify archive taxonomy
ls -la .codex/archive/
# Expected: phase-reports/, root-consolidation/, artifacts/, config-legacy/

# Verify .gitignore applied
git check-ignore venv_test/ coverage_reports/ 2>/dev/null && echo "✓ Ignores applied"

# Verify no dangling symlinks
find . -type l -exec test ! -e {} \; -print | head -5
```

### Archive Inventory Completeness

```bash
# Verify NDJSON indexes exist
ls -la .codex/archive/*/INVENTORY.ndjson 2>/dev/null || echo "⚠ Some inventories missing"

# Sample inventory records
jq '.[0]' .codex/archive/phase-reports/INVENTORY.ndjson
```

### Git History Integrity

```bash
# Verify all moves tracked as renames (not delete+create)
git log --raw --diff-filter=R -- .codex/archive/ | head -10

# Verify git log --follow works on moved files
git log --follow .codex/archive/phase-reports/phase-1-10/PHASE_1_REPORT.md | head -5
```

### Reference Validation

```bash
# Confirm no broken references to archived files
grep -r "\.codex/PHASE_.*\.md" src/ tests/ 2>/dev/null | head -3

# Search for hardcoded paths to moved files
grep -r "PHASE_.*REPORT\.md" . --exclude-dir=.git --exclude-dir=.codex 2>/dev/null | head -3
```

**Success**: All checks pass with no broken references

---

## Rollback Procedures

### Per-Batch Rollback

Each batch can be rolled back independently:

```bash
# Rollback Batch 0 (venvs)
git revert <batch-0-commit-hash>

# Rollback Batch 2 (root declutter)
git revert <batch-2-commit-hash>

# Rollback all batches (if needed)
git revert <batch-0-hash>^..<batch-4-hash>
```

### Full Cleanup Rollback

If cleanup causes unexpected issues:

```bash
# Find cleanup commit range
git log --oneline | grep "cleanup(batch"

# Revert entire cleanup series
git revert <oldest-cleanup-hash>^..<newest-cleanup-hash>

# Verify restoration
git ls-files | wc -l  # Should return to ~17,100
ls PHASE_*.md | wc -l  # Phase reports should reappear in root
```

### Git History Preservation

All moves are tracked via `git mv`, so:
- `git log --follow <file>` works for moved files
- `git blame <file>` traces back across moves
- `git show <commit>:<old-path>` recovers moved file content

---

## Monitoring & Metrics

### Track Progress

| Batch | Status | Files | Commit Hash | Date |
|-------|--------|-------|-------------|------|
| 0 (venvs) | ⏳ Pending | ~715 | — | — |
| 1 (artifacts) | ⏳ Pending | ~150 | — | — |
| 2 (root) | ⏳ Pending | ~114 | — | — |
| 3 (phase reports) | ⏳ Pending | ~866 | — | — |
| 4 (config legacy) | ⏸️ Deferred | ~15 | — | (After Track 8.3) |

### Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Total file reduction | >= 4,000 files (30%) | — |
| Root files | <= 40 | — |
| Config roots | 2 active + 1 archive | — |
| Archive inventory | 100% completeness | — |
| Git history | 100% preserved | — |
| Broken references | 0 | — |

---

## Cross-Track Coordination

### Track 8.1 (Documentation Consolidation)

**Shared Archive**: `.codex/archive/`  
**Coordination Point**: Batch 2 (root declutter) creates phase history archive  
**Handoff**: Phase 8.2 pass root declutter results to 8.1 before starting Batch 3

**Expected Overlap**:
- Both tracks may archive phase reports
- Use unified NDJSON inventory to dedup

### Track 8.3 (Case-Collision Resolution)

**Dependency**: Batch 4 (config consolidation) must wait for Track 8.3 completion  
**Why**: Batch 4 moves config directories; 8.3 renames for case consistency  
**Coordination**: 
1. Complete Batches 0-3 now
2. Hand off completion status to Track 8.3
3. Execute Batch 4 only after Track 8.3 completes
4. Validate case consistency in `.codex/archive/` directories

---

## Summary & Timeline

| Phase | Batches | Duration | Risk | Go/No-Go |
|-------|---------|----------|------|----------|
| **Immediate** | 0, 1 | ~25 min | ✅ LOW | 🟢 GO |
| **Near-term** | 2, 3 | ~75 min | 🟡 MED | 🟢 GO (after 0,1) |
| **Deferred** | 4 | ~60 min | 🔴 HIGH | ⏸️ After Track 8.3 |

**Estimated Total Duration**: ~2 hours (Batches 0-3), + Batch 4 TBD  
**Target Completion**: Phase 8.2 WS2.3 (execution phase)

---

**Document Status**: ✅ Complete  
**Next Step**: Execute Batch 0 & 1 (venvs + artifacts) with Phase Lead approval  
**Maintained by**: Phase 8.2 Track 8.2 Execution Team
