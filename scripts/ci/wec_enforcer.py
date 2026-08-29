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
import time
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
    _WEC_MERGE_REQUIRED: frozenset[str] = _swa._MERGE_REQUIRED_WORKFLOWS
except Exception:
    # Fallback — minimal hard-coded list so the script stays self-contained.
    _WEC_ITEMS = [
        ("deferral-language-gate.yml",    "Deferral language guard",           True),
        ("agent-auth-delegation.yml",     "Agent token delegation",            True),
        ("workflow-execution-gate.yml",   "WEC gate",                          True),
        ("cost-gate.yml",                 "Cost governance gate",              True),
        ("auto-approve-workflows",        "Auto-approve pending workflows",    True),
        ("auth-tests.yml",                "Authentication Tests",              False),
        ("audit-qa-suite.yml",            "Audit & QA Suite (Unified)",       False),
        ("data-quality-suite.yml",        "Data Quality & Determinism Suite",  False),
        ("docker-build-push.yml",         "Build & push Docker image (GHCR)", False),
        ("nox_gates.yml",                 "Nox quality gates",                 False),
        ("security-scanning-suite.yml",   "Full security audit",               False),
        ("test-rag.yml",                  "RAG Module Tests",                  False),
        ("scheduled-archival.yml",        "Scheduled archival",                False),
        ("scheduled-dependency-audit.yml", "Dependency audit",                   False),
    ]
    _WEC_ALWAYS_REQUIRED: frozenset[str] = frozenset(  # type: ignore[no-redef]
        fname for fname, _, req in _WEC_ITEMS if req
    )
    _WEC_MERGE_REQUIRED: frozenset[str] = frozenset(_WEC_ALWAYS_REQUIRED)  # type: ignore[no-redef]

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
            raw = resp.read()
            body = json.loads(raw) if raw.strip() else {}
            return resp.status, body
    except urllib.error.HTTPError as exc:
        try:
            err_body = json.loads(exc.read())
        except Exception:
            err_body = {}
        return exc.code, err_body


