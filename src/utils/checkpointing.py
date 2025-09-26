"""Lightweight checkpointing utilities with RNG tracking.

This module provides a pared down version of the checkpoint manager used in
``codex_ml``.  It focuses on reproducibility by capturing and restoring random
number generator (RNG) state across Python, NumPy and PyTorch (when
available).  Checkpoints are stored under ``<root>/epoch-<n>`` with companion
metadata files:

``meta.json``
    Epoch number and metric dictionary supplied by the caller.

``rng.json``
    Captured RNG state to allow deterministic resumption.

The :class:`CheckpointManager` keeps ``keep_last`` most recent checkpoints and
``keep_best`` snapshots sorted by the ``val_loss`` metric (lower is better).

The implementation intentionally avoids heavyweight dependencies; if NumPy or
PyTorch are missing the corresponding RNG sections are skipped.
"""

from __future__ import annotations

import inspect
import json
import random
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, cast

if TYPE_CHECKING:
    from typing import Protocol

    class _TorchModule(Protocol):
        def load(self, *args: Any, **kwargs: Any) -> Any: ...

        random: Any
        cuda: Any

        def tensor(self, *args: Any, **kwargs: Any) -> Any: ...

        uint8: Any

        def manual_seed(self, *args: Any, **kwargs: Any) -> Any: ...


try:  # pragma: no cover - optional numpy
    import numpy as np

    NUMPY_AVAILABLE = True
except Exception:  # pragma: no cover
    NUMPY_AVAILABLE = False

_imported_torch: Any | None

try:  # pragma: no cover - optional torch
    import torch as _imported_torch
except Exception:  # pragma: no cover
    _imported_torch = None

torch = cast("_TorchModule | None", _imported_torch)
TORCH_AVAILABLE = torch is not None


def load_checkpoint(
    path: str | Path,
    *,
    map_location: str | None = "cpu",
    safe: bool = True,
    **kwargs,
) -> Any:
    """Load a checkpoint with safer defaults.

    Args:
        path: Filesystem path to the checkpoint file.
        map_location: Where to map tensors when loading (defaults to CPU for determinism).
        safe: When ``True`` (default) require ``torch.load`` to support ``weights_only`` and
            use it to avoid arbitrary object deserialisation. Set to ``False`` only for
            trusted checkpoints.
        **kwargs: Additional keyword arguments forwarded to ``torch.load``.

    Raises:
        RuntimeError: If ``safe=True`` but the installed torch version lacks ``weights_only``.
    """

    if torch is None:
        raise RuntimeError("PyTorch is required to load checkpoints")
    assert torch is not None

    if safe:
        try:
            return torch.load(  # nosec B614 - restricted to tensor payloads via weights_only
                path, map_location=map_location, weights_only=True, **kwargs
            )
        except TypeError as exc:
            raise RuntimeError(
                "Installed torch lacks `weights_only` support; cannot safely load untrusted checkpoint"
            ) from exc

    if "weights_only" not in kwargs:
        try:
            load_sig = inspect.signature(torch.load)
        except (TypeError, ValueError):  # pragma: no cover - PyTorch may bypass inspect
            load_sig = None
        if load_sig and "weights_only" in load_sig.parameters:
            kwargs = dict(kwargs)
            kwargs["weights_only"] = False

    return torch.load(path, map_location=map_location, **kwargs)  # nosec B614 - trusted path only


def _dump_rng() -> Dict[str, Any]:
    """Capture RNG state from available libraries in a JSON friendly form."""
    py_state = random.getstate()
    state: Dict[str, Any] = {"python": [py_state[0], list(py_state[1]), py_state[2]]}
    if NUMPY_AVAILABLE:
        np_state = np.random.get_state()
        state["numpy"] = [
            np_state[0],
            np_state[1].tolist(),
            np_state[2],
            np_state[3],
            np_state[4],
        ]
    if torch is not None:
        state["torch"] = {"cpu": torch.random.get_rng_state().tolist()}
        if torch.cuda.is_available():  # pragma: no cover - cuda optional
            state["torch"]["cuda"] = [s.tolist() for s in torch.cuda.get_rng_state_all()]
    return state


