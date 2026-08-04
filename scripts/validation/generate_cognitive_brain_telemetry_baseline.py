#!/usr/bin/env python3
"""Generate a file-based telemetry baseline report for the Cognitive Brain runtime.

This script performs a static, file-only analysis of
``src/codex/cognitive_brain/**/*.py`` and the matching test suite under
``tests/cognitive_brain/**/*.py``.  It does not require any external
infrastructure, running services, or test execution.

The report is written to ``docs/validation/COGNITIVE_BRAIN_TELEMETRY_BASELINE.md``.
"""

from __future__ import annotations

import ast
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "src" / "codex" / "cognitive_brain"
TEST_DIR = REPO_ROOT / "tests" / "cognitive_brain"
OUTPUT_PATH = REPO_ROOT / "docs" / "validation" / "COGNITIVE_BRAIN_TELEMETRY_BASELINE.md"

FORENSICS_FIELDS = ("decision_id", "turn_id", "task_id")


# ---------------------------------------------------------------------------
# AST scanners
# ---------------------------------------------------------------------------


class TelemetryVisitor(ast.NodeVisitor):
    """Collect telemetry usage and forensics-field population from a Python module."""

    def __init__(self) -> None:
        self.record_calls = 0
        self.cogtel_ctors = 0
        self.event_ctors = 0
        self.event_types: Dict[Optional[str], int] = defaultdict(int)
        self.session_guard_records = 0
        self.forensics_events: List[Dict[str, Any]] = []

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        name = _call_name(node.func)

        if name.endswith(".record"):
            self.record_calls += 1
            if self._is_session_guard_record(node):
                self.session_guard_records += 1

        if name == "CognitiveTelemetry":
            self.cogtel_ctors += 1

        if name == "TelemetryEvent":
            self.event_ctors += 1
            kw: Dict[str, Any] = {kw.arg: _literal(kw.value) for kw in node.keywords if kw.arg}
            event_type = kw.get("event_type")
            if isinstance(event_type, str):
                self.event_types[event_type] += 1

            present = [f for f in FORENSICS_FIELDS if f in kw]
            self.forensics_events.append(
                {
                    "event_type": event_type,
                    "present_fields": present,
                    "all_present": all(f in kw for f in FORENSICS_FIELDS),
                }
            )

        self.generic_visit(node)

    def _is_session_guard_record(self, node: ast.Call) -> bool:
        """Detect ``telemetry.record(TelemetryEvent(event_type='session_guard'))``."""
        if not node.args:
            return False
        first_arg = node.args[0]
        if not isinstance(first_arg, ast.Call):
            return False
        if _call_name(first_arg.func) != "TelemetryEvent":
            return False
        for kw in first_arg.keywords:
            if kw.arg == "event_type" and _literal(kw.value) == "session_guard":
                return True
        return False


class ShellVerdictVisitor(ast.NodeVisitor):
    """Count references to ``PolicyVerdict.DENY``, ``ALLOW``, and ``AUDIT``."""

    def __init__(self) -> None:
        self.deny = 0
        self.allow = 0
        self.audit = 0

    def visit_Attribute(self, node: ast.Attribute) -> None:  # noqa: N802
        if isinstance(node.value, ast.Name) and node.value.id == "PolicyVerdict":
            if node.attr == "DENY":
                self.deny += 1
            elif node.attr == "ALLOW":
                self.allow += 1
            elif node.attr == "AUDIT":
                self.audit += 1
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _call_name(func: ast.expr) -> str:
    if isinstance(func, ast.Attribute):
        parts: List[str] = []
        node: ast.expr = func
        while isinstance(node, ast.Attribute):
            parts.append(node.attr)
            node = node.value
        if isinstance(node, ast.Name):
            parts.append(node.id)
        return ".".join(reversed(parts))
    if isinstance(func, ast.Name):
        return func.id
    return ""


def _literal(node: ast.expr) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.List):
        return [_literal(e) for e in node.elts]
    if isinstance(node, ast.Dict):
        return {_literal(k): _literal(v) for k, v in zip(node.keys, node.values)}
    return "..."


def walk_files(root: Path) -> List[Path]:
    return sorted(root.rglob("*.py")) if root.exists() else []


