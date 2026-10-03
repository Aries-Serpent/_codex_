# Mutation Testing Report

## Scope
- Target modules: `src/codex_ml/utils/determinism.py`, `src/codex_ml/utils/seed.py`
- Supporting tests:
  - `tests/unit/test_gap22_mutation_killers.py`
  - `tests/smoke/test_determinism.py`
  - `tests/utils/test_seed.py`

## Execution
- Installed tooling: `mutmut`, `pytest-timeout`
- Command:
  - `python -m mutmut run --max-children 4`
- Mutmut baseline test phase passed (`28 passed`), but mutant-to-test mapping failed.

## Results
- Total generated mutants: **189**
- Killed: **0**
- Survived: **0**
- Not checked: **189**
- Achieved mutation score: **0.0% (blocked)**
- Target score: **>=85%**

## Gap Analysis (Why 85% was not achievable in this run)
1. Mutmut reported: *“could not find any test case for any mutant”*.
2. Repository uses deprecated mutmut config keys (`paths_to_mutate`, `tests_dir`) and invalid glob in `do_not_mutate` (`*.pyc`), which likely broke test selection/mapping on current mutmut.
3. Because all mutants were `not checked`, no meaningful kill ratio could be computed this cycle.

## Recommended Remediation
1. Update `[tool.mutmut]` config in `pyproject.toml` to current schema:
   - rename `paths_to_mutate` -> `source_paths`
   - replace `tests_dir` with `pytest_add_cli_args_test_selection`
2. Fix `do_not_mutate` glob patterns.
3. Re-run mutation campaign after config migration and keep same targeted modules/tests for comparability.

## Parallel Work Confirmation
- Mutation run executed in parallel with quick changed-only validation work.
