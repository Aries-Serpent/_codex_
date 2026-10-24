"""Compatibility package for the legacy `codex.cli` import contract."""

from __future__ import annotations

import sys
from importlib import import_module
from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "cli"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

from aries_serpent_core.cli import (  # noqa: F401
    ALLOWED_TASKS,
    _emit_group_help,
    _fix_pool,
    _missing_command,
    app,
    auth_group,
    chronicle,
    clean_logs_cmd,
    cli,
    export_env_cmd,
    init_db_cmd,
    list_sessions_cmd,
    logs,
    main,
    query_logs_cmd,
    repro_group,
    session_logger_cmd,
    tokenizer_group,
    validate_env_cmd,
    viewer_cmd,
)

sys.modules[f"{__name__}.main"] = import_module("aries_serpent_core.cli.main")

__all__ = [
    "ALLOWED_TASKS",
    "_emit_group_help",
    "_fix_pool",
    "_missing_command",
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
