# PHASE 5.1: REPOSITORY CLEANUP CHECKLIST

**Campaign:** Phase 3-5 Multi-Agent Deployment  
**Track:** Phase 5 (Repository Organization)  
**Agent:** Repository Hygiene Agent  
**Date:** July 3, 2026  

---

## OVERVIEW

This checklist provides step-by-step guidance for cleaning up the _codex_ repository based on Phase 5.1 hygiene audit findings. Tasks are organized by priority and risk level.

---

## PRIORITY 1: CRITICAL CLEANUP (Do First - Minimal Risk)

### Task 1.1: Remove Compiled Python Bytecode
**Risk Level:** 🟢 LOW  
**Time Estimate:** 5-10 minutes  
**Status:** [ ] Ready to Execute

**Scope:**
- 38 .pyc files across 14 __pycache__ directories
- Total size: 421.5 KB
- Safe to delete (auto-regenerated on import)

**Steps:**
```bash
# Step 1: Verify __pycache__ directories exist
find . -type d -name __pycache__ | wc -l
# Expected: 14

# Step 2: Remove all __pycache__ directories
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# Step 3: Verify removal
find . -type d -name __pycache__ | wc -l
# Expected: 0

# Step 4: Verify .pyc files are gone
find . -name "*.pyc" -type f | wc -l
# Expected: 0
```

**Validation:**
- [ ] All __pycache__ directories removed
- [ ] No .pyc files remaining
- [ ] Import tests pass (python -c "import codex")
- [ ] No functional impact

**Commit Message:**
```
build(cleanup): Remove 38 compiled Python bytecode files

- Delete 14 __pycache__ directories (421.5 KB)
- .pyc files are auto-generated and should not be in repo
- Already covered by .gitignore
- Refs: Phase 5.1 Hygiene Audit
```

---

### Task 1.2: Remove Backup Files
**Risk Level:** 🟢 LOW  
**Time Estimate:** 5 minutes  
**Status:** [ ] Ready to Execute

**Files to Remove:**
1. `.mutmut.ini.bak` (0.3 KB)
2. `src/codex/github/mcp_poster.py.bak` (102.0 KB)
3. `pyproject.toml.backup-day2` (14 KB)

**Steps:**
```bash
# Step 1: List backup files
ls -lah .mutmut.ini.bak
ls -lah pyproject.toml.backup-day2
ls -lah src/codex/github/mcp_poster.py.bak

# Step 2: Remove files
rm -f .mutmut.ini.bak
rm -f pyproject.toml.backup-day2
rm -f src/codex/github/mcp_poster.py.bak

# Step 3: Verify removal
ls -la .mutmut.ini.bak 2>&1 | grep "No such"
```

**Validation:**
- [ ] All .bak files removed
- [ ] No backup files remain
- [ ] Git status shows 3 deletions

**Commit Message:**
```
build(cleanup): Remove 3 backup files

- Delete .mutmut.ini.bak (0.3 KB)
- Delete src/codex/github/mcp_poster.py.bak (102.0 KB)
- Delete pyproject.toml.backup-day2 (14 KB)
- Total: 116.3 KB cleaned
- Refs: Phase 5.1 Hygiene Audit
```

---

### Task 1.3: Consolidate Mutmut Configuration Files
**Risk Level:** 🟡 MEDIUM  
**Time Estimate:** 20 minutes  
**Status:** [ ] Requires Review Before Action

**Current State:**
```
.mutmut.ini                          (PRIMARY)
.mutmut-cognitive-brain.ini
.mutmut-agent-memory.ini
.mutmut-comprehensive.ini
.mutmut-day1-baseline.ini
.mutmut-track2-config.ini
.mutmut-phase7b-trackc.ini
.mutmut-priority1.ini
.mutmut-wave3-lane32.ini
```

**Consolidation Plan:**
1. Examine content of each variant
2. Identify which configs are actively used
3. Merge necessary overrides into `.mutmut.ini`
4. Delete variants
5. Update CI/CD to use single config

**Steps:**
```bash
# Step 1: Examine files
head -20 .mutmut.ini
head -20 .mutmut-cognitive-brain.ini
# ... repeat for others

# Step 2: Check which are referenced in CI
grep -r "mutmut.*\.ini" .github/workflows/ || echo "No direct refs"
grep -r "mutmut.*\.ini" .codex/ || echo "No direct refs"

# Step 3: Check pytest config
grep -A5 "mutmut" pytest.ini

# Step 4: Identify active config (should be .mutmut.ini)
cat .mutmut.ini

# Step 5: AFTER VERIFICATION - Delete variants
rm -f .mutmut-*.ini

# Step 6: Verify
ls -la .mutmut*.ini
```

