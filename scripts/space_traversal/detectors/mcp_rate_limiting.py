from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects rate limiting in MCP server. Looks for RateLimiter classes or usage.
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
            if "RateLimiter" in text or "rate_limit" in text:
                evidence.append(path)
                if "RateLimiter" in text:
                    found.append("RateLimiter")
                if "rate_limit" in text:
                    found.append("rate_limit")
    required = ["RateLimiter"]
    return {
        "id": "mcp-rate-limiting",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"category": "mcp"}
    }
