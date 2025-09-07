from __future__ import annotations

from typing import List


class Connector:
    async def list_files(self, path: str) -> List[str]:  # pragma: no cover - interface
        raise NotImplementedError

    async def read_file(self, path: str) -> bytes:  # pragma: no cover - interface
        raise NotImplementedError

    async def write_file(self, path: str, data: bytes) -> None:  # pragma: no cover - interface
        raise NotImplementedError
