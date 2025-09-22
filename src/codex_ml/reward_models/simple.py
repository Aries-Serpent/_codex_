from __future__ import annotations

from typing import Any, Mapping, Optional

from codex_ml.interfaces.reward_model import RewardModel


class LengthRewardModel(RewardModel):
    """Toy reward model that scores completions by length.

    Parameters
    ----------
    scale:
        Multiplicative factor applied to the completion length.
    offset:
        Constant added to the scaled length.

    This implementation is intentionally simple and is intended for tests and
    examples. The reward defaults to the number of characters in the completion
    but can be tuned via ``scale`` and ``offset``.
    """

    def __init__(self, *, scale: float = 1.0, offset: float = 0.0) -> None:
        self.scale = float(scale)
        self.offset = float(offset)

    def evaluate(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        """Return ``offset + scale * len(completion)`` as the reward."""
        return self.offset + self.scale * float(len(completion))

    def learn(self, data: Any) -> dict[str, float]:
        """Dummy learn method returning a placeholder metric."""
        return {"loss": 0.0}
