import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Iterable, Mapping, Sequence
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


def _dataset_version(checksums: Mapping[str, str], *, name: str | None = None) -> str:
    """Return a deterministic dataset version hash from file checksums."""

    payload = {
        "name": name or "dataset",
        "files": {k: checksums[k] for k in sorted(checksums)},
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def record_dataset_checksums(
    files: Iterable[Path], out_path: Path, *, dataset_name: str | None = None
) -> dict[str, str]:
    """Write SHA256 checksums for ``files`` to ``out_path`` and a version sidecar."""

    checksums: dict[str, str] = {}
    for fp in files:
        p = Path(fp)
        if p.exists():
            checksums[p.name] = hashlib.sha256(p.read_bytes()).hexdigest()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(checksums, indent=2), encoding="utf-8")

    version = _dataset_version(checksums, name=dataset_name)
    sidecar = out_path.with_suffix(out_path.suffix + ".version.json")
    sidecar.write_text(
        json.dumps({"version": version, "files": checksums, "name": dataset_name}, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return checksums


def _copy_if_exists(path: Path, dest_dir: Path) -> Path | None:
    if not path.exists():
        return None
    dest_dir.mkdir(parents=True, exist_ok=True)
    target = dest_dir / path.name
    shutil.copy2(path, target)
    return target


_LOCK_CANDIDATES: Sequence[str] = (
    "requirements/lock.txt",
    "uv.lock",
    "requirements/lock-ml.txt",
    "requirements/lock-eval.txt",
)


def capture_environment(
    save_path: str | Path, *, include_locks: bool = True, lock_candidates: Sequence[str] = _LOCK_CANDIDATES
) -> None:
    """Capture Python packages, environment variables, and dependency locks."""

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

    if include_locks:
        locks_dir = target / "dependency_locks"
        for candidate in lock_candidates:
            _copy_if_exists(Path(candidate), locks_dir)


__all__ = [
    "capture_environment",
    "_dataset_version",
    "record_dataset_checksums",
    "restore_rng_state",
    "set_deterministic",
    "set_reproducible",
    "set_seed",
    "snapshot_rng_state",
]
