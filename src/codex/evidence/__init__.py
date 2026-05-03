"""Evidence helpers for Codex operations."""

from __future__ import annotations

import sys
from importlib import util
from pathlib import Path
from types import ModuleType

from .core import evidence_append


def _load_legacy_module() -> ModuleType:
    module_name = "codex._legacy_evidence"
    if module_name in sys.modules:
        return sys.modules[module_name]
    legacy_path = Path(__file__).resolve().parent.parent / "evidence.py"
    spec = util.spec_from_file_location(module_name, legacy_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load legacy evidence module from {legacy_path!s}")
    module = util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_legacy = _load_legacy_module()
append_evidence = _legacy.append_evidence
utc_now = _legacy.utc_now

__all__ = ["append_evidence", "evidence_append", "utc_now"]
