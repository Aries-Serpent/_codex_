"""Handler for the agent.aais.batch built-in skill.

Scores a batch of texts with the AAIS rubric and returns per-item results
plus an aggregated summary.  All processing is in-process (no model calls).
"""

from __future__ import annotations

from codex.skills.aais import AAISScorer

_DEFAULT_THRESHOLD = 0.75
_scorer = AAISScorer()


def run(payload: dict) -> dict:
    """Score a list of items with the AAIS rubric.

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

    scores: list[dict] = []
    total_score = 0.0

    for item in items:
        item_id = str(item.get("id", ""))
        text = str(item.get("text", ""))
        result = _scorer.score(text)

        entry: dict = {
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
        scores.append(entry)
        total_score += result.total

    passed = sum(1 for s in scores if s["pass"])
    avg = round(total_score / len(scores), 4) if scores else None

    return {
        "scores": scores,
        "summary": {
            "total": len(scores),
            "passed": passed,
            "failed": len(scores) - passed,
            "avg_score": avg,
            "threshold": threshold,
        },
    }
