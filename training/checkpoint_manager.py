"""Simple callback for periodic checkpointing during training.

This manager integrates with the HuggingFace ``Trainer`` by exposing a
callback that saves model state every ``save_steps`` steps.  It retains the
last ``keep_last`` checkpoints and lays groundwork for tracking best
checkpoints based on a chosen metric (not yet implemented).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:  # pragma: no cover - transformers optional
    from transformers import TrainerCallback, TrainerControl, TrainerState
except Exception:  # pragma: no cover
    TrainerCallback = object  # type: ignore
    TrainerState = TrainerControl = object  # type: ignore

from codex_ml.utils.checkpointing import save_checkpoint


class CheckpointManager:
    """Step-based checkpoint saver for HuggingFace ``Trainer``."""

    def __init__(self, directory: Path | str, save_steps: int = 100, keep_last: int = 3) -> None:
        self.directory = Path(directory)
        self.save_steps = int(save_steps)
        self.keep_last = int(keep_last)
        self.directory.mkdir(parents=True, exist_ok=True)

    def callback(self) -> "TrainerCallback":
        manager = self

        class _Callback(TrainerCallback):  # type: ignore[misc]
            def __init__(self) -> None:
                self.model: Any | None = None
                self.optimizer: Any | None = None
                self.lr_scheduler: Any | None = None

            def on_train_begin(self, args, state: TrainerState, control: TrainerControl, **kwargs):
                self.model = kwargs.get("model")
                self.optimizer = kwargs.get("optimizer")
                self.lr_scheduler = kwargs.get("lr_scheduler")
                return control

            def on_step_end(self, args, state: TrainerState, control: TrainerControl, **kwargs):
                if state.global_step and state.global_step % manager.save_steps == 0:
                    if self.model is None or self.optimizer is None:
                        raise RuntimeError("CheckpointManager callback missing model or optimizer")
                    ckpt_path = manager.directory / f"step-{state.global_step}.pt"
                    save_checkpoint(
                        str(ckpt_path),
                        self.model,
                        self.optimizer,
                        self.lr_scheduler,
                        int(state.epoch or 0),
                        {},
                    )
                    ckpts = sorted(
                        manager.directory.glob("step-*.pt"),
                        key=lambda p: int(p.stem.split("-")[1]),
                        reverse=True,
                    )
                    for old in ckpts[manager.keep_last :]:
                        try:
                            old.unlink()
                        except Exception:  # pragma: no cover - best effort
                            pass
                return control

        return _Callback()
