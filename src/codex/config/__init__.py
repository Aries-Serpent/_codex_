"""Compatibility exports for legacy `codex.config` imports."""

from __future__ import annotations

from pathlib import Path

_pkg_root = Path(__file__).resolve().parent
_migrated_root = _pkg_root.parent.parent / "aries_serpent_core" / "config"

__path__ = [str(_pkg_root)]
if _migrated_root.is_dir():
    __path__.append(str(_migrated_root))

from aries_serpent_core.config.env_vars import EnvVarConfig, EnvironmentManager, env_manager
from aries_serpent_core.config.env_vars import load_env_config as _load_env_config


def load_env_config():
    return _load_env_config()


__all__ = ["EnvVarConfig", "EnvironmentManager", "env_manager", "load_env_config"]
