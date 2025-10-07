from __future__ import annotations
from pathlib import Path

REQUIRED = ["UnifiedTrainingConfig", "run_unified_training"]


def detect(file_index: dict) -> dict:
    files = file_index.get("files", [])
    paths = [f["path"] for f in files]
    evidence = [p for p in paths if p.endswith("unified_training.py")]
    found_patterns = []
    if evidence:
        # crude scan for required patterns
        for ev in evidence:
            try:
                text = Path(ev).read_text(encoding="utf-8", errors="ignore")
            except Exception:
                text = ""
            for pat in REQUIRED:
                if pat in text:
                    found_patterns.append(pat)
    return {
        "id": "unified-training",
        "evidence_files": evidence,
        "found_patterns": sorted(set(found_patterns)),
        "required_patterns": REQUIRED,
        "meta": {"category": "training"},
    }
