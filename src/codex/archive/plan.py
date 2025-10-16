from __future__ import annotations

import re
import time
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from fnmatch import fnmatch
from pathlib import Path
from re import Pattern
from typing import Any, Final

from .detect import FileMeta, stat_file
from .score import ScoreInput, archive_score

DEPRECATION_PAT: Final[Pattern[str]] = re.compile(
    r"\b(DEPRECATED|LEGACY|PRUNE_ME)\b", re.IGNORECASE
)


@dataclass
class PlanEntry:
    path: str
    reason: str
    age_days: int
    ref_count: int
    coverage: float
    score: float
    commit_sha: str
    mime: str
    lang: str
    tags: list[str]
    size_bytes: int
    sloc: int


def _has_deprecation_tag(p: Path) -> bool:
    try:
        txt = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return False
    return bool(DEPRECATION_PAT.search(txt))


def _in_excludes(p: Path, excludes: Iterable[str]) -> bool:
    s = p.as_posix()
    return any(fnmatch(s, pat) for pat in excludes)


def build_plan(
    root: Path,
    *,
    analyze_sha: str,
    excludes: Iterable[str],
    age_days_threshold: int,
    default_reason: str = "dead",
) -> dict[str, Any]:
    now = time.time()
    entries: list[PlanEntry] = []
    for p in root.rglob("*"):
        if p.is_dir():
            continue
        if _in_excludes(p, excludes):
            continue
        fm: FileMeta = stat_file(p)
        age_days = int((now - fm.mtime_epoch) / 86400)
        dep = _has_deprecation_tag(p)
        inp = ScoreInput(
            age_days=age_days,
            ref_count=0,
            coverage=0.0,
            has_deprecation_tag=dep,
        )
        score = archive_score(inp, tau=age_days_threshold)
        if score >= 0.7:
            entries.append(
                PlanEntry(
                    path=fm.path,
                    reason=default_reason,
                    age_days=age_days,
                    ref_count=0,
                    coverage=0.0,
                    score=score,
                    commit_sha=analyze_sha,
                    mime=fm.mime,
                    lang=fm.lang,
                    tags=["auto-plan"],
                    size_bytes=fm.size_bytes,
                    sloc=fm.sloc,
                )
            )
    serial = [asdict(e) for e in sorted(entries, key=lambda e: (-e.score, e.path))]
    return {"generated_at": int(now), "analyze_sha": analyze_sha, "entries": serial}
