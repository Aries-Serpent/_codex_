"""
Curves Module

This module provides functionality for curves.

Usage:
    from metrics.curves import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

# BEGIN: CODEX_METRIC_CURVES
from __future__ import annotations

import json
from pathlib import Path


def append_curve(path: Path, metric: str, step: int, value: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    f = path / f"{metric}.jsonl"
    with f.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({"step": step, "value": value}) + "\n")


def summarize(path: Path, metric: str) -> dict[str, float]:
    import statistics as st

    f = path / f"{metric}.jsonl"
    vals: list[float] = []
    if f.exists():
        for line in f.read_text(encoding="utf-8").splitlines():
            vals.append(float(json.loads(line)["value"]))
    return {"count": len(vals), "mean": (st.mean(vals) if vals else 0.0)}


# END: CODEX_METRIC_CURVES
