from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from codex_ml.utils.checkpointing import build_payload_bytes, dump_rng_state


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
        keep_best: int | None = None,
        best_k: int | None = None,
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.save_steps = int(save_steps) if save_steps else 0
        self.keep_last = int(keep_last)
        self.metric = metric
        self.mode = mode
        resolved_best = best_k if best_k is not None else keep_best
        if resolved_best is None:
            resolved_best = 1
        self.best_k = max(1, int(resolved_best))
        self._best_meta = self.root / "best.json"
        self._best_file = self.root / "best"
        self._best_dir = self.root / "best_candidates"
        self._best_dir.mkdir(parents=True, exist_ok=True)
        self._best_records: list[dict[str, Any]] = []
        if self.metric and self._best_meta.exists():
            try:
                data = json.loads(self._best_meta.read_text(encoding="utf-8"))
                items = data.get("items")
                if isinstance(items, list):
                    for entry in items:
                        path = entry.get("path")
                        value = entry.get("value")
                        step = entry.get("step")
                        if path is None or value is None:
                            continue
                        try:
                            self._best_records.append(
                                {
                                    "path": str(path),
                                    "value": float(value),
                                    "step": int(step) if step is not None else 0,
                                }
                            )
                        except (TypeError, ValueError):
                            continue
                elif "value" in data and "step" in data:
                    path = data.get("path")
                    if path is None and self._best_file.exists():
                        try:
                            path = os.readlink(self._best_file)
                        except OSError:
                            try:
                                path = self._best_file.read_text(encoding="utf-8").strip()
                            except Exception:
                                path = None
                    if path is not None:
                        try:
                            self._best_records.append(
                                {
                                    "path": str(path),
                                    "value": float(data.get("value", 0.0)),
                                    "step": int(data.get("step", 0)),
                                }
                            )
                        except (TypeError, ValueError):
                            pass
            except Exception:
                self._best_records = []
        self._best_records = self._best_records[: self.best_k]
        self._best = self._best_records[0]["value"] if self._best_records else None
        self._refresh_best_symlinks()

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
        *,
        rng_state: Optional[Dict[str, Any] | bool] = None,
    ) -> Path:
        """Persist ``payload`` under ``<prefix>-{step}.pt`` and manage retention."""
        path = self.root / f"{prefix}-{step}.pt"
        tmp = path.with_suffix(".tmp")
        tmp.write_bytes(payload)
        os.replace(tmp, path)
        self._prune(prefix)
        self._update_best(path, step, metrics)
        rng_payload: Optional[Dict[str, Any]]
        if rng_state is True:
            rng_payload = dump_rng_state()
        elif isinstance(rng_state, dict):
            rng_payload = dict(rng_state)
        else:
            rng_payload = None
        if metrics or rng_payload:
            meta_path = path.with_suffix(".meta.json")
            meta_path.write_text(
                json.dumps(
                    {
                        "step": int(step),
                        "metrics": metrics or {},
                        "rng": rng_payload,
                    },
                    indent=2,
                    sort_keys=True,
                ),
                encoding="utf-8",
            )
        return path

    def maybe_save(
        self,
        step: int,
        payload: bytes,
        metrics: Optional[Dict[str, float]],
        save_steps: int,
        prefix: str = "ckpt",
        *,
        rng_state: Optional[Dict[str, Any] | bool] = None,
    ) -> Optional[Path]:
        if save_steps and step % save_steps == 0:
            return self.save_now(step, payload, metrics, prefix, rng_state=rng_state)
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
                    manager.save_now(
                        step,
                        payload,
                        self._logs,
                        prefix="step",
                        rng_state=True,
                    )
                return control

        return _Callback()

    # ------------------------------------------------------------------
    # Helpers
    def _prune(self, prefix: str) -> None:
        if self.keep_last <= 0:
            return
        pattern = f"{prefix}-*.pt"
        ckpts = sorted(self.root.glob(pattern), key=self._extract_step)
        protected = {rec["path"] for rec in self._best_records}
        for p in ckpts[: -self.keep_last]:
            if p.name in protected:
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
            record = {"step": step, "value": val, "path": path.name}
            existing = [r for r in self._best_records if r["path"] != path.name]
            existing.append(record)

            def keyfn(item: dict[str, Any]) -> tuple[float, int]:
                value = float(item.get("value", 0.0))
                step_idx = int(item.get("step", 0))
                return (value, step_idx) if self.mode == "min" else (-value, step_idx)

            existing.sort(key=keyfn)
            self._best_records = existing[: self.best_k]
            self._best = self._best_records[0]["value"] if self._best_records else None
            top = self._best_records[0]
            payload = {
                "value": top["value"],
                "step": top["step"],
                "path": top["path"],
                "items": self._best_records,
            }
            self._best_meta.write_text(
                json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
            )
            self._refresh_best_symlinks()

    def _refresh_best_symlinks(self) -> None:
        if not self._best_dir.exists():
            self._best_dir.mkdir(parents=True, exist_ok=True)
        desired = set()
        for idx, record in enumerate(self._best_records, start=1):
            link = self._best_dir / f"best-{idx}.pt"
            target = self.root / record["path"]
            desired.add(link.name)
            try:
                if link.exists() or link.is_symlink():
                    link.unlink()
            except FileNotFoundError:
                pass
            try:
                rel = os.path.relpath(target, start=self._best_dir)
                os.symlink(rel, link)
            except OSError:
                link.write_text(str(target), encoding="utf-8")
        for child in list(self._best_dir.iterdir()):
            if child.name not in desired:
                try:
                    if child.is_symlink() or child.is_file():
                        child.unlink()
                except FileNotFoundError:
                    pass
        try:
            if self._best_file.exists() or self._best_file.is_symlink():
                self._best_file.unlink()
        except FileNotFoundError:
            pass
        if self._best_records:
            best_target = self._best_records[0]["path"]
            try:
                os.symlink(best_target, self._best_file)
            except OSError:
                self._best_file.write_text(best_target, encoding="utf-8")

    @staticmethod
    def find_resume(root: str | Path) -> Optional[str]:
        path = Path(root)
        candidates = list(path.glob("ckpt-*.pt")) + list(path.glob("step-*.pt"))
        if not candidates:
            return None
        latest = max(candidates, key=CheckpointManager._extract_step)
        return str(latest)


__all__ = ["CheckpointManager"]
