# CI Coverage Implementation & uv.lock Maintenance Guide

## Overview

This document explains the CI coverage infrastructure, uv.lock maintenance procedures, and troubleshooting steps for the `_codex_` repository.

## Recent Changes (Previous Cycle-11-12)

### CI Workflow Fixes

1. **Removed unsupported nox `-q` flag**
   - **Issue**: Nox CLI does not support the `-q` (quiet) flag
   - **Fix**: Removed `-q` from all `nox -s <session>` invocations in `.github/workflows/ci.yml`
   - **Impact**: All 4 CI job sessions (tests, ml_tests, eval_tests, verify_hygiene) now run successfully

2. **Fixed uv.lock TOML parse errors**
   - **Issue**: `uv.lock` contained 10 malformed header lines (bare environment marker strings)
   - **Fix**: Removed malformed lines and added proper TOML header `version = 1`
   - **Impact**: uv dependency resolution now works correctly in CI

3. **Added uv.lock validation step**
   - **Purpose**: Detect corrupted uv.lock files early in CI pipeline
   - **Location**: `.github/workflows/ci.yml` after Python setup, before environment setup
   - **Behavior**: Fails fast with clear error message if TOML is invalid

4. **Added artifacts directory initialization**
   - **Purpose**: Ensure artifacts directory exists for migration summaries and coverage reports
   - **Location**: Early in CI workflow
   - **Files created**: `artifacts/MIGRATION_SUMMARY.md` placeholder

### Coverage Infrastructure

- **Coverage threshold**: Stored in `.github/coverage_threshold.txt` (current: 96%)
- **Coverage parser**: `.github/scripts/ci_parse_coverage.py`
  - Handles multiple XML formats (coverage.py, percentage variants)
  - Interprets values as percentages (0-100) or fractions (0-1)
  - Returns clear error codes for parse failures

## Manual uv.lock Regeneration Instructions

When the CI uv.lock validation step fails, a maintainer must regenerate the lock file locally.

### Prerequisites
- Python 3.10+ installed
- Git repository cloned locally
- Write access to the repository

### Step-by-Step Instructions

```bash
# 1. Create a fix branch
git checkout -b fix/regen-uv-lock

# 2. Install/upgrade uv
python -m pip install --upgrade uv

# 3. Remove corrupted lock file
rm -f uv.lock

# 4. Regenerate lock file
uv lock

# 5. Verify lock file and sync dependencies
uv sync --locked

# 6. Validate TOML locally
python - <<'PY'
import tomllib
with open('uv.lock', 'rb') as f:
    tomllib.loads(f.read().decode('utf-8'))
print("✓ uv.lock is valid TOML")
PY

# 7. Commit and push
git add uv.lock
git commit -m "chore: regenerate uv.lock to fix malformed TOML"
git push --set-upstream origin fix/regen-uv-lock

# 8. Open PR and merge after CI green
```text

### Verification Commands

After regenerating uv.lock, verify locally:

```bash
# Validate TOML structure
python -c "import tomllib; tomllib.loads(open('uv.lock','r').read()); print('✓ uv.lock OK')"

# Run nox sessions
python -m pip install --upgrade nox
nox -s verify_hygiene
nox -s tests
nox -s evidence_check

# Test coverage parser (if coverage.xml exists)
python .github/scripts/ci_parse_coverage.py artifacts/coverage.xml
```text

## Troubleshooting

### uv.lock TOML Parse Error

**Symptom**: CI fails with "TOML parse error at line X, column Y"

**Cause**: The lock file contains invalid TOML syntax, often from:
- Manual edits
- Merge conflicts
- Corrupted uv tool state

**Solution**: Follow "Manual uv.lock Regeneration Instructions" above

### Nox "unrecognized arguments" Error

**Symptom**: CI fails with "nox: error: unrecognized arguments: -q"

**Cause**: The installed nox version doesn't support the `-q` flag

**Solution**: Already fixed in `.github/workflows/ci.yml` (commit dee5f91)

### Missing artifacts Directory

**Symptom**: CI fails when trying to write to `artifacts/`

**Cause**: Directory not created in workflow

**Solution**: Already fixed - workflow now creates `artifacts/` early (commit dee5f91+)

## Definition of Done (DoD) Checklist

When implementing CI changes, verify:

- [ ] All workflow files have `-q` flag removed from nox invocations
- [ ] uv.lock validation step present in workflows that use uv
- [ ] artifacts directory created early in workflow
- [ ] MIGRATION_SUMMARY.md placeholder created in CI
- [ ] Coverage parser exists and handles multiple XML formats
- [ ] Coverage threshold file exists (`.github/coverage_threshold.txt`)
- [ ] Artifacts directory ignored in `.gitignore`
- [ ] Documentation updated (this file)
- [ ] Manual uv.lock regen instructions provided
- [ ] CI passes with green status

## File Locations

| File | Purpose |
|------|---------|
| `.github/workflows/ci.yml` | Main CI workflow with segmented sessions |
| `.github/scripts/ci_parse_coverage.py` | Coverage XML parser |
| `.github/coverage_threshold.txt` | Coverage threshold (96%) |
| `.github/docs/CI_Coverage_Implementation_Copilot.md` | This file |
| `.gitignore` | Ensures `artifacts/` not committed |
| `uv.lock` | Python dependency lock file |

## Dependencies

### Segmented Requirements

The repository uses segmented dependency management:

- **Baseline**: Core dependencies in `pyproject.toml`
- **ML**: `requirements-ml-cpu.txt` (torch, transformers)
- **Eval**: `requirements-eval.txt` (metrics, evaluation tools)
- **Notebook**: `requirements-notebook.txt` (visualization, interactive)

### Nox Sessions

- `tests`: Baseline tests (no ML dependencies)
- `ml_tests`: ML-specific tests
- `eval_tests`: Evaluation metrics tests
- `verify_hygiene`: Dependency hygiene checks
- `evidence_check`: Validates evidence JSONL schema

## Contact

For questions or issues:
- Review this documentation
- Check CI workflow logs
- Consult `AGENTS.md` for additional guidelines
