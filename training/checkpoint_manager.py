from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from codex_ml.utils.checkpointing import _write_checksum_manifest, build_payload_bytes


@dataclass
class _BestState:
    metric: Optional[str]
    mode: str = "min"
    value: float | None = None


class CheckpointManager:
    """Lightweight manager for periodic and best checkpoints."""

    def __init__(
        self,
        directory: Path | str,
        keep_last: int = 3,
        metric: str | None = None,
        mode: str = "min",
    ) -> None:
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.keep_last = int(keep_last)
        self.best = _BestState(metric=metric, mode=mode)
        self._re = re.compile(r"ckpt-(\\d+)\\.pt$")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _atomic_write(self, path: Path, data: bytes) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        _write_checksum_manifest(path)

    def _step_from_name(self, name: str) -> int:
        m = self._re.match(name)
        return int(m.group(1)) if m else -1

    def _trim_old(self) -> None:
        files = []
        for p in self.dir.glob("ckpt-*.pt"):
            m = self._re.match(p.name)
            if m:
                files.append((int(m.group(1)), p))
        files.sort(key=lambda t: t[0])
        if len(files) <= self.keep_last:
            return
        best_target = None
        best_link = self.dir / "best"
        if best_link.is_symlink():
            best_target = os.readlink(best_link)
        for _, path in files[: -self.keep_last]:
            if best_target and Path(best_target).name == path.name:
                continue
            try:
                path.unlink()
            except FileNotFoundError:
                pass

    def _promote_best(self, ckpt: Path, metrics: Dict[str, float] | None) -> bool:
        metric_name = self.best.metric
        if not metric_name or not metrics or metric_name not in metrics:
            return False
        val = float(metrics[metric_name])
        better = self.best.value is None or (
            val < self.best.value if self.best.mode == "min" else val > self.best.value
        )
        if better:
            link = self.dir / "best"
            if link.exists() or link.is_symlink():
                link.unlink()
            os.symlink(ckpt.name, link)
            (self.dir / "best.json").write_text(
                json.dumps(
                    {
                        "metric": metric_name,
                        "value": val,
                        "step": self._step_from_name(ckpt.name),
                    },
                    indent=2,
                )
            )
            self.best.value = val
            return True
        return False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def save_now(
        self,
        tag: int | str,
        payload_bytes: bytes,
        metrics: Optional[Dict[str, float]] = None,
    ) -> Path:
        name = f"ckpt-{tag}.pt" if isinstance(tag, int) else f"{tag}.pt"
        path = self.dir / name
        self._atomic_write(path, payload_bytes)
        last = self.dir / "last"
        if last.exists() or last.is_symlink():
            last.unlink()
        os.symlink(path.name, last)
        self._promote_best(path, metrics)
        self._trim_old()
        return path

    def maybe_save(
        self,
        step: int,
        payload_bytes: bytes,
        metrics: Optional[Dict[str, float]],
        save_steps: int,
    ) -> Optional[Path]:
        if save_steps and step % save_steps == 0:
            return self.save_now(step, payload_bytes, metrics)
        return None

    def callback(self, save_steps: int):
        from transformers import TrainerCallback

        manager = self

        class _Callback(TrainerCallback):
            def on_log(self, args, state, control, logs=None, **kwargs):
                if save_steps and state.global_step % save_steps == 0:
                    model = kwargs.get("model")
                    optimizer = kwargs.get("optimizer")
                    sched = kwargs.get("lr_scheduler")
                    scaler = kwargs.get("scaler")
                    payload = build_payload_bytes(
                        model,
                        optimizer,
                        sched,
                        scaler,
                        rng_state=True,
                    )
                    manager.save_now(state.global_step, payload, logs)
                return control

            def on_evaluate(self, args, state, control, metrics=None, **kwargs):
                model = kwargs.get("model")
                optimizer = kwargs.get("optimizer")
                sched = kwargs.get("lr_scheduler")
                scaler = kwargs.get("scaler")
                payload = build_payload_bytes(
                    model,
                    optimizer,
                    sched,
                    scaler,
                    rng_state=True,
                )
                manager.save_now(state.global_step, payload, metrics)
                return control

        return _Callback()

    @classmethod
    def find_resume(cls, directory: str | Path) -> Optional[Path]:
        d = Path(directory)
        link = d / "last"
        if link.is_symlink():
            return d / os.readlink(link)
        files = sorted(
            [p for p in d.glob("ckpt-*.pt")],
            key=lambda p: p.stat().st_mtime,
        )
        return files[-1] if files else None
