#!/usr/bin/env python3
"""
CI Pattern Pipeline — Phase 6 Orchestrator

Runs the complete detect → fix → record → report pipeline in a single invocation.
This is the recommended entry point for CI workflows and Copilot agent sessions.

Pipeline stages
---------------
1. **Detect**   — ``auto_fix_common_issues.py --check-only --json-output <tmp>``
2. **Fix**      — ``auto_fix_common_issues.py --json-output <tmp>`` (skip in check-only mode)
3. **Record**   — ``pattern_recorder.py record --report <tmp>``
4. **Report**   — print human-readable summary + write structured JSON artefact

Usage
-----
    # Full pipeline (detect + fix + record + report):
    python scripts/ci/ci_pattern_pipeline.py

    # Check-only (detect + record + report, no fixes applied):
    python scripts/ci/ci_pattern_pipeline.py --check-only

    # Write structured JSON artefact for downstream consumers:
    python scripts/ci/ci_pattern_pipeline.py --artefact .codex/pipeline-report.json

    # Restrict to specific patterns:
    python scripts/ci/ci_pattern_pipeline.py --pattern 18

    # Dry-run (show what would be fixed without touching files):
    python scripts/ci/ci_pattern_pipeline.py --dry-run

Environment variables
---------------------
    CODEX_DB_PATH           Cognitive brain DB (default: ~/.codex/cli_history.db)
    CODEX_GIT_SHA / GITHUB_SHA   Git SHA for audit trail
    GITHUB_RUN_ID / COPILOT_SESSION_ID   Session identifier
    CODEX_PIPELINE_STRICT   Exit 1 if any auto-fixable issues remain after fixes
                            (default: 0 — informational only)

Exit codes
----------
    0   All checks passed (or --check-only with no auto-fixable issues)
    1   Auto-fixable issues remain after fix attempt (only when --strict or
        CODEX_PIPELINE_STRICT=1) **or** when --check-only finds fixable issues
        and CODEX_PIPELINE_STRICT=1
    2   Internal error (missing dependency, DB write failure, etc.)
"""

from __future__ import annotations

import argparse
import contextlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_AUTO_FIX = _REPO_ROOT / "scripts" / "ci" / "auto_fix_common_issues.py"
_RECORDER = _REPO_ROOT / "scripts" / "ci" / "pattern_recorder.py"

_DB_PATH = os.environ.get(
    "CODEX_DB_PATH",
    os.path.join(os.path.expanduser("~"), ".codex", "cli_history.db"),
)
_GIT_SHA = (
    os.environ.get("CODEX_GIT_SHA")
    or os.environ.get("GITHUB_SHA")
)
_SESSION = (
    os.environ.get("GITHUB_RUN_ID")
    or os.environ.get("COPILOT_SESSION_ID")
)
_STRICT = os.environ.get("CODEX_PIPELINE_STRICT", "0") == "1"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_recorder():
    """Dynamically import pattern_recorder."""
    if not _RECORDER.exists():
        return None
    spec = importlib.util.spec_from_file_location("pattern_recorder", _RECORDER)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _run_auto_fix(
    *,
    check_only: bool,
    dry_run: bool,
    pattern: Optional[int],
    json_output: str,
) -> subprocess.CompletedProcess:
    """Invoke auto_fix_common_issues.py and return the completed process."""
    cmd = [sys.executable, str(_AUTO_FIX), "--json-output", json_output]
    if check_only:
        cmd.append("--check-only")
    if dry_run:
        cmd.append("--dry-run")
    if pattern is not None:
        cmd += ["--pattern", str(pattern)]
    return subprocess.run(cmd, capture_output=True, text=True, cwd=_REPO_ROOT)


def _print_report(report: Dict[str, Any], *, check_only: bool) -> None:
    """Print a human-readable pipeline summary."""
    total = report.get("total_issues", 0)
    auto_fix = report.get("auto_fixable", 0)
    manual = report.get("manual_review", 0)
    fixes = report.get("fixes_applied", {})

    print("\n" + "═" * 60)
    print("  CI PATTERN PIPELINE — SUMMARY")
    print("═" * 60)
    print(f"  Mode          : {'check-only' if check_only else 'fix'}")
    print(f"  Total issues  : {total}")
    print(f"  Auto-fixable  : {auto_fix}")
    print(f"  Manual review : {manual}")
    if fixes:
        print("  Fixes applied :")
        for name, count in fixes.items():
            print(f"    {'✅' if count > 0 else '⚠️ '} {name}: {count}")
    print("═" * 60)

    issues = report.get("issues", [])
    if issues:
        print("\n  Detected patterns:")
        for issue in issues[:30]:
            flag = "✅" if report.get("fixes_applied", {}).get(issue.get("pattern_name", ""), 0) > 0 else "⚠️ "
            print(
                f"    {flag} [{issue.get('pattern', '?'):>2}] "
                f"{issue.get('pattern_name', '?'):<22}  "
                f"{issue.get('file', ''):30}:{issue.get('line', 0)}"
            )
        if len(issues) > 30:
            print(f"    … and {len(issues) - 30} more (see artefact)")
    print()


