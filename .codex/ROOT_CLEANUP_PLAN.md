# 🧹 Root Directory Cleanup Plan

**Date**: 2026-02-09  
**Status**: 🔄 IN PROGRESS  
**Safety Level**: ZERO-BREAKAGE GUARANTEE  
**AI Agency Policy**: ACTIVE 🤖

---

## 📊 Current Root Directory Audit

### Files to Relocate (27 files)

#### Test/Debug Files (Priority 1 - Can be safely moved/removed)
1. `a.py` (20 bytes) - Test file → **DELETE** or move to `tests/scratch/`
2. `b.py` (20 bytes) - Test file → **DELETE** or move to `tests/scratch/`

#### Documentation Files (Priority 1 - Move to docs/)
3. `DETERMINISM_CHECK_FIX.md` (5.0KB) - Test fix documentation → `docs/testing/`
4. `DETERMINISM_FIX_VERIFICATION.txt` (7.0KB) - Verification log → `.codex/test_results/`
5. `STOPITERATION_FIX_REPORT.md` (8.4KB) - Fix report → `docs/testing/`
6. `TEST_FIXES_PR3178.md` (5.5KB) - PR fix documentation → `.codex/pr_fixes/`
7. `TEST_FIXES_PR3178_BATCH2.md` (9.6KB) - PR fix documentation → `.codex/pr_fixes/`
8. `TEST_FIXES_PROGRESS_REPORT.md` (5.8KB) - Progress report → `.codex/pr_fixes/`
9. `TEST_FIXES_SUMMARY.md` (9.3KB) - Summary report → `.codex/pr_fixes/`
10. `FINAL_REPORT.md` (4.1KB) - Final report → `.codex/pr_fixes/`
11. `FINAL_TEST_STATUS.md` (3.1KB) - Test status → `.codex/pr_fixes/`
12. `.codex/archive/misc/.copilot-review-exclusions.md` (6.0KB) - Config file → `.github/copilot/`
13. `.security-exceptions.md` (8.6KB) - Security config → `docs/security/`

#### Configuration Files (Priority 2 - Keep in root, validate usage)
14. `noxfile.py` (24KB) - Build/test automation → **KEEP** (standard location)
15. `conftest.py` (8.7KB) - Pytest configuration → **KEEP** (standard location)
16. `.mutmut-config.txt` (943 bytes) - Mutation testing config → **KEEP**
17. `.mypy-baseline.txt` (115 bytes) - Type checking baseline → **KEEP**

#### Requirements Files (Priority 2 - Keep in root, consider requirements/ folder)
18. `requirements.txt` (1.4KB) - **KEEP** (standard location)
19. `requirements-dev.txt` (318 bytes) - **KEEP**
20. `requirements-test.txt` (886 bytes) - **KEEP**
21. `requirements-optional.txt` (1.1KB) - **KEEP**
22. `requirements-notebook.txt` (171 bytes) - **KEEP**
23. `requirements-minimal.txt` (925 bytes) - **KEEP**
24. `requirements-eval.txt` (221 bytes) - **KEEP**
25. `requirements-ml-lite.txt` (582 bytes) - **KEEP**
26. `requirements-ml-cpu.txt` (278 bytes) - **KEEP**

#### Agent Documentation (Priority 1 - Already in good location)
27. `.codex/archive/deprecated/AGENTS.md` (28KB) - **KEEP** (primary agent documentation)

---

## 🎯 Migration Strategy

### Phase 1: Create Destination Directories
```bash
# Create necessary directories
mkdir -p docs/testing
mkdir -p .codex/test_results
mkdir -p .codex/pr_fixes
mkdir -p .github/copilot
mkdir -p tests/scratch
```

### Phase 2: Move Documentation Files (Low Risk)
**Impact**: ZERO (no imports, references are relative)

