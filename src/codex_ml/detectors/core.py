from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Iterable, Mapping, Optional

try:  # optional; Branch C provides schema_v2
    from codex_ml.checkpointing import schema_v2 as _schema
except Exception:  # pragma: no cover
    _schema = None  # type: ignore

Json = Mapping[str, Any]


@dataclass(frozen=True)
class DetectorFinding:
    name: str
    passed: bool
    message: str | None = None


@dataclass(frozen=True)
class DetectorResult:
    detector: str
    score: float  # [0, 1]
    findings: list[DetectorFinding] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    extras: dict[str, Any] = field(default_factory=dict)


def as_dict(r: DetectorResult) -> dict[str, Any]:
    return asdict(r)


def from_dict(d: Json) -> DetectorResult:
    findings = [DetectorFinding(**f) for f in d.get("findings", [])]
    return DetectorResult(
        detector=d["detector"],
        score=float(d["score"]),
        findings=findings,
        tags=list(d.get("tags", [])),
        extras=dict(d.get("extras", {})),
    )


Detector = Callable[[Optional[Json]], DetectorResult]


def run_detectors(
    detectors: Iterable[Detector], manifest: Optional[Json] = None
) -> list[DetectorResult]:
    """Execute detectors; if schema v2 is present, validate manifest first."""

    if manifest is not None and _schema is not None:
        try:
            _schema.validate_manifest(manifest)
        except Exception:
            # propagate a negative finding in all detectors
            neg = DetectorFinding(name="manifest.valid", passed=False, message="invalid manifest")
            return [DetectorResult(detector="preflight.manifest", score=0.0, findings=[neg])]
    out: list[DetectorResult] = []
    for det in detectors:
        out.append(det(manifest))
    return out
