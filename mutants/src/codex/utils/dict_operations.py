"""
P014: Dictionary Operations Utilities

Consolidates 1,832 occurrences of dict.get() patterns and dictionary
access patterns into safe, tested utility functions.

Example:
    # Instead of: config.get('database', {})
    db_config = safe_get(config, 'database', default={})

    # Instead of: config['db']['host'] with error handling
    host = nested_get(config, 'db.host', default='localhost')
"""

from typing import Any, Dict, Optional, TypeVar, Union

__all__ = [
    "safe_get",
    "nested_get",
    "nested_set",
    "get_typed",
    "set_if_missing",
    "DictAccessor",
    "DictAccessError",
]

T = TypeVar("T")


class DictAccessError(KeyError):
    """Raised when dictionary access fails."""

    pass


def safe_get(
    data: Optional[Dict[str, Any]],
    key: str,
    default: Any = None,
) -> Any:
    """
    Safely get a value from a dictionary.

    Args:
        data: The dictionary to access (can be None)
        key: The key to retrieve
        default: Default value if key not found

    Returns:
        The value at key, or default if not found

    Example:
        >>> safe_get({'a': 1}, 'a')
        1
        >>> safe_get({'a': 1}, 'b', default=0)
        0
        >>> safe_get(None, 'a', default=0)
        0
    """
    if data is None:
        return default
    return data.get(key, default)


def nested_get(
    data: Optional[Dict[str, Any]],
    path: str,
    default: Any = None,
    separator: str = ".",
) -> Any:
    """
    Get a value from nested dictionaries using dot notation.

    Args:
        data: The root dictionary to access
        path: Dot-separated path to the value (e.g., 'db.host')
        default: Default value if path not found
        separator: Path separator character (default: '.')

    Returns:
        The value at path, or default if not found

    Example:
        >>> config = {'db': {'host': 'localhost'}}
        >>> nested_get(config, 'db.host')
        'localhost'
        >>> nested_get(config, 'db.port', default=5432)
        5432
        >>> nested_get(None, 'db.host', default='localhost')
        'localhost'
    """
    if data is None:
        return default

    keys = path.split(separator)
    current = data

    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default

    return current


def nested_set(
    data: Dict[str, Any],
    path: str,
    value: Any,
    separator: str = ".",
    create_missing: bool = True,
) -> Dict[str, Any]:
    """
    Set a value in nested dictionaries using dot notation.

    Args:
        data: The root dictionary to modify
        path: Dot-separated path to the value (e.g., 'db.host')
        value: The value to set
        separator: Path separator character (default: '.')
        create_missing: If True, create missing intermediate dicts

    Returns:
        The modified dictionary (returns input data)

    Raises:
        DictAccessError: If path cannot be created and create_missing=False

    Example:
        >>> config = {}
        >>> nested_set(config, 'db.host', 'localhost')
        >>> config
        {'db': {'host': 'localhost'}}
    """
    keys = path.split(separator)
    current = data

    # Navigate/create intermediate dictionaries
    for key in keys[:-1]:
        if key not in current:
            if not create_missing:
                raise DictAccessError(f"Cannot create missing key '{key}' in path")
            current[key] = {}
        elif not isinstance(current[key], dict):
            raise DictAccessError(f"Cannot traverse non-dict at key '{key}'")
        current = current[key]

    # Set the final value
    current[keys[-1]] = value
    return data


def get_typed(
    data: Optional[Dict[str, Any]],
    key: str,
    target_type: type,
    default: Optional[T] = None,
) -> Union[Any, Optional[T]]:
    """
    Get a value from a dictionary and assert its type.

    Args:
        data: The dictionary to access
        key: The key to retrieve
        target_type: Expected type of the value
        default: Default if key not found or type doesn't match

    Returns:
        The value if it matches the type, else default

    Example:
        >>> config = {'port': 8080}
        >>> get_typed(config, 'port', int, default=3000)
        8080
        >>> get_typed(config, 'missing', int, default=3000)
        3000
    """
    value = safe_get(data, key, default=None)

    if value is None:
        return default

    if isinstance(value, target_type):
        return value

    return default


def set_if_missing(
    data: Dict[str, Any],
    key: str,
    value: Any,
) -> Any:
    """
    Set a dictionary value only if the key is missing.

    Args:
        data: The dictionary to modify
        key: The key to set
        value: The value to set

    Returns:
        The current value at the key (existing or newly set)

    Example:
        >>> config = {}
        >>> set_if_missing(config, 'debug', False)
        False
        >>> set_if_missing(config, 'debug', True)
        False  # Already set, so returns existing value
    """
    if key not in data:
        data[key] = value
    return data[key]


class DictAccessor:
    """
    Chainable dictionary accessor for safe nested access.

    Example:
        >>> config = {'db': {'host': 'localhost', 'port': 5432}}
        >>> accessor = DictAccessor(config)
        >>> accessor.get('db').get('host').value()
        'localhost'
    """

    def __init__(self, data: Optional[Dict[str, Any]] = None, default: Any = None):
        """
        Initialize the accessor.

        Args:
            data: The dictionary to wrap
            default: Default value for missing keys
        """
        self._data = data
        self._default = default

    def get(self, key: str, default: Any = None) -> "DictAccessor":
        """
        Get a value and return a new accessor for chaining.

        Args:
            key: The key to retrieve
            default: Default value if key not found

        Returns:
            New DictAccessor with the retrieved value

        Example:
            >>> accessor = DictAccessor({'a': {'b': 1}})
            >>> accessor.get('a').get('b').value()
            1
        """
        if self._data is None:
            return DictAccessor(None, default or self._default)

        if isinstance(self._data, dict):
            value = self._data.get(key, default or self._default)
            return DictAccessor(value, default or self._default)

        return DictAccessor(None, default or self._default)

    def value(self, default: Any = None) -> Any:
        """
        Get the current value.

        Args:
            default: Default to return if current value is None

        Returns:
            The current value or default

        Example:
            >>> accessor = DictAccessor({'a': 1})
            >>> accessor.get('a').value()
            1
            >>> accessor.get('missing').value(default=0)
            0
        """
        if self._data is None:
            return default or self._default
        return self._data

    def __repr__(self) -> str:
        """String representation."""
        return f"DictAccessor({self._data!r})"
