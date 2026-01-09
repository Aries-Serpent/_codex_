"""Lightweight Hydra error stubs for offline testing environments.

.. deprecated::
    This module is deprecated as part of PS-01 Configuration Consolidation.
    Use `codex.utils.config_loader.MissingConfigException` instead.
    This compatibility shim will be removed in a future version.
"""

from __future__ import annotations

import warnings

warnings.warn(
    "config_legacy.errors is deprecated. "
    "Use codex.utils.config_loader.MissingConfigException instead. "
    "This module will be removed in a future version.",
    DeprecationWarning,
    stacklevel=2,
)

# Try to import from the new location first
try:
    from codex.utils.config_loader import MissingConfigException
except ImportError:
    # Fallback to local definition for backward compatibility
    class MissingConfigException(FileNotFoundError):
        """Exception raised when a requested Hydra config file cannot be located."""

        def __init__(
            self,
            *,
            missing_cfg_file: str,
            message: str | None = None,
            config_name: str | None = None,
            **_: object,
        ) -> None:
            self.missing_cfg_file = missing_cfg_file
            self.config_name = config_name
            resolved = message or f"Missing config file: {missing_cfg_file}"
            super().__init__(resolved)
            self.message = resolved


__all__ = ["MissingConfigException"]

