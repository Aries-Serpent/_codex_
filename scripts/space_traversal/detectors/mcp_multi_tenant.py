from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects multi-tenant support in MCP (e.g., tenant identifiers or isolation logic).
    Likely not present, but searches for 'tenant' keyword.
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence = []
    found = []
    for path in files:
        lower = path.lower()
        if "tenant" in lower or "multi_tenant" in lower or "multitenant" in lower:
            evidence.append(path)
            found.append("tenant")
    # Expect at least some notion of tenant context to consider this implemented
    required = ["tenant"]
    return {
        "id": "mcp-multi-tenant",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"category": "mcp"}
    }
