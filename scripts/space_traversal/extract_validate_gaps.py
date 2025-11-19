from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from scripts.space_traversal import stable_manifest

REQUIRED_FIELDS = ("id", "title", "description")


def extract_gaps(decoded_report: dict[str, Any]) -> dict[str, Any]:
    gaps = decoded_report.get("gaps", [])
    normalized = []
    for gap in gaps:
        if not isinstance(gap, dict):
            continue
        if not all(field in gap for field in REQUIRED_FIELDS):
            continue
        normalized.append(
            {
                "id": str(gap["id"]),
                "title": str(gap["title"]),
                "description": str(gap["description"]),
                "severity": str(gap.get("severity", "")),
            }
        )
    return {"gaps": normalized, "count": len(normalized)}


def write_gaps(gaps: dict[str, Any], destination: Path, stable_output: bool = False) -> Path:
    if stable_output:
        return stable_manifest.write_stable_json(gaps, destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(gaps, indent=2), encoding="utf-8")
    return destination
