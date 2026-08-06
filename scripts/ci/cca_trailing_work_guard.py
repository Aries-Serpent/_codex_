#!/usr/bin/env python3
"""
cca_trailing_work_guard.py — Copilot Cloud Agent trailing-work telemetry guard
═══════════════════════════════════════════════════════════════════════════════

Read-only / advisory (Tier 0/1) caller-side guard for CCA runs.

Emits one JSONL checkpoint record per invocation to:
    .codex/telemetry/cca_trailing_work.jsonl

Recommended thresholds (derived from run 30980481579 post-mortem):
    step_count > 120  → warn
    step_count > 180  → escalate
    api_quota_remaining < 500 → abort
    no step completion for > 10 min → stalled
    duplicate fc_call_ within window → abort

Usage in copilot-setup-steps.yml (static caller-side hook):
    - name: CCA trailing-work guard
      continue-on-error: true
      env:
        CCA_STEP_COUNT: ${{ steps.some_step.outputs.step_count }}
        ACCESS_REST_REMAINING: ${{ env.ACCESS_REST_REMAINING }}
        CCA_FC_CALL_ID: ${{ steps.some_step.outputs.fc_call_id }}
      run: python3 scripts/ci/cca_trailing_work_guard.py --emit

Standalone checks:
    python3 scripts/ci/cca_trailing_work_guard.py --emit --step-count 130
    python3 scripts/ci/cca_trailing_work_guard.py --check --run-id 30980481579
    python3 scripts/ci/cca_trailing_work_guard.py --report

Exit codes:
    0  OK or dry-run
    1  Warning / escalation detected
    2  Abort condition detected (low quota, duplicate fc_call_, severe stall)
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
TELEMETRY_DIR = REPO_ROOT / ".codex" / "telemetry"
TELEMETRY_LOG = TELEMETRY_DIR / "cca_trailing_work.jsonl"

# Thresholds
WARN_STEP_THRESHOLD = int(os.environ.get("CCA_WARN_STEP_THRESHOLD", "120"))
ESCALATE_STEP_THRESHOLD = int(os.environ.get("CCA_ESCALATE_STEP_THRESHOLD", "180"))
ABORT_QUOTA_THRESHOLD = int(os.environ.get("CCA_ABORT_QUOTA_THRESHOLD", "500"))
STALL_MINUTES = int(os.environ.get("CCA_STALL_MINUTES", "10"))
DUPLICATE_WINDOW_SECONDS = int(os.environ.get("CCA_DUPLICATE_WINDOW_SECONDS", "300"))


def _now() -> str:
    return datetime.now(tz=timezone.utc).isoformat()


def _resolve_int(name: str, default: int) -> int:
    val = os.environ.get(name, "")
    if val:
        try:
            return int(val)
        except ValueError:
            pass
    return default


def _resolve_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip() or default


def _rate_limit_remaining() -> int:
    """Probe GitHub /rate_limit for core remaining; return -1 on failure."""
    token = (
        os.environ.get("CODEX_MASTER_KEY")
        or os.environ.get("CODEX_BACKUP_KEY")
        or os.environ.get("GITHUB_TOKEN")
        or ""
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "codex-cca-trailing-work-guard/1.0",
    }
    if token:
        headers["Authorization"] = f"******"
    req = urllib.request.Request("https://api.github.com/rate_limit", headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        core = data.get("resources", {}).get("core", {})
        return int(core.get("remaining", -1))
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError):
        return -1


def _read_log() -> list[dict[str, Any]]:
    if not TELEMETRY_LOG.exists():
        return []
    records: list[dict[str, Any]] = []
    for line in TELEMETRY_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            records.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return records


def _is_duplicate_fc_call(run_id: str, job_id: str, fc_call_id: str) -> bool:
    if not fc_call_id:
        return False
    cutoff = time.time() - DUPLICATE_WINDOW_SECONDS
    for rec in reversed(_read_log()):
        if (
            rec.get("run_id") == run_id
            and rec.get("job_id") == job_id
            and rec.get("fc_call_id") == fc_call_id
        ):
            ts = rec.get("ts", "")
            try:
                dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
                if dt.timestamp() >= cutoff:
                    return True
            except ValueError:
                return True
    return False


def _last_checkpoint_time(run_id: str, job_id: str) -> datetime | None:
    for rec in reversed(_read_log()):
        if rec.get("run_id") == run_id and rec.get("job_id") == job_id:
            ts = rec.get("ts", "")
            try:
                return datetime.fromisoformat(ts.replace("Z", "+00:00"))
            except ValueError:
                continue
    return None


def _compute_status(
    step_count: int,
    api_quota_remaining: int,
    run_id: str,
    job_id: str,
    fc_call_id: str,
) -> tuple[str, list[str], int]:
    reasons: list[str] = []
    status = "ok"
    exit_code = 0

    # Step-count thresholds
    if step_count > ESCALATE_STEP_THRESHOLD:
        status = "escalate_steps"
        reasons.append(
            f"step_count {step_count} > escalate threshold {ESCALATE_STEP_THRESHOLD}"
        )
        exit_code = max(exit_code, 1)
    elif step_count > WARN_STEP_THRESHOLD:
        status = "warn_steps"
        reasons.append(
            f"step_count {step_count} > warning threshold {WARN_STEP_THRESHOLD}"
        )
        exit_code = max(exit_code, 1)

    # API quota
    if api_quota_remaining >= 0 and api_quota_remaining < ABORT_QUOTA_THRESHOLD:
        status = "abort_quota"
        reasons.append(
            f"api_quota_remaining {api_quota_remaining} < abort threshold {ABORT_QUOTA_THRESHOLD}"
        )
        exit_code = 2

    # Stalled detection
    last_ts = _last_checkpoint_time(run_id, job_id)
    if last_ts is not None:
        elapsed_min = (datetime.now(tz=timezone.utc) - last_ts).total_seconds() / 60
        if elapsed_min > STALL_MINUTES:
            status = "stalled" if status == "ok" else status
            reasons.append(
                f"no checkpoint for {elapsed_min:.1f} min (stall threshold {STALL_MINUTES} min)"
            )
            exit_code = max(exit_code, 1)

    # Duplicate fc_call_ detection
    if _is_duplicate_fc_call(run_id, job_id, fc_call_id):
        status = "abort_duplicate"
        reasons.append(f"duplicate fc_call_id {fc_call_id!r} within {DUPLICATE_WINDOW_SECONDS}s window")
        exit_code = 2

    return status, reasons, exit_code


def emit_checkpoint(args: argparse.Namespace) -> int:
    TELEMETRY_DIR.mkdir(parents=True, exist_ok=True)

    run_id = args.run_id or _resolve_str("GITHUB_RUN_ID", "local")
    job_id = args.job_id or _resolve_str("GITHUB_JOB", "local")
    lane = args.lane or _resolve_str("CCA_LANE", "")
    fix_id = args.fix_id or _resolve_str("CCA_FIX_ID", "")
    step_count = args.step_count if args.step_count is not None else _resolve_int("CCA_STEP_COUNT", 0)
    fc_call_id = args.fc_call_id or _resolve_str("CCA_FC_CALL_ID", "")

    api_quota = args.quota
    if api_quota is None:
        api_quota = _resolve_int("ACCESS_REST_REMAINING", -1)
    if api_quota < 0:
        api_quota = _rate_limit_remaining()

    status, reasons, exit_code = _compute_status(
        step_count, api_quota, run_id, job_id, fc_call_id
    )

    next_checkpoint = _now()

    record = {
        "ts": _now(),
        "run_id": run_id,
        "job_id": job_id,
        "lane": lane,
        "fix_id": fix_id,
        "status": status,
        "step_count": step_count,
        "api_quota_remaining": api_quota,
        "next_checkpoint": next_checkpoint,
        "reasons": reasons,
        "fc_call_id": fc_call_id,
    }

    if args.dry_run:
        print(json.dumps(record, indent=2))
        return 0

    with TELEMETRY_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record) + "\n")

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        icon = "✅" if status == "ok" else ("⚠️" if exit_code == 1 else "🛑")
        with open(summary_path, "a", encoding="utf-8") as fh:
            fh.write(
                f"\n### {icon} CCA Trailing-Work Guard\n"
                f"- Status: `{status}`\n"
                f"- step_count: `{step_count}`\n"
                f"- api_quota_remaining: `{api_quota}`\n"
            )
            if reasons:
                fh.write(f"- Reasons: {', '.join(reasons)}\n")

    print(f"cca_trailing_work: status={status} step_count={step_count} quota={api_quota}")
    if reasons:
        for r in reasons:
            print(f"  - {r}")

    return exit_code


def check_run(args: argparse.Namespace) -> int:
    run_id = args.run_id or _resolve_str("GITHUB_RUN_ID")
    if not run_id:
        print("ERROR: --run-id or GITHUB_RUN_ID required", file=sys.stderr)
        return 1

    records = [r for r in _read_log() if r.get("run_id") == run_id]
    if not records:
        print(f"No telemetry records found for run_id={run_id}")
        return 0

    latest = records[-1]
    print(json.dumps(latest, indent=2))
    return 0 if latest.get("status") == "ok" else (2 if latest.get("status", "").startswith("abort") else 1)


def generate_report(_args: argparse.Namespace) -> int:
    records = _read_log()
    if not records:
        print("No CCA trailing-work telemetry records yet.")
        return 0

    total = len(records)
    statuses: dict[str, int] = {}
    for r in records:
        statuses[r.get("status", "unknown")] = statuses.get(r.get("status", "unknown"), 0) + 1

    latest = records[-1]
    print("# CCA Trailing-Work Telemetry Report\n")
    print(f"- Total checkpoints: {total}")
    print(f"- Latest checkpoint: {latest.get('ts')}")
    print(f"- Latest run_id: {latest.get('run_id')}")
    print("- Status distribution:")
    for status, count in sorted(statuses.items(), key=lambda x: -x[1]):
        print(f"  - {status}: {count}")
    return 0


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    emit = sub.add_parser("emit", help="Emit a checkpoint record")
    emit.add_argument("--run-id", default="")
    emit.add_argument("--job-id", default="")
    emit.add_argument("--lane", default="")
    emit.add_argument("--fix-id", default="")
    emit.add_argument("--step-count", type=int, default=None)
    emit.add_argument("--quota", type=int, default=None)
    emit.add_argument("--fc-call-id", default="")
    emit.add_argument("--dry-run", action="store_true")

    check = sub.add_parser("check", help="Check latest record for a run")
    check.add_argument("--run-id", default="")

    report = sub.add_parser("report", help="Print telemetry summary report")

    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.command == "emit":
        return emit_checkpoint(args)
    if args.command == "check":
        return check_run(args)
    if args.command == "report":
        return generate_report(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
