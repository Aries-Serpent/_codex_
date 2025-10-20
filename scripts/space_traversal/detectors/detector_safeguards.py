from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

SAFEGUARD_KEYWORDS = {
    "sha256",
    "checksum",
    "rng",
    "seed",
    "offline",
    "WANDB_MODE",
}


def detect(repo_root: Path) -> Dict[str, Any]:
    """
    Scan files for safeguard keywords. Returns evidence that can be consumed by S3/S4.

    Output schema:
    {
      "id": "safeguards_keywords",
      "evidence": { "<relpath>": <match_count>, ... },
      "total_hits": <int>,
      "unique_files": <int>
    }
    """
    repo_root = Path(repo_root).resolve()
    evidence: Dict[str, int] = {}
    for p in repo_root.rglob('*'):
        if not p.is_file():
            continue
        if p.suffix.lower() not in {'.py', '.md', '.sh', '.txt', '.yml', '.yaml'}:
            continue
        try:
            text = p.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            continue
        hits = sum(1 for w in SAFEGUARD_KEYWORDS if w in text)
        if hits:
            evidence[str(p.relative_to(repo_root))] = hits

    return {
        "id": "safeguards_keywords",
        "evidence": dict(sorted(evidence.items())),
        "total_hits": int(sum(evidence.values())),
        "unique_files": int(len(evidence)),
    }

