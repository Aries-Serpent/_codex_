# BEGIN: CODEX_IFACE_RL
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping


class RLAgent(ABC):
    """Abstract RL agent for text generation or other environments."""

    @abstractmethod
    def select_action(self, state: Any) -> Any:
        """Choose an action for the given state."""
        raise NotImplementedError

    @abstractmethod
    def update(self, trajectory: Mapping[str, Any]) -> dict[str, float]:
        """Update agent from a trajectory and return metrics (e.g., loss)."""
        raise NotImplementedError

    @abstractmethod
    def save(self, path: str) -> None:
        """Persist agent state."""
        raise NotImplementedError

    @abstractmethod
    def load(self, path: str) -> None:
        """Restore agent state."""
        raise NotImplementedError


# END: CODEX_IFACE_RL
