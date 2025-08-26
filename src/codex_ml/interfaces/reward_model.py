# BEGIN: CODEX_IFACE_REWARD
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Mapping, Optional


class RewardModel(ABC):
    """Abstract reward model producing a scalar score for (prompt, completion)."""

    @abstractmethod
    def score(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        """Return a scalar reward (higher is better)."""
        raise NotImplementedError

    def batch_score(
        self,
        pairs: list[tuple[str, str]],
        *,
        metadatas: Optional[list[Optional[Mapping[str, Any]]]] = None,
    ) -> list[float]:
        """Optional batch scoring; default maps to score()."""
        res: list[float] = []
        for i, (p, c) in enumerate(pairs):
            md = metadatas[i] if metadatas and i < len(metadatas) else None
            res.append(self.score(p, c, metadata=md))
        return res


# END: CODEX_IFACE_REWARD
