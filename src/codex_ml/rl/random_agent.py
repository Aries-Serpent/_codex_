"""Toy random policy agent implementing the RLAgent interface."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Any, Mapping, Sequence

from codex_ml.interfaces.rl import RLAgent


class RandomAgent(RLAgent):
    """Agent that selects actions uniformly at random from a candidate set."""

    def __init__(self, actions: Sequence[Any] | None = None) -> None:
        self.actions = list(actions) if actions is not None else [0, 1]

    def act(self, state: Any) -> Any:  # noqa: D401 - docstring inherited
        return random.choice(self.actions)

    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:  # noqa: D401
        return {"loss": 0.0}

    def save(self, path: str) -> None:  # noqa: D401
        Path(path).write_text(",".join(map(str, self.actions)), encoding="utf-8")

    def load(self, path: str) -> None:  # noqa: D401
        try:
            data = Path(path).read_text(encoding="utf-8").strip()
            if data:
                self.actions = [int(x) if x.isdigit() else x for x in data.split(",")]
        except Exception:  # pragma: no cover - best effort
            pass
