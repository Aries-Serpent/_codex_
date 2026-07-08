"""
P009: Environment Variable Access Utilities

Consolidates 492 occurrences of os.environ.get() patterns into
consistent, well-tested utility functions with type support.

Example:
    # Instead of: os.environ.get('DEBUG', 'false')
    debug = get_env_bool('DEBUG', default=False)

    # Instead of: os.environ.get('PORT')
    port = get_env_int('PORT', required=True)
"""

import os
from typing import List, Optional, TypeVar

__all__ = [
    "get_env",
    "get_env_int",
    "get_env_float",
    "get_env_bool",
    "get_env_list",
    "require_env",
    "validate_env",
    "EnvVarError",
]

T = TypeVar("T")


class EnvVarError(ValueError):
    """Raised when an environment variable check fails."""

    pass


def get_env(
    name: str,
    default: Optional[str] = None,
    required: bool = False,
) -> Optional[str]:
    """
    Get an environment variable with optional validation.

    Args:
        name: Name of the environment variable
        default: Default value if not found
        required: If True, raise error if not found

    Returns:
        The environment variable value, default, or None

    Raises:
        EnvVarError: If required=True and variable not found

    Example:
        >>> get_env('PATH')  # Returns system PATH
        >>> get_env('MY_VAR', default='default_value')
    """
    value = os.environ.get(name)

    if value is not None:
        return value

    if default is not None:
        return default

    if required:
        raise EnvVarError(f"Required environment variable '{name}' not found")

    return None


def get_env_int(
    name: str,
    default: Optional[int] = None,
    required: bool = False,
) -> Optional[int]:
    """
    Get an environment variable as an integer.

    Args:
        name: Name of the environment variable
        default: Default value if not found
        required: If True, raise error if not found

    Returns:
        The environment variable value as int, default, or None

    Raises:
        EnvVarError: If value cannot be converted to int or required=True and not found

    Example:
        >>> get_env_int('PORT', default=8080)
        8080
    """
    value = get_env(name, required=required)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        raise EnvVarError(f"Environment variable '{name}' must be an integer, got '{value}'")


def get_env_float(
    name: str,
    default: Optional[float] = None,
    required: bool = False,
) -> Optional[float]:
    """
    Get an environment variable as a float.

    Args:
        name: Name of the environment variable
        default: Default value if not found
        required: If True, raise error if not found

    Returns:
        The environment variable value as float, default, or None

    Raises:
        EnvVarError: If value cannot be converted to float or required=True and not found
    """
    value = get_env(name, required=required)

    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        raise EnvVarError(f"Environment variable '{name}' must be a float, got '{value}'")


def get_env_bool(
    name: str,
    default: Optional[bool] = None,
    required: bool = False,
) -> Optional[bool]:
    """
    Get an environment variable as a boolean.

    Recognizes true/false values: 1, true, yes, on (case-insensitive)

    Args:
        name: Name of the environment variable
        default: Default value if not found
        required: If True, raise error if not found

    Returns:
        The environment variable value as bool, default, or None

    Raises:
        EnvVarError: If value is not a valid boolean

    Example:
        >>> get_env_bool('DEBUG', default=False)
        False
    """
    value = get_env(name, required=required)

    if value is None:
        return default

    if value.lower() in ("1", "true", "yes", "on"):
        return True
    elif value.lower() in ("0", "false", "no", "off"):
        return False
    else:
        raise EnvVarError(
            f"Environment variable '{name}' must be a boolean, got '{value}'. "
            f"Valid values: 1/0, true/false, yes/no, on/off"
        )


def get_env_list(
    name: str,
    separator: str = ",",
    default: Optional[List[str]] = None,
    required: bool = False,
) -> Optional[List[str]]:
    """
    Get an environment variable as a list of strings.

    Args:
        name: Name of the environment variable
        separator: Character to split on (default: comma)
        default: Default list if not found
        required: If True, raise error if not found

    Returns:
        The environment variable value as list, default, or None

    Example:
        >>> # With ALLOWED_HOSTS=localhost,127.0.0.1
        >>> get_env_list('ALLOWED_HOSTS')
        ['localhost', '127.0.0.1']
    """
    value = get_env(name, required=required)

    if value is None:
        return default

    return [item.strip() for item in value.split(separator) if item.strip()]


def require_env(name: str) -> str:
    """
    Get a required environment variable.

    Args:
        name: Name of the environment variable

    Returns:
        The environment variable value

    Raises:
        EnvVarError: If variable not found

    Example:
        >>> api_key = require_env('API_KEY')
    """
    value = get_env(name, required=True)
    assert value is not None  # Type guard
    return value


def validate_env(*required_vars: str) -> None:
    """
    Validate that all required environment variables are set.

    Args:
        *required_vars: Names of required environment variables

    Raises:
        EnvVarError: If any required variable is missing

    Example:
        >>> validate_env('API_KEY', 'DATABASE_URL', 'LOG_LEVEL')
    """
    missing = []
    for var_name in required_vars:
        if var_name not in os.environ:
            missing.append(var_name)

    if missing:
        raise EnvVarError(f"Missing required environment variables: {', '.join(missing)}")
