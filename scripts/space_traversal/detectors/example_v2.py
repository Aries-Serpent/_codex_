"""Example v2 detector demonstrating _evidence_v2 payloads."""

from __future__ import annotations
from typing import Any, Dict, List

__all__ = ["detect_v2"]

def detect_v2(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """
    Example detector v2 that returns structured evidence entries.
    Combines evidence from markdown with 'status' and python files with 'detector',
    as well as '.py' files referencing 'serve' or 'checkpoint' (demonstrating advanced v2 features).
    """
    files = file_index.get("files", [])
    evidence_v2: List[Dict[str, Any]] = []
    found_patterns = set()
    required_patterns = ["status", "detector", "serve"]

    for meta in files:
        path = meta.get("path", "")
        if path.endswith(".md") and "status" in path:
            evidence_v2.append({
                "path": path,
                "signal": "status-doc",
                "confidence": 0.85
            })
            found_patterns.add("status")
        elif path.endswith(".py") and "detector" in path:
            evidence_v2.append({
                "path": path,
                "signal": "detector-code",
                "confidence": 0.85
            })
            found_patterns.add("detector")
        elif path.endswith(".py") and ("serve" in path.lower() or "checkpoint" in path.lower()):
            # Advanced v2 example: evidence with ranges and extra info
            range_block = {"start_line": 1, "end_line": 40}
            evidence_v2.append({
                "path": path,
                "signal": "serve-or-checkpoint",
                "confidence": 0.90,
                "ranges": [range_block],
                "excerpt": None
            })
            found_patterns.update(["serve", "checkpoint"])

    if not evidence_v2:
        # No evidence found, fill with required structure
        return {
            "id": "example-evidence-v2",
            "evidence": [],
            "found_patterns": [],
            "required_patterns": required_patterns,
            "meta": {"_evidence_v2": [], "detector_version": "v2", "source": "example_v2"},
        }

    return {
        "id": "example-evidence-v2",
        "evidence": evidence_v2,
        "found_patterns": sorted(found_patterns),
        "required_patterns": required_patterns,
        "meta": {"_evidence_v2": evidence_v2, "detector_version": "v2", "source": "example_v2"},
    }
