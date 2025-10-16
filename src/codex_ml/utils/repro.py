"""Reproducibility helpers for deterministic seeding and checkpoint resume."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

from . import seeding as _seeding
from .checkpointing import dump_rng_state, load_rng_state

set_reproducible = _seeding.set_reproducible
_set_deterministic = _seeding.set_deterministic


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


def snapshot_rng_state() -> dict[str, Any]:
    """Capture RNG state for Python, NumPy and PyTorch."""

    return dump_rng_state()


def restore_rng_state(state: Mapping[str, Any]) -> None:
    """Restore RNG state previously captured with :func:`snapshot_rng_state`."""

    load_rng_state(dict(state), prefer_resume=False)


def set_deterministic(flag: bool) -> None:
    """Toggle PyTorch deterministic algorithms without re-seeding."""

    _set_deterministic(flag)


def record_dataset_checksums(files: Iterable[Path], out_path: Path) -> dict[str, str]:
    """Write SHA256 checksums for ``files`` to ``out_path``."""

    checksums: dict[str, str] = {}
    for fp in files:
        p = Path(fp)
        if p.exists():
            checksums[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(checksums, indent=2), encoding="utf-8")
    return checksums


def capture_environment(save_path: str | Path) -> None:
    """Capture Python packages and environment variables for reproducibility."""

    target = Path(save_path)
    target.mkdir(parents=True, exist_ok=True)

    pip_freeze = subprocess.check_output([sys.executable, "-m", "pip", "freeze"], text=True)
    (target / "pip_freeze.txt").write_text(pip_freeze, encoding="utf-8")

    secret_pattern = re.compile(r"(token|key|secret|password|pwd|passphrase)", re.IGNORECASE)
    redacted_env = {
        key: ("<redacted>" if secret_pattern.search(key) else value)
        for key, value in os.environ.items()
    }
    (target / "env_vars.json").write_text(json.dumps(redacted_env, indent=2), encoding="utf-8")


__all__ = [
    "capture_environment",
    "record_dataset_checksums",
    "restore_rng_state",
    "set_deterministic",
    "set_reproducible",
    "set_seed",
    "snapshot_rng_state",
]
