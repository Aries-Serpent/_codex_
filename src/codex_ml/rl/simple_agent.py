"""Minimal RL agent implementation used for tests and examples."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from codex_ml.interfaces.rl import RLAgent


class RandomAgent(RLAgent):
    """A trivial agent that always returns action ``0``."""

    def act(self, state: Any) -> Any:
        return 0

    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:
        return {"loss": 0.0}

    def save(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("RANDOM_AGENT")

    def load(self, path: str) -> None:
        with open(path, encoding="utf-8") as fh:
            fh.read()


__all__ = ["RandomAgent"]
