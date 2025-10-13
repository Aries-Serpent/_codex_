"""Consolidation planning for near-duplicate files."""

from __future__ import annotations

import time
from dataclasses import dataclass
from fnmatch import fnmatch
from pathlib import Path
from typing import Dict, Iterable, List

from .detect import FileMeta, stat_file
from .similarity import Similarity, compute_similarity


def _serialise_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _in_excludes(path: Path, patterns: Iterable[str]) -> bool:
    serial = path.as_posix()
    return any(fnmatch(serial, pattern) for pattern in patterns)


def _freshness(now: float, mtime_epoch: float) -> float:
    age_days = max(0.0, (now - mtime_epoch) / 86400.0)
    if age_days <= 7:
        return 1.0
    if age_days <= 30:
        return 0.8
    if age_days <= 180:
        return 0.5
    if age_days <= 365:
        return 0.3
    return 0.1


def _path_fitness(path: str) -> float:
    normalised = path.replace("\\", "/")
    score = 0.0
    if normalised.startswith("src/codex/"):
        score += 0.5
    if "/legacy/" in normalised or normalised.startswith("legacy/"):
        score -= 0.3
    if normalised.endswith("_v2.py"):
        score += 0.1
    return max(0.0, min(1.0, score))


def _complexity_penalty(size_bytes: int, sloc: int) -> float:
    return min(0.4, (sloc / 2000.0) + (size_bytes / (512 * 1024)))


def _usage_heuristic(path: Path) -> float:
    serial = path.as_posix()
    if "legacy" in serial:
        return 0.1
    if serial.startswith("src/codex/"):
        return 0.7
    return 0.4


def _testcov_heuristic(path: Path) -> float:
    guess = Path("tests") / f"{path.stem}.py"
    return 0.6 if guess.exists() else 0.0


def canon_score(meta: FileMeta, *, freshness: float, usage: float, testcov: float) -> float:
    a, b, c, d, eps = 0.25, 0.25, 0.20, 0.20, 0.10
    base = (
        a * max(0.0, min(1.0, freshness))
        + b * max(0.0, min(1.0, usage))
        + c * max(0.0, min(1.0, testcov))
        + d * _path_fitness(meta.path)
    )
    penalty = eps * _complexity_penalty(meta.size_bytes, meta.sloc)
    return round(max(0.0, min(1.0, base - penalty)), 4)


@dataclass(slots=True)
class ConsolidationCandidate:
    path: str
    score: float
    freshness: float
    usage: float
    testcov: float
    size_bytes: int
    sloc: int
    mtime_epoch: float
    mime: str
    lang: str


def _candidate_from_meta(meta: FileMeta, *, now: float) -> ConsolidationCandidate:
    freshness = _freshness(now, meta.mtime_epoch)
    usage = _usage_heuristic(Path(meta.path))
    testcov = _testcov_heuristic(Path(meta.path))
    return ConsolidationCandidate(
        path=meta.path,
        score=canon_score(meta, freshness=freshness, usage=usage, testcov=testcov),
        freshness=freshness,
        usage=usage,
        testcov=testcov,
        size_bytes=meta.size_bytes,
        sloc=meta.sloc,
        mtime_epoch=meta.mtime_epoch,
        mime=meta.mime,
        lang=meta.lang,
    )


def _is_near_duplicate(path_a: Path, path_b: Path, *, sim: Similarity, jaccard_min: float, hd_max: int) -> bool:
    if path_a.suffix == ".py" and path_b.suffix == ".py" and sim.py_ast_equal:
        return True
    if sim.jaccard >= jaccard_min:
        return True
    if path_a.suffix in {".md", ".txt"} and path_b.suffix in {".md", ".txt"}:
        return sim.doc_hd <= hd_max
    return False


def build_consolidation_plan(
    root: Path,
    *,
    excludes: Iterable[str],
    jaccard_min: float = 0.92,
    hd_max: int = 3,
) -> dict[str, object]:
    now = time.time()
    files = sorted(
        [p for p in root.rglob("*") if p.is_file() and not _in_excludes(p, excludes)],
        key=lambda p: p.as_posix(),
    )
    metadata: Dict[str, FileMeta] = {}
    path_lookup: Dict[str, Path] = {}
    for p in files:
        serial = _serialise_path(p, root)
        meta = stat_file(p)
        meta.path = serial
        metadata[serial] = meta
        path_lookup[serial] = p
    visited: set[str] = set()
    clusters: List[dict[str, object]] = []

    for idx, path in enumerate(files):
        serial = _serialise_path(path, root)
        if serial in visited:
            continue
        group = [serial]
        for other in files[idx + 1 :]:
            other_serial = _serialise_path(other, root)
            if other_serial in visited:
                continue
            sim = compute_similarity(path, other)
            if _is_near_duplicate(path, other, sim=sim, jaccard_min=jaccard_min, hd_max=hd_max):
                group.append(other_serial)
                visited.add(other_serial)
        if len(group) == 1:
            visited.add(serial)
            continue
        candidates = [_candidate_from_meta(metadata[g], now=now) for g in group]
        candidates.sort(key=lambda c: (-c.score, c.path))
        canonical = candidates[0]
        duplicates: List[dict[str, object]] = []
        canonical_path = path_lookup[canonical.path]
        for dup in candidates[1:]:
            dup_path = path_lookup[dup.path]
            sim = compute_similarity(canonical_path, dup_path)
            duplicates.append(
                {
                    "path": dup.path,
                    "similarity": {
                        "jaccard": sim.jaccard,
                        "doc_hd": float(sim.doc_hd),
                        "py_ast_equal": 1.0 if sim.py_ast_equal else 0.0,
                    },
                }
            )
            visited.add(dup.path)
        clusters.append(
            {
                "canonical": {
                    "path": canonical.path,
                    "score": canonical.score,
                    "freshness": canonical.freshness,
                    "usage": canonical.usage,
                    "testcov": canonical.testcov,
                    "size_bytes": canonical.size_bytes,
                    "sloc": canonical.sloc,
                    "mtime_epoch": canonical.mtime_epoch,
                    "mime": canonical.mime,
                    "lang": canonical.lang,
                },
                "duplicates": duplicates,
            }
        )
        visited.add(canonical.path)

    return {"generated_at": int(now), "clusters": clusters}
