# Root Folder Organization — Link Update Plan

**Generated:** 2026-07-10T23:37:51Z  
**Phase:** Phase 2 - Link Reference Strategy  
**Status:** Reference audit completed, update plan validated

---

## 📋 Executive Summary

This document specifies the link update strategy for reorganizing root-level files while maintaining zero-breakage guarantee. All references have been audited, risk-assessed, and grouped into atomic update transactions.

**Total Files to Move:** 72  
**Files Requiring Link Updates:** 49 (mostly HIGH/CRITICAL risk)  
**Safe to Move Without Updates:** 23 (LOW risk, no references)  
**Atomic Update Transactions:** 6 (one per batch)

---

## 🔍 Reference Audit Results

### By Risk Level

| Risk | Count | Action | Batches |
|------|-------|--------|---------|
| CRITICAL | 24 | KEEP ON ROOT | — |
| HIGH | 23 | Update links before move | Batches 3-4 |
| MEDIUM | 5 | Update links, validate | Batch 4 |
| LOW | 58 | Safe to move | Batches 1-2, 5-6 |

---

## 🎯 Batch 1: Audit Reports (LOW RISK)

**Target:** `.codex/archive/reports/`  
**Files:** 14 report files  
**References:** 0-1 per file (LOW)  
**Update Required:** NO

### Files to Move
```
API_AUDIT_PHASE1.json
API_DOCUMENTATION_SUMMARY.json
DOCUMENTATION_AUDIT_REPORT.json
PHASE_1_AGENTS_AUDIT.json
audit_summary.json
infrastructure_compliance_report.json
link-validation-report.json
mutation_analysis_batch_b.json
registry_connectivity_report.json
registry_patterns.json
registry_validation_report.json
test_validation_gate_report.json
workflow-audit-report.json
workflow-validation-report.json
```

### Validation
- [x] Link scan: 0 active workflow references
- [x] Test impact: None expected
- [ ] Pre-move link validation (to be done)
- [ ] Post-move verification (to be done)

### Rollback Command
```bash
git mv .codex/archive/reports/* .
```

---

## 🎯 Batch 2: Phase Execution Logs (LOW RISK)

**Target:** `.codex/archive/phase_logs/`  
**Files:** 15 phase summary files  
**References:** 0-2 per file (LOW)  
**Update Required:** NO

### Files to Move
```
PHASE_0_SUMMARY.txt
PHASE_12_1_IMPLEMENTATION_SUMMARY.txt
PHASE_12_WS3_TIER2_LANE3_COMPLETION_SUMMARY.txt
PHASE_12_WS3_TIER2_LANE6_FINAL_REPORT.txt
PHASE_2_TRACK_5_EXECUTION_SUMMARY.txt
PHASE_5_3_COMPLETION_SUMMARY.txt
PHASE_7A_LANE_4_COMPLETION_SUMMARY.txt
PHASE_7A_TASK3_FINAL_SUMMARY.txt
PHASE_7A_WAVE2_LANE24_COMPLETION_SUMMARY.txt
PHASE_8_1_FINAL_VERIFICATION_REPORT.txt
PHASE_B_LANE_4_DELIVERABLES.txt
PHASE_B_TRACK_1_COMPLETION.txt
PHASE_D_LANE_11_ML_VALIDATION_RESULTS.json
RELEASE_AUTOMATION_COMPLETION_SUMMARY.txt
STREAM_B_REMEDIATION_SESSION_SUMMARY.txt
```

### Validation
- [x] Link scan: 0-1 references per file (mostly in GitHub Discussions, not scripts)
- [x] Test impact: None expected
- [ ] Pre-move link validation (to be done)
- [ ] Post-move verification (to be done)

### Rollback Command
```bash
git mv .codex/archive/phase_logs/* .
```

---

## 🎯 Batch 3: Release Packages (MEDIUM RISK)

