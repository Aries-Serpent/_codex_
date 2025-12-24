"""
MCP Error Handling Capability Detector

Detects structured error handling patterns in MCP implementations including
error classes, error codes, JSON-RPC error responses, and recovery mechanisms.

Safeguards:
- Input validation on file_index structure
- Bounded file reading with size limits
- Defensive error handling for file operations
- Deterministic output for reproducibility
"""

from pathlib import Path
from typing import Any
import logging

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Detects structured error handling for MCP (MCPError classes, error codes).

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

    # Error handling patterns to detect
    patterns = {
        "MCPError": "error_class",
        "jsonrpc": "protocol",
        '"error"': "error_payload",
        "error_code": "error_codes",
        "ErrorCode": "error_enum",
        "try:": "exception_handling",
        "except": "exception_handling",
        "raise": "exception_raising",
        "traceback": "error_tracing",
        "error_handler": "error_handler",
        "on_error": "error_callback",
    }

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

        # Pattern detection
        file_has_evidence = False
        for pattern, pattern_type in patterns.items():
            if pattern in text:
                found.append(pattern)
                file_has_evidence = True

        if file_has_evidence:
            evidence.append(path)

    required = ["MCPError"]

    # Deterministic sorting (safeguard - reproducibility)
    evidence = sorted(set(evidence))
    found = sorted(set(found))

    return {
        "id": "mcp-error-handling",
        "evidence_files": evidence,
        "found_patterns": found,
        "required_patterns": required,
        "docs_keywords": [
            "error",
            "exception",
            "handling",
            "mcp-error",
            "error-code",
            "jsonrpc",
            "error-response",
            "recovery",
            "retry",
            "fallback",
            "graceful-degradation",
            "error-handler",
            "traceback",
            "mcp",
            "safeguards",
            "validation",
            "robustness",
        ],
        "meta": {
            "category": "mcp",
            "layer": "reliability",
            "detector_version": "1.2",
            "safeguards": [
                "input-validation",
                "bounds-checking",
                "error-handling",
                "graceful-degradation",
                "logging",
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
        "id": "mcp-error-handling",
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": ["MCPError"],
        "docs_keywords": [
            "error",
            "exception",
            "handling",
            "mcp",
        ],
        "meta": {"category": "mcp", "error": True},
    }
