#!/usr/bin/env python3
"""Proactive CI Monitor — scan ALL open PRs for failed CI and post Copilot rescue comments.

This script is the engine behind ``proactive-ci-monitor.yml``.  It is the
**authoritative** safety net: any CI failure that was NOT caught by the
per-push self-healing cascade will be surfaced here on the next scheduled run.

Algorithm
---------
1. List all open PRs in the repository.
2. For each PR, fetch the most-recent workflow runs for its HEAD commit.
3. Classify each failure with the ``ci.health.analyzer`` pattern catalogue.
4. If a failure has no existing Copilot rescue comment for this (run_id, sha):
   a. Post a structured RCA comment with @copilot tag.
   b. Apply the SHA-scoped upsert marker so subsequent failures on the same
      commit are appended rather than creating new comments.
5. Skip transient-infra failures that self-resolve on re-run.
6. Emit a JSON report to stdout (captured as artifact by the workflow).

Usage::

    python scripts/ci/proactive_ci_monitor.py \\
        --repo Aries-Serpent/_codex_ \\
        --token "$GITHUB_TOKEN" \\
        [--dry-run]

Environment variables
---------------------
GITHUB_TOKEN        GitHub PAT with ``repo`` + ``workflow`` scopes.
PROACTIVE_DRY_RUN   Set to ``1`` to skip comment posting (print only).
PROACTIVE_MAX_AGE_H Max age in hours of failed runs to consider (default 24).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger("proactive_ci_monitor")
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

# ---------------------------------------------------------------------------
# ci.health.analyzer skill — primary classification engine
# ---------------------------------------------------------------------------

try:
    from codex.skills.ci_health_analyzer.handler import run as _ci_health_run

    _CI_HEALTH_AVAILABLE = True
except ImportError:
    _CI_HEALTH_AVAILABLE = False
    logger.debug("ci.health.analyzer skill unavailable; falling back to built-in patterns")

# ---------------------------------------------------------------------------
# Failure categories we actively escalate vs. silently skip
# ---------------------------------------------------------------------------

_SKIP_CATEGORIES = {"transient-infra"}  # auto-retry; no need for @copilot comment

# Known patterns — lightweight copy of ci_health_analyzer rules for script use
_PATTERNS: list[dict] = [
    {
        "id": "RP-COMMENT-GATE",
        "category": "pre-flight-gate",
        "confidence": 0.95,
        "regex": re.compile(
            r"blocking comment.*unaddressed|comment.review.gate.*failed", re.I
        ),
        "fix": "Reply to every BLOCKING comment, then push a new commit.",
    },
    {
        "id": "RP-CHANGELOG-GATE",
        "category": "pre-flight-gate",
        "confidence": 0.95,
        "regex": re.compile(r"CHANGELOG.*not updated|Verify CHANGELOG", re.I),
        "fix": "Add ### Fixed (SN) entry to CHANGELOG.md + update accountability report.",
    },
    {
        "id": "RP-P23",
        "category": "supply-chain",
        "confidence": 0.90,
        "regex": re.compile(r"No such \w+Detector", re.I),
        "fix": "python scripts/ci/auto_fix_common_issues.py --pattern 23",
    },
    {
        "id": "RP-P22",
        "category": "pre-flight-gate",
        "confidence": 0.90,
        "regex": re.compile(r"files were modified by hook.*sync-tracked", re.I),
        "fix": "python scripts/ci/sync_tracked_files.py --fix && git add -A && git commit",
    },
    {
        "id": "RP-RUFF",
        "category": "code-fix-required",
        "confidence": 0.90,
        "regex": re.compile(r"\.py:\d+:\d+: [EFW]\d{3,4}", re.I),
        "fix": "python -m ruff check --fix src/ tests/",
    },
    {
        "id": "RP-009",
        "category": "code-fix-required",
        "confidence": 0.85,
        "regex": re.compile(r"\d+ error.*?>\s*\d+", re.I),
        "fix": "Fix type errors: python scripts/ci/mypy_baseline.py",
    },
    {
        "id": "RP-019",
        "category": "code-fix-required",
        "confidence": 0.85,
        "regex": re.compile(r"ModuleNotFoundError", re.I),
        "fix": "Check for src. absolute import regression (P19).",
    },
    {
        "id": "RP-TRANSIENT-API503",
        "category": "transient-infra",
        "confidence": 0.95,
        "regex": re.compile(
            r"An error occurred while processing your request|HTTP 503|runner.*shutdown",
            re.I,
        ),
        "fix": "Re-run workflow — transient GitHub infrastructure failure.",
    },
    {
        "id": "RP-ACTIONLINT",
        "category": "workflow-config",
        "confidence": 0.90,
        "regex": re.compile(r"actionlint.*\.github/workflows/", re.I),
        "fix": "Fix YAML/shell issue in the reported workflow file.",
    },
    {
        "id": "RP-UNKNOWN",
        "category": "unknown",
        "confidence": 0.0,
        "regex": re.compile(r""),  # catch-all
        "fix": "Inspect full logs; check GitHub Actions run URL for step-level error.",
    },
]


def _classify(log_text: str, history: list[dict] | None = None) -> dict:
    """Return a classification dict for *log_text*.

    When the ``ci.health.analyzer`` skill is importable it is used as the
    primary engine (which also computes a ``trend`` from *history* when
    provided).  Falls back to the local ``_PATTERNS`` list when the skill
    is not available (e.g. running in a minimal environment).

    Parameters
    ----------
    log_text:
        Raw CI log text to classify.
    history:
        Optional list of previous :func:`_classify` results for the same PR,
        most-recent-last.  Passed to ``ci.health.analyzer`` so it can compute
        recurrence and flap trends.
    """
    if _CI_HEALTH_AVAILABLE:
        payload: dict[str, Any] = {"run_logs": log_text}
        if history:
            # Translate our result dicts to the shape ci_health_analyzer expects
            payload["history"] = [
                {
                    "pattern_id": h.get("pattern_id", ""),
                    "category": h.get("category", "unknown"),
                    "confidence": h.get("confidence", 0.0),
                }
                for h in history
            ]
        try:
            skill_result = _ci_health_run(payload)
            return {
                "id": skill_result.get("pattern_id", "RP-UNKNOWN"),
                "category": skill_result.get("category", "unknown"),
                "confidence": skill_result.get("confidence", 0.0),
                "fix": " ".join(skill_result.get("fix_commands", [])),
                "trend": skill_result.get("trend"),
            }
        except Exception as exc:  # noqa: BLE001
            logger.warning("ci.health.analyzer raised %s; falling back to built-in", exc, exc_info=True)

    # ── Built-in fallback ────────────────────────────────────────────────────
    for pat in _PATTERNS:
        if pat["id"] == "RP-UNKNOWN":
            continue
        if pat["regex"].search(log_text):
            return pat
    return _PATTERNS[-1]  # RP-UNKNOWN


# ---------------------------------------------------------------------------
# GitHub API helpers
# ---------------------------------------------------------------------------


def _gh(
    path: str,
    token: str,
    method: str = "GET",
    body: dict | None = None,
) -> Any:
    """Make a GitHub API call; return parsed JSON or raise on error."""
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        body_text = exc.read().decode(errors="replace")
        logger.warning("GitHub API %s %s → %s: %s", method, path, exc.code, body_text[:300])
        raise


def _list_open_prs(repo: str, token: str) -> list[dict]:
    """Return all open PRs (paginated)."""
    prs: list[dict] = []
    page = 1
    while True:
        batch = _gh(f"/repos/{repo}/pulls?state=open&per_page=50&page={page}", token)
        if not batch:
            break
        prs.extend(batch)
        if len(batch) < 50:
            break
        page += 1
    return prs


def _latest_runs_for_sha(repo: str, sha: str, token: str) -> list[dict]:
    """Return workflow runs for a specific commit SHA."""
    data = _gh(f"/repos/{repo}/actions/runs?head_sha={sha}&per_page=50", token)
    return data.get("workflow_runs", [])


def _get_run_logs_text(repo: str, run_id: int, token: str) -> str:
    """Download and return the first 20 000 chars of run logs (best-effort)."""
    try:
        # Get jobs first — look for failed steps
        jobs = _gh(f"/repos/{repo}/actions/runs/{run_id}/jobs?filter=latest", token)
        snippets: list[str] = []
        for job in jobs.get("jobs", []):
            if job.get("conclusion") not in {"failure", "cancelled"}:
                continue
            for step in job.get("steps", []):
                if step.get("conclusion") == "failure":
                    snippets.append(
                        f"{job['name']} › {step['name']}"
                    )
        return "\n".join(snippets)
    except Exception:
        return ""


def _existing_rescue_comment(
    repo: str,
    pr_number: int,
    sha12: str,
    run_id: int,
    token: str,
) -> bool:
    """Return True if a rescue/healing comment for this (sha12, run_id) exists."""
    comments = _gh(
        f"/repos/{repo}/issues/{pr_number}/comments?per_page=100",
        token,
    )
    marker_sha = f"<!-- copilot-healing:{sha12}:"
    marker_run = f"ci-rescue:3856:run-{run_id}"
    marker_run_generic = f"ci-rescue-rca:3856:sha-{sha12}"
    for c in comments:
        body = c.get("body", "")
        if marker_sha in body or marker_run in body or marker_run_generic in body:
            return True
    return False


def _post_rescue_comment(
    repo: str,
    pr_number: int,
    pr_sha: str,
    run: dict,
    pattern: dict,
    dry_run: bool,
    token: str,
) -> None:
    """Post a structured RCA + @copilot tag comment to the PR."""
    sha12 = pr_sha[:12]
    run_id = run["id"]
    workflow_name = run.get("name", "Unknown workflow")
    run_url = run.get("html_url", "")
    branch = run.get("head_branch", "")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    body = (
        f"<!-- proactive-ci-monitor:{sha12}:{run_id} -->\n"
        f"## 🔍 Proactive CI Monitor — Failure Detected\n\n"
        f"**Workflow:** `{workflow_name}`  \n"
        f"**Run:** [{run_id}]({run_url})  \n"
        f"**Branch:** `{branch}`  \n"
        f"**Commit:** `{sha12}`  \n"
        f"**Detected at:** {now}  \n"
        f"**Pattern:** `{pattern['id']}` ({pattern['category']})\n\n"
        f"### Fix\n\n"
        f"```\n{pattern['fix']}\n```\n\n"
        f"@copilot Fix the failing CI workflow \"{workflow_name}\" (run #{run_id}).\n\n"
        f"**Steps:**\n"
        f"1. Load `.codex/CODEBASE_AGENCY_POLICY.md` (§0 — fix ALL issues)\n"
        f"2. Check logs: {run_url}\n"
        f"3. Apply pattern fix above\n"
        f"4. Run `python scripts/ci/auto_fix_common_issues.py --check-only` to verify\n"
        f"5. Update `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`\n"
        f"6. Push fix and confirm CI is green\n\n"
        f"_Posted by: proactive-ci-monitor.yml (authoritative safety net)_\n"
        f"_[🔗 Workflow run]({run_url})_\n"
    )

    if dry_run:
        logger.info(
            "[DRY-RUN] Would post comment to PR #%d for run %d (%s)",
            pr_number,
            run_id,
            pattern["id"],
        )
        return

    try:
        _gh(
            f"/repos/{repo}/issues/{pr_number}/comments",
            token,
            method="POST",
            body={"body": body},
        )
        logger.info("Posted rescue comment to PR #%d (run %d, %s)", pr_number, run_id, pattern["id"])
    except Exception as exc:
        logger.error("Failed to post comment to PR #%d: %s", pr_number, exc)


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------


def scan(
    repo: str,
    token: str,
    dry_run: bool,
    max_age_h: int,
    target_pr: int = 0,
    min_confidence: float = 0.5,
) -> dict:
    """Scan open PRs and post rescue comments for unhandled failures.

    Parameters
    ----------
    repo:         ``owner/repo`` string.
    token:        GitHub PAT with ``repo`` + ``workflow`` + ``pull-requests`` scopes.
    dry_run:      If True, analyse but do not post any comments.
    max_age_h:    Only consider failures younger than this many hours.
    target_pr:    When > 0, scan only this PR number (single-PR mode).
    min_confidence: Only escalate patterns whose confidence is at or above this
                  threshold (0.0 = all, 1.0 = only 100% certain matches).
    """
    report: dict = {
        "scanned_prs": 0,
        "failed_runs": 0,
        "escalated": 0,
        "skipped_transient": 0,
        "below_confidence": 0,
        "already_addressed": 0,
        "details": [],
        "config": {
            "dry_run": dry_run,
            "max_age_h": max_age_h,
            "target_pr": target_pr,
            "min_confidence": min_confidence,
        },
    }

    now = datetime.now(timezone.utc)
    age_cutoff_s = max_age_h * 3600

    # ── Fetch PRs (single-PR mode or all-open) ─────────────────────────────
    if target_pr > 0:
        logger.info("Single-PR mode: scanning PR #%d in %s", target_pr, repo)
        try:
            pr_data = _gh(f"/repos/{repo}/pulls/{target_pr}", token)
            prs = [pr_data]
        except Exception as exc:
            logger.error("Could not fetch PR #%d: %s", target_pr, exc)
            return report
    else:
        logger.info("All-open-PR mode: fetching PRs for %s …", repo)
        prs = _list_open_prs(repo, token)

    logger.info("Scanning %d open PR(s).", len(prs))
    report["scanned_prs"] = len(prs)

    # Per-PR classification history: maps pr_number → list of prior result dicts.
    # Passed to ci.health.analyzer so it can detect recurrence / flap trends.
    _pr_history: dict[int, list[dict]] = {}

    for pr in prs:
        pr_number: int = pr["number"]
        pr_sha: str = pr["head"]["sha"]
        sha12 = pr_sha[:12]

        runs = _latest_runs_for_sha(repo, pr_sha, token)
        for run in runs:
            conclusion = run.get("conclusion")
            if conclusion not in {"failure", "cancelled", "timed_out"}:
                continue

            # Age filter
            updated_at = run.get("updated_at", "")
            if updated_at:
                try:
                    run_dt = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    if (now - run_dt).total_seconds() > age_cutoff_s:
                        continue
                except ValueError:  # malformed timestamp — skip age-filtering for this run
                    pass

            report["failed_runs"] += 1
            run_id: int = run["id"]
            workflow_name: str = run.get("name", "")

            # Classify — pass accumulated history for this PR so ci.health.analyzer
            # can compute recurrence / flap trends across runs in this scan.
            log_text = _get_run_logs_text(repo, run_id, token)
            log_text = f"{workflow_name}\n{log_text}"
            prior_history = _pr_history.get(pr_number, [])
            pattern = _classify(log_text, history=prior_history)

            detail: dict = {
                "pr": pr_number,
                "sha": sha12,
                "run_id": run_id,
                "workflow": workflow_name,
                "pattern_id": pattern["id"],
                "category": pattern["category"],
                "confidence": pattern["confidence"],
                "trend": pattern.get("trend"),
                "action": None,
            }

            # Accumulate this result into per-PR history for subsequent runs
            _pr_history.setdefault(pr_number, []).append(
                {
                    "pattern_id": pattern["id"],
                    "category": pattern["category"],
                    "confidence": pattern["confidence"],
                }
            )

            # Skip transient
            if pattern["category"] in _SKIP_CATEGORIES:
                report["skipped_transient"] += 1
                detail["action"] = "skipped-transient"
                report["details"].append(detail)
                continue

            # Confidence gate
            if pattern["confidence"] < min_confidence:
                report["below_confidence"] += 1
                detail["action"] = f"below-confidence-{pattern['confidence']:.2f}"
                report["details"].append(detail)
                logger.debug(
                    "PR #%d run %d: pattern %s confidence %.2f < threshold %.2f — skipping",
                    pr_number, run_id, pattern["id"], pattern["confidence"], min_confidence,
                )
                continue

            # Duplicate check
            already = _existing_rescue_comment(repo, pr_number, sha12, run_id, token)
            if already:
                report["already_addressed"] += 1
                detail["action"] = "already-addressed"
                report["details"].append(detail)
                continue

            # Escalate
            _post_rescue_comment(repo, pr_number, pr_sha, run, pattern, dry_run, token)
            report["escalated"] += 1
            detail["action"] = "escalated" if not dry_run else "dry-run"
            report["details"].append(detail)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Proactive CI Monitor — scan open PRs for unaddressed failures and "
            "post @copilot rescue comments.\n\n"
            "IMMEDIATE USE (before merging to main):\n"
            "  gh workflow run 'proactive-ci-monitor.yml' \\\n"
            "    --ref copilot/research-ai-agent-skills-architecture \\\n"
            "    -f scope=all-open-prs -f dry_run=false\n\n"
            "Or from the GitHub Actions UI:\n"
            "  Actions → 🔍 Proactive CI Monitor → Run workflow\n"
            "  (select branch: copilot/research-ai-agent-skills-architecture)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--repo",
        default=os.environ.get("GITHUB_REPOSITORY", ""),
        help="owner/repo  (default: $GITHUB_REPOSITORY)",
    )
    parser.add_argument(
        "--token",
        default=os.environ.get("GITHUB_TOKEN", ""),
        help="GitHub PAT  (default: $GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=os.environ.get("PROACTIVE_DRY_RUN", "0") == "1",
        help="Analyse only — do not post any comments",
    )
    parser.add_argument(
        "--max-age-h",
        type=int,
        default=int(os.environ.get("PROACTIVE_MAX_AGE_H", "24")),
        help="Only consider failures younger than N hours  (default: 24)",
    )
    parser.add_argument(
        "--target-pr",
        type=int,
        default=0,
        help="Scan only this PR number (0 = all open PRs)",
    )
    parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.5,
        help="Minimum pattern confidence to escalate [0.0–1.0]  (default: 0.5)",
    )
    parser.add_argument(
        "--output",
        default="",
        help="Write JSON report to this path",
    )
    args = parser.parse_args()

    if not args.repo:
        logger.error("--repo is required (or set GITHUB_REPOSITORY)")
        return 1
    if not args.token:
        logger.error("--token is required (or set GITHUB_TOKEN)")
        return 1

    report = scan(
        args.repo,
        args.token,
        args.dry_run,
        args.max_age_h,
        target_pr=args.target_pr,
        min_confidence=args.min_confidence,
    )

    print(json.dumps(report, indent=2))

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(report, fh, indent=2)
        logger.info("Report written to %s", args.output)

    logger.info(
        "Done — %d PR(s) | %d failed run(s) | %d escalated | "
        "%d transient skipped | %d below-confidence | %d already addressed",
        report["scanned_prs"],
        report["failed_runs"],
        report["escalated"],
        report["skipped_transient"],
        report.get("below_confidence", 0),
        report["already_addressed"],
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
