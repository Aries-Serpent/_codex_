# BEGIN: CODEX_RISK_SCORE
"""Simple safety classifier with optional transformer backend.

The function attempts to load a tiny sentiment model via ``transformers`` to
produce a probabilistic risk score. When the dependency or model is
unavailable, it falls back to a logistic model based on keyword matches.
Scores are always in the ``[0.0, 1.0]`` range."""
from __future__ import annotations

from math import exp
from typing import Dict

try:  # optional dependency for a real classifier
    from transformers import pipeline  # type: ignore
except Exception:  # pragma: no cover - transformers not installed
    pipeline = None  # type: ignore

MODEL_NAME = "philschmid/tiny-bert-sst2-distilled"
_classifier = None

# keyword weights used by the fallback logistic model
WEIGHTS: Dict[str, float] = {
    "password": 1.0,
    "api_key": 1.0,
    "ssn": 1.0,
    "rm -rf /": 2.0,
    "kill": 2.0,
    "drop database": 2.0,
}


def _load_classifier():
    global _classifier
    if pipeline is None:
        return None
    if _classifier is None:
        _classifier = pipeline("text-classification", model=MODEL_NAME)
    return _classifier


def _keyword_logistic(text: str) -> float:
    tl = text.lower()
    score = sum(weight for k, weight in WEIGHTS.items() if k in tl)
    return 1.0 / (1.0 + exp(-score)) if score > 0 else 0.0


def risk_score(text: str) -> float:
    """Return a risk score between 0 and 1 for ``text``."""
    clf = _load_classifier()
    if clf is not None:
        result = clf(text, truncation=True)[0]
        score = float(result["score"])
        label = result["label"].lower()
        if label in {"negative", "toxic", "unsafe", "label_1"}:
            return score
        return 1.0 - score
    return _keyword_logistic(text)


# END: CODEX_RISK_SCORE
