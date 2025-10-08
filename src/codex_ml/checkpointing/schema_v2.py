"""Checkpoint manifest v2 dataclasses and helpers."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

SCHEMA_ID = "codex.checkpoint.v2"


@dataclass(frozen=True)
class RunMeta:
    """Metadata describing the run that produced a checkpoint."""

    id: str
    created_at: str
    framework: str = "pytorch"
    codex_version: str | None = None


@dataclass(frozen=True)
class WeightsMeta:
    """Metadata for the primary weights artifact."""

    format: str
    bytes: int
    dtype: str = "float32"
    sharded: bool = False


@dataclass(frozen=True)
class OptimizerMeta:
    """Optimizer checkpoint metadata."""

    name: str
    bytes: int


@dataclass(frozen=True)
class SchedulerMeta:
    """Scheduler checkpoint metadata."""

    name: str | None = None


@dataclass(frozen=True)
class RNGMeta:
    """Random number generator state metadata."""

    torch: str | None = None
    python: str | None = None
    numpy: str | None = None


@dataclass(frozen=True)
class CheckpointManifest:
    """Structured representation of a checkpoint manifest."""

    schema: str = SCHEMA_ID
    run: RunMeta = field(default_factory=lambda: RunMeta(id="unknown", created_at=""))
    weights: WeightsMeta = field(default_factory=lambda: WeightsMeta(format="pt", bytes=0))
    optimizer: OptimizerMeta | None = None
    scheduler: SchedulerMeta | None = None
    rng: RNGMeta | None = None
    notes: str | None = None


def to_dict(obj: Any) -> dict[str, Any]:
    """Return a JSON-serialisable dictionary for ``obj``."""

    if isinstance(obj, Mapping):
        return dict(obj)
    return asdict(obj)


def from_dict(data: Mapping[str, Any]) -> CheckpointManifest:
    """Create :class:`CheckpointManifest` from a mapping."""

    run = data.get("run", {})
    weights = data.get("weights", {})
    optimizer = data.get("optimizer")
    scheduler = data.get("scheduler")
    rng = data.get("rng")
    return CheckpointManifest(
        schema=str(data.get("schema", SCHEMA_ID)),
        run=RunMeta(
            id=str(run.get("id", "unknown")),
            created_at=str(run.get("created_at", "")),
            framework=str(run.get("framework", "pytorch")),
            codex_version=run.get("codex_version"),
        ),
        weights=WeightsMeta(
            format=str(weights.get("format", "pt")),
            bytes=int(weights.get("bytes", 0)),
            dtype=str(weights.get("dtype", "float32")),
            sharded=bool(weights.get("sharded", False)),
        ),
        optimizer=(
            OptimizerMeta(
                name=str(optimizer.get("name")),
                bytes=int(optimizer.get("bytes", 0)),
            )
            if isinstance(optimizer, Mapping) and optimizer.get("name")
            else None
        ),
        scheduler=(
            SchedulerMeta(
                name=str(scheduler.get("name")) if scheduler.get("name") is not None else None,
            )
            if isinstance(scheduler, Mapping)
            else None
        ),
        rng=(
            RNGMeta(
                torch=str(rng.get("torch")) if rng.get("torch") is not None else None,
                python=str(rng.get("python")) if rng.get("python") is not None else None,
                numpy=str(rng.get("numpy")) if rng.get("numpy") is not None else None,
            )
            if isinstance(rng, Mapping)
            else None
        ),
        notes=data.get("notes"),
    )


def canonical_json(obj: Any) -> str:
    """Serialise ``obj`` to canonical JSON (sorted keys, compact separators)."""

    payload = to_dict(obj)
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj: Any) -> str:
    """Return the SHA256 digest for the canonical JSON representation of ``obj``."""

    canonical = canonical_json(obj)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def validate_manifest(data: Mapping[str, Any]) -> None:
    """Validate minimal structural requirements for a manifest."""

    for section in ("schema", "run", "weights"):
        if section not in data:
            raise ValueError(f"manifest missing required section: {section}")
    if data.get("schema") != SCHEMA_ID:
        raise ValueError(f"unexpected schema id: {data.get('schema')!r}")
    run = data.get("run", {})
    weights = data.get("weights", {})
    if "id" not in run or "created_at" not in run:
        raise ValueError("run.id and run.created_at required")
    if "format" not in weights or "bytes" not in weights:
        raise ValueError("weights.format and weights.bytes required")


def is_v2(data: Mapping[str, Any]) -> bool:
    """Return ``True`` if the manifest already declares the v2 schema id."""

    return data.get("schema") == SCHEMA_ID


def upgrade_from_v1(data: Mapping[str, Any]) -> dict[str, Any]:
    """Best-effort upgrade from an older manifest shape to v2."""

    if is_v2(data):
        return dict(data)
    meta = data.get("meta") or {}
    weights = data.get("weights") or {}
    upgraded = {
        "schema": SCHEMA_ID,
        "run": {
            "id": meta.get("id", "unknown"),
            "created_at": meta.get("created_at", ""),
            "framework": meta.get("framework", "pytorch"),
            "codex_version": meta.get("codex_version"),
        },
        "weights": {
            "format": weights.get("format", "pt"),
            "bytes": int(weights.get("bytes", 0)),
            "dtype": weights.get("dtype", "float32"),
            "sharded": bool(weights.get("sharded", False)),
        },
        "optimizer": data.get("optimizer"),
        "scheduler": data.get("scheduler"),
        "rng": data.get("rng"),
        "notes": data.get("notes"),
    }
    validate_manifest(upgraded)
    return upgraded


def manifest_digest_from_path(path: Path) -> str:
    """Compute the canonical digest for a manifest on disk."""

    contents = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(contents, Mapping):
        raise ValueError("manifest on disk must be a JSON object")
    return digest(contents)


__all__ = [
    "CheckpointManifest",
    "RunMeta",
    "WeightsMeta",
    "OptimizerMeta",
    "SchedulerMeta",
    "RNGMeta",
    "SCHEMA_ID",
    "canonical_json",
    "digest",
    "from_dict",
    "is_v2",
    "manifest_digest_from_path",
    "to_dict",
    "upgrade_from_v1",
    "validate_manifest",
]
