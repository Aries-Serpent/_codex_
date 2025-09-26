"""Light‑weight RLHF helpers used in tests and examples.

The real project will eventually plug in large reward models and policy
optimisers.  For the purposes of offline tests we provide a deterministic
reward model calibrator and a tiny trainer that coordinates a reward model with
an :class:`~codex_ml.interfaces.rl.RLAgent` implementation.  The goal is to
offer a concrete implementation that exercises the surrounding plumbing without
pulling in heavyweight dependencies.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, MutableMapping, Optional, Sequence

from codex_ml.interfaces.reward_model import RewardModel as RewardModelBase
from codex_ml.interfaces.rl import RLAgent

LOGGER = logging.getLogger(__name__)


def _coerce_triples(data: Iterable[Any]) -> list[tuple[str, str, float]]:
    """Normalise preference data into ``(prompt, completion, reward)`` tuples."""

    triples: list[tuple[str, str, float]] = []
    for item in data:
        prompt: Optional[str]
        completion: Optional[str]
        reward_value: Optional[float]

        if isinstance(item, Mapping):
            prompt = item.get("prompt")
            completion = item.get("completion")
            reward_value_raw = item.get("reward")
        elif isinstance(item, (tuple, list)) and len(item) >= 3:
            prompt = item[0]  # type: ignore[index]
            completion = item[1]  # type: ignore[index]
            reward_value_raw = item[2]  # type: ignore[index]
        else:  # pragma: no cover - defensive branch
            LOGGER.debug("Skipping unsupported preference entry: %r", item)
            continue

        if prompt is None or completion is None:
            LOGGER.debug("Skipping preference entry missing text: %r", item)
            continue

        try:
            reward_value = float(reward_value_raw) if reward_value_raw is not None else None
        except (TypeError, ValueError):
            LOGGER.debug("Skipping preference entry with non-numeric reward: %r", item)
            continue

        if reward_value is None:
            LOGGER.debug("Skipping preference entry without reward: %r", item)
            continue

        triples.append((str(prompt), str(completion), reward_value))

    return triples


@dataclass
class RewardModel(RewardModelBase):
    """Tiny reward model that calibrates a base implementation.

    The model wraps another :class:`RewardModelBase` instance (``LengthRewardModel``
    by default) and learns a linear transformation ``reward = scale * base + bias``
    from labelled preferences.  The helper is intentionally small but proves out
    the reward-model API for downstream tooling.
    """

    base_model: RewardModelBase | None = None
    scale: float = 1.0
    bias: float = 0.0
    _last_metrics: dict[str, float] = field(default_factory=dict, init=False, repr=False)

    def __post_init__(self) -> None:
        if self.base_model is None:
            from .simple import LengthRewardModel

            self.base_model = LengthRewardModel()

    # ``RewardModelBase`` already defines ``batch_evaluate``; we override
    # ``evaluate`` to apply the learnt calibration.
    def evaluate(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        if self.base_model is None:
            raise RuntimeError("RLHFRewardModel.base_model is None; cannot evaluate safely")
        base = self.base_model.evaluate(prompt, completion, metadata=metadata)
        return self.scale * float(base) + self.bias

    def score(
        self,
        prompt: str,
        completion: str,
        *,
        metadata: Optional[Mapping[str, Any]] = None,
    ) -> float:
        """Compatibility alias matching the historical stub method name."""

        return self.evaluate(prompt, completion, metadata=metadata)

    def learn(self, data: Iterable[Any]) -> dict[str, float]:  # noqa: D401 - interface method
        # Materialise the iterable so that we can feed it both to the wrapped
        # model and to the calibration logic without exhausting generators.
        materialised = list(data)
        triples = _coerce_triples(materialised)

        if self.base_model is None:
            raise RuntimeError("RLHFRewardModel.base_model is None; cannot compute metrics")
        base_metrics: dict[str, float] = {}
        try:
            maybe_metrics = self.base_model.learn(materialised)
        except Exception as exc:  # pragma: no cover - defensive
            LOGGER.debug("Base reward model learn() failed: %s", exc)
        else:
            if isinstance(maybe_metrics, Mapping):
                base_metrics = {
                    f"base_{k}": float(v)
                    for k, v in maybe_metrics.items()
                    if isinstance(v, (int, float))
                }

        if not triples:
            metrics = {"examples": 0.0, "scale": self.scale, "bias": self.bias}
            metrics.update(base_metrics)
            self._last_metrics = metrics
            return metrics

        xs = [self.base_model.evaluate(p, c) for p, c, _ in triples]
        ys = [reward for _, _, reward in triples]
        n = len(xs)

        mean_x = sum(xs) / n
        mean_y = sum(ys) / n
        denom = sum((x - mean_x) ** 2 for x in xs)
        if denom <= 1e-12:
            scale = 0.0
        else:
            scale = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys)) / denom
        bias = mean_y - scale * mean_x

        self.scale = float(scale)
        self.bias = float(bias)

        mse = sum((self.scale * x + self.bias - y) ** 2 for x, y in zip(xs, ys)) / n

        metrics = {
            "examples": float(n),
            "scale": self.scale,
            "bias": self.bias,
            "mse": float(mse),
        }
        metrics.update(base_metrics)
        self._last_metrics = metrics
        return metrics


class RLTrainer:
    """Minimal trainer orchestrating an agent and a reward model."""

    def __init__(
        self,
        agent: RLAgent,
        reward_model: RewardModel,
        *,
        discount: float = 1.0,
    ) -> None:
        self.agent = agent
        self.reward_model = reward_model
        self.discount = discount

    def _prepare_rewards(self, trajectory: Mapping[str, Any]) -> list[float]:
        rewards: list[float] = []
        existing = trajectory.get("rewards")
        if isinstance(existing, Sequence):
            for value in existing:
                try:
                    rewards.append(float(value))
                except (TypeError, ValueError):  # pragma: no cover - defensive
                    LOGGER.debug("Ignoring non-numeric reward value: %r", value)

        explicit = trajectory.get("reward")
        prompt = trajectory.get("prompt")
        completion = trajectory.get("completion")
        computed: Optional[float]
        if explicit is not None:
            try:
                computed = float(explicit)
            except (TypeError, ValueError):  # pragma: no cover - defensive
                computed = None
        elif prompt is not None and completion is not None:
            computed = self.reward_model.score(str(prompt), str(completion))
        else:
            computed = None

        if computed is not None:
            rewards.append(float(computed))

        return rewards

    def train(
        self,
        trajectories: Iterable[Mapping[str, Any]],
        *,
        reward_dataset: Iterable[Any] | None = None,
    ) -> dict[str, float]:
        reward_metrics: Optional[Mapping[str, float]] = None
        if reward_dataset is not None:
            dataset_list = list(reward_dataset)
            reward_metrics = self.reward_model.learn(dataset_list)

        episodes = 0
        total_reward = 0.0
        discounted_reward = 0.0
        metric_totals: dict[str, float] = defaultdict(float)
        metric_counts: dict[str, int] = defaultdict(int)

        for trajectory in trajectories:
            episodes += 1
            traj_dict: MutableMapping[str, Any] = dict(trajectory)
            rewards = self._prepare_rewards(traj_dict)
            if rewards:
                traj_dict["rewards"] = rewards
                total_reward += sum(rewards)
                discounted_reward += sum((self.discount**i) * r for i, r in enumerate(rewards))

            agent_metrics = self.agent.update(traj_dict)
            for key, value in agent_metrics.items():
                try:
                    metric_totals[key] += float(value)
                    metric_counts[key] += 1
                except (TypeError, ValueError):  # pragma: no cover - defensive
                    LOGGER.debug("Ignoring non-numeric agent metric %s=%r", key, value)

        result: dict[str, float] = {
            "episodes": float(episodes),
            "total_reward": float(total_reward),
            "discounted_reward": float(discounted_reward),
        }
        for key, value in metric_totals.items():
            count = metric_counts[key]
            if count:
                result[f"agent_{key}"] = value / count

        if reward_metrics is not None:
            for key, value in reward_metrics.items():
                if isinstance(value, (int, float)):
                    result[f"reward_{key}"] = float(value)

        return result
