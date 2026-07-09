"""
P007: JSON Serialization/Deserialization Utilities

Consolidates 897 occurrences of json.load/dump patterns.

Example:
    # Instead of: json.load(open('file.json'))
    data = load_json('file.json', default={})

    # Instead of: json.dumps(data)
    json_str = dump_json(data, pretty=True)
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Type, TypeVar

__all__ = [
    "load_json",
    "dump_json",
    "json_to_obj",
    "obj_to_json",
    "safe_json_loads",
    "JSONError",
]

T = TypeVar("T")


class JSONError(ValueError):
    """Raised when JSON operations fail."""

    pass


def safe_json_loads(data: str, default: Any = None) -> Any:
    """
    Safely load JSON from a string.

    Args:
        data: JSON string to parse
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default value

    Example:
        >>> safe_json_loads('{"a": 1}')
        {'a': 1}
        >>> safe_json_loads('invalid', default={})
        {}
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return default


def load_json(
    file_path: str,
    default: Any = None,
    encoding: str = "utf-8",
) -> Any:
    """
    Load JSON from a file.

    Args:
        file_path: Path to JSON file
        default: Default value if file not found or invalid
        encoding: File encoding (default: utf-8)

    Returns:
        Parsed JSON data or default

    Example:
        >>> data = load_json('config.json', default={})
    """
    try:
        path = Path(file_path)
        with open(path, "r", encoding=encoding) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        return default


def dump_json(
    data: Any,
    file_path: Optional[str] = None,
    pretty: bool = False,
    encoding: str = "utf-8",
) -> str:
    """
    Dump data to JSON string or file.

    Args:
        data: Data to serialize
        file_path: Optional file path to write to
        pretty: If True, format with indentation
        encoding: File encoding (default: utf-8)

    Returns:
        JSON string

    Example:
        >>> dump_json({'a': 1}, pretty=True)
        '{\\n  "a": 1\\n}'
    """
    kwargs = {"indent": 2 if pretty else None}
    json_str = json.dumps(data, **kwargs)

    if file_path:
        path = Path(file_path)
        with open(path, "w", encoding=encoding) as f:
            f.write(json_str)

    return json_str


def json_to_obj(data: Dict[str, Any], obj_class: Type[T]) -> T:
    """
    Convert JSON dict to object.

    Args:
        data: JSON dictionary
        obj_class: Target class

    Returns:
        Instance of obj_class

    Example:
        >>> class User:
        ...     def __init__(self, name: str): self.name = name
        >>> json_to_obj({'name': 'John'}, User)
        <User object>
    """
    if hasattr(obj_class, "from_dict"):
        return obj_class.from_dict(data)
    return obj_class(**data)


def obj_to_json(obj: Any) -> Dict[str, Any]:
    """
    Convert object to JSON-compatible dict.

    Args:
        obj: Object to serialize

    Returns:
        JSON-compatible dictionary

    Example:
        >>> class User:
        ...     def __init__(self, name): self.name = name
        ...     def to_dict(self): return {'name': self.name}
        >>> obj_to_json(User('John'))
        {'name': 'John'}
    """
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise JSONError(f"Cannot serialize {type(obj)} to JSON")
