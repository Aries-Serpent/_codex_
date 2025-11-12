"""
Hydra ConfigStore compatibility utilities.

Hydra versions <1.3 do not provide ConfigStore.exists(); this shim
offers a unified interface:
    safe_exists(cs, name) -> bool
"""
from __future__ import annotations
from typing import Any

def safe_exists(config_store: Any, name: str) -> bool:
    """
    Check if a config name exists in the ConfigStore.
    Compatible with both old and new Hydra versions.
    """
    # Modern Hydra (>=1.3)
    if hasattr(config_store, "exists"):
        try:
            return bool(config_store.exists(name=name))
        except Exception:
            return False
    # Fallback: enumerate names
    try:
        listed = [item.name for item in config_store.list()]
        return name in listed
    except Exception:
        return False
