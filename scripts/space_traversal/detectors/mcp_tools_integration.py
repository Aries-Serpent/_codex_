from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dynamic detector for MCP & tools integration capability.

    Contract:
      - Accepts the context_index-like dict with 'files' list of {path, ...}
      - Returns the capability dict with id, evidence_files, found_patterns, required_patterns, meta
    """
    files = [f.get("path") for f in file_index.get("files", []) if f.get("path")]
    evidence = [
        p
        for p in files
        if p.startswith("mcp/")
        or p.startswith("tools/")
        or "mcp" in p.lower()
        or "tool" in p.lower()
    ]
    found = []
    required = ["mcp", "tool"]
    for p in evidence:
        stem = Path(p).stem.lower()
        if "mcp" in stem:
            found.append("mcp")
        if "tool" in stem:
            found.append("tool")
    return {
        "id": "mcp-tools-integration",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"layer": "integration"},
    }
