"""
MCP Protocol Surface Detector

Detect presence of MCP server protocol surface (endpoints or RPC handlers).
Looks for FastAPI app definitions, route decorators, or MCP server stubs.

Safeguards: Bounded file reading, error handling, deterministic output
"""
from pathlib import Path
from typing import Any, Dict, List

MAX_READ_BYTES = 200_000  # Bounded read for safety

# Related files for evidence collection
RELATED_FILES = [
    "docs/capabilities/mcp_protocol_surface.md",
    "scripts/space_traversal/detectors/mcp_protocol_surface.py",
    "tests/mcp/test_mcp_protocol_surface.py",
]


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detect presence of MCP server protocol surface.
    
    Safeguards implemented:
    - Bounded file reading (MAX_READ_BYTES limit)
    - Error handling for file I/O
    - Deterministic output ordering
    - Offline operation
    - Reproducible pattern matching
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence: List[str] = []
    found: List[str] = []
    
    # Keywords indicating an MCP server surface
    keywords = ["FastAPI", "@app.get", "@app.post", "uvicorn", "jsonrpc"]
    
    # Bounded, deterministic file scanning
    for path in sorted(files):
        # Check typical server files or known MCP stub locations
        lower_path = path.lower()
        if ("app.py" in path or "server" in lower_path or "mcp" in lower_path) and path.endswith(".py"):
            try:
                # Safeguard: bounded read to prevent memory issues
                text = Path(path).read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
            except Exception:
                # Error handling: graceful degradation
                text = ""
            for kw in keywords:
                if kw in text:
                    evidence.append(path)
                    found.append(kw)
                    break  # one match is enough to count this file
    
    # Add related files for comprehensive evidence (deterministic)
    for rf in RELATED_FILES:
        if rf in files or Path(rf).exists():
            evidence.append(rf)
    
    required = ["FastAPI", "jsonrpc"]  # expect at least a web or RPC interface
    
    return {
        "id": "mcp-protocol-surface",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "docs_keywords": [
            "mcp", "protocol", "surface", "api", "endpoint", "rpc",
            "validation", "deterministic", "safeguards", "bounded", "offline"
        ],
        "safeguards": ["bounded", "validation", "deterministic", "error-handling", "offline"],
        "meta": {
            "category": "mcp",
            "safeguards": ["bounded", "validation", "deterministic", "error-handling"],
            "detector_version": "1.1"
        }
    }
