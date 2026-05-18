"""Package initialization.

Re-exports the common metrics helpers from ``src/metrics.py`` so that
``from metrics import append_ndjson`` resolves correctly even when
``scripts/`` is prepended to ``sys.path`` by test modules that need to
import from the ``scripts`` package directly.  Without these re-exports
the empty package shadows ``src/metrics.py``, causing an ``ImportError``
at collection time for any test that exercises ``src.training.trainer``.
"""

from __future__ import annotations

try:
    from src.metrics import accuracy, append_ndjson, write_ndjson

    __all__ = ["accuracy", "append_ndjson", "write_ndjson"]
except ModuleNotFoundError:
    # Graceful fallback: if the ``src`` package itself is not on sys.path
    # (e.g. when scripts/ is used as a standalone tool outside the repo),
    # leave the package importable but without re-exports.
    # NOTE: We catch only ModuleNotFoundError (a subclass of ImportError) so
    # that ImportErrors raised *inside* src.metrics (e.g. a broken import in
    # that module) still propagate and are visible to the developer.
    __all__ = []
