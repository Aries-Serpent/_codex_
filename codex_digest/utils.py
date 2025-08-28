from __future__ import annotations
from typing import Iterable, Tuple, Dict, List
import re


REDACT_ENV_KEYS = ("API_KEY", "TOKEN", "SECRET", "PASS", "PASSWORD", "CREDENTIAL")


def redact(s: str) -> str:
    return re.sub(r"([A-Za-z0-9_\-]{16,})", "[REDACTED]", s)


def five_whys(problem: str) -> List[str]:
    qs = [f"Why is '{problem}' happening?"]
    for i in range(2, 6):
        qs.append(f"Why {i-1}? What underlying cause enables the previous?")
    return qs


def pick_best(candidates: List[Tuple[str, float]]) -> Tuple[str, float]:
    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)
    return candidates[0]
