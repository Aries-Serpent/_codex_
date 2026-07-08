"""
Centralized Configuration Loader

Single source of truth for all configuration loading across the codebase.
Consolidates conf/, config/, configs/, omegaconf/, and config_legacy/ into
a unified loading system with Hydra/OmegaConf support.

Part of Phase 3: Configuration Sprawl Resolution
"""

from __future__ import annotations

import logging
import os
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Determine repository root
REPO_ROOT = Path(__file__).resolve().parents[1]

# Configuration directory hierarchy (in priority order)
CONFIG_DIRS = {
    "primary": REPO_ROOT / "conf",  # Primary Hydra-based configs
    "configs": REPO_ROOT / "configs",  # Secondary application configs
    "deprecated_config": REPO_ROOT / "config",  # Deprecated
    "deprecated_legacy": REPO_ROOT / "config_legacy",  # Deprecated
    "deprecated_omegaconf": REPO_ROOT / "omegaconf",  # Deprecated
}

# Environment variable keys
ENV_VARS = {
    "CONFIG_DIR": "CODEX_CONFIG_DIR",
    "ENV": "CODEX_ENV",
    "DEBUG": "CODEX_DEBUG",
}


class ConfigLoader:
    """
    Centralized configuration loader.

    Loads configuration from conf/ directory (Hydra-based) as the single
    source of truth, with fallback support for configs/ directory.

    Deprecated directories (config/, config_legacy/, omegaconf/) are
    excluded by default and will log warnings if accessed.
    """

    def __init__(
        self,
        config_dir: Optional[Path] = None,
        allow_deprecated: bool = False,
        strict_mode: bool = False,
    ):
        """
        Initialize configuration loader.

        Args:
            config_dir: Override default config directory
            allow_deprecated: Allow loading from deprecated directories
            strict_mode: Raise errors instead of warnings for deprecated access
        """
        self.config_dir = config_dir or CONFIG_DIRS["primary"]
        self.allow_deprecated = allow_deprecated
        self.strict_mode = strict_mode
        self._cache: dict[str, Any] = {}

        # Ensure primary config directory exists
        if not self.config_dir.exists():
            logger.warning(f"Primary config directory not found: {self.config_dir}")
            # Fall back to configs/ if conf/ doesn't exist
            if CONFIG_DIRS["configs"].exists():
                self.config_dir = CONFIG_DIRS["configs"]
                logger.info(f"Using fallback config directory: {self.config_dir}")

        logger.info(f"ConfigLoader initialized: {self.config_dir}")

    def load(
        self,
        config_name: str,
        config_path: Optional[str] = None,
        overrides: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Load configuration file.

        Args:
            config_name: Name of config file (without extension)
            config_path: Optional subdirectory within config_dir
            overrides: Optional dictionary of override values

        Returns:
            Loaded configuration as dictionary
        """
        cache_key = f"{config_path or ''}/{config_name}"

        # Check cache
        if cache_key in self._cache and overrides is None:
            logger.debug(f"Loading from cache: {cache_key}")
            return self._cache[cache_key].copy()

        # Construct full path
        if config_path:
            full_path = self.config_dir / config_path / config_name
        else:
            full_path = self.config_dir / config_name

        # Try different extensions
        config_file = None
        for ext in [".yaml", ".yml", ".json", ".toml", ""]:
            candidate = full_path.with_suffix(ext) if ext else full_path
            if candidate.exists():
                config_file = candidate
                break

        if not config_file:
            raise FileNotFoundError(
                f"Configuration file not found: {config_name} in {config_path or self.config_dir}"
            )

        # Load based on file type
        config = self._load_file(config_file)

        # Apply overrides
        if overrides:
            config = self._apply_overrides(config, overrides)

        # Cache result
        if overrides is None:
            self._cache[cache_key] = config.copy()

        logger.debug(f"Loaded config: {cache_key}")
        return config

    def _load_file(self, file_path: Path) -> dict[str, Any]:
        """Load configuration file based on extension."""
        import json

        suffix = file_path.suffix.lower()

        try:
            if suffix in [".yaml", ".yml"]:
                return self._load_yaml(file_path)
            if suffix == ".json":
                with open(file_path) as f:
                    return json.load(f)
            elif suffix == ".toml":
                return self._load_toml(file_path)
            else:
                # Try YAML as default
                return self._load_yaml(file_path)

        except (IOError, OSError) as e:
            type(e).__name__
            logger.error(f"Failed to load {file_path}: <ERROR_TYPE>")
            raise

    def _load_yaml(self, file_path: Path) -> dict[str, Any]:
        """Load YAML file."""
        try:
            import yaml

            with open(file_path) as f:
                return yaml.safe_load(f) or {}
        except ImportError:
            logger.error("PyYAML not installed. Install with: pip install pyyaml")
            raise

    def _load_toml(self, file_path: Path) -> dict[str, Any]:
        """Load TOML file."""
        try:
            import tomli

            with open(file_path, "rb") as f:
                return tomli.load(f)
        except ImportError:
            logger.error("tomli not installed. Install with: pip install tomli")
            raise

    def _apply_overrides(self, config: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
        """Apply override values to configuration."""
        result = config.copy()

        for key, value in overrides.items():
            # Support nested keys with dot notation (e.g., "model.hidden_size")
            if "." in key:
                self._set_nested(result, key.split("."), value)
            else:
                result[key] = value

        return result

    def _set_nested(self, d: dict[str, Any], keys: list[str], value: Any) -> None:
        """Set nested dictionary value using list of keys."""
        for key in keys[:-1]:
            d = d.setdefault(key, {})
        d[keys[-1]] = value

    def load_from_deprecated(self, directory: str, config_name: str) -> dict[str, Any]:
        """
        Load from deprecated directory with warning.

        Args:
            directory: Deprecated directory name (config, config_legacy, omegaconf)
            config_name: Configuration file name

        Returns:
            Loaded configuration
        """
        if not self.allow_deprecated:
            message = (
                f"Attempting to load from deprecated directory: {directory}. "
                f"This directory is scheduled for removal. "
                f"Migrate to conf/ directory."
            )
            if self.strict_mode:
                raise DeprecationWarning(message)
            warnings.warn(message, DeprecationWarning)
            logger.warning(message)

        # Load from deprecated location
        deprecated_dir = REPO_ROOT / directory
        if not deprecated_dir.exists():
            raise FileNotFoundError(f"Deprecated directory not found: {directory}")

        full_path = deprecated_dir / config_name
        return self._load_file(full_path)

    def get_env_var(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """
        Get environment variable with CODEX_ prefix.

        Args:
            key: Variable name (without CODEX_ prefix)
            default: Default value if not set

        Returns:
            Environment variable value or default
        """
        env_key = ENV_VARS.get(key, f"CODEX_{key.upper()}")
        return os.environ.get(env_key, default)

    def clear_cache(self) -> None:
        """Clear configuration cache."""
        self._cache.clear()
        logger.debug("Configuration cache cleared")


# Global instance
_config_loader: Optional[ConfigLoader] = None


def get_config_loader(
    config_dir: Optional[Path] = None,
    allow_deprecated: bool = False,
    strict_mode: bool = False,
) -> ConfigLoader:
    """
    Get or create global ConfigLoader instance.

    Args:
        config_dir: Override default config directory
        allow_deprecated: Allow loading from deprecated directories
        strict_mode: Raise errors instead of warnings for deprecated access

    Returns:
        ConfigLoader instance
    """
    global _config_loader

    if _config_loader is None:
        _config_loader = ConfigLoader(
            config_dir=config_dir,
            allow_deprecated=allow_deprecated,
            strict_mode=strict_mode,
        )

    return _config_loader


def load_config(
    config_name: str,
    config_path: Optional[str] = None,
    overrides: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """
    Convenience function to load configuration.

    Args:
        config_name: Name of config file (without extension)
        config_path: Optional subdirectory within config_dir
        overrides: Optional dictionary of override values

    Returns:
        Loaded configuration as dictionary
    """
    loader = get_config_loader()
    return loader.load(config_name, config_path, overrides)


def reset_config_loader() -> None:
    """Reset global ConfigLoader instance."""
    global _config_loader
    _config_loader = None


# Migration helpers


def detect_config_sprawl() -> dict[str, list[str]]:
    """
    Detect configuration files across all directories.

    Returns:
        Dictionary mapping directory names to lists of config files
    """
    results = {}

    for name, path in CONFIG_DIRS.items():
        if not path.exists():
            continue

        configs = []
        for ext in ["*.yaml", "*.yml", "*.json", "*.toml"]:
            configs.extend([str(f.relative_to(path)) for f in path.rglob(ext)])

        if configs:
            results[name] = sorted(configs)

    return results


def generate_migration_report() -> str:
    """
    Generate report of configuration sprawl for migration planning.

    Returns:
        Markdown-formatted migration report
    """
    sprawl = detect_config_sprawl()

    report = ["# Configuration Sprawl Analysis\n"]
    report.append(
        f"**Analysis Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')}\n"
    )
    report.append("## Summary\n")

    total_files = sum(len(files) for files in sprawl.values())
    report.append(f"- **Total Config Files:** {total_files}\n")
    report.append(f"- **Directories:** {len(sprawl)}\n\n")

    report.append("## Directory Breakdown\n")

    for name, files in sprawl.items():
        status = (
            "✅ Primary"
            if name == "primary"
            else "⚠️ Deprecated" if "deprecated" in name else "🔄 Secondary"
        )
        report.append(f"\n### {name} - {status}\n")
        report.append(f"- **File Count:** {len(files)}\n")
        report.append(f"- **Path:** `{CONFIG_DIRS[name]}`\n")

        if files:
            report.append("\n**Files:**\n")
            for f in files[:10]:  # Show first 10
                report.append(f"- `{f}`\n")
            if len(files) > 10:
                report.append(f"- ... and {len(files) - 10} more\n")

    report.append("\n## Recommendations\n")
    report.append("1. Migrate all configs to `conf/` (primary)\n")
    report.append("2. Use `configs/` for application-specific runtime configs\n")
    report.append("3. Archive deprecated directories to `archive/removed/`\n")
    report.append("4. Update all import statements to use `load_config()`\n")

    return "".join(report)


if __name__ == "__main__":
    # Generate migration report when run as script
    print(generate_migration_report())
