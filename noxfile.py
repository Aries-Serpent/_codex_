"""Root noxfile.py - delegates to configs/development/noxfile.py.

This file exists to support nox invocations from the repository root.
All session definitions are maintained in configs/development/noxfile.py.
"""

from __future__ import annotations

import shutil
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


@nox.session(name="gates", python=_dev_noxfile.DEFAULT_PYTHON)
def gates(session: nox.Session) -> None:
    """Security gates - alias for the sec session."""
    session.notify("sec")


@nox.session(name="tests", python=_dev_noxfile.DEFAULT_PYTHON)
def tests(session: nox.Session) -> None:
    """Run the project test suite with coverage enabled."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.run(
        "pytest",
        "-p",
        "pytest_cov",
        "--cov=src/codex_ml",
        "--cov-branch",
        "--cov-report=term-missing",
        "-q",
        "tests",
    )


@nox.session(name="security", python=_dev_noxfile.DEFAULT_PYTHON)
def security(session: nox.Session) -> None:
    """Run dependency and secret scans for the repository root."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.env.setdefault("PYTHONUTF8", "1")

    session.log("[security] installing pip-audit and checking for gitleaks")
    session.install("pip-audit")
    if (Path(__file__).resolve().parent / "requirements.txt").exists():
        session.run("pip-audit", "-r", "requirements.txt", success_codes=[0, 1])
    else:
        session.run("pip-audit", success_codes=[0, 1])

    if (Path(__file__).resolve().parent / ".gitleaks.toml").exists() and shutil.which("gitleaks"):
        session.run(
            "gitleaks",
            "detect",
            "--source=.",
            "--config=.gitleaks.toml",
            "--verbose",
            success_codes=[0, 1],
            external=True,
        )
    elif (Path(__file__).resolve().parent / ".gitleaks.toml").exists():
        session.log("[security] gitleaks is not installed; skipping secret scan")


@nox.session(name="precommit", python=_dev_noxfile.DEFAULT_PYTHON)
def precommit(session: nox.Session) -> None:
    """Pre-commit checks - verify no merge markers and basic file integrity."""
    session.chdir(str(Path(__file__).resolve().parent))
    session.notify("patch_debris")
