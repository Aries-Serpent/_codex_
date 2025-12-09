"""
Token-similarity duplication heuristic for content-aware file duplication detection.

Intent:
- Provide an alternative duplication ratio estimation using token similarity
  across evidence file names (and optionally content, guarded).
- Deterministic, offline-only, lightweight by default (paths/stems only).

API:
- estimate(evidence_files: list[str], repo_root: Path) -> float
  Returns duplication ratio in [0,1] based on token overlap clustering.
- duplication_ratio_token_similarity(evidence_files, file_cache, threshold, max_pairwise, max_tokens_per_file)
  Enhanced API with configurable parameters for content-based token similarity.

Notes:
- Default implementation uses lowercased stem-token Jaccard overlap.
- This scaffold is intentionally conservative: it does NOT read file contents
  (to stay fast/offline) unless future configs opt-in.
- If evidence_files is empty or single-entry, returns 0.0 duplication.
- Inspired by simple Jaccard similarity patterns commonly seen in open-source
  analysis tools (e.g., overlap of word tokens).
- Deterministic tokenization ensures stable, reproducible results.
- max_pairwise caps pairwise comparisons using deterministic sampling.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Set


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


def _tokenize_content(content: str, max_tokens: int = 1000) -> Set[str]:
    """
    Tokenize file content into deterministic tokens.

    Args:
        content: File content to tokenize
        max_tokens: Maximum number of tokens to extract (for performance)

    Returns:
        Set of lowercase alphanumeric tokens
    """
    # Split on non-alphanumeric, lowercase, filter empties and short tokens
    tokens = re.split(r"[^a-z0-9]+", content.lower())
    tokens = [t for t in tokens if len(t) >= 2]
    # Take first max_tokens deterministically
    tokens = tokens[:max_tokens]
    return set(tokens)


def _deterministic_sample_pairs(n: int, max_pairs: int) -> List[tuple]:
    """
    Deterministically sample pairs for comparison when total pairs > max_pairs.

    Uses sorted indices and simple hash-based selection for reproducibility.

    Args:
        n: Number of items
        max_pairs: Maximum number of pairs to sample

    Returns:
        List of (i, j) tuples representing pairs to compare
    """
    all_pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    total_pairs = len(all_pairs)

    if total_pairs <= max_pairs:
        return all_pairs

    # Deterministic sampling using simple hash-based selection
    # Sort pairs to ensure deterministic ordering
    all_pairs.sort()

    # Use simple hash with fixed seed for deterministic selection
    # This is faster than SHA256 and sufficient for sampling
    selected = []
    for pair in all_pairs:
        # Combine pair indices into a hashable key
        pair_key = f"{pair[0]}:{pair[1]}"
        # Use Python's built-in hash with modulo for selection
        # Note: Python's hash is not deterministic across processes/versions,
        # so we use a simple arithmetic approach instead
        pair_value = (pair[0] * 1000 + pair[1]) % total_pairs
        if pair_value < max_pairs:
            selected.append(pair)
            if len(selected) >= max_pairs:
                break

    # If we didn't get enough, take first max_pairs deterministically
    if len(selected) < max_pairs:
        selected = all_pairs[:max_pairs]

    return selected


def duplication_ratio_token_similarity(
    evidence_files: List[str],
    file_cache: Dict[str, str],
    threshold: float = 0.7,
    max_pairwise: int = 1000,
    max_tokens_per_file: int = 1000,
) -> float:
    """
    Compute duplication ratio using token-based Jaccard similarity with content analysis.

    This is the enhanced API requested in the roadmap. It:
    - Uses deterministic tokenization of file content
    - Performs pairwise Jaccard similarity comparisons
    - Caps comparisons to max_pairwise using deterministic sampling
    - Returns duplication ratio in [0, 1]

    Args:
        evidence_files: List of file paths to compare
        file_cache: Dictionary mapping file paths to their content
        threshold: Jaccard similarity threshold to consider files similar (default 0.7)
        max_pairwise: Maximum number of pairwise comparisons (default 1000)
        max_tokens_per_file: Maximum tokens to extract per file (default 1000)

    Returns:
        float in [0, 1] representing duplication ratio
    """
    files = [p for p in evidence_files if p]
    n = len(files)

    if n <= 1:
        return 0.0

    # Build token sets for each file
    token_sets = []
    for file_path in files:
        content = file_cache.get(file_path, "")
        # Combine path tokens and content tokens for richer comparison
        path_tokens = _stem_tokens(file_path)
        content_tokens = _tokenize_content(content, max_tokens_per_file)
        # Union of both sets
        combined_tokens = path_tokens | content_tokens
        token_sets.append(combined_tokens)

    # Determine pairs to compare
    total_possible_pairs = (n * (n - 1)) // 2
    pairs_to_compare = _deterministic_sample_pairs(n, min(max_pairwise, total_possible_pairs))

    # Count similar pairs
    similar_pairs = 0
    for i, j in pairs_to_compare:
        sim = _jaccard(token_sets[i], token_sets[j])
        if sim >= threshold:
            similar_pairs += 1

    if len(pairs_to_compare) == 0:
        return 0.0

    ratio = similar_pairs / len(pairs_to_compare)
    return max(0.0, min(1.0, ratio))


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
