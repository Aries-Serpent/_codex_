"""
dup_similarity.py — Token-similarity duplication heuristic (scaffold, optional)

Intent:
- Provide an alternative duplication ratio estimation using token similarity
  across evidence file names (and optionally content, guarded).
- Deterministic, offline-only, lightweight by default (paths/stems only).

API:
- estimate(evidence_files: list[str], repo_root: Path) -> float
  Returns duplication ratio in [0,1] based on token overlap clustering.

Notes:
- Default implementation uses lowercased stem-token Jaccard overlap.
- This scaffold is intentionally conservative: it does NOT read file contents
  (to stay fast/offline) unless future configs opt-in.
- If evidence_files is empty or single-entry, returns 0.0 duplication.
- Inspired by simple Jaccard similarity patterns commonly seen in open-source
  analysis tools (e.g., overlap of word tokens).

Future hooks (v1.2.x):
- Optional content tokenization (bounded bytes, stable tokenizer)
- Minhash/LSH for larger sets (still offline)
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Set


def _stem_tokens(path: str) -> Set[str]:
    """
    Tokenize the file stem into simple, deterministic tokens.
    - Lowercase
    - Split on non-alphanumeric boundaries
    - Remove empty tokens
    """
    import re

    stem = Path(path).stem.lower()
    toks = re.split(r"[^a-z0-9]+", stem)
    return {t for t in toks if t}


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a and not b:
        return 0.0
    inter = a & b
    union = a | b
    if not union:
        return 0.0
    return len(inter) / len(union)


def estimate(evidence_files: List[str], repo_root: Path) -> float:
    """
    Estimate duplication ratio using pairwise token similarity among evidence files.

    Heuristic:
    - Compute tokens for each path's stem.
    - For each unique pair, compute Jaccard similarity.
    - Define a "similar" pair if similarity >= 0.8 (tunable, fixed here for determinism).
    - Duplication ratio = (# similar pairs) / (# all pairs), clamped to [0,1].

    This provides a smoother measure than exact-stem duplication while remaining offline.

    Args:
      evidence_files: repository-relative paths for capability evidence
      repo_root: Path to repo root (currently unused; reserved for future content opts)

    Returns:
      float in [0, 1] duplication ratio.
    """
    files = [p for p in evidence_files if p]
    n = len(files)
    if n <= 1:
        return 0.0

    token_sets = [_stem_tokens(p) for p in files]
    similar_pairs = 0
    total_pairs = 0
    for i in range(n):
        for j in range(i + 1, n):
            total_pairs += 1
            sim = _jaccard(token_sets[i], token_sets[j])
            if sim >= 0.8:
                similar_pairs += 1
    if total_pairs == 0:
        return 0.0
    ratio = similar_pairs / total_pairs
    return max(0.0, min(1.0, ratio))
