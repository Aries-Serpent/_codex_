"""Lightweight Hydra error stubs for offline testing environments."""

from __future__ import annotations


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
