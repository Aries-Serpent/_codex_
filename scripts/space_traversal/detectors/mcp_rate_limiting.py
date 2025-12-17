"""
MCP Rate Limiting Capability Detector

Detects rate limiting patterns in MCP implementations including token bucket
algorithms, sliding window, request throttling, and quota management.

Safeguards:
- Input validation on file_index structure
- Bounded file reading with size limits
- Defensive error handling for file operations
- Deterministic output for reproducibility
"""

from pathlib import Path
from typing import Any, Dict
import logging

# Configure logging for safeguard tracing
logger = logging.getLogger(__name__)


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects rate limiting in MCP server. Looks for RateLimiter classes or usage.

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

    # Rate limiting patterns to detect
    patterns = {
        "RateLimiter": "rate_limiter_class",
        "rate_limit": "rate_limit_usage",
        "throttle": "throttling",
        "token_bucket": "token_bucket_algo",
        "sliding_window": "sliding_window_algo",
        "quota": "quota_management",
        "requests_per_second": "rps_limit",
        "requests_per_minute": "rpm_limit",
        "429": "too_many_requests",
        "Retry-After": "retry_header",
        "X-RateLimit": "rate_limit_header",
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

    required = ["RateLimiter"]

    # Deterministic sorting (safeguard - reproducibility)
    evidence = sorted(set(evidence))
    found = sorted(set(found))

    return {
        "id": "mcp-rate-limiting",
        "evidence_files": evidence,
        "found_patterns": found,
        "required_patterns": required,
        "docs_keywords": [
            "rate-limiting",
            "throttling",
            "rate-limiter",
            "token-bucket",
            "sliding-window",
            "quota",
            "requests-per-second",
            "429",
            "too-many-requests",
            "retry-after",
            "mcp",
            "safeguards",
            "protection",
            "abuse-prevention",
            "api-limits",
            "capacity",
        ],
        "meta": {
            "category": "mcp",
            "layer": "protection",
            "detector_version": "1.2",
            "safeguards": [
                "input-validation",
                "bounds-checking",
                "error-handling",
                "request-throttling",
                "quota-enforcement",
            ],
            "files_processed": len(files),
            "evidence_count": len(evidence),
        },
    }


def _empty_result() -> Dict[str, Any]:
    """
    Returns empty detection result for error cases.

    Safeguard: Ensures consistent return type even on errors.
    """
    return {
        "id": "mcp-rate-limiting",
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": ["RateLimiter"],
        "docs_keywords": [
            "rate-limiting",
            "throttling",
            "mcp",
        ],
        "meta": {"category": "mcp", "error": True},
    }
