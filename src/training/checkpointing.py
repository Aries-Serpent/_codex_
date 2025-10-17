from __future__ import annotations

import inspect
import math
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:  # pragma: no cover - torch is optional in minimal environments
    import torch
except Exception:  # pragma: no cover - gracefully degrade when torch missing
    torch = None  # type: ignore[assignment]


def _torch_supports_weights_only() -> bool:
    if torch is None:
        return False
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        return False
    try:
        signature = inspect.signature(load_fn)
    except (TypeError, ValueError):  # pragma: no cover - torch may bypass inspect
        return False
    return "weights_only" in signature.parameters


_TORCH_SUPPORTS_WEIGHTS_ONLY = _torch_supports_weights_only()


def _torch_rng_get_state() -> Any:
    if torch is None:
        raise RuntimeError("torch is required to capture RNG state")
    random_mod = getattr(torch, "random", None)
    getter = getattr(random_mod, "get_rng_state", None) if random_mod is not None else None
    if callable(getter):
        return getter()
    legacy_getter = getattr(torch, "get_rng_state", None)
    if callable(legacy_getter):
        return legacy_getter()
    raise RuntimeError("Current torch build lacks RNG state APIs")


def _torch_rng_set_state(state: Any) -> None:
    if torch is None:
        raise RuntimeError("torch is required to restore RNG state")
    random_mod = getattr(torch, "random", None)
    setter = getattr(random_mod, "set_rng_state", None) if random_mod is not None else None
    if callable(setter):
        setter(state)
        return
    legacy_setter = getattr(torch, "set_rng_state", None)
    if callable(legacy_setter):
        legacy_setter(state)
        return
    raise RuntimeError("Current torch build lacks RNG state APIs")


def _torch_load(path: str, *, map_location: str | torch.device | None) -> Any:
    if torch is None:
        raise RuntimeError("torch is required to load checkpoints")
    load_fn = getattr(torch, "load", None)
    if load_fn is None:
        raise RuntimeError("Current torch build does not expose torch.load")
    kwargs: dict[str, Any] = {}
    if map_location is not None:
        kwargs["map_location"] = map_location
    if _TORCH_SUPPORTS_WEIGHTS_ONLY:
        kwargs["weights_only"] = False
    try:
        return load_fn(path, **kwargs)
    except TypeError as exc:
        if _TORCH_SUPPORTS_WEIGHTS_ONLY and "weights_only" in str(exc):
            kwargs.pop("weights_only", None)
            return load_fn(path, **kwargs)
        raise


@dataclass
class RNGState:
    """Container capturing CPU and (optionally) CUDA RNG states."""

    cpu: torch.Tensor | None = None
    cuda_all: list[torch.Tensor] | None = None


def snapshot_rng_state() -> RNGState:
    """Snapshot the current RNG state for CPU and CUDA generators."""

    if torch is None:
        return RNGState()
    cpu_state = _torch_rng_get_state()
    cuda_state = None
    if hasattr(torch, "cuda") and torch.cuda.is_available():
        cuda_state = torch.cuda.get_rng_state_all()  # type: ignore[attr-defined]
    return RNGState(cpu=cpu_state, cuda_all=cuda_state)


def restore_rng_state(state: RNGState) -> None:
    """Restore RNG state captured by :func:`snapshot_rng_state`."""

    if torch is None:
        return
    if state.cpu is not None:
        _torch_rng_set_state(state.cpu)
    if state.cuda_all is not None and hasattr(torch, "cuda") and torch.cuda.is_available():
        with suppress(Exception):  # pragma: no cover - best effort restoration
            torch.cuda.set_rng_state_all(state.cuda_all)  # type: ignore[attr-defined]


def _score_key(metric: float | None, epoch: int, mode: str) -> tuple[int, float, int]:
    """Return a sorting key where better checkpoints compare lower."""

    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    is_nan = 1
    if metric is not None and not (isinstance(metric, float) and math.isnan(metric)):
        is_nan = 0
    value: float
    if metric is None or (isinstance(metric, float) and math.isnan(metric)):
        value = math.inf
    else:
        value = float(metric)
    best_scalar = value if mode == "min" else -value
    return (is_nan, best_scalar, -int(epoch))


def _parse_epoch_metric(path: Path) -> tuple[int | None, float | None]:
    """Extract the epoch and metric components from checkpoint filenames."""

    name = path.stem
    if not name.startswith("epoch") or "-metric" not in name:
        return None, None
    try:
        prefix, metric_str = name.split("-metric", 1)
        epoch = int(prefix.replace("epoch", ""))
        metric = float(metric_str)
        return epoch, metric
    except Exception:
        return None, None


def _best_k_retention(dirpath: Path, keep_best_k: int, mode: str) -> None:
    """Keep only the top-k checkpoints according to metric ordering."""

    checkpoints = list(dirpath.glob("epoch*-metric*.pt"))
    scored: list[tuple[tuple[int, float, int], Path]] = []
    for path in checkpoints:
        epoch, metric = _parse_epoch_metric(path)
        if epoch is None:
            continue
        scored.append((_score_key(metric, epoch, mode), path))
    if not scored or len(scored) <= keep_best_k:
        return
    scored_sorted = sorted(scored, key=lambda item: item[0])
    for _, path in scored_sorted[keep_best_k:]:
        with suppress(OSError):
            path.unlink(missing_ok=True)


def save_checkpoint(
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    *,
    epoch: int,
    val_metric: float,
    out_dir: str | Path,
    mode: str = "min",
    keep_best_k: int = 3,
    extra: dict[str, Any] | None = None,
) -> Path:
    """Serialise model, optimizer, and RNG state to disk, retaining top-k files."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    if mode not in {"min", "max"}:
        raise ValueError("mode must be 'min' or 'max'")
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    rng_state = snapshot_rng_state()
    filename = out_path / f"epoch{epoch}-metric{val_metric:.6f}.pt"
    payload: dict[str, Any] = {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "val_metric": float(val_metric),
        "epoch": int(epoch),
        "rng_cpu": rng_state.cpu,
        "rng_cuda_all": rng_state.cuda_all,
    }
    if extra:
        payload.update(extra)
    torch.save(payload, filename)
    _best_k_retention(out_path, keep_best_k=keep_best_k, mode=mode)
    return filename


def load_checkpoint(
    path: str | Path,
    model: torch.nn.Module,
    optimizer: torch.optim.Optimizer | None = None,
    *,
    strict: bool = True,
    map_location: str | torch.device | None = None,
    restore_rng: bool = True,
) -> tuple[int, float]:
    """Load a checkpoint and optionally restore optimizer and RNG state."""

    if torch is None:
        raise RuntimeError("torch is required for checkpointing")
    location = map_location or (
        "cpu" if not getattr(torch, "cuda", None) or not torch.cuda.is_available() else "cuda"
    )
    payload = _torch_load(str(path), map_location=location)
    model.load_state_dict(payload["model_state"], strict=strict)
    if optimizer is not None and "optimizer_state" in payload:
        optimizer.load_state_dict(payload["optimizer_state"])
    if restore_rng:
        restore_rng_state(
            RNGState(cpu=payload.get("rng_cpu"), cuda_all=payload.get("rng_cuda_all"))
        )
    return int(payload.get("epoch", 0)), float(payload.get("val_metric", float("nan")))


__all__ = [
    "RNGState",
    "snapshot_rng_state",
    "restore_rng_state",
    "save_checkpoint",
    "load_checkpoint",
]
