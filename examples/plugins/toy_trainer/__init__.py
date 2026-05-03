"""Toy trainer plugin illustrating the expected callable signature."""

from __future__ import annotations

from collections.abc import Iterable
from typing import List


def build():
    def train(
        model, data: Iterable[object]
    ) -> list[dict[str, object]]:  # pragma: no cover - illustrative
        history: list[dict[str, object]] = []
        for step, batch in enumerate(data):
            history.append({"step": step, "batch": batch, "loss": 0.0})
        return history

    return train


__all__ = ["build"]
