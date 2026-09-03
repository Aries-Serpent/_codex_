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

import importlib.util
import sys
from pathlib import Path


def _load_repo_sitecustomize() -> None:
    """Execute the repository's real startup hook from the ``configs`` tree."""
    root = Path(__file__).resolve().parent
    config_path = root / "configs" / "sitecustomize.py"
    if not config_path.exists():
        return

    spec = importlib.util.spec_from_file_location("codex_sitecustomize_config", config_path)
    if spec is None or spec.loader is None:
        return

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)


_load_repo_sitecustomize()
