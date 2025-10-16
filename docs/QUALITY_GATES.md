# Local Quality Gates

All gates are **offline-friendly** and run without hosted services:

```bash
nox -s tests        # pytest + coverage (fail-under 70%)
nox -s cli_smoke    # Typer CLI smoke (version, split, checkpoint, MLflow file backend)
nox -s tracking_smoke
nox -s lint         # Ruff/Black/isort (offline)
nox -s typecheck    # mypy
```

Additional tooling:

* `nox -s sast` — Bandit, Semgrep (local rules), and `pip-audit`.
* `CODEX_COV_FLOOR=75 nox -s coverage` — bump the coverage floor for focused sweeps.
* `pre-commit run --all-files` — formatters and secret detection.
