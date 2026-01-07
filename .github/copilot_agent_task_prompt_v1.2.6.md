# Next Iteration Prompt (v1.2.4) — Legacy Import Reduction & Final Polish

**Generated**: 2025-12-05  
**Author**: Copilot Agent  
**Previous**: v1.2.3 (Determinism Hardening & Baseline Consolidation)

## Status Summary

**Wave 2.1 Complete**: Determinism hardening, baseline consolidation, and validation framework established.

**Current State**:
- ✅ Determinism verified across runs (PASS)
- ✅ Template hash validation (PASS)
- ✅ Shadowing gates enforced (PASS)
- ✅ Baseline established (39 capabilities tracked)
- ✅ Regression diff capture implemented
- ✅ CI workflow enhanced with quality metrics
- ✅ Refactor tooling created (`refactor_imports.py`)
- ⏳ Legacy imports: 99 identified, 0% reduced (target: ≥50%)

## Objectives for v1.2.4

1. **Execute Legacy Import Reduction** (Primary Goal)
2. **Validate CI Workflow End-to-End** 
3. **Polish Documentation**
4. **Final Acceptance Testing**
5. **Generate v1.2.5 Prompt**

---

## Part A: Legacy Import Reduction (≥50% Target)

### A.1: Analysis Phase

Current baseline from `reports/legacy_import_usage.csv`:
- **hydra**: 29 references (29.3%)
- **training**: 53 references (53.5%)
- **tokenization**: 13 references (13.1%)
- **models**: 4 references (4.0%)
- **Total**: 99 references

**Priority Order** (highest impact first):
1. `training` → `src.training` (53 sites)
2. `hydra` → Note: Already in `config_legacy/`, these are imports of the legacy module
3. `tokenization` → `src.tokenization` (13 sites)
4. `models` → `src.modeling` (4 sites)

### A.2: Execution Steps

Use the `refactor_imports.py` tool in batches:

```bash
# 1. Dry-run to preview changes
python scripts/remediation/refactor_imports.py \
  --mapping '{"training":"src.training"}' \
  --dry-run --limit 100 > refactor_training_preview.txt

# 2. Review preview
less refactor_training_preview.txt

# 3. Apply in batches (with automatic test validation)
python scripts/remediation/refactor_imports.py \
  --mapping '{"training":"src.training"}' \
  --apply --batch-size 10

# 4. Repeat for tokenization
python scripts/remediation/refactor_imports.py \
  --mapping '{"tokenization":"src.tokenization"}' \
  --apply --batch-size 5

# 5. Repeat for models
python scripts/remediation/refactor_imports.py \
  --mapping '{"models":"src.modeling"}' \
  --apply --batch-size 5

# 6. Regenerate report
python scripts/remediation/analyze_legacy_usage.py
wc -l reports/legacy_import_usage.csv
```

### A.3: Validation After Each Batch

```bash
# Run tests
pytest tests/validation/ -v

# Verify no regressions
python scripts/space_traversal/audit_runner.py run
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json
```

### A.4: Acceptance

- [ ] Legacy import count reduced from 99 to ≤50 (≥50% reduction)
- [ ] All validation tests pass
- [ ] No score regressions (deltas within ±0.01)
- [ ] CSV before/after attached to PR

---

## Part B: CI Workflow End-to-End Validation

### B.1: Test PR Workflow

Create a test branch and PR to trigger CI:

```bash
# Create test branch
git checkout -b test/ci-validation-v1.2.4
echo "# CI Test" >> CI_TEST.md
git add CI_TEST.md
git commit -m "test: CI workflow validation"
git push origin test/ci-validation-v1.2.4

# Open PR via GitHub CLI or UI
gh pr create --title "test: CI workflow validation" --body "Testing CI gates"
```

### B.2: Verify CI Behavior

Check that the following jobs run:
- [ ] `space-audit-fast` completes and uploads artifacts
- [ ] `quality-gates` runs and posts PR comment with metrics
- [ ] PR comment includes:
  - Low maturity count
  - Legacy import count
  - Shadowing status
  - Regression diff (if baseline exists)

### B.3: Test Baseline Auto-Update

On main branch (after merge):
```bash
# Trigger workflow_dispatch or wait for push to main
# Verify that baseline age check runs
# Verify baseline updates if > 30 days old
```

---

## Part C: Documentation Polish

### C.1: Usage Guide Enhancement

Add determinism validation section to `Usage_Guide.md`:

```markdown
## 8. CI Regression Baseline Workflow

### Establishing a Baseline

After significant capability improvements, establish a new baseline:

\`\`\`bash
bash scripts/ci/establish_baseline.sh --force
git add audit_artifacts/baselines/capabilities_scored.json
git commit -m "feat: Update audit baseline"
git push
\`\`\`

### Determinism Validation

To verify audit pipeline determinism:

\`\`\`bash
python scripts/space_traversal/verify_determinism.py --runs 2
\`\`\`

Expected output: `[PASS] Determinism verified across runs.`

If the check fails:
1. Review the deep_diff output to identify the source of non-determinism
2. Ensure all file iterations use `sorted()`
3. Check that floating-point values are properly rounded
4. Verify that no timestamps leak into compared artifacts
\`\`\`
```

### C.2: Update Traversal_Workflow.md

Document the determinism enhancements in stage S4.

### C.3: Create EXECUTION_LOG.md

Document the complete validation sequence with outputs:

```markdown
# Audit Remediation Execution Log (v1.2.4)

## Date: 2025-12-05

### Validation Sequence

1. **Determinism Check**
   \`\`\`
   $ python scripts/space_traversal/verify_determinism.py --runs 2
   [PASS] Determinism verified across runs.
   \`\`\`

2. **Template Hash**
   \`\`\`
   $ python scripts/space_traversal/validate_template_hash.py
   [PASS] Template hash matches manifest.
   \`\`\`

[... continue for all validation steps ...]
```

