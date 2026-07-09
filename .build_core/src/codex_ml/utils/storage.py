"""
Storage Module

This module provides functionality for storage.

Usage:
    from utils.storage import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Protocol, runtime_checkable  # noqa: E402


@runtime_checkable
class StorageProvider(Protocol):
    """Protocol for checkpoint storage adapters."""

    def upload_directory(self, local_path: Path, remote_path: str) -> None:
        """Upload ``local_path`` into ``remote_path``."""

    def download_directory(self, remote_path: str, local_path: Path) -> None:
        """Download ``remote_path`` into ``local_path``."""

    def iter_checkpoints(self, prefix: str) -> Iterable[str]:
        """Yield remote checkpoint directories under ``prefix``."""


@dataclass(slots=True)
class FSSpecStorage(StorageProvider):
    """Simple :mod:`fsspec`-backed checkpoint synchronisation helper."""

    base_url: str
    create: bool = True

    def __post_init__(self) -> None:
        try:
            import fsspec
        except (IOError, OSError) as exc:  # pragma: no cover - optional dependency missing
            raise RuntimeError("fsspec is required to use the FSSpecStorage backend") from exc

        fs, root_path = fsspec.core.url_to_fs(self.base_url)
        self._fs = fs
        self._root_path = root_path.rstrip("/")
        if self.create and not self._fs.exists(
            self._root_path
        ):  # pragma: no cover - memfs creates eagerly
            self._fs.makedirs(self._root_path, exist_ok=True)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _join(self, fragment: str | Path | None = None) -> str:
        base = self._root_path
        if not fragment:
            return base
        frag = str(fragment).lstrip("/")
        if not frag:
            return base
        if not base:
            return frag
        return f"{base}/{frag}"

    def _iter_local_files(self, root: Path) -> Iterator[Path]:
        for item in sorted(root.rglob("*")):
            if item.is_file():
                yield item

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------
    def upload_directory(self, local_path: Path, remote_path: str) -> None:
        for file_path in self._iter_local_files(local_path):
            rel = file_path.relative_to(local_path).as_posix()
            remote_file = self._join(f"{remote_path.rstrip('/')}/{rel}" if rel else remote_path)
            parent = remote_file.rsplit("/", 1)[0] if "/" in remote_file else remote_file
            self._fs.makedirs(parent, exist_ok=True)
            with file_path.open("rb") as src, self._fs.open(remote_file, "wb") as dst:
                dst.write(src.read())

    def download_directory(self, remote_path: str, local_path: Path) -> None:
        target_root = Path(local_path)
        target_root.mkdir(parents=True, exist_ok=True)
        base = self._join(remote_path)
        if not self._fs.exists(base):
            raise FileNotFoundError(f"Remote checkpoint path not found: {remote_path}")
        for entry in self._fs.find(base):
            if self._fs.isdir(entry):
                continue
            rel = entry[len(base) :].lstrip("/")
            destination = target_root / rel
            destination.parent.mkdir(parents=True, exist_ok=True)
            with self._fs.open(entry, "rb") as src, destination.open("wb") as dst:
                dst.write(src.read())

    def iter_checkpoints(self, prefix: str) -> Iterable[str]:
        base = self._join(prefix)
        if not self._fs.exists(base):
            return []
        entries: list[str] = []
        for entry in self._fs.listdir(base, detail=True):
            if isinstance(entry, tuple):
                path, info = entry
            else:
                path = entry.get("name", "")
                info = entry
            if not info.get("type", "").startswith("d"):
                continue
            # identify checkpoint directories by the presence of state files
            state_pt = f"{path}/state.pt"
            state_pkl = f"{path}/state.pkl"
            if self._fs.exists(state_pt) or self._fs.exists(state_pkl):
                rel = path
                if rel.startswith(self._root_path):
                    rel = rel[len(self._root_path) :].lstrip("/")
                entries.append(rel or Path(path).name)
        entries.sort()
        return entries


__all__ = ["FSSpecStorage", "StorageProvider"]