**Pre-Deletion Verification Checklist:**
- [ ] All variant configs reviewed
- [ ] Active overrides identified
- [ ] No CI/CD configs reference deleted files
- [ ] Changes documented
- [ ] Team agrees on consolidation

**Commit Message:**
```
build(cleanup): Consolidate 8 mutmut config variants to single .mutmut.ini

- Keep: .mutmut.ini (primary config)
- Delete: .mutmut-cognitive-brain.ini, .mutmut-agent-memory.ini, etc.
- All active overrides merged into primary config
- Simplifies mutation testing configuration
- Refs: Phase 5.1 Hygiene Audit
```

---

## PRIORITY 2: HIGH-VALUE CLEANUP (Do This Sprint)

### Task 2.1: Archive Phase Reports from Root
**Risk Level:** 🟡 MEDIUM  
**Time Estimate:** 20-30 minutes  
**Status:** [ ] Ready for Execution

**Files to Archive (180+ files, 2.2+ MB):**
```
PHASE_12_1_IMPLEMENTATION_SUMMARY.txt
PHASE_1_AGENTS_AUDIT.json
PHASE_2_TRACK_5_EXECUTION_SUMMARY.txt
PHASE_3_6_DELIVERABLES.md
PHASE_7A_LANE_4_COMPLETION_SUMMARY.txt
PHASE_7A_TASK3_FINAL_SUMMARY.txt
PHASE_7A_WAVE2_LANE24_COMPLETION_SUMMARY.txt
PHASE_8_1_FINAL_VERIFICATION_REPORT.txt
PHASE_B_LANE_4_DELIVERABLES.txt
PHASE_B_TRACK_1_COMPLETION.txt
PHASE_D_LANE_11_ML_VALIDATION_RESULTS.json
... and 169 more
```

**Steps:**
```bash
# Step 1: Create archive directory
mkdir -p archive/phases
mkdir -p archive/phases/reports

# Step 2: Move phase files
find . -maxdepth 1 -name "PHASE_*.txt" -o -name "PHASE_*.md" -o -name "PHASE_*.json" | \
  xargs -I {} mv {} archive/phases/reports/

# Step 3: Create index
cat > archive/phases/INDEX.md << 'EOF'
# Phase Reports Archive

This directory contains archived phase execution reports from Phase 1-D.

## Files by Type

### Phase 1-2 Reports
- PHASE_1_AGENTS_AUDIT.json
- PHASE_2_TRACK_5_EXECUTION_SUMMARY.txt

### Phase 3-6 Reports  
- PHASE_3_6_DELIVERABLES.md

### Phase 7A Reports
- PHASE_7A_LANE_4_COMPLETION_SUMMARY.txt
- PHASE_7A_TASK3_FINAL_SUMMARY.txt
- PHASE_7A_WAVE2_LANE24_COMPLETION_SUMMARY.txt

### Phase 8+ Reports
- PHASE_8_1_FINAL_VERIFICATION_REPORT.txt
- PHASE_B_LANE_4_DELIVERABLES.txt
- PHASE_B_TRACK_1_COMPLETION.txt
- PHASE_D_LANE_11_ML_VALIDATION_RESULTS.json
- PHASE_12_1_IMPLEMENTATION_SUMMARY.txt

Total: 180+ phase execution reports archived.
For active phase status, see .codex/phases/
EOF

# Step 4: Verify
ls -1 archive/phases/reports/ | wc -l
```

**Validation:**
- [ ] All PHASE_*.txt/md/json files moved to archive/phases/
- [ ] INDEX.md created
- [ ] Root directory no longer contains phase reports
- [ ] No build breaks
- [ ] Links updated if referenced elsewhere

**Commit Message:**
```
build(cleanup): Archive 180+ phase execution reports to archive/phases/

- Move PHASE_*.txt, PHASE_*.md, PHASE_*.json to archive/phases/reports/
- Reduce root directory clutter by 2.2 MB
- Create INDEX.md for archive navigation
- Phase status tracked in .codex/phases/ instead
- Refs: Phase 5.1 Hygiene Audit
```

---

### Task 2.2: Archive Large Log Files
**Risk Level:** 🟡 MEDIUM  
**Time Estimate:** 15 minutes  
**Status:** [ ] Requires Verification Before Action

**Files to Archive (1.9+ MB):**
```
mutmut_output.txt                             (332.2 KB)
coverage-report.txt                           (142.5 KB)
semgrep-m01-check-v2.json                     (3.8 MB)
semgrep-m01-final.json                        (3.3 MB)
workflow-audit-report.json                    (1.7 MB)
link-validation-report.json                   (277 KB)
phase_9_2_coverage_run.log                    (11.2 KB)
phase_9_2_initial_test_run.log                (2.1 KB)
```

