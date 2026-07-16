"""Shim to `src/tokenization/cli.py` so editable checkouts expose the Typer app."""

from __future__ import annotations

import importlib.util
import pathlib
import sys
from types import ModuleType

_src = pathlib.Path(__file__).resolve().parents[1] / "src" / "tokenization" / "cli.py"


def _load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("tokenization._src_cli", _src)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load tokenization.cli from {_src}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_module = _load()
__all__ = getattr(_module, "__all__", [])
for name in __all__:
    if hasattr(_module, name):
        globals()[name] = getattr(_module, name)


def _run_app() -> None:
    """Delegate execution to the underlying Typer application or main entry point."""

    app = getattr(_module, "app", None)
    if callable(app):
        app()
        return
    main = getattr(_module, "main", None)
    if callable(main):
        main()
        return
    raise SystemExit(
        "tokenization.cli shim cannot execute because the loaded module provides neither an"
        " 'app' Typer instance nor a callable 'main' entry point."
    )


if __name__ == "__main__":
    _run_app()


def _append_error_block(error_text: str, block_name: str = "error") -> str:
    """Append an error block to formatted output."""
    return f"\n[{block_name}]\n{error_text}\n"
