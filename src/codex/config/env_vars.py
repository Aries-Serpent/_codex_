"""Compatibility shim for `codex.config.env_vars`."""

from __future__ import annotations

from aries_serpent_core.config.env_vars import (
    EnvVarConfig,
    EnvironmentManager,
    env_manager,
)


def load_env_config():
    """Return the active environment variables in a JSON-friendly dict."""
    import json
    import os

    config: dict[str, str] = {}
    for key, value in os.environ.items():
        if value and key == "CONFIG_JSON":
            try:
                config = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in CONFIG_JSON: {value!r}") from exc
        elif key.startswith("CODEX_") or key.startswith("TEST_"):
            config[key] = value
    return config


__all__ = ["EnvVarConfig", "EnvironmentManager", "env_manager", "load_env_config"]
