"""Repository-root nox entrypoint.

The canonical session registry lives in ``configs/development/noxfile.py``.
This wrapper keeps the live workflow commands stable while exposing the active
repo-level aliases that the workflow contract expects at the repository root.
"""

from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

import nox

DEV_NOXFILE_PATH = Path(__file__).resolve().parent / "configs" / "development" / "noxfile.py"

spec = spec_from_file_location("_dev_noxfile", DEV_NOXFILE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load noxfile from {DEV_NOXFILE_PATH}")

_dev_noxfile = module_from_spec(spec)
sys.modules["_dev_noxfile"] = _dev_noxfile
spec.loader.exec_module(_dev_noxfile)

nox.options.reuse_existing_virtualenvs = _dev_noxfile.nox.options.reuse_existing_virtualenvs
nox.options.stop_on_first_error = _dev_noxfile.nox.options.stop_on_first_error
nox.options.error_on_missing_interpreters = _dev_noxfile.nox.options.error_on_missing_interpreters

REPO_ROOT = Path(__file__).resolve().parent


def _run_dev_session(session: nox.Session, name: str) -> None:
    """Execute the canonical nox session implementation for the given name."""
    func = getattr(_dev_noxfile, name)
    if not callable(func):
        raise RuntimeError(f"Canonical nox registry does not define {name!r}")
    func(session)


def _run_repo_tool(
    session: nox.Session,
    script: str,
    *args: str,
) -> None:
    """Execute an in-repo validation helper with the arguments it expects."""
    script_path = REPO_ROOT / script
    if script_path.exists():
        session.run("python", str(script_path), *args, external=True)


# Keep direct-call compatibility for repo tests while allowing the canonical
# registry in configs/development/noxfile.py to remain the single source of
# session registration for `nox -l` / `nox -s ...`.
@nox.session(name="tests", python=_dev_noxfile.DEFAULT_PYTHON)
def tests(session: nox.Session) -> None:
    """Repository-level test gate used by the live workflow surface."""
    session.chdir(str(REPO_ROOT))
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

    rules_path = REPO_ROOT / "manifests" / "codex_eval_rules.v3.json"
    sample_path = REPO_ROOT / "samples" / "assistant_message_summary.sample.json"
    selection_rules_path = REPO_ROOT / "manifests" / "selection_guard_rules.json"
    schema_validate_pairs = (
        (selection_rules_path, REPO_ROOT / "schemas" / "selection_guard_rules.schema.json"),
        (rules_path, REPO_ROOT / "schemas" / "codex_eval_rules.v3.schema.json"),
    )

    _run_repo_tool(session, "tools/validate_fences.py")
    _run_repo_tool(
        session,
        "tools/codex_evaluator.py",
        "--rules",
        str(rules_path),
        "--input",
        str(sample_path),
    )
    _run_repo_tool(
        session,
        "tools/selection_guard.py",
        "--rules",
        str(selection_rules_path),
        "--input",
        str(sample_path),
    )
    _run_repo_tool(
        session,
        "tools/schema_validate.py",
        *(
            arg
            for pair in schema_validate_pairs
            for arg in ("--data", str(pair[0]), "--schema", str(pair[1]))
        ),
    )
    session.install("-e", ".[full]")
    session.run(
        "pytest",
        "-q",
        "--cov=src",
        "--cov=training",
        "--cov-report=term-missing",
        "--cov-fail-under=3.5",
        "tests",
    )


@nox.session(name="lint", python=_dev_noxfile.DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """Compatibility alias for the canonical lint session."""
    _run_dev_session(session, "lint")


@nox.session(name="typecheck", python=_dev_noxfile.DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Compatibility alias for the canonical typecheck session."""
    _run_dev_session(session, "typecheck")


def workflow_policy(session: nox.Session) -> None:
    """Compatibility alias for workflow contract validation."""
    _run_dev_session(session, "workflow_policy")


def gates(session: nox.Session) -> None:
    """Compatibility alias for the repo-level security gate."""
    session.chdir(str(REPO_ROOT))
    session.log(
        "gates alias delegates to sec; the canonical stack runs bandit, "
        "semgrep, detect-secrets, pip-audit, and gitleaks."
    )
    _run_dev_session(session, "gates")


def precommit(session: nox.Session) -> None:
    """Compatibility alias for the repo-level patch-debris guard."""
    session.chdir(str(REPO_ROOT))
    session.log(
        "precommit alias delegates to patch_debris to prevent merge markers "
        "and patch debris."
    )
    _run_dev_session(session, "precommit")


@nox.session(name="security", python=_dev_noxfile.DEFAULT_PYTHON)
def security(session: nox.Session) -> None:
    """Compatibility alias for the repo-level security gate."""
    session.chdir(str(REPO_ROOT))
    session.log(
        "security alias delegates to sec; the canonical stack runs bandit, "
        "semgrep, detect-secrets, pip-audit, and gitleaks."
    )
    _run_dev_session(session, "sec")


def coverage(session: nox.Session) -> None:
    """Compatibility alias for the canonical coverage session."""
    _run_dev_session(session, "coverage")
