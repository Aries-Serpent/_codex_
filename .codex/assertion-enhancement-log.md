# Assertion Enhancement Log

## Campaign Log

### 1) Import-readiness test hardening
- File: `tests/test_codex_ml_readiness_imports.py`
- Change:
  - Introduced `_assert_import_contract(mod, module_name)`
  - Updated import tests to validate:
    - `mod.__name__ == module_name`
    - `hasattr(mod, "__spec__")`
    - module exposes at least one public symbol
- Result:
  - Converted many trivial not-None checks into structural module contract assertions.

### 2) Determinism state assertions
- File: `tests/smoke/test_determinism.py`
- Change:
  - Expanded assertions on returned state dict fields (`seed`, `deterministic`, expected keys).
  - Added test for `seed=None` behavior to ensure no false random-seed reporting.

### 3) Seed utility behavior strengthening
- File: `tests/utils/test_seed.py`
- Change:
  - Added deterministic shuffle test asserting:
    - identical output for same seed
    - different output for different seeds
    - original input immutability
    - output is a permutation of input

## Validation Events
- `rvs_preflight --group quick --changed-only --workers 4`: PASS
- `mutmut run --max-children 4`: blocked (all mutants reported `not checked`)

## Follow-up Actions
- Migrate mutmut config to non-deprecated keys.
- Re-run mutation campaign and add mutant-killing tests for any survivors.
