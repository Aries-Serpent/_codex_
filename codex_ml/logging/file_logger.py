"""Simple file-backed metric logger used by the training examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Mapping, MutableMapping

__all__ = ["FileLogger"]


class FileLogger:
    """Write structured metric rows to disk in a couple of lightweight formats.

    Parameters
    ----------
    root:
        Directory where log files will be written.  The directory is created when
        the logger is constructed.
    formats:
        Iterable of format specifiers.  Supported values are ``"ndjson"`` and
        ``"csv"``.  When omitted an ndjson stream is produced.
    filename_stem:
        Basename without the file extension.  ``metrics`` is used by default.
    """

    _CSV_DELIM = ","

    def __init__(
        self,
        *,
        root: str | Path,
        formats: Iterable[str] | None = None,
        filename_stem: str = "metrics",
    ) -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)
        self._formats = tuple(str(fmt).lower() for fmt in (formats or ("ndjson",)))
        self._stem = filename_stem
        self._paths: dict[str, Path] = {}
        for fmt in self._formats:
            suffix = ".ndjson" if fmt == "ndjson" else f".{fmt}"
            self._paths[fmt] = self._root / f"{self._stem}{suffix}"

    # ------------------------------------------------------------------
    def log(self, row: Mapping[str, object]) -> None:
        """Append ``row`` to all configured outputs."""

        payload = dict(row)
        if not payload:
            return
        if "ndjson" in self._formats:
            self._write_ndjson(payload)
        if "csv" in self._formats:
            self._write_csv(payload)

    # ------------------------------------------------------------------
    def _write_ndjson(self, payload: Mapping[str, object]) -> None:
        target = self._paths["ndjson"]
        with target.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=False) + "\n")

    # ------------------------------------------------------------------
    def _write_csv(self, payload: Mapping[str, object]) -> None:
        target = self._paths["csv"]
        header_needed = not target.exists()
        with target.open("a", encoding="utf-8") as handle:
            if header_needed:
                handle.write(self._CSV_DELIM.join(payload.keys()) + "\n")
            handle.write(self._CSV_DELIM.join(_format_csv_value(value) for value in payload.values()) + "\n")

    # ------------------------------------------------------------------
    def paths(self) -> MutableMapping[str, Path]:
        """Return a mapping of format -> path for downstream inspection."""

        return dict(self._paths)


def _format_csv_value(value: object) -> str:
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value, ensure_ascii=False)
