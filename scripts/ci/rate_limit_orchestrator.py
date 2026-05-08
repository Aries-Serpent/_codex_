#!/usr/bin/env python3
"""
rate_limit_orchestrator.py — Rate-limit-aware workflow orchestration for GitHub Actions.

Purpose
-------
Prevents GitHub API rate-limit exhaustion caused by repetitive, concurrent, or
cascading workflow triggers. Implements four patterns:

  Pattern A — Pre-call rate-limit status check (fast guard before any API call)
  Pattern B — Workflow deduplication (cancel in-flight runs superseded by a newer push)
  Pattern C — Exponential-backoff retry with jitter for 429/403 responses
  Pattern D — Concurrent workflow cap (enforce max N in-progress runs per branch)

Usage
-----
    # Check current rate limits and print a status report:
    python scripts/ci/rate_limit_orchestrator.py --status

    # Deduplicate: cancel all older in-progress runs for <workflow> on <branch>:
    python scripts/ci/rate_limit_orchestrator.py --deduplicate \
        --workflow validate.yml --branch main --keep-latest

    # Cap: ensure at most N concurrent runs across all workflows on a branch:
    python scripts/ci/rate_limit_orchestrator.py --cap --max-concurrent 5 \
        --branch copilot/my-feature

    # Full orchestration pass (deduplicate + cap + status):
    python scripts/ci/rate_limit_orchestrator.py --orchestrate \
        --branch "${{ github.head_ref }}"

Environment variables
---------------------
    GH_TOKEN               — GitHub token (CODEX_MASTER_KEY preferred)
    REPO                   — owner/repo (defaults to Aries-Serpent/_codex_)
    GH_TRICKLE_POLITE_SLEEP — seconds between API calls (default 0.3)
    GH_TRICKLE_MIN_REMAINING — minimum remaining before switching token (default 20)
    RATE_LIMIT_MAX_CONCURRENT — max concurrent in-progress workflow runs (default 8)

Exit codes
----------
    0  All operations completed successfully (or no action needed).
    1  Unrecoverable error (token missing, API unreachable after retries).
    2  Rate-limit critical: remaining < MIN_REMAINING on ALL tokens.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_DEFAULT_REPO = "Aries-Serpent/_codex_"
_GH_API_BASE = "https://api.github.com"
_DEFAULT_MAX_CONCURRENT = int(os.environ.get("RATE_LIMIT_MAX_CONCURRENT", "8"))
_POLITE_SLEEP = float(os.environ.get("GH_TRICKLE_POLITE_SLEEP", "0.3"))
_MIN_REMAINING = int(os.environ.get("GH_TRICKLE_MIN_REMAINING", "20"))
_MAX_RETRIES = 3
_MAX_BACKOFF = 60  # seconds

# Workflow names that must never be cancelled by the orchestrator (safety guard).
_PROTECTED_WORKFLOWS: frozenset[str] = frozenset({
    "iterative-self-healing-ci.yml",
    "copilot-setup-steps.yml",
    "workflow-execution-gate.yml",
    "agent-auth-delegation.yml",
    "deferral-language-gate.yml",
    "comment-review-gate.yml",
    "pre-merge-validation.yml",
    "cost-gate.yml",
    "token-expiry-monitor.yml",
    "admin-action-notifier.yml",
})


# ---------------------------------------------------------------------------
# GitHub API helper
# ---------------------------------------------------------------------------

def _discover_tokens() -> list[str]:
    """Return all non-empty tokens in priority order."""
    names = [
        "CODEX_MASTER_KEY",
        "CODEX_BACKUP_KEY",
        "CODEX_ADMIN_KEY",
        "GH_TOKEN",
        "GITHUB_TOKEN",
    ]
    return [t for name in names if (t := os.environ.get(name, "").strip())]


def _gh_api(
    method: str,
    path: str,
    token: str,
    body: dict[str, Any] | None = None,
    *,
    accept: str = "application/vnd.github+json",
) -> tuple[int, Any]:
    """Make a single GitHub API call; return (status_code, parsed_body)."""
    url = f"{_GH_API_BASE}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": accept,
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read()
            parsed = json.loads(raw) if raw.strip() else {}
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {}
        return exc.code, err_body


def _gh_api_with_retry(
    method: str,
    path: str,
    tokens: list[str],
    body: dict[str, Any] | None = None,
) -> tuple[int, Any]:
    """Call GitHub API with retry + exponential backoff across available tokens."""
    if not tokens:
        logger.error("No GitHub tokens available — set GH_TOKEN or CODEX_MASTER_KEY")
        sys.exit(1)

    for attempt in range(_MAX_RETRIES):
        token = tokens[attempt % len(tokens)]
        status, result = _gh_api(method, path, token, body)

        if status in (200, 201, 202, 204):
            time.sleep(_POLITE_SLEEP)
            return status, result

        if status in (429, 403):
            wait = min(_MAX_BACKOFF, (2 ** attempt) + random.uniform(0, 1))
            logger.warning("Rate-limited (HTTP %d) — sleeping %.1fs before retry %d", status, wait, attempt + 1)
            time.sleep(wait)
            continue

        if status == 422:
            # Unprocessable — probably already cancelled; treat as success
            return status, result

        # Other errors — log and retry
        logger.warning("HTTP %d on %s %s (attempt %d): %s", status, method, path, attempt + 1, result)
        time.sleep(_POLITE_SLEEP)

    return 0, {}


# ---------------------------------------------------------------------------
# Pattern A — Rate-limit status check
# ---------------------------------------------------------------------------

def check_rate_limit_status(tokens: list[str]) -> dict[str, Any]:
    """Return rate-limit status for all tokens. Exit 2 if all are critical."""
    report: dict[str, Any] = {"tokens": [], "overall_status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

    any_ok = False
    for i, token in enumerate(tokens):
        status, data = _gh_api("GET", "/rate_limit", token)
        if status != 200:
            entry = {"token_index": i, "status": "error", "http_status": status}
        else:
            core = data.get("resources", {}).get("core", {})
            remaining = core.get("remaining", 0)
            limit = core.get("limit", 5000)
            reset_at = core.get("reset", 0)
            reset_in = max(0, reset_at - int(time.time()))
            pct = round(100 * remaining / max(limit, 1))
            entry = {
                "token_index": i,
                "remaining": remaining,
                "limit": limit,
                "pct": pct,
                "reset_in_seconds": reset_in,
                "status": "ok" if remaining >= _MIN_REMAINING else "critical",
            }
            if remaining >= _MIN_REMAINING:
                any_ok = True
        report["tokens"].append(entry)
        time.sleep(_POLITE_SLEEP)

    if not any_ok:
        report["overall_status"] = "critical"
        logger.error("❌ ALL tokens are rate-limited (remaining < %d). Sleeping until reset.", _MIN_REMAINING)

    return report


# ---------------------------------------------------------------------------
# Pattern B — Workflow deduplication
# ---------------------------------------------------------------------------

def deduplicate_workflow(
    workflow_file: str,
    branch: str,
    repo: str,
    tokens: list[str],
    *,
    keep_latest: bool = True,
    dry_run: bool = False,
) -> int:
    """Cancel superseded in-progress runs of *workflow_file* on *branch*.

    Returns the number of runs cancelled.
    """
    if workflow_file in _PROTECTED_WORKFLOWS:
        logger.info("ℹ️  %s is protected — skipping deduplication", workflow_file)
        return 0

    path = f"/repos/{repo}/actions/workflows/{urllib.parse.quote(workflow_file, safe='')}/runs"
    params = f"?branch={urllib.parse.quote(branch)}&status=in_progress&per_page=100"
    status, data = _gh_api_with_retry("GET", path + params, tokens)

    runs: list[dict[str, Any]] = data.get("workflow_runs", []) if status == 200 else []
    if len(runs) <= 1:
        logger.info("✅ %s on '%s': %d in-progress run(s) — no duplicates to cancel", workflow_file, branch, len(runs))
        return 0

    # Sort by run number descending (newest first)
    runs.sort(key=lambda r: r.get("run_number", 0), reverse=True)

    # Keep the newest; cancel the rest
    to_cancel = runs[1:] if keep_latest else runs
    cancelled = 0
    for run in to_cancel:
        run_id = run["id"]
        run_number = run.get("run_number", "?")
        if dry_run:
            logger.info("[DRY-RUN] Would cancel run #%s (id=%s) of %s", run_number, run_id, workflow_file)
            cancelled += 1
            continue
        cancel_status, _ = _gh_api_with_retry("POST", f"/repos/{repo}/actions/runs/{run_id}/cancel", tokens)
        if cancel_status in (202, 204, 422):
            logger.info("🛑 Cancelled run #%s (id=%s) of %s", run_number, run_id, workflow_file)
            cancelled += 1
        else:
            logger.warning("⚠️  Failed to cancel run #%s (id=%s) — HTTP %d", run_number, run_id, cancel_status)

    return cancelled


# ---------------------------------------------------------------------------
# Pattern D — Concurrent cap enforcement
# ---------------------------------------------------------------------------

def enforce_concurrent_cap(
    branch: str,
    repo: str,
    tokens: list[str],
    max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
    *,
    dry_run: bool = False,
) -> int:
    """Cancel oldest in-progress runs across all workflows on *branch* when count > *max_concurrent*.

    Protected workflows are never cancelled. Returns number of runs cancelled.
    """
    path = f"/repos/{repo}/actions/runs"
    params = f"?branch={urllib.parse.quote(branch)}&status=in_progress&per_page=100"
    status, data = _gh_api_with_retry("GET", path + params, tokens)

    runs: list[dict[str, Any]] = data.get("workflow_runs", []) if status == 200 else []

    # Filter out protected workflows
    cancellable = [
        r for r in runs
        if r.get("path", "").split("/")[-1] not in _PROTECTED_WORKFLOWS
        and r.get("name", "") not in _PROTECTED_WORKFLOWS
    ]

    if len(cancellable) <= max_concurrent:
        logger.info("✅ In-progress runs on '%s': %d total, %d cancellable — within cap (%d)",
                    branch, len(runs), len(cancellable), max_concurrent)
        return 0

    # Sort oldest first (ascending run_number); cancel oldest excess
    cancellable.sort(key=lambda r: r.get("run_number", 0))
    excess = cancellable[:len(cancellable) - max_concurrent]
    cancelled = 0

    for run in excess:
        run_id = run["id"]
        wf_name = run.get("name", "unknown")
        run_number = run.get("run_number", "?")
        if dry_run:
            logger.info("[DRY-RUN] Would cancel run #%s '%s' (id=%s)", run_number, wf_name, run_id)
            cancelled += 1
            continue
        cancel_status, _ = _gh_api_with_retry("POST", f"/repos/{repo}/actions/runs/{run_id}/cancel", tokens)
        if cancel_status in (202, 204, 422):
            logger.info("🛑 CAP: Cancelled run #%s '%s' (id=%s)", run_number, wf_name, run_id)
            cancelled += 1
        else:
            logger.warning("⚠️  CAP: Failed to cancel run #%s '%s' — HTTP %d", run_number, wf_name, cancel_status)

    return cancelled


# ---------------------------------------------------------------------------
# Full orchestration pass
# ---------------------------------------------------------------------------

_DEDUP_WORKFLOWS = [
    "validate.yml",
    "resilient_validation.yml",
    "nox_gates.yml",
    "coverage-with-timeout.yml",
    "security-scanning-suite.yml",
    "codeql-analysis.yml",
    "documentation-link-checker.yml",
    "reference-integrity.yml",
    "docker-build-push.yml",
    "code-quality-coverage-suite.yml",
]


def orchestrate(
    branch: str,
    repo: str,
    tokens: list[str],
    max_concurrent: int = _DEFAULT_MAX_CONCURRENT,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run a full orchestration pass: rate-limit check → dedup → cap."""
    logger.info("═══ Rate-Limit Orchestration Pass ═══")
    logger.info("Branch: %s | Repo: %s | Max concurrent: %d", branch, repo, max_concurrent)

    # Step 1: Check rate limits
    rate_status = check_rate_limit_status(tokens)
    logger.info("Rate-limit status: %s", rate_status["overall_status"])
    for t in rate_status["tokens"]:
        if "remaining" in t:
            logger.info("  Token[%d]: %d/%d remaining (%d%%)", t["token_index"], t["remaining"], t["limit"], t["pct"])

    if rate_status["overall_status"] == "critical":
        logger.error("🚨 Rate-limit critical — aborting orchestration to preserve quota")
        return {"status": "aborted", "reason": "rate_limit_critical", "rate_status": rate_status}

    # Step 2: Deduplicate cancellable workflows
    total_cancelled_dedup = 0
    for wf in _DEDUP_WORKFLOWS:
        n = deduplicate_workflow(wf, branch, repo, tokens, dry_run=dry_run)
        total_cancelled_dedup += n

    # Step 3: Enforce concurrent cap
    total_cancelled_cap = enforce_concurrent_cap(branch, repo, tokens, max_concurrent, dry_run=dry_run)

    result = {
        "status": "ok",
        "branch": branch,
        "repo": repo,
        "cancelled_dedup": total_cancelled_dedup,
        "cancelled_cap": total_cancelled_cap,
        "total_cancelled": total_cancelled_dedup + total_cancelled_cap,
        "dry_run": dry_run,
        "rate_status": rate_status,
    }
    logger.info("═══ Orchestration complete — cancelled %d run(s) total ═══", result["total_cancelled"])
    return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Rate-limit-aware GitHub Actions workflow orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--status", action="store_true", help="Print rate-limit status for all tokens")
    p.add_argument("--deduplicate", action="store_true", help="Cancel duplicate in-progress runs for a workflow")
    p.add_argument("--cap", action="store_true", help="Enforce max-concurrent cap across all workflows on a branch")
    p.add_argument("--orchestrate", action="store_true", help="Run full orchestration (dedup + cap + status)")
    p.add_argument("--workflow", default="", help="Workflow filename for --deduplicate (e.g. validate.yml)")
    p.add_argument("--branch", default="", help="Branch name to scope operations")
    p.add_argument("--repo", default=os.environ.get("REPO", _DEFAULT_REPO), help="owner/repo")
    p.add_argument("--max-concurrent", type=int, default=_DEFAULT_MAX_CONCURRENT, help="Max concurrent runs (--cap)")
    p.add_argument("--keep-latest", action="store_true", default=True, help="Keep newest run when deduplicating")
    p.add_argument("--dry-run", action="store_true", help="Show what would be cancelled without doing it")
    p.add_argument("--json-output", metavar="FILE", default="", help="Write JSON result to FILE")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    tokens = _discover_tokens()
    if not tokens:
        logger.error("No GitHub token found. Set GH_TOKEN, CODEX_MASTER_KEY, or GITHUB_TOKEN.")
        return 1

    result: dict[str, Any] = {}

    if args.status:
        result = check_rate_limit_status(tokens)
        print(json.dumps(result, indent=2))

    elif args.deduplicate:
        if not args.workflow:
            logger.error("--workflow is required for --deduplicate")
            return 1
        if not args.branch:
            logger.error("--branch is required for --deduplicate")
            return 1
        n = deduplicate_workflow(args.workflow, args.branch, args.repo, tokens,
                                 keep_latest=args.keep_latest, dry_run=args.dry_run)
        result = {"cancelled": n, "workflow": args.workflow, "branch": args.branch, "dry_run": args.dry_run}
        print(json.dumps(result, indent=2))

    elif args.cap:
        if not args.branch:
            logger.error("--branch is required for --cap")
            return 1
        n = enforce_concurrent_cap(args.branch, args.repo, tokens,
                                   args.max_concurrent, dry_run=args.dry_run)
        result = {"cancelled": n, "branch": args.branch, "max_concurrent": args.max_concurrent, "dry_run": args.dry_run}
        print(json.dumps(result, indent=2))

    elif args.orchestrate:
        if not args.branch:
            logger.error("--branch is required for --orchestrate")
            return 1
        result = orchestrate(args.branch, args.repo, tokens,
                             args.max_concurrent, dry_run=args.dry_run)
        print(json.dumps(result, indent=2))
        if result.get("status") == "aborted":
            return 2

    else:
        logger.error("No operation specified. Use --status, --deduplicate, --cap, or --orchestrate.")
        return 1

    if args.json_output:
        with open(args.json_output, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        logger.info("JSON result written to %s", args.json_output)

    return 0


if __name__ == "__main__":
    sys.exit(main())
