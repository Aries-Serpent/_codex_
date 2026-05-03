from __future__ import annotations

import dataclasses
import datetime as _dt
import json
import pathlib
from collections.abc import Iterable
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts"
ARTIFACTS.mkdir(exist_ok=True)
REGRESSION_LOG = ARTIFACTS / "model_regression_log.ndjson"

REGRESSION_CATEGORIES: dict[str, str] = {
    "R1": "Data integrity and determinism",
    "R2": "Model initialization and adapters",
    "R3": "Infrastructure and training loops",
    "R4": "Performance and resource posture",
    "R5": "Safety, policy, and honesty",
}


@dataclasses.dataclass
class RegressionRun:
    category: str
    name: str
    status: str
    duration_s: float | None = None
    details: str | None = None
    timestamp: str = dataclasses.field(
        default_factory=lambda: _dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    )
    metadata: dict[str, Any] = dataclasses.field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "name": self.name,
            "status": self.status,
            "duration_s": self.duration_s,
            "details": self.details,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }


def record_regression(run: RegressionRun) -> None:
    if run.category not in REGRESSION_CATEGORIES:
        raise ValueError(f"Unknown regression category: {run.category}")
    payload = run.as_dict()
    REGRESSION_LOG.parent.mkdir(exist_ok=True)
    with REGRESSION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(payload) + "\n")


def load_regression_log() -> list[dict[str, Any]]:
    if not REGRESSION_LOG.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in REGRESSION_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


def summarize_by_category(entries: Iterable[dict[str, Any]]) -> dict[str, dict[str, int]]:
    summary: dict[str, dict[str, int]] = {k: {} for k in REGRESSION_CATEGORIES}
    for entry in entries:
        category = entry.get("category")
        status = entry.get("status", "unknown")
        if category not in summary:
            continue
        bucket = summary[category]
        bucket[status] = bucket.get(status, 0) + 1
    return summary


def write_coverage_report(entries: Iterable[dict[str, Any]]) -> pathlib.Path:
    summary = summarize_by_category(entries)
    lines = [
        "# Model Regression Coverage",
        "",
        "| Category | Description | Pass | Fail | Skip |",
        "| --- | --- | --- | --- | --- |",
    ]
    for cat, desc in REGRESSION_CATEGORIES.items():
        bucket = summary.get(cat, {})
        lines.append(
            f"| {cat} | {desc} | {bucket.get('passed', 0)} | {bucket.get('failed', 0)} | {bucket.get('skipped', 0)} |"
        )
    report_path = ARTIFACTS / "model_regression_coverage.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path
