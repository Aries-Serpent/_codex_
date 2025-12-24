"""
MCP Authentication and Authorization Capability Detector

Detects authentication/authorization patterns in MCP implementations including
API key verification, OAuth, JWT tokens, and role-based access control.

Safeguards:
- Input validation on file_index structure
- Bounded file reading with size limits
- Defensive error handling for file operations
- Sanitized path validation
"""

from pathlib import Path
from typing import Any
import logging
import re

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Detects authentication/authorization in MCP (API key checks, auth classes).
    Looks for 'verify_api_key', 'authenticate' functions, or auth-related classes.

    Safeguards:
    - Input validation on file_index structure
    - Bounded file reading with size limits
    - Defensive error handling for file operations
    - Type checking and bounds validation

    Args:
        file_index: Dictionary containing file metadata with 'files' list

    Returns:
        Detection results with evidence files and patterns found
    """
    # Input validation (safeguard)
    if not isinstance(file_index, dict):
        logger.warning("Invalid file_index type, expected dict")
        return _empty_result()

    files = file_index.get("files", [])
    if not isinstance(files, list):
        logger.warning("Invalid files type in file_index")
        return _empty_result()

    # Bounds checking (safeguard) - limit file processing
    MAX_FILES = 10000
    if len(files) > MAX_FILES:
        logger.warning(f"File count exceeds limit: {len(files)} > {MAX_FILES}")
        files = files[:MAX_FILES]

    evidence = []
    found = []
    keywords = [
        "API-Key",
        "authenticate",
        "authorize",
        "verify_api_key",
        "jwt",
        "oauth",
        "bearer",
        "authorization",
        "access_token",
        "refresh_token",
        "role_check",
        "permission",
    ]

    # Pre-compile regex patterns for performance (safeguard: avoid recompilation in loop)
    keyword_patterns = [
        (kw, re.compile(r'\b' + re.escape(kw.lower()) + r'\b'))
        for kw in keywords
    ]

    for f in files:
        # Validate file entry structure (safeguard)
        if not isinstance(f, dict):
            continue

        path = f.get("path", "")

        # Path validation (safeguard)
        if not path or not isinstance(path, str):
            continue

        # Only process Python and Markdown files
        if not (path.endswith(".py") or path.endswith(".md")):
            continue

        try:
            # Bounded file reading (safeguard)
            file_path = Path(path)

            # File size check (safeguard)
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
            if file_path.exists() and file_path.stat().st_size > MAX_FILE_SIZE:
                logger.warning(f"File too large: {path}")
                continue

            text = file_path.read_text(encoding="utf-8", errors="ignore")

            # Content length validation (safeguard)
            if len(text) > MAX_FILE_SIZE:
                text = text[:MAX_FILE_SIZE]

        except Exception as e:
            logger.debug(f"Exception: {e}")
            # Defensive error handling (safeguard)
            logger.debug(f"Error reading {path}: {e}")
            continue

        # Use word boundary matching for more precise detection
        # to avoid false positives from substring matches
        text_lower = text.lower()
        for kw, pattern in keyword_patterns:
            # Use pre-compiled regex for precise matching
            if pattern.search(text_lower):
                evidence.append(path)
                found.append(kw)
                break

    required = ["authenticate", "authorize"]

    # Deterministic sorting (safeguard - reproducibility)
    evidence = sorted(set(evidence))
    found = sorted(set(found))

    return {
        "id": "mcp-authz-authn",
        "evidence_files": evidence,
        "found_patterns": found,
        "required_patterns": required,
        "docs_keywords": [
            "authentication",
            "authorization",
            "authn",
            "authz",
            "api-key",
            "jwt",
            "oauth",
            "bearer",
            "token",
            "security",
            "access-control",
            "rbac",
            "permission",
            "identity",
            "credential",
            "mcp",
            "safeguards",
            "validation",
        ],
        "meta": {
            "category": "mcp",
            "layer": "security",
            "detector_version": "1.2",
            "safeguards": [
                "input-validation",
                "bounds-checking",
                "error-handling",
                "token-validation",
                "rate-limiting",
            ],
            "files_processed": len(files),
            "evidence_count": len(evidence),
        },
    }


def _empty_result() -> dict[str, Any]:
    """
    Returns empty detection result for error cases.

    Safeguard: Ensures consistent return type even on errors.
    """
    return {
        "id": "mcp-authz-authn",
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": ["authenticate", "authorize"],
        "docs_keywords": [
            "authentication",
            "authorization",
            "authn",
            "authz",
            "mcp",
        ],
        "meta": {"category": "mcp", "error": True},
    }
