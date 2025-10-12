from __future__ import annotations

from typing import Any

from common.hooks import BaseHook
from common.registry import METRICS


@METRICS.register("nonzero_rate")
def register_nonzero_rate(df=None, **_kwargs) -> float:
    if df is None or "value" not in df.columns:
        return float("nan")
    total = len(df)
    if total == 0:
        return 0.0
    return float((df["value"] != 0).sum() / total)


class StepCounterHook(BaseHook):
    def on_init(self, state: dict[str, Any]) -> None:  # type: ignore[override]
        state["plugin_steps"] = 0

    def on_step_end(self, state: dict[str, Any]) -> None:  # type: ignore[override]
        state["plugin_steps"] = int(state.get("plugin_steps", 0)) + 1
