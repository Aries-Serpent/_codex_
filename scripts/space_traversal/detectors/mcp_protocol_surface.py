from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect presence of MCP server protocol surface (endpoints or RPC handlers).
    Looks for FastAPI app definitions, route decorators, or MCP server stubs.
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence = []
    found = []
    # Keywords indicating an MCP server surface
    keywords = ["FastAPI", "@app.get", "@app.post", "uvicorn", "jsonrpc"]
    for path in files:
        # Check typical server files or known MCP stub locations
        lower_path = path.lower()
        if ("app.py" in path or "server" in lower_path or "mcp" in lower_path) and path.endswith(".py"):
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            for kw in keywords:
                if kw in text:
                    evidence.append(path)
                    found.append(kw)
                    break  # one match is enough to count this file
    required = ["FastAPI", "jsonrpc"]  # expect at least a web or RPC interface
    return {
        "id": "mcp-protocol-surface",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"category": "mcp"}
    }
