# BEGIN: CODEX_IFACE_REWARD
"""Reward model interfaces and a built-in heuristic implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Iterable, Mapping, Optional, Sequence

from codex_ml.plugins import reward_models

__all__ = ["RewardModel", "HeuristicRewardModel", "RewardModelError"]


class RewardModelError(ValueError):
    """Raised when provided data is incompatible with the reward model."""


class RewardModel(ABC):
    """Abstract reward model producing a scalar evaluation.

    Implementations must be deterministic and side-effect free because they are
    executed during tests and offline CI.  ``evaluate`` should always succeed
    for well-formed inputs; validation errors must raise
    :class:`RewardModelError` to provide actionable feedback to the caller.
    """

    @abstractmethod
    def evaluate(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        """Return a scalar reward (higher is better)."""

    def batch_evaluate(
        self,
        pairs: Sequence[tuple[str, str]],
        *,
        metadatas: Optional[Sequence[Optional[Mapping[str, Any]]]] = None,
    ) -> list[float]:
        """Optional batch evaluation; default maps to :meth:`evaluate`."""

        results: list[float] = []
        for index, (prompt, completion) in enumerate(pairs):
            meta = None
            if metadatas and index < len(metadatas):
                meta = metadatas[index]
            results.append(self.evaluate(prompt, completion, metadata=meta))
        return results

    @abstractmethod
    def learn(self, data: Any) -> dict[str, float]:
        """Update model parameters from data and return training metrics."""


@reward_models.register("heuristic")
@dataclass(slots=True)
class HeuristicRewardModel(RewardModel):
    """Lightweight rule-based reward model used in smoke tests.

    The model scores completions using a small set of deterministic heuristics
    that favour concise answers which avoid dangerous tokens.  It requires no
    external dependencies and executes in milliseconds, making it safe for
    offline CI environments.

    Parameters
    ----------
    banned_tokens:
        Sequence of lower-cased substrings that incur a security penalty when
        present in the completion.
    helpful_tokens:
        Tokens that slightly increase the reward when encountered.
    length_penalty:
        Multiplier applied to overly long completions.  Values should be in the
        range ``[0, 1]`` where higher numbers impose stronger penalties.
    target_length:
        Ideal token length; completions longer than this threshold will be
        penalised.
    """

    banned_tokens: Sequence[str] = ("drop table", "rm -rf", "shutdown")
    helpful_tokens: Sequence[str] = ("explain", "example", "steps")
    length_penalty: float = 0.02
    target_length: int = 128

    def __post_init__(self) -> None:
        if self.length_penalty < 0:
            raise RewardModelError("length_penalty must be non-negative")
        if self.target_length <= 0:
            raise RewardModelError("target_length must be positive")

    def _normalise(self, text: str) -> str:
        return " ".join(text.lower().split())

    def evaluate(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        if not isinstance(prompt, str) or not isinstance(completion, str):
            raise RewardModelError("prompt and completion must be strings")
        completion_norm = self._normalise(completion)
        if not completion_norm:
            return -1.0

        tokens = completion_norm.split()
        token_count = len(tokens)

        score = 0.8  # generous baseline to reward helpful answers
        score += min(token_count, self.target_length) / (4 * self.target_length)

        for helper in self.helpful_tokens:
            if helper in completion_norm:
                score += 0.1

        for banned in self.banned_tokens:
            if banned in completion_norm:
                score -= 0.5

        if token_count > self.target_length:
            score -= (token_count - self.target_length) * self.length_penalty

        # Encourage lexical overlap with the prompt when provided
        prompt_norm = self._normalise(prompt)
        if prompt_norm:
            prompt_tokens = set(prompt_norm.split())
            overlap = prompt_tokens.intersection(tokens)
            score += len(overlap) / (5 * max(1, len(prompt_tokens)))

        if metadata and metadata.get("safety_flag"):
            score -= 0.2

        return max(-1.0, min(1.0, score))

    def learn(self, data: Any) -> dict[str, float]:
        """Return summary statistics for provided supervised data.

        ``data`` should be an iterable of mappings containing ``prompt`` and
        ``completion`` keys.  Optional ``label`` or ``score`` entries are used
        for diagnostics but do not affect the rule-based parameters.  The
        method never mutates internal state; it simply returns aggregated
        metrics for visibility in logs and tests.
        """

        if data is None:
            raise RewardModelError("training data may not be None")
        if not isinstance(data, Iterable):
            raise RewardModelError("training data must be iterable")

        count = 0
        rewards: list[float] = []
        avg_label = 0.0
        for entry in data:
            if not isinstance(entry, Mapping):
                raise RewardModelError("each entry must be a mapping")
            prompt = entry.get("prompt", "")
            completion = entry.get("completion", "")
            metadata = entry.get("metadata")
            reward = self.evaluate(str(prompt), str(completion), metadata=metadata)
            rewards.append(reward)
            label = entry.get("label") or entry.get("score") or 0.0
            try:
                avg_label += float(label)
            except Exception:  # pragma: no cover - defensive fallback
                pass
            count += 1

        if count == 0:
            return {"samples": 0, "mean_reward": 0.0, "mean_label": 0.0}

        return {
            "samples": count,
            "mean_reward": sum(rewards) / count,
            "mean_label": avg_label / count,
        }


# END: CODEX_IFACE_REWARD
