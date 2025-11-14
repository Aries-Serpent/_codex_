# [Doc]: CI Pytest-Cov Plugin Fix — Explicit Enable & Env Override

## Why tests failed
- Pytest could not recognize --cov flags because the pytest-cov plugin was not loaded (plugin autoload disabled in some environments).

## Fix Strategy (defense-in-depth)
- Explicit plugin enable: `-p pytest_cov` in nox coverage session.
- Explicit install: session installs `pytest` and `pytest-cov`.
- Env override in CI: `PYTEST_DISABLE_PLUGIN_AUTOLOAD=0` for coverage job.
- Plugin import in conftest: `pytest_plugins = ["pytest_cov"]`.

## Verification
- "unrecognized arguments: --cov" no longer appears.
- coverage.xml and htmlcov are generated under artifacts/.
- Repo coverage gate enforced at 95%; targeted files at 96%+.

— End —
