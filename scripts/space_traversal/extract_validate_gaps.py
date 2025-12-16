"""
extract_validate_gaps.py
Canonical extraction implementation for gaps from decoded artifacts.
"""

from typing import Any, List


def extract_gaps(decoded_json: dict[str, Any]) -> List[Any]:
    """
    Extracts the 'gaps' from the decoded validator artifact.

    Parameters:
        decoded_json (dict): The decoded artifact JSON object

    Returns:
        List[Any]: List of gaps, or empty list if not present
    """
    gaps = decoded_json.get("gaps")
    if isinstance(gaps, list):
        return gaps
    elif gaps is not None:
        # For robustness, if gaps is a dict or other type, return as singleton list
        return [gaps]
    return []
