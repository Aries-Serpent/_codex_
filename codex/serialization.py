"""Serialization module with secure deserialization - SECURE VERSION.

This module provides secure deserialization methods that prevent
insecure deserialization vulnerabilities (CWE-502).

Security Model:
- Uses json.loads() for untrusted data (JSON is inherently safe)
- Avoids pickle.loads() for untrusted sources
- Validates data structure after deserialization
- Type hints ensure expected data types
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union

logger = logging.getLogger(__name__)


def safe_deserialize_json(data_str: str, expected_type: Optional[type] = None) -> Any:
    """Safely deserialize JSON string from untrusted source.

    Uses json.loads() which is safe because JSON cannot execute code.
    This is the SECURE alternative to pickle.loads().

    Args:
        data_str: JSON string from untrusted source
        expected_type: Optional expected type for validation

    Returns:
        Deserialized Python object

    Raises:
        ValueError: If data is invalid JSON or doesn't match expected type
        TypeError: If expected_type is not a valid type
    """
    if not isinstance(data_str, str):
        raise ValueError(f"data_str must be a string, got {type(data_str)}")

    try:
        # SECURE: json.loads() is safe - it cannot execute arbitrary code
        # JSON only supports basic types: str, int, float, bool, None, list, dict
        data = json.loads(data_str)
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON: %s", str(e))
        raise ValueError(f"Invalid JSON: {e}") from e

    # Validate against expected type if provided
    if expected_type is not None:
        if not isinstance(expected_type, type):
            raise TypeError(f"expected_type must be a type, got {type(expected_type)}")

        if not isinstance(data, expected_type):
            raise ValueError(
                f"Deserialized data is {type(data).__name__}, expected {expected_type.__name__}"
            )

    return data


def safe_deserialize_dict(json_str: str) -> Dict[str, Any]:
    """Safely deserialize JSON string to dictionary.

    Ensures the deserialized object is a dictionary.

    Args:
        json_str: JSON string from untrusted source

    Returns:
        Dictionary

    Raises:
        ValueError: If JSON is invalid or doesn't deserialize to a dict
    """
    if not isinstance(json_str, str):
        raise ValueError(f"json_str must be a string, got {type(json_str)}")

    # SECURE: Use json.loads() with type validation
    return safe_deserialize_json(json_str, expected_type=dict)


def safe_deserialize_list(json_str: str) -> List[Any]:
    """Safely deserialize JSON string to list.

    Ensures the deserialized object is a list.

    Args:
        json_str: JSON string from untrusted source

    Returns:
        List

    Raises:
        ValueError: If JSON is invalid or doesn't deserialize to a list
    """
    if not isinstance(json_str, str):
        raise ValueError(f"json_str must be a string, got {type(json_str)}")

    # SECURE: Use json.loads() with type validation
    return safe_deserialize_json(json_str, expected_type=list)


def load_user_config(json_str: str) -> Dict[str, Any]:
    """Load user configuration from JSON string.

    This is the SECURE way to load untrusted configuration data.
    Never use pickle.loads() for untrusted data.

    Args:
        json_str: JSON configuration string from untrusted source

    Returns:
        Configuration dictionary

    Raises:
        ValueError: If configuration is invalid
    """
    if not isinstance(json_str, str):
        raise ValueError(f"json_str must be a string, got {type(json_str)}")

    # SECURE: json.loads() cannot execute arbitrary code
    config = safe_deserialize_dict(json_str)

    # Validate expected keys
    required_keys = {"version", "settings"}
    provided_keys = set(config.keys())

    # Check that required keys exist (can be relaxed based on requirements)
    if not required_keys.issubset(provided_keys):
        missing = required_keys - provided_keys
        logger.warning("Configuration missing expected keys: %s", missing)

    return config


def deserialize_and_validate(
    json_str: str, schema_validator: Optional[callable] = None
) -> Dict[str, Any]:
    """Deserialize JSON with optional schema validation.

    Args:
        json_str: JSON string from untrusted source
        schema_validator: Optional function to validate deserialized data

    Returns:
        Validated dictionary

    Raises:
        ValueError: If JSON is invalid or validation fails
    """
    if not isinstance(json_str, str):
        raise ValueError(f"json_str must be a string, got {type(json_str)}")

    # SECURE: Deserialize with json.loads()
    data = safe_deserialize_dict(json_str)

    # Apply schema validation if provided
    if schema_validator is not None:
        if not callable(schema_validator):
            raise TypeError("schema_validator must be callable")

        try:
            schema_validator(data)
        except Exception as e:
            logger.error("Schema validation failed: %s", str(e))
            raise ValueError(f"Schema validation failed: {e}") from e

    return data


# SECURITY NOTICE: DO NOT USE pickle.loads() FOR UNTRUSTED DATA
# ============================================================
# pickle.loads() can execute arbitrary Python code and should NEVER be used
# with untrusted input. Use json.loads() instead.
#
# Unsafe (DO NOT USE):
#   import pickle
#   data = pickle.loads(untrusted_string)  # CWE-502 vulnerability!
#
# Safe (USE THIS):
#   import json
#   data = json.loads(untrusted_string)  # Safe - cannot execute code