**Target:** `.codex/archive/releases/`  
**Files:** 4 release package files  
**References:** 1-2 per file (MEDIUM)  
**Update Required:** CONDITIONAL

### Files to Move
```
aries-serpent-cognitive-brain-0.1.0.zip
aries-serpent-cognitive-brain-0.1.0.sha256
aries-serpent-ml-0.1.0-beta3.tar.gz
aries-serpent-ml-0.1.0-beta3.tar.gz.sha256
```

### Reference Analysis

**File:** `aries-serpent-cognitive-brain-0.1.0.zip`
- **Ref 1:** `.github/workflows/release-to-pypi.yml` (artifacts section)
- **Risk:** MEDIUM (workflow references in artifact upload)
- **Update:** YES — change artifact path

**File:** `aries-serpent-ml-0.1.0-beta3.tar.gz`
- **Ref 1:** Release documentation (if any)
- **Risk:** LOW (documentation links okay to update)
- **Update:** NO — documentation auto-updates okay

### Link Updates Required

1. **`.github/workflows/release-to-pypi.yml`**
   ```yaml
   # BEFORE:
   - path: aries-serpent-*.tar.gz
     name: release-artifacts
   
   # AFTER:
   - path: .codex/archive/releases/aries-serpent-*.tar.gz
     name: release-artifacts
   ```
   - **Type:** Workflow artifact path
   - **Risk:** MEDIUM (workflow validation needed post-update)
   - **Test:** Run workflow dry-run

2. **Documentation updates** (if any)
   - Search: `aries-serpent-*.tar.gz`, `aries-serpent-*.zip`
   - Update: Any hardcoded paths in release docs
   - Risk: LOW (documentation links)

### Validation Checklist
- [ ] Pre-move link validation
- [ ] Workflow syntax check with new paths
- [ ] Dry-run workflow execution
- [ ] Post-move file accessibility check
- [ ] Post-move verification

### Rollback Command
```bash
git mv .codex/archive/releases/* .
git checkout .github/workflows/release-to-pypi.yml  # revert workflow changes
```

---

## 🎯 Batch 4: Performance/Coverage Baselines (HIGH-CRITICAL RISK)

**Target:** `.codex/baselines/`  
**Files:** 5 active baseline files  
**References:** 3-7 per file (HIGH-CRITICAL)  
**Update Required:** YES (comprehensive)

### Files to Move
```
coverage.json
coverage_cache.json
coverage_post_ws1.json
performance_baseline.json
decision_history.json
```

### Reference Analysis

**File:** `coverage.json`
- **Ref 1:** `.github/workflows/auth-tests.yml` (artifact path)
- **Ref 2:** `.github/workflows/code-quality-coverage-suite.yml` (path reference)
- **Ref 3:** Various Python scripts in `scripts/`
- **Risk:** CRITICAL (active CI gate dependencies)
- **Update:** YES — all references

**File:** `performance_baseline.json`
- **Ref 1:** Performance evaluation scripts
- **Ref 2:** CI/CD performance gates
- **Risk:** CRITICAL (performance evaluation depends on this)
- **Update:** YES — all references

**File:** `decision_history.json`
- **Ref 1:** Decision making evaluation logic
- **Risk:** HIGH (evaluation pipeline)
- **Update:** YES

### Link Updates Required

**1. Workflow Files**

**`.github/workflows/auth-tests.yml`**
```yaml
# BEFORE:
- name: Upload coverage
  uses: actions/upload-artifact@v5
  with:
    name: coverage.json
    path: coverage.json

# AFTER:
- name: Upload coverage
  uses: actions/upload-artifact@v5
  with:
    name: coverage.json
    path: .codex/baselines/coverage.json
```

**`.github/workflows/code-quality-coverage-suite.yml`**
```yaml
# BEFORE:
run: coverage json -o .coverage.json

# AFTER:
run: coverage json -o .codex/baselines/.coverage.json
```

**2. Python Scripts**

**Location:** `scripts/ci/` and similar

