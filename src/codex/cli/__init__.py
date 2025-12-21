"""
Codex CLI Module — Unified Command-Line Interface

AI_AGENT_HINTS:
- Canonical import (Click legacy/test): `from codex.cli import cli`
- Canonical import (Typer modern): `from codex.cli import app`
- Entry point: `from codex.cli import main`
- Implementation locations:
  - Click:  src/codex/cli.py  (exports click.Group named `cli`)
  - Typer:  src/codex/cli/main.py (exports Typer `app` and `main`)
- Design: Facade export surface to keep imports deterministic (no shadowing surprises).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any

from .main import app, main

# Deterministically load Click CLI group from src/codex/cli.py without shadowing/circular imports.
_codex_root = Path(__file__).resolve().parent.parent  # src/codex
_click_cli_path = _codex_root / "cli.py"


def _load_click_cli() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)
    
    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        return None
    
    spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    sys.modules["codex._cli_click"] = module
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return getattr(module, "cli", None)


cli = _load_click_cli()

__all__ = ["app", "main", "cli"]

if cli is None:
    # Non-fatal import warning, but tests will fail if Click CLI is required.
    import warnings

    warnings.warn(
        f"Click CLI group 'cli' could not be loaded from {_click_cli_path}. "
        "IMPACT: All CLI commands (e.g., 'codex run', 'codex analyze') will be unavailable. "
        "RESOLUTION: Ensure src/codex/cli.py exists and exports a Click 'cli' group. "
        "Check for import errors with: python -c 'from src.codex.cli import cli; print(cli)'",
        ImportWarning,
        stacklevel=2,
    )
