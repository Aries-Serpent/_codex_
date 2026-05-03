#!/usr/bin/env python3
"""
PDA Loop + AfterMath Failure Pattern Logger
============================================

Records CI failure patterns, applied fixes, and verification outcomes into the
structured PDA (Plan-Do-Act) iterations log at ``.codex/aftermath/pda_iterations.jsonl``.
Also writes to the cognitive brain SQLite ``patterns`` table via ``pattern_recorder.py``
when the DB is accessible.

This closes the feedback loop between CI failures and grounded agent solutions:

    CI fails → pda_failure_logger records pattern + root_cause
             → next session queries --summarize to get proven fix templates
             → agent applies fix → logger records verification outcome
             → grounded solution confidence increases over time

Usage
-----

Log a failure (before fix attempt)::

    python scripts/ci/pda_failure_logger.py log-failure \\
        --session S283 --pr 3854 --branch 0D_base_ \\
        --pattern-id RP-SC2089 \\
        --workflow "Workflow Compliance Audit (actionlint)" \\
        --workflow-run 23910086431 \\
        --error-text "SC2089: Quotes/backslashes in this variable will not be respected" \\
        --root-cause "FILES_ARG built as string; word-split on expansion corrupts args" \\
        --fix-template 'Use Bash arrays: FILES_ARG=(); FILES_ARG+=(--files x); cmd "${FILES_ARG[@]}"'

Log a successful fix verification::

    python scripts/ci/pda_failure_logger.py log-fix \\
        --session S283 --pr 3854 \\
        --pattern-id RP-SC2089 \\
        --fix-applied "Converted FILES_ARG/DRY_FLAG to Bash arrays in workflow-execution-gate.yml" \\
        --verification-cmd "actionlint .github/workflows/workflow-execution-gate.yml" \\
        --verification-passed

Summarize grounded solutions (most-fixed patterns with highest success rate)::

    python scripts/ci/pda_failure_logger.py summarize

    python scripts/ci/pda_failure_logger.py summarize --pattern-id RP-SC2089

Dump all entries for a session::

    python scripts/ci/pda_failure_logger.py dump --session S283

Environment
-----------
    CODEX_DB_PATH      Path to the cognitive brain SQLite database (optional).
    GITHUB_SHA         Git SHA to tag entries (set automatically by Actions).
    GITHUB_RUN_ID      Workflow run ID.
    COPILOT_SESSION_ID Fallback session identifier.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PDA_LOG = _REPO_ROOT / ".codex" / "aftermath" / "pda_iterations.jsonl"
_SOLUTIONS_YAML = _REPO_ROOT / ".codex" / "aftermath" / "failure_pattern_solutions.yaml"
_RECORDER = _REPO_ROOT / "scripts" / "ci" / "pattern_recorder.py"

_DB_PATH = os.environ.get("CODEX_DB_PATH", "")
_GIT_SHA = os.environ.get("GITHUB_SHA", "") or os.environ.get("CODEX_GIT_SHA", "")
_RUN_ID = os.environ.get("GITHUB_RUN_ID", "") or os.environ.get("COPILOT_SESSION_ID", "")


# ---------------------------------------------------------------------------
# Core entry schema
# ---------------------------------------------------------------------------

def _now() -> str:
    # Use hyphen-separated format to ensure Windows-compatible filenames
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%MZ")


def _read_log() -> list[dict[str, Any]]:
    if not _PDA_LOG.exists():
        return []
    entries = []
    for line in _PDA_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            pass  # malformed JSONL line – skip silently
            _ = None  # noqa: BLE001
    return entries


def _append_entry(entry: dict[str, Any]) -> None:
    _PDA_LOG.parent.mkdir(parents=True, exist_ok=True)
    with _PDA_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[pda] ✅ Logged to {_PDA_LOG.relative_to(_REPO_ROOT)}")


def _record_to_sqlite(pattern_id: str, pattern_name: str, description: str,
                       file_path: str = "", line_number: int = 0,
                       auto_fixable: bool = True, fixed: bool = False) -> None:
    """Forward entry to pattern_recorder.py if available."""
    if not _RECORDER.exists():
        return
    args = [
        sys.executable, str(_RECORDER), "insert",
        "--pattern-id", pattern_id,
        "--pattern-name", pattern_name,
        "--description", description,
    ]
    if file_path:
        args += ["--file-path", file_path]
    if line_number:
        args += ["--line", str(line_number)]
    if auto_fixable:
        args.append("--auto-fixable")
    if fixed:
        args.append("--fixed")
    if _DB_PATH:
        args += ["--db", _DB_PATH]
    try:
        subprocess.run(args, capture_output=True, timeout=10)
    except Exception:
        pass  # SQLite record is best-effort; never fail the main flow
        _ = None  # noqa: BLE001


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_log_failure(args: argparse.Namespace) -> int:
    """Record a new CI failure occurrence."""
    entry: dict[str, Any] = {
        "type": "failure",
        "timestamp": _now(),
        "session": args.session or "",
        "pr_number": args.pr or 0,
        "branch": args.branch or "",
        "git_sha": (_GIT_SHA or "")[:12],
        "workflow_run_id": args.workflow_run or _RUN_ID,
        "pattern_id": args.pattern_id,
        "workflow": args.workflow or "",
        "error_text": (args.error_text or "")[:500],
        "root_cause": args.root_cause or "",
        "fix_template": args.fix_template or "",
        "verification_cmd": args.verification_cmd or "",
        "status": "open",
    }
    _append_entry(entry)
    _record_to_sqlite(
        pattern_id=args.pattern_id,
        pattern_name=args.pattern_id,
        description=f"[{args.session}] {args.root_cause or args.error_text or args.pattern_id}",
        auto_fixable=bool(args.fix_template),
        fixed=False,
    )
    return 0


def cmd_log_fix(args: argparse.Namespace) -> int:
    """Record the outcome of a fix attempt for a known pattern."""
    passed = bool(args.verification_passed)
    entry: dict[str, Any] = {
        "type": "fix",
        "timestamp": _now(),
        "session": args.session or "",
        "pr_number": args.pr or 0,
        "branch": args.branch or "",
        "git_sha": (_GIT_SHA or "")[:12],
        "workflow_run_id": _RUN_ID,
        "pattern_id": args.pattern_id,
        "fix_applied": args.fix_applied or "",
        "verification_cmd": args.verification_cmd or "",
        "verification_passed": passed,
        "status": "resolved" if passed else "fix-attempted",
    }
    _append_entry(entry)
    _record_to_sqlite(
        pattern_id=args.pattern_id,
        pattern_name=args.pattern_id,
        description=f"[{args.session}] fix: {args.fix_applied or 'applied'}",
        auto_fixable=True,
        fixed=passed,
    )
    return 0


def cmd_log_session(args: argparse.Namespace) -> int:
    """Record a full session PDA iteration entry (WEC state + outcome summary)."""
    entry: dict[str, Any] = {
        "type": "session",
        "timestamp": _now(),
        "session": args.session,
        "pr_number": args.pr or 0,
        "branch": args.branch or "",
        "git_sha": (_GIT_SHA or "")[:12],
        "plan": {
            "workflows_checked": (args.workflows_checked or "").split(",") if args.workflows_checked else [],
            "workflows_unchecked": (args.workflows_unchecked or "").split(",") if args.workflows_unchecked else [],
        },
        "patterns_fixed": (args.patterns_fixed or "").split(",") if args.patterns_fixed else [],
        "patterns_open": (args.patterns_open or "").split(",") if args.patterns_open else [],
        "ci_checks_green": args.ci_green or 0,
        "ci_checks_red": args.ci_red or 0,
        "lessons": args.lessons or "",
        "status": "complete",
    }
    _append_entry(entry)
    return 0


def cmd_summarize(args: argparse.Namespace) -> int:
    """Print grounded solution summary for CI failure patterns."""
    entries = _read_log()
    if not entries:
        print("No PDA entries found.")
        return 0

    # Build per-pattern stats
    patterns: dict[str, dict[str, Any]] = {}
    for e in entries:
        pid = e.get("pattern_id", "")
        if not pid:
            continue
        if pid not in patterns:
            patterns[pid] = {
                "pattern_id": pid,
                "occurrences": 0,
                "fixes_attempted": 0,
                "fixes_passed": 0,
                "root_causes": [],
                "fix_templates": [],
                "fix_applied_samples": [],
                "verification_cmds": [],
                "last_seen": "",
                "last_session": "",
                "workflows": set(),
            }
        rec = patterns[pid]
        rec["last_seen"] = max(rec["last_seen"], e.get("timestamp", ""))
        rec["last_session"] = e.get("session", rec["last_session"])
        if e["type"] == "failure":
            rec["occurrences"] += 1
            if e.get("root_cause"):
                rec["root_causes"].append(e["root_cause"])
            if e.get("fix_template"):
                rec["fix_templates"].append(e["fix_template"])
            if e.get("workflow"):
                rec["workflows"].add(e["workflow"])
        elif e["type"] == "fix":
            rec["fixes_attempted"] += 1
            if e.get("verification_passed"):
                rec["fixes_passed"] += 1
            if e.get("fix_applied"):
                rec["fix_applied_samples"].append(e["fix_applied"])
            if e.get("verification_cmd"):
                rec["verification_cmds"].append(e["verification_cmd"])

    # Filter if --pattern-id given
    if args.pattern_id:
        patterns = {k: v for k, v in patterns.items() if k == args.pattern_id}

    if not patterns:
        print(f"No entries for pattern '{args.pattern_id}'.")
        return 0

    # Sort by occurrences desc
    sorted_patterns = sorted(patterns.values(), key=lambda x: x["occurrences"], reverse=True)

    print("\n" + "=" * 70)
    print("  PDA Loop — Grounded CI Failure Pattern Solutions")
    print("=" * 70)

    for rec in sorted_patterns:
        success_rate = (
            f"{rec['fixes_passed']}/{rec['fixes_attempted']} "
            f"({100*rec['fixes_passed']//rec['fixes_attempted'] if rec['fixes_attempted'] else 0}%)"
            if rec["fixes_attempted"] else "no fix recorded yet"
        )
        print(f"\n┌─ Pattern: {rec['pattern_id']}")
        print(f"│  Occurrences : {rec['occurrences']}")
        print(f"│  Fix success : {success_rate}")
        print(f"│  Last seen   : {rec['last_seen']}  session={rec['last_session']}")
        if rec["workflows"]:
            print(f"│  Workflows   : {', '.join(sorted(rec['workflows']))}")
        if rec["root_causes"]:
            rc = rec["root_causes"][-1]
            print(f"│  Root cause  : {rc}")
        if rec["fix_templates"]:
            ft = rec["fix_templates"][-1]
            print(f"│  Fix template: {ft}")
        elif rec["fix_applied_samples"]:
            fa = rec["fix_applied_samples"][-1]
            print(f"│  Fix applied : {fa}")
        if rec["verification_cmds"]:
            vc = rec["verification_cmds"][-1]
            print(f"│  Verify with : {vc}")
        print(f"└{'─'*67}")

    print(f"\nTotal patterns tracked: {len(patterns)}")
    print(f"Total PDA entries    : {len(entries)}")
    return 0


def cmd_dump(args: argparse.Namespace) -> int:
    """Dump all PDA entries, optionally filtered by session."""
    entries = _read_log()
    if args.session:
        entries = [e for e in entries if e.get("session") == args.session]
    if args.pr:
        entries = [e for e in entries if e.get("pr_number") == args.pr]
    print(json.dumps(entries, indent=2, ensure_ascii=False))
    return 0


def cmd_export_solutions(args: argparse.Namespace) -> int:
    """Export grounded solutions to YAML for use by agents."""
    try:
        import yaml  # type: ignore[import-untyped]
    except ImportError:
        print("PyYAML not installed; using JSON output instead.")
        yaml = None  # type: ignore[assignment]

    entries = _read_log()
    # Build solution map
    solutions: dict[str, dict[str, Any]] = {}
    for e in entries:
        pid = e.get("pattern_id", "")
        if not pid:
            continue
        if pid not in solutions:
            solutions[pid] = {
                "pattern_id": pid,
                "occurrences": 0,
                "fix_success_rate": 0.0,
                "root_cause": "",
                "fix_template": "",
                "verification_cmd": "",
                "last_session": "",
                "last_seen": "",
            }
        s = solutions[pid]
        s["last_seen"] = max(s["last_seen"], e.get("timestamp", ""))
        s["last_session"] = e.get("session", s["last_session"])
        if e["type"] == "failure":
            s["occurrences"] += 1
            s["root_cause"] = e.get("root_cause") or s["root_cause"]
            s["fix_template"] = e.get("fix_template") or s["fix_template"]
            s["verification_cmd"] = e.get("verification_cmd") or s["verification_cmd"]

    out_path = Path(args.output) if args.output else _SOLUTIONS_YAML
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if yaml is not None:
        out_path.write_text(yaml.dump({"solutions": list(solutions.values())},
                                       default_flow_style=False, allow_unicode=True),
                             encoding="utf-8")
    else:
        out_path.with_suffix(".json").write_text(
            json.dumps({"solutions": list(solutions.values())}, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
    print(f"[pda] Solutions exported to {out_path}")
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="PDA Loop + AfterMath Failure Pattern Logger",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # log-failure
    lf = sub.add_parser("log-failure", help="Record a new CI failure occurrence")
    lf.add_argument("--session", default="")
    lf.add_argument("--pr", type=int, default=0)
    lf.add_argument("--branch", default="")
    lf.add_argument("--pattern-id", required=True, help="e.g. RP-SC2089, RP-019, RP-ZIP-SLIP")
    lf.add_argument("--workflow", default="")
    lf.add_argument("--workflow-run", default="")
    lf.add_argument("--error-text", default="", help="Raw error text (truncated to 500 chars)")
    lf.add_argument("--root-cause", default="", help="Human-readable root cause")
    lf.add_argument("--fix-template", default="", help="Command or code snippet to fix")
    lf.add_argument("--verification-cmd", default="", help="Command to verify fix")

    # log-fix
    lfx = sub.add_parser("log-fix", help="Record a fix attempt outcome")
    lfx.add_argument("--session", default="")
    lfx.add_argument("--pr", type=int, default=0)
    lfx.add_argument("--branch", default="")
    lfx.add_argument("--pattern-id", required=True)
    lfx.add_argument("--fix-applied", default="")
    lfx.add_argument("--verification-cmd", default="")
    lfx.add_argument("--verification-passed", action="store_true")

    # log-session
    ls = sub.add_parser("log-session", help="Record full session PDA iteration")
    ls.add_argument("--session", required=True)
    ls.add_argument("--pr", type=int, default=0)
    ls.add_argument("--branch", default="")
    ls.add_argument("--workflows-checked", default="", help="Comma-separated checked workflows")
    ls.add_argument("--workflows-unchecked", default="", help="Comma-separated unchecked")
    ls.add_argument("--patterns-fixed", default="", help="Comma-separated pattern IDs fixed")
    ls.add_argument("--patterns-open", default="", help="Comma-separated open pattern IDs")
    ls.add_argument("--ci-green", type=int, default=0)
    ls.add_argument("--ci-red", type=int, default=0)
    ls.add_argument("--lessons", default="")

    # summarize
    sm = sub.add_parser("summarize", help="Print grounded solution summary")
    sm.add_argument("--pattern-id", default="", help="Filter to a specific pattern")

    # dump
    dm = sub.add_parser("dump", help="Dump raw PDA log entries")
    dm.add_argument("--session", default="", help="Filter by session ID")
    dm.add_argument("--pr", type=int, default=0, help="Filter by PR number")

    # export-solutions
    ex = sub.add_parser("export-solutions", help="Export YAML solution library")
    ex.add_argument("--output", default="", help="Output path (default: .codex/aftermath/failure_pattern_solutions.yaml)")

    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    dispatch = {
        "log-failure": cmd_log_failure,
        "log-fix": cmd_log_fix,
        "log-session": cmd_log_session,
        "summarize": cmd_summarize,
        "dump": cmd_dump,
        "export-solutions": cmd_export_solutions,
    }
    return dispatch[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
