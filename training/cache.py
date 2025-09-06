from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Iterator

import numpy as np


class TokenCache:
    """Persist tokenized batches to disk as NPZ shards with a manifest."""

    def __init__(self, out_dir: str | Path, rows_per_shard: int = 1024) -> None:
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.rows_per_shard = int(rows_per_shard)
        self._buffer: list[Dict[str, np.ndarray]] = []
        self._buffer_rows = 0
        self._shard_idx = 0
        self.manifest: dict[str, object] = {
            "rows_per_shard": self.rows_per_shard,
            "shards": [],
        }
        self._write_manifest()

    def add_batch(self, batch: Dict[str, np.ndarray]) -> None:
        """Append a batch to the cache, flushing when reaching ``rows_per_shard``."""
        self._buffer.append(batch)
        rows = next(iter(batch.values())).shape[0]
        self._buffer_rows += rows
        if self._buffer_rows >= self.rows_per_shard:
            self._flush()

    def _flush(self) -> None:
        if not self._buffer:
            return
        shard_path = self.out_dir / f"shard_{self._shard_idx:05d}.npz"
        data: Dict[str, np.ndarray] = {}
        for key in self._buffer[0].keys():
            data[key] = np.concatenate([b[key] for b in self._buffer], axis=0)
        np.savez(shard_path, **data)  # type: ignore[arg-type]
        rows = int(next(iter(data.values())).shape[0])
        shard_info = {"path": shard_path.name, "rows": rows}
        self.manifest["shards"].append(shard_info)  # type: ignore[attr-defined]
        self._buffer.clear()
        self._buffer_rows = 0
        self._shard_idx += 1
        self._write_manifest()

    def finalize(self) -> None:
        """Flush remaining data to disk."""
        self._flush()

    def _write_manifest(self) -> None:
        (self.out_dir / "manifest.json").write_text(json.dumps(self.manifest))

    @staticmethod
    def iter_batches(out_dir: str | Path) -> Iterator[Dict[str, np.ndarray]]:
        """Yield cached batches from ``out_dir`` using ``numpy.memmap``."""
        out = Path(out_dir)
        manifest = json.loads((out / "manifest.json").read_text())
        for shard in manifest.get("shards", []):
            shard_path = out / shard["path"]
            data = np.load(shard_path, mmap_mode="r")
            batch = {k: data[k] for k in data.files}
            yield batch
            data.close()
