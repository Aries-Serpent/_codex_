"""
Golden Harness Status Module

This module provides functionality for golden harness status.

Usage:
    from codex_harness.golden_harness_status import ...

Classes:
    [To be documented]

Functions:
    [To be documented]

Author: Codex Team
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_STATUS_PASS = {
    "pass",
    "passed",
    "ok",
    "success",
    "green",
    "approved",
    "true",
    "1",
    "yes",
}
_STATUS_FAIL = {
    "fail",
    "failed",
    "block",
    "blocked",
    "reject",
    "red",
    "false",
    "0",
    "no",
}


@dataclass
class HarnessSignal:
    name: str
    status: str
    detail: str

    def to_dict(self) -> dict[str, str]:
        return {"name": self.name, "status": self.status, "detail": self.detail}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_status(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    lowered = str(value).lower()
    if lowered in _STATUS_PASS:
        return True
    if lowered in _STATUS_FAIL:
        return False
    return None


def _load_json_if_exists(path: Path) -> Any:
    if not path or not path.exists():
        return None
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _evaluate_ra_policy(policy: Any) -> HarnessSignal:
    if not policy:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="Responsible AI policy outcomes missing; defaulting to caution.",
        )
    statuses: list[bool] = []
    if isinstance(policy, dict):
        if "policies" in policy:
            statuses.extend(
                [_normalize_status(p.get("status")) for p in policy.get("policies", [])]  # type: ignore[misc]
            )
        if "results" in policy:
            statuses.extend([_normalize_status(p.get("status")) for p in policy.get("results", [])])  # type: ignore[misc]
        if "status" in policy:
            statuses.append(_normalize_status(policy.get("status")))  # type: ignore[arg-type]
        if not statuses:
            statuses.extend(
                [_normalize_status(v) for v in policy.values() if not isinstance(v, (dict, list))]  # type: ignore[misc]
            )
    if not statuses:
        return HarnessSignal(
            name="ra_policy",
            status="yellow",
            detail="No normalized policy statuses found; treating as partial coverage.",
        )
    failing = [s for s in statuses if s is False]
    if failing:
        return HarnessSignal(
            name="ra_policy",
            status="red",
            detail="At least one RA gate failed.",
        )
    return HarnessSignal(
        name="ra_policy", status="green", detail="RA policies reported pass states."
    )


def _extract_gate_mapping(payload: Any) -> dict[str, bool | None]:
    mapping: dict[str, bool | None] = {}
    if isinstance(payload, dict) and "gates" in payload:
        for entry in payload.get("gates", []):
            if not isinstance(entry, dict) or "tool" not in entry:
                continue
            mapping[entry["tool"]] = _normalize_status(entry.get("status") or entry.get("result"))
    elif isinstance(payload, dict):
        mapping = {k: _normalize_status(v) for k, v in payload.items()}
    return mapping


def _evaluate_honesty(path: Path) -> HarnessSignal:
    data = _load_json_if_exists(path)
    if not data:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata not found; unable to confirm workflow statements.",
        )
    statements = data.get("statements") or []
    if not isinstance(statements, list) or not statements:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Honesty metadata present but contains no statements.",
        )
    missing_fields = [
        idx
        for idx, stmt in enumerate(statements)
        if not stmt.get("content") or stmt.get("category") is None or "verified" not in stmt
    ]
    if missing_fields:
        return HarnessSignal(
            name="honesty_metadata",
            status="yellow",
            detail="Some honesty statements are incomplete; review required.",
        )
    return HarnessSignal(
        name="honesty_metadata",
        status="green",
        detail="Honesty statements recorded and complete.",
    )


def _evaluate_tool_trace(trace_path: Path, gate_path: Path | None) -> HarnessSignal:
    if not trace_path.exists():
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail="Tool trace not found; cannot confirm local tool coverage.",
        )
    entries: list[dict[str, Any]] = []
    for line in trace_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entries.append(json.loads(line))
    if not entries:
        return HarnessSignal(name="tool_trace", status="yellow", detail="Tool trace is empty.")

    gate_mapping: dict[str, bool | None] = {}
    if gate_path and gate_path.exists():
        gate_payload = _load_json_if_exists(gate_path)
        gate_mapping = _extract_gate_mapping(gate_payload)

    gate_mismatches = [e for e in entries if e.get("ra_gate_match") is False]
    missing_expected: list[str] = []
    if gate_mapping:
        observed = {e.get("tool") for e in entries}
        missing_expected = sorted({tool for tool in gate_mapping if tool not in observed})

    if gate_mismatches:
        return HarnessSignal(
            name="tool_trace",
            status="red",
            detail="RA gate mismatch detected in tool trace entries.",
        )
    if missing_expected:
        return HarnessSignal(
            name="tool_trace",
            status="yellow",
            detail=f"Missing tool trace entries for: {', '.join(missing_expected)}.",
        )
    return HarnessSignal(name="tool_trace", status="green", detail="Tool invocations captured.")


def compute_golden_harness_status(
    *,
    ra_policy_path: Path | None = Path("artifacts/gates/ra_policy.json"),
    honesty_path: Path = Path("artifacts/honesty_metadata.json"),
    tool_trace_path: Path = Path("artifacts/tool_trace.ndjson"),
    ra_gate_path: Path | None = Path("artifacts/gates/ra_gate_results.json"),
    output_path: Path = Path("golden_harness_status.json"),
) -> dict[str, Any]:
    ra_policy = _load_json_if_exists(ra_policy_path) if ra_policy_path else None
    signals = [
        _evaluate_ra_policy(ra_policy),
        _evaluate_honesty(honesty_path),
        _evaluate_tool_trace(tool_trace_path, ra_gate_path),
    ]
    overall = "green"
    if any(sig.status == "red" for sig in signals):
        overall = "red"
    elif any(sig.status == "yellow" for sig in signals):
        overall = "yellow"
    payload = {
        "generated_at": _utc_now(),
        "overall_status": overall,
        "signals": [sig.to_dict() for sig in signals],
        "inputs": {
            "ra_policy_path": str(ra_policy_path) if ra_policy_path else None,
            "honesty_path": str(honesty_path),
            "tool_trace_path": str(tool_trace_path),
            "ra_gate_path": str(ra_gate_path) if ra_gate_path else None,
        },
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return payload


__all__ = ["HarnessSignal", "compute_golden_harness_status"]
