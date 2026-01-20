# Pytest Coverage Dependency Fix (2026-01-20)

## Summary
Resolved a critical dependency conflict blocking CI workflows where `coverage==7.6.0` was pinned while `pytest-cov==7.0.0` requires `coverage>=7.10.6`. Updated the workflow to allow `coverage>=7.10.6,<8` and added the Codecov token reference for authenticated uploads.

## Root Cause
- `coverage==7.6.0` pin in `test-comprehensive.yml`.
- `pytest-cov==7.0.0` requires `coverage>=7.10.6`.
- Pip resolution failed, preventing tests from running and coverage artifacts from generating.

## Resolution Applied
- Updated coverage requirement to `coverage>=7.10.6,<8`.
- Added `token: ${{ secrets.CODECOV_TOKEN }}` to Codecov upload step (token must be set in repo secrets).

## Verification Plan
- Confirm dependency installation completes in CI for Python 3.11/3.12.
- Ensure `python -m pytest tests/ -v` executes (install step no longer fails).
- Validate coverage artifacts (`coverage.xml`, `htmlcov/`) are generated and uploaded.
- Watch for removal of artifact_missing warnings across the next 3 runs.

## Follow-up Actions
- Ensure CODECOV_TOKEN is configured in GitHub Secrets.
- Monitor CI runs for `test-comprehensive.yml` and confirm artifacts.
- Escalate if any dependency resolver errors persist.
