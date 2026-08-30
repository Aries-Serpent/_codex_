"""
Repro Module

This module provides functionality for repro.

Usage:
    from utils.repro import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

import hashlib
import json
import logging
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

logger = logging.getLogger(__name__)
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
        json.dumps(
            {"version": version, "files": checksums, "name": dataset_name},
            indent=2,
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return checksums


def compute_file_hash(filepath: Path | str, algorithm: str = "sha256") -> str:
    """Compute cryptographic hash of file contents.

    Args:
        filepath: Path to file to hash
        algorithm: Hash algorithm (default: sha256)

    Returns:
        Hexadecimal digest of file contents
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")

    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def compute_directory_hash(
    dirpath: Path | str, extensions: list[str] | None = None, recursive: bool = True
) -> dict[str, str]:
    """Compute hashes for all files in directory.

    Args:
        dirpath: Path to directory
        extensions: Optional list of file extensions to include
        recursive: Whether to recurse into subdirectories

    Returns:
        Dictionary mapping relative file paths to their SHA256 hashes
    """
    dirpath = Path(dirpath)
    if not dirpath.exists():
        raise FileNotFoundError(f"Directory not found: {dirpath}")

    if not dirpath.is_dir():
        raise NotADirectoryError(f"Not a directory: {dirpath}")

    hashes = {}
    files = sorted(dirpath.rglob("*") if recursive else dirpath.glob("*"))

    for filepath in files:
        if not filepath.is_file():
            continue
        if extensions and filepath.suffix not in extensions:
            continue

        try:
            rel_path = filepath.relative_to(dirpath)
            hashes[str(rel_path)] = compute_file_hash(filepath)
        except (IOError, OSError):
            logger.warning("Exception occurred", exc_info=True)
            continue

    return hashes


class DatasetManifest:
    """Manages dataset integrity through hash manifests."""

    def __init__(self, dataset_path: Path | str):
        self.dataset_path = Path(dataset_path)
        self.manifest: dict[str, Any] = {
            "dataset_path": str(self.dataset_path.resolve()),
            "file_hashes": {},
            "total_files": 0,
            "total_size_bytes": 0,
            "generated_at": None,
            "manifest_version": "1.0",
        }

    def generate(
        self, extensions: list[str] | None = None, recursive: bool = True
    ) -> dict[str, Any]:
        """Generate manifest with file hashes."""
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset path not found: {self.dataset_path}")

        self.manifest["file_hashes"] = compute_directory_hash(
            self.dataset_path, extensions=extensions, recursive=recursive
        )
        self.manifest["total_files"] = len(self.manifest["file_hashes"])

        import time

        self.manifest["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        total_size = sum(
            (self.dataset_path / rel_path).stat().st_size
            for rel_path in self.manifest["file_hashes"]
            if (self.dataset_path / rel_path).exists()
        )
        self.manifest["total_size_bytes"] = total_size

        return self.manifest

    def save(self, output_path: Path | str) -> Path:
        """Save manifest to JSON file."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.manifest, f, indent=2, sort_keys=True)

        return output_path

    @classmethod
    def load(cls, manifest_path: Path | str) -> "DatasetManifest":
        """Load manifest from JSON file."""
        manifest_path = Path(manifest_path)
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest file not found: {manifest_path}")

        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict) or "dataset_path" not in data:
            raise ValueError("Invalid manifest format")

        instance = cls(data["dataset_path"])
        instance.manifest = data
        return instance

    def verify(self, manifest_path: Path | str | None = None) -> dict[str, list[str]]:
        """Verify current dataset against saved manifest."""
        if manifest_path is not None:
            saved_manifest = self.load(manifest_path).manifest
        else:
            saved_manifest = self.manifest

        current_hashes = compute_directory_hash(self.dataset_path)

        results: dict[str, list[str]] = {
            "missing": [],
            "modified": [],
            "added": [],
        }

        saved_files = set(saved_manifest.get("file_hashes", {}).keys())
        current_files = set(current_hashes.keys())

        results["missing"] = sorted(saved_files - current_files)
        results["added"] = sorted(current_files - saved_files)

        for file in sorted(saved_files & current_files):
            if saved_manifest["file_hashes"][file] != current_hashes[file]:
                results["modified"].append(file)

        return results

    def has_drift(self, manifest_path: Path | str | None = None) -> bool:
        """Check if dataset has drifted from manifest."""
        diff = self.verify(manifest_path)
        return bool(diff["missing"] or diff["modified"] or diff["added"])


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
    save_path: str | Path,
    *,
    include_locks: bool = True,
    lock_candidates: Sequence[str] = _LOCK_CANDIDATES,
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
    "DatasetManifest",
    "_dataset_version",
    "capture_environment",
    "compute_directory_hash",
    "compute_file_hash",
    "record_dataset_checksums",
    "restore_rng_state",
    "set_deterministic",
    "set_reproducible",
    "set_seed",
    "snapshot_rng_state",
]
