# [Validation]: Coverage Enforcement for Targeted Modules
> Generated: 2024-11-11  
> Roles: QA Lead, Developer  

## Policy

- **Repository-level fail-under**: 95% (pytest-cov)
- **Targeted modules per-file threshold goal**: 96–99% for:
  - `src/codex_ml/evaluation/loop.py`
  - `src/codex_ml/evaluation/cli.py`
  - `src/codex_ml/checkpointing/bestk.py`
  - `src/codex_ml/logging/registry.py`
  - `src/codex/ast/cli.py`
  - `tools/validate_experiments.py`

## How to Enforce

1. Run tests with coverage:
   ```bash
   pytest --cov=src/codex_ml --cov=src/codex --cov-report=xml:artifacts/coverage.xml --cov-report=term-missing --cov-fail-under=95
   ```

2. Optionally run `tools/check_coverage.py` to validate per-file thresholds by parsing `artifacts/coverage.xml`.

## Coverage Targets

| Module | Target | Status |
|--------|--------|--------|
| evaluation/loop.py | 96% | Target |
| evaluation/cli.py | 96% | Target |
| checkpointing/bestk.py | 98% | Target |
| logging/registry.py | 95% | Target |
| ast/cli.py | 95% | Target |
| validate_experiments.py | 96% | Target |

## Next Iteration Goals

- Add edge case tests for 99% coverage
- Add golden baseline tests for regression prevention
- Add determinism tests for reproducibility

## Artifacts

- `artifacts/coverage.xml` - Coverage report for CI
- `htmlcov/index.html` - Coverage HTML report (local)
