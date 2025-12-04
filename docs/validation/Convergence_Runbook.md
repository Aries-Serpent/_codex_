# [Runbook]: Convergence & Audit Verification
> Generated: 2025-12-04 | Author: mbaetiong

## Commands
| Task | Command |
|------|---------|
| Full pipeline | `python scripts/space_traversal/audit_runner.py run` |
| Fast path | `make space-audit-fast` |
| Cleanup root (dry-run) | `python scripts/remediation/cleanup_root.py --dry-run` |
| Cleanup root (execute) | `python scripts/remediation/cleanup_root.py --yes` |
| Verify conflicts | `python scripts/remediation/verify_conflicts.py --expect-site-packages` |
| Legacy report | `python scripts/remediation/analyze_legacy_usage.py` |
| Determinism check | `python scripts/space_traversal/verify_determinism.py --runs 2` |
| Validate template hash | `python scripts/space_traversal/validate_template_hash.py` |
| Run shadowing test | `pytest -q tests/validation/test_shadowing.py` |

## Acceptance Criteria
- **Zero Root Imports** (from src/), or documented exceptions.
- **Test Parity**: CI passes when PYTHONPATH restricted to src/.
- **Manifest Integrity**: audit_run_manifest.json includes repo_root_sha and template_hash.
- **Determinism**: two successive runs produce identical repo_root_sha and artifacts (ignoring timestamps).
- **Shadowing**: hydra resolves to site-packages; otherwise fail with remediation guidance.

## Workflow Overview

### Phase 1: Sanitation
Clean up the repository root directory from clutter:
```bash
# Preview what will be moved
python scripts/remediation/cleanup_root.py --dry-run

# Execute the cleanup
python scripts/remediation/cleanup_root.py --yes
```

This moves all `*_REPORT.md` and `*_SUMMARY.md` files from the repository root to `reports/archive/`.

### Phase 2: Structural Analysis
Run the audit pipeline to analyze the codebase structure:
```bash
# Full audit (all stages S1-S7)
python scripts/space_traversal/audit_runner.py run

# Fast path (skip facet grouping and gap analysis)
make space-audit-fast
```

**Expected Outputs:**
- `audit_artifacts/context_index.json` - File inventory
- `audit_artifacts/capabilities_raw.json` - Raw capability detection
- `audit_artifacts/capabilities_scored.json` - Scored capabilities
- `audit_artifacts/gaps.json` - Low-maturity capabilities
- `reports/capability_matrix_<timestamp>.md` - Human-readable report
- `audit_run_manifest.json` - Integrity manifest

### Phase 3: Conflict Verification
Check for import shadowing and split-brain conflicts:
```bash
# Verify that hydra imports resolve to site-packages
python scripts/remediation/verify_conflicts.py --expect-site-packages

# Generate legacy import usage report
python scripts/remediation/analyze_legacy_usage.py
```

Review the generated `reports/legacy_import_usage.csv` for imports that need refactoring.

### Phase 4: Quality Gates
Verify determinism and integrity:
```bash
# Run pipeline twice and compare artifacts
python scripts/space_traversal/verify_determinism.py --runs 2

# Validate template hash
python scripts/space_traversal/validate_template_hash.py

# Run validation tests
pytest tests/validation/ -v
```

## Troubleshooting

### Hydra Shadowing Detected
**Symptom**: `verify_conflicts.py` fails with "Local 'hydra/' directory is shadowing the installed library."

**Remediation**:
1. Rename root `hydra/` directory:
   ```bash
   git mv hydra config_legacy
   ```
2. Update imports in the codebase to use `config_legacy` instead
3. Or move the directory under `src/`:
   ```bash
   git mv hydra src/codex_conf
   ```

### Split-Brain Ambiguity
**Symptom**: Both `training` and `src.training` are importable.

**Remediation**:
1. Review `reports/legacy_import_usage.csv` to find all legacy imports
2. Refactor imports to use `src.training` instead of `training`
3. Add deprecation warnings to root modules:
   ```python
   import warnings
   warnings.warn("Module 'training' is deprecated. Use 'src.training' instead.", DeprecationWarning)
   ```

### Determinism Failure
**Symptom**: `verify_determinism.py` reports mismatches between runs.

**Possible Causes**:
- Non-deterministic file iteration (use `sorted()`)
- Timestamp leaking into artifact comparison (should be filtered)
- Dynamic detector ordering issues

**Remediation**:
1. Inspect the specific artifact that differs
2. Ensure all file iterations use `sorted()`
3. Check that timestamp fields are properly excluded in comparison

### Template Hash Mismatch
**Symptom**: `validate_template_hash.py` warns about hash mismatch.

**Remediation**:
Re-run the full audit pipeline to regenerate the manifest:
```bash
python scripts/space_traversal/audit_runner.py run
```

## Reviewer Checklist
- [ ] Scripts enhanced with CLI flags and idempotent behavior.
- [ ] Structural-integrity detector emits balanced evidence with limit.
- [ ] Legacy import CSV exists and has the correct header.
- [ ] Tests present and pass locally (or skip safely).
- [ ] CI workflow present and enforces gates.
- [ ] Documentation updated (Runbook, Usage Guide).
- [ ] Sample artifacts attached (at least capabilities_scored.json and manifest).
- [ ] No security vulnerabilities introduced.
- [ ] All linters and formatters pass.
- [ ] Dry-run outputs reviewed and validated.

## Rollback Plan
If the changes cause build failures or test regressions:

1. **Hydra shadowing issues**: 
   ```bash
   git mv config_legacy hydra  # Restore original structure
   ```

2. **Import breakage**:
   - Revert import path changes
   - Keep both root and src modules temporarily with symlinks if needed

3. **Determinism failures**:
   - Use `git reset --soft HEAD~1` to undo commits
   - Fix sorting/ordering issues
   - Re-run verification

4. **Score regressions**:
   ```bash
   # Compare old and new scores
   python scripts/space_traversal/audit_runner.py diff \
     --old audit_artifacts/capabilities_scored_old.json \
     --new audit_artifacts/capabilities_scored_new.json
   ```
   Adjust patterns or weights in `.copilot-space/workflow.yaml` if needed.

## CI Integration
The audit workflow runs automatically on:
- **Pull Requests**: Fast audit + conflict verification
- **Main branch pushes**: Full audit + determinism check

Review the CI logs to ensure all quality gates pass.

## Security Summary
All scripts operate offline and do not make network calls. They:
- Read files from the repository
- Generate reports and artifacts
- Perform static analysis only
- Do not execute arbitrary code from the repository

The shadowing test ensures that standard library packages are not accidentally overridden by local directories.

## Next Steps
After completing this runbook:
1. Review generated artifacts in `audit_artifacts/` and `reports/`
2. Address any low-maturity capabilities identified in `gaps.json`
3. Refactor legacy imports identified in `legacy_import_usage.csv`
4. Update documentation to reflect new import patterns
5. Monitor CI for any regressions

## Support
For issues or questions:
- Check the logs in `audit_artifacts/` for detailed error messages
- Review the detector implementations in `scripts/space_traversal/detectors/`
- Consult `docs/validation/Usage_Guide.md` for additional context
