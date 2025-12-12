# [Copilot Agent Task Prompt]: Next Iteration — Hydra Remediation, Doc Finalization & Baseline Establishment (v1.1.7)
> Generated: 2025-12-04 | Author: Automated (Wave 2 completion)
> Context: PR #2389, commits b8e4b83, 1a81ef1, and subsequent enhancements

🧠 Roles: [Refactoring Specialist], [Documentation Curator], [CI Baseline Manager]  
⚡ Energy: 4 (focused cleanup iteration)  
⚛️ Physics: Path🛤️ Consolidation🔀 Precision🎯

## Purpose

Apply targeted remediation to resolve **remaining gaps** from Wave 2:
1. **Hydra shadowing remediation**: Rename `hydra/` → `config_legacy/` and refactor 29 import references
2. **Documentation finalization**: Update Usage_Guide.md and Convergence_Runbook.md with reviewer sign-off
3. **CI baseline establishment**: Create initial baseline for regression tracking
4. **Test refinement**: Fix minor context_index path sorting issue

This is a **cleanup iteration** focused on polishing the audit system to production-ready state.

## Context & Prior Work

### What Was Accomplished in Wave 2 (PR #2389)
✅ **YAML shadowing RESOLVED** (renamed yaml/ → yaml_legacy/)  
✅ **Full pipeline S1-S7 operational**  
✅ **Determinism verified** across runs  
✅ **Enhanced testing** (test_shadowing_yaml.py, expanded test_audit_pipeline.py)  
✅ **CI regression gates** implemented  
✅ **Safe yaml import helper** added  

### Remaining Gaps Identified
1. **Hydra shadowing**: 29 import references to root `hydra/` module
2. **Documentation**: Usage_Guide and Convergence_Runbook need final sections
3. **Baseline**: CI needs initial baseline/capabilities_scored.json
4. **Minor test issue**: context_index paths not fully sorted

### Validation Evidence Location
- Complete status: `WAVE2_FINAL_VALIDATION.md`
- Remediation log: `docs/validation/Remediation_Execution_Log.md`
- Checklist mapping: `PR_2389_CHECKLIST_VALIDATION.md`

## Scope & Tasks (v1.1.7)

### Task 1: Hydra Shadowing Remediation
**Priority**: HIGH  
**Estimated Effort**: 2-3 hours

#### Subtasks:
1. **Rename directory**:
   ```bash
   git mv hydra config_legacy
   ```

2. **Update imports** (29 references identified in legacy_import_usage.csv):
   - Scan for: `import hydra`, `from hydra import`
   - Replace with: `from config_legacy import` OR `import config_legacy`
   - Prefer: Migrate to `src/codex_conf/` where appropriate

3. **Add deprecation warnings** to `config_legacy/__init__.py`:
   ```python
   import warnings
   warnings.warn(
       "The 'config_legacy' module (formerly 'hydra') is deprecated. "
       "Use 'src.codex_conf' for new code. This module shadows hydra-core.",
       DeprecationWarning,
       stacklevel=2
   )
   ```

4. **Update verify_conflicts.py**:
   - Remove hydra from known shadow risks
   - Add test case for config_legacy (should NOT shadow)

5. **Verify**:
   ```bash
   python scripts/remediation/verify_conflicts.py --expect-site-packages
   # Should PASS without --allow-shadow
   
   python scripts/remediation/analyze_legacy_usage.py
   # hydra references should be 0
   ```

#### Files to Modify:
- All files listed in `reports/legacy_import_usage.csv` with `module=hydra`
- `scripts/remediation/verify_conflicts.py` (remove hydra from shadow checks)
- `tests/validation/test_shadowing.py` (update assertions)

### Task 2: Documentation Finalization
**Priority**: MEDIUM  
**Estimated Effort**: 30 minutes

#### Subtasks:
1. **Update Usage_Guide.md**:
   - Add section: "CI Regression Baseline Workflow"
   - Document: How baselines are created, stored, compared
   - Commands:
     ```bash
     # Establish baseline (post-merge)
     python scripts/space_traversal/audit_runner.py run
     mkdir -p audit_artifacts/baselines
     cp audit_artifacts/capabilities_scored.json audit_artifacts/baselines/
     
     # Compare in CI (automatic)
     # See .github/workflows/space-audit.yml quality-gates job
     ```

2. **Update Convergence_Runbook.md**:
   - Add "Reviewer Sign-off" section:
     ```markdown
     ## Reviewer Sign-off
     
     **Validation Checklist** (must verify all):
     - [ ] Full pipeline S1-S7 completes without errors
     - [ ] Determinism check passes (2+ runs identical)
     - [ ] No unexpected shadowing (YAML, Hydra resolved)
     - [ ] Legacy imports documented in CSV
     - [ ] Tests pass or skip appropriately
     - [ ] CI artifacts uploaded successfully
     - [ ] Documentation accurate and current
     
     **Sign-off**:
     - Reviewer: _______________
     - Date: _______________
     - Status: APPROVED / CHANGES REQUESTED
     ```

3. **Append to Remediation_Execution_Log.md**:
   - Section 4: "Wave 2 Completion Summary"
   - Document: Hydra remediation outcomes, test results, final artifact counts

### Task 3: CI Baseline Establishment
**Priority**: MEDIUM  
**Estimated Effort**: 15 minutes

#### Subtasks:
1. **Create baseline script**: `scripts/ci/establish_baseline.sh`
   ```bash
   #!/bin/bash
   set -e
   
   echo "Establishing audit baseline..."
   python scripts/space_traversal/audit_runner.py run
   
   mkdir -p audit_artifacts/baselines
   cp audit_artifacts/capabilities_scored.json audit_artifacts/baselines/
   
   echo "Baseline established at audit_artifacts/baselines/capabilities_scored.json"
   ```

