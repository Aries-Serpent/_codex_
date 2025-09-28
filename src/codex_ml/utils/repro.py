"""Reproducibility helpers for deterministic seeding and checkpoint resume."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping

from .checkpointing import dump_rng_state, load_rng_state
from .seeding import set_deterministic as _set_deterministic
from .seeding import set_reproducible


def set_seed(seed: int, *, deterministic: bool | None = None) -> None:
    """Seed Python, NumPy and PyTorch RNGs.

    Parameters
    ----------
    seed:
        Seed applied across libraries.
    deterministic:
        When provided, toggles PyTorch deterministic algorithms via
        :func:`torch.use_deterministic_algorithms`. Defaults to ``True`` to
        preserve historical behaviour.
    """

    if deterministic is None:
        set_reproducible(seed)
    else:
        set_reproducible(seed, deterministic=deterministic)


def snapshot_rng_state() -> Dict[str, Any]:
    """Capture RNG state for Python, NumPy and PyTorch."""

    return dump_rng_state()


def restore_rng_state(state: Mapping[str, Any]) -> None:
    """Restore RNG state previously captured with :func:`snapshot_rng_state`."""

    load_rng_state(dict(state))


def set_deterministic(flag: bool) -> None:
    """Toggle PyTorch deterministic algorithms without re-seeding."""

    _set_deterministic(flag)


def record_dataset_checksums(files: Iterable[Path], out_path: Path) -> Dict[str, str]:
    """Write SHA256 checksums for ``files`` to ``out_path``."""

    checksums: Dict[str, str] = {}
    for fp in files:
        p = Path(fp)
        if p.exists():
            checksums[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(checksums, indent=2), encoding="utf-8")
    return checksums


__all__ = [
    "set_reproducible",
    "set_seed",
    "set_deterministic",
    "snapshot_rng_state",
    "restore_rng_state",
    "record_dataset_checksums",
]
