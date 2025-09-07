from __future__ import annotations

from typing import Any, Mapping, Optional

from codex_ml.interfaces.reward_model import RewardModel


class LengthRewardModel(RewardModel):
    """Toy reward model that scores completions by length.

    This implementation is intentionally simple and is intended for tests and
    examples. The reward is the number of characters in the completion.
    """

    def evaluate(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        """Return the length of ``completion`` as the reward."""
        return float(len(completion))

    def learn(self, data: Any) -> dict[str, float]:
        """Dummy learn method returning a placeholder metric."""
        return {"loss": 0.0}
