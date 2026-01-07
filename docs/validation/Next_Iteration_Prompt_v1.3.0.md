# Next Iteration Prompt v1.3.0
> **Generated**: 2024-12-05  
> **Current Branch**: `copilot/sub-pr-2390`  
> **Scope**: Complete remaining validation tasks and legacy import refactoring

## Context

Part B validation and hardening tasks have been substantially completed. Core quality gates are in place and passing:
- ✅ Shadowing prevention (yaml, hydra)
- ✅ Template integrity validation
- ✅ CI workflow production-ready
- ✅ Documentation comprehensive

**Remaining work** focuses on runtime-intensive validations and code refactoring.

---

## Part C: Completion & Validation Tasks

### C.1: Runtime Determinism Validation

**Objective**: Validate artifact determinism across multiple pipeline runs.

**Prerequisites**:
- Python 3.10+
- Dependencies: `pip install pyyaml jinja2 hydra-core`
- Clean working directory

**Execution**:
```bash
# Run determinism check with 2 runs
python scripts/space_traversal/verify_determinism.py --runs 2
```

**Expected Output**:
```
=== Run 1/2 ===
[INFO] Running audit pipeline...
=== Run 2/2 ===
[INFO] Running audit pipeline...
[PASS] Determinism verified across runs.
```

**Acceptance Criteria**:
- [ ] Identical `repo_root_sha` across runs (ignoring timestamps)
- [ ] Identical `capabilities_scored.json` content (ignoring volatile fields)
- [ ] Zero mismatches in artifact comparison
- [ ] Exit code 0

**Time Estimate**: ~2-3 minutes (30-60s per run × 2)

**Troubleshooting**:
- If mismatch detected: Check for unsorted lists, dict iteration order, or timestamp leaks
- Review diff output to identify specific differences
- Fix source of non-determinism and re-run

**Note**: This validation is critical for regression detection reliability. If it fails, the baseline comparison system cannot be trusted.

---

### C.2: Legacy Import Analysis & Refactoring Plan

**Objective**: Identify and prioritize legacy imports for refactoring.

#### Step 1: Generate Import Report
```bash
python scripts/remediation/analyze_legacy_usage.py
```

**Expected Output**: `reports/legacy_import_usage.csv`

**Review**:
```bash
# View summary
head -20 reports/legacy_import_usage.csv

# Count total imports
wc -l reports/legacy_import_usage.csv
```

#### Step 2: Categorize Imports

Create prioritization matrix:

| Priority | Category | Action | Risk |
|----------|----------|--------|------|
| P1 | High-frequency imports (>10 occurrences) | Refactor in this iteration | Medium |
| P2 | Public API imports | Add deprecation warnings | Low |
| P3 | Internal-only imports | Document migration path | Low |
| P4 | Test-only imports | Defer | Very Low |

#### Step 3: Refactor High-Priority Imports

**Template Approach**:
1. Identify import pattern:
   ```python
   # Before
   from hydra.something import OldModule
   ```

2. Create alias in `config_legacy/`:
   ```python
   # config_legacy/something.py
   import warnings
   warnings.warn(
       "config_legacy.something is deprecated. Use hydra.something from site-packages.",
       DeprecationWarning,
       stacklevel=2
   )
   from hydra.something import OldModule
   ```

3. Update imports gradually:
   ```python
   # After
   from hydra.something import OldModule  # Now imports from site-packages
   ```

4. Add test to verify no shadowing:
   ```python
   def test_no_hydra_shadowing():
       import hydra
       assert "site-packages" in hydra.__file__
   ```

**Acceptance Criteria**:
- [ ] Legacy import CSV generated
- [ ] Imports categorized by priority
- [ ] P1 imports refactored (if < 10 occurrences)
- [ ] Deprecation warnings added
- [ ] Tests verify no new shadowing introduced
- [ ] `verify_conflicts.py` still passes

**Time Estimate**: 1-2 hours depending on import count

**Risk Mitigation**:
- Refactor incrementally (1-2 imports per commit)
- Run tests after each change
- Keep rollback plan ready

---

### C.3: CI Baseline Age Monitoring (Optional Enhancement)

**Objective**: Add automated baseline freshness checks.

**Implementation**:

1. Add baseline age check to workflow:
```yaml
- name: Check baseline age
  id: baseline-age
  run: |
    if [ -f audit_artifacts/baselines/capabilities_scored.json ]; then
      # Cross-platform age calculation using Python
      AGE_DAYS=$(python -c "import os, time; print(int((time.time() - os.path.getmtime('audit_artifacts/baselines/capabilities_scored.json')) / 86400))")
      echo "age_days=$AGE_DAYS" >> $GITHUB_OUTPUT
      if [ $AGE_DAYS -gt 30 ]; then
        echo "⚠️ Baseline is $AGE_DAYS days old - consider refreshing"
      fi
    fi
```

2. Add conditional baseline refresh on main branch:
```yaml
- name: Refresh baseline if stale
  if: github.ref == 'refs/heads/main' && steps.baseline-age.outputs.age_days > 30
  run: |
    ./scripts/ci/establish_baseline.sh --force
    git config user.name "github-actions[bot]"
    git config user.email "github-actions[bot]@users.noreply.github.com"
    git add audit_artifacts/baselines/capabilities_scored.json
    git commit -m "chore: Auto-refresh audit baseline [skip ci]"
    git push
```

