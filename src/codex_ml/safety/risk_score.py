# BEGIN: CODEX_RISK_SCORE
from __future__ import annotations


def risk_score(text: str) -> float:
    bad = ["password", "api_key", "ssn", "rm -rf /", "kill", "drop database"]
    score = 0
    tl = text.lower()
    for k in bad:
        if k in tl:
            score += 1
    return float(score)


# END: CODEX_RISK_SCORE
