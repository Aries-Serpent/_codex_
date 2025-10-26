#!/usr/bin/env python
"""
Local task runner for _codex_ (no CI usage). Provides one-command sessions:
  - gates: fences → evaluator → (optional) schema checks → selection guard
  - tests: run repo tests with pytest plugin autoload disabled
  - precommit: run all pre-commit hooks locally
"""
from __future__ import annotations

import nox


@nox.session
def gates(session: nox.Session) -> None:
    """Run local gates: structure + scoring + schemas + selection guard."""
    session.install("-r", "requirements-dev.txt")
    # 1) Fence integrity
    session.run("python", "tools/validate_fences.py")
    # 2) Evaluator
    session.run(
        "python",
        "tools/codex_evaluator.py",
        "--rules",
        "manifests/codex_eval_rules.v3.json",
        "--input",
        "samples/assistant_message_summary.sample.json",
    )
    # 3) Schema checks (graceful even if jsonschema not installed—tool exits 0 with info)
    session.run(
        "python",
        "tools/schema_validate.py",
        "--data",
        "manifests/selection_guard_rules.json",
        "--schema",
        "schemas/selection_guard_rules.schema.json",
        "--data",
        "manifests/codex_eval_rules.v3.json",
        "--schema",
        "schemas/codex_eval_rules.v3.schema.json",
    )
    # 4) Selection guard (non-fatal—mirrors scripts/run_local_gates.sh behavior)
    session.run(
        "python",
        "tools/selection_guard.py",
        "--rules",
        "manifests/selection_guard_rules.json",
        "--input",
        "samples/assistant_message_summary.sample.json",
        "--selected",
        "3",
        success_codes=[0, 1, 2],
    )


@nox.session
def tests(session: nox.Session) -> None:
    """Run pytest with plugin autoload disabled (deterministic)."""
    session.install("-r", "requirements-dev.txt")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.run("pytest", "-q")


@nox.session
def precommit(session: nox.Session) -> None:
    """Run all pre-commit hooks locally (manual)."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")
