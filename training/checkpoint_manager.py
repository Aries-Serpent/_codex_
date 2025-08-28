from __future__ import annotations

from pathlib import Path
from typing import Optional

try:
    from transformers import TrainerCallback, TrainerControl, TrainerState
except Exception:  # pragma: no cover - transformers optional
    TrainerCallback = object  # type: ignore
    TrainerState = TrainerControl = object  # type: ignore


class CheckpointManager:
    """Simple step-based checkpoint saver for ``Trainer``."""

    def __init__(self, checkpoint_dir: Path | str, save_steps: int = 100) -> None:
        self.dir = Path(checkpoint_dir)
        self.save_steps = int(save_steps)
        self.dir.mkdir(parents=True, exist_ok=True)

    def callback(self) -> "TrainerCallback":
        manager = self

        class _Callback(TrainerCallback):  # type: ignore[misc]
            def on_step_end(self, args, state: TrainerState, control: TrainerControl, **kwargs):
                if state.global_step > 0 and state.global_step % manager.save_steps == 0:
                    path = manager.dir / f"step-{state.global_step}"
                    model = kwargs.get("model")
                    if hasattr(model, "save_pretrained"):
                        model.save_pretrained(path)

        return _Callback()
