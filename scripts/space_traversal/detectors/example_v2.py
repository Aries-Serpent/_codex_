"""Example v2 detector demonstrating _evidence_v2 payloads."""
from __future__ import annotations

from typing import Any, Dict, List


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    files: List[Dict[str, Any]] = file_index.get("files", [])
    evidence: List[str] = []
    meta_evidence: List[Dict[str, Any]] = []

    for meta in files:
        path = meta.get("path", "")
        if path.endswith(".md") and "status" in path:
            evidence.append(path)
            meta_evidence.append({"path": path, "signal": "status-doc"})
        elif path.endswith(".py") and "detector" in path:
            evidence.append(path)
            meta_evidence.append({"path": path, "signal": "detector-code"})

    if not evidence:
        return {
            "id": "example-v2",
            "evidence_files": [],
            "found_patterns": [],
            "required_patterns": ["status", "detector"],
            "meta": {"_evidence_v2": []},
        }

    return {
        "id": "example-v2",
        "evidence_files": sorted(set(evidence)),
        "found_patterns": ["status", "detector"],
        "required_patterns": ["status", "detector"],
        "meta": {"_evidence_v2": meta_evidence, "detector_version": 2},
    }
