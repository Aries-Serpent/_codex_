"""
Errors Module

This module provides functionality for errors.

Usage:
    from codex_audit.errors import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

import json  # noqa: E402
from collections.abc import Iterable, Mapping  # noqa: E402
from dataclasses import dataclass, field  # noqa: E402
from datetime import UTC, datetime  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Optional  # noqa: E402


@dataclass
class ErrorRecord:
    phase_id: int
    step_label: str
    description: str
    message: str
    brief_context: str
    ra_references: list[str] = field(default_factory=lambda: ["RA-1", "RA-3"])
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat(timespec="seconds"))

    def to_dict(self) -> dict[str, object]:
        return {
            "phase_id": self.phase_id,
            "step_label": self.step_label,
            "description": self.description,
            "message": self.message,
            "brief_context": self.brief_context,
            "ra_references": list(self.ra_references),
            "timestamp": self.timestamp,
        }

    def to_markdown(self) -> str:
        ra_str = ", ".join(self.ra_references)
        return (
            f"[ERROR] {self.timestamp} | {self.phase_id}.{self.step_label} ({self.description})\n"
            f"Message: {self.message}\n"
            f"Context: {self.brief_context}\n"
            f"RA Policy: {ra_str}\n"
        )


def append_error_record(path: Path, record: ErrorRecord) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing: list[Mapping[str, object]] = []
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = []
    existing.append(record.to_dict())
    path.write_text(json.dumps(existing, indent=2, sort_keys=True), encoding="utf-8")


def load_error_records(path: Path) -> Iterable[ErrorRecord]:
    if not path.exists():
        return
    entries = json.loads(path.read_text(encoding="utf-8"))
    for entry in entries:
        yield ErrorRecord(
            phase_id=entry.get("phase_id", 0),
            step_label=entry.get("step_label", "unknown"),
            description=entry.get("description", ""),
            message=entry.get("message", ""),
            brief_context=entry.get("brief_context", ""),
            ra_references=list(entry.get("ra_references", [])),
            timestamp=entry.get("timestamp", datetime.now(UTC).isoformat(timespec="seconds")),
        )


def attach_ra_references(
    record: ErrorRecord, ra_rules: Optional[Iterable[str]] = None
) -> ErrorRecord:
    if ra_rules:
        record.ra_references = list(dict.fromkeys(ra_rules))
    return record


def capture_error(
    storage_json: Path,
    storage_markdown: Path,
    record: ErrorRecord,
) -> None:
    append_error_record(storage_json, record)
    with storage_markdown.open("a", encoding="utf-8") as handle:
        handle.write(record.to_markdown())
        handle.write("\n")