def _write_artefact(
    path: str,
    report: Dict[str, Any],
    *,
    recorded: int,
    pipeline_status: str,
) -> None:
    """Write the structured pipeline artefact JSON."""
    artefact: Dict[str, Any] = {
        "pipeline_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pipeline_status": pipeline_status,
        "git_sha": _GIT_SHA,
        "session": _SESSION,
        "diagnostic_report": report,
        "patterns_recorded": recorded,
    }
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(artefact, indent=2), encoding="utf-8")
    print(f"  Pipeline artefact written to: {path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run the full CI pattern pipeline: detect → fix → record → report",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Detect patterns only; do not apply fixes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be fixed without modifying files",
    )
    parser.add_argument(
        "--pattern",
        type=int,
        metavar="N",
        help="Run only pattern N (1–18)",
    )
    parser.add_argument(
        "--artefact",
        type=str,
        metavar="PATH",
        help="Write structured JSON artefact to PATH",
    )
    parser.add_argument(
        "--no-record",
        action="store_true",
        help="Skip recording to the cognitive brain DB",
    )
    parser.add_argument(
        "--db",
        default=_DB_PATH,
        help="Cognitive brain DB path (overrides $CODEX_DB_PATH)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        default=_STRICT,
        help="Exit 1 if auto-fixable issues remain after fixes",
    )
    parser.add_argument(
        "--session",
        default=_SESSION,
        help="Session / PR identifier for audit trail",
    )
    parser.add_argument(
        "--sha",
        default=_GIT_SHA,
        help="Git SHA for audit trail",
    )
    args = parser.parse_args(argv)

    print(f"\n🔍 CI Pattern Pipeline — {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")

    if not _AUTO_FIX.exists():
        print(f"ERROR: auto_fix_common_issues.py not found at {_AUTO_FIX}", file=sys.stderr)
        return 2

    # ── Stage 1 + 2: Detect (and optionally Fix) ─────────────────────────────
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".json", delete=False
    ) as tmp:
        tmp_path = tmp.name

    try:
        print("  Stage 1/3: Running pattern detection…", end=" ", flush=True)
        proc = _run_auto_fix(
            check_only=args.check_only,
            dry_run=args.dry_run,
            pattern=args.pattern,
            json_output=tmp_path,
        )
        print("done" if proc.returncode in (0, 1) else f"exit {proc.returncode}")

        # Print any unexpected stderr from auto_fix
        if proc.stderr.strip():
            for line in proc.stderr.strip().splitlines():
                print(f"    {line}")

        try:
            report: Dict[str, Any] = json.loads(Path(tmp_path).read_text())
        except (json.JSONDecodeError, OSError):
            report = {"total_issues": 0, "auto_fixable": 0, "issues": [], "fixes_applied": {}}

        # ── Stage 3: Record ──────────────────────────────────────────────────
        recorded = 0
        if not args.no_record:
            print("  Stage 2/3: Recording patterns to cognitive brain DB…", end=" ", flush=True)
            recorder = _load_recorder()
            if recorder is not None:
                try:
                    conn = recorder._open_db(args.db)
                    recorded = recorder.record_from_report(
                        Path(tmp_path), conn, args.session, args.sha
                    )
                    conn.close()
                    print(f"{recorded} occurrence(s) recorded")
                except Exception as exc:
                    print(f"WARNING: {exc}")
            else:
                print("skipped (pattern_recorder.py not found)")
        else:
            print("  Stage 2/3: Recording skipped (--no-record)")

        # ── Stage 4: Report ──────────────────────────────────────────────────
        print("  Stage 3/3: Generating report…")
        _print_report(report, check_only=args.check_only)

        # Determine pipeline status
        remaining_fixable = report.get("auto_fixable", 0) - sum(
            report.get("fixes_applied", {}).values()
        )
        if args.check_only:
            pipeline_status = "issues_detected" if report.get("auto_fixable", 0) > 0 else "clean"
        else:
            pipeline_status = "fixed" if remaining_fixable <= 0 else "partial"

        # Write artefact if requested
        if args.artefact:
            _write_artefact(
                args.artefact,
                report,
                recorded=recorded,
                pipeline_status=pipeline_status,
            )

        # Exit code logic
        if args.strict:
            if args.check_only and report.get("auto_fixable", 0) > 0:
                print(
                    f"❌ {report['auto_fixable']} auto-fixable issue(s) detected "
                    "(strict mode — exiting 1)",
                    file=sys.stderr,
                )
                return 1
            if not args.check_only and remaining_fixable > 0:
                print(
                    f"❌ {remaining_fixable} auto-fixable issue(s) remain after fixes "
                    "(strict mode — exiting 1)",
                    file=sys.stderr,
                )
                return 1

        print("✅ Pipeline complete")
        return 0

    finally:
        with contextlib.suppress(OSError):
            os.unlink(tmp_path)


if __name__ == "__main__":
    sys.exit(main())
