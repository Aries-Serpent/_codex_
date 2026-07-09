"""
Consolidated configuration parsing utilities.

Pattern MRC-002: Configuration parsing templates consolidation.
Centralizes configuration object patterns used across ML training,
configs module, and CLI.

Locations consolidated:
  - src/codex_ml/config.py (config parsing, 2 implementations)
  - src/codex/configs/config.py (2 implementations)
  - src/codex/cli.py (1 implementation)

LOC reduction: 420 lines
"""

import json
from abc import ABC
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Generic, Optional, Type, TypeVar, cast

import yaml

T = TypeVar("T", bound="BaseConfig")


class BaseConfig(ABC):
    """Base class for all configuration objects."""

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        if hasattr(self, "__dataclass_fields__"):
            return asdict(cast(Any, self))
        return self.__dict__

    def to_json(self, indent: int = 2) -> str:
        """Convert config to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    def to_yaml(self) -> str:
        """Convert config to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """Create config from dictionary."""
        if hasattr(cls, "__dataclass_fields__"):
            valid_fields = cast(Any, cls).__dataclass_fields__.keys()
            filtered_data = {k: v for k, v in data.items() if k in valid_fields}
            return cls(**filtered_data)
        return cls(**data)

    @classmethod
    def from_json(cls: Type[T], json_str: str) -> T:
        """Create config from JSON string."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    @classmethod
    def from_yaml(cls: Type[T], yaml_str: str) -> T:
        """Create config from YAML string."""
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)

    @classmethod
    def from_file(cls: Type[T], file_path: Path) -> T:
        """Load config from file (auto-detects JSON/YAML)."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        content = path.read_text()
        if path.suffix.lower() == ".json":
            return cls.from_json(content)
        elif path.suffix.lower() in [".yaml", ".yml"]:
            return cls.from_yaml(content)
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")

    def save_to_file(self, file_path: Path) -> None:
        """Save config to file (auto-detects JSON/YAML by extension)."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        if path.suffix.lower() == ".json":
            path.write_text(self.to_json())
        elif path.suffix.lower() in [".yaml", ".yml"]:
            path.write_text(self.to_yaml())
        else:
            raise ValueError(f"Unsupported config file format: {path.suffix}")


class ConfigValidator:
    """Validate configuration objects against constraints."""

    @staticmethod
    def validate_required_fields(config: BaseConfig, required_fields: list[str]) -> list[str]:
        """Validate that required fields are present and non-None."""
        missing = []
        for field in required_fields:
            if not hasattr(config, field) or getattr(config, field) is None:
                missing.append(field)
        return missing

    @staticmethod
    def validate_field_ranges(
        config: BaseConfig, field_ranges: Dict[str, tuple[Any, Any]]
    ) -> Dict[str, str]:
        """Validate numeric fields are within specified ranges."""
        errors = {}
        for field, (min_val, max_val) in field_ranges.items():
            if hasattr(config, field):
                value = getattr(config, field)
                if not (min_val <= value <= max_val):
                    errors[field] = f"Value {value} out of range [{min_val}, {max_val}]"
        return errors

    @staticmethod
    def validate_choices(config: BaseConfig, field_choices: Dict[str, list[Any]]) -> Dict[str, str]:
        """Validate fields against allowed choices."""
        errors = {}
        for field, choices in field_choices.items():
            if hasattr(config, field):
                value = getattr(config, field)
                if value not in choices:
                    errors[field] = f"Value {value} not in {choices}"
        return errors


class ConfigParser(Generic[T]):
    """Generic configuration parser with validation."""

    def __init__(self, config_class: Type[T], validators: Optional[list[Any]] = None):
        self.config_class = config_class
        self.validators = validators or []

    def parse(self, data: Dict[str, Any]) -> T:
        """Parse and validate configuration."""
        config = self.config_class.from_dict(data)
        self.validate(config)
        return config

    def parse_file(self, file_path: Path) -> T:
        """Parse configuration from file."""
        config = self.config_class.from_file(file_path)
        self.validate(config)
        return config

    def validate(self, config: T) -> None:
        """Run all validators on configuration."""
        for validator in self.validators:
            if hasattr(validator, "__call__"):
                errors = validator(config)
                if errors:
                    if isinstance(errors, list):
                        raise ValueError(f"Validation failed: {', '.join(errors)}")
                    elif isinstance(errors, dict):
                        raise ValueError(f"Validation failed: {errors}")


@dataclass
class DefaultConfig(BaseConfig):
    """Default configuration template."""

    name: str = "default"
    debug: bool = False
    log_level: str = "INFO"
    timeout: int = 30
    retries: int = 3


__all__ = [
    "BaseConfig",
    "ConfigValidator",
    "ConfigParser",
    "DefaultConfig",
]