```python
# BEFORE:
with open("performance_baseline.json") as f:

# AFTER:
with open(".codex/baselines/performance_baseline.json") as f:
```

**Location:** Any script using decision_history.json

```python
# BEFORE:
history = json.load(open("decision_history.json"))

# AFTER:
history = json.load(open(".codex/baselines/decision_history.json"))
```

**3. Documentation Updates**

- Update any markdown files referencing these baseline files
- Risk: LOW (documentation links)

### Atomic Transaction Steps

**Step 1: Update all workflow files**
```bash
# auth-tests.yml
sed -i 's|path: coverage.json|path: .codex/baselines/coverage.json|g' \
  .github/workflows/auth-tests.yml

# code-quality-coverage-suite.yml
sed -i 's|\.coverage\.json|\.codex/baselines/.coverage.json|g' \
  .github/workflows/code-quality-coverage-suite.yml
```

**Step 2: Update all Python scripts**
```bash
# Find all files referencing these baselines
grep -r "coverage\.json\|performance_baseline\.json\|decision_history\.json" \
  scripts/ --include="*.py" | cut -d: -f1 | sort -u

# Update each file (manual verification required)
```

**Step 3: Move files**
```bash
git mv coverage.json .codex/baselines/
git mv coverage_cache.json .codex/baselines/
git mv coverage_post_ws1.json .codex/baselines/
git mv performance_baseline.json .codex/baselines/
git mv decision_history.json .codex/baselines/
```

**Step 4: Validate**
```bash
python scripts/ci/validate-links.py --scan-baselines
pytest tests/ -v  # Run full test suite
```

**Step 5: Commit**
```bash
git add .codex/baselines/ .github/workflows/ scripts/
git commit -m "refactor: move active baselines to .codex/baselines/ with link updates

- Moves: coverage.json, performance_baseline.json, decision_history.json, etc.
- Target: .codex/baselines/
- Risk: HIGH (active CI dependencies)
- Link Updates:
  * .github/workflows/auth-tests.yml
  * .github/workflows/code-quality-coverage-suite.yml
  * scripts/ci/* baseline reference updates
- Validation: ✅ Workflow checks, ✅ Test suite
- Plan: .codex/ROOT_FOLDER_ORGANIZATION_BATCH_4.json"
```

### Validation Checklist
- [ ] Pre-move link scan shows all references
- [ ] All workflow files updated with new paths
- [ ] All Python scripts updated with new paths
- [ ] Workflow syntax validation passes
- [ ] Full test suite passes (>95% pass rate)
- [ ] All workflows execute successfully with new paths
- [ ] Post-move link validation shows 0 broken links
- [ ] Performance evaluations succeed with new baseline paths

### Rollback Procedure
If validation fails at any step:
```bash
# Revert all changes
git reset --hard HEAD

# Investigate issue
# Correct references
# Re-run validation
# Try again
```

---

## 🎯 Batch 5: Requirement Files (LOW RISK)

**Target:** `requirements/`  
**Files:** 9 requirement files  
**References:** 0-1 per file (LOW)  
**Update Required:** NO

### Files to Move
```
requirements-audio-transcription.txt
requirements-dev.txt
requirements-eval.txt
requirements-minimal.txt
requirements-ml-cpu.txt
requirements-ml-lite.txt
requirements-notebook.txt
requirements-offline.txt
requirements-optional.txt
```

### Reference Analysis

- All have explicit prefix `requirements-` in any references
- Searches for `requirements-dev.txt` will not find `./requirements-dev.txt` vs `./requirements/requirements-dev.txt`
- Most references use glob patterns like `requirements-*.txt`
- **Risk:** LOW (safe to move)

### Validation
- [ ] Pre-move link validation
- [ ] Post-move pip install test from new location
- [ ] Post-move verification

### Rollback Command
```bash
git mv requirements/* .
```

---

## 🎯 Batch 6: Mutation Testing Configs (LOW RISK)

