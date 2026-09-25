#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path

_repo_root = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "src.tools.template_lint",
    _repo_root / "src" / "tools" / "template_lint.py",
)
if _spec is None or _spec.loader is None:
    raise RuntimeError("Unable to load template_lint implementation")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)

main = _module.main


if __name__ == "__main__":
    raise SystemExit(main())
