from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects MCP versioning and compatibility support.
    Looks for version constants or negotiation logic.
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence = []
    found = []
    for path in files:
        if path.endswith(".py"):
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            if "MCP_VERSIONS" in text or "negotiate_version" in text:
                evidence.append(path)
                if "MCP_VERSIONS" in text:
                    found.append("MCP_VERSIONS")
                if "negotiate_version" in text:
                    found.append("negotiate_version")
    required = ["MCP_VERSIONS"]
    return {
        "id": "mcp-versioning-compat",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"category": "mcp"}
    }
