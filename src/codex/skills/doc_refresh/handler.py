"""Handler for the doc.refresh.agent built-in skill.

Plans and optionally applies AAIS-scored doc refresh across target paths.
"""

from __future__ import annotations

import hashlib
import logging
from pathlib import Path
from typing import Any

from codex.skills.aais import AAISScorer

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).parents[4]
_AAIS_PRUNE_THRESHOLD = 0.30  # docs scoring below this are candidates for pruning
_AAIS_REFRESH_THRESHOLD = 0.60  # docs scoring below this need refresh


def plan_and_apply(payload: dict[str, Any]) -> dict[str, Any]:
    """Score, plan, and optionally apply doc refresh.

    Parameters
    ----------
    payload : dict
        Expected keys:
        - ``paths`` (list[str], required): directory or file paths to scan.
        - ``style`` (str, optional): scoring style; currently only ``"aais"``.
        - ``prune_stale`` (bool, optional): include prune ops in plan.
        - ``actions`` (list[str], optional): ``["score", "plan", "apply"]``.

    Returns
    -------
    dict
        ``{"plan": [...], "aais_score": float, "patches": [...]}``.
    """
    paths: list[str] = payload.get("paths", [])
    prune_stale: bool = bool(payload.get("prune_stale", False))
    actions: list[str] = payload.get("actions", ["score", "plan"])

    if not paths:
        return {"plan": [], "aais_score": 0.0, "patches": [], "error": "paths is required"}

    scorer = AAISScorer()
    plan: list[dict[str, Any]] = []
    scores: list[float] = []

    for path_str in paths:
        scan_path = _REPO_ROOT / path_str if not Path(path_str).is_absolute() else Path(path_str)
        if not scan_path.exists():
            logger.debug("Doc refresh: path '%s' not found; skipping", scan_path)
            continue

        md_files = list(scan_path.rglob("*.md")) if scan_path.is_dir() else [scan_path]

        for md_file in sorted(md_files):
            try:
                text = md_file.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            aais = scorer.score(text)
            scores.append(aais.total)

            rel = _safe_relative(md_file, scan_path)
            content_hash = hashlib.sha256(text.encode()).hexdigest()[:16]

            if aais.total < _AAIS_PRUNE_THRESHOLD and prune_stale:
                plan.append(
                    {
                        "op": "prune",
                        "path": rel,
                        "reason": f"AAIS {aais.total:.2f} < prune threshold {_AAIS_PRUNE_THRESHOLD}",  # noqa: E501
                        "aais_score": aais.total,
                        "hash": content_hash,
                    }
                )
            elif aais.total < _AAIS_REFRESH_THRESHOLD:
                plan.append(
                    {
                        "op": "upsert",
                        "path": rel,
                        "reason": f"AAIS {aais.total:.2f} < refresh threshold {_AAIS_REFRESH_THRESHOLD}",  # noqa: E501
                        "aais_score": aais.total,
                        "hash": content_hash,
                        "dimensions": {
                            "concision": aais.concision,
                            "acronym_discipline": aais.acronym_discipline,
                            "structure": aais.structure,
                            "clarity": aais.clarity,
                            "citation_lineage": aais.citation_lineage,
                        },
                    }
                )

    overall_aais = sum(scores) / len(scores) if scores else 0.0

    patches: list[dict[str, Any]] = []
    if "apply" in actions:
        for op in plan:
            if op["op"] == "prune":
                patches.append(
                    {"applied": "prune", "path": op["path"], "status": "pending_human_review"}
                )
            elif op["op"] == "upsert":
                patches.append(
                    {"applied": "upsert_flag", "path": op["path"], "status": "flagged_for_refresh"}
                )

    return {
        "plan": plan,
        "aais_score": round(overall_aais, 4),
        "patches": patches,
        "files_scanned": len(scores),
    }


def _safe_relative(path: Path, base: Path) -> str:
    """Return *path* relative to *base* (or *_REPO_ROOT*), falling back to str."""
    for anchor in (base, _REPO_ROOT):
        try:
            return str(path.relative_to(anchor))
        except ValueError:
            continue
    return str(path)
