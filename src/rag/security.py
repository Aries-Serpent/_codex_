"""
Security utilities for RAG pipeline - Input validation and sanitization.

This module provides security functions for the RAG pipeline to prevent:
- SQL injection attacks via ChromaDB queries
- Code injection via filter parameters
- Path traversal attacks
- DoS via oversized inputs

Security Fixes for Issue #5299:
- ChromaDB code injection vulnerability (CVE-2025-XXXXX)
- Input validation for all user-supplied data
"""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Maximum lengths for input validation
MAX_QUERY_LENGTH = 10000
MAX_FILTER_KEYS = 50
MAX_FILTER_VALUE_LENGTH = 1000
MAX_METADATA_SIZE = 50000

# Pattern for SQL injection detection
SQL_INJECTION_PATTERNS = [
    r"(?i)(union|select|insert|update|delete|drop|create|alter)",
    r"(?i)(;|--|\*/|/\*)",
    r"(?i)(exec|execute|script)",
]

# Pattern for code injection detection
CODE_INJECTION_PATTERNS = [
    r"(__import__|eval|exec|compile|__code__|__globals__|__builtins__)",
    r"(os\.|sys\.|subprocess\.|pickle\.)",
    r"(\${|@\{|{{)",
]


def sanitize_query(query: str) -> str:
    """
    Sanitize user-supplied query string.

    Args:
        query: Raw query string from user

    Returns:
        Sanitized query string

    Raises:
        ValueError: If query fails security checks
    """
    if not isinstance(query, str):
        raise ValueError("Query must be a string")

    if not query.strip():
        raise ValueError("Query cannot be empty")

    if len(query) > MAX_QUERY_LENGTH:
        raise ValueError(f"Query exceeds maximum length of {MAX_QUERY_LENGTH}")

    # Detect potential SQL injection attempts
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, query):
            logger.warning(f"Potential SQL injection detected in query: {query[:100]}")
            raise ValueError("Query contains potentially dangerous SQL syntax")

    # Remove/escape dangerous characters that might be used in injection
    sanitized = query.strip()

    # Replace multiple spaces with single space (normalization)
    sanitized = re.sub(r"\s+", " ", sanitized)

    logger.debug(f"Query sanitized: {len(sanitized)} chars")
    return sanitized


def validate_filters(filters: Optional[dict]) -> dict[str, Any]:
    """
    Validate and sanitize filter parameters.

    Args:
        filters: Dictionary of filter parameters

    Returns:
        Validated filter dictionary

    Raises:
        ValueError: If filters fail security checks
    """
    if filters is None:
        return {}

    if not isinstance(filters, dict):
        raise ValueError("Filters must be a dictionary")

    if len(filters) > MAX_FILTER_KEYS:
        raise ValueError(f"Filters exceed maximum key count of {MAX_FILTER_KEYS}")

    validated_filters: dict[str, Any] = {}
    for key, value in filters.items():
        # Validate filter key
        if not isinstance(key, str):
            raise ValueError(f"Filter key must be a string, got {type(key)}")

        if not key.isidentifier():
            raise ValueError(f"Invalid filter key: {key} (must be valid identifier)")

        # Check for code injection patterns in key
        if _contains_code_injection(key):
            logger.warning(f"Potential code injection detected in filter key: {key}")
            raise ValueError("Filter key contains potentially dangerous code patterns")

        # Validate filter value
        if isinstance(value, str):
            if len(value) > MAX_FILTER_VALUE_LENGTH:
                raise ValueError(f"Filter value exceeds maximum length of {MAX_FILTER_VALUE_LENGTH}")

            if _contains_code_injection(value):
                logger.warning(f"Potential code injection detected in filter value: {value[:100]}")
                raise ValueError("Filter value contains potentially dangerous code patterns")

            validated_filters[key] = value.strip()
        elif isinstance(value, (int, float, bool)):
            validated_filters[key] = value
        elif value is None:
            validated_filters[key] = None
        else:
            raise ValueError(
                f"Filter value must be string, number, boolean, or null, got {type(value)}"
            )

    logger.debug(f"Filters validated: {len(validated_filters)} keys")
    return validated_filters


def validate_metadata(metadata: Optional[dict]) -> dict[str, Any]:
    """
    Validate and sanitize metadata dictionary.

    Args:
        metadata: Dictionary of metadata

    Returns:
        Validated metadata dictionary

    Raises:
        ValueError: If metadata fails security checks
    """
    if metadata is None:
        return {}

    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary")

    # Check total metadata size
    import json

    metadata_size = len(json.dumps(metadata))
    if metadata_size > MAX_METADATA_SIZE:
        raise ValueError(f"Metadata exceeds maximum size of {MAX_METADATA_SIZE} bytes")

    validated_metadata: dict[str, Any] = {}
    for key, value in metadata.items():
        if not isinstance(key, str):
            raise ValueError("Metadata key must be a string")

        if _contains_code_injection(key):
            logger.warning(f"Potential code injection in metadata key: {key}")
            raise ValueError("Metadata key contains potentially dangerous code patterns")

        # Recursively validate nested values (but prevent deep nesting)
        if isinstance(value, (str, int, float, bool)):
            validated_metadata[key] = value
        elif isinstance(value, dict):
            # Prevent deep nesting (max 1 level)
            for subkey, subvalue in value.items():
                if isinstance(subvalue, dict):
                    raise ValueError("Metadata nesting exceeds maximum depth of 1")

                if not isinstance(subkey, str):
                    raise ValueError("Nested metadata key must be a string")

                if _contains_code_injection(subkey):
                    raise ValueError("Nested metadata key contains dangerous code patterns")

            validated_metadata[key] = value
        elif value is None:
            validated_metadata[key] = None
        else:
            raise ValueError(f"Metadata value type {type(value)} not supported")

    logger.debug(f"Metadata validated: {len(validated_metadata)} keys")
    return validated_metadata


def _contains_code_injection(value: str) -> bool:
    """
    Check if a string contains potential code injection patterns.

    Args:
        value: String to check

    Returns:
        True if potential injection patterns found, False otherwise
    """
    for pattern in CODE_INJECTION_PATTERNS:
        if re.search(pattern, value):
            return True
    return False


def validate_document_id(doc_id: str) -> str:
    """
    Validate document ID.

    Args:
        doc_id: Document ID string

    Returns:
        Validated document ID

    Raises:
        ValueError: If doc_id fails validation
    """
    if not isinstance(doc_id, str):
        raise ValueError("Document ID must be a string")

    if not doc_id.strip():
        raise ValueError("Document ID cannot be empty")

    if len(doc_id) > 256:
        raise ValueError("Document ID exceeds maximum length of 256")

    # Allow alphanumeric, hyphens, underscores, and dots
    if not re.match(r"^[a-zA-Z0-9._\-]+$", doc_id):
        raise ValueError("Document ID contains invalid characters")

    return doc_id.strip()


def validate_top_k(top_k: int) -> int:
    """
    Validate top_k parameter.

    Args:
        top_k: Number of results to return

    Returns:
        Validated top_k value

    Raises:
        ValueError: If top_k is invalid
    """
    if not isinstance(top_k, int):
        raise ValueError("top_k must be an integer")

    if top_k <= 0:
        raise ValueError("top_k must be greater than 0")

    if top_k > 100:
        logger.warning(f"top_k={top_k} exceeds recommended maximum of 100, capping to 100")
        return 100

    return top_k
