"""Minimal RL agent implementation used for tests and examples."""

from __future__ import annotations

from typing import Any, Mapping

from codex_ml.interfaces.rl import RLAgent


class RandomAgent(RLAgent):
    """A trivial agent that always returns action ``0``."""

    def act(self, state: Any) -> Any:  # noqa: D401 - inherit docstring
        return 0

    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:  # noqa: D401
        return {"loss": 0.0}

    def save(self, path: str) -> None:  # noqa: D401
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("RANDOM_AGENT")

    def load(self, path: str) -> None:  # noqa: D401
        with open(path, "r", encoding="utf-8") as fh:
            fh.read()


__all__ = ["RandomAgent"]

