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

from codex.logging.structured_logger import logger

from .main import app, main

# Deterministically load Click CLI group from src/codex/cli.py without shadowing/circular imports.
_codex_root = Path(__file__).resolve().parent.parent  # src/codex
_click_cli_path = _codex_root / "cli.py"


_cli_load_error: Exception | None = None


def _load_click_cli() -> Any:
    """Load the Click CLI group from src/codex/cli.py using importlib."""
    global _cli_load_error

    # Check if already loaded to ensure idempotency
    if "codex._cli_click" in sys.modules:
        existing_module = sys.modules["codex._cli_click"]
        return getattr(existing_module, "cli", None)

    # Validate that the file exists before attempting to load
    if not _click_cli_path.exists() or not _click_cli_path.is_file():
        _cli_load_error = FileNotFoundError(f"Click CLI file not found: {_click_cli_path}")
        return None

    try:
        spec = importlib.util.spec_from_file_location("codex._cli_click", _click_cli_path)
        if spec is None or spec.loader is None:
            _cli_load_error = ImportError(f"Failed to create import spec for {_click_cli_path}")
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules["codex._cli_click"] = module
        spec.loader.exec_module(module)
        return getattr(module, "cli", None)
    except (ImportError, AttributeError) as exc:  # pragma: no cover
        _cli_load_error = exc
        return None


cli = _load_click_cli()


def _initialize_cli_groups() -> dict[str, Any]:
    """Initialize CLI groups and helpers from loaded Click module.
    
    Returns a dictionary with all CLI group exports properly typed.
    This pattern avoids uninitialized variable anti-pattern while
    maintaining backward compatibility for test imports.
    """
    groups: dict[str, Any] = {
        "logs": None,
        "tokenizer_group": None,
        "repro_group": None,
        "auth_group": None,
        "chronicle": None,
        "_fix_pool": None,
        "init_db_cmd": None,
        "export_env_cmd": None,
        "clean_logs_cmd": None,
        "session_logger_cmd": None,
        "query_logs_cmd": None,
        "validate_env_cmd": None,
        "list_sessions_cmd": None,
        "viewer_cmd": None,
        "ALLOWED_TASKS": None,
        "_emit_group_help": None,
        "_missing_command": None,
    }

    if cli is not None:
        # Import the groups from the loaded module
        _cli_module = sys.modules.get("codex._cli_click")
        if _cli_module:
            for key in groups:
                groups[key] = getattr(_cli_module, key, None)

    return groups


# Initialize CLI groups once and expose as module attributes
_cli_groups = _initialize_cli_groups()
logs: Any = _cli_groups["logs"]
tokenizer_group: Any = _cli_groups["tokenizer_group"]
repro_group: Any = _cli_groups["repro_group"]
auth_group: Any = _cli_groups["auth_group"]
chronicle: Any = _cli_groups["chronicle"]
_fix_pool: Any = _cli_groups["_fix_pool"]
init_db_cmd: Any = _cli_groups["init_db_cmd"]
export_env_cmd: Any = _cli_groups["export_env_cmd"]
clean_logs_cmd: Any = _cli_groups["clean_logs_cmd"]
session_logger_cmd: Any = _cli_groups["session_logger_cmd"]
query_logs_cmd: Any = _cli_groups["query_logs_cmd"]
validate_env_cmd: Any = _cli_groups["validate_env_cmd"]
list_sessions_cmd: Any = _cli_groups["list_sessions_cmd"]
viewer_cmd: Any = _cli_groups["viewer_cmd"]
ALLOWED_TASKS: Any = _cli_groups["ALLOWED_TASKS"]
_emit_group_help: Any = _cli_groups["_emit_group_help"]
_missing_command: Any = _cli_groups["_missing_command"]

__all__ = [
    "_emit_group_help",
    "_fix_pool",
    "_missing_command",
    "ALLOWED_TASKS",
    "app",
    "auth_group",
    "chronicle",
    "clean_logs_cmd",
    "cli",
    "export_env_cmd",
    "init_db_cmd",
    "list_sessions_cmd",
    "logs",
    "main",
    "query_logs_cmd",
    "repro_group",
    "session_logger_cmd",
    "tokenizer_group",
    "validate_env_cmd",
    "viewer_cmd",
]

if cli is None:
    # Non-fatal import warning, but tests will fail if Click CLI is required.
    import warnings

    warnings.warn(
        f"Click CLI group 'cli' could not be loaded from {_click_cli_path}. "
        "IMPACT: All CLI commands (e.g., 'codex run', 'codex analyze') will be unavailable. "
        "RESOLUTION: Ensure src/codex/cli.py exists and exports a Click 'cli' group. "
        "Check for import errors with: python -c 'from src.codex.cli import cli; logger.info(cli)'. "
        f"Underlying error: {_cli_load_error!r}",
        ImportWarning,
        stacklevel=2,
    )
