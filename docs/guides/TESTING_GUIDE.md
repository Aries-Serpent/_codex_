# Testing & Coverage Guide

## Coverage Gates

Codex enforces a **minimum 3.5% code coverage** requirement to keep the test
suite healthy even in lean environments. The low bar ensures the baseline suite
never regresses to zero coverage while accommodating air-gapped or resource
constrained runners.

### Running Tests

**Option 1: pytest (recommended)**
```bash
pytest --cov=src/codex_ml --cov-fail-under=3.5
```

**Option 2: Makefile**
```bash
make -C config test
```

**Option 3: nox**
```bash
nox --noxfile config/noxfile.py -s tests
```

**Option 4: Validate enforcement**
```bash
python scripts/validate_coverage_gates.py
```

## Coverage Failures

If coverage falls below 3.5%:

1. Add or update tests that exercise the uncovered code paths.
2. Target 5–10% coverage for new submissions to buffer the minimum gate.
3. Inspect gaps with an HTML report: `pytest --cov-report=html`.
4. Commit the new tests alongside the fixes that require them.

## Future Coverage Targets

| Phase | Target |
|-------|--------|
| Phase 2–3 | 5–10% |
| Phase 4+ | 20–30% |
| Production hardening | 70–90% |

Tracking coverage progression early keeps later phases focused on meaningful
quality improvements rather than emergency backfilling.
