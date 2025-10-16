"""Dataset manifest helpers used by the modular training stack."""

from __future__ import annotations

import hashlib
import json
import os
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, cast

from codex_ml.utils.atomic_io import safe_write_text


def _sha256_file(path: Path, chunk_size: int = 1 << 16) -> str:
    """Compute the SHA-256 digest for ``path`` in a streaming fashion."""

    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _default_created_at() -> int:
    """Return a reproducible timestamp honouring ``SOURCE_DATE_EPOCH``."""

    override = os.environ.get("SOURCE_DATE_EPOCH")
    if override:
        try:
            return int(float(override))
        except ValueError:
            pass
    return int(time.time())


@dataclass(slots=True)
class Shard:
    path: str
    size: int
    sha256: str


@dataclass(slots=True)
class DatasetManifest:
    schema_version: str = "1.0"
    created_at: int = field(default_factory=_default_created_at)
    dataset_id: str | None = None
    shards: list[Shard] = field(default_factory=list)

    @staticmethod
    def build(root: str | Path, shard_paths: list[str]) -> DatasetManifest:
        """Construct a manifest for ``shard_paths`` relative to ``root``."""

        base = Path(root)
        entries: list[Shard] = []
        for relative in shard_paths:
            file_path = base / relative
            stat = file_path.stat()
            entries.append(
                Shard(
                    path=relative,
                    size=stat.st_size,
                    sha256=_sha256_file(file_path),
                )
            )
        return DatasetManifest(shards=entries)

    def to_json(self) -> str:
        """Serialise the manifest to a formatted JSON string."""

        return json.dumps(
            {
                "schema_version": self.schema_version,
                "created_at": self.created_at,
                "dataset_id": self.dataset_id,
                "shards": [asdict(shard) for shard in self.shards],
            },
            indent=2,
            sort_keys=True,
        )

    def write(self, path: str | Path) -> Path:
        """Persist the manifest to ``path`` atomically."""

        result = cast(Path, safe_write_text(path, self.to_json()))
        return result

    @staticmethod
    def load(path: str | Path) -> DatasetManifest:
        """Load a manifest from disk without mutating the file."""

        data: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        shards = [Shard(**entry) for entry in data.get("shards", [])]
        return DatasetManifest(
            schema_version=data.get("schema_version", "1.0"),
            created_at=int(data.get("created_at", 0)),
            dataset_id=data.get("dataset_id"),
            shards=shards,
        )

    def verify(self, root: str | Path) -> None:
        """Ensure every shard exists beneath ``root`` with matching checksums."""

        base = Path(root)
        for shard in self.shards:
            target = base / shard.path
            if not target.exists():
                raise ValueError(f"Missing shard: {shard.path}")
            actual = _sha256_file(target)
            if actual != shard.sha256:
                raise ValueError(
                    f"Checksum mismatch for {shard.path}: " f"expected {shard.sha256}, got {actual}"
                )


__all__ = ["DatasetManifest", "Shard"]
