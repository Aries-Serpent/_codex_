"""CSV mapping loaders with typed validation and evidence logging."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Generic, TypeVar

from pydantic import BaseModel, ValidationError

from codex.evidence import append_evidence, utc_now

from .models import RoutingPattern, SlaParity

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
    candidate = repo_root / path
    return candidate


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
