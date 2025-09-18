"""Connector interfaces used by operational tooling.

The original codebase exposed an empty stub that raised
``NotImplementedError`` at runtime which made even smoke tests fail once the
module was imported.  The repository relies on a light-weight connector to
read and write artefacts during local development, so this module now ships a
fully working implementation that is deterministic and easy to exercise in
tests.

Two layers are provided:

``Connector``
    An abstract base class that documents the asynchronous contract.

``LocalConnector``
    A concrete implementation backed by the local filesystem.  It includes
    validation to prevent directory traversal, uses ``asyncio.to_thread`` to
    offload blocking I/O, and emits helpful error messages.

Both classes are intentionally dependency free to keep offline CI viable.
"""

from __future__ import annotations

import asyncio
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

__all__ = ["Connector", "LocalConnector", "ConnectorError"]


class ConnectorError(RuntimeError):
    """Raised when a connector operation fails.

    The exception message is geared towards end users so the error can be
    surfaced directly in CLI output without additional formatting.
    """


class Connector(ABC):
    """Abstract asynchronous storage connector."""

    @abstractmethod
    async def list_files(self, path: str) -> List[str]:
        """Return a sorted list of files under ``path``.

        Implementations MUST return paths relative to the connector root to
        keep consumers agnostic about the backing storage.  Errors should be
        raised as :class:`ConnectorError` with descriptive messages.
        """

    @abstractmethod
    async def read_file(self, path: str) -> bytes:
        """Read a single file from storage."""

    @abstractmethod
    async def write_file(self, path: str, data: bytes) -> None:
        """Persist ``data`` at ``path`` overwriting any existing file."""


@dataclass(slots=True)
class LocalConnector(Connector):
    """Filesystem backed connector used in local smoke tests.

    Parameters
    ----------
    root:
        Base directory that stores all artefacts.  The connector guarantees
        that every requested path stays within this directory; attempts to
        escape via ``..`` components raise :class:`ConnectorError`.

    Attributes
    ----------
    root: :class:`pathlib.Path`
        Normalised absolute path used for all operations.

    The implementation relies on ``asyncio.to_thread`` so it can be used in
    asynchronous FastAPI handlers without blocking the event loop.  Each
    public method validates inputs eagerly to catch mistakes early.
    """

    root: Path

    def __post_init__(self) -> None:
        self.root = Path(self.root).expanduser().resolve()
        if not self.root.exists():
            self.root.mkdir(parents=True, exist_ok=True)

    # -- Helper utilities -------------------------------------------------
    def _resolve(self, relative_path: str) -> Path:
        if not relative_path:
            raise ConnectorError("path may not be empty")
        clean_parts: Iterable[str] = (
            part for part in Path(relative_path).parts if part not in {"", "."}
        )
        candidate = (self.root.joinpath(*clean_parts)).resolve()
        if not os.path.commonpath([self.root, candidate]) == str(self.root):
            raise ConnectorError(f"refusing to access path outside root: {relative_path}")
        return candidate

    async def list_files(self, path: str) -> List[str]:
        target = self._resolve(path)
        if not target.exists():
            return []

        def _scan() -> List[str]:
            items: List[str] = []
            if target.is_file():
                rel = target.relative_to(self.root)
                items.append(str(rel))
                return items
            for item in sorted(target.rglob("*")):
                if item.is_file():
                    items.append(str(item.relative_to(self.root)))
            return items

        return await asyncio.to_thread(_scan)

    async def read_file(self, path: str) -> bytes:
        target = self._resolve(path)
        if not target.exists() or not target.is_file():
            raise ConnectorError(f"file does not exist: {path}")

        def _read() -> bytes:
            return target.read_bytes()

        return await asyncio.to_thread(_read)

    async def write_file(self, path: str, data: bytes) -> None:
        target = self._resolve(path)
        target.parent.mkdir(parents=True, exist_ok=True)

        def _write() -> None:
            target.write_bytes(data)

        await asyncio.to_thread(_write)
