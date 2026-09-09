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
LEGACY_TEST_ENV_GUARD = "PYTEST_DISABLE_PLUGIN_AUTOLOAD"
LEGACY_REPO_TEST_TOOLS = (
    "tools/validate_fences.py",
    "tools/codex_evaluator.py",
    "tools/selection_guard.py",
    "tools/schema_validate.py",
)
LEGACY_TEST_COVERAGE_TARGETS = ("--cov=src", "--cov=training")


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


# The canonical registry in configs/development/noxfile.py owns the live
# session registrations. Keep this root wrapper as a thin compatibility shim so
# we do not re-register the same session names and trigger nox warnings.
def tests(session: nox.Session) -> None:
    """Compatibility adapter for the canonical tests session."""
    _run_dev_session(session, "tests")


def lint(session: nox.Session) -> None:
    """Compatibility adapter for the canonical lint session."""
    _run_dev_session(session, "lint")


def typecheck(session: nox.Session) -> None:
    """Compatibility adapter for the canonical typecheck session."""
    _run_dev_session(session, "typecheck")


def workflow_policy(session: nox.Session) -> None:
    """Compatibility adapter for the canonical workflow_policy session."""
    _run_dev_session(session, "workflow_policy")


def gates(session: nox.Session) -> None:
    """Compatibility adapter for the canonical gates session."""
    session.chdir(str(REPO_ROOT))
    session.log(
        "gates adapter delegates to the canonical nox registry; no duplicate "
        "session registration occurs here."
    )
    _run_dev_session(session, "gates")


def precommit(session: nox.Session) -> None:
    """Compatibility adapter for the canonical precommit session."""
    session.chdir(str(REPO_ROOT))
    session.log(
        "precommit adapter delegates to the canonical nox registry; no duplicate "
        "session registration occurs here."
    )
    _run_dev_session(session, "precommit")


@nox.session(name="security", python=_dev_noxfile.DEFAULT_PYTHON)
def security(session: nox.Session) -> None:
    """Compatibility adapter for the canonical security gate session."""
    session.chdir(str(REPO_ROOT))
    session.log(
        "security adapter delegates to the canonical sec session; it still runs "
        "bandit, semgrep, detect-secrets, pip-audit, and gitleaks."
    )
    _run_dev_session(session, "sec")


def coverage(session: nox.Session) -> None:
    """Compatibility adapter for the canonical coverage session."""
    _run_dev_session(session, "coverage")
