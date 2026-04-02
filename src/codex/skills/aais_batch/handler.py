"""Handler for the agent.aais.batch built-in skill.

Scores a batch of texts with the AAIS rubric and returns per-item results
plus an aggregated summary.  All processing is in-process (no model calls).

Supports both synchronous and async batching:
- ``run(payload)``      — synchronous, processes items sequentially.
- ``run_async(payload)``— async, processes items concurrently via
  ``asyncio.gather`` (useful for large batches in async contexts).
"""

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from codex.skills.aais import AAISScorer

_DEFAULT_THRESHOLD = 0.75
_scorer = AAISScorer()


def _score_item(
    item: dict,
    threshold: float,
    include_dims: bool,
) -> dict:
    """Score a single item dict and return the result entry."""
    item_id = str(item.get("id", ""))
    text = str(item.get("text", ""))
    result = _scorer.score(text)

    entry: dict[str, Any] = {
        "id": item_id,
        "total": round(result.total, 4),
        "pass": result.total >= threshold,
    }
    if include_dims:
        entry["dimensions"] = {
            "concision": round(result.concision, 4),
            "acronym_discipline": round(result.acronym_discipline, 4),
            "structure": round(result.structure, 4),
            "clarity": round(result.clarity, 4),
            "citation_lineage": round(result.citation_lineage, 4),
        }
    return entry


def _build_summary(scores: list[dict], threshold: float) -> dict:
    passed = sum(1 for s in scores if s["pass"])
    total_score = sum(s["total"] for s in scores)
    avg = round(total_score / len(scores), 4) if scores else None
    return {
        "total": len(scores),
        "passed": passed,
        "failed": len(scores) - passed,
        "avg_score": avg,
        "threshold": threshold,
    }


def run(payload: dict) -> dict:
    """Score a list of items with the AAIS rubric (synchronous).

    Parameters
    ----------
    payload : dict
        Expected keys:

        - ``items`` (list, required): each entry is a dict with
          ``{"id": str, "text": str}``.  ``id`` may be any stable string.
        - ``threshold`` (float, optional): pass/fail gate (default 0.75).
        - ``include_dimensions`` (bool, optional): include per-dimension
          scores in output (default False).

    Returns
    -------
    dict
        ``{"scores": [...], "summary": {...}}``.
        Each score entry has ``{id, total, pass, ...dimensions?}``.
    """
    items: list[dict] = list(payload.get("items", []))
    if not items:
        return {
            "scores": [],
            "summary": {"total": 0, "passed": 0, "failed": 0, "avg_score": None},
        }

    threshold: float = float(payload.get("threshold", _DEFAULT_THRESHOLD))
    include_dims: bool = bool(payload.get("include_dimensions", False))

    scores = [_score_item(item, threshold, include_dims) for item in items]

    return {
        "scores": scores,
        "summary": _build_summary(scores, threshold),
    }


async def run_async(payload: dict) -> dict:
    """Score a list of items with the AAIS rubric (async / concurrent).

    Uses a ``ThreadPoolExecutor`` so the CPU-bound scoring does not block
    the event loop.  Useful when calling from an async context with large
    batches (e.g. 100+ items).

    Parameters
    ----------
    payload : dict
        Same keys as :func:`run`.  Additional optional key:

        - ``max_workers`` (int, optional): thread pool size (default: min(32,
          len(items) + 4)).  Set to 1 to force sequential execution.

    Returns
    -------
    dict
        Same shape as :func:`run`.
    """
    items: list[dict] = list(payload.get("items", []))
    if not items:
        return {
            "scores": [],
            "summary": {"total": 0, "passed": 0, "failed": 0, "avg_score": None},
        }

    threshold: float = float(payload.get("threshold", _DEFAULT_THRESHOLD))
    include_dims: bool = bool(payload.get("include_dimensions", False))
    max_workers: int = int(
        payload.get("max_workers", min(32, len(items) + 4))
    )

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            loop.run_in_executor(executor, _score_item, item, threshold, include_dims)
            for item in items
        ]
        scores: list[dict] = list(await asyncio.gather(*futures))

    return {
        "scores": scores,
        "summary": _build_summary(scores, threshold),
    }
