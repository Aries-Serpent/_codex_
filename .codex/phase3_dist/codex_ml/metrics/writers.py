"""
Writers Module

This module provides functionality for writers.

Usage:
    from metrics.writers import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import csv  # noqa: E402
import json  # noqa: E402
import os  # noqa: E402
import time  # noqa: E402
from collections.abc import Mapping, Sequence  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Any  # noqa: E402
from uuid import uuid4  # noqa: E402

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
    extra: dict[str, Any] = field(default_factory=dict)
    run_id: str | None = None
    tags: Mapping[str, str] | None = None

    def as_dict(self) -> dict[str, Any]:
        payload = {
            "metric": self.metric,
            "value": float(self.value),
            "step": int(self.step),
            "split": self.split,
            "ts": self.ts,
        }
        payload.update(self.extra)
        if self.run_id:
            payload["run_id"] = self.run_id
        if self.tags:
            payload["tags"] = dict(self.tags)
        return payload


class BaseMetricsWriter:
    """Common validation helpers shared across metrics writers."""

    def __init__(
        self,
        path: str | Path,
        *,
        run_id: str | None = None,
        default_tags: Mapping[str, str] | None = None,
    ) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.run_id = run_id or os.getenv("CODEX_RUN_ID") or f"run-{uuid4().hex}"
        self.default_tags = dict(default_tags) if default_tags else {}

    def _normalise(self, record: Mapping[str, Any] | MetricsRecord) -> dict[str, Any]:
        if isinstance(record, MetricsRecord):
            payload = record.as_dict()
        else:
            payload = dict(record)
            payload.setdefault("ts", _timestamp())
            payload.setdefault("split", "train")
            payload.setdefault("metric", "unknown")
            payload.setdefault("value", 0.0)
            payload.setdefault("step", 0)
        payload.setdefault("run_id", self.run_id)
        raw_tags = payload.pop("tags", {}) or {}
        missing = [field for field in _REQUIRED_FIELDS if field not in payload]
        if missing:
            raise ValueError(f"metric record missing required fields: {missing}")
        try:
            payload["value"] = float(payload["value"])
        except (ValueError, TypeError) as exc:  # pragma: no cover - defensive conversion
            raise ValueError("metric value must be numeric") from exc
        payload["step"] = int(payload["step"])
        payload["metric"] = str(payload["metric"])
        payload["split"] = str(payload.get("split", "train"))
        tags = dict(self.default_tags)
        if isinstance(raw_tags, Mapping):
            tags.update({str(k): str(v) for k, v in raw_tags.items()})
        tags.setdefault("metric", payload["metric"])
        tags.setdefault("step", str(payload["step"]))
        if payload.get("run_id"):
            tags.setdefault("run_id", str(payload["run_id"]))
        payload["tags"] = tags
        return payload

    def close(
        self,
    ) -> None:  # pragma: no cover - convenience for parity with logging APIs
        """Close writer resources if necessary."""

    def write(self, record: Mapping[str, Any] | MetricsRecord) -> None:
        """Write a metrics record. Subclasses must implement this method."""
        raise TypeError(
            f"{self.__class__.__name__}.write() must be implemented by subclass. "
            f"Use NDJSONMetricsWriter or CSVMetricsWriter."
        )


class NDJSONMetricsWriter(BaseMetricsWriter):
    """Append structured metrics to newline-delimited JSON."""

    def write(self, record: Mapping[str, Any] | MetricsRecord) -> None:
        payload = self._normalise(record)
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


class CSVMetricsWriter(BaseMetricsWriter):
    """Persist metrics to CSV with a stable header."""

    _FIELDS: Sequence[str] = (
        "metric",
        "value",
        "step",
        "split",
        "ts",
        "run_id",
        "tags",
    )

    def __init__(self, path: str | Path, **kwargs: Any) -> None:
        super().__init__(path, **kwargs)
        self._has_header = self.path.exists() and self.path.stat().st_size > 0

    def write(self, record: Mapping[str, Any] | MetricsRecord) -> None:
        payload = self._normalise(record)
        with self.path.open("a", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=self._FIELDS)
            if not self._has_header:
                writer.writeheader()
                self._has_header = True
            row = {field: payload.get(field) for field in self._FIELDS}
            row["tags"] = json.dumps(payload.get("tags", {}), sort_keys=True)
            writer.writerow(row)


__all__ = ["CSVMetricsWriter", "MetricsRecord", "NDJSONMetricsWriter"]