**Pre-Archive Verification:**
```bash
# Check if files are referenced in code
grep -r "mutmut_output.txt" src/ tests/ .codex/ --include="*.py" || echo "Not referenced"
grep -r "coverage-report.txt" src/ tests/ .codex/ --include="*.py" || echo "Not referenced"
grep -r "semgrep-m01" src/ tests/ .codex/ --include="*.py" || echo "Not referenced"
```

**Steps:**
```bash
# Step 1: Create archive structure
mkdir -p archive/logs/{mutation-testing,coverage,security-scans,workflow-audits}

# Step 2: Move files
mv mutmut_output.txt archive/logs/mutation-testing/
mv coverage-report.txt archive/logs/coverage/
mv semgrep-m01-*.json archive/logs/security-scans/
mv workflow-audit-report.json archive/logs/workflow-audits/
mv link-validation-report.json archive/logs/workflow-audits/
mv phase_9_2_*.log archive/logs/

# Step 3: Create archive README
cat > archive/logs/README.md << 'EOF'
# Build & Test Logs Archive

Contains archived build outputs, test results, and audit reports.

## Structure

- `mutation-testing/` - Mutmut mutation testing results
- `coverage/` - Code coverage reports
- `security-scans/` - Semgrep and security scan results
- `workflow-audits/` - GitHub Actions and workflow audit results

## Retention Policy

Logs are archived immediately to avoid root clutter. Latest builds available in CI/CD pipelines.

For active logs, run:
- `pytest --cov=src` (for coverage)
- `mutmut run` (for mutation testing)
- `semgrep --config=p/security-audit` (for security scans)
EOF

# Step 4: Verify
du -sh archive/logs/
```

**Validation Checklist:**
- [ ] All large logs archived
- [ ] No references to root log files in CI/CD
- [ ] Archive README created
- [ ] Root directory cleaned
- [ ] Build system still works

**Commit Message:**
```
build(cleanup): Archive 8 large log files to archive/logs/

- Move mutmut_output.txt (332.2 KB)
- Move semgrep-m01-*.json (7.1 MB combined)
- Move coverage-report.txt (142.5 KB)
- Move workflow audit reports (1.7+ MB)
- Total: ~9.5 MB cleaned from root
- Create archive/logs/README.md for navigation
- Refs: Phase 5.1 Hygiene Audit
```

---

### Task 2.3: Reorganize Root Documentation Files
**Risk Level:** 🟡 MEDIUM  
**Time Estimate:** 30 minutes  
**Status:** [ ] Plan Before Action

**Current State:**
```
Root .md files: 28 files
.codex/archive/deprecated/AGENTS.md, CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md, etc.
```

**Target State:**
```
Root: Only essential files (README.md, LICENSE, SECURITY.md, CODE_OF_CONDUCT.md)
/docs/: All other documentation
/docs/guides/: Implementation guides
/docs/api/: API documentation
/docs/architecture/: Architecture docs
```

**Steps (Phase 2 of Task - Planning Only):**
```
Step 1: Categorize root .md files
- Essential (keep in root): README.md, SECURITY.md, CODE_OF_CONDUCT.md, LICENSE
- Implementation guides: CONTRIBUTING.md → /docs/guides/
- Process docs: CLEANUP_VALIDATION_INFRASTRUCTURE.md → /docs/processes/
- Internal docs: .codex/archive/deprecated/AGENTS.md → /docs/internal/
- Phase docs: Already handled (archived)

Step 2: Create /docs directory structure (if needed)
Step 3: Move files in batches
Step 4: Update root README.md with links to /docs/
Step 5: Verify no broken links
```

**Validation Checklist:**
- [ ] Root .md files reduced to <5
- [ ] All moved files accessible in /docs/
- [ ] README.md links to /docs/
- [ ] No broken internal links
- [ ] Navigation clear

**Commit Message:**
```
docs(cleanup): Reorganize 20+ root .md files to /docs/

- Keep only essential: README.md, SECURITY.md, CODE_OF_CONDUCT.md
- Move guides to /docs/guides/
- Move process docs to /docs/processes/
- Move internal docs to /docs/internal/
- Update README with /docs navigation
- Refs: Phase 5.1 Hygiene Audit
```

---

## PRIORITY 3: MEDIUM-VALUE CLEANUP (Planning Phase)

### Task 3.1: Consolidate Requirements Files
**Risk Level:** 🟡 MEDIUM  
**Time Estimate:** 45 minutes (Planning + Execution)  
**Status:** [ ] Requires Planning & Testing

**Current Structure (10 files):**
```
requirements.txt
requirements-dev.txt
requirements-test.txt
requirements-optional.txt
requirements-minimal.txt
requirements-ml-cpu.txt
requirements-ml-lite.txt
requirements-notebook.txt
requirements-eval.txt
requirements-audio-transcription.txt
```

