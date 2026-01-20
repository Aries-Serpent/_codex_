# Path to 100% Coverage Planset: Dependency Conflict Coverage Fix

- **Date**: 2026-01-20
- **Owner**: ai_org_repo_admin
- **Scope**: CI dependency resolution + coverage artifact generation
- **Target**: Restore test execution and coverage artifact creation in `test-comprehensive.yml`.

## Goal
Ensure CI installs succeed, tests run, and coverage artifacts are produced with compatible versions of `coverage` and `pytest-cov`.

## Current Gaps
- Coverage install fails due to incompatible pin.
- No test execution means no coverage output or artifacts.
- Codecov uploads may fail without configured token.

## Plan to 100%
1. **Dependency Alignment**
   - Update coverage pin to `>=7.10.6,<8` in `test-comprehensive.yml`.
   - Verify pip resolves `pytest-cov==7.0.0` with the updated coverage range.

2. **Coverage Artifact Validation**
   - Run tests locally with coverage enabled.
   - Confirm `coverage.xml` and `htmlcov/` generated.

3. **Codecov Upload Verification**
   - Add `token: ${{ secrets.CODECOV_TOKEN }}` to the workflow.
   - Ensure secret is configured in repo settings.

4. **CI Monitoring**
   - Observe next three CI runs for successful dependency installation.
   - Confirm artifact uploads complete without warnings.

## Verification Checklist
- [ ] `python -m pytest tests/ -v` executes without install-time dependency errors.
- [ ] `coverage.xml` and `htmlcov/` exist after tests.
- [ ] Codecov upload step succeeds with token.
- [ ] No artifact_missing warnings in the next 3 CI runs.

## Risks & Mitigations
- **Risk**: Hidden dependency conflicts in other workflows.
  - **Mitigation**: Audit other workflows for `coverage` pins.
- **Risk**: Codecov token not configured.
  - **Mitigation**: Notify maintainers to set secret.

## Next Review
- After first successful CI run with dependency fix applied.
