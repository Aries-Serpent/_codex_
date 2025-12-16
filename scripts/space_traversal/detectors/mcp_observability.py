from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Detects observability features (logging, metrics, tracing) for MCP.
    Looks for logging setup, 'X-Request-Id', or Prometheus metrics usage.
    """
    files = [f.get("path", "") for f in file_index.get("files", [])]
    evidence = []
    found = []
    keywords = ["init_json_logging", "X-Request-Id", "metrics", "prometheus"]
    for path in files:
        if path.endswith(".py") or path.endswith(".md"):
            try:
                text = Path(path).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            for kw in keywords:
                if kw in text:
                    evidence.append(path)
                    found.append(kw)
                    break
    required = ["X-Request-Id", "logging"]
    return {
        "id": "mcp-observability",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": required,
        "meta": {"category": "mcp"},
    }
