from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Dict, Any

from src.codex_ml.utils.atomic_io import safe_write_text


def _sha256_file(path: Path, chunk_size: int = 1 << 16) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass
class Shard:
    path: str
    size: int
    sha256: str


@dataclass
class DatasetManifest:
    schema_version: str = "1.0"
    created_at: int = field(default_factory=lambda: int(os.environ.get("SOURCE_DATE_EPOCH", "0")) or __import__("time").time().__int__())
    dataset_id: str | None = None
    shards: List[Shard] = field(default_factory=list)

    @staticmethod
    def build(root: str | Path, shard_paths: List[str]) -> "DatasetManifest":
        root = Path(root)
        entries: List[Shard] = []
        for rel in shard_paths:
            p = root / rel
            stat = p.stat()
            entries.append(Shard(path=rel, size=stat.st_size, sha256=_sha256_file(p)))
        return DatasetManifest(shards=entries)

    def to_json(self) -> str:
        return json.dumps(
            {
                "schema_version": self.schema_version,
                "created_at": self.created_at,
                "dataset_id": self.dataset_id,
                "shards": [asdict(s) for s in self.shards],
            },
            indent=2,
            sort_keys=True,
        )

    def write(self, path: str | Path) -> Path:
        return safe_write_text(path, self.to_json())

    @staticmethod
    def load(path: str | Path) -> "DatasetManifest":
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        shards = [Shard(**s) for s in data.get("shards", [])]
        man = DatasetManifest(
            schema_version=data.get("schema_version", "1.0"),
            created_at=data.get("created_at", 0),
            dataset_id=data.get("dataset_id"),
            shards=shards,
        )
        return man

    def verify(self, root: str | Path) -> None:
        """
        Recompute sha256 for each shard and raise ValueError on mismatch or missing.
        """
        root = Path(root)
        for s in self.shards:
            p = root / s.path
            if not p.exists():
                raise ValueError(f"Missing shard: {s.path}")
            actual = _sha256_file(p)
            if actual != s.sha256:
                raise ValueError(f"Checksum mismatch for {s.path}: expected {s.sha256}, got {actual}")