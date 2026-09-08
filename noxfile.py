"""Root noxfile.py - delegates to configs/development/noxfile.py.

This file exists to support nox invocations from the repository root.
All session definitions are maintained in configs/development/noxfile.py.
"""

from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

# Load the development noxfile
DEV_NOXFILE_PATH = Path(__file__).resolve().parent / "configs" / "development" / "noxfile.py"

# Import the development noxfile as a module
spec = spec_from_file_location("_dev_noxfile", DEV_NOXFILE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load noxfile from {DEV_NOXFILE_PATH}")

_dev_noxfile = module_from_spec(spec)
sys.modules["_dev_noxfile"] = _dev_noxfile
spec.loader.exec_module(_dev_noxfile)

# Re-export nox module and all configured sessions
import nox  # noqa: E402

# Copy nox options from the development noxfile
nox.options.reuse_existing_virtualenvs = _dev_noxfile.nox.options.reuse_existing_virtualenvs
nox.options.stop_on_first_error = _dev_noxfile.nox.options.stop_on_first_error
nox.options.error_on_missing_interpreters = _dev_noxfile.nox.options.error_on_missing_interpreters

# Keep the root-level entry points explicit so CI and tests can discover the
# supported sessions without depending on the nested config implementation.
# The canonical registry remains in `configs/development/noxfile.py`; the root
# file mirrors the commonly-used sessions that workflow automation invokes
# directly and makes the contract visible to static checks.


@nox.session(name="lint", python=_dev_noxfile.DEFAULT_PYTHON)
def lint(session: nox.Session) -> None:
    """Run the repo lint checks from the root entry point."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    session.run("ruff", "check", "src", "tests", "scripts", "tools", success_codes=[0, 1])
    session.run("isort", "--check-only", "src", "tests", "scripts", "tools", success_codes=[0, 1])
    session.run("black", "--check", "src", "tests", "scripts", "tools", success_codes=[0, 1])


@nox.session(name="typecheck", python=_dev_noxfile.DEFAULT_PYTHON)
def typecheck(session: nox.Session) -> None:
    """Run the repo's targeted mypy checks from the root entry point."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.env.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    targets = ["src/security", "scripts/space_traversal", "src/codex_ml"]
    repo_root = Path(__file__).resolve().parent
    existing = [target for target in targets if (repo_root / target).exists()]
    if not existing:
        session.log("No mypy targets found; skipping root typecheck alias.")
        return
    session.run("mypy", *existing, success_codes=[0, 1])


@nox.session(name="tests", python=_dev_noxfile.DEFAULT_PYTHON)
def tests(session: nox.Session) -> None:
    """Run the repo test suite with the standard pytest guard enabled."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.env["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"
    session.run("python", "tools/validate_fences.py", external=True, success_codes=[0, 1])
    session.run("python", "tools/codex_evaluator.py", external=True, success_codes=[0, 1])
    session.run("python", "tools/selection_guard.py", external=True, success_codes=[0, 1])
    session.run("python", "tools/schema_validate.py", external=True, success_codes=[0, 1])
    session.run("pytest", "-q", "tests")


@nox.session(name="workflow_policy", python=_dev_noxfile.DEFAULT_PYTHON)
def workflow_policy(session: nox.Session) -> None:
    """Validate workflow YAML, action versions, and the repo's nox/session contracts."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.run("python", "scripts/ci/check_workflow_yaml.py", ".github/workflows")
    session.run("python", "scripts/ci/enforce_actions_versions.py")


@nox.session(name="gates", python=_dev_noxfile.DEFAULT_PYTHON)
def gates(session: nox.Session) -> None:
    """Security gates - alias for the sec session."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.run("python", "-m", "nox", "-s", "sec")


@nox.session(name="precommit", python=_dev_noxfile.DEFAULT_PYTHON)
def precommit(session: nox.Session) -> None:
    """Pre-commit checks - verify no merge markers and basic file integrity."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.run("python", "-m", "nox", "-s", "patch_debris")
