# BEGIN: CODEX_IFACE_RL
"""Reinforcement-learning agent interfaces with a default bandit agent."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, MutableMapping, Sequence

from codex_ml.plugins import rl_agents

__all__ = ["RLAgent", "BanditRLAgent", "RLAgentError"]


class RLAgentError(RuntimeError):
    """Raised when an agent receives malformed input."""


class RLAgent(ABC):
    """Abstract RL agent for text generation or other environments."""

    @abstractmethod
    def act(self, state: Any) -> Any:
        """Choose an action for the given state."""

    @abstractmethod
    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:
        """Update agent from a trajectory and return metrics (e.g., loss)."""

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist agent state."""

    @abstractmethod
    def load(self, path: str) -> None:
        """Restore agent state."""


@rl_agents.register("bandit")
@dataclass(slots=True)
class BanditRLAgent(RLAgent):
    """Deterministic contextual bandit agent used for smoke tests.

    The agent maintains running averages of rewards for each action and always
    selects the highest-scoring option.  The behaviour is deterministic to keep
    tests reproducible; ties are resolved lexicographically.

    Parameters
    ----------
    actions:
        Optional list of allowed actions.  If omitted the agent learns actions
        on the fly when :meth:`update` is called.
    exploration_bonus:
        Small value added to unseen actions to encourage trying them at least
        once.  Set to ``0`` to disable exploration entirely.
    """

    actions: Sequence[str] | None = None
    exploration_bonus: float = 0.05
    _values: MutableMapping[str, float] = field(default_factory=dict, init=False)
    _counts: MutableMapping[str, int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        if self.exploration_bonus < 0:
            raise RLAgentError("exploration_bonus must be non-negative")
        if self.actions:
            for action in self.actions:
                self._values[str(action)] = 0.0
                self._counts[str(action)] = 0

    def _ensure_known(self, action: str) -> None:
        if action not in self._values:
            self._values[action] = 0.0
            self._counts[action] = 0

    def act(self, state: Mapping[str, Any]) -> str:
        if not isinstance(state, Mapping):
            raise RLAgentError("state must be a mapping")
        candidates = state.get("candidates")
        if candidates is None:
            candidates = list(self._values.keys())
        if not candidates:
            raise RLAgentError("no candidate actions provided")

        selected = None
        best_value = float("-inf")
        for candidate in candidates:
            candidate_str = str(candidate)
            self._ensure_known(candidate_str)
            count = self._counts[candidate_str]
            value = self._values[candidate_str]
            if count == 0:
                value += self.exploration_bonus
            if value > best_value or (
                value == best_value and (selected is None or candidate_str < selected)
            ):
                selected = candidate_str
                best_value = value
        assert selected is not None  # defensive
        return selected

    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:
        if not isinstance(trajectory, Mapping):
            raise RLAgentError("trajectory must be a mapping")
        actions = trajectory.get("actions")
        rewards = trajectory.get("rewards")
        if not isinstance(actions, Sequence) or not isinstance(rewards, Sequence):
            raise RLAgentError("actions and rewards must be sequences")
        if len(actions) != len(rewards):
            raise RLAgentError("actions and rewards must have equal length")
        if not actions:
            return {"updates": 0, "mean_reward": 0.0}

        total_reward = 0.0
        for action, reward in zip(actions, rewards):
            action_str = str(action)
            try:
                reward_value = float(reward)
            except Exception as exc:  # pragma: no cover - defensive
                raise RLAgentError(f"invalid reward value: {reward}") from exc
            self._ensure_known(action_str)
            count = self._counts[action_str] + 1
            self._counts[action_str] = count
            old_value = self._values[action_str]
            self._values[action_str] = old_value + (reward_value - old_value) / count
            total_reward += reward_value

        return {"updates": len(actions), "mean_reward": total_reward / len(actions)}

    def save(self, path: str) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {"values": dict(self._values), "counts": dict(self._counts)}
        target.write_text(json.dumps(payload), encoding="utf-8")

    def load(self, path: str) -> None:
        target = Path(path)
        if not target.exists():
            raise RLAgentError(f"state file does not exist: {path}")
        payload = json.loads(target.read_text(encoding="utf-8"))
        values = payload.get("values", {})
        counts = payload.get("counts", {})
        if not isinstance(values, dict) or not isinstance(counts, dict):
            raise RLAgentError("invalid state file")
        self._values = {str(k): float(v) for k, v in values.items()}
        self._counts = {str(k): int(v) for k, v in counts.items()}


# END: CODEX_IFACE_RL
