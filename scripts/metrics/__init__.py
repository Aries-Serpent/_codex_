"""Package initialization.

Re-exports the common metrics helpers from ``src/metrics.py`` so that
``from metrics import append_ndjson`` resolves correctly even when
``scripts/`` is prepended to ``sys.path`` by test modules that need to
import from the ``scripts`` package directly.  Without these re-exports
the empty package shadows ``src/metrics.py``, causing an ``ImportError``
at collection time for any test that exercises ``src.training.trainer``.
"""

from __future__ import annotations

import importlib.util as _importlib_util
import sys as _sys
from pathlib import Path as _Path

try:
    # Load the canonical ``src/metrics.py`` module directly by path instead of
    # ``from metrics import ...``: when ``scripts/`` is on ``sys.path`` this
    # package shadows the top-level ``metrics`` name, so a plain import would
    # resolve to this partially-initialized package and raise ImportError.
    _src_metrics = _Path(__file__).resolve().parents[2] / "src" / "metrics.py"
    _spec = _importlib_util.spec_from_file_location("_codex_src_metrics", _src_metrics)
    if _spec is None or _spec.loader is None:
        raise ModuleNotFoundError(str(_src_metrics))
    _module = _importlib_util.module_from_spec(_spec)
    _sys.modules.setdefault("_codex_src_metrics", _module)
    _spec.loader.exec_module(_module)

    accuracy = _module.accuracy
    append_ndjson = _module.append_ndjson
    write_ndjson = _module.write_ndjson

    __all__ = ["accuracy", "append_ndjson", "write_ndjson"]
except ModuleNotFoundError:
    # Graceful fallback: if the ``src`` package itself is not on sys.path
    # (e.g. when scripts/ is used as a standalone tool outside the repo),
    # leave the package importable but without re-exports.
    # NOTE: We catch only ModuleNotFoundError (a subclass of ImportError) so
    # that ImportErrors raised *inside* src.metrics (e.g. a broken import in
    # that module) still propagate and are visible to the developer.
    __all__ = []
