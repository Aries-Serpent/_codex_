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

Log a caller-labelled fix verification (not independent execution evidence)::

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
import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

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
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_log() -> list[Any]:
    """Read without migration; retain malformed JSON verbatim for raw dumps."""
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
            entries.append({"_pda_parse_error": True, "raw_record": line})
    return entries


def _aware_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = datetime.strptime(value, "%Y-%m-%dT%H-%MZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return None
    if parsed.tzinfo is None:
        return None
    try:
        return parsed.astimezone(timezone.utc)
    except (ValueError, OverflowError):
        return None


def _timestamp(value: Any) -> str:
    parsed = _aware_timestamp(value)
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ") if parsed is not None else ""


def _text(entry: dict[str, Any], key: str) -> str:
    value = entry.get(key)
    return value if isinstance(value, str) else ""


def _classify(entry: Any) -> str:
    if not isinstance(entry, dict) or entry.get("_pda_parse_error"):
        return "malformed"
    version = entry.get("schema_version")
    if version is not None and (type(version) is not int or version != 1):
        return "unsupported_schema"
    if entry.get("classification") == "solution_export":
        return "export"
    kind = entry.get("type")
    if kind is None:
        return "unknown"
    if not isinstance(kind, str):
        return "malformed"
    if kind in {"session", "session_loop", "test"}:
        return "test" if kind == "test" else "session"
    kinds = {
        "failure": "failure",
        "fix": "caller_labelled_repair",
        "repair_success": "caller_labelled_repair",
        "attempt": "attempt",
        "repair_attempt": "attempt",
        "result": "unverified_result",
        "verification_result": "unverified_result",
    }
    category = kinds.get(kind, "unknown")
    if category != "unknown" and not _text(entry, "pattern_id"):
        return "malformed"
    for field in ("verification_passed", "success", "verified"):
        if field in entry and type(entry[field]) is not bool:
            return "malformed"
    if category in {"attempt", "unverified_result"} and not _text(entry, "attempt_id"):
        return "malformed"
    return category


def _aggregate(entries: list[Any]) -> tuple[dict[str, dict[str, Any]], dict[str, int]]:
    """Separate caller labels from uniquely linked, explicitly verified results.

    This adapter does not execute verification. ``verified_result`` describes
    supplied record evidence, not proof that a hosted command ran. Joins require
    explicit matching session, commit and workflow-run identities and a strictly
    later aware result timestamp. Missing or ambiguous evidence stays unverified.
    Unsupported schemas/types remain visible; no raw entry is rewritten.
    """
    categories = [_classify(entry) for entry in entries]
    counts = dict.fromkeys(
        (
            "failure",
            "caller_labelled_repair",
            "attempt",
            "verified_result",
            "unverified_result",
            "session",
            "test",
            "unknown",
            "malformed",
            "unsupported_schema",
            "export",
            "unknown_timestamp",
        ),
        0,
    )
    links: dict[tuple[str, str, str], dict[str, list[int]]] = {}
    for index, (entry, category) in enumerate(zip(entries, categories)):
        if category not in {"attempt", "unverified_result"}:
            continue
        key = (
            _text(entry, "pattern_id"),
            _text(entry, "session"),
            _text(entry, "attempt_id"),
        )
        link = links.setdefault(key, {"attempts": [], "results": []})
        link["attempts" if category == "attempt" else "results"].append(index)
    for link in links.values():
        if len(link["attempts"]) != 1 or len(link["results"]) != 1:
            continue
        result_index = link["results"][0]
        result = entries[result_index]
        attempt = entries[link["attempts"][0]]
        identity_matches = all(
            _text(attempt, field).strip() and _text(attempt, field) == _text(result, field)
            for field in ("session", "git_sha", "workflow_run_id")
        )
        attempt_time = _aware_timestamp(attempt.get("timestamp"))
        result_time = _aware_timestamp(result.get("timestamp"))
        chronological = (
            attempt_time is not None and result_time is not None and attempt_time < result_time
        )
        outcome = result.get("success", result.get("verification_passed"))
        conflicting = (
            "success" in result
            and "verification_passed" in result
            and result["success"] != result["verification_passed"]
        )
        if (
            identity_matches
            and chronological
            and result.get("verified") is True
            and type(outcome) is bool
            and not conflicting
        ):
            categories[result_index] = "verified_result"

    patterns: dict[str, dict[str, Any]] = {}
    for entry, category in zip(entries, categories):
        counts[category] += 1
        timestamp = _timestamp(entry.get("timestamp")) if isinstance(entry, dict) else ""
        counts["unknown_timestamp"] += int(not timestamp)
        if category in {"session", "test", "malformed", "unsupported_schema", "export"}:
            continue
        pid = _text(entry, "pattern_id")
        if not pid:
            continue
        rec = patterns.setdefault(
            pid,
            {
                "pattern_id": pid,
                "occurrences": 0,
                "fixes_attempted": 0,
                "fixes_passed": 0,
                "verified_attempts": 0,
                "verified_successes": 0,
                "unknown_records": 0,
                "root_causes": [],
                "fix_templates": [],
                "fix_applied_samples": [],
                "verification_cmds": [],
                "last_seen": "",
                "last_session": "",
                "workflows": set(),
            },
        )
        if timestamp and timestamp >= rec["last_seen"]:
            rec["last_seen"] = timestamp
            rec["last_session"] = _text(entry, "session")
        if category == "failure":
            rec["occurrences"] += 1
            for field, target in (
                ("root_cause", "root_causes"),
                ("fix_template", "fix_templates"),
                ("verification_cmd", "verification_cmds"),
            ):
                if value := _text(entry, field):
                    rec[target].append(value)
            if workflow := _text(entry, "workflow"):
                rec["workflows"].add(workflow)
        elif category == "caller_labelled_repair":
            rec["fixes_attempted"] += 1
            rec["fixes_passed"] += int(
                entry.get("verification_passed") is True
                or ("verification_passed" not in entry and entry.get("success") is True)
            )
            if value := _text(entry, "fix_applied"):
                rec["fix_applied_samples"].append(value)
            if value := _text(entry, "verification_cmd"):
                rec["verification_cmds"].append(value)
        elif category == "verified_result":
            rec["verified_attempts"] += 1
            rec["verified_successes"] += int(
                entry.get("success", entry.get("verification_passed")) is True
            )
        elif category in {"unknown", "unverified_result"}:
            rec["unknown_records"] += 1
    for rec in patterns.values():
        rec["caller_labelled_success_rate"] = (
            rec["fixes_passed"] / rec["fixes_attempted"] if rec["fixes_attempted"] else None
        )
        rec["fix_success_rate"] = (
            rec["verified_successes"] / rec["verified_attempts"]
            if rec["verified_attempts"]
            else None
        )
        rec["classification"] = "verified_result" if rec["verified_attempts"] else "unknown"
    return patterns, counts


def _append_entry(entry: dict[str, Any]) -> None:
    entry = {"schema_version": 1, **entry}
    _PDA_LOG.parent.mkdir(parents=True, exist_ok=True)
    with _PDA_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"[pda] ✅ Logged to {_PDA_LOG}")


