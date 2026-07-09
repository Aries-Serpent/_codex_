"""
Honesty Module

This module provides functionality for honesty.

Usage:
    from codex_harness.honesty import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_ALLOWED_CATEGORIES = {
    "VERIFIED",
    "INFERRED",
    "PLANNED",
    "SUMMARY",
    "AUDIT",
    "ASSERTED",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class HonestyStatement:
    content: str
    category: str
    verified: bool
    workflow: str | None = None
    timestamp: str = field(default_factory=_utc_now)
    metadata: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        if self.metadata is None:
            payload.pop("metadata", None)
        return payload


@dataclass
class HonestyMetadata:
    workflow: str
    statements: list[HonestyStatement] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        category_counts: dict[str, int] = {}
        verified_count = 0
        for statement in self.statements:
            category_counts[statement.category] = category_counts.get(statement.category, 0) + 1
            verified_count += int(bool(statement.verified))
        return {
            "total": len(self.statements),
            "verified": verified_count,
            "categories": category_counts,
        }


class HonestyRecorder:
    """Capture and flush honesty statements for the golden harness."""

    def __init__(
        self,
        workflow: str = "default",
        output_path: Path | str = Path("artifacts/honesty_metadata.json"),
    ) -> None:
        self.workflow = workflow
        self.output_path = Path(output_path)
        self._metadata = HonestyMetadata(workflow=workflow)

    @property
    def statements(self) -> list[HonestyStatement]:
        return list(self._metadata.statements)

    def record_statement(
        self,
        content: str,
        category: str,
        verified: bool,
        metadata: dict[str, Any] | None = None,
    ) -> HonestyStatement:
        if not content:
            raise ValueError("content is required for honesty statements")
        normalized_category = category.upper().strip()
        if normalized_category not in _ALLOWED_CATEGORIES:
            _ALLOWED_CATEGORIES.add(normalized_category)
        statement = HonestyStatement(
            content=content,
            category=normalized_category,
            verified=bool(verified),
            workflow=self.workflow,
            metadata=metadata,
        )
        self._metadata.statements.append(statement)
        return statement

    def flush(self, path: Path | str | None = None) -> Path:
        output = Path(path) if path else self.output_path
        output.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "workflow": self._metadata.workflow,
            "statements": [s.to_dict() for s in self._metadata.statements],
            "summary": self._metadata.summary(),
            "last_updated": _utc_now(),
        }
        output.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
        return output

    def load_existing(self) -> None:
        if not self.output_path.exists():
            return
        data = json.loads(self.output_path.read_text(encoding="utf-8"))
        statements = data.get("statements", [])
        for stmt in statements:
            self._metadata.statements.append(
                HonestyStatement(
                    content=stmt.get("content", ""),
                    category=str(stmt.get("category", "UNCATEGORIZED")).upper(),
                    verified=bool(stmt.get("verified", False)),
                    workflow=stmt.get("workflow", self.workflow),
                    timestamp=stmt.get("timestamp", _utc_now()),
                    metadata=stmt.get("metadata"),
                )
            )
