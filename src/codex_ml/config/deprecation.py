"""Deprecation warnings for legacy config directories."""

import os
import warnings
from pathlib import Path


def find_repo_root(start_path: Path = None) -> Path:
    """Find the repository root by searching for a .git directory upwards from start_path.
    If CODEX_REPO_ROOT env var is set, use that. Raises RuntimeError if not found."""
    env_root = os.getenv("CODEX_REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    if start_path is None:
        start_path = Path(__file__).resolve()
    for parent in [start_path] + list(start_path.parents):
        if (parent / ".git").is_dir():
            return parent
    raise RuntimeError(
        "Could not determine repository root. Please set CODEX_REPO_ROOT environment variable."
    )


def check_legacy_config_usage():
    """Warn if legacy config directories are being used."""
    try:
        repo_root = find_repo_root()
    except RuntimeError:
        # Can't determine repo root, skip check
        return

    legacy_dirs = ["conf", "config"]
    for legacy in legacy_dirs:
        legacy_path = repo_root / legacy
        if legacy_path.exists() and legacy_path.is_dir():
            try:
                if any(legacy_path.iterdir()):
                    # Check if it's not just the DEPRECATED.md file
                    non_deprecated_files = [
                        f for f in legacy_path.iterdir() if f.name != "DEPRECATED.md"
                    ]
                    if non_deprecated_files:
                        warnings.warn(
                            f"Legacy config directory '{legacy}/' detected. "
                            f"Please migrate to 'configs/' directory. "
                            f"See configs/README.md for migration guide.",
                            DeprecationWarning,
                            stacklevel=2,
                        )
            except (PermissionError, OSError):
                # Skip this legacy directory if we can't access it
                continue


# Auto-check on import
if os.getenv("CODEX_CHECK_LEGACY_CONFIGS", "1") == "1":
    check_legacy_config_usage()


__all__ = ["check_legacy_config_usage", "find_repo_root"]
