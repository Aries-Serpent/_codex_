from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping, Optional


SCHEMA_ID = "codex.checkpoint.v2"
SCHEMA_VERSION = (2, 0)


@dataclass(frozen=True)
class RunMeta:
    id: str
    created_at: str  # ISO8601 string
    framework: str = "pytorch"
    codex_version: Optional[str] = None


@dataclass(frozen=True)
class WeightsMeta:
    format: str  # "pt" | "safetensors" | ...
    bytes: int
    dtype: str = "float32"
    sharded: bool = False


@dataclass(frozen=True)
class OptimizerMeta:
    name: str
    bytes: int


@dataclass(frozen=True)
class SchedulerMeta:
    name: Optional[str] = None


@dataclass(frozen=True)
class RNGMeta:
    torch: Optional[str] = None
    python: Optional[str] = None
    numpy: Optional[str] = None


@dataclass(frozen=True)
class CheckpointManifest:
    schema: str = SCHEMA_ID
    run: RunMeta = field(default_factory=lambda: RunMeta(id="unknown", created_at=""))
    weights: WeightsMeta = field(default_factory=lambda: WeightsMeta(format="pt", bytes=0))
    optimizer: Optional[OptimizerMeta] = None
    scheduler: Optional[SchedulerMeta] = None
    rng: Optional[RNGMeta] = None
    notes: Optional[str] = None


def to_dict(obj: Any) -> dict[str, Any]:
    return asdict(obj)


def from_dict(d: Mapping[str, Any]) -> CheckpointManifest:
    run = d.get("run", {})
    weights = d.get("weights", {})
    return CheckpointManifest(
        schema=d.get("schema", SCHEMA_ID),
        run=RunMeta(**run),
        weights=WeightsMeta(**weights),
        optimizer=OptimizerMeta(**d["optimizer"]) if d.get("optimizer") else None,
        scheduler=SchedulerMeta(**d["scheduler"]) if d.get("scheduler") else None,
        rng=RNGMeta(**d["rng"]) if d.get("rng") else None,
        notes=d.get("notes"),
    )


def canonical_json(obj: Any) -> str:
    if not isinstance(obj, Mapping):
        obj = to_dict(obj)
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj: Any) -> str:
    s = canonical_json(obj)
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def validate_manifest(d: Mapping[str, Any]) -> None:
    """
    Minimal structural check: raises ValueError if required fields are absent.
    Intentionally stdlib-only (no jsonschema).
    """

    for k in ("schema", "run", "weights"):
        if k not in d:
            raise ValueError(f"manifest missing required section: {k}")
    if "id" not in d["run"] or "created_at" not in d["run"]:
        raise ValueError("run.id and run.created_at required")
    if "format" not in d["weights"] or "bytes" not in d["weights"]:
        raise ValueError("weights.format and weights.bytes required")


def is_v2(d: Mapping[str, Any]) -> bool:
    return d.get("schema") == SCHEMA_ID


def upgrade_from_v1(d: Mapping[str, Any]) -> Mapping[str, Any]:
    """
    Best-effort migration from a hypothetical v1 shape to v2.
    Rules:
      - map top-level 'meta' → 'run'
      - ensure required fields exist, else raise
    """

    if is_v2(d):
        return d
    meta = d.get("meta") or {}
    run = {
        "id": meta.get("id") or "unknown",
        "created_at": meta.get("created_at") or "",
        "framework": meta.get("framework") or "pytorch",
        "codex_version": meta.get("codex_version"),
    }
    weights = d.get("weights") or {}
    out = {
        "schema": SCHEMA_ID,
        "run": run,
        "weights": {
            "format": weights.get("format") or "pt",
            "bytes": int(weights.get("bytes") or 0),
            "dtype": weights.get("dtype") or "float32",
            "sharded": bool(weights.get("sharded") or False),
        },
        "optimizer": d.get("optimizer"),
        "scheduler": d.get("scheduler"),
        "rng": d.get("rng"),
        "notes": d.get("notes"),
    }
    validate_manifest(out)
    return out


def manifest_digest_from_path(path: Path) -> str:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return digest(data)
