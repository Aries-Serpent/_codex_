"""Compatibility shim for ``python -m codex_ml`` when importing from the repo root."""

from __future__ import annotations

import pkgutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if SRC.exists():  # pragma: no branch - defensive guard
    sys.path.insert(0, str(SRC))
    import codex_ml as _package  # noqa: PLC0415

    _package.__path__ = pkgutil.extend_path(list(_package.__path__), _package.__name__)

from codex_ml._package_main import run  # noqa: E402

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
