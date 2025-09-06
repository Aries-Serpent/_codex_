"""Engine-agnostic checkpoint manager with retention and best tracking."""

from __future__ import annotations

import contextlib
import hashlib
import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


# write checksum manifest alongside checkpoint for integrity
def _write_checksum(path: Path) -> None:
    meta = {
        "file": path.name,
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
    }
    (path.parent / "checksums.json").write_text(json.dumps(meta), encoding="utf-8")


@dataclass
class _Best:
    metric: Optional[str]
    mode: str = "min"
    value: float | None = None


class CheckpointManager:
    """Manage periodic checkpoints and track the best snapshot."""

    def __init__(
        self,
        directory: str | Path,
        keep_last: int = 3,
        metric: str | None = "eval_loss",
        mode: str = "min",
    ) -> None:
        self.dir = Path(directory)
        self.dir.mkdir(parents=True, exist_ok=True)
        self.keep_last = int(keep_last)
        self.best = _Best(metric, mode)
        self._re_ckpt = re.compile(r"ckpt-(\d+)\.pt$")

    # ------------------------------------------------------------------
    # internal helpers
    # ------------------------------------------------------------------
    def _atomic_write(self, path: Path, data: bytes) -> None:
        tmp = path.with_suffix(path.suffix + ".tmp")
        with open(tmp, "wb") as fh:
            fh.write(data)
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, path)
        _write_checksum(path)

    def _step_from_name(self, name: str) -> int:
        m = self._re_ckpt.search(name)
        return int(m.group(1)) if m else -1

    def _trim_old(self) -> None:
        ckpts = sorted(
            [p for p in self.dir.glob("ckpt-*.pt") if self._re_ckpt.search(p.name)],
            key=lambda p: self._step_from_name(p.name),
        )
        best_target = None
        best_link = self.dir / "best"
        if best_link.is_symlink():
            with contextlib.suppress(OSError):
                best_target = (self.dir / os.readlink(best_link)).resolve()
        for p in ckpts[: -self.keep_last] if self.keep_last > 0 else ckpts:
            if best_target and p.resolve() == best_target:
                continue
            with contextlib.suppress(FileNotFoundError):
                p.unlink()

    def _promote_best(self, ckpt_path: Path, metrics: Dict[str, float] | None) -> None:
        if not self.best.metric or not metrics or self.best.metric not in metrics:
            return
        val = float(metrics[self.best.metric])
        better = self.best.value is None or (
            val < self.best.value if self.best.mode == "min" else val > self.best.value
        )
        if better:
            link = self.dir / "best"
            with contextlib.suppress(FileNotFoundError):
                link.unlink()
            os.symlink(ckpt_path.name, link)
            (self.dir / "best.json").write_text(
                json.dumps(
                    {
                        "metric": self.best.metric,
                        "value": val,
                        "step": self._step_from_name(ckpt_path.name),
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            self.best.value = val

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    def save_now(
        self, step: int, payload_bytes: bytes, metrics: Dict[str, float] | None = None
    ) -> Path:
        name = f"ckpt-{step}.pt"
        path = self.dir / name
        self._atomic_write(path, payload_bytes)
        link = self.dir / "last"
        with contextlib.suppress(FileNotFoundError):
            link.unlink()
        os.symlink(path.name, link)
        self._promote_best(path, metrics)
        self._trim_old()
        return path

    def maybe_save(
        self,
        step: int,
        payload_bytes: bytes,
        metrics: Dict[str, float] | None,
        save_steps: int,
    ) -> Path | None:
        if save_steps and step % save_steps == 0:
            return self.save_now(step, payload_bytes, metrics)
        return None

    @classmethod
    def find_resume(cls, directory: str | Path) -> str | None:
        d = Path(directory)
        link = d / "last"
        if link.is_symlink():
            try:
                return str((d / os.readlink(link)).resolve())
            except OSError:
                return None
        if link.exists():
            return str(link)
        ckpts = sorted(
            [p for p in d.glob("ckpt-*.pt")],
            key=lambda p: p.stat().st_mtime,
        )
        return str(ckpts[-1]) if ckpts else None
