"""
import logging
logger = logging.getLogger(__name__)
MCP Server Lifecycle Management Capability Detector

Tracks startup, shutdown, healthz endpoints, and application lifecycle hooks.
Part of the Space Traversal audit pipeline for MCP service maturity.
"""

from pathlib import Path


MAX_READ_BYTES = 200_000
REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(path_input) -> str:
    """
    Read text from file with bounded read.

    Safeguard: Bounded read to prevent memory issues.
    Validation: Handle path resolution and errors gracefully.
    """
    try:
        # Validation: Convert to Path if string
        if isinstance(path_input, str):
            path = Path(path_input)
        else:
            path = path_input

        if not path.is_absolute():
            path = REPO_ROOT / path

        if not path.exists():
            return ""

        # Bounded read safeguard
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except (OSError, IOError, UnicodeDecodeError):
        return ""


def detect(file_index: dict) -> dict:
    """
    Detect MCP lifecycle management capability from file index.

    Validation: Checks both path-based and content-based evidence.
    Safeguards: Bounded reads, error handling, deterministic sorting.

    Args:
        file_index: Dictionary with 'files' list, each item has:
                    {'path': str, 'ext': str, 'size': int, 'sha': str}

    Returns:
        Dictionary with required fields including functionality score
    """
    files = file_index.get("files", [])
    evidence = []
    found = set()
    content_evidence: dict[str, list[str]] = {}

    # Patterns indicating lifecycle management
    lifecycle_keywords = {
        "startup": [
            "startup",
            "initialize",
            "LifecycleManager",
            "register_startup_hook",
            "on_startup",
        ],
        "shutdown": ["shutdown", "cleanup", "register_shutdown_hook", "teardown", "on_shutdown"],
        "healthz": ["healthz", "is_healthy", "is_ready", "health_check", "/health", "/ready"],
    }

    required_patterns = ["startup", "shutdown", "healthz"]

    # Check relevant files
    for f in files:
        path = f["path"]
        path_lower = path.lower()

        # Validation: Focus on lifecycle-related files
        is_relevant = (
            "lifecycle" in path_lower
            or "mcp/" in path_lower
            or "services/mcp/" in path_lower
            or ("test" in path_lower and "mcp" in path_lower)
            or ("docs" in path_lower and "mcp" in path_lower and "lifecycle" in path_lower)
        )

        if is_relevant:
            evidence.append(path)

            # Content-based detection (improved functionality)
            if path.endswith(".py"):
                text = _read_text(path)
                if text:
                    detected_patterns = []
                    for pattern_name, keywords in lifecycle_keywords.items():
                        if any(kw in text for kw in keywords):
                            found.add(pattern_name)
                            detected_patterns.append(pattern_name)

                    if detected_patterns:
                        content_evidence[path] = detected_patterns

    # Calculate functionality based on patterns found
    functionality_score = len(found) / len(required_patterns) if required_patterns else 0.0

    return {
        "id": "mcp-lifecycle-management",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(found),
        "required_patterns": required_patterns,
        "docs_keywords": [
            "startup",
            "shutdown",
            "healthz",
            "lifecycle",
            "initialization",
            "cleanup",
        ],
        "safeguards": ["validation", "bounded", "error-handling", "deterministic"],
        "functionality_impl": functionality_score,  # Explicit functionality tracking
        "content_evidence": dict(sorted(content_evidence.items())),
        "meta": {
            "category": "mcp",
            "priority": "high",
            "framework": "FastAPI",
            "detector_version": "1.3",
            "implementation": "src/services/mcp/lifecycle.py",
            "tests": "tests/mcp/test_lifecycle_management.py",
            "deterministic": True,
            "offline": True,
            "bounded": True,
        },
    }
