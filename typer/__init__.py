"""Transparent proxy to the real *typer* package installed in site-packages.

This stub exists so that ``from typer.testing import CliRunner`` works even
before the dev dependencies are installed.  Without an ``__init__.py`` the
``typer/`` directory would be treated as a namespace package that shadows the
real *typer* wheel, causing ``hasattr(typer, 'Typer')`` to return ``False``
and all CLI apps to be set to ``None`` at module load time.

When the real *typer* wheel is present in ``sys.path`` (e.g. after
``pip install -e .[dev]``) every public symbol is re-exported from it.
When it is absent the module stays empty, which preserves the existing
``if typer is None`` / ``if not hasattr(typer, 'Typer')`` fallback paths.
"""
from __future__ import annotations

import importlib.util
import os
import sys

_stub_dir = os.path.abspath(os.path.dirname(__file__))


def _load_real_typer() -> None:
    """Find the real *typer* package and re-export all its public symbols."""
    for _entry in sys.path:
        _abs = os.path.abspath(_entry)
        if _abs == _stub_dir:
            continue
        _init = os.path.join(_abs, "typer", "__init__.py")
        if not os.path.isfile(_init):
            continue
        _spec = importlib.util.spec_from_file_location(
            "typer",
            _init,
            submodule_search_locations=[os.path.dirname(_init)],
        )
        if _spec is None or _spec.loader is None:
            continue
        # Register the real module under 'typer' *before* executing so that
        # any internal ``import typer`` inside the wheel resolves correctly.
        _real = importlib.util.module_from_spec(_spec)
        sys.modules["typer"] = _real
        try:
            _spec.loader.exec_module(_real)
        except Exception:  # pragma: no cover — real typer load failure
            sys.modules["typer"] = sys.modules.get("typer", _real)
        # Promote all public names into this module's global namespace so
        # ``from typer import Typer`` works through the stub path too.
        globals().update(
            {k: v for k, v in vars(_real).items() if not k.startswith("__")}
        )
        return


_load_real_typer()
