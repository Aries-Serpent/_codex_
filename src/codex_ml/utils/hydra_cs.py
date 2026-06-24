"""
Hydra ConfigStore compatibility utilities.

Hydra versions <1.3 do not provide ConfigStore.exists(); this shim
offers a unified interface:
    safe_exists(cs, name, group=None) -> bool
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)


def safe_exists(config_store: Any, name: str, group: Optional[str] = None) -> bool:
    """
    Check if a config name exists in the ConfigStore.
    Compatible with both old and new Hydra versions.

    Args:
        config_store: ConfigStore instance
        name: Name of the config (without .yaml extension)
        group: Optional group name (e.g., "experiment")

    Returns:
        True if config exists, False otherwise
    """
    # Modern Hydra (>=1.3) with exists method
    if hasattr(config_store, "exists"):
        try:
            if group:
                return bool(config_store.exists(group=group, name=name))
            return bool(config_store.exists(name=name))
        except (ValueError, TypeError, RuntimeError):
            logger.debug("safe_exists: ConfigStore.exists() raised", exc_info=True)
            return False

    # Fallback: use list() method
    try:
        if group:
            # List items in the group
            items = config_store.list(group)
            # Check if name.yaml is in the list
            return f"{name}.yaml" in items
        # List items at root
        items = config_store.list("")
        # Check if name.yaml is in the list
        return f"{name}.yaml" in items
    except (ValueError, TypeError, RuntimeError):
        logger.debug("safe_exists: ConfigStore.list() raised", exc_info=True)
        return False
