"""Detector for MCP security safeguards such as confirmation prompts or dry-run toggles."""

from __future__ import annotations
import logging
logger = logging.getLogger(__name__)

from pathlib import Path
from typing import Any

KEYWORDS = ["confirm", "dry_run", "sanitize", "validation", "bounds", "rollback"]


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
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
        "docs_keywords": [
            "mcp",
            "security",
            "safeguards",
            "validation",
            "sanitization",
            "confirm",
            "dry-run",
            "defensive",
            "protection",
            "safety",
            "bounds-checking",
            "error-handling",
            "rollback",
            "audit",
        ],
        "meta": {
            "category": "mcp",
            "safeguards": [
                "confirmation",
                "dry-run",
                "sanitization",
                "validation",
                "bounds-checking",
                "rollback",
            ],
            "detector_version": "1.2",
        },
    }
