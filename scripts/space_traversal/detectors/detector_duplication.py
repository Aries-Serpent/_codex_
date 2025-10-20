from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any, Dict


def detect(repo_root: Path) -> Dict[str, Any]:
    """
    Compute a duplication ratio over file stems to approximate naming duplication.

    dup_ratio = (sum_over_stems(max(count-1, 0))) / evidence_count, clamped to [0, 1]

    Output schema:
    {
      "id": "duplication_ratio",
      "dup_ratio": <float>,
      "counts": { "stem": count, ... },
      "evidence_count": <int>
    }
    """
    repo_root = Path(repo_root).resolve()
    stems = []
    for p in repo_root.rglob('*'):
        if p.is_file():
            stems.append(p.stem.lower())

    counts = Counter(stems)
    duplicates = sum(max(c - 1, 0) for c in counts.values())
    evidence_count = max(len(stems), 1)
    dup_ratio = max(0.0, min(1.0, duplicates / evidence_count))

    return {
        "id": "duplication_ratio",
        "dup_ratio": float(dup_ratio),
        "counts": dict(sorted(counts.items())),
        "evidence_count": int(evidence_count),
    }

