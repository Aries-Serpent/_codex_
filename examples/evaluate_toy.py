"""Evaluate toy predictions using the metric registry."""

from __future__ import annotations

import json

from codex_ml.registry import get_metric


def main() -> None:
    preds = ["hello", "codex"]
    targets = ["hello", "world"]
    metrics = {
        "accuracy@token": get_metric("accuracy@token")([1, 2, 3], [1, 2, 3]),
        "exact_match": get_metric("exact_match")(preds, targets),
        "f1": get_metric("f1")(preds, targets),
    }
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
