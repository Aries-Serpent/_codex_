from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

try:  # pragma: no cover - optional dependency
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore


class BaseHook:
    def on_init(self, state: dict[str, Any]) -> None: ...

    def on_step_end(self, state: dict[str, Any]) -> None: ...

    def on_epoch_end(self, state: dict[str, Any]) -> None: ...

    def on_checkpoint(self, state: dict[str, Any]) -> None: ...

    def on_finish(self, state: dict[str, Any]) -> None: ...


class HookManager:
    def __init__(self, hooks: list[BaseHook] | None = None) -> None:
        self.hooks: list[BaseHook] = hooks or []

    def add(self, hook: BaseHook) -> None:
        self.hooks.append(hook)

    def dispatch(self, name: str, state: dict[str, Any]) -> None:
        for hook in self.hooks:
            try:
                getattr(hook, name)(state)  # type: ignore[attr-defined]
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning("Hook %s.%s error: %s", hook.__class__.__name__, name, exc)


class EMAHook(BaseHook):
    """Maintain an exponential moving average of model parameters."""

    def __init__(self, decay: float = 0.999) -> None:
        self.decay = decay
        self.shadow: dict[str, Any] = {}

    def on_init(self, state: dict[str, Any]) -> None:
        if torch is None:
            return
        model = state.get("model")
        if model is None:
            return
        self.shadow = {name: param.detach().clone() for name, param in model.state_dict().items()}

    def on_step_end(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        model = state.get("model")
        if model is None:
            return
        with torch.no_grad():
            for name, param in model.state_dict().items():
                if name in self.shadow:
                    self.shadow[name].mul_(self.decay).add_(param.detach(), alpha=1.0 - self.decay)

    def on_checkpoint(self, state: dict[str, Any]) -> None:
        if torch is None or not self.shadow:
            return
        checkpoint_dir = state.get("checkpoint_dir")
        if checkpoint_dir is None:
            return
        try:
            torch.save(self.shadow, Path(checkpoint_dir) / "ema.pt")
        except Exception as exc:  # pragma: no cover - optional path
            logger.warning("EMAHook save failed: %s", exc)


class CheckpointHook(BaseHook):
    def __init__(
        self, every_steps: int = 100, out_dir: str | Path = "data/models/checkpoints"
    ) -> None:
        self.every_steps = max(int(every_steps), 1)
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def on_step_end(self, state: dict[str, Any]) -> None:
        # Clear any stale checkpoint directory so downstream hooks only react when a
        # checkpoint is freshly written. `_train_loop` dispatches `on_checkpoint`
        # every step, and without clearing this flag hooks like `EMAHook` would
        # keep writing their artifacts on every iteration once the first
        # checkpoint is produced.
        state.pop("checkpoint_dir", None)
        if torch is None:
            return
        step = int(state.get("global_step", 0))
        if step <= 0 or step % self.every_steps != 0:
            return
        model = state.get("model")
        if model is None or not hasattr(model, "state_dict"):
            return
        try:
            from torch import save as torch_save

            ckpt_path = self.out_dir / f"ckpt_step{step}.pt"
            torch_save(model.state_dict(), ckpt_path)
            state["checkpoint_dir"] = str(self.out_dir)
        except Exception as exc:  # pragma: no cover - optional
            logger.warning("Checkpoint save failed: %s", exc)


class NDJSONLogHook(BaseHook):
    def __init__(self, file: str | Path) -> None:
        self.file = Path(file)
        self.file.parent.mkdir(parents=True, exist_ok=True)

    def on_step_end(self, state: dict[str, Any]) -> None:
        record = {
            "ts": int(time.time()),
            "step": int(state.get("global_step", 0)),
            "epoch": int(state.get("epoch", 0)),
            "loss": float(state.get("last_loss")) if state.get("last_loss") is not None else None,
        }
        try:
            with self.file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(record) + "\n")
        except Exception as exc:  # pragma: no cover - best effort
            logger.debug("NDJSONLogHook failed to append record: %s", exc)
