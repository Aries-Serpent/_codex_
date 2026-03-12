#!/usr/bin/env python3
"""
PR Comment Consolidator — groups multiple workflow status comments into a
single "📊 PR Status Dashboard" comment per pull request.

Instead of each workflow posting its own separate comment (creating comment
noise), all workflows call this script (or the companion GitHub Action) to
update a single consolidated comment.  Informational results appear in
collapsible ``<details>`` sections; only actionable issues surface at the top.

Usage (from GitHub Actions step)
---------------------------------
    python scripts/ci/pr_comment_consolidator.py \\
        --pr-number  "${{ github.event.pull_request.number }}" \\
        --workflow   "Semgrep Security Scan" \\
        --status     "success" \\
        --summary    "No security issues found" \\
        --details    "Scanned 1 243 files; 0 findings."

Environment variables (GitHub-injected)
----------------------------------------
    GITHUB_TOKEN          — or CODEX_MASTER_KEY — used for API calls
    GITHUB_REPOSITORY     — e.g. "Aries-Serpent/_codex_"

Exit codes
----------
    0   success (comment posted or updated)
    1   missing required arg or API error
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional

# ── sentinel embedded in every dashboard comment ─────────────────────────────
_MARKER = "<!-- PR_STATUS_DASHBOARD_v1 -->"
_SEPARATOR = "\n---\n"

# Status icons
_ICONS = {
    "success": "✅",
    "failure": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "skipped": "⏭️",
    "in_progress": "🔄",
}


# ── GitHub API helpers ────────────────────────────────────────────────────────

def _token() -> str:
    tok = os.environ.get("GITHUB_TOKEN") or os.environ.get("CODEX_MASTER_KEY", "")
    if not tok:
        print("ERROR: GITHUB_TOKEN or CODEX_MASTER_KEY is required.", file=sys.stderr)
        sys.exit(1)
    return tok


def _repo() -> str:
    return os.environ.get("GITHUB_REPOSITORY", "Aries-Serpent/_codex_")


def _api_request(
    method: str,
    path: str,
    body: Optional[dict] = None,
    token: str = "",
) -> dict[str, Any]:
    url = f"https://api.github.com{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"GitHub API {method} {url} → {exc.code}: {detail}") from exc


def _list_comments(pr_number: int, token: str) -> list[dict]:
    repo = _repo()
    comments: list[dict] = []
    page = 1
    while True:
        batch = _api_request(
            "GET",
            f"/repos/{repo}/issues/{pr_number}/comments?per_page=100&page={page}",
            token=token,
        )
        if not batch:
            break
        comments.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return comments


def _find_dashboard_comment(pr_number: int, token: str) -> Optional[dict]:
    for comment in _list_comments(pr_number, token):
        if _MARKER in comment.get("body", ""):
            return comment
    return None


def _create_comment(pr_number: int, body: str, token: str) -> dict:
    repo = _repo()
    return _api_request(
        "POST",
        f"/repos/{repo}/issues/{pr_number}/comments",
        body={"body": body},
        token=token,
    )


def _update_comment(comment_id: int, body: str, token: str) -> dict:
    repo = _repo()
    return _api_request(
        "PATCH",
        f"/repos/{repo}/issues/comments/{comment_id}",
        body={"body": body},
        token=token,
    )


# ── comment body builder ──────────────────────────────────────────────────────

def _parse_existing(body: str) -> dict[str, str]:
    """Extract per-workflow section data from an existing dashboard comment."""
    sections: dict[str, str] = {}
    # Each section is delimited by <!-- SECTION:name --> markers
    import re

    pattern = re.compile(
        r"<!-- SECTION:([^>]+) -->(.*?)<!-- /SECTION:\1 -->",
        re.DOTALL,
    )
    for m in pattern.finditer(body):
        sections[m.group(1)] = m.group(2).strip()
    return sections


def _build_body(sections: dict[str, dict[str, str]], run_url: str = "") -> str:
    """Render the full consolidated dashboard comment body."""
    actionable = {k: v for k, v in sections.items() if v.get("status") == "failure"}
    informational = {k: v for k, v in sections.items() if v.get("status") != "failure"}

    lines: list[str] = [
        _MARKER,
        "## 📊 PR Status Dashboard",
        "",
        f"_Last updated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} "
        + (f"· [View run]({run_url})" if run_url else "") + "_",
        "",
    ]

    # ── Actionable issues (failures) ─────────────────────────────────────────
    if actionable:
        lines += [
            "### 🔴 Issues Requiring Attention",
            "",
        ]
        for name, info in actionable.items():
            icon = _ICONS.get(info.get("status", ""), "❓")
            lines += [
                "<details open>",
                f"<summary>{icon} <strong>{name}</strong> — {info.get('summary', '')}</summary>",
                "",
                info.get("details", "_No additional details._"),
                "",
                "</details>",
                "",
            ]

    # ── Informational results ─────────────────────────────────────────────────
    if informational:
        passed = sum(1 for v in informational.values() if v.get("status") == "success")
        total = len(informational)
        headline = f"✅ Informational Results ({passed}/{total} passed)"
        lines += [
            "<details>",
            f"<summary>{headline}</summary>",
            "",
            "| Workflow | Status | Summary |",
            "|----------|--------|---------|",
        ]
        for name, info in informational.items():
            icon = _ICONS.get(info.get("status", ""), "❓")
            summary = info.get("summary", "").replace("|", "\\|")
            lines.append(f"| {name} | {icon} {info.get('status', '?')} | {summary} |")

        # Expand each with full details inside nested <details>
        lines += ["", "---", ""]
        for name, info in informational.items():
            if info.get("details"):
                lines += [
                    "<details>",
                    f"<summary>📋 {name} details</summary>",
                    "",
                    info["details"],
                    "",
                    "</details>",
                    "",
                ]

        lines += ["</details>", ""]

    if not sections:
        lines += ["_No workflow results yet._", ""]

    return "\n".join(lines)


def _build_body_from_raw(raw_sections: dict[str, str]) -> str:
    """Parse serialised sections stored as JSON strings and render."""
    parsed: dict[str, dict[str, str]] = {}
    for name, blob in raw_sections.items():
        try:
            parsed[name] = json.loads(blob)
        except json.JSONDecodeError:
            parsed[name] = {"status": "info", "summary": blob, "details": ""}
    return _build_body(parsed)


# ── section storage in comment (serialise as hidden JSON blob) ────────────────

def _encode_section(name: str, status: str, summary: str, details: str) -> str:
    payload = json.dumps({"status": status, "summary": summary, "details": details})
    return (
        f"<!-- SECTION:{name} -->\n"
        f"<!-- PAYLOAD:{payload} -->\n"
        f"<!-- /SECTION:{name} -->"
    )


def _decode_sections(body: str) -> dict[str, dict[str, str]]:
    import re

    sections: dict[str, dict[str, str]] = {}
    for m in re.finditer(
        r"<!-- SECTION:([^>]+) -->\s*<!-- PAYLOAD:(\{.*?\}) -->\s*<!-- /SECTION:\1 -->",
        body,
        re.DOTALL,
    ):
        name = m.group(1)
        try:
            sections[name] = json.loads(m.group(2))
        except json.JSONDecodeError:
            sections[name] = {"status": "info", "summary": m.group(2), "details": ""}
    return sections


# ── main logic ────────────────────────────────────────────────────────────────

def consolidate(
    pr_number: int,
    workflow_name: str,
    status: str,
    summary: str,
    details: str,
    run_url: str = "",
    token: str = "",
) -> None:
    """Update (or create) the consolidated PR Status Dashboard comment."""
    if not token:
        token = _token()

    # Fetch existing dashboard comment if any
    existing = _find_dashboard_comment(pr_number, token)
    if existing:
        sections = _decode_sections(existing["body"])
    else:
        sections = {}

    # Update this workflow's section
    sections[workflow_name] = {
        "status": status,
        "summary": summary,
        "details": details,
    }

    # Build the new body: human-readable table + hidden section payloads
    visible = _build_body(sections, run_url=run_url)
    hidden_blobs = "\n".join(
        _encode_section(name, info["status"], info["summary"], info["details"])
        for name, info in sections.items()
    )
    full_body = visible + "\n\n<!-- SECTIONS_DATA -->\n" + hidden_blobs

    if existing:
        _update_comment(existing["id"], full_body, token)
        print(f"✅ Updated PR #{pr_number} dashboard comment (id {existing['id']})")
    else:
        result = _create_comment(pr_number, full_body, token)
        print(f"✅ Created PR #{pr_number} dashboard comment (id {result['id']})")


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pr-number", type=int, required=True, help="Pull request number")
    p.add_argument("--workflow", required=True, help="Workflow / check name (e.g. 'Semgrep Scan')")
    p.add_argument("--status", required=True,
                   choices=["success", "failure", "warning", "info", "skipped", "in_progress"],
                   help="Outcome of this workflow run")
    p.add_argument("--summary", default="", help="One-line result summary")
    p.add_argument("--details", default="", help="Extended markdown details (optional)")
    p.add_argument("--run-url", default="", help="Link to this Actions run")
    p.add_argument("--token", default="", help="GitHub token (falls back to GITHUB_TOKEN env var)")
    args = p.parse_args()

    try:
        consolidate(
            pr_number=args.pr_number,
            workflow_name=args.workflow,
            status=args.status,
            summary=args.summary,
            details=args.details,
            run_url=args.run_url,
            token=args.token,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
