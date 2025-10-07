"""Structured metric writers with JSONL/CSV backends and schema validation."""

from __future__ import annotations

import csv
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence

_REQUIRED_FIELDS = ("metric", "value", "step")


def _timestamp() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


@dataclass(slots=True)
class MetricsRecord:
    """A structured metrics payload used by :class:`BaseMetricsWriter`."""

    metric: str
    value: float
    step: int
    split: str = "train"
    ts: str = field(default_factory=_timestamp)
    extra: Dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> Dict[str, Any]:
        payload = {
            "metric": self.metric,
            "value": float(self.value),
            "step": int(self.step),
            "split": self.split,
            "ts": self.ts,
        }
        payload.update(self.extra)
        return payload


class BaseMetricsWriter:
    """Common validation helpers shared across metrics writers."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _normalise(self, record: Mapping[str, Any] | MetricsRecord) -> Dict[str, Any]:
        if isinstance(record, MetricsRecord):
            payload = record.as_dict()
        else:
            payload = dict(record)
            payload.setdefault("ts", _timestamp())
            payload.setdefault("split", "train")
            payload.setdefault("metric", "unknown")
            payload.setdefault("value", 0.0)
            payload.setdefault("step", 0)
        missing = [field for field in _REQUIRED_FIELDS if field not in payload]
        if missing:
            raise ValueError(f"metric record missing required fields: {missing}")
        try:
            payload["value"] = float(payload["value"])
        except Exception as exc:  # pragma: no cover - defensive conversion
            raise ValueError("metric value must be numeric") from exc
        payload["step"] = int(payload["step"])
        payload["metric"] = str(payload["metric"])
        payload["split"] = str(payload.get("split", "train"))
        return payload

    def close(self) -> None:  # pragma: no cover - convenience for parity with logging APIs
        """Close writer resources if necessary."""

    def write(self, record: Mapping[str, Any] | MetricsRecord) -> None:
        raise NotImplementedError


class NDJSONMetricsWriter(BaseMetricsWriter):
    """Append structured metrics to newline-delimited JSON."""

    def write(self, record: Mapping[str, Any] | MetricsRecord) -> None:
        payload = self._normalise(record)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


class CSVMetricsWriter(BaseMetricsWriter):
    """Persist metrics to CSV with a stable header."""

    _FIELDS: Sequence[str] = ("metric", "value", "step", "split", "ts")

    def __init__(self, path: str | Path) -> None:
        super().__init__(path)
        self._has_header = self.path.exists() and self.path.stat().st_size > 0

    def write(self, record: Mapping[str, Any] | MetricsRecord) -> None:
        payload = self._normalise(record)
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self._FIELDS)
            if not self._has_header:
                writer.writeheader()
                self._has_header = True
            writer.writerow({field: payload.get(field) for field in self._FIELDS})


__all__ = ["MetricsRecord", "NDJSONMetricsWriter", "CSVMetricsWriter"]