```bash
# Test fix documentation
mv DETERMINISM_CHECK_FIX.md docs/testing/
mv STOPITERATION_FIX_REPORT.md docs/testing/

# Test results
mv DETERMINISM_FIX_VERIFICATION.txt .codex/test_results/

# PR fix documentation
mv TEST_FIXES_PR3178.md .codex/pr_fixes/
mv TEST_FIXES_PR3178_BATCH2.md .codex/pr_fixes/
mv TEST_FIXES_PROGRESS_REPORT.md .codex/pr_fixes/
mv TEST_FIXES_SUMMARY.md .codex/pr_fixes/
mv FINAL_REPORT.md .codex/pr_fixes/
mv FINAL_TEST_STATUS.md .codex/pr_fixes/

# Configuration files
mv .codex/archive/misc/.copilot-review-exclusions.md .github/copilot/review-exclusions.md
mv .security-exceptions.md docs/security/security-exceptions.md
```

### Phase 3: Handle Test Files (Low Risk)
**Impact**: ZERO (not imported, likely temporary)

```bash
# Option 1: Delete (recommended)
rm a.py b.py

# Option 2: Move to scratch (if needed for reference)
# mv a.py tests/scratch/
# mv b.py tests/scratch/
```

### Phase 4: Update Cross-References (Medium Risk)
**Impact**: Documentation links need updating

Files that might reference moved files:
- README.md
- docs/**/*.md
- .codex/**/*.md
- .github/**/*.md

**Validation**:
```bash
# Search for references to moved files
grep -r "DETERMINISM_CHECK_FIX.md" --include="*.md" .
grep -r "STOPITERATION_FIX_REPORT.md" --include="*.md" .
grep -r "TEST_FIXES" --include="*.md" .
grep -r "copilot-review-exclusions" --include="*.md" --include="*.yaml" --include="*.yml" .
grep -r "security-exceptions" --include="*.md" --include="*.yaml" --include="*.yml" .
```

### Phase 5: Validation
```bash
# Verify no broken imports
python -c "import sys; sys.path.insert(0, 'src'); import codex"

# Verify pytest still works
pytest --collect-only

# Verify nox sessions
nox --list

# Run pre-commit checks
pre-commit run --all-files
```

---

## 🔍 Impact Analysis

### Files with ZERO Impact (Safe to Move Immediately)
- `a.py`, `b.py` - Test/scratch files
- `DETERMINISM_CHECK_FIX.md` - Documentation only
- `DETERMINISM_FIX_VERIFICATION.txt` - Log file
- `STOPITERATION_FIX_REPORT.md` - Documentation only
- `TEST_FIXES_*.md` - Documentation only
- `FINAL_*.md` - Documentation only

### Files with LOW Impact (Need Reference Updates)
- `.codex/archive/misc/.copilot-review-exclusions.md` - May be referenced in workflows
- `.security-exceptions.md` - May be referenced in security tools

### Files to KEEP in Root (Standard/Required Locations)
- `noxfile.py` - Standard Python project automation (nox expects root)
- `conftest.py` - Pytest root conftest (pytest expects root)
- `requirements*.txt` - Standard Python dependency files (pip expects root)
- `.mutmut-config.txt` - Mutmut expects root
- `.mypy-baseline.txt` - Mypy expects root
- `.codex/archive/deprecated/AGENTS.md` - Primary entry point for agent documentation

---

## 📁 Directories to Organize (Out of Scope - Future Work)

### Potential Consolidation Opportunities
Many root-level directories could be organized better:

**Development Tools**:
- `nox_sessions/` → Keep (nox convention)
- `.githooks/` → Keep (git convention)
- `.pre-commit-scripts/` → Keep (pre-commit convention)

**Configuration**:
- `conf/`, `config/`, `config_legacy/`, `configs/` → Consider merging
- `omegaconf/`, `yaml_legacy/` → Consider merging into `configs/`

**Data/Assets**:
- `data/`, `datasets/`, `samples/` → Could consolidate
- `assets/`, `artifacts/` → Could consolidate

**Code Organization**:
- `cli/`, `utils/`, `tools/` → Some overlap with src/
- `agents/`, `automation/`, `actions/` → Could consolidate
- `codex_*` directories → Many could be in src/

**Testing**:
- `tests/`, `tests_rust/`, `benches/`, `benchmarks/` → Good separation
- `baseline/` → Move to tests/

**Documentation**:
- `guides/`, `prompts/`, `PROMPTS/` → Consolidate into docs/
- `notebooks/` → Keep (standard for Jupyter)

