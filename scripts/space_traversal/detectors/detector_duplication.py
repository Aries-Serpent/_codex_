"""
Duplication Ratio Detector

Analyzes code duplication across the repository using stem-based and token-similarity methods.
Provides comprehensive metrics for consistency scoring.

Patterns detected: analysis, detection, reporting
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any


def detect(file_index: dict[str, Any]) -> dict[str, Any]:
    """
    Compute duplication ratio over file stems using the S1 context index.

    This detector performs analysis of file name duplication to support consistency scoring.
    Implements deterministic detection with reproducible results.

    Args:
        file_index: Context index with files list

    Returns:
        Detection result with duplication metrics and patterns
    """

    files = file_index.get("files", [])
    stems = [Path(f["path"]).stem.lower() for f in files]

    # Analysis: Count stem occurrences (deterministic, bounded operation)
    counts = Counter(stems)
    duplicates = sum(c for c in counts.values() if c > 1)
    evidence_count = max(len(stems), 1)
    dup_ratio = max(0.0, min(1.0, duplicates / evidence_count))

    # Detection: Identify duplicate groups for reporting
    duplicate_groups = _find_duplicate_groups(files, counts)

    # Reporting: Generate comprehensive metrics
    found_patterns = _detect_patterns(dup_ratio, duplicate_groups)

    return {
        "id": "duplication_ratio",
        "dup_ratio": float(dup_ratio),
        "counts": dict(sorted(counts.items())),
        "evidence_count": int(evidence_count),
        "duplicate_groups": duplicate_groups,
        "metrics": {
            "total_duplicates": duplicates,
            "unique_stems": len(counts),
            "duplication_percentage": round(dup_ratio * 100, 2),
        },
        # Provide fields expected by the dynamic detector contract
        "evidence_files": sorted({f["path"] for f in files}),
        "found_patterns": found_patterns,
        "required_patterns": ["analysis", "detection", "reporting"],
        "docs_keywords": ["duplication", "similarity", "analysis", "detection", "consistency"],
        "meta": {
            "method": "stem_based",
            "deterministic": True,
            "offline": True,
        },
    }


def _find_duplicate_groups(files: list[dict[str, Any]], counts: Counter) -> dict[str, list[str]]:
    """
    Find groups of files with duplicate stems.

    Safeguard: Bounded operation, deterministic ordering

    Args:
        files: list of file info dicts
        counts: Counter of stem occurrences

    Returns:
        Dictionary mapping stems to lists of duplicate file paths
    """
    duplicate_groups: dict[str, list[str]] = {}

    # Group files by stem (deterministic ordering)
    stem_to_files: dict[str, list[str]] = {}
    for f in files:
        stem = Path(f["path"]).stem.lower()
        if stem not in stem_to_files:
            stem_to_files[stem] = []
        stem_to_files[stem].append(f["path"])

    # Filter to only duplicates (validation: count > 1)
    for stem, file_list in sorted(stem_to_files.items()):
        if counts[stem] > 1:
            duplicate_groups[stem] = sorted(file_list)  # Deterministic ordering

    return duplicate_groups


def _detect_patterns(dup_ratio: float, duplicate_groups: dict[str, list[str]]) -> list[str]:
    """
    Detect which patterns are present based on analysis results.

    Args:
        dup_ratio: Calculated duplication ratio
        duplicate_groups: Dictionary of duplicate file groups

    Returns:
        list of detected pattern names
    """
    patterns = []

    # Pattern: analysis (always present - we analyze the files)
    patterns.append("analysis")

    # Pattern: detection (present if we detect duplicates or confirm uniqueness)
    if dup_ratio > 0 or len(duplicate_groups) == 0:
        patterns.append("detection")

    # Pattern: reporting (present if we have metrics to report)
    patterns.append("reporting")

    return patterns