def _load_rng(state: Dict[str, Any]) -> None:
    """Restore RNG state from :func:`_dump_rng`."""
    if "python" in state:
        py = state["python"]
        random.setstate((py[0], tuple(py[1]), py[2]))
    if NUMPY_AVAILABLE and "numpy" in state:
        np_state = state["numpy"]
        np.random.set_state(
            (
                np_state[0],
                np.array(np_state[1], dtype=np.uint32),
                np_state[2],
                np_state[3],
                np_state[4],
            )
        )
    if torch is not None and "torch" in state:
        torch.random.set_rng_state(torch.tensor(state["torch"]["cpu"], dtype=torch.uint8))
        if "cuda" in state["torch"] and torch.cuda.is_available():  # pragma: no cover
            torch.cuda.set_rng_state_all(
                [torch.tensor(s, dtype=torch.uint8) for s in state["torch"]["cuda"]]
            )


def dump_rng_state() -> Dict[str, Any]:
    """Public helper to snapshot RNG state."""

    return _dump_rng()


def load_rng_state(state: Dict[str, Any]) -> None:
    """Restore RNG state previously captured with :func:`dump_rng_state`."""

    _load_rng(state)


def set_seed(seed: int) -> None:
    """Seed all available RNG libraries with ``seed``."""

    random.seed(seed)
    if NUMPY_AVAILABLE:
        np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():  # pragma: no cover - cuda optional
            torch.cuda.manual_seed_all(seed)


class CheckpointManager:
    """Manage checkpoint directories with retention policies."""

    def __init__(self, root: Path, keep_last: int = 5, keep_best: int = 1) -> None:
        self.root = Path(root)
        self.keep_last = int(keep_last)
        self.keep_best = int(keep_best)
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    def save(self, epoch: int, *, metrics: Optional[Dict[str, Any]] = None) -> Path:
        """Save a checkpoint directory and apply retention policies."""

        ep_dir = self.root / f"epoch-{epoch}"
        ep_dir.mkdir(parents=True, exist_ok=True)
        (ep_dir / "meta.json").write_text(
            json.dumps({"epoch": epoch, "metrics": metrics or {}}, indent=2),
            encoding="utf-8",
        )
        (ep_dir / "rng.json").write_text(json.dumps(_dump_rng(), indent=2), encoding="utf-8")

        if metrics:
            best_file = self.root / "best.json"
            items = []
            if best_file.exists():
                items = json.loads(best_file.read_text(encoding="utf-8")).get("items", [])
            entry = {"epoch": epoch, "metrics": metrics, "path": str(ep_dir)}
            items.append(entry)

            def keyfn(x: Dict[str, Any]) -> float:
                return x.get("metrics", {}).get("val_loss", float("inf"))

            items.sort(key=keyfn)
            best_file.write_text(
                json.dumps({"items": items[: max(1, self.keep_best)]}, indent=2),
                encoding="utf-8",
            )

        self.apply_retention()
        return ep_dir

    # ------------------------------------------------------------------
    def apply_retention(self) -> None:
        entries = [p for p in self.root.glob("epoch-*") if p.is_dir()]
        entries.sort(key=lambda p: int(p.name.split("-")[-1]), reverse=True)
        keep = {e.name for e in entries[: max(1, self.keep_last)]}
        best_file = self.root / "best.json"
        if best_file.exists():
            data = json.loads(best_file.read_text(encoding="utf-8")).get("items", [])
            for item in data:
                keep.add(Path(item["path"]).name)
        for e in entries:
            if e.name not in keep:
                shutil.rmtree(e, ignore_errors=True)


__all__ = [
    "CheckpointManager",
    "dump_rng_state",
    "load_checkpoint",
    "load_rng_state",
    "set_seed",
]
