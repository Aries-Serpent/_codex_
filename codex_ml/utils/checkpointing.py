"""Minimal checkpointing helpers used by the training scaffold."""

from __future__ import annotations

import io
import json
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, MutableMapping, Optional

try:  # pragma: no cover - torch is an optional dependency for tests
    import torch
except Exception as exc:  # pragma: no cover - defensive fallback
    torch = None  # type: ignore[assignment]

try:  # pragma: no cover - numpy optional
    import numpy as np
except Exception:  # pragma: no cover - defensive fallback
    np = None  # type: ignore[assignment]

__all__ = [
    "CheckpointManager",
    "build_payload_bytes",
    "dump_rng_state",
    "load_payload",
    "load_rng_state",
    "load_training_checkpoint",
    "save_checkpoint",
    "set_seed",
]


def set_seed(seed: int, output_dir: str | Path | None = None, *, deterministic: bool = False) -> None:
    """Initialise Python, NumPy and Torch RNGs with ``seed``."""

    random.seed(seed)
    if np is not None:
        try:
            np.random.seed(seed)  # type: ignore[arg-type]
        except Exception:  # pragma: no cover - defensive
            pass
    if torch is not None:
        try:
            torch.manual_seed(seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed_all(seed)
            if deterministic and getattr(torch, "backends", None) is not None:
                cudnn = torch.backends.cudnn  # type: ignore[attr-defined]
                cudnn.deterministic = True
                cudnn.benchmark = False
        except Exception:  # pragma: no cover - defensive
            pass
    if output_dir is not None:
        Path(output_dir).mkdir(parents=True, exist_ok=True)


def dump_rng_state() -> dict[str, Any]:
    """Capture the current RNG state of Python, NumPy and Torch if available."""

    state: dict[str, Any] = {"python": random.getstate()}
    if np is not None:
        try:
            state["numpy"] = np.random.get_state()  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - defensive
            pass
    if torch is not None:
        torch_state: dict[str, Any] = {}
        try:
            torch_state["cpu"] = torch.random.get_rng_state()
        except Exception:
            pass
        try:
            if torch.cuda.is_available():
                torch_state["cuda"] = [s.cpu() for s in torch.cuda.get_rng_state_all()]
        except Exception:  # pragma: no cover - cuda optional
            pass
        if torch_state:
            state["torch"] = torch_state
    return state


def load_rng_state(state: Mapping[str, Any]) -> None:
    """Restore RNG state captured via :func:`dump_rng_state`."""

    try:
        random.setstate(state.get("python"))  # type: ignore[arg-type]
    except Exception:  # pragma: no cover - defensive
        pass
    if np is not None and "numpy" in state:
        try:
            np.random.set_state(state["numpy"])  # type: ignore[arg-type]
        except Exception:  # pragma: no cover - defensive
            pass
    if torch is not None and "torch" in state:
        torch_state = state["torch"]
        try:
            cpu_state = torch_state.get("cpu")
            if cpu_state is not None:
                torch.random.set_rng_state(cpu_state)
        except Exception:
            pass
        try:
            cuda_state = torch_state.get("cuda")
            if cuda_state is not None and torch.cuda.is_available():
                torch.cuda.set_rng_state_all(cuda_state)
        except Exception:  # pragma: no cover - cuda optional
            pass


def build_payload_bytes(
    model: Any,
    optimizer: Any | None = None,
    scheduler: Any | None = None,
    scaler: Any | None = None,
    *,
    rng_state: bool = False,
) -> bytes:
    """Serialise model and optimiser state into a ``torch.save`` payload."""

    if torch is None:  # pragma: no cover - torch unavailable
        raise RuntimeError("torch is required to build checkpoint payloads")

    payload: dict[str, Any] = {
        "model": model.state_dict() if model is not None else None,
        "optimizer": optimizer.state_dict() if optimizer is not None else None,
        "scheduler": scheduler.state_dict() if hasattr(scheduler, "state_dict") else None,
        "scaler": scaler.state_dict() if hasattr(scaler, "state_dict") else None,
    }
    if rng_state:
        payload["rng_state"] = dump_rng_state()
    buffer = io.BytesIO()
    torch.save(payload, buffer)
    return buffer.getvalue()


def save_checkpoint(
    path: str | Path,
    model: Any,
    optimizer: Any | None,
    scheduler: Any | None,
    epoch: int,
    extra: Optional[Mapping[str, Any]] = None,
    scaler: Any | None = None,
) -> Path:
    """Persist a checkpoint dictionary to ``path`` and return the resolved path."""

    if torch is None:  # pragma: no cover - torch unavailable
        raise RuntimeError("torch is required to save checkpoints")

    payload: dict[str, Any] = {
        "epoch": int(epoch),
        "model": model.state_dict() if model is not None else None,
        "optimizer": optimizer.state_dict() if optimizer is not None else None,
        "scheduler": scheduler.state_dict() if hasattr(scheduler, "state_dict") else None,
        "extra": dict(extra or {}),
    }
    if scaler is not None and hasattr(scaler, "state_dict"):
        payload["scaler"] = scaler.state_dict()
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, target)
    return target


