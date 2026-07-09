"""
P013: YAML Operations Utilities

Consolidates 59 occurrences of yaml.load/dump patterns.

Example:
    # Instead of: yaml.safe_load(open('file.yml'))
    config = load_yaml('config.yml', default={})
"""

from pathlib import Path
from typing import Any, Optional

import yaml

__all__ = [
    "load_yaml",
    "dump_yaml",
    "YAMLError",
]


class YAMLError(ValueError):
    """Raised when YAML operations fail."""

    pass


def load_yaml(
    file_path: str,
    default: Any = None,
    encoding: str = "utf-8",
) -> Any:
    """Load YAML from file."""
    try:
        path = Path(file_path)
        with open(path, "r", encoding=encoding) as f:
            return yaml.safe_load(f)
    except (FileNotFoundError, yaml.YAMLError, IOError):
        return default


def dump_yaml(
    data: Any,
    file_path: Optional[str] = None,
    encoding: str = "utf-8",
) -> str:
    """Dump data to YAML string or file."""
    yaml_str = yaml.dump(data, default_flow_style=False)

    if file_path:
        path = Path(file_path)
        with open(path, "w", encoding=encoding) as f:
            f.write(yaml_str)

    return yaml_str
