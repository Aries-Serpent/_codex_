"""
P011: Configuration Validation Utilities

Consolidates 125 occurrences of config validation patterns.

Example:
    # Instead of: if not config.get('db'): raise ValueError(...)
    validate_config(config, {'db': (dict, True), 'port': (int, False)})
"""

from typing import Any, Dict, List, Tuple, Type

__all__ = [
    "validate_config",
    "ConfigValidator",
    "ValidationError",
]


class ValidationError(ValueError):
    """Raised when validation fails."""

    pass


def validate_config(
    config: Dict[str, Any],
    schema: Dict[str, Tuple[Type, bool]],
) -> None:
    """
    Validate configuration against a schema.

    Args:
        config: Configuration dictionary
        schema: Dict mapping keys to (type, required) tuples

    Raises:
        ValidationError: If validation fails

    Example:
        >>> schema = {'db': (dict, True), 'port': (int, False)}
        >>> validate_config({'db': {}}, schema)  # OK
    """
    for key, (expected_type, required) in schema.items():
        if key not in config:
            if required:
                raise ValidationError(f"Required config key '{key}' missing")
        else:
            value = config[key]
            if not isinstance(value, expected_type):
                raise ValidationError(
                    f"Config key '{key}' must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )


class ConfigValidator:
    """Fluent configuration validator."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.errors: List[str] = []

    def require(self, key: str) -> "ConfigValidator":
        """Require a config key."""
        if key not in self.config:
            self.errors.append(f"Required config key '{key}' missing")
        return self

    def require_type(self, key: str, expected_type: Type) -> "ConfigValidator":
        """Require a key to have a specific type."""
        if key in self.config:
            value = self.config[key]
            if not isinstance(value, expected_type):
                self.errors.append(
                    f"Config key '{key}' must be {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
        return self

    def validate(self) -> None:
        """Validate all checks."""
        if self.errors:
            raise ValidationError("; ".join(self.errors))
