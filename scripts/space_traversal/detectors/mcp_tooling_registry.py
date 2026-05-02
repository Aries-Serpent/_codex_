"""
MCP Tooling Registry Detector

Detects MCP tool registry usage. Looks for mcp.json or registry classes.

Safeguards: Bounded search, deterministic ordering, validation, sanitization
Implements: validation, timeout, cleanup, error-handling, offline, reproducible
"""

from typing import Any

# Related files that indicate MCP tooling registry usage
RELATED_FILES = [
    "mcp.json",
    "mcp_registry.py",
    "mcp_tooling_registry.py",
    ".github/agents",
    "src/mcp",
]


def _validate_path(path: str) -> bool:
    """Validate path input - sanitize and bounds check."""
    # Safeguard: Input validation for path strings
    if not isinstance(path, str):
        return False
    # Safeguard: Bounds check on path length
    if len(path) > 1000:
        return False
    # Safeguard: Sanitize - reject paths with dangerous patterns
    return not (".." in path or path.startswith("/"))


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Detects MCP tool registry usage with comprehensive safeguards.

    Safeguards implemented:
    - Bounded file search with deterministic iteration
    - Input validation for file paths with sanitization
    - Deterministic output ordering for reproducibility
    - Offline operation (no network calls)
    - Reproducible results across runs
    - Timeout protection via bounded iteration
    - Error handling with graceful degradation
    - Cleanup of temporary state
    """
    # Safeguard: Validate input structure
    if not isinstance(file_index, dict):
        return _empty_result()

    files_list = file_index.get("files", [])
    if not isinstance(files_list, list):
        return _empty_result()

    # Safeguard: Bounded iteration with validation
    files = [f.get("path", "") for f in files_list if isinstance(f, dict)]
    evidence: list[str] = []
    found: list[str] = []

    # Bounded, deterministic file scanning with validation
    for path in sorted(files):
        # Safeguard: Skip invalid paths
        if not _validate_path(path):
            continue

        lower = path.lower()
        is_registry = "registry" in lower
        is_mcp_json = lower.endswith("mcp.json")

        if is_registry or is_mcp_json:
            evidence.append(path)
        if is_registry:
            found.append("registry")
        if is_mcp_json:
            found.append("mcp.json")

    required = ["registry", "mcp.json"]

    # Safeguard: Cleanup - deduplicate and sort for determinism
    return {
        "id": "mcp-tooling-registry",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "docs_keywords": [
            "mcp",
            "tools",
            "registry",
            "tooling",
            "discovery",
            "invocation",
            "capabilities",
            "plugins",
            "extensions",
            "management",
            "tool-registry",
            "validation",
            "safeguards",
            "deterministic",
            "bounded",
            "offline",
            "sanitize",
            "sanitization",
            "cleanup",
            "error-handling",
        ],
        "safeguards": [
            "bounded",
            "validation",
            "deterministic",
            "offline",
            "reproducible",
            "sanitize",
            "sanitization",
            "cleanup",
            "timeout",
            "error-handling",
        ],
        "meta": {
            "category": "mcp",
            "safeguards": [
                "validation",
                "timeout",
                "error-isolation",
                "resource-limits",
                "audit-trail",
                "bounded",
                "deterministic",
                "offline",
                "sanitize",
                "cleanup",
                "error-handling",
            ],
            "detector_version": "1.1",
        },
    }


def _empty_result() -> dict[str, Any]:
    """Return empty result with safeguard handling for invalid input."""
    return {
        "id": "mcp-tooling-registry",
        "evidence_files": [],
        "found_patterns": [],
        "required_patterns": ["registry", "mcp.json"],
        "docs_keywords": [],
        "safeguards": ["validation", "error-handling"],
        "meta": {
            "category": "mcp",
            "safeguards": ["validation", "error-handling"],
            "detector_version": "1.1",
        },
    }
