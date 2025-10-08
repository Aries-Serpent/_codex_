"""Package entry point.

Allows: `python -m codex_ml ...`
If a consolidated CLI is available under `codex_ml.cli`, we defer to it.
Otherwise we print a brief usage note.
"""

from __future__ import annotations

import importlib
import sys


def _run_cli() -> int:
    try:
        # Prefer module execution to avoid import-time side effects
        mod = importlib.import_module("codex_ml.cli")
    except Exception:
        sys.stdout.write("codex_ml: package entrypoint\nTry: python -m codex_ml.cli --help\n")
        return 0
    if hasattr(mod, "main"):
        return int(mod.main() or 0)
    # If subcommands exist as modules, show a hint
    sys.stdout.write("codex_ml.cli present. Try: python -m codex_ml.cli --help\n")
    return 0


def run() -> int:
    """Execute the package-level CLI."""

    return _run_cli()


if __name__ == "__main__":
    raise SystemExit(run())
