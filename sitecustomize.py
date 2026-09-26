"""Repository startup shim for Python auto-import hooks.

Python imports ``sitecustomize`` automatically when it can be found on the
startup path. This repository keeps the operational bootstrap under
``configs/sitecustomize.py`` so a thin root-level shim is sufficient to keep the
ML/RAG environment, offline tracking defaults, and ``src`` path injection active
without requiring manual ``PYTHONPATH`` editing in local or CI sessions.

Keeping this file small also isolates the startup behavior from the main package
logic and avoids accidental import drift in the security gate.
"""

from __future__ import annotations

import importlib.abc
import importlib.util
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent


class _SiteCustomizeFinder(importlib.abc.MetaPathFinder):
    """Keep the root shim reloadable even when pytest strips repo root from sys.path."""

    def find_spec(self, fullname, path=None, target=None):
        if fullname != "sitecustomize":
            return None
        candidate = _REPO_ROOT / "sitecustomize.py"
        if not candidate.exists():
            return None
        return importlib.util.spec_from_file_location(fullname, candidate)


if not any(isinstance(finder, _SiteCustomizeFinder) for finder in sys.meta_path):
    sys.meta_path.insert(0, _SiteCustomizeFinder())


def _load_repo_sitecustomize() -> None:
    """Execute the repository's real startup hook from the ``configs`` tree."""
    config_path = _REPO_ROOT / "configs" / "sitecustomize.py"
    if not config_path.exists():
        return

    spec = importlib.util.spec_from_file_location("codex_sitecustomize_config", config_path)
    if spec is None or spec.loader is None:
        return

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


_load_repo_sitecustomize()
