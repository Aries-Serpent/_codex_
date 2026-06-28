"""Handler for the agent.aais.batch built-in skill.

Scores a batch of texts with the AAIS rubric and returns per-item results
plus an aggregated summary.  All processing is in-process (no model calls).

Supports both synchronous and async batching:
- ``run(payload)``      — synchronous, processes items sequentially.
- ``run_async(payload)``— async, processes items concurrently via
  ``asyncio.gather`` with a Semaphore-based ``max_concurrency`` gate
  (useful for large batches in async contexts).
"""

from __future__ import annotations

import asyncio
import warnings
from typing import Any

from codex.skills.aais import AAISScorer

_DEFAULT_THRESHOLD = 0.75
_scorer = AAISScorer()


def _get_max_concurrency(payload: dict[str, Any], default: int) -> int:
    """Extract max_concurrency from payload with validation."""
    val = default
    if "max_concurrency" in payload:
        val = int(payload["max_concurrency"])
    elif "max_workers" in payload:
        warnings.warn(
            "'max_workers' is deprecated; use 'max_concurrency' instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        val = int(payload["max_workers"])

    if val < 0:
        raise ValueError("max_concurrency must be >= 0")
    return val


def _score_item(
    item: dict[str, Any],
    threshold: float,
    include_dims: bool,
) -> dict[str, Any]:
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


def _build_summary(scores: list[dict[str, Any]], threshold: float) -> dict[str, Any]:
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


def run(payload: dict[str, Any]) -> dict[str, Any]:
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
        - ``max_concurrency`` (int, optional): maximum batch chunk size for
          synchronous processing.  Useful for very large batches to limit peak
          memory pressure.  Set to 0 (default) to process all items at once.
          Items are processed sequentially in chunks; the API is identical to
          the unbounded case.
        - ``max_workers`` (int, optional): deprecated alias for
          ``max_concurrency``.

    Returns
    -------
    dict
        ``{"scores": [...], "summary": {...}}``.
        Each score entry has ``{id, total, pass, ...dimensions?}``.
    """
    items: list[dict[str, Any]] = list[Any](payload.get("items", []))
    if not items:
        return {
            "scores": [],
            "summary": {"total": 0, "passed": 0, "failed": 0, "avg_score": None},
        }

    threshold: float = float(payload.get("threshold", _DEFAULT_THRESHOLD))
    include_dims: bool = bool(payload.get("include_dimensions", False))
    max_concurrency: int = _get_max_concurrency(payload, 0)

    if max_concurrency > 0:
        # Process in sequential chunks to throttle peak memory on large batches.
        scores: list[dict[str, Any]] = []
        for start in range(0, len(items), max_concurrency):
            chunk = items[start : start + max_concurrency]
            scores.extend(_score_item(item, threshold, include_dims) for item in chunk)
    else:
        scores = [_score_item(item, threshold, include_dims) for item in items]

    return {
        "scores": scores,
        "summary": _build_summary(scores, threshold),
    }


async def run_async(payload: dict[str, Any]) -> dict[str, Any]:
    """Score a list of items with the AAIS rubric (async / concurrent).

    Dispatches each item to the default thread executor so CPU-bound scoring
    does not block the event loop.  A ``max_concurrency`` semaphore caps the
    number of items in flight simultaneously, preventing runaway memory use on
    very large batches.

    Parameters
    ----------
    payload : dict
        Same keys as :func:`run`.  Additional optional keys:

        - ``max_concurrency`` (int, optional): maximum number of items scored
          concurrently (default: min(32, len(items) + 4)).  Set to 1 to force
          sequential execution.
        - ``max_workers`` (int, optional): alias for ``max_concurrency``;
          accepted for backwards compatibility.

    Returns
    -------
    dict
        Same shape as :func:`run`.
    """
    items: list[dict[str, Any]] = list[Any](payload.get("items", []))
    if not items:
        return {
            "scores": [],
            "summary": {"total": 0, "passed": 0, "failed": 0, "avg_score": None},
        }

    threshold: float = float(payload.get("threshold", _DEFAULT_THRESHOLD))
    include_dims: bool = bool(payload.get("include_dimensions", False))
    _default_concurrency = min(32, len(items) + 4)
    max_concurrency: int = _get_max_concurrency(payload, _default_concurrency)

    loop = asyncio.get_running_loop()
    sem = asyncio.Semaphore(max_concurrency)

    async def _guarded(item: dict[str, Any]) -> dict[str, Any]:
        async with sem:
            return await loop.run_in_executor(None, _score_item, item, threshold, include_dims)

    scores: list[dict[str, Any]] = list[Any](
        await asyncio.gather(*[_guarded(item) for item in items])
    )

    return {
        "scores": scores,
        "summary": _build_summary(scores, threshold),
    }
