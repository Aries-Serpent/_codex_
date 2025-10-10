"""Capability scoring utilities for the traversal workflow (v1.1.0)."""

from __future__ import annotations

from typing import Dict, List


__all__ = [
    "aggregate_scores",
    "explain_score",
    "normalize_weights",
    "score_capability",
]


def normalize_weights(weights: Dict[str, float]) -> Dict[str, float]:
    total = float(sum(weights.values()))
    if total <= 0:
        raise ValueError("Weights must sum > 0")
    return {k: v / total for k, v in weights.items()}


def score_capability(components: Dict[str, float], weights: Dict[str, float]) -> float:
    w = normalize_weights(weights)
    return sum(max(0.0, min(1.0, components.get(k, 0.0))) * w[k] for k in w)


def explain_score(capability: dict, weights: Dict[str, float]) -> dict:
    components = capability.get("components", {})
    w_norm = normalize_weights(weights)
    partials = {}
    for k in w_norm:
        val = max(0.0, min(1.0, components.get(k, 0.0)))
        partials[k] = {"component_value": val, "weight": w_norm[k], "contribution": val * w_norm[k]}

    score = round(sum(v["contribution"] for v in partials.values()), 4)
    return {"id": capability.get("id"), "score": score, "partials": partials}


def aggregate_scores(capabilities: List[dict], weights: Dict[str, float]) -> List[dict]:
    w_norm = normalize_weights(weights)
    return [explain_score(cap, w_norm) for cap in capabilities]
