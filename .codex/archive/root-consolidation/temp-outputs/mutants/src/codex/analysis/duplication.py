"""
Duplication Module

This module provides functionality for duplication.

Usage:
    from analysis.duplication import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import hashlib  # noqa: E402
from collections import defaultdict  # noqa: E402
from collections.abc import Iterable  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402

DEFAULT_EXTENSIONS = (".py", ".md", ".yaml", ".yml", ".json", ".txt")


@dataclass
class DuplicationReport:
    stats: dict[str, Any]
    duplicate_groups: list[dict[str, Any]]
    content_duplicates: list[dict[str, Any]]
    recommendations: list[str]


def _hash_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as e:
        logger.debug(f"OSError: {type(e).__name__}")
        logger.warning(f"OSError: {type(e).__name__}", exc_info=True)
        return ""


def _assess_severity(ratio: float, *, acceptable: float, warning: float, critical: float) -> str:
    if ratio <= acceptable:
        return "acceptable"
    if ratio <= warning:
        return "warning"
    if ratio <= critical:
        return "high"
    return "critical"


def analyze_duplication(
    root_path: Path | str,
    *,
    extensions: Iterable[str] | None = None,
    acceptable_ratio: float = 0.10,
    warning_ratio: float = 0.20,
    critical_ratio: float = 0.30,
) -> DuplicationReport:
    base = Path(root_path)
    chosen_exts = tuple(extensions) if extensions is not None else DEFAULT_EXTENSIONS

    files: list[Path] = []
    for ext in chosen_exts:
        files.extend(base.rglob(f"*{ext}"))

    stem_groups: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        if path.is_file():
            stem_groups[path.stem.lower()].append(path)

    duplicate_groups = {stem: paths for stem, paths in stem_groups.items() if len(paths) > 1}

    content_hashes: dict[str, list[Path]] = defaultdict(list)
    for path in files:
        if path.is_file():
            digest = _hash_file(path)
            content_hashes[digest].append(path)

    total_files = len(files)
    duplicate_count = sum(max(len(paths) - 1, 0) for paths in stem_groups.values())
    ratio = duplicate_count / max(total_files, 1)
    severity = _assess_severity(
        ratio,
        acceptable=acceptable_ratio,
        warning=warning_ratio,
        critical=critical_ratio,
    )

    def _format_paths(paths: list[Path]) -> list[str]:
        return [str(p.relative_to(base)) for p in paths]

    def _format_duplicate_groups() -> list[dict[str, Any]]:
        formatted: list[dict[str, Any]] = []
        for stem, paths in sorted(duplicate_groups.items(), key=lambda item: -len(item[1]))[:20]:
            formatted.append(
                {
                    "stem": stem,
                    "count": len(paths),
                    "paths": _format_paths(paths),
                }
            )
        return formatted

    def _format_content_duplicates() -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        for digest, paths in content_hashes.items():
            if len(paths) > 1:
                entries.append(
                    {
                        "hash": digest[:16],
                        "count": len(paths),
                        "paths": _format_paths(paths),
                    }
                )
        return sorted(entries, key=lambda item: -item["count"])[:10]

    recommendations: list[str] = []
    if ratio < acceptable_ratio:
        recommendations.append(f"Duplication ratio {ratio:.2%} is within acceptable limits.")
    elif ratio < warning_ratio:
        recommendations.append(
            f"Duplication ratio {ratio:.2%} is elevated; review duplicate groups."
        )
    else:
        recommendations.append(f"Duplication ratio {ratio:.2%} is high; prioritise consolidation.")

    content_dup_groups = len([1 for _, paths in content_hashes.items() if len(paths) > 1])
    if duplicate_groups:
        recommendations.append(f"Found {len(duplicate_groups)} filename duplicate groups.")
    if content_dup_groups:
        recommendations.append(f"Found {content_dup_groups} exact content duplicate groups.")

    stats = {
        "total_files": total_files,
        "duplicate_count": duplicate_count,
        "duplication_ratio": ratio,
        "duplicate_groups_count": len(duplicate_groups),
        "content_duplicate_groups": content_dup_groups,
        "severity": severity,
    }

    return DuplicationReport(
        stats=stats,
        duplicate_groups=_format_duplicate_groups(),
        content_duplicates=_format_content_duplicates(),
        recommendations=recommendations,
    )


__all__ = ["DEFAULT_EXTENSIONS", "DuplicationReport", "analyze_duplication"]
