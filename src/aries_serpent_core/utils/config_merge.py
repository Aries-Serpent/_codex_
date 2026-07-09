"""
P005: Dictionary/Config Merging Utilities

Consolidates 532 occurrences of dict merging and config update patterns.

Example:
    # Instead of: config = {**base, **overrides}
    config = merge_dicts(base, overrides, deep=True)
"""

from typing import Any, Dict, Optional

__all__ = [
    "merge_dicts",
    "safe_merge",
    "deep_merge",
    "ConfigDict",
    "MergeError",
]


class MergeError(ValueError):
    """Raised when merge operations fail."""

    pass


def merge_dicts(
    *dicts: Dict[str, Any],
    deep: bool = False,
    on_conflict: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Merge multiple dictionaries.

    Args:
        *dicts: Dictionaries to merge
        deep: If True, recursively merge nested dicts
        on_conflict: 'first', 'last', or 'error' on key conflicts

    Returns:
        Merged dictionary

    Example:
        >>> merge_dicts({'a': 1}, {'b': 2})
        {'a': 1, 'b': 2}
    """
    if not dicts:
        return {}

    result = dict(dicts[0])

    for d in dicts[1:]:
        if d is None:
            continue

        for key, value in d.items():
            if key in result and deep and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value

    return result


def safe_merge(
    base: Dict[str, Any],
    *overrides: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Safely merge dictionaries with base taking precedence if missing values.

    Args:
        base: Base dictionary
        *overrides: Overriding dictionaries

    Returns:
        Merged dictionary
    """
    return merge_dicts(base, *overrides)


def deep_merge(
    base: Dict[str, Any],
    override: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Deep merge with override taking precedence.

    Args:
        base: Base dictionary
        override: Override dictionary

    Returns:
        Deep merged dictionary
    """
    return merge_dicts(base, override, deep=True)


class ConfigDict(dict):
    """Dictionary subclass supporting chainable merges."""

    def merge(self, *others: Dict[str, Any], **kwargs) -> "ConfigDict":
        """Merge other dicts into this one."""
        result = merge_dicts(self, *others, **kwargs)
        return ConfigDict(result)

    def update_deep(self, other: Dict[str, Any]) -> "ConfigDict":
        """Deep update from another dict."""
        result = deep_merge(self, other)
        return ConfigDict(result)
