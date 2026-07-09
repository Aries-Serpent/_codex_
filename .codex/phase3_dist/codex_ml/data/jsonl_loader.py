"""
Jsonl Loader Module

This module provides functionality for jsonl loader.

Usage:
    from data.jsonl_loader import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import json  # noqa: E402
import random  # noqa: E402
from collections.abc import Iterable, Sequence  # noqa: E402
from pathlib import Path  # noqa: E402

__all__ = ["load_jsonl"]


def _normalise_text(value: object) -> Sequence[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value if item is not None]
    return [json.dumps(value, ensure_ascii=False)]


def _extract_texts_from_line(line: str) -> Iterable[str]:
    line = line.strip()
    if not line:
        return []
    try:
        obj = json.loads(line)
    except json.JSONDecodeError:
        logger.debug("Exception caught, returning", exc_info=True)
        return [line]
    if isinstance(obj, dict) and "text" in obj:
        return _normalise_text(obj["text"])
    if isinstance(obj, str):
        return [obj]
    return [line]


def load_jsonl(
    path: str | Path, *, seed: int = 42, val_fraction: float = 0.0
) -> tuple[list[str], list[str]]:
    """Load a JSONL file, returning (train_texts, val_texts).

    Parameters
    ----------
    path:
        File location to read.  Missing files yield two empty lists.
    seed:
        Seed used for deterministic shuffling prior to splitting.
    val_fraction:
        Fraction of examples assigned to the validation set (clamped to [0, 0.5]).
    """

    target = Path(path)
    if not target.exists():
        return [], []

    texts: list[str] = []
    for line in target.read_text(encoding="utf-8").splitlines():
        for item in _extract_texts_from_line(line):
            texts.append(str(item).strip())

    if not texts:
        return [], []

    val_fraction = max(0.0, min(float(val_fraction or 0.0), 0.5))
    rng = random.Random(int(seed))  # nosec B311 - deterministic validation split
    rng.shuffle(texts)

    n_val = int(len(texts) * val_fraction)
    val_texts = texts[:n_val]
    train_texts = texts[n_val:]
    return train_texts, val_texts