**Proposed Target:**
```
requirements/
  ├── base.txt         (core dependencies)
  ├── dev.txt          (development tools)
  ├── test.txt         (testing tools)
  ├── ml.txt           (ML optional)
  └── all.txt          (consolidated all)

pyproject.toml         (single source of truth)
```

**Note:** This is a planning-phase recommendation. Requires:
- Dependency impact analysis
- CI/CD workflow updates
- Testing of all installation scenarios

---

### Task 3.2: Organize /misc/ Directory
**Risk Level:** 🟡 MEDIUM  
**Time Estimate:** 30 minutes  
**Status:** [ ] Requires Classification First

**Current Content:**
```
/misc/
  ├── repo-owner-review/
  │   ├── archived-artifacts/
  │   ├── archive-files/
  │   └── archived-backups/
```

**Action Plan:**
1. Review content of each subdirectory
2. Identify valuable vs. archivable content
3. Move valuable content to appropriate location
4. Archive or remove rest
5. Delete empty /misc/ directory

---

### Task 3.3: Clean Up Pytest Configuration Files
**Risk Level:** 🟡 MEDIUM  
**Time Estimate:** 20 minutes  
**Status:** [ ] Requires Verification

**Current Files:**
```
pytest.ini
pytest_mutation_override.ini
pytest_mutmut_override.ini
```

**Goal:** Single source of truth in `pytest.ini`

---

## PRIORITY 4: VALIDATION & VERIFICATION

### Task 4.1: Pre-Cleanup Validation
**Status:** [ ] Execute Before Any Deletions

**Checklist:**
```bash
# 1. Verify repository state
git status
git log --oneline -5

# 2. Check for references to files being deleted
grep -r "\.bak" .github/workflows/ --include="*.yml"
grep -r "\.pyc" .github/workflows/ --include="*.yml"
grep -r "PHASE_" .codex/*.json 2>/dev/null | head -5

# 3. Ensure all builds pass
pytest --co -q | head -20

# 4. Check imports work
python -c "import codex; print('OK')"

# 5. Verify no uncommitted changes
git status --porcelain | wc -l
```

---

### Task 4.2: Post-Cleanup Validation
**Status:** [ ] Execute After Each Priority Level

**Checklist:**
```bash
# 1. Verify files removed
ls -la .mutmut.ini.bak 2>&1 | grep "cannot access"
find . -name "*.pyc" | wc -l  # Should be 0

# 2. Verify directory structure
du -sh . | head -1
ls -1 archive/phases/reports/ | wc -l

# 3. Run tests
pytest tests/ -v --tb=short 2>&1 | tail -20

# 4. Verify no functional impact
python -c "import codex; codex.foo()" 2>&1

# 5. Check git status
git status
```

---

### Task 4.3: Create Post-Cleanup Report
**Status:** [ ] Generate Summary

**Contents:**
- Files deleted (with sizes)
- Files archived (with locations)
- Total size cleaned (MB)
- Improvements to health score
- Before/after metrics

---

## RISK MITIGATION CHECKLIST

### For All Tasks:
- [ ] Backup completed before any deletions
- [ ] Changes committed to branch, not pushed yet
- [ ] Git history preserved (no hard resets)
- [ ] All tests passing after changes
- [ ] No build breaks introduced
- [ ] Documentation updated with new structure

### For Configuration Consolidation (Task 1.3):
- [ ] All CI/CD workflows reviewed
- [ ] No active overrides missed
- [ ] Mutation testing still works
- [ ] Test configuration unchanged

### For File Archival (Task 2.1, 2.2):
- [ ] Archive directory exists
- [ ] INDEX.md created for navigation
- [ ] No active references to archived files
- [ ] Retrievability verified

---

## ROLLBACK PROCEDURES

If issues occur after cleanup:

```bash
# View recent commits
git log --oneline -10

# Revert last commit
git revert HEAD

# Or reset to before cleanup
git reset --hard <commit-before-cleanup>

# Push rollback
git push origin main
```

---

## SUCCESS METRICS

Upon completion of Priority 1 & 2 cleanup:

| Metric | Before | Target | Status |
|--------|--------|--------|--------|
| Root files | 152 | <50 | [ ] |
| Stale .pyc files | 38 | 0 | [ ] |
| Backup files | 3 | 0 | [ ] |
| Phase reports in root | 180+ | 0 | [ ] |
| Large logs in root | 8 | 0 | [ ] |
| Config variants | 12 | 1 | [ ] |
| Root directory MB | ~10 | <1 | [ ] |
| Health Score | 62 | 85+ | [ ] |

---

## SIGN-OFF

**Audit Date:** July 3, 2026  
**Cleanup Authorized By:** Phase 5 Authority  
**Execution Status:** [ ] Pending [ ] In Progress [ ] Complete  

---

**Next Step:** Execute Priority 1 tasks, then reassess for Priority 2

