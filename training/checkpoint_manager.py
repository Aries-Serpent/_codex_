from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict, Optional

from codex_ml.utils.checkpointing import build_payload_bytes


class CheckpointManager:
    """Lightweight step-based checkpoint manager."""

    def __init__(
        self,
        root: str | Path,
        *,
        save_steps: int | None = None,
        keep_last: int = 5,
        metric: str | None = None,
        mode: str = "min",
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.save_steps = int(save_steps) if save_steps else 0
        self.keep_last = int(keep_last)
        self.metric = metric
        self.mode = mode
        self._best: Optional[float] = None
        self._best_file = self.root / "best"
        self._best_meta = self.root / "best.json"
        if self.metric and self._best_meta.exists():
            try:
                data = json.loads(self._best_meta.read_text(encoding="utf-8"))
                self._best = float(data.get("value"))
            except Exception:
                self._best = None

    # ------------------------------------------------------------------
    # Basic file helpers
    @staticmethod
    def _extract_step(path: Path) -> int:
        try:
            return int(path.stem.split("-")[1])
        except Exception:
            return -1

    # ------------------------------------------------------------------
    # Public API
    def save_now(
        self,
        step: int,
        payload: bytes,
        metrics: Optional[Dict[str, float]] = None,
        prefix: str = "ckpt",
    ) -> Path:
        """Persist ``payload`` under ``<prefix>-{step}.pt`` and manage retention."""
        path = self.root / f"{prefix}-{step}.pt"
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(payload)
        os.replace(tmp, path)
        self._prune(prefix)
        self._update_best(path, step, metrics)
        return path

    def maybe_save(
        self,
        step: int,
        payload: bytes,
        metrics: Optional[Dict[str, float]],
        save_steps: int,
        prefix: str = "ckpt",
    ) -> Optional[Path]:
        if save_steps and step % save_steps == 0:
            return self.save_now(step, payload, metrics, prefix)
        return None

    def callback(self):
        """Return a ``TrainerCallback`` that uses this manager."""
        if not self.save_steps:
            raise RuntimeError("save_steps must be set to use callback()")
        from transformers import TrainerCallback  # lazy import

        manager = self
        save_every = self.save_steps

        class _Callback(TrainerCallback):  # type: ignore[misc]
            def __init__(self) -> None:
                self.model = None
                self.optimizer = None
                self.lr_scheduler = None
                self.scaler = None
                self._logs: Optional[Dict[str, float]] = None

            def on_train_begin(self, args, state, control, **kwargs):
                self.model = kwargs.get("model")
                self.optimizer = kwargs.get("optimizer")
                self.lr_scheduler = kwargs.get("lr_scheduler")
                self.scaler = kwargs.get("scaler")
                if self.model is None or self.optimizer is None:
                    raise RuntimeError("model and optimizer are required for checkpointing")
                return control

            def on_log(self, args, state, control, logs=None, **kwargs):
                self._logs = dict(logs or {})
                return control

            def on_step_end(self, args, state, control, **kwargs):
                step = state.global_step
                if step and save_every and step % save_every == 0:
                    if self.model is None or self.optimizer is None:
                        raise RuntimeError(
                            "Checkpoint callback missing model/optimizer; on_train_begin not called"
                        )
                    payload = build_payload_bytes(
                        self.model,
                        self.optimizer,
                        self.lr_scheduler,
                        self.scaler,
                        rng_state=True,
                    )
                    manager.save_now(step, payload, self._logs, prefix="step")
                return control

        return _Callback()

    # ------------------------------------------------------------------
    # Helpers
    def _prune(self, prefix: str) -> None:
        if self.keep_last <= 0:
            return
        pattern = f"{prefix}-*.pt"
        ckpts = sorted(self.root.glob(pattern), key=self._extract_step)
        best_path: Optional[Path] = None
        if self._best_file.is_symlink():
            try:
                best_path = self.root / os.readlink(self._best_file)
            except OSError:
                best_path = None
        for p in ckpts[: -self.keep_last]:
            if best_path is not None and p == best_path:
                continue
            try:
                p.unlink()
            except FileNotFoundError:
                pass

    def _update_best(self, path: Path, step: int, metrics: Optional[Dict[str, float]]) -> None:
        if not self.metric or not metrics or self.metric not in metrics:
            return
        val = float(metrics[self.metric])
        better = False
        if self._best is None:
            better = True
        elif self.mode == "min":
            better = val < self._best
        else:
            better = val > self._best
        if better:
            self._best = val
            if self._best_file.exists() or self._best_file.is_symlink():
                try:
                    self._best_file.unlink()
                except Exception:
                    pass
            os.symlink(path.name, self._best_file)
            data = {"step": step, "value": val}
            self._best_meta.write_text(json.dumps(data), encoding="utf-8")

    @staticmethod
    def find_resume(root: str | Path) -> Optional[str]:
        path = Path(root)
        candidates = list(path.glob("ckpt-*.pt")) + list(path.glob("step-*.pt"))
        if not candidates:
            return None
        latest = max(candidates, key=CheckpointManager._extract_step)
        return str(latest)


__all__ = ["CheckpointManager"]