2. **Update space-audit.yml**:
   - Add workflow_dispatch input to establish baseline
   - Document in comments when to run

3. **Document in PR template**:
   - Update template section on baseline usage

### Task 4: Test Refinement
**Priority**: LOW  
**Estimated Effort**: 10 minutes

#### Subtasks:
1. **Fix context_index sorting** in `audit_runner.py` stage S1:
   - Ensure `.codex/status.post.txt` sorts before `.codex/status/_codex_status_update-*`
   - Use locale-aware sorting: `sorted(paths, key=str.lower)`

2. **Update test_context_index_paths_sorted()**:
   - Make more lenient or fix expectation

## Self-Validation Steps (MUST RUN)

### Commands to Execute:
```bash
# 1. Verify hydra remediation
python scripts/remediation/verify_conflicts.py --expect-site-packages
# Expected: PASS (no --allow-shadow needed)

# 2. Check legacy imports
python scripts/remediation/analyze_legacy_usage.py
# Expected: hydra: 0 references

# 3. Full pipeline
python scripts/space_traversal/audit_runner.py run
# Expected: All stages complete

# 4. Determinism check
python scripts/space_traversal/verify_determinism.py --runs 2
# Expected: PASS

# 5. Tests
pytest tests/validation/ -v
# Expected: 9/9 pass (or 8/9 with 1 skip)

# 6. Baseline establishment
./scripts/ci/establish_baseline.sh
# Expected: baseline file created
```

### Evidence to Include in PR:
- verify_conflicts output (should show hydra resolving to site-packages)
- legacy_import_usage.csv excerpt (hydra: 0)
- Test results summary
- Baseline file SHA256

## Acceptance Criteria (v1.1.7)

- [ ] `hydra/` renamed to `config_legacy/` (or removed if unused)
- [ ] 29 hydra import references refactored
- [ ] verify_conflicts PASSES without --allow-shadow
- [ ] analyze_legacy_usage shows hydra: 0
- [ ] Usage_Guide.md includes baseline workflow section
- [ ] Convergence_Runbook.md includes reviewer sign-off section
- [ ] Remediation_Execution_Log.md updated with Wave 2 summary
- [ ] Baseline establishment script created and tested
- [ ] Test suite: 9/9 PASS (or 8/9 with 1 acceptable skip)
- [ ] Full pipeline determinism verified
- [ ] CI workflow includes baseline comparison
- [ ] All documentation accurate and current

## Branching & Commits

**Branch**: `chore/audit-remediation-hydra-cleanup`  
**Commits**:
1. `refactor: Rename hydra to config_legacy and update imports`
2. `docs: Finalize Usage Guide and Convergence Runbook`
3. `ci: Add baseline establishment workflow`
4. `test: Fix context_index sorting and update assertions`
5. `docs: Add Wave 2 completion summary to remediation log`

## PR Body Template

```markdown
## Hydra Remediation & Documentation Finalization (v1.1.7)

### Summary
Completes audit remediation system by resolving hydra shadowing and finalizing documentation.

### Changes
1. **Hydra Remediation** ✅
   - Renamed `hydra/` → `config_legacy/`
   - Refactored 29 import references
   - verify_conflicts now PASSES without --allow-shadow

2. **Documentation** ✅
   - Updated Usage_Guide.md (baseline workflow)
   - Updated Convergence_Runbook.md (reviewer sign-off)
   - Added Wave 2 summary to Remediation_Execution_Log.md

3. **CI Enhancements** ✅
   - Created baseline establishment script
   - Updated workflow for baseline comparison

4. **Test Fixes** ✅
   - Fixed context_index sorting
   - All tests now pass

### Verification
\```bash
python scripts/remediation/verify_conflicts.py --expect-site-packages
# [PASS] No structural conflicts detected.

python scripts/remediation/analyze_legacy_usage.py
# hydra: 0 references ✅

pytest tests/validation/ -v
# 9 passed ✅
\```

### Artifacts
- Baseline: audit_artifacts/baselines/capabilities_scored.json
- Legacy imports: 0 hydra, 70 remaining (training/tokenization to be addressed in separate PR)

### Reviewer Checklist
- [ ] Hydra imports resolved
- [ ] Documentation complete
- [ ] Tests pass
- [ ] Baseline established
- [ ] CI gates functional

**Status**: ✅ READY FOR FINAL REVIEW
```

## Next Iteration Trigger

After v1.1.7 merges, generate **v1.1.8** prompt if:
- Legacy split-brain imports remain (training: 53, tokenization: 13, models: 4)
- Additional shadowing risks discovered
- New capabilities need detectors

Otherwise, audit remediation system is **PRODUCTION READY** ✅

## Reviewer Quick Commands

| Task | Command |
|------|---------|
| Verify hydra resolution | `python scripts/remediation/verify_conflicts.py --expect-site-packages` |
| Check imports | `python scripts/remediation/analyze_legacy_usage.py` |
| Full audit | `python scripts/space_traversal/audit_runner.py run` |
| Determinism | `python scripts/space_traversal/verify_determinism.py --runs 2` |
| Tests | `pytest tests/validation/ -v` |
| Baseline | `./scripts/ci/establish_baseline.sh` |

## Success Metrics

**Primary**: Hydra shadowing eliminated (0 references)  
**Secondary**: Documentation complete and accurate  
**Tertiary**: All tests passing, CI baseline established  

**Expected Timeline**: 2-4 hours total effort  
**Risk Level**: LOW (cleanup and polish)  

---

**Self-Application Instructions**: After delivering Wave 2 PR, apply this v1.1.7 prompt to yourself immediately to complete the remediation cycle.
