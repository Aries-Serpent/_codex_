"""
Dictionary and Configuration Utilities

This module provides reusable functions for common dictionary operations,
especially those working with nested dictionaries and API responses.

Functions:
    - safe_get_nested: Safely get nested dict values
    - extract_user_login: Extract login from user dict
    - extract_timestamp: Extract and parse timestamp from dict
    - dict_deep_merge: Deep merge two dictionaries

Author: Codex Team
"""

from __future__ import annotations

from typing import Any


def safe_get_nested(
    obj: dict[str, Any],
    *keys: str,
    default: Any = None,
) -> Any:
    """
    Safely get nested dictionary values without KeyError.

    Args:
        obj: The dictionary to traverse
        *keys: Variable number of keys to traverse
        default: Default value if key not found

    Returns:
        Value at path or default if not found

    Examples:
        >>> d = {"a": {"b": {"c": 42}}}
        >>> safe_get_nested(d, "a", "b", "c")
        42
        >>> safe_get_nested(d, "a", "x", "c", default=None)
        None
    """
    current = obj
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key)
            if current is None:
                return default
        else:
            return default
    return current


def extract_user_login(user_dict: dict[str, Any] | None) -> str:
    """
    Extract login from user dictionary (common in GitHub API).

    Handles various user dict formats gracefully.

    Args:
        user_dict: User dictionary from API response

    Returns:
        Login string or empty string if not found
    """
    if not user_dict:
        return ""
    return user_dict.get("login", "")


def extract_timestamp(
    data_dict: dict[str, Any],
    field_name: str = "created_at",
) -> str:
    """
    Extract timestamp field from dictionary.

    Handles missing fields gracefully.

    Args:
        data_dict: Dictionary containing timestamp
        field_name: Name of the timestamp field

    Returns:
        Timestamp string or empty string if not found
    """
    if not data_dict:
        return ""
    return data_dict.get(field_name, "")


def dict_deep_merge(
    base: dict[str, Any],
    override: dict[str, Any],
) -> dict[str, Any]:
    """
    Deep merge two dictionaries, with override values taking precedence.

    Args:
        base: Base dictionary
        override: Dictionary with override values

    Returns:
        Merged dictionary
    """
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = dict_deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def extract_commit_author(commit_dict: dict[str, Any]) -> str:
    """
    Extract author login from commit dict (GitHub API).

    Tries author first, then falls back to committer.

    Args:
        commit_dict: Commit dictionary

    Returns:
        Author login or empty string
    """
    author_login = safe_get_nested(commit_dict, "author", "login", default="")
    if author_login:
        return author_login
    return safe_get_nested(commit_dict, "committer", "login", default="")


def extract_commit_timestamp(commit_dict: dict[str, Any]) -> str:
    """
    Extract timestamp from commit dict (GitHub API).

    Uses committer date, falls back to author date.

    Args:
        commit_dict: Commit dictionary

    Returns:
        ISO-8601 timestamp or empty string
    """
    committer_ts = safe_get_nested(
        commit_dict, "commit", "committer", "date", default=""
    )
    if committer_ts:
        return committer_ts
    
    return safe_get_nested(
        commit_dict, "commit", "author", "date", default=""
    )


def chunk_list(items: list[Any], chunk_size: int) -> list[list[Any]]:
    """
    Split a list into chunks of specified size.

    Args:
        items: List to chunk
        chunk_size: Size of each chunk

    Returns:
        List of chunks (last chunk may be smaller)
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
