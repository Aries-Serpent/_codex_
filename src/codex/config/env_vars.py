"""Compatibility shim for `codex.config.env_vars`."""

from __future__ import annotations

import json
import os


def load_env_config():
    config = {}
    for key, value in os.environ.items():
        if value and key == "CONFIG_JSON":
            try:
                config = json.loads(value)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in CONFIG_JSON: {value!r}") from exc
        elif key.startswith("CODEX_") or key.startswith("TEST_"):
            config[key] = value
    return config


__all__ = ["load_env_config"]
