# Local Checks & Tooling — Run 1 (2025-09-22)

## Environment Preparation

| Step | Command | Notes |
| --- | --- | --- |
| Create virtualenv | `python3 -m venv .venv` | Fresh interpreter for offline tools. |
| Activate environment | `. .venv/bin/activate` | Shell activation for this session. |
| Install dev stack | `pip install -r requirements-dev.txt` | Pulled in linters, pytest, semgrep, etc. |
| Install pre-commit hooks | `pre-commit install` | Ensures local hooks cover pre-commit, pre-push, prepare-commit-msg. |

## Quality Gates to Run After Changes

| Category | Command | Purpose |
| --- | --- | --- |
| Markdown fences | `python tools/validate_fences.py --strict-inner` | Verifies audit docs, reports, and logs use language-tagged fences. |
| Pre-commit suite | `pre-commit run --all-files` | Runs configured lint/type/test hooks (including the fence gate). |
| Pytest spot check | `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/tools/test_validate_fences.py` | Sanity check for the new fence validator (full suite available via `nox -s tests`). |

## Notes

- CI remains disabled; all commands must run locally/offline.
- Legacy markdown in `.codex/` violates fence rules—left untouched this run but excluded from the validator’s default scope.
