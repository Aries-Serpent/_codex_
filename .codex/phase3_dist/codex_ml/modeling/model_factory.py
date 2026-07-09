"""Model factory scaffolding for _codex_.

Provides a tiny placeholder API for constructing models given a config dict.
Real implementations should handle dtype, device placement, and optional
LoRA/PEFT hooks with guarded imports.
"""

from typing import Any


class DummyModel:
    def __init__(self, hidden_size: int = 8) -> None:
        self.hidden_size = hidden_size

    def __call__(self, x) -> None:
        return x


def build_model(config: dict[str, Any]) -> DummyModel:
    hidden = int(config.get("hidden_size", 8))
    return DummyModel(hidden_size=hidden)
