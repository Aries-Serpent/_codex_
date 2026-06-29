"""Centralized configuration loader using Hydra Compose API.

This module provides utilities for loading and validating configuration files
using Hydra's composition API. It consolidates error handling and provides
structured error messages from conf/errors/defaults.yaml.

Key features:
- Hydra Compose API integration for dynamic config loading
- Structured error handling with YAML-based error definitions
- Schema validation support via Pydantic (optional)
- Fallback mechanisms for offline/testing environments
- Configuration override support

Usage:
    from codex.utils.config_loader import load_config, load_error_config

    # Load error configuration
    errors = load_error_config()

    # Load application configuration
    cfg = load_config(config_name="base", config_dir="conf")
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import with fallback support
try:
    from omegaconf import DictConfig, OmegaConf

    _OMEGACONF_AVAILABLE = True
except ImportError:
    logger.warning("OmegaConf not available, using dict fallback")
    DictConfig = dict  # type: ignore[misc,assignment]
    OmegaConf = None  # type: ignore[misc,assignment]
    _OMEGACONF_AVAILABLE = False

# Hydra imports with robust fallbacks
try:
    from hydra import compose, initialize_config_dir
    from hydra.errors import MissingConfigException as HydraMissingConfigException

    _HYDRA_AVAILABLE = True
except ImportError:
    logger.debug("Hydra not available, using fallback")
    compose = None

    initialize_config_dir = None

    HydraMissingConfigException = FileNotFoundError

    _HYDRA_AVAILABLE = False

# Try to import from config_legacy as fallback
if not _HYDRA_AVAILABLE:
    try:
        from config_legacy.errors import MissingConfigException
    except ImportError:
        # Define our own if neither is available
        class MissingConfigException(FileNotFoundError):  # type: ignore[no-redef]
            """Exception raised when a configuration file cannot be located."""

            def __init__(
                self,
                missing_cfg_file: str | None = None,
                *,
                message: str | None = None,
                **kwargs: Any,
            ) -> None:
                if missing_cfg_file is None:
                    missing_cfg_file = kwargs.pop("missing_cfg_file", "")
                self.missing_cfg_file = missing_cfg_file
                resolved = message or f"Missing config file: {missing_cfg_file}"
                super().__init__(resolved)
                self.message = resolved

else:
    MissingConfigException = HydraMissingConfigException


@dataclass
class ErrorConfig:
    """Structured error configuration."""

    code: str
    message: str
    severity: str
    resolution: str

    def format(self, **kwargs: Any) -> str:
        """Format error message with context."""
        return f"[{self.code}] {self.message.format(**kwargs)}"


class ConfigLoader:
    """Centralized configuration loader using Hydra Compose API."""

    def __init__(self, repo_root: Path | None = None) -> None:
        """Initialize the config loader.

        Args:
            repo_root: Root directory of the repository. If None, auto-detected.
        """
        self.repo_root = repo_root or self._find_repo_root()
        self.error_config: dict[str, Any] = {}
        self._load_error_config()

    @staticmethod
    def _find_repo_root() -> Path:
        """Find the repository root directory."""
        current = Path(__file__).resolve()
        for parent in current.parents:
            if (parent / ".git").exists() or (parent / "pyproject.toml").exists():
                return parent
        # Fallback to parent of src
        return current.parents[3]

    def _load_error_config(self) -> None:
        """Load error configuration from conf/errors/defaults.yaml."""
        error_config_path = self.repo_root / "conf" / "errors" / "defaults.yaml"
        if not error_config_path.exists():
            logger.warning(f"Error config not found at {error_config_path}")
            self.error_config = self._get_default_error_config()
            return

        try:
            import yaml

            with error_config_path.open("r") as f:
                self.error_config = yaml.safe_load(f) or {}
        except ImportError:
            logger.warning("PyYAML not available, using default error config")
            self.error_config = self._get_default_error_config()
        except (IOError, OSError) as e:
            type(e).__name__
            logger.warning("Failed to load error config: <ERROR_TYPE>")
            self.error_config = self._get_default_error_config()

    @staticmethod
    def _get_default_error_config() -> dict[str, Any]:
        """Get default error configuration when YAML loading fails."""
        return {
            "config_errors": {
                "missing_config": {
                    "code": "CONFIG_001",
                    "message": "Missing configuration file",
                    "severity": "error",
                    "resolution": "Ensure the configuration file exists",
                }
            },
            "defaults": {
                "log_errors": True,
                "raise_on_error": True,
                "fallback_enabled": True,
            },
        }

    def get_error(self, category: str, error_key: str) -> ErrorConfig | None:
        """Get structured error configuration.

        Args:
            category: Error category (e.g., 'config_errors', 'hydra_errors')
            error_key: Specific error key within category

        Returns:
            ErrorConfig object or None if not found
        """
        errors = self.error_config.get(category, {})
        # Ensure errors is a dict before calling .get()
        if not isinstance(errors, dict):
            return None
        error_data = errors.get(error_key)
        if error_data and isinstance(error_data, dict):
            return ErrorConfig(**error_data)
        return None

    def _resolve_config_dir(self, config_dir: str | Path | None) -> Path:
        """Resolve config directory path with dual-path support.

        Args:
            config_dir: Config directory path (None, relative, or absolute)

        Returns:
            Resolved Path object
        """
        if config_dir is None:
            # Default to conf/ (Hydra convention), fallback to configs/
            primary = self.repo_root / "conf"
            if primary.exists():
                return primary
            return self.repo_root / "configs"
        if not Path(config_dir).is_absolute():
            return self.repo_root / config_dir
        return Path(config_dir)

    def _try_legacy_path(self, config_name: str, primary_dir: Path) -> Path | None:
        """Try to find config in legacy location.

        Args:
            config_name: Name of the config file
            primary_dir: Primary directory that was checked

        Returns:
            Path to legacy config file or None if not found
        """
        # If primary was conf/, try configs/
        if primary_dir.name == "conf" or "conf" in str(primary_dir):
            # Map conf/ structure to configs/ structure
            relative_to_conf = (
                primary_dir.relative_to(self.repo_root / "conf")
                if (self.repo_root / "conf") in primary_dir.parents
                else Path(".")
            )

            # Try common legacy mappings
            legacy_candidates = [
                self.repo_root / "configs" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / "training" / relative_to_conf / f"{config_name}.yaml",
                self.repo_root / "configs" / f"{config_name}.yaml",
            ]

            for candidate in legacy_candidates:
                if candidate.exists():
                    logger.debug(f"Found legacy config: {candidate}")
                    return candidate

        return None

    def load_config(
        self,
        config_name: str,
        config_dir: str | Path | None = None,
        overrides: list[str] | None = None,
        allow_fallback: bool = True,
    ) -> DictConfig | dict[str, Any]:
        """Load configuration using Hydra Compose API.

        Args:
            config_name: Name of config file (without .yaml extension)
            config_dir: Directory containing config files (relative to repo root or absolute)
            overrides: List of config overrides (e.g., ["key=value"])
            allow_fallback: Whether to use fallback when config not found

        Returns:
            DictConfig (or dict if OmegaConf unavailable)

        Raises:
            MissingConfigException: If config not found and allow_fallback=False
        """
        overrides = overrides or []

        # Resolve config directory with dual-path fallback
        config_dir = self._resolve_config_dir(config_dir)
        config_file = config_dir / f"{config_name}.yaml"

        # Try legacy path if primary not found (backward compatibility)
        if not config_file.exists() and allow_fallback:
            legacy_file = self._try_legacy_path(config_name, config_dir)
            if legacy_file:
                logger.info(f"Using legacy config path: {legacy_file}")
                config_file = legacy_file
                config_dir = config_file.parent

        # Try Hydra Compose API first
        if _HYDRA_AVAILABLE and config_dir.is_dir() and config_file.exists():
            try:
                with initialize_config_dir(version_base=None, config_dir=str(config_dir)):
                    cfg = compose(config_name=config_name, overrides=overrides)

                if _OMEGACONF_AVAILABLE:
                    # Convert to container and back for cleaner structure
                    container = OmegaConf.to_container(cfg, resolve=True)
                    if isinstance(container, dict):
                        return OmegaConf.create(container)
                    return cfg
                return cfg
            except (IOError, OSError) as e:
                type(e).__name__
                logger.warning("Hydra compose failed: <ERROR_TYPE>")
                if not allow_fallback:
                    raise

        # Fallback: load YAML directly
        if config_file.exists():
            try:
                import yaml

                with config_file.open("r") as f:
                    data = yaml.safe_load(f) or {}

                # Apply overrides manually
                if overrides:
                    data = self._apply_overrides(data, overrides)

                if _OMEGACONF_AVAILABLE and OmegaConf is not None:
                    return OmegaConf.create(data)
                return data
            except ImportError:
                logger.error("PyYAML required for config loading")
                if not allow_fallback:
                    raise
            except (ValueError, TypeError, RuntimeError) as e:
                type(e).__name__
                logger.error("Failed to load config: <ERROR_TYPE>")
                if not allow_fallback:
                    raise

        # No config found
        if not allow_fallback:
            error = self.get_error("config_errors", "missing_config")
            msg = error.format() if error else f"Missing config file: {config_file}"
            raise MissingConfigException(missing_cfg_file=str(config_file), message=msg)

        # Return empty config as fallback
        logger.warning(f"Config not found, returning empty fallback: {config_file}")
        if _OMEGACONF_AVAILABLE and OmegaConf is not None:
            return OmegaConf.create({})
        return {}

    @staticmethod
    def _apply_overrides(data: dict[str, Any], overrides: list[str]) -> dict[str, Any]:
        """Apply dotlist overrides to configuration dictionary.

        Args:
            data: Configuration dictionary
            overrides: List of override strings (e.g., ["key.subkey=value"])

        Returns:
            Modified configuration dictionary
        """
        for override in overrides:
            if "=" not in override:
                continue

            key_path, value_str = override.split("=", 1)
            keys = key_path.split(".")

            # Parse value
            try:
                import yaml

                value = yaml.safe_load(value_str)
            except (ValueError, TypeError):
                value = value_str

            # Navigate and set value
            current = data
            for key in keys[:-1]:
                if key not in current:
                    current[key] = {}
                current = current[key]
            current[keys[-1]] = value

        return data


# Global loader instance
_global_loader: ConfigLoader | None = None


def get_loader() -> ConfigLoader:
    """Get or create global ConfigLoader instance."""
    global _global_loader
    if _global_loader is None:
        _global_loader = ConfigLoader()
    return _global_loader


def load_config(
    config_name: str,
    config_dir: str | Path | None = None,
    overrides: list[str] | None = None,
    allow_fallback: bool = True,
) -> DictConfig | dict[str, Any]:
    """Load configuration using global loader.

    Args:
        config_name: Name of config file (without .yaml extension)
        config_dir: Directory containing config files
        overrides: List of config overrides
        allow_fallback: Whether to use fallback when config not found

    Returns:
        Configuration object
    """
    loader = get_loader()
    return loader.load_config(config_name, config_dir, overrides, allow_fallback)


def load_error_config() -> dict[str, Any]:
    """Load error configuration.

    Returns:
        Error configuration dictionary
    """
    loader = get_loader()
    return loader.error_config


__all__ = [
    "ConfigLoader",
    "ErrorConfig",
    "MissingConfigException",
    "get_loader",
    "load_config",
    "load_error_config",
]
