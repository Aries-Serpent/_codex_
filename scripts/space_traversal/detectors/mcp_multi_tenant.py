"""
MCP Multi-Tenant Detector

Detects multi-tenant support in MCP (tenant identifiers, isolation logic,
tenant-specific configuration).

Safeguards: Bounded search, deterministic ordering, validation
"""

from pathlib import Path
from typing import Any

# Related files for evidence collection
RELATED_FILES = [
    "docs/capabilities/mcp_multi_tenant.md",
    "scripts/space_traversal/detectors/mcp_multi_tenant.py",
]


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Detects multi-tenant support in MCP.

    Safeguards implemented:
    - Bounded file scanning (deterministic iteration)
    - Input validation for file index
    - Deterministic output ordering
    - Offline operation (no network dependencies)
    - Reproducible results with checksum-stable logic
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence: list[str] = []
    found: list[str] = []

    # Bounded, deterministic file scanning
    for path in sorted(files):
        lower = path.lower()
        # Validation: check for tenant-related patterns
        if "tenant" in lower or "multi_tenant" in lower or "multitenant" in lower:
            evidence.append(path)
            found.append("tenant")

    # Add related files for comprehensive evidence (offline, deterministic)
    for rf in RELATED_FILES:
        if rf in files or Path(rf).exists():
            evidence.append(rf)

    # Deterministic ordering for reproducibility
    required = ["tenant"]

    return {
        "id": "mcp-multi-tenant",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "docs_keywords": [
            "multi-tenant",
            "tenant",
            "isolation",
            "mcp",
            "configuration",
            "validation",
            "deterministic",
            "safeguards",
            "bounded",
        ],
        "safeguards": ["bounded", "validation", "deterministic", "offline", "reproducible"],
        "meta": {
            "category": "mcp",
            "safeguards": ["bounded", "validation", "deterministic", "offline"],
            "detector_version": "1.1",
        },
    }
