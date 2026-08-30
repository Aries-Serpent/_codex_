"""
Schema V2 Module

This module provides functionality for schema v2.

Usage:
    from checkpointing.schema_v2 import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import hashlib
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Optional

from codex_ml.io.atomic import atomic_write_text, canonical_json_dumps

CANON_SEPARATORS = (",", ":")  # compact; RFC8785-compatible shape
SCHEMA_ID = "codex.checkpoint.v2"


def _reject_non_json_number(x: float) -> None:
    # JSON forbids NaN/Infinity; JCS/I-JSON require IEEE-754-friendly numbers.
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        raise ValueError("Non-finite JSON number (NaN/Inf) not allowed")


def to_canonical_bytes(obj: Any) -> bytes:
    """Return canonicalized JSON bytes for hashing/signing (deterministic)."""

    # Walk and reject NaN/Inf proactively
    def _walk(v: Any) -> Any:
        if isinstance(v, float):
            _reject_non_json_number(v)
            return v
        if isinstance(v, dict):
            return {k: _walk(v[k]) for k in v}
        if isinstance(v, list):
            return [_walk(i) for i in v]
        return v

    normalized = _walk(obj)
    text = canonical_json_dumps(normalized)
    return text.encode("utf-8")


def sha256_hexdigest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass
class CheckpointMetaV2:
    run_id: str
    step: int
    epoch: int
    created_utc: float
    notes: Optional[str] = None
    extra: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        # drop None to keep canonical bytes stable across envs
        return {k: v for k, v in d.items() if v is not None}


def compute_manifest_digest(manifest: dict[str, Any]) -> str:
    return sha256_hexdigest(to_canonical_bytes(manifest))


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        # Note: stdlib json doesn't expose duplicate-key hooks;
        # we assume upstream generation respects no-dup rule (I-JSON).
        return json.load(f)


def validate_manifest(m: dict[str, Any]) -> list[str]:
    """Return list of problems; empty if valid enough for hashing."""

    problems: list[str] = []
    if not isinstance(m, dict):
        return ["manifest must be a mapping"]
    if "schema" in m and m["schema"] not in (SCHEMA_ID,):
        problems.append("unsupported schema")

    required_flat = ("run_id", "step", "epoch", "created_utc")
    has_run_block = "run" in m and isinstance(m.get("run"), dict)
    missing_flat = [r for r in required_flat if r not in m]
    if missing_flat and not has_run_block:
        problems.extend(f"missing field: {r}" for r in missing_flat)

    run = m.get("run")
    if run is not None:
        if not isinstance(run, dict):
            problems.append("run must be a mapping")
        else:
            if "id" not in run:
                problems.append("missing field: run.id")
            if "created_at" in run and not isinstance(run["created_at"], str):
                problems.append("run.created_at must be string timestamp")

    weights = m.get("weights")
    if weights is not None and not isinstance(weights, dict):
        problems.append("weights must be a mapping when provided")

    return problems


def from_dict(manifest: dict[str, Any]) -> dict[str, Any]:
    """Create a normalized manifest ensuring schema id and basic validation."""

    normalized = dict(manifest)
    normalized.setdefault("schema", SCHEMA_ID)
    problems = validate_manifest(normalized)
    if problems:
        raise ValueError("; ".join(problems))
    return normalized


def to_dict(manifest: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy with schema id enforced (used for roundtrips)."""

    copy = dict(manifest)
    copy.setdefault("schema", SCHEMA_ID)
    return copy


def upgrade_from_v1(v1_manifest: dict[str, Any]) -> dict[str, Any]:
    """Best-effort upgrade from legacy v1 schema into v2 layout."""

    meta = v1_manifest.get("meta", {})
    return {
        "schema": SCHEMA_ID,
        "run": {
            "id": meta.get("id", "unknown"),
            "created_at": meta.get("created_at", ""),
            "framework": meta.get("framework", "unknown"),
        },
        "weights": v1_manifest.get("weights", {}),
        "optimizer": v1_manifest.get("optimizer", {}),
        "notes": v1_manifest.get("notes"),
    }


def new_manifest(run_id: str, step: int, epoch: int, notes: str | None = None) -> dict[str, Any]:
    meta = CheckpointMetaV2(
        run_id=run_id,
        step=step,
        epoch=epoch,
        created_utc=time.time(),
        notes=notes,
    )
    m = meta.to_dict()
    m["digest"] = compute_manifest_digest(m)
    return m


def write_manifest_json(path: Path, manifest: dict[str, Any]) -> Path:
    """Write the manifest JSON atomically (canonical, fsync'd)."""

    atomic_write_text(path, canonical_json_dumps(manifest))
    return path
