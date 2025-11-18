from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects structured error handling for MCP (MCPError classes, error codes).
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
            if "MCPError" in text or "jsonrpc" in text and '"error"' in text:
                evidence.append(path)
                if "MCPError" in text:
                    found.append("MCPError")
                # If JSON-RPC error patterns (like '"error":' in a JSON context)
                if '"error"' in text:
                    found.append("error payload")
    required = ["MCPError"]
    return {
        "id": "mcp-error-handling",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"category": "mcp"}
    }
