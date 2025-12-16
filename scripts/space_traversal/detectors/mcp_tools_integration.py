from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamic detector for MCP & tools integration capability.

    Detects MCP server/client integration, tool registration,
    and plugin system implementations.

    Contract:
      - Accepts the context_index-like dict with 'files' list of {path, ...}
      - Returns the capability dict with id, evidence_files, found_patterns, required_patterns, meta

    Safeguards: Deterministic detection, bounded operations.
    """
    files = [f.get("path") for f in file_index.get("files", []) if f.get("path")]
    evidence = [
        p
        for p in files
        if p.startswith("mcp/")
        or p.startswith("tools/")
        or p.startswith("src/mcp/")
        or p.startswith("src/services/mcp/")
        or "mcp" in p.lower()
        or "tool" in p.lower()
    ]
    found = []
    required = ["mcp", "tool", "registry", "integration"]

    # Pattern detection
    for p in evidence:
        stem = Path(p).stem.lower()
        path_lower = p.lower()

        if "mcp" in stem or "mcp" in path_lower:
            found.append("mcp")
        if "tool" in stem or "tool" in path_lower:
            found.append("tool")
        if "registry" in stem or "registry" in path_lower:
            found.append("registry")
        if "integration" in stem or "server" in stem or "client" in stem:
            found.append("integration")

    # Calculate functionality score
    functionality_score = len(set(found) & set(required)) / len(required) if required else 0.0

    return {
        "id": "mcp-tools-integration",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "docs_keywords": [
            "mcp",
            "tools",
            "integration",
            "registry",
            "plugins",
            "server",
            "client",
            "api",
        ],
        "safeguards": ["validation", "deterministic", "bounded"],
        "functionality_impl": functionality_score,
        "meta": {"layer": "integration", "deterministic": True, "offline": True, "bounded": True},
    }