def _record_to_sqlite(
    pattern_id: str,
    pattern_name: str,
    description: str,
    file_path: str = "",
    line_number: int = 0,
    auto_fixable: bool = True,
    fixed: bool = False,
) -> None:
    """Forward entry to pattern_recorder.py if available."""
    if not _RECORDER.exists():
        return
    args = [
        sys.executable,
        str(_RECORDER),
        "insert",
        "--pattern-id",
        pattern_id,
        "--pattern-name",
        pattern_name,
        "--description",
        description,
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
        logger.debug("Suppressed exception in handler", exc_info=True)


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
            "workflows_checked": (
                (args.workflows_checked or "").split(",") if args.workflows_checked else []
            ),
            "workflows_unchecked": (
                (args.workflows_unchecked or "").split(",") if args.workflows_unchecked else []
            ),
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

    patterns, counts = _aggregate(entries)
    print("Record classification: " + json.dumps(counts, sort_keys=True))

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
            if rec["fixes_attempted"]
            else "no fix recorded yet"
        )
        print(f"\n┌─ Pattern: {rec['pattern_id']}")
        print(f"│  Occurrences : {rec['occurrences']}")
        print(f"│  Fix success : {success_rate} (caller-labelled only)")
        rate = rec["fix_success_rate"]
        print(
            f"│  Verified    : {rec['verified_successes']}/{rec['verified_attempts']} "
            f"rate={rate if rate is not None else 'unknown'}"
        )
        print(f"│  Unknown     : {rec['unknown_records']}")
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
        entries = [e for e in entries if isinstance(e, dict) and e.get("session") == args.session]
    if args.pr:
        entries = [e for e in entries if isinstance(e, dict) and e.get("pr_number") == args.pr]
    print(json.dumps(entries, indent=2, ensure_ascii=False))
    return 0


def cmd_export_solutions(args: argparse.Namespace) -> int:
    """Export grounded solutions to YAML for use by agents."""
    try:
        import yaml
    except ImportError:
        print("PyYAML not installed; using JSON output instead.")
        yaml = None

    entries = _read_log()
    patterns, counts = _aggregate(entries)
    solutions = []
    for rec in patterns.values():
        solution = {
            key: value
            for key, value in rec.items()
            if key
            not in {
                "root_causes",
                "fix_templates",
                "fix_applied_samples",
                "verification_cmds",
                "workflows",
            }
        }
        for field, source in (
            ("root_cause", "root_causes"),
            ("fix_template", "fix_templates"),
            ("verification_cmd", "verification_cmds"),
        ):
            solution[field] = rec[source][-1] if rec[source] else ""
        solutions.append(solution)
    payload = {
        "schema_version": 1,
        "classification": "solution_export",
        "record_counts": counts,
        "total_records": len(entries),
        "rate_semantics": {
            "fix_success_rate": "verified_successes / verified_attempts; null means unknown",
            "caller_labelled_success_rate": "fixes_passed / fixes_attempted; caller labels only",
        },
        "solutions": solutions,
    }

    out_path = Path(args.output) if args.output else _SOLUTIONS_YAML
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if yaml is not None:
        out_path.write_text(
            yaml.dump(payload, default_flow_style=False, allow_unicode=True), encoding="utf-8"
        )
    else:
        out_path = out_path.with_suffix(".json")
        out_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False),
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
    ex.add_argument(
        "--output",
        default="",
        help="Output path (default: .codex/aftermath/failure_pattern_solutions.yaml)",
    )

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
