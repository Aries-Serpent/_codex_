"""Model factory scaffolding for _codex_.

Provides a tiny placeholder API for constructing models given a config dict.
Real implementations should handle dtype, device placement, and optional
LoRA/PEFT hooks with guarded imports.
"""


class DummyModel:
    def __init__(self, hidden_size: int = 8) -> None:
        self.hidden_size = hidden_size

    def __call__(self, x):
        return x


def build_model(config: dict) -> DummyModel:
    hidden = int(config.get("hidden_size", 8))
    return DummyModel(hidden_size=hidden)