**⚠️ Note**: Directory reorganization is a MAJOR refactoring requiring:
- Import path updates across entire codebase
- CI/CD workflow updates
- Documentation updates
- Extensive testing

**Recommendation**: OUT OF SCOPE for this PR. Create follow-up issue.

---

## ✅ Execution Plan (This PR)

### Immediate Actions (LOW RISK)
1. ✅ Delete test files: `a.py`, `b.py`
2. ✅ Move documentation to appropriate folders
3. ✅ Update cross-references
4. ✅ Validate no breakage

### Deferred Actions (FUTURE)
1. ⏳ Directory consolidation (requires extensive refactoring)
2. ⏳ Import path updates
3. ⏳ CI/CD workflow updates
4. ⏳ Comprehensive testing

---

## 🧪 Testing Strategy

### Pre-Move Validation
```bash
# Capture current state
pytest --collect-only > .codex/test_collection_before.txt
nox --list > .codex/nox_sessions_before.txt
git ls-files > .codex/git_files_before.txt
```

### Post-Move Validation
```bash
# Verify same state
pytest --collect-only > .codex/test_collection_after.txt
nox --list > .codex/nox_sessions_after.txt
git ls-files > .codex/git_files_after.txt

# Compare
diff .codex/test_collection_before.txt .codex/test_collection_after.txt
diff .codex/nox_sessions_before.txt .codex/nox_sessions_after.txt
```

### Smoke Tests
```bash
# Import test
python -c "import sys; sys.path.insert(0, 'src'); import codex; print('✅ Imports work')"

# Pytest test
pytest tests/test_imports.py -v

# Pre-commit test
pre-commit run --files $(git diff --name-only --cached) || echo "Check failures"
```

---

## 📝 Cross-Reference Updates

### Files to Check
```bash
# Find references to moved files
rg "DETERMINISM_CHECK_FIX" --type md
rg "STOPITERATION_FIX_REPORT" --type md
rg "TEST_FIXES" --type md
rg "copilot-review-exclusions" --type md --type yaml
rg "security-exceptions" --type md --type yaml
```

### Update Patterns
- `DETERMINISM_CHECK_FIX.md` → `docs/testing/DETERMINISM_CHECK_FIX.md`
- `STOPITERATION_FIX_REPORT.md` → `docs/testing/STOPITERATION_FIX_REPORT.md`
- `TEST_FIXES_*.md` → `.codex/pr_fixes/TEST_FIXES_*.md`
- `.codex/archive/misc/.copilot-review-exclusions.md` → `.github/copilot/review-exclusions.md`
- `.security-exceptions.md` → `docs/security/security-exceptions.md`

---

## 🎯 Success Criteria

### Must Have (Blocking)
- ✅ All moved files accessible at new locations
- ✅ No broken links in documentation
- ✅ pytest collection unchanged
- ✅ nox sessions list unchanged
- ✅ All imports work
- ✅ Pre-commit hooks pass
- ✅ Git history preserved

### Nice to Have (Non-Blocking)
- ✅ Root directory cleaner (fewer loose files)
- ✅ Better organization
- ✅ Easier navigation
- ✅ Updated documentation

---

## 🚦 Risk Assessment

### ZERO RISK ✅
- Deleting `a.py`, `b.py` (test files)
- Moving markdown documentation files
- Moving text log files

### LOW RISK 🟡
- Moving `.codex/archive/misc/.copilot-review-exclusions.md` (may need workflow updates)
- Moving `.security-exceptions.md` (may need tool config updates)

### HIGH RISK 🔴 (OUT OF SCOPE)
- Moving configuration files (noxfile.py, conftest.py, requirements.txt)
- Reorganizing directories (requires extensive refactoring)
- Moving Python modules (requires import updates)

---

## 📋 Implementation Checklist

- [ ] Create destination directories
- [ ] Delete test files (a.py, b.py)
- [ ] Move documentation files
- [ ] Move configuration files to appropriate locations
- [ ] Search for cross-references
- [ ] Update all cross-references
- [ ] Run validation tests
- [ ] Verify no breakage
- [ ] Update .gitignore if needed
- [ ] Commit with detailed message
- [ ] Document changes in CHANGELOG.md

---

**Status**: Plan Complete - Ready for Execution  
**Next**: Execute Phase 1 (Create Directories)
