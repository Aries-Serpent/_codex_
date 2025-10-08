from __future__ import annotations

from importlib import import_module
from typing import Any, Mapping, Optional

from .core import DetectorResult, DetectorFinding

EXPECTED_SYMBOLS = ("train", "resume")


def _check_module() -> tuple[bool, list[DetectorFinding]]:
    try:
        mod = import_module("codex_ml.training.unified_training")
    except Exception as e:
        return (False, [DetectorFinding("module.import", False, f"{e.__class__.__name__}: {e}")])
    findings: list[DetectorFinding] = [DetectorFinding("module.import", True)]
    # soft symbol checks
    for name in EXPECTED_SYMBOLS:
        ok = hasattr(mod, name)
        findings.append(DetectorFinding(f"symbol.{name}", ok, None if ok else "missing"))
    ok_all = all(f.passed for f in findings)
    return (ok_all, findings)


def detect(manifest: Optional[Mapping[str, Any]]) -> DetectorResult:
    ok, findings = _check_module()
    # score: 1.0 if module import ok and all expected symbols present, else 0.5 on import ok, else 0.0
    if not findings or not findings[0].passed:
        score = 0.0
    else:
        missing = [f for f in findings if f.name.startswith("symbol.") and not f.passed]
        score = 1.0 if not missing else 0.5
    tags = ["training", "unified"]
    return DetectorResult(detector="unified_training", score=score, findings=findings, tags=tags)
