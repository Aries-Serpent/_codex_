from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a duplication ratio over file stems using the S1 context index."""

    files = file_index.get("files", [])
    stems = [Path(f["path"]).stem.lower() for f in files]

    counts = Counter(stems)
    duplicates = sum(max(c - 1, 0) for c in counts.values())
    evidence_count = max(len(stems), 1)
    dup_ratio = max(0.0, min(1.0, duplicates / evidence_count))

    return {
        "id": "duplication_ratio",
        "dup_ratio": float(dup_ratio),
        "counts": dict(sorted(counts.items())),
        "evidence_count": int(evidence_count),
        # Provide fields expected by the dynamic detector contract.
        "evidence_files": sorted({f["path"] for f in files}),
        "found_patterns": ["unique_stems"] if dup_ratio == 0 else [],
        "required_patterns": ["unique_stems"],
    }