**Acceptance Criteria**:
- [ ] Baseline age calculated correctly
- [ ] Warning logged if > 30 days old
- [ ] Optional: Auto-refresh on main branch
- [ ] Does not break existing workflow

**Time Estimate**: 30 minutes

**Note**: This is optional and can be deferred if time-constrained.

---

### C.4: Final Code Review & Security Scan

**Objective**: Ensure all changes meet quality and security standards.

#### Code Review
```bash
# Request automated code review
# (This will be done via the code_review tool in the agent)
```

**Review Focus**:
- Security: No credentials or secrets introduced
- Quality: Code follows project conventions
- Testing: All new code has test coverage
- Documentation: Changes are documented

#### Security Scan
```bash
# Run CodeQL checker
# (This will be done via the codeql_checker tool in the agent)
```

**Expected**: No new vulnerabilities introduced

**Acceptance Criteria**:
- [ ] Code review comments addressed
- [ ] CodeQL scan clean (or issues documented)
- [ ] Linters pass: `ruff`, `black`, `mypy`
- [ ] Pre-commit hooks pass

---

### C.5: Integration Testing & Final Validation

**Objective**: Comprehensive end-to-end validation.

#### Full Pipeline Test
```bash
# Clean environment
rm -rf audit_artifacts/ audit_run_manifest.json

# Run full pipeline
python scripts/space_traversal/audit_runner.py run

# Validate outputs
ls -lh audit_artifacts/
ls -lh reports/
cat audit_run_manifest.json
```

**Checks**:
- [ ] All artifacts generated (index, facets, capabilities, gaps)
- [ ] Report rendered successfully
- [ ] Manifest includes integrity fields
- [ ] No errors or warnings in logs

#### Regression Test
```bash
# Compare against baseline
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json
```

**Expected**: No unexpected regressions

#### Validation Test Suite
```bash
# Run all validation tests
pytest tests/validation/ -v --tb=short

# Run specific critical tests
pytest tests/validation/test_shadowing.py -v
pytest tests/validation/test_audit_pipeline.py -v
```

**Acceptance Criteria**:
- [ ] All validation tests pass
- [ ] No test skips (or skips documented)
- [ ] No test warnings

---

## Success Criteria

For this iteration to be considered **complete and ready for merge**:

### Validation ✅
- [x] Shadowing prevention verified
- [x] Template integrity verified
- [ ] Determinism validation passed
- [ ] CI pipeline tested end-to-end

### Code Quality ✅
- [x] Documentation complete
- [ ] Code review passed
- [ ] Security scan clean
- [ ] Linters passing

### Functionality 🔄
- [ ] Legacy imports analyzed
- [ ] High-priority imports refactored
- [ ] Tests covering changes
- [ ] No regressions introduced

### CI/CD ✅
- [x] Workflow operational
- [x] Baseline established
- [x] Quality gates enforced
- [ ] Optional: Baseline age monitoring

---

## Rollback Plan

If critical issues arise:

1. **Determinism Failures**:
   - Identify non-deterministic source
   - Fix sorting/ordering
   - Re-validate

2. **Import Refactoring Issues**:
   - Revert specific commits: `git revert <commit-sha>`
   - Restore working import paths
   - Add to known issues list

3. **CI Workflow Issues**:
   - Revert workflow changes: `git checkout HEAD~1 .github/workflows/space-audit.yml`
   - Test locally before pushing
   - Gradual re-introduction of changes

---

## Estimated Timeline

| Task | Time | Priority |
|------|------|----------|
| C.1: Determinism validation | 5 min | High |
| C.2: Legacy import analysis | 30 min | High |
| C.2: Import refactoring | 1-2 hrs | Medium |
| C.3: Baseline age monitoring | 30 min | Low |
| C.4: Code review & security | 15 min | High |
| C.5: Integration testing | 20 min | High |
| **Total** | **3-4 hrs** | - |

**Critical Path**: C.1 → C.4 → C.5 (must complete)  
**Optional**: C.2 (refactoring), C.3 (monitoring)

---

## Post-Merge Actions

After PR merge:

1. **Monitor CI**: Watch first main branch build for issues
2. **Baseline Validation**: Ensure baseline comparison works in CI
3. **Documentation**: Link PR to relevant issues/projects
4. **Announcement**: Notify team of new audit capabilities
5. **Follow-up**: Track legacy import refactoring progress

---

## Agent Self-Application Instructions

When applying this prompt:

1. **Start with validation**: Run C.1 determinism check first
2. **Skip if time-limited**: Defer C.2 (refactoring) and C.3 (monitoring) if needed
3. **Always complete**: C.4 (code review) and C.5 (integration tests)
4. **Document decisions**: Update this file with actual results
5. **Report progress**: Use report_progress after each major task

**Priority Order**: C.1 > C.4 > C.5 > C.2 > C.3

---

## Notes for Reviewers

This iteration completes the audit remediation system validation. Key deliverables:

- ✅ Production-ready CI workflow
- ✅ Comprehensive documentation
- ✅ Quality gates enforced
- 🔄 Determinism validation (pending)
- 🔄 Legacy import strategy (in progress)

**Recommended Approval Path**:
1. Review validation summaries (PartB_Validation_Summary.md)
2. Verify key scripts execute successfully
3. Check CI workflow is operational
4. Approve with optional follow-up for legacy imports

**Questions/Issues**: Contact @mbaetiong or file GitHub issue.
