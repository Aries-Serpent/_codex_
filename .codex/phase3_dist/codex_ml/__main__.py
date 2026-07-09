"""Module entry point for ``python -m codex_ml``."""

from __future__ import annotations

import sys

from ._package_main import run

if __name__ == "__main__":
    sys.exit(run())
