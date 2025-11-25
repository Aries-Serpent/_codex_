from __future__ import annotations

from collections.abc import Mapping, Sequence

from .registry import register_metric


def _coerce_reward(value: object) -> float:
    if isinstance(value, Mapping) and "reward" in value:
        value = value.get("reward")
    try:
        return float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return 0.0


@register_metric("reward/mean", override=True)
@register_metric("reward:mean", override=True)
def reward_mean(predictions: Sequence[object], targets: Sequence[object] | None = None) -> float:
    """Return the mean reward from predictions or mapping payloads."""

    if not predictions:
        return 0.0
    values = [_coerce_reward(p) for p in predictions]
    return float(sum(values) / len(values))


@register_metric("reward/success_rate", override=True)
@register_metric("reward:success_rate", override=True)
def reward_success_rate(
    predictions: Sequence[object], targets: Sequence[object] | None = None, *, threshold: float = 0.0
) -> float:
    """Proportion of rewards meeting or exceeding ``threshold``."""

    if not predictions:
        return 0.0
    values = [_coerce_reward(p) for p in predictions]
    hits = sum(1 for value in values if value >= threshold)
    return float(hits / len(values))


__all__ = ["reward_mean", "reward_success_rate"]