---

## Part D: Final Acceptance Testing

### D.1: Full Validation Sequence

Run the complete test battery:

```bash
# 1. Install dependencies
pip install --user --upgrade pyyaml jinja2 hydra-core pytest

# 2. Full audit
python scripts/space_traversal/audit_runner.py run

# 3. Validations
python scripts/space_traversal/validate_template_hash.py
python scripts/space_traversal/verify_determinism.py --runs 2
python scripts/remediation/verify_conflicts.py --expect-site-packages

# 4. Legacy import report
python scripts/remediation/analyze_legacy_usage.py
wc -l reports/legacy_import_usage.csv

# 5. Regression diff
python scripts/space_traversal/audit_runner.py diff \
  --old audit_artifacts/baselines/capabilities_scored.json \
  --new audit_artifacts/capabilities_scored.json

# 6. Tests
pytest -q tests/validation/test_shadowing.py \
       tests/validation/test_shadowing_yaml.py \
       tests/validation/test_legacy_import_report.py \
       tests/validation/test_audit_pipeline.py
```

### D.2: Collect Evidence

Capture outputs to files:
```bash
python scripts/space_traversal/verify_determinism.py --runs 2 > determinism.log 2>&1
python scripts/space_traversal/validate_template_hash.py > template_hash.log 2>&1
python scripts/remediation/verify_conflicts.py --expect-site-packages > shadowing.log 2>&1
pytest tests/validation/ -v > pytest_validation.log 2>&1
```

### D.3: Compute Artifact Hashes

```bash
sha256sum audit_run_manifest.json > artifacts_sha256.txt
sha256sum audit_artifacts/capabilities_scored.json >> artifacts_sha256.txt
sha256sum audit_artifacts/baselines/capabilities_scored.json >> artifacts_sha256.txt
```

---

## Part E: Acceptance Criteria Checklist

All must PASS before proceeding to v1.2.5:

- [ ] **Determinism**: Two runs produce identical normalized outputs
- [ ] **Template Hash**: Manifest hash matches computed Jinja directory hash
- [ ] **Shadowing**: yaml and hydra resolve to site-packages (no local shadowing)
- [ ] **Baseline**: Exists at `audit_artifacts/baselines/capabilities_scored.json`
- [ ] **Regression Diff**: Captured and shows no significant deltas (±0.01 tolerance)
- [ ] **Legacy Imports**: Count reduced by ≥50% (target: ≤50 from 99)
- [ ] **Validation Tests**: All pass or skip safely (minimum 9/10)
- [ ] **Documentation**: Convergence_Runbook.md includes Wave 2.1 summary
- [ ] **CI Workflow**: Tested end-to-end with test PR
- [ ] **Artifacts**: All logs and hashes attached to PR body

---

## Part F: PR Requirements

### F.1: PR Title
```
feat: Complete legacy import reduction and final validation (v1.2.4)
```

### F.2: PR Body Template

```markdown
## Summary

Completes legacy import reduction, validates CI workflow end-to-end, and performs final acceptance testing for the audit remediation system.

## Changes

- Reduced legacy imports from 99 to XX (XX% reduction)
- Validated CI workflow with test PR
- Updated documentation (Usage Guide, Convergence Runbook, Execution Log)
- Ran full validation sequence with all evidence captured

## Validation Results

### Determinism Check
\`\`\`
[attach determinism.log content]
\`\`\`

### Template Hash
\`\`\`
[attach template_hash.log content]
\`\`\`

### Shadowing Gates
\`\`\`
[attach shadowing.log content]
\`\`\`

### Regression Diff
\`\`\`
[attach regression_diff.txt content]
\`\`\`

### Legacy Imports
- **Before**: 99 references
- **After**: XX references  
- **Reduction**: XX%
- **Target Met**: [YES/NO]

### Validation Tests
\`\`\`
[attach pytest_validation.log summary]
\`\`\`

## Artifact Hashes
\`\`\`
[attach artifacts_sha256.txt content]
\`\`\`

## Acceptance Criteria

- [x] Determinism: PASS
- [x] Template Hash: PASS
- [x] Shadowing: PASS
- [x] Baseline: Established
- [x] Regression Diff: Captured
- [x] Legacy Imports: ≥50% reduction
- [x] Tests: ≥90% pass rate
- [x] Documentation: Updated
- [x] CI: Validated
- [x] Artifacts: Attached

## Next Steps

See `.github/copilot_agent_task_prompt.next.md` (v1.2.5) for follow-up iteration.
```

---

## Part G: Generate v1.2.5 Prompt

After all acceptance criteria pass, create the next prompt focusing on:

1. **Production Readiness Review**
2. **Performance Optimization** (if audit runtime > 2 minutes)
3. **Advanced CI Features** (auto-baseline refresh, score trending)
4. **Split-Brain Architecture Resolution** (long-term)

Save to: `.github/copilot_agent_task_prompt.next.md`

---

## Self-Application Instructions

Once v1.2.4 is complete and merged:

```bash
# Automatically open PR for v1.2.5
gh pr create --title "feat: [Auto] Production readiness and optimization (v1.2.5)" \
  --body-file .github/copilot_agent_task_prompt.next.md \
  --base main
```

---

## Success Criteria

This iteration is complete when:
1. All acceptance criteria are PASS
2. PR is open with full evidence attached
3. v1.2.5 prompt is generated and will be auto-applied
4. Reviewer has approved the PR

**Do NOT declare completion until all evidence is attached and acceptance criteria are verified.**

---

End of v1.2.4 Prompt
