from __future__ import annotations

import re

REDACT_ENV_KEYS = ("API_KEY", "TOKEN", "SECRET", "PASS", "PASSWORD", "CREDENTIAL")


def redact(s: str) -> str:
    return re.sub(r"([A-Za-z0-9_\-]{16,})", "[REDACTED]", s)


def five_whys(problem: str) -> list[str]:
    qs = [f"Why is '{problem}' happening?"]
    for i in range(2, 6):
        qs.append(f"Why {i-1}? What underlying cause enables the previous?")
    return qs


def pick_best(candidates: list[tuple[str, float]]) -> tuple[str, float]:
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    return candidates[0]
