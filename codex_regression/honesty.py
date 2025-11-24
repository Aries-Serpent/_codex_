from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

VALID_POLICY_LABELS = {"verified", "inferred", "planned"}
STATUS_MAP = {"pass": "pass", "passed": "pass", "fail": "fail", "failed": "fail", "approved": "pass"}


def validate_honesty_metadata(entries: Iterable[Dict[str, str]]) -> List[str]:
    issues: List[str] = []
    seen = set()
    for idx, entry in enumerate(entries, start=1):
        statement_id = entry.get("statement_id")
        if not statement_id:
            issues.append(f"Entry {idx}: missing statement_id")
            continue
        if statement_id in seen:
            issues.append(f"Entry {idx}: duplicate statement_id {statement_id}")
        seen.add(statement_id)
        required = ["prompt", "response", "timestamp", "source"]
        missing = [field for field in required if not entry.get(field)]
        if missing:
            issues.append(f"Entry {idx}: missing fields {', '.join(missing)}")
        label = entry.get("policy_label", "").lower()
        if label and label not in VALID_POLICY_LABELS:
            issues.append(f"Entry {idx}: invalid policy label {label}")
    return issues


def validate_tool_trace_against_ra(
    tool_traces: Iterable[Dict[str, str]], ra_results: Iterable[Dict[str, str]]
) -> List[str]:
    trace_map = {trace.get("trace_id"): trace for trace in tool_traces if trace.get("trace_id")}
    issues: List[str] = []
    for result in ra_results:
        trace_id = result.get("trace_id")
        if not trace_id:
            issues.append("RA result missing trace_id")
            continue
        trace = trace_map.get(trace_id)
        if not trace:
            issues.append(f"RA result {trace_id} missing tool trace")
            continue
        ra_status = STATUS_MAP.get(result.get("status", "").lower(), "unknown")
        trace_status = STATUS_MAP.get(trace.get("status", "").lower(), "unknown")
        if ra_status != "unknown" and trace_status != "unknown" and ra_status != trace_status:
            issues.append(f"Trace {trace_id} status mismatch: ra={ra_status} trace={trace_status}")
    return issues


def derive_ra_status_from_artifacts(
    artifacts: Iterable[Dict[str, str]], *, allow_missing: bool = False
) -> Tuple[str, Dict[str, int]]:
    counts: Dict[str, int] = {"pass": 0, "fail": 0, "unknown": 0}
    for artifact in artifacts:
        status = STATUS_MAP.get(artifact.get("status", "").lower(), "unknown")
        counts[status] = counts.get(status, 0) + 1
    total = sum(counts.values())
    if total == 0 and not allow_missing:
        raise ValueError("No artifacts provided for RA derivation")
    if counts["fail"]:
        derived = "fail"
    elif counts["pass"]:
        derived = "pass"
    else:
        derived = "unknown"
    return derived, counts
