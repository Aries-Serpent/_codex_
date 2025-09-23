# [Module]: NDJSON logger
# > Generated: 2025-08-26 20:36:12 | Author: mbaetiong
import json
import os
from typing import Any, Dict, Iterable

__all__ = ["NDJSONLogger"]


class NDJSONLogger:
    """Simple append-only NDJSON writer with context manager support."""

    def __init__(self, path: str = ".artifacts/metrics.ndjson"):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._path = path
        self._fh = open(path, "a", encoding="utf-8")
        self._closed = False

    @property
    def path(self) -> str:
        return self._path

    def write(self, record: Dict[str, Any]) -> None:
        if self._closed:
            raise ValueError("NDJSONLogger is closed")
        self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fh.flush()

    def write_many(self, records: Iterable[Dict[str, Any]]) -> None:
        for record in records:
            self.write(record)

    def close(self) -> None:
        if self._closed:
            return
        try:
            self._fh.flush()
            self._fh.close()
        finally:
            self._closed = True

    def __enter__(self) -> "NDJSONLogger":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        self.close()
        return False
