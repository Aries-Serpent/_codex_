"""
Writers Module

This module provides functionality for writers.

Usage:
    from tracking.writers import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path
from typing import Any, Dict, Optional


class _NdjsonWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def write(self, row: Dict[str, Any]) -> None:
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True))
            handle.write("\n")


class _CsvWriter:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._header_written = False
        self._field_order: Optional[list[str]] = None

    def write(self, row: Dict[str, Any]) -> None:
        if self._field_order is None:
            self._field_order = sorted(row.keys())

        new_fields = sorted(set(row.keys()) - set(self._field_order))
        if new_fields:
            self._field_order.extend(new_fields)
            self._header_written = False

        with self.path.open("a", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=self._field_order, extrasaction="ignore")
            if not self._header_written:
                writer.writeheader()
                self._header_written = True
            writer.writerow({key: row.get(key) for key in self._field_order})


_ndjson: Optional[_NdjsonWriter] = None
_csv: Optional[_CsvWriter] = None
_output_dir: Optional[Path] = None


def set_output_dir(output_dir: Path | str) -> None:
    global _ndjson, _csv, _output_dir
    _output_dir = Path(output_dir).resolve()
    _output_dir.mkdir(parents=True, exist_ok=True)
    _ndjson = _NdjsonWriter(_output_dir / "telemetry.ndjson")
    _csv = _CsvWriter(_output_dir / "telemetry.csv")


def _ensure_default_output_dir() -> None:
    if _ndjson is None or _csv is None:
        set_output_dir(Path("artifacts/telemetry"))


def log_metrics(step: int, metrics: Dict[str, Any], run_id: str) -> None:
    _ensure_default_output_dir()
    payload = dict(metrics)
    payload["_ts"] = float(time.time())
    payload["_run_id"] = str(run_id)
    payload["_step"] = int(step)
    assert _ndjson is not None and _csv is not None
    _ndjson.write(payload)
    _csv.write(payload)


def get_paths() -> Dict[str, str]:
    _ensure_default_output_dir()
    assert _output_dir is not None
    return {
        "output_dir": str(_output_dir),
        "ndjson": str(_output_dir / "telemetry.ndjson"),
        "csv": str(_output_dir / "telemetry.csv"),
    }
