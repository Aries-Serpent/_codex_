"""Deprecation warnings for legacy config directories."""

import logging
import os
import warnings
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def find_repo_root(start_path: Optional[Path] = None) -> Path:
    """Find repository root by searching for .git directory.

    Uses CODEX_REPO_ROOT env var if set, otherwise walks up parents.
    Raises RuntimeError if not found.

    Args:
        start_path: Starting path for search (default: this file's location)

    Returns:
        Path to repository root

    Raises:
        RuntimeError: If repository root cannot be determined
    """
    env_root = os.getenv("CODEX_REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()

    if start_path is None:
        start_path = Path(__file__).resolve()

    for parent in [start_path] + list(start_path.parents):
        if (parent / ".git").is_dir():
            return parent

    raise RuntimeError(
        "Could not determine repository root. Set CODEX_REPO_ROOT environment variable."
    )


def check_legacy_config_usage() -> None:
    """Warn if legacy config directories are being used."""
    try:
        repo_root = find_repo_root()
    except RuntimeError as e:
        type(e).__name__
        logger.debug("RuntimeError: <ERROR_TYPE>")
        logger.warning("RuntimeError: <ERROR_TYPE>", exc_info=True)
        return  # Cannot determine root, skip check

    for legacy in ["conf", "config"]:
        legacy_path = repo_root / legacy
        if legacy_path.exists() and legacy_path.is_dir():
            try:
                non_deprecated = [f for f in legacy_path.iterdir() if f.name != "DEPRECATED.md"]
                if non_deprecated:
                    warnings.warn(
                        f"Legacy config directory '{legacy}/' detected. "
                        f"Please migrate to 'configs/' directory.",
                        DeprecationWarning,
                        stacklevel=2,
                    )
            except (PermissionError, NotADirectoryError, OSError) as e:
                type(e).__name__
                logger.debug("Exception: <ERROR_TYPE>")
                logger.debug(f"Could not check legacy directory {legacy}: <ERROR_TYPE>")
                continue


# Auto-check on import
if os.getenv("CODEX_CHECK_LEGACY_CONFIGS", "1") == "1":
    check_legacy_config_usage()


__all__ = ["check_legacy_config_usage", "find_repo_root"]
