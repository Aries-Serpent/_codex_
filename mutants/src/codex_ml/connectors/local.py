"""
Local Module

This module provides functionality for local.

Usage:
    from connectors.local import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from .base import Connector


class LocalConnector(Connector):
    async def list_files(self, path: str) -> list[str]:
        return await asyncio.to_thread(lambda: [p.name for p in Path(path).iterdir()])

    async def read_file(self, path: str) -> bytes:
        return await asyncio.to_thread(Path(path).read_bytes)

    async def write_file(self, path: str, data: bytes) -> None:
        await asyncio.to_thread(Path(path).write_bytes, data)
