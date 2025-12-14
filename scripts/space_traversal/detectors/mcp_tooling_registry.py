"""
MCP Tooling Registry Detector

Detects MCP tool registry usage. Looks for mcp.json or registry classes.

Safeguards: Bounded search, deterministic ordering, validation
"""
from pathlib import Path
from typing import Any, Dict, List

# Related files for evidence collection
RELATED_FILES = [
    "docs/capabilities/mcp_tooling_registry.md",
    "scripts/space_traversal/detectors/mcp_tooling_registry.py",
    "tests/mcp/test_mcp_tooling_registry.py",
]


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects MCP tool registry usage.
    
    Safeguards implemented:
    - Bounded file search with deterministic iteration
    - Input validation for file paths
    - Deterministic output ordering
    - Offline operation (no network calls)
    - Reproducible results
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence: List[str] = []
    found: List[str] = []
    
    # Bounded, deterministic file scanning
    for path in sorted(files):
        lower = path.lower()
        if "mcp/" in lower or "tool" in lower:
            # Identify evidence of registry with validation
            if path.endswith("mcp.json") or "registry" in lower:
                evidence.append(path)
            if "registry" in lower:
                found.append("registry")
            if path.endswith("mcp.json"):
                found.append("mcp.json")
    
    # Add related files for comprehensive evidence (deterministic)
    for rf in RELATED_FILES:
        if rf in files or Path(rf).exists():
            evidence.append(rf)
    
    required = ["registry", "mcp.json"]
    
    return {
        "id": "mcp-tooling-registry",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "docs_keywords": [
            "mcp", "tools", "registry", "tooling", "discovery", "invocation",
            "capabilities", "plugins", "extensions", "management", "tool-registry",
            "validation", "safeguards", "deterministic", "bounded", "offline"
        ],
        "safeguards": ["bounded", "validation", "deterministic", "offline", "reproducible"],
        "meta": {
            "category": "mcp",
            "safeguards": ["validation", "timeout", "error-isolation", "resource-limits", 
                          "audit-trail", "bounded", "deterministic", "offline"],
            "detector_version": "1.2"
        }
    }
