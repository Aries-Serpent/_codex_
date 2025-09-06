"""Simple callback for periodic checkpointing during training.

This manager integrates with the HuggingFace ``Trainer`` by exposing a
callback that saves model state every ``save_steps`` steps.  It retains the
last ``keep_last`` checkpoints and lays groundwork for tracking best
checkpoints based on a chosen metric (not yet implemented).
"""

from __future__ import annotations

from pathlib import Path

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
            def on_step_end(self, args, state: TrainerState, control: TrainerControl, **kwargs):
                if state.global_step and state.global_step % manager.save_steps == 0:
                    ckpt_path = manager.directory / f"step-{state.global_step}.pt"
                    save_checkpoint(
                        str(ckpt_path),
                        kwargs.get("model"),
                        kwargs.get("optimizer"),
                        kwargs.get("lr_scheduler"),
                        int(state.epoch or 0),
                        {},
                    )
                    ckpts = sorted(
                        manager.directory.glob("step-*.pt"),
                        key=lambda p: p.stat().st_mtime,
                        reverse=True,
                    )
                    for old in ckpts[manager.keep_last :]:
                        try:
                            old.unlink()
                        except Exception:  # pragma: no cover - best effort
                            pass
                return control

        return _Callback()
