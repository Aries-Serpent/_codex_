#!/usr/bin/env python
"""
Local task runner for _codex_ (no CI usage). Provides one-command sessions:
  - gates: fences → evaluator → (optional) schema checks → selection guard
  - tests: run repo tests with pytest plugin autoload disabled
  - precommit: run all pre-commit hooks locally
"""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional

import nox

_EVALUATOR = Path("tools/codex_evaluator.py")
_EVALUATOR_RULES = Path("manifests/codex_eval_rules.v3.json")
_SELECTION_GUARD = Path("tools/selection_guard.py")
_SELECTION_RULES = Path("manifests/selection_guard_rules.json")
_SELECTION_DEFAULT_SAMPLE = Path("samples/assistant_message_summary.sample.json")
_SCHEMA_VALIDATE = Path("tools/schema_validate.py")
_SELECTION_SCHEMA = Path("schemas/selection_guard_rules.schema.json")
_EVALUATOR_SCHEMA = Path("schemas/codex_eval_rules.v3.schema.json")
_CONFIG_VALIDATOR = Path("tools/validate_configs.py")


def _resolve_summary(posargs: Iterable[str]) -> Optional[Path]:
    """Best-effort resolution of the summary input path for evaluator/guard."""

    for candidate in posargs:
        path = Path(candidate).expanduser()
        if path.exists():
            return path
    if _SELECTION_DEFAULT_SAMPLE.exists():
        return _SELECTION_DEFAULT_SAMPLE
    return None


def _log_skip(session: nox.Session, step: str, reason: str) -> None:
    session.log(f"[skip] {step}: {reason}")


@nox.session
def gates(session: nox.Session) -> None:
    """Run local gates: structure + scoring + schemas + selection guard."""
    session.install("-r", "requirements-dev.txt")
    # 1) Fence integrity
    session.run("python", "tools/validate_fences.py")
    # 2) Evaluator
    summary = _resolve_summary(session.posargs)
    if not _EVALUATOR.exists():
        _log_skip(session, "codex evaluator", f"missing {_EVALUATOR}")
    elif not _EVALUATOR_RULES.exists():
        _log_skip(session, "codex evaluator", f"missing rules {_EVALUATOR_RULES}")
    elif summary is None:
        _log_skip(
            session,
            "codex evaluator",
            "no summary input (pass a path via `nox -s gates -- path/to/summary.json`)",
        )
    else:
        session.run(
            "python",
            str(_EVALUATOR),
            "--rules",
            str(_EVALUATOR_RULES),
            "--input",
            str(summary),
        )
    # 3) Schema checks (graceful even if jsonschema not installed—tool exits 0 with info)
    if not _SCHEMA_VALIDATE.exists():
        _log_skip(session, "schema validation", f"missing {_SCHEMA_VALIDATE}")
    else:
        schema_args = ["python", str(_SCHEMA_VALIDATE)]
        if _SELECTION_RULES.exists() and _SELECTION_SCHEMA.exists():
            schema_args.extend(
                [
                    "--data",
                    str(_SELECTION_RULES),
                    "--schema",
                    str(_SELECTION_SCHEMA),
                ]
            )
        else:
            _log_skip(
                session,
                "schema validation",
                f"missing selection guard manifest or schema ({_SELECTION_RULES}, {_SELECTION_SCHEMA})",
            )
        if _EVALUATOR_RULES.exists() and _EVALUATOR_SCHEMA.exists():
            schema_args.extend(
                [
                    "--data",
                    str(_EVALUATOR_RULES),
                    "--schema",
                    str(_EVALUATOR_SCHEMA),
                ]
            )
        else:
            _log_skip(
                session,
                "schema validation",
                f"missing evaluator manifest or schema ({_EVALUATOR_RULES}, {_EVALUATOR_SCHEMA})",
            )
        if len(schema_args) > 2:
            session.run(*schema_args)
        else:
            _log_skip(session, "schema validation", "no data/schema pairs available")
    # 4) Selection guard (non-fatal—mirrors scripts/run_local_gates.sh behavior)
    if not _SELECTION_GUARD.exists():
        _log_skip(session, "selection guard", f"missing {_SELECTION_GUARD}")
    elif not _SELECTION_RULES.exists():
        _log_skip(session, "selection guard", f"missing rules {_SELECTION_RULES}")
    elif summary is None:
        _log_skip(
            session,
            "selection guard",
            "no summary input (pass a path via `nox -s gates -- path/to/summary.json`)",
        )
    else:
        session.run(
            "python",
            str(_SELECTION_GUARD),
            "--rules",
            str(_SELECTION_RULES),
            "--input",
            str(summary),
            "--selected",
            "3",
            success_codes=[0, 1, 2],
        )
    if _CONFIG_VALIDATOR.exists():
        session.run("python", str(_CONFIG_VALIDATOR), "--quiet")
    else:
        _log_skip(session, "config schemas", f"missing {_CONFIG_VALIDATOR}")


@nox.session
def tests(session: nox.Session) -> None:
    """Run pytest with plugin autoload disabled (deterministic)."""
    session.install("-r", "requirements-dev.txt")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.run("pytest", "-q")


@nox.session
def status(session: nox.Session) -> None:
    """Render a template-mode STATUS_REPORT.md with verbose output and artifacts."""
    session.install("-r", "requirements-dev.txt")
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.run(
        "python",
        "tools/status_report.py",
        "--summary",
        "samples/assistant_message_summary.sample.json",
        "--selected",
        "3",
        "--template",
        "docs/templates/status_update.md",
        "--branch",
        "local/nox",
        "--pr",
        "local",
        "--verbose",
        "--save-logs",
        "--out",
        "STATUS_REPORT.md",
    )
    # Also emit capability scores
    session.run("python", "tools/status/capability_autodiscovery.py")


@nox.session
def precommit(session: nox.Session) -> None:
    """Run all pre-commit hooks locally (manual)."""
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")


@nox.session(name="model-smoke")
def model_smoke(session: nox.Session) -> None:
    """Instantiate the default model on CPU to catch dtype/device regressions."""
    session.install("-r", "requirements-dev.txt")
    session.run(
        "python",
        "-c",
        (
            "from codex_ml.models.factory import load_model; "
            "load_model({'device': 'cpu', 'dtype': 'float32'})"
        ),
    )


@nox.session(name="status-validate")
def status_validate(session: nox.Session) -> None:
    """Validate the latest generated status JSON against the v1.1 schema (offline)."""
    session.install("-r", "requirements-dev.txt")
    # Validate today's artifact if present
    from datetime import datetime, timezone
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = f"reports/daily/_codex_status_update-{today}.json"
    session.run("python", "tools/status/validate_status_update.py", path)


@nox.session(name="env-snapshot")
def env_snapshot(session: nox.Session) -> None:
    """Emit artifacts/env_snapshot.json for reproducibility evidence."""
    session.install("-r", "requirements-dev.txt")
    session.run("python", "tools/env/export_env_json.py")


@nox.session(name="lint")
def lint(session: nox.Session) -> None:
    """Static linting/format checks (local-only)."""
    session.install("ruff==0.5.7", "black==24.8.0")
    session.run("ruff", "check", ".")
    session.run("black", "--check", ".")
