"""Deterministic RL agent backed by a local JSON policy."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from codex_ml.interfaces.rl import RLAgent


@dataclass
class _PolicyState:
    actions: Sequence[int]
    loop: bool


class ScriptedAgent(RLAgent):
    """Replay a finite list of actions stored in an offline fixture."""

    def __init__(self, policy: _PolicyState) -> None:
        if not policy.actions:
            raise ValueError("Policy must contain at least one action")
        self._policy = policy
        self._index = 0

    @classmethod
    def from_file(cls, path: str | Path) -> "ScriptedAgent":
        candidate = Path(path)
        if candidate.is_dir():
            candidate = candidate / "policy.json"
        if not candidate.exists():
            raise FileNotFoundError(f"Policy file not found: {candidate}")
        payload = json.loads(candidate.read_text(encoding="utf-8"))
        actions = payload.get("actions", [])
        if not isinstance(actions, list):  # pragma: no cover - defensive
            raise TypeError("Policy JSON must include an 'actions' list")
        parsed_actions = [int(value) for value in actions]
        loop = bool(payload.get("loop", True))
        return cls(_PolicyState(actions=parsed_actions, loop=loop))

    def act(self, state: Any) -> Any:  # noqa: D401 - interface compliance
        action = self._policy.actions[self._index]
        self._index += 1
        if self._index >= len(self._policy.actions):
            self._index = 0 if self._policy.loop else len(self._policy.actions) - 1
        return action

    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:  # noqa: D401
        return {"loss": 0.0}

    def save(self, path: str) -> None:  # noqa: D401
        target = Path(path)
        payload = {"actions": list(self._policy.actions), "loop": self._policy.loop}
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load(self, path: str) -> None:  # noqa: D401
        reloaded = self.from_file(path)
        self._policy = reloaded._policy
        self._index = 0


__all__ = ["ScriptedAgent"]
