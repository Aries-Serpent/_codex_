"""
Load Module

This module provides functionality for load.

Usage:
    from mapping.load import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


import csv  # noqa: E402
from dataclasses import dataclass  # noqa: E402
from pathlib import Path  # noqa: E402
from typing import Generic, TypeVar  # noqa: E402

from pydantic import BaseModel, ValidationError  # noqa: E402

from codex.evidence import append_evidence, utc_now  # noqa: E402

from .models import RoutingPattern, SlaParity  # noqa: E402

__all__ = [
    "MappingLoadResult",
    "load_all_mappings",
    "load_routing",
    "load_sla",
]

T = TypeVar("T", bound=BaseModel)


@dataclass(slots=True)
class MappingLoadResult(Generic[T]):
    records: list[T]
    deferred: int = 0


def _log_deferred(source: Path, row_number: int, row: dict[str, str], error: object) -> None:
    append_evidence(
        "deferred.jsonl",
        {
            "ts": utc_now(),
            "source": source.as_posix(),
            "row_number": row_number,
            "error": error,
            "row": row,
            "phase": "mapping-validation",
        },
    )


def _resolve_path(path: Path) -> Path:
    if path.exists():
        return path
    if path.is_absolute():
        return path
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / path


def _load_csv(path: Path, model: type[T]) -> MappingLoadResult[T]:
    candidate = _resolve_path(path)
    if not candidate.exists():
        raise FileNotFoundError(f"Mapping file not found: {path}")

    records: list[T] = []
    deferred = 0
    with candidate.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for idx, raw_row in enumerate(reader, start=2):
            row = {key: (value or "").strip() for key, value in raw_row.items() if key}
            if not any(row.values()):
                continue
            try:
                records.append(model.model_validate(row))
            except ValidationError as exc:
                type(exc).__name__
                logger.debug("ValidationError: <ERROR_TYPE>")
                _log_deferred(candidate, idx, row, exc.errors(include_url=False))
                deferred += 1
    return MappingLoadResult(records=records, deferred=deferred)


def load_routing(path: Path) -> MappingLoadResult[RoutingPattern]:
    return _load_csv(path, RoutingPattern)


def load_sla(path: Path) -> MappingLoadResult[SlaParity]:
    return _load_csv(path, SlaParity)


def load_all_mappings(mappings_dir: Path) -> dict[str, dict[str, object]]:
    routing = load_routing(mappings_dir / "routing_patterns.csv")
    slas = load_sla(mappings_dir / "sla_parity.csv")
    return {
        "routing": {
            "source": _resolve_path(mappings_dir / "routing_patterns.csv").as_posix(),
            "count": len(routing.records),
            "deferred": routing.deferred,
            "rows": [record.model_dump() for record in routing.records],
        },
        "sla": {
            "source": _resolve_path(mappings_dir / "sla_parity.csv").as_posix(),
            "count": len(slas.records),
            "deferred": slas.deferred,
            "rows": [record.model_dump() for record in slas.records],
        },
    }
