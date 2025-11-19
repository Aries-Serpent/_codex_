"""Detector for MCP security safeguards such as confirmation prompts or dry-run toggles."""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

KEYWORDS = ["confirm", "dry_run", "sanitize"]


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    evidence = []
    found = []
    for meta in file_index.get("files", []):
        path = meta.get("path", "")
        if not path.endswith(".py") and not path.endswith(".md"):
            continue
        try:
            text = Path(path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            text = ""
        for keyword in KEYWORDS:
            if keyword in text:
                evidence.append(path)
                found.append(keyword)
                break
    return {
        "id": "mcp-security-safeguards",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": KEYWORDS,
        "meta": {"category": "mcp"},
    }
