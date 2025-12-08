"""Deprecation warnings for legacy config directories."""

import os
import warnings
from pathlib import Path


def check_legacy_config_usage():
    """Warn if legacy config directories are being used."""
    repo_root = Path(__file__).parent.parent.parent.parent

    legacy_dirs = ["conf", "config"]
    for legacy in legacy_dirs:
        legacy_path = repo_root / legacy
        if legacy_path.exists() and any(legacy_path.iterdir()):
            # Check if it's not just the DEPRECATED.md file
            non_deprecated_files = [f for f in legacy_path.iterdir() if f.name != "DEPRECATED.md"]
            if non_deprecated_files:
                warnings.warn(
                    f"Legacy config directory '{legacy}/' detected. "
                    f"Please migrate to 'configs/' directory. "
                    f"See configs/README.md for migration guide.",
                    DeprecationWarning,
                    stacklevel=2,
                )


# Auto-check on import
if os.getenv("CODEX_CHECK_LEGACY_CONFIGS", "1") == "1":
    check_legacy_config_usage()


__all__ = ["check_legacy_config_usage"]