def analyze_directory(root: Path) -> Dict[str, Any]:
    """Return aggregate metrics for ``root``."""
    totals: Dict[str, Any] = {
        "record_calls": 0,
        "cogtel_ctors": 0,
        "event_ctors": 0,
        "event_types": defaultdict(int),
        "session_guard_records": 0,
        "forensics_events": [],
        "files": {},
    }

    for py_file in walk_files(root):
        rel = str(py_file.relative_to(REPO_ROOT))
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            totals["files"][rel] = {"error": str(exc)}
            continue

        visitor = TelemetryVisitor()
        visitor.visit(tree)

        file_summary = {
            "record_calls": visitor.record_calls,
            "cogtel_ctors": visitor.cogtel_ctors,
            "event_ctors": visitor.event_ctors,
            "event_types": dict(visitor.event_types),
            "session_guard_records": visitor.session_guard_records,
            "forensics_all": sum(1 for e in visitor.forensics_events if e["all_present"]),
            "forensics_total": len(visitor.forensics_events),
        }
        totals["files"][rel] = file_summary

        totals["record_calls"] += visitor.record_calls
        totals["cogtel_ctors"] += visitor.cogtel_ctors
        totals["event_ctors"] += visitor.event_ctors
        totals["session_guard_records"] += visitor.session_guard_records
        for et, count in visitor.event_types.items():
            totals["event_types"][et] += count
        totals["forensics_events"].extend(visitor.forensics_events)

    totals["event_types"] = dict(totals["event_types"])
    return totals


def analyze_shell_policy(path: Path) -> Dict[str, int]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    visitor = ShellVerdictVisitor()
    visitor.visit(tree)
    return {"DENY": visitor.deny, "ALLOW": visitor.allow, "AUDIT": visitor.audit}


