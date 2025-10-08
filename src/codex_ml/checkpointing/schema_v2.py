from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import hashlib
import json
import math
import time
import pathlib

CANON_SEPARATORS = (",", ":")  # compact; RFC8785-compatible shape


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
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=CANON_SEPARATORS,
        ensure_ascii=False,
    ).encode("utf-8")


def sha256_hexdigest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


@dataclass
class CheckpointMetaV2:
    run_id: str
    step: int
    epoch: int
    created_utc: float
    notes: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        # drop None to keep canonical bytes stable across envs
        return {k: v for k, v in d.items() if v is not None}


def compute_manifest_digest(manifest: Dict[str, Any]) -> str:
    return sha256_hexdigest(to_canonical_bytes(manifest))


def load_json(path: pathlib.Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        # Note: stdlib json doesn't expose duplicate-key hooks;
        # we assume upstream generation respects no-dup rule (I-JSON).
        return json.load(f)


def validate_manifest(m: Dict[str, Any]) -> list[str]:
    """Return list of problems; empty if valid enough for hashing."""

    problems: list[str] = []
    for k in ("run_id", "step", "epoch", "created_utc"):
        if k not in m:
            problems.append(f"missing field: {k}")
    if "created_utc" in m and not isinstance(m["created_utc"], (int, float)):
        problems.append("created_utc must be number (UTC seconds)")
    for n in ("step", "epoch"):
        if n in m and not isinstance(m[n], int):
            problems.append(f"{n} must be int")
    # number sanity
    if "created_utc" in m:
        _reject_non_json_number(float(m["created_utc"]))
    return problems


def new_manifest(run_id: str, step: int, epoch: int, notes: str | None = None) -> Dict[str, Any]:
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
