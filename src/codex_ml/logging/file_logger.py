"""Simple file-based metric logging sinks."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Iterator, Literal, Mapping, Optional, Tuple, cast

JsonLogFmt = Literal["ndjson", "csv"]

_VALID_FORMATS: Tuple[str, ...] = ("ndjson", "csv")


def _normalize_formats(formats: Iterable[JsonLogFmt | str]) -> Tuple[JsonLogFmt, ...]:
    seen: list[str] = []
    for raw in formats:
        fmt = str(raw).lower()
        if fmt not in _VALID_FORMATS:
            raise ValueError(f"unsupported format: {fmt}")
        if fmt not in seen:
            seen.append(fmt)
    if not seen:
        seen.append("ndjson")
    return tuple(cast(JsonLogFmt, fmt) for fmt in seen)


def _iter_fieldnames(row: Mapping[str, object]) -> Iterator[str]:
    for key in row.keys():
        yield str(key)


@dataclass
class FileLogger:
    """Write metric dictionaries to structured files (NDJSON/CSV).

    Parameters
    ----------
    root:
        Directory where output files will be created.
    formats:
        Iterable of output formats. ``"ndjson"`` is used by default; ``"csv"``
        can be added for spreadsheet-friendly exports.
    filename_stem:
        Shared stem for generated files (``metrics`` by default).
    """

    root: Path | str
    formats: Iterable[JsonLogFmt] = field(default_factory=lambda: ("ndjson",))
    filename_stem: str = "metrics"

    def __post_init__(self) -> None:
        self.root = Path(self.root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._formats = _normalize_formats(self.formats)
        self._ndjson_path: Optional[Path] = None
        self._csv_path: Optional[Path] = None
        self._csv_fieldnames: list[str] | None = None
        if "ndjson" in self._formats:
            self._ndjson_path = self.root / f"{self.filename_stem}.ndjson"
        if "csv" in self._formats:
            self._csv_path = self.root / f"{self.filename_stem}.csv"

    def log(self, row: Mapping[str, object]) -> None:
        """Append the provided mapping to every configured output format."""
        payload = dict(row)
        if self._ndjson_path is not None:
            self._append_ndjson(payload)
        if self._csv_path is not None:
            self._append_csv(payload)

    def _append_ndjson(self, row: Mapping[str, object]) -> None:
        assert self._ndjson_path is not None
        with self._ndjson_path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    def _append_csv(self, row: Mapping[str, object]) -> None:
        assert self._csv_path is not None
        if self._csv_fieldnames is None:
            self._csv_fieldnames = list(_iter_fieldnames(row))
        else:
            for name in _iter_fieldnames(row):
                if name not in self._csv_fieldnames:
                    self._csv_fieldnames.append(name)
        path = self._csv_path
        write_header = not path.exists() or path.stat().st_size == 0
        with path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=self._csv_fieldnames, extrasaction="ignore")
            if write_header:
                writer.writeheader()
            writer.writerow({k: row.get(k) for k in self._csv_fieldnames})

    def paths(self) -> Dict[str, Optional[Path]]:
        """Return the resolved NDJSON and CSV paths (may be ``None``)."""

        return {"ndjson": self._ndjson_path, "csv": self._csv_path}


__all__ = ["FileLogger", "JsonLogFmt"]
