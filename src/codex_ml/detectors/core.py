"""Lightweight detector primitives and helpers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Callable, Iterable, Mapping, Optional

try:  # optional dependency: schema helpers may not exist in older branches
    from codex_ml.checkpointing import schema_v2 as _schema
except Exception:  # pragma: no cover - tolerate missing checkpoint schema
    _schema = None  # type: ignore[assignment]

Json = Mapping[str, Any]


@dataclass(frozen=True)
class DetectorFinding:
    """A single check emitted by a detector."""

    name: str
    passed: bool
    message: str | None = None


@dataclass(frozen=True)
class DetectorResult:
    """Top-level detector outcome."""

    detector: str
    score: float  # [0, 1]
    findings: list[DetectorFinding] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    extras: dict[str, Any] = field(default_factory=dict)


def as_dict(result: DetectorResult) -> dict[str, Any]:
    """Convert a :class:`DetectorResult` into a JSON-serialisable dict."""

    return asdict(result)


def from_dict(data: Json) -> DetectorResult:
    """Create a :class:`DetectorResult` from a dictionary payload."""

    findings = [DetectorFinding(**finding) for finding in data.get("findings", [])]
    return DetectorResult(
        detector=data["detector"],
        score=float(data["score"]),
        findings=findings,
        tags=list(data.get("tags", [])),
        extras=dict(data.get("extras", {})),
    )


Detector = Callable[[Optional[Json]], DetectorResult]


def run_detectors(
    detectors: Iterable[Detector],
    manifest: Optional[Json] = None,
) -> list[DetectorResult]:
    """Execute ``detectors`` and return their results."""

    if manifest is not None and _schema is not None:
        try:
            _schema.validate_manifest(manifest)
        except Exception:
            neg = DetectorFinding(name="manifest.valid", passed=False, message="invalid manifest")
            return [DetectorResult(detector="preflight.manifest", score=0.0, findings=[neg])]

    return [detector(manifest) for detector in detectors]


__all__ = [
    "DetectorFinding",
    "DetectorResult",
    "Detector",
    "as_dict",
    "from_dict",
    "run_detectors",
]
