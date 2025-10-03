"""Offline-friendly remote connector implementations."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Iterable, List

from codex_ml.monitoring.health import record_health_event

from .base import Connector, ConnectorError, LocalConnector

__all__ = ["RemoteConnector"]

DEFAULT_CACHE_ROOT = Path.home() / ".codex" / "remote_cache"


class RemoteConnector(Connector):
    """Local emulation of remote storage with manifest tracking."""

    def __init__(
        self,
        endpoint: str | None = None,
        *,
        cache_root: str | Path | None = None,
        readonly: bool = False,
    ) -> None:
        self.endpoint = endpoint or "offline://remote"
        root = Path(cache_root or DEFAULT_CACHE_ROOT).expanduser()
        self._local = LocalConnector(root)
        self.readonly = readonly
        self._manifest_name = ".remote_manifest.json"
        self._manifest_path = self._local.root / self._manifest_name
        if not self._manifest_path.exists():
            self._write_manifest(files=[], created=True)
        record_health_event(
            "connectors.remote",
            "initialised",
            details={
                "endpoint": self.endpoint,
                "cache_root": str(self._local.root),
                "readonly": self.readonly,
            },
        )

    @property
    def cache_root(self) -> Path:
        """Return the backing cache directory."""

        return self._local.root

    async def list_files(self, path: str) -> List[str]:  # type: ignore[override]
        try:
            entries = await self._local.list_files(path)
        except ConnectorError as exc:
            record_health_event(
                "connectors.remote",
                "list_failed",
                details={"path": path, "error": str(exc)},
            )
            raise
        filtered = sorted(entry for entry in entries if entry != self._manifest_name)
        record_health_event(
            "connectors.remote",
            "listed",
            details={"path": path, "count": len(filtered)},
        )
        return filtered

    async def read_file(self, path: str) -> bytes:  # type: ignore[override]
        try:
            data = await self._local.read_file(path)
        except ConnectorError as exc:
            record_health_event(
                "connectors.remote",
                "read_failed",
                details={"path": path, "error": str(exc)},
            )
            raise
        record_health_event(
            "connectors.remote",
            "read",
            details={"path": path, "size": len(data)},
        )
        return data

    async def write_file(self, path: str, data: bytes) -> None:  # type: ignore[override]
        if self.readonly:
            record_health_event(
                "connectors.remote",
                "write_blocked",
                details={"path": path, "endpoint": self.endpoint},
            )
            raise ConnectorError(f"remote connector is read-only for endpoint {self.endpoint}")
        await self._local.write_file(path, data)
        files = [item for item in await self._local.list_files(".") if item != self._manifest_name]
        self._write_manifest(files=files)
        record_health_event(
            "connectors.remote",
            "write",
            details={"path": path, "size": len(data), "file_count": len(files)},
        )

    def _write_manifest(self, *, files: Iterable[str], created: bool = False) -> None:
        payload = {
            "endpoint": self.endpoint,
            "readonly": self.readonly,
            "files": sorted(str(item) for item in files),
        }
        timestamp_key = "created_at" if created else "updated_at"
        payload[timestamp_key] = datetime.utcnow().isoformat() + "Z"
        self._manifest_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
