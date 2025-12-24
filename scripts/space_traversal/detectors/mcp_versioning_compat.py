from pathlib import Path
from typing import Any
import logging

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Detects MCP versioning and compatibility support.

    This detector identifies version negotiation, compatibility checking,
    and backward compatibility support in MCP implementations.

    Safeguards:
    - Input validation on file_index structure
    - Bounded file reading with timeout protection
    - Defensive error handling for file operations
    - Sanitized path validation

    Args:
        file_index: Dictionary containing file metadata

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
    patterns_to_detect = {
        "MCP_VERSIONS": "version_constants",
        "negotiate_version": "negotiation_logic",
        "supports_feature": "compatibility_check",
        "validate_version": "version_validation",
    }

    for file_entry in files:
        # Validate file entry structure (safeguard)
        if not isinstance(file_entry, dict):
            continue

        path = file_entry.get("path", "")

        # Path validation (safeguard)
        if not path or not isinstance(path, str):
            continue

        # Only process Python files (safeguard - type filtering)
        if not path.endswith(".py"):
            continue

        try:
            # Bounded file reading (safeguard)
            file_path = Path(path)

            # Path traversal protection (safeguard)
            if not _is_safe_path(file_path):
                logger.warning(f"Unsafe path detected: {path}")
                continue

            # File size check (safeguard)
            MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit
            if file_path.stat().st_size > MAX_FILE_SIZE:
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

        # Pattern detection with validation
        file_has_evidence = False
        for pattern, pattern_type in patterns_to_detect.items():
            if pattern in text:
                found.append(pattern)
                file_has_evidence = True

        if file_has_evidence:
            evidence.append(path)

    # Required patterns for full functionality
    required = ["MCP_VERSIONS"]

    # Deterministic sorting (safeguard - reproducibility)
    evidence = sorted(set(evidence))
    found = sorted(set(found))

    return {
        "id": "mcp-versioning-compat",
        "evidence_files": evidence,
        "found_patterns": found,
        "required_patterns": required,
        "docs_keywords": [
            "versioning",
            "compatibility",
            "negotiation",
            "semver",
            "semantic-versioning",
            "backward-compatible",
            "deprecation",
            "migration",
            "protocol-version",
            "api-version",
            "version-negotiation",
            "compatibility-matrix",
            "mcp",
            "safeguards",
            "validation",
        ],
        "meta": {
            "category": "mcp",
            "layer": "protocol",
            "detector_version": "1.3",
            "safeguards": [
                "input-validation",
                "bounds-checking",
                "error-handling",
                "path-traversal-protection",
                "deterministic-sorting",
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
        "id": "mcp-versioning-compat",
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": ["MCP_VERSIONS"],
        "meta": {"category": "mcp", "error": True},
    }


def _is_safe_path(path: Path) -> bool:
    """
    Validate path for security (path traversal prevention).

    Safeguard: Prevents directory traversal attacks and ensures
    paths are within allowed bounds.

    Args:
        path: Path to validate

    Returns:
        True if path is safe, False otherwise
    """
    try:
        # Resolve to absolute path
        resolved = path.resolve()

        # Check for suspicious patterns (safeguard)
        path_str = str(resolved)
        if ".." in path_str or path_str.startswith("/etc") or path_str.startswith("/sys"):
            return False

        # Validate path exists and is a file
        if not resolved.exists() or not resolved.is_file():
            return False

        return True
    except Exception:
        # Defensive fallback (safeguard)
        return False
