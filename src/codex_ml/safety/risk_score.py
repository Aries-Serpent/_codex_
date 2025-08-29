# BEGIN: CODEX_RISK_SCORE
"""Placeholder keyword-based risk scoring.

This stub assigns a score of ``1.0`` when any risky keyword is found in the
input text (case-insensitive) and ``0.0`` otherwise.

TODO: replace with a real model-based classifier.
"""
from __future__ import annotations

FLAGGED = {"password", "api_key", "ssn", "rm -rf /", "kill", "drop database"}


def risk_score(text: str) -> float:
    tl = text.lower()
    return 1.0 if any(k in tl for k in FLAGGED) else 0.0


# END: CODEX_RISK_SCORE