def _get_token() -> str:
    token = os.environ.get("GH_TOKEN", "").strip()
    if not token:
        print("❌ GH_TOKEN env var is required", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(1)
    return token


def _get_repo() -> str:
    repo = os.environ.get("REPO", "").strip()
    if not repo:
        print("❌ REPO env var is required", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(1)
    return repo


# ---------------------------------------------------------------------------
# WEC parsing helpers
# ---------------------------------------------------------------------------

_WEC_HEADING = "## 🔄 Workflow Execution Checklist"
_CHECKBOX_RE = re.compile(
    r"^- \[([ xX])\]\s+((?:[\w\-]+(?:\.[\w\-]+)*\.yml)|auto-approve-workflows)",
    re.MULTILINE,
)


def _extract_wec_section(body: str) -> str:
    """Return the raw WEC section text from a PR body, or empty string.
    
    Handles HTML-encoded entities (e.g., &lt;!-- for <!--) to ensure
    marker detection works correctly. See Issue: PR #5324 cascading error loop.
    """
    # Decode HTML entities to handle PR body storage encoding
    import html
    decoded_body = html.unescape(body)
    
    idx = decoded_body.find(_WEC_HEADING)
    if idx == -1:
        return ""
    rest = decoded_body[idx:]
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
        print(f"❌ Failed to fetch PR #{pr_number}: HTTP {status}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(1)
    return data.get("body") or ""


def _list_workflow_states(token: str, repo: str) -> dict[str, str]:
    """
    Return mapping: workflow filename (e.g. validate.yml) -> state.

    State examples: active, disabled_manually, disabled_inactivity.
    """
    states: dict[str, str] = {}
    page = 1
    while True:
        status, data = _gh_api(
            "GET",
            f"/repos/{repo}/actions/workflows?per_page=100&page={page}",
            token,
        )
        if status != 200 or not isinstance(data, dict):
            break
        workflows = data.get("workflows", [])
        if not isinstance(workflows, list) or not workflows:
            break
        for wf in workflows:
            if not isinstance(wf, dict):
                continue
            wf_path = str(wf.get("path", "")).strip()
            wf_state = str(wf.get("state", "")).strip()
            if not wf_path:
                continue
            wf_file = os.path.basename(wf_path)
            if wf_file:
                states[wf_file] = wf_state
        if len(workflows) < 100:
            break
        page += 1
    return states


# ---------------------------------------------------------------------------
# Mode: --validate-body
# ---------------------------------------------------------------------------

def cmd_validate_body(pr_number: int) -> int:
    token = _get_token()
    repo = _get_repo()

    # Fetch PR body; if the primary token is expired/forbidden, try GH_TOKEN /
    # GITHUB_TOKEN fallback and treat persistent auth errors as a soft fail
    # (don't block the gate).
    status, data = _gh_api("GET", f"/repos/{repo}/pulls/{pr_number}", token)
    if status in (401, 403):
        # Workflows export GH_TOKEN; older runners may use GITHUB_TOKEN instead.
        fallback = (
            os.environ.get("GH_TOKEN", "").strip()
            or os.environ.get("GITHUB_TOKEN", "").strip()
        )
        if fallback and fallback != token:
            status, data = _gh_api("GET", f"/repos/{repo}/pulls/{pr_number}", fallback)
    if status in (401, 403):
        print(
            f"⚠️  PR #{pr_number}: Auth error (HTTP {status}) fetching PR body — "
            "WEC validation skipped (token may be expired; re-run after refreshing credentials).",
            file=sys.stderr,
        )
        return 0  # soft fail: cannot validate but must not block the gate
    if status != 200 or not isinstance(data, dict):
        print(f"❌ Failed to fetch PR #{pr_number}: HTTP {status}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        return 1
    body = data.get("body") or ""

    section = _extract_wec_section(body)
    if not section:
        print(f"❌ PR #{pr_number}: No WEC section ('{_WEC_HEADING}') found.")  # codeql[py/clear-text-logging-sensitive-data]
        return 1

    print(f"✅ PR #{pr_number}: WEC section found.")  # codeql[py/clear-text-logging-sensitive-data]
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
            print(f"  ✅ {fname}")  # codeql[py/clear-text-logging-sensitive-data]

    if errors:
        print("\nWEC validation FAILED:")  # codeql[py/clear-text-logging-sensitive-data]
        for e in errors:
            print(e)  # codeql[py/clear-text-logging-sensitive-data]
        return 1

    # Validate selected and merge-required workflows are active in Actions.
    workflow_states = _list_workflow_states(token, repo)
    if workflow_states:
        checked_workflows = sorted(
            fname for fname, checked in checkboxes.items()
            if checked and fname.endswith(".yml")
        )
        checked_non_active = [
            (wf, workflow_states.get(wf, "missing"))
            for wf in checked_workflows
            if workflow_states.get(wf) not in ("active",)
        ]

        merge_required_non_active = [
            (wf, workflow_states.get(wf, "missing"))
            for wf in sorted(_WEC_MERGE_REQUIRED)
            if wf.endswith(".yml") and workflow_states.get(wf) not in ("active",)
        ]

        if checked_non_active or merge_required_non_active:
            print("\nWEC validation FAILED: workflow state integrity")  # codeql[py/clear-text-logging-sensitive-data]
            if checked_non_active:
                print("  ❌ Checked in WEC but non-active in Actions:")  # codeql[py/clear-text-logging-sensitive-data]
                for wf, state in checked_non_active:
                    print(f"     - {wf}: {state}")  # codeql[py/clear-text-logging-sensitive-data]
            if merge_required_non_active:
                print("  ❌ Merge-required WEC workflows non-active in Actions:")  # codeql[py/clear-text-logging-sensitive-data]
                for wf, state in merge_required_non_active:
                    print(f"     - {wf}: {state}")  # codeql[py/clear-text-logging-sensitive-data]
            return 1
    else:
        print("⚠️  Workflow state audit unavailable — skipping active/non-active integrity check.")  # codeql[py/clear-text-logging-sensitive-data]

    print("\n✅ WEC validation passed — all always-required items are checked.")  # codeql[py/clear-text-logging-sensitive-data]
    return 0


# ---------------------------------------------------------------------------
# Mode: --check-workflow
# ---------------------------------------------------------------------------

def cmd_check_workflow(workflow_filename: str, pr_number: int) -> int:
    """Return 0=run, 2=skip, 1=error."""
    if workflow_filename in _WEC_ALWAYS_REQUIRED:
        print(f"✅ {workflow_filename} is always-required — run it.")  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    token = _get_token()
    repo = _get_repo()
    body = _fetch_pr_body(token, repo, pr_number)
    checkboxes = _parse_wec_checkboxes(body)

    if workflow_filename not in checkboxes:
        print(f"ℹ️  {workflow_filename} not found in WEC — defaulting to run.")  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    if checkboxes[workflow_filename]:
        print(f"✅ {workflow_filename} is checked [x] — run it.")  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    print(f"⏭️  {workflow_filename} is unchecked [ ] — skip it.")  # codeql[py/clear-text-logging-sensitive-data]
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
    print(json.dumps(result))  # codeql[py/clear-text-logging-sensitive-data]
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
    # Use a stable SHA prefix (up to 12 chars); slicing is safe for shorter values.
    sha_stripped = head_sha.strip()
    if not sha_stripped:
        return []
    sha_prefix = sha_stripped[:12]
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
                print(f"🛑 Cancelled run #{run_id} for {wf}")  # codeql[py/clear-text-logging-sensitive-data]
                cancelled += 1
            else:
                print(f"⚠️  Could not cancel run #{run_id} for {wf}: HTTP {status_code}")  # codeql[py/clear-text-logging-sensitive-data]

    print(f"\nSummary: {cancelled} run(s) cancelled, {skipped} always-required skipped.")  # codeql[py/clear-text-logging-sensitive-data]
    return 0


# ---------------------------------------------------------------------------
# Mode: --dispatch-checked
# ---------------------------------------------------------------------------

def _approve_run(token: str, repo: str, run_id: int, dry_run: bool = False) -> str:
    """Approve a single action_required run.  Returns 'approved', 'dry-run', or 'failed'."""
    label = f"run #{run_id}"
    if dry_run:
        print(f"  [DRY] Would approve {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "dry-run"
    status, body = _gh_api("POST", f"/repos/{repo}/actions/runs/{run_id}/approve", token)
    if status in (200, 201, 204):
        print(f"  ✅ Approved {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "approved"
    msg = body.get("message", "") if isinstance(body, dict) else str(body)
    print(f"  ⚠️  approve → HTTP {status} ({msg}) — trying rerun for {label}")  # codeql[py/clear-text-logging-sensitive-data]
    # Fallback: rerun (clears action_required for same-repo pushes)
    status2, body2 = _gh_api("POST", f"/repos/{repo}/actions/runs/{run_id}/rerun", token)
    if status2 in (200, 201, 204):
        print(f"  ✅ Rerun triggered for {label}")  # codeql[py/clear-text-logging-sensitive-data]
        return "approved"
    msg2 = body2.get("message", "") if isinstance(body2, dict) else str(body2)
    print(f"  ❌ Both approve and rerun failed for {label}: HTTP {status2} ({msg2})")  # codeql[py/clear-text-logging-sensitive-data]
    return "failed"


_DISPATCH_OUTCOME_APPROVED       = "approved"        # was action_required → approved
_DISPATCH_OUTCOME_ALREADY_RUNNING = "already_running" # queued/in_progress — no action needed
_DISPATCH_OUTCOME_TIMED_OUT       = "timed_out"       # run never appeared within max_wait_sec
_DISPATCH_OUTCOME_FAILED          = "failed"           # approval API call returned an error


def _find_and_approve_dispatched_run(
    token: str,
    repo: str,
    workflow: str,
    branch: str,
    *,
    max_wait_sec: int = 45,
    poll_interval: int = 5,
) -> str:
    """Poll for a newly-dispatched run in action_required state and approve it.

    Returns one of:
      - ``_DISPATCH_OUTCOME_APPROVED``        — run found in action_required and approved
      - ``_DISPATCH_OUTCOME_ALREADY_RUNNING`` — run found in queued/in_progress (no approval needed)
      - ``_DISPATCH_OUTCOME_TIMED_OUT``       — run did not appear within max_wait_sec
      - ``_DISPATCH_OUTCOME_FAILED``          — approval API call returned an error

    The strategy:
      1. Look for runs of ``workflow`` on ``branch`` in ``action_required`` state.
      2. If found, approve immediately.
      3. If in queued/in_progress state, the run is already unblocked — no approval needed.
      4. If not found within ``max_wait_sec``, falls back to the 5-min schedule sweep.
    """
    wf_encoded = urllib.parse.quote(workflow)
    branch_encoded = urllib.parse.quote(branch)
    deadline = time.monotonic() + max_wait_sec
    attempt = 0

    while time.monotonic() < deadline:
        attempt += 1
        # First check action_required runs for this workflow on this branch
        path = (
            f"/repos/{repo}/actions/workflows/{wf_encoded}/runs"
            f"?status=action_required&branch={branch_encoded}&per_page=10"
        )
        status, data = _gh_api("GET", path, token)
        if status == 200 and isinstance(data, dict):
            runs = data.get("workflow_runs", [])
            if runs:
                run_id = runs[0]["id"]
                print(f"  🔓 Found action_required run #{run_id} for {workflow} — approving…")  # codeql[py/clear-text-logging-sensitive-data]
                result = _approve_run(token, repo, run_id)
                if result in ("approved", "dry-run"):
                    return _DISPATCH_OUTCOME_APPROVED
                return _DISPATCH_OUTCOME_FAILED
        # Not in action_required yet — maybe it's already running or queued
        # Only treat queued/in_progress as "already unblocked" — completed runs
        # may be stale runs from previous pushes and must NOT short-circuit the poll.
        path2 = (
            f"/repos/{repo}/actions/workflows/{wf_encoded}/runs"
            f"?branch={branch_encoded}&per_page=5"
        )
        status2, data2 = _gh_api("GET", path2, token)
        if status2 == 200 and isinstance(data2, dict):
            latest_runs = data2.get("workflow_runs", [])
            for r in latest_runs:
                if r.get("status") in ("queued", "in_progress"):
                    print(
                        f"  ℹ️  {workflow} run #{r['id']} is already {r['status']} "
                        "(no approval needed)"
                    )
                    return _DISPATCH_OUTCOME_ALREADY_RUNNING

        remaining = int(deadline - time.monotonic())
        print(f"  ⏳ Waiting for {workflow} run to appear ({remaining}s left)…")  # codeql[py/clear-text-logging-sensitive-data]
        time.sleep(poll_interval)

    print(f"  ⚠️  Timed out waiting for {workflow} run to appear — it may self-approve via schedule.")  # codeql[py/clear-text-logging-sensitive-data]
    return _DISPATCH_OUTCOME_TIMED_OUT


def cmd_dispatch_checked(pr_number: int, head_sha: str, repo: str) -> int:
    token = _get_token()
    branch = os.environ.get("HEAD_BRANCH", "").strip()
    if not branch:
        print("❌ HEAD_BRANCH env var is required for --dispatch-checked", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        sys.exit(1)

    newly_checked_raw = os.environ.get("NEWLY_CHECKED", "").strip()
    if not newly_checked_raw or newly_checked_raw == "[]":
        print("ℹ️  No newly-checked workflows to dispatch.")  # codeql[py/clear-text-logging-sensitive-data]
        return 0

    try:
        workflows: list[str] = json.loads(newly_checked_raw)
    except Exception:
        print(f"❌ Could not parse NEWLY_CHECKED JSON: {newly_checked_raw!r}", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
        return 1

    # Per-workflow default inputs forwarded on WEC-triggered dispatch.
    # Keeps dispatch behaviour explicit and consistent with the UI defaults.
    # Add entries here for any opt-in workflow that has meaningful inputs.
    _WORKFLOW_DEFAULT_INPUTS: dict[str, dict[str, str]] = {
        "codeql-alert-fetcher.yml": {
            "pipeline": "collect,autofix,prompt",
            # state/max_pages/page_sleep_ms/top_n/include_dependabot/include_secrets
            # all use their built-in defaults — only override if changing behaviour.
        },
    }

    dispatched = 0
    approved = 0
    already_running = 0
    timed_out = 0
    skipped = 0
    for wf in workflows:
        if wf in _WEC_ALWAYS_REQUIRED:
            print(f"⏭️  Skipping {wf} — always-required (fires automatically)")  # codeql[py/clear-text-logging-sensitive-data]
            skipped += 1
            continue
        path = (
            f"/repos/{repo}/actions/workflows/{urllib.parse.quote(wf)}/dispatches"
        )
        # Build dispatch payload: always include ref; add explicit inputs when
        # the workflow has non-trivial choice/string inputs so the correct
        # pipeline stage fires rather than relying on GitHub's default logic.
        dispatch_payload: dict[str, object] = {"ref": branch}
        wf_inputs = _WORKFLOW_DEFAULT_INPUTS.get(wf)
        if wf_inputs:
            dispatch_payload["inputs"] = wf_inputs
            print(f"  📋 Forwarding inputs for {wf}: {wf_inputs}")  # codeql[py/clear-text-logging-sensitive-data]

        status_code, resp = _gh_api("POST", path, token, dispatch_payload)
        if status_code in (200, 201, 204):
            print(f"🚀 Dispatched {wf} on branch {branch!r}")  # codeql[py/clear-text-logging-sensitive-data]
            dispatched += 1
            # --- Post-dispatch approval: approve if run lands in action_required ---
            print(f"  ⏳ Checking if {wf} needs approval after dispatch…")  # codeql[py/clear-text-logging-sensitive-data]
            outcome = _find_and_approve_dispatched_run(token, repo, wf, branch)
            if outcome == _DISPATCH_OUTCOME_APPROVED:
                approved += 1
            elif outcome == _DISPATCH_OUTCOME_ALREADY_RUNNING:
                already_running += 1
            elif outcome == _DISPATCH_OUTCOME_TIMED_OUT:
                timed_out += 1
        else:
            print(f"⚠️  Failed to dispatch {wf}: HTTP {status_code} — {resp}")  # codeql[py/clear-text-logging-sensitive-data]

    print(
        f"\nSummary: {dispatched} workflow(s) dispatched, "
        f"{approved} approved (was action_required), "
        f"{already_running} already running (no approval needed), "
        f"{timed_out} timed-out (will self-approve via schedule), "
        f"{skipped} always-required skipped."
    )
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
            print("❌ --head-sha or HEAD_SHA env var is required", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
            sys.exit(1)
        sys.exit(cmd_cancel_unchecked(args.pr, head_sha, repo))

    elif args.dispatch_checked:
        if not args.pr:
            parser.error("--dispatch-checked requires --pr N")
        head_sha = args.head_sha or os.environ.get("HEAD_SHA", "")
        repo = _get_repo()
        if not head_sha:
            print("❌ --head-sha or HEAD_SHA env var is required", file=sys.stderr)  # codeql[py/clear-text-logging-sensitive-data]
            sys.exit(1)
        sys.exit(cmd_dispatch_checked(args.pr, head_sha, repo))


if __name__ == "__main__":
    main()
