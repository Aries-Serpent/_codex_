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


MAX_READ_BYTES = 200_000
REPO_ROOT = Path(__file__).resolve().parents[3]


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ_BYTES]
    except Exception:
        return ""


def detect(file_index: Dict[str, Any]) -> Dict[str, Any]:
    """Scan files for safeguard keywords using the S1 context index."""

    files = file_index.get("files", [])
    evidence: Dict[str, int] = {}
    text_cache: Dict[str, str] = {}
    allowed_suffixes = {".py", ".md", ".sh", ".txt", ".yml", ".yaml"}
    for entry in files:
        rel_path = entry.get("path")
        if not rel_path:
            continue
        if Path(rel_path).suffix.lower() not in allowed_suffixes:
            continue
        text = _read_text(REPO_ROOT / rel_path)
        hits = sum(1 for w in SAFEGUARD_KEYWORDS if w in text)
        if hits:
            evidence[rel_path] = hits
            text_cache[rel_path] = text

    total_hits = int(sum(evidence.values()))
    return {
        "id": "safeguards_keywords",
        "evidence": dict(sorted(evidence.items())),
        "total_hits": total_hits,
        "unique_files": int(len(evidence)),
        "evidence_files": sorted(evidence.keys()),
        "found_patterns": sorted(
            {w for w in SAFEGUARD_KEYWORDS if any(w in text_cache[p] for p in evidence)}
        ),
        "required_patterns": sorted(SAFEGUARD_KEYWORDS),
    }