def load_training_checkpoint(
    path: str | Path,
    model: Any | None = None,
    optimizer: Any | None = None,
    scheduler: Any | None = None,
    scaler: Any | None = None,
    *,
    map_location: str | torch.device | None = None,
) -> MutableMapping[str, Any]:
    """Load a checkpoint produced by :func:`save_checkpoint`."""

    if torch is None:  # pragma: no cover - torch unavailable
        raise RuntimeError("torch is required to load checkpoints")

    target = Path(path)
    data = torch.load(target, map_location=map_location)
    if model is not None and data.get("model"):
        model.load_state_dict(data["model"])
    if optimizer is not None and data.get("optimizer"):
        optimizer.load_state_dict(data["optimizer"])
    if scheduler is not None and data.get("scheduler") and hasattr(scheduler, "load_state_dict"):
        scheduler.load_state_dict(data["scheduler"])
    if scaler is not None and data.get("scaler") and hasattr(scaler, "load_state_dict"):
        scaler.load_state_dict(data["scaler"])
    return data


def load_payload(
    path: str | Path,
    model: Any | None,
    optimizer: Any | None,
    scheduler: Any | None,
    scaler: Any | None = None,
    *,
    map_location: str | torch.device | None = None,
) -> None:
    """Load raw payload bytes into the supplied training objects."""

    load_training_checkpoint(
        path,
        model=model,
        optimizer=optimizer,
        scheduler=scheduler,
        scaler=scaler,
        map_location=map_location,
    )


@dataclass
class CheckpointRecord:
    step: int
    path: Path
    metric: float | None = None


class CheckpointManager:
    """Keep track of periodic checkpoints and prune old files."""

    def __init__(
        self,
        root: str | Path,
        *,
        keep_last: int = 5,
        metric: str | None = None,
        mode: str = "min",
    ) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.keep_last = max(1, int(keep_last))
        self.metric = metric
        self.mode = mode

    # ------------------------------------------------------------------
    def maybe_save(
        self,
        step: int,
        payload: bytes,
        logs: Mapping[str, float] | None,
        save_steps: int,
    ) -> Optional[Path]:
        """Persist ``payload`` when ``step`` aligns with ``save_steps``."""

        if save_steps and step % int(save_steps) != 0:
            return None
        target = self.root / f"ckpt-{int(step):08d}.pt"
        target.write_bytes(payload)
        self._prune_old()
        return target

    # ------------------------------------------------------------------
    def _prune_old(self) -> None:
        checkpoints = sorted(self.root.glob("ckpt-*.pt"))
        if len(checkpoints) <= self.keep_last:
            return
        for path in checkpoints[:-self.keep_last]:
            try:
                path.unlink()
            except Exception:  # pragma: no cover - best effort
                continue

    # ------------------------------------------------------------------
    @staticmethod
    def find_resume(root: str | Path) -> Optional[str]:
        """Return the most recent checkpoint in ``root`` if one exists."""

        root_path = Path(root)
        candidates = sorted(root_path.glob("ckpt-*.pt"))
        if not candidates:
            return None
        return str(candidates[-1])