def percentage(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return (numerator / denominator) * 100.0


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def build_report(src: Dict[str, Any], tests: Dict[str, Any]) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    total_record_calls = src["record_calls"] + tests["record_calls"]
    total_cogtel_ctors = src["cogtel_ctors"] + tests["cogtel_ctors"]
    total_event_ctors = src["event_ctors"] + tests["event_ctors"]
    total_events = total_record_calls + total_cogtel_ctors + total_event_ctors

    src_forensics_all = sum(1 for e in src["forensics_events"] if e["all_present"])
    src_forensics_total = len(src["forensics_events"])
    tests_forensics_all = sum(1 for e in tests["forensics_events"] if e["all_present"])
    tests_forensics_total = len(tests["forensics_events"])
    combined_forensics_all = src_forensics_all + tests_forensics_all
    combined_forensics_total = src_forensics_total + tests_forensics_total
    forensics_completeness_rate = percentage(combined_forensics_all, combined_forensics_total)

    total_session_guard_records = src["session_guard_records"] + tests["session_guard_records"]
    session_guard_interception_rate = percentage(total_session_guard_records, total_event_ctors)

    shell_verdicts = analyze_shell_policy(SRC_DIR / "shell_policy.py")
    total_verdicts = sum(shell_verdicts.values())

    lines: List[str] = []
    lines.append("# Cognitive Brain Telemetry Baseline")
    lines.append("")
    lines.append(f"**Generated:** {generated_at}")
    lines.append("")
    lines.append(
        "This baseline is produced by a static, file-only scan of the Cognitive Brain "
        "source tree and its test suite.  It estimates telemetry event volume, "
        "forensics completeness, session-guard interception, and shell-policy verdict "
        "distribution without requiring external infrastructure or test execution."
    )
    lines.append("")

    # Summary table
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---|")
    lines.append(f"| Source files scanned | {len(walk_files(SRC_DIR))} |")
    lines.append(f"| Test files scanned | {len(walk_files(TEST_DIR))} |")
    lines.append(f"| ``telemetry.record`` calls (src + tests) | {total_record_calls} |")
    lines.append(f"| ``CognitiveTelemetry`` instantiations (src + tests) | {total_cogtel_ctors} |")
    lines.append(f"| ``TelemetryEvent`` constructions (src + tests) | {total_event_ctors} |")
    lines.append(f"| Decision event volume estimate | {total_events} |")
    lines.append(
        f"| Forensics completeness rate | {forensics_completeness_rate:.1f}% "
        f"({combined_forensics_all}/{combined_forensics_total}) |"
    )
    lines.append(
        f"| Session Guard interception rate | {session_guard_interception_rate:.1f}% "
        f"({total_session_guard_records}/{total_event_ctors}) |"
    )
    lines.append(f"| Shell verdict references (source) | {total_verdicts} |")
    lines.append("")

    # Decision Event Volume table
    lines.append("## Decision Event Volume")
    lines.append("")
    lines.append(
        "Estimated volume is the sum of ``telemetry.record`` calls, "
        "``CognitiveTelemetry`` instantiations, and ``TelemetryEvent`` constructions "
        "detected in each file."
    )
    lines.append("")
    lines.append(
        "| Source File | record calls | CognitiveTelemetry ctor | " "TelemetryEvent ctor | Volume |"
    )
    lines.append("|---|---|---|---|---|")

    def _volume_rows(scope: Dict[str, Any]) -> None:
        for rel, data in sorted(scope["files"].items()):
            if "error" in data:
                lines.append(f"| {rel} | parse error | parse error | parse error | parse error |")
                continue
            vol = data["record_calls"] + data["cogtel_ctors"] + data["event_ctors"]
            if vol == 0:
                continue
            lines.append(
                f"| {rel} | {data['record_calls']} | {data['cogtel_ctors']} | "
                f"{data['event_ctors']} | {vol} |"
            )

    _volume_rows(src)
    lines.append("")

    # Forensics Completeness table
    lines.append("## Forensics Completeness")
    lines.append("")
    lines.append(
        "A ``TelemetryEvent`` is considered forensics-complete when ``decision_id``, "
        "``turn_id``, and ``task_id`` are all explicitly populated at the construction "
        "site."
    )
    lines.append("")
    lines.append("| Scope | Events with all fields | Total events | Completeness |")
    lines.append("|---|---|---|---|")
    lines.append(
        f"| Source | {src_forensics_all} | {src_forensics_total} | "
        f"{percentage(src_forensics_all, src_forensics_total):.1f}% |"
    )
    lines.append(
        f"| Tests | {tests_forensics_all} | {tests_forensics_total} | "
        f"{percentage(tests_forensics_all, tests_forensics_total):.1f}% |"
    )
    lines.append(
        f"| Combined | {combined_forensics_all} | {combined_forensics_total} | "
        f"{forensics_completeness_rate:.1f}% |"
    )
    lines.append("")

    # Session Guard Interception Rate table
    lines.append("## Session Guard Interception Rate")
    lines.append("")
    lines.append(
        "The interception rate is the share of ``TelemetryEvent`` constructions that "
        "are emitted through ``SessionGuard`` (``event_type='session_guard'``) versus "
        "all ``TelemetryEvent`` constructions detected in source and tests."
    )
    lines.append("")
    lines.append("| Scope | session_guard events | Total TelemetryEvent constructions | Rate |")
    lines.append("|---|---|---|---|")
    src_events = src["event_ctors"]
    tests_events = tests["event_ctors"]
    lines.append(
        f"| Source | {src['session_guard_records']} | {src_events} | "
        f"{percentage(src['session_guard_records'], src_events):.1f}% |"
    )
    lines.append(
        f"| Tests | {tests['session_guard_records']} | {tests_events} | "
        f"{percentage(tests['session_guard_records'], tests_events):.1f}% |"
    )
    lines.append(
        f"| Combined | {total_session_guard_records} | {total_event_ctors} | "
        f"{session_guard_interception_rate:.1f}% |"
    )
    lines.append("")

    # Shell Verdict Distribution table
    lines.append("## Shell Verdict Distribution")
    lines.append("")
    lines.append(
        "Verdict counts are static references to ``PolicyVerdict.DENY``, "
        "``PolicyVerdict.ALLOW``, and ``PolicyVerdict.AUDIT`` in ``shell_policy.py``."
    )
    lines.append("")
    lines.append("| Verdict | Count | Share |")
    lines.append("|---|---|---|")
    for verdict in ("DENY", "ALLOW", "AUDIT"):
        count = shell_verdicts[verdict]
        share = percentage(count, total_verdicts)
        lines.append(f"| {verdict} | {count} | {share:.1f}% |")
    lines.append(f"| **Total** | **{total_verdicts}** | **100.0%** |")
    lines.append("")

    # Methodology
    lines.append("## Methodology")
    lines.append("")
    lines.append(
        "1. **Walk** ``src/codex/cognitive_brain/**/*.py`` and "
        "``tests/cognitive_brain/**/*.py``."
    )
    lines.append(
        "2. **Parse** each file with the Python ``ast`` module; skip files that fail " "to parse."
    )
    lines.append(
        "3. **Count** ``telemetry.record(...)`` call sites, "
        "``CognitiveTelemetry(...)`` instantiations, and ``TelemetryEvent(...)`` "
        "constructions."
    )
    lines.append(
        "4. **Inspect** each ``TelemetryEvent(...)`` keyword argument list.  Count "
        "events where ``decision_id``, ``turn_id``, and ``task_id`` are all "
        "explicitly provided."
    )
    lines.append(
        "5. **Detect** ``session_guard`` interception by looking for "
        "``telemetry.record(TelemetryEvent(event_type='session_guard', ...))``."
    )
    lines.append(
        "6. **Analyze** ``src/codex/cognitive_brain/shell_policy.py`` for references "
        "to ``PolicyVerdict.DENY``, ``PolicyVerdict.ALLOW``, and "
        "``PolicyVerdict.AUDIT``."
    )
    lines.append("7. **Emit** this markdown report with the generated UTC timestamp.")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    src = analyze_directory(SRC_DIR)
    tests = analyze_directory(TEST_DIR)
    report = build_report(src, tests)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
