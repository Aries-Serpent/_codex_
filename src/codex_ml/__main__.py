"""Executable entry point for ``python -m codex_ml``."""

from __future__ import annotations

from ._package_main import run

if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(run())
