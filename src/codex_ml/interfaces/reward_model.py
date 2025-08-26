# BEGIN: CODEX_IFACE_REWARD
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional


class RewardModel(ABC):
    """Abstract reward model producing a scalar evaluation for (prompt, completion)."""

    @abstractmethod
    def evaluate(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        """Return a scalar reward (higher is better)."""
        raise NotImplementedError

    def batch_evaluate(
        self,
        pairs: list[tuple[str, str]],
        *,
        metadatas: Optional[list[Optional[Mapping[str, Any]]]] = None,
    ) -> list[float]:
        """Optional batch evaluation; default maps to evaluate()."""
        res: list[float] = []
        for i, (p, c) in enumerate(pairs):
            md = metadatas[i] if metadatas and i < len(metadatas) else None
            res.append(self.evaluate(p, c, metadata=md))
        return res

    @abstractmethod
    def learn(self, data: Any) -> dict[str, float]:
        """Update model parameters from data and return training metrics."""
        raise NotImplementedError


# END: CODEX_IFACE_REWARD
