"""
P012: API Response Handling Utilities

Consolidates 291 occurrences of HTTP/API response handling patterns.

Example:
    # Instead of: response.json() with error handling
    data = get_json_response(response)

    # Instead of: check response.status_code manually
    handle_response(response, expected_status=200)
"""

import json
from typing import Any, Dict, List, Optional, Union

__all__ = [
    "handle_response",
    "get_json_response",
    "check_status",
    "ResponseParser",
    "ResponseError",
]


class ResponseError(Exception):
    """Raised when response handling fails."""

    pass


def handle_response(
    response: Any,
    expected_status: Union[int, List[int]] = 200,
    raise_on_error: bool = True,
) -> bool:
    """
    Handle HTTP response with status check.

    Args:
        response: HTTP response object
        expected_status: Expected status code(s)
        raise_on_error: If True, raise on status mismatch

    Returns:
        True if status matches

    Raises:
        ResponseError: If status doesn't match and raise_on_error=True
    """
    expected = [expected_status] if isinstance(expected_status, int) else expected_status
    status = getattr(response, "status_code", None)

    if status not in expected:
        msg = f"Expected status {expected}, got {status}"
        if raise_on_error:
            raise ResponseError(msg)
        return False

    return True


def check_status(
    response: Any,
    codes: List[int] = None,
) -> None:
    """
    Assert response has expected status code.

    Args:
        response: HTTP response
        codes: List of acceptable codes (default: [200])

    Raises:
        ResponseError: If status doesn't match
    """
    if codes is None:
        codes = [200]

    handle_response(response, expected_status=codes, raise_on_error=True)


def get_json_response(
    response: Any,
    path: Optional[str] = None,
    default: Any = None,
) -> Any:
    """
    Get JSON data from response.

    Args:
        response: HTTP response object
        path: Optional dot-separated path to extract (e.g., 'data.users')
        default: Default value if parsing fails

    Returns:
        Parsed JSON or default
    """
    try:
        data = response.json()
    except (AttributeError, json.JSONDecodeError, ValueError):
        return default

    if path:
        parts = path.split(".")
        for part in parts:
            if isinstance(data, dict):
                data = data.get(part)
            else:
                return default
        return data

    return data


class ResponseParser:
    """Parse HTTP responses with multiple methods."""

    def __init__(self, response: Any):
        self.response = response

    def json(self, default: Any = None) -> Any:
        """Get JSON data."""
        return get_json_response(self.response, default=default)

    def text(self, default: str = "") -> str:
        """Get response text."""
        return getattr(self.response, "text", default)

    def headers(self) -> Dict[str, str]:
        """Get response headers."""
        return getattr(self.response, "headers", {})

    def status(self) -> int:
        """Get status code."""
        return getattr(self.response, "status_code", 0)

    def is_success(self) -> bool:
        """Check if response indicates success."""
        status = self.status()
        return 200 <= status < 300

    def is_error(self) -> bool:
        """Check if response indicates error."""
        return not self.is_success()
