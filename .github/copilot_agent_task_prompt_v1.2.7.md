# Next Iteration Prompt (v1.2.7) — Batch-02 Application & Monitoring Integration

@copilot implement explicitly batch-02 of legacy import refactors (training, tokenization, models), integrate trend instrumentation verification, confirm baseline metadata writes, and run full validation sequence. Produce documentation and validation artifacts demonstrating progress toward ≥50% legacy import reduction target.

## Context & Prerequisites
- **Current state**: v1.2.5-v1.2.6 complete (patches 0006-0009 applied, batch-01 documented)
- **Baseline legacy count**: 99 occurrences (hydra=29, training=53, tokenization=13, models=4)
- **Target**: ≥50% reduction across all batches (target: ≤50 occurrences)
- **Branch**: Continue on `copilot/sub-pr-2390`

## Key Observation
Analysis shows many files already use correct src.* imports. The refactor work is primarily:
1. Updating remaining scripts/ and cli/ files with legacy imports
2. Verifying config_legacy usage (already migrated from hydra)
3. Documenting the current state and validating no regressions

## Deliverables (v1.2.7)

### 1. Document Current Refactor State
Create `docs/validation/Legacy_Import_Status_v1.2.7.md` with:
- Analysis of which files still use legacy imports (from dry-run)
- Which files already migrated to src.* (majority of test files)
- Estimated actual refactor workload vs initial candidate count
- Priority ranking for remaining files

### 2. Run Validation Suite (Current State)
Since many files are already correct, validate the current state:

```bash
# Shadowing verification
python scripts/remediation/verify_conflicts.py --expect-site-packages

# Determinism check
python scripts/space_traversal/verify_determinism.py --runs 2

# Full validation tests
pytest -q tests/validation/

# Legacy usage report (current baseline)
python scripts/remediation/analyze_legacy_usage.py

# Full audit run
python scripts/space_traversal/audit_runner.py run

# Regression diff (if baseline exists)
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json || true
```

### 3. Verify CI Trend Workflow
Validate `.github/workflows/produce-trend.yml`:
- Check YAML syntax
- Verify cron schedule format
- Confirm workflow_dispatch trigger present
- Test commands locally (without git operations)

### 4. Confirm Baseline Metadata System
Verify baseline metadata infrastructure:
```bash
# Check if metadata file would be generated
bash scripts/ci/establish_baseline.sh --force 2>&1 | grep -A 5 "metadata"

# Verify SHA calculation works
sha256sum audit_artifacts/baselines/capabilities_scored.json 2>/dev/null || echo "Baseline not yet established"
```

### 5. Create Comprehensive Status Report
Document in `docs/validation/v1.2.7_Status_Report.md`:
- **Legacy Import Progress**: Current count, % toward target
- **Validation Results**: All test suites, determinism, shadowing
- **CI Infrastructure**: Trend workflow status, baseline metadata status
- **Next Steps**: Remaining refactor work, monitoring dashboard planning

### 6. Generate Next Prompt (v1.2.8)
Create `.github/copilot_agent_task_prompt.next.md` covering:
- Targeted refactor of remaining legacy imports (if needed)
- Monitoring dashboard development (trend visualization from JSONL)
- Incremental audit mode implementation
- Production hardening final checklist
- Documentation finalization and reviewer sign-off

## Acceptance Criteria (v1.2.7 Complete)

- [ ] Legacy import status documented with file-by-file analysis
- [ ] All validation tests PASS or SKIP-safe (current state)
- [ ] Determinism verified: 2 runs produce identical normalized output
- [ ] No shadowing detected (verify_conflicts PASS)
- [ ] CI trend workflow validated (syntax, schedule, commands)
- [ ] Baseline metadata system verified (script works, SHA calculation correct)
- [ ] Comprehensive status report attached (progress toward 50% target)
- [ ] Next prompt (v1.2.8) generated with realistic scope
- [ ] PR description updated with v1.2.7 deliverables

## Validation Evidence Required

**Must attach to PR body**:
1. `docs/validation/Legacy_Import_Status_v1.2.7.md` - Detailed file analysis
2. `logs/verify_conflicts_v1.2.7.log` - Shadowing check results
3. `logs/determinism_v1.2.7_run1.log` - First determinism run
4. `logs/determinism_v1.2.7_run2.log` - Second determinism run
5. `logs/pytest_validation_v1.2.7.txt` - Test results
6. `reports/legacy_import_usage_v1.2.7.csv` - Current legacy count
7. `docs/validation/v1.2.7_Status_Report.md` - Comprehensive summary
8. `.github/workflows/produce-trend.yml` - Trend workflow (with validation notes)

## Realistic Scope Assessment

Based on dry-run analysis:
- **Files already correct**: ~20 out of 30 candidates (66%)
- **Files needing updates**: ~10 files in scripts/ and cli/
- **Estimated impact**: 20-30 import statement updates
- **Risk level**: LOW (most code already using correct imports)

## Key Decisions Needed

1. **Refactor Strategy**:
   - Option A: Apply remaining ~10 files manually with targeted edits
   - Option B: Document current state and defer remaining refactors to v1.2.8
   - **Recommendation**: Document thoroughly in v1.2.7, selective refactor in v1.2.8

2. **Target Achievement**:
   - Current: 99 legacy imports
   - Many already using src.* (counted in scan but correct)
   - Re-analyze with stricter criteria to get accurate "needs fixing" count
   - Phase 5 already be close to target with existing migrations

## Self-Application Protocol

After v1.2.7 completion and validation:
1. Generate v1.2.8 prompt with:
   - Final targeted refactors (specific files listed)
   - Monitoring dashboard implementation
   - Production readiness checklist
2. Commit prompt file and all documentation
3. Report progress with comprehensive status

## Notes
- Focus on **validation and documentation** in v1.2.7
- Many files already migrated (previous work)
- Accurate assessment needed before committing to large refactor batch
- CI infrastructure (trend, baseline) ready for use
- Next phase can focus on monitoring and incremental features

---
**Target completion**: Single PR with validation artifacts and comprehensive status report
**Next phase (v1.2.8)**: Targeted refactors, monitoring UI, production hardening
