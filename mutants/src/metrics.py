"""Common evaluation metrics and NDJSON helpers for Codex."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping
from pathlib import Path


def accuracy(predictions: Iterable[int], labels: Iterable[int]) -> float:
    """Return the fraction of matching elements between ``predictions`` and ``labels``."""

    preds = list(predictions)
    labs = list(labels)
    if len(preds) != len(labs):
        raise ValueError("predictions and labels must be the same length")
    if not preds:
        return 0.0
    matches = sum(int(pred == label) for pred, label in zip(preds, labs, strict=False))
    return matches / len(preds)


def write_ndjson(records: Iterable[Mapping[str, object]], path: str | Path) -> None:
    """Write ``records`` to ``path`` in newline-delimited JSON format."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(dict(record), ensure_ascii=False))
            handle.write("\n")


def append_ndjson(record: Mapping[str, object], path: str | Path) -> None:
    """Append ``record`` as a JSON line to ``path``."""

    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(dict(record), ensure_ascii=False))
        handle.write("\n")


__all__ = ["accuracy", "append_ndjson", "write_ndjson"]
