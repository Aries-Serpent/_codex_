#!/usr/bin/env python3
"""wec_enforcer.py — Workflow Execution Checklist (WEC) enforcement tool.

Modes
-----
--validate-body --pr N
    Fetch PR body and validate WEC section integrity.

--check-workflow FILENAME.yml --pr N
    Exit 0 if workflow should run, 2 if it should be skipped, 1 on error.

--detect-changes
    Read BODY_BEFORE / BODY_AFTER env vars; output JSON diff of WEC state.

--cancel-unchecked --pr N --head-sha SHA --repo REPO
    Cancel in-progress runs for workflows that were unchecked in WEC.

--dispatch-checked --pr N --head-sha SHA --repo REPO
    Dispatch workflows that were newly checked in WEC (from NEWLY_CHECKED env).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# ---------------------------------------------------------------------------
# Import canonical WEC items from session_wrapup_autofix (with fallback)
# ---------------------------------------------------------------------------

try:
    import importlib.util as _ilu
    import pathlib as _pathlib

    _swa_path = _pathlib.Path(__file__).parent / "session_wrapup_autofix.py"
    _spec = _ilu.spec_from_file_location("session_wrapup_autofix", _swa_path)
    _swa = _ilu.module_from_spec(_spec)  # type: ignore[arg-type]
    _spec.loader.exec_module(_swa)  # type: ignore[union-attr]
    _WEC_ITEMS: list[tuple[str, str, bool]] = _swa._WEC_ITEMS
    _WEC_ALWAYS_REQUIRED: frozenset[str] = _swa._WEC_ALWAYS_REQUIRED
except Exception:
    # Fallback — minimal hard-coded list so the script stays self-contained.
    _WEC_ITEMS = [
        ("pre-merge-validation.yml",    "Pre-merge checks",                  True),
        ("comment-review-gate.yml",     "Comment review gate",               True),
        ("deferral-language-gate.yml",  "Deferral language guard",           True),
        ("agent-auth-delegation.yml",   "Agent token delegation",            True),
        ("workflow-execution-gate.yml", "WEC gate",                          True),
        ("copilot-agent-checkin.yml",   "Agent check-in",                    True),
        ("copilot-agent-session-done.yml", "Auto-post review",               True),
        ("copilot-iterative-self-healing.yml", "Iterative self-healing",     True),
        ("cost-gate.yml",               "Cost governance gate",              True),
    ]
    _WEC_ALWAYS_REQUIRED: frozenset[str] = frozenset(  # type: ignore[no-redef]
        fname for fname, _, req in _WEC_ITEMS if req
    )

# ---------------------------------------------------------------------------
# GitHub API helper
# ---------------------------------------------------------------------------

def _gh_api(
    method: str,
    path: str,
    token: str,
    body: dict | None = None,
    *,
    base_url: str = "https://api.github.com",
) -> tuple[int, object]:
    url = f"{base_url}{path}"
    data = json.dumps(body).encode() if body else None
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {}
        return exc.code, err_body


def _get_token() -> str:
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        print("❌ GH_TOKEN env var is required", file=sys.stderr)
        sys.exit(1)
    return token


def _get_repo() -> str:
    repo = os.environ.get("REPO", "").strip()
    if not repo:
        print("❌ REPO env var is required", file=sys.stderr)
        sys.exit(1)
    return repo


# ---------------------------------------------------------------------------
# WEC parsing helpers
# ---------------------------------------------------------------------------

_WEC_HEADING = "## 🔄 Workflow Execution Checklist"
_CHECKBOX_RE = re.compile(r"^- \[([ xX])\]\s+([\w\-][\w\-]*(?:\.yml)?)", re.MULTILINE)


def _extract_wec_section(body: str) -> str:
    """Return the raw WEC section text from a PR body, or empty string."""
    idx = body.find(_WEC_HEADING)
    if idx == -1:
        return ""
    rest = body[idx:]
    # Find next ## heading (but not the same one)
    next_heading = re.search(r"\n## ", rest[3:])
    if next_heading:
        return rest[: next_heading.start() + 3]
    return rest


def _parse_wec_checkboxes(body: str) -> dict[str, bool]:
    """Return filename → checked mapping from WEC section in body."""
    section = _extract_wec_section(body)
    result: dict[str, bool] = {}
    for m in _CHECKBOX_RE.finditer(section):
        state, filename = m.group(1), m.group(2)
        result[filename] = state.lower() == "x"
    return result


def _fetch_pr_body(token: str, repo: str, pr_number: int) -> str:
    status, data = _gh_api("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status != 200 or not isinstance(data, dict):
        print(f"❌ Failed to fetch PR #{pr_number}: HTTP {status}", file=sys.stderr)
        sys.exit(1)
    return data.get("body") or ""


# ---------------------------------------------------------------------------
# Mode: --validate-body
# ---------------------------------------------------------------------------

def cmd_validate_body(pr_number: int) -> int:
    token = _get_token()
    repo = _get_repo()
    body = _fetch_pr_body(token, repo, pr_number)

    section = _extract_wec_section(body)
    if not section:
        print(f"❌ PR #{pr_number}: No WEC section ('{_WEC_HEADING}') found.")
        return 1

    print(f"✅ PR #{pr_number}: WEC section found.")
    checkboxes = _parse_wec_checkboxes(body)
    errors: list[str] = []

    for fname, label, always_required in _WEC_ITEMS:
        if not always_required:
            continue
        checked = checkboxes.get(fname)
        if checked is None:
            errors.append(f"  ❌ MISSING required item: {fname} — {label}")
        elif not checked:
            errors.append(f"  ❌ UNCHECKED required item: {fname} — {label}")
        else:
            print(f"  ✅ {fname}")

    if errors:
        print("\nWEC validation FAILED:")
        for e in errors:
            print(e)
        return 1

    print("\n✅ WEC validation passed — all always-required items are checked.")
    return 0


# ---------------------------------------------------------------------------
# Mode: --check-workflow
# ---------------------------------------------------------------------------

def cmd_check_workflow(workflow_filename: str, pr_number: int) -> int:
    """Return 0=run, 2=skip, 1=error."""
    if workflow_filename in _WEC_ALWAYS_REQUIRED:
        print(f"✅ {workflow_filename} is always-required — run it.")
        return 0

    token = _get_token()
    repo = _get_repo()
    body = _fetch_pr_body(token, repo, pr_number)
    checkboxes = _parse_wec_checkboxes(body)

    if workflow_filename not in checkboxes:
        print(f"ℹ️  {workflow_filename} not found in WEC — defaulting to run.")
        return 0

    if checkboxes[workflow_filename]:
        print(f"✅ {workflow_filename} is checked [x] — run it.")
        return 0

    print(f"⏭️  {workflow_filename} is unchecked [ ] — skip it.")
    return 2


# ---------------------------------------------------------------------------
# Mode: --detect-changes
# ---------------------------------------------------------------------------

def cmd_detect_changes() -> int:
    body_before = os.environ.get("BODY_BEFORE", "")
    body_after = os.environ.get("BODY_AFTER", "")

    before = _parse_wec_checkboxes(body_before)
    after = _parse_wec_checkboxes(body_after)

    all_filenames = set(before) | set(after)
    newly_checked: list[str] = []
    newly_unchecked: list[str] = []

    for fname in sorted(all_filenames):
        was = before.get(fname, False)
        is_now = after.get(fname, False)
        if not was and is_now:
            newly_checked.append(fname)
        elif was and not is_now:
            newly_unchecked.append(fname)

    result = {
        "newly_checked": newly_checked,
        "newly_unchecked": newly_unchecked,
        "always_required": sorted(_WEC_ALWAYS_REQUIRED),
    }
    print(json.dumps(result))
    return 0


# ---------------------------------------------------------------------------
# Mode: --cancel-unchecked
# ---------------------------------------------------------------------------

def _get_unchecked_workflows(token: str, repo: str, pr_number: int) -> list[str]:
    body = _fetch_pr_body(token, repo, pr_number)
    checkboxes = _parse_wec_checkboxes(body)
    result: list[str] = []
    for fname, checked in checkboxes.items():
        if not checked and fname not in _WEC_ALWAYS_REQUIRED:
            result.append(fname)
    return result


def _list_runs_for_workflow(
    token: str,
    repo: str,
    workflow_filename: str,
    head_sha: str,
    branch: str | None = None,
) -> list[dict]:
    """Return in-progress or queued runs for a workflow matching head_sha."""
    # Require at least 7 chars for a meaningful SHA prefix comparison.
    sha_prefix = head_sha.strip()[:12] if len(head_sha.strip()) >= 7 else head_sha.strip()
    runs: list[dict] = []
    for status in ("in_progress", "queued"):
        path = (
            f"/repos/{repo}/actions/workflows/{urllib.parse.quote(workflow_filename)}"
            f"/runs?status={status}&per_page=50"
        )
        if branch:
            path += f"&branch={urllib.parse.quote(branch)}"
        _, data = _gh_api("GET", path, token)
        if isinstance(data, dict):
            for run in data.get("workflow_runs", []):
                if run.get("head_sha", "").startswith(sha_prefix):
                    runs.append(run)
    return runs


def cmd_cancel_unchecked(pr_number: int, head_sha: str, repo: str) -> int:
    token = _get_token()
    branch = os.environ.get("HEAD_BRANCH", "").strip() or None
    unchecked = os.environ.get("NEWLY_UNCHECKED", "").strip()
    workflows: list[str]
    if unchecked and unchecked != "[]":
        try:
            workflows = json.loads(unchecked)
        except Exception:
            workflows = _get_unchecked_workflows(token, repo, pr_number)
    else:
        workflows = _get_unchecked_workflows(token, repo, pr_number)

    cancelled = 0
    skipped = 0
    for wf in workflows:
        if wf in _WEC_ALWAYS_REQUIRED:
            skipped += 1
            continue
        runs = _list_runs_for_workflow(token, repo, wf, head_sha, branch)
        for run in runs:
            run_id = run["id"]
            status_code, _ = _gh_api(
                "POST", f"/repos/{repo}/actions/runs/{run_id}/cancel", token
            )
            if status_code in (202, 204):
                print(f"🛑 Cancelled run #{run_id} for {wf}")
                cancelled += 1
            else:
                print(f"⚠️  Could not cancel run #{run_id} for {wf}: HTTP {status_code}")

    print(f"\nSummary: {cancelled} run(s) cancelled, {skipped} always-required skipped.")
    return 0


# ---------------------------------------------------------------------------
# Mode: --dispatch-checked
# ---------------------------------------------------------------------------

def cmd_dispatch_checked(pr_number: int, head_sha: str, repo: str) -> int:
    token = _get_token()
    branch = os.environ.get("HEAD_BRANCH", "").strip()
    if not branch:
        print("❌ HEAD_BRANCH env var is required for --dispatch-checked", file=sys.stderr)
        sys.exit(1)

    newly_checked_raw = os.environ.get("NEWLY_CHECKED", "").strip()
    if not newly_checked_raw or newly_checked_raw == "[]":
        print("ℹ️  No newly-checked workflows to dispatch.")
        return 0

    try:
        workflows: list[str] = json.loads(newly_checked_raw)
    except Exception:
        print(f"❌ Could not parse NEWLY_CHECKED JSON: {newly_checked_raw!r}", file=sys.stderr)
        return 1

    dispatched = 0
    skipped = 0
    for wf in workflows:
        if wf in _WEC_ALWAYS_REQUIRED:
            print(f"⏭️  Skipping {wf} — always-required (fires automatically)")
            skipped += 1
            continue
        path = (
            f"/repos/{repo}/actions/workflows/{urllib.parse.quote(wf)}/dispatches"
        )
        status_code, resp = _gh_api("POST", path, token, {"ref": branch})
        if status_code in (200, 201, 204):
            print(f"🚀 Dispatched {wf} on branch {branch!r}")
            dispatched += 1
        else:
            print(f"⚠️  Failed to dispatch {wf}: HTTP {status_code} — {resp}")

    print(f"\nSummary: {dispatched} workflow(s) dispatched, {skipped} always-required skipped.")
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="WEC enforcement tool — validates, detects changes, cancels/dispatches workflows."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--validate-body", action="store_true",
                       help="Validate that all always-required WEC items are checked.")
    group.add_argument("--check-workflow", metavar="FILENAME.yml",
                       help="Check if a specific workflow should run (exits 0=run, 2=skip).")
    group.add_argument("--detect-changes", action="store_true",
                       help="Detect WEC checkbox changes between BODY_BEFORE and BODY_AFTER.")
    group.add_argument("--cancel-unchecked", action="store_true",
                       help="Cancel in-progress runs for unchecked workflows.")
    group.add_argument("--dispatch-checked", action="store_true",
                       help="Dispatch newly-checked workflows.")

    parser.add_argument("--pr", type=int, metavar="N",
                        help="Pull request number.")
    parser.add_argument("--head-sha", metavar="SHA",
                        help="HEAD commit SHA (used for cancel/dispatch).")
    parser.add_argument("--repo", metavar="OWNER/REPO",
                        help="Repository slug (overrides REPO env var).")
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    # Allow --repo flag to override env var
    if args.repo:
        os.environ["REPO"] = args.repo

    if args.validate_body:
        if not args.pr:
            parser.error("--validate-body requires --pr N")
        sys.exit(cmd_validate_body(args.pr))

    elif args.check_workflow:
        if not args.pr:
            parser.error("--check-workflow requires --pr N")
        sys.exit(cmd_check_workflow(args.check_workflow, args.pr))

    elif args.detect_changes:
        sys.exit(cmd_detect_changes())

    elif args.cancel_unchecked:
        if not args.pr:
            parser.error("--cancel-unchecked requires --pr N")
        head_sha = args.head_sha or os.environ.get("HEAD_SHA", "")
        repo = _get_repo()
        if not head_sha:
            print("❌ --head-sha or HEAD_SHA env var is required", file=sys.stderr)
            sys.exit(1)
        sys.exit(cmd_cancel_unchecked(args.pr, head_sha, repo))

    elif args.dispatch_checked:
        if not args.pr:
            parser.error("--dispatch-checked requires --pr N")
        head_sha = args.head_sha or os.environ.get("HEAD_SHA", "")
        repo = _get_repo()
        if not head_sha:
            print("❌ --head-sha or HEAD_SHA env var is required", file=sys.stderr)
            sys.exit(1)
        sys.exit(cmd_dispatch_checked(args.pr, head_sha, repo))


if __name__ == "__main__":
    main()
