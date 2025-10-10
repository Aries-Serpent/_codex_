"""
Sample dynamic detector: inference-serving
Non-invasive: inspects file paths only (offline-friendly).
"""
from __future__ import annotations

from typing import Any, Dict, List

ID = "inference-serving"
REQUIRED = ["server", "fastapi"]


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    files: List[Dict[str, Any]] = file_index.get("files", [])
    py_paths = [f["path"] for f in files if f.get("path", "").endswith(".py")]
    # Lightweight signal: filenames or directories containing serving hints
    evidence = [p for p in py_paths if any(tok in p.lower() for tok in ("serve", "server", "api"))]
    found = []
    for p in evidence:
        name = p.lower()
        if "fastapi" in name:
            found.append("fastapi")
        if "server" in name or "serve" in name:
            found.append("server")
    return {
        "id": ID,
        "evidence_files": sorted(set(evidence)),
        "found_patterns": sorted(set(found)),
        "required_patterns": REQUIRED,
        "meta": {"layer": "serving"},
    }
