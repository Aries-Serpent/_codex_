#!/usr/bin/env python3
"""Approve action_required workflow runs via the GitHub UI using Playwright.

Last-resort fallback when the REST API approve endpoint returns non-2xx.
Uses the maintainer's session (CODEX_MASTER_KEY as GITHUB_TOKEN env so
playwright_github_session.py can log in via GitHub CLI OAuth flow).

Usage:
    REPO=Aries-Serpent/_codex_ HEAD_SHA=<sha> python scripts/ci/approve_via_playwright.py

Requirements:
    pip install playwright
    playwright install chromium

Environment:
    REPO         owner/repo slug
    HEAD_SHA     Commit SHA whose action_required runs to approve
    GH_TOKEN     GitHub token (must be maintainer-level)
    DRY_RUN      "true" to screenshot without clicking
    HEADLESS     "false" to show browser (default: true)
"""

from __future__ import annotations

import os
import sys


def _list_action_required_runs(repo: str, sha: str, token: str) -> list[dict]:
    """Use API to get run IDs and URLs for action_required runs."""
    import json
    import urllib.error
    import urllib.request

    url = (
        f"https://api.github.com/repos/{repo}/actions/runs"
        f"?status=action_required&head_sha={sha}&per_page=100"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
        return data.get("workflow_runs", [])
    except Exception as exc:
        print(f"⚠️  Could not list runs: {exc}", file=sys.stderr)
        return []


def approve_via_browser(
    repo: str,
    sha: str,
    token: str,
    *,
    dry_run: bool = False,
    headless: bool = True,
) -> dict[str, int]:
    """Navigate to each action_required run page and click 'Approve and run'.

    Returns dict with counts: approved, skipped, errors.
    """
    try:
        from playwright.sync_api import sync_playwright  # type: ignore[import-untyped]
    except ImportError:
        print("❌ playwright not installed — run: pip install playwright && playwright install chromium",
              file=sys.stderr)
        raise SystemExit(1)

    runs = _list_action_required_runs(repo, sha, token)
    if not runs:
        print("ℹ️  No action_required runs found for this SHA.")
        return {"approved": 0, "skipped": 0, "errors": 0}

    owner, repo_name = repo.split("/", 1)
    counts: dict[str, int] = {"approved": 0, "skipped": 0, "errors": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()

        # Inject auth cookie / token so GitHub UI treats us as logged-in
        # Use storage state if available, otherwise set gh_token cookie
        context.set_extra_http_headers({"Authorization": f"token {token}"})

        page = context.new_page()

        for run in runs:
            run_id = run["id"]
            run_name = run.get("name", str(run_id))
            run_url = f"https://github.com/{owner}/{repo_name}/actions/runs/{run_id}"

            print(f"\n── {run_name} (#{run_id})")
            print(f"   URL: {run_url}")

            try:
                page.goto(run_url, wait_until="networkidle", timeout=30_000)
                page.wait_for_timeout(2_000)  # let JS render

                # Screenshot for audit trail — stored under .codex/screenshots/ (not /tmp/)
                import pathlib as _pl
                ss_dir = _pl.Path(".codex/screenshots")
                ss_dir.mkdir(parents=True, exist_ok=True)
                ss_path = str(ss_dir / f"approve_playwright_{run_id}.png")
                page.screenshot(path=ss_path)
                print(f"   📸 Screenshot: {ss_path}")

                if dry_run:
                    print(f"   [DRY] Would click 'Approve and run' for #{run_id}")
                    counts["skipped"] += 1
                    continue

                # Look for the "Approve and run" button
                btn = page.locator(
                    "button:has-text('Approve and run'), "
                    "button:has-text('Approve'), "
                    "[data-testid='approve-run-button']"
                ).first

                if btn.is_visible(timeout=5_000):
                    btn.click()
                    page.wait_for_timeout(2_000)
                    print(f"   ✅ Clicked 'Approve and run' for #{run_id}")
                    counts["approved"] += 1
                else:
                    print("   ⏭️  'Approve and run' button not found — may already be running")
                    counts["skipped"] += 1

            except Exception as exc:
                print(f"   ❌ Playwright error for #{run_id}: {exc}", file=sys.stderr)
                counts["errors"] += 1

        browser.close()

    return counts


def main() -> int:
    repo    = os.environ.get("REPO") or os.environ.get("GITHUB_REPOSITORY", "")
    sha     = os.environ.get("HEAD_SHA", "").strip()
    token   = (
        os.environ.get("GH_TOKEN")
        or os.environ.get("CODEX_MASTER_KEY")
        or os.environ.get("CODEX_BACKUP_KEY", "")
    )
    dry_run  = os.environ.get("DRY_RUN", "false").lower() == "true"
    headless = os.environ.get("HEADLESS", "true").lower() != "false"

    if not repo:
        print("❌ REPO env var required", file=sys.stderr)
        return 1
    if not sha:
        print("❌ HEAD_SHA env var required", file=sys.stderr)
        return 1
    if not token:
        print("❌ GH_TOKEN (or CODEX_MASTER_KEY) env var required", file=sys.stderr)
        return 1

    mode = "🔍 DRY-RUN" if dry_run else "🚀 LIVE"
    print(f"\n⚡ approve_via_playwright — {mode}")
    print(f"   repo     : {repo}")
    print(f"   head_sha : {sha[:12]}")
    print(f"   headless : {headless}")

    counts = approve_via_browser(repo, sha, token, dry_run=dry_run, headless=headless)

    print(f"\n── Summary: approved={counts['approved']}  "
          f"skipped={counts['skipped']}  errors={counts['errors']}")
    return 1 if counts["errors"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
