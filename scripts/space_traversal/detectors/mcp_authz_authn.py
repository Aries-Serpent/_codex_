from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects authentication/authorization in MCP (API key checks, auth classes).
    Looks for 'verify_api_key', 'authenticate' functions, or auth-related classes.
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence = []
    found = []
    keywords = ["API-Key", "authenticate", "authorize"]
    for path in files:
        if path.endswith(".py"):
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            for kw in keywords:
                if kw in text:
                    evidence.append(path)
                    found.append(kw)
                    break
    required = ["authenticate", "authorize"]
    return {
        "id": "mcp-authz-authn",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"category": "mcp"}
    }
