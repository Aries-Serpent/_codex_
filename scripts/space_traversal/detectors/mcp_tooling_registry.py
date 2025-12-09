from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects MCP tool registry usage. Looks for mcp.json or registry classes.
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence = []
    found = []
    for path in files:
        lower = path.lower()
        if "mcp/" in lower or "tool" in lower:
            # Identify evidence of registry:
            # - The mcp.json config file
            # - Any 'registry.py' in mcp module
            if path.endswith("mcp.json") or "registry" in lower:
                evidence.append(path)
            if "registry" in lower:
                found.append("registry")
            if path.endswith("mcp.json"):
                found.append("mcp.json")
    required = ["registry", "mcp.json"]
    return {
        "id": "mcp-tooling-registry",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "docs_keywords": [
            "mcp", "tools", "registry", "tooling", "discovery", "invocation",
            "capabilities", "plugins", "extensions", "management", "tool-registry",
            "validation", "safeguards"
        ],
        "meta": {
            "category": "mcp",
            "safeguards": ["validation", "timeout", "error-isolation", "resource-limits", "audit-trail"],
            "detector_version": "1.1"
        }
    }
