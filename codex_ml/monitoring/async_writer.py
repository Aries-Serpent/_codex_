"""Asynchronous file writer shim."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping

__all__ = ["AsyncLogFile"]


class AsyncLogFile:
    """Synchronous but API-compatible log writer used in tests."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, record: Mapping[str, object]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(dict(record), ensure_ascii=False) + "\n")

    def close(self) -> None:  # pragma: no cover - trivial
        pass