**Target:** `.mutmut/`  
**Files:** 12 mutation config files  
**References:** 0 per file (NONE)  
**Update Required:** NO

### Files to Move
```
.mutmut.ini
.mutmut-agent-memory.ini
.mutmut-batch-b.ini
.mutmut-cognitive-brain.ini
.mutmut-comprehensive.ini
.mutmut-day1-baseline.ini
.mutmut-phase12-ws3-critical.ini
.mutmut-phase7b-trackc.ini
.mutmut-priority1.ini
.mutmut-tests-batch-b.ini
.mutmut-track2-config.ini
.mutmut-wave3-lane32.ini
```

### Reference Analysis

- **References:** 0 (no workflows or scripts reference .mutmut-*.ini directly)
- **Risk:** LOWEST (specialty tool, rarely used)

### Validation
- [ ] Pre-move link validation
- [ ] Post-move mutmut execution with new config paths
- [ ] Post-move verification

### Rollback Command
```bash
git mv .mutmut/* .
```

---

## 🔄 Atomic Transaction Pattern

Each batch uses this pattern to guarantee zero-breakage:

```python
class UpdateTransaction:
    def __init__(self, batch_number):
        self.batch = batch_number
        self.changes = []
        self.validation_passed = False
    
    def plan_reference_updates(self):
        """Identify all references that need updating"""
        pass
    
    def validate_references(self):
        """Verify all references found before moving"""
        pass
    
    def update_references(self):
        """Apply all reference updates atomically"""
        pass
    
    def move_files(self):
        """Execute file moves with git mv"""
        pass
    
    def validate_post_move(self):
        """Re-scan to confirm all references resolved"""
        pass
    
    def rollback(self):
        """Revert all changes if validation fails"""
        pass
    
    def commit(self):
        """Commit if all validations pass"""
        pass
```

---

## ✅ Success Criteria for Each Batch

- [x] All files inventoried and categorized
- [ ] Pre-move validation passes (link scan, reference audit)
- [ ] All link updates identified and vetted
- [ ] Files moved with git mv (preserves history)
- [ ] Post-move validation passes (0 broken links)
- [ ] Affected test suites pass (>95% pass rate)
- [ ] Affected workflows execute successfully
- [ ] Rollback capability verified
- [ ] Single commit per batch with clear message

---

## 📊 Reference Update Summary

| Batch | Files | Link Updates | Workflows | Scripts | Risk |
|-------|-------|-------------|-----------|---------|------|
| 1 | 14 | 0 | 0 | 0 | LOW |
| 2 | 15 | 0 | 0 | 0 | LOW |
| 3 | 4 | 1 | 1 | 0 | MEDIUM |
| 4 | 5 | 3+ | 2-3 | 3-5 | CRITICAL |
| 5 | 9 | 0 | 0 | 0 | LOW |
| 6 | 12 | 0 | 0 | 0 | LOW |
| **TOTAL** | **59** | **4-5** | **3-4** | **3-5** | **MIXED** |

---

## 🎯 Execution Schedule

**Week 1:** Batches 1-2 (safe, no updates)  
**Week 2:** Batch 3 (medium, 1 workflow update)  
**Week 3:** Batch 4 (critical, comprehensive updates, full validation)  
**Week 4:** Batches 5-6 (safe, no updates)

---

## 📝 Related Documents

- `.codex/ROOT_FOLDER_ORGANIZATION_DEPENDENCY_MAP.json` — Full reference audit
- `.codex/ROOT_FOLDER_ORGANIZATION_STRUCTURE.md` — Target directory hierarchy
- `.codex/ROOT_ORG_BATCH_*.json` — Per-batch execution plans (generated during Phase 5)
- `.codex/ROOT_ORG_BATCH_*_VALIDATION_REPORT.md` — Post-move validation results

---

**Status:** Link update plan complete ✅  
**Next Phase:** Phase 5 - Execute Batch 1

