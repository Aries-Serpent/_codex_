"""Repository-root nox entrypoint.

The canonical session registry lives in ``configs/development/noxfile.py``.
This file intentionally avoids re-registering the same sessions so nox only has
one authoritative registry to discover.
"""

from __future__ import annotations

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

DEV_NOXFILE_PATH = Path(__file__).resolve().parent / "configs" / "development" / "noxfile.py"

spec = spec_from_file_location("_dev_noxfile", DEV_NOXFILE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Could not load noxfile from {DEV_NOXFILE_PATH}")

_dev_noxfile = module_from_spec(spec)
sys.modules["_dev_noxfile"] = _dev_noxfile
spec.loader.exec_module(_dev_noxfile)

import nox  # noqa: E402

nox.options.reuse_existing_virtualenvs = _dev_noxfile.nox.options.reuse_existing_virtualenvs
nox.options.stop_on_first_error = _dev_noxfile.nox.options.stop_on_first_error
nox.options.error_on_missing_interpreters = _dev_noxfile.nox.options.error_on_missing_interpreters

REPO_ROOT = Path(__file__).resolve().parent


@nox.session(name="security", python=_dev_noxfile.DEFAULT_PYTHON)
def security(session: nox.Session) -> None:
    """Compatibility alias for the repo-level security gate."""
    session.chdir(str(REPO_ROOT))
    session.log("security alias delegates to sec; the canonical stack runs bandit, semgrep, detect-secrets, pip-audit, and gitleaks.")
    session.notify("sec")
