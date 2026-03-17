#!/usr/bin/env python3
"""
PR Comment Consolidator — groups multiple workflow status comments into a
single "📊 PR Status Dashboard" comment per pull request.

Instead of each workflow posting its own separate comment (creating comment
noise), all workflows call this script (or the companion GitHub Action) to
update a single consolidated comment.  Informational results appear in
collapsible ``<details>`` sections; only actionable issues surface at the top.

Every dashboard update now includes a **Merge Readiness Score** (0–100) at the
top of the comment so reviewers always know the PR's merge state at a glance:

    ≥ 85  →  🟢 Merge-ready
    60–84 →  🟡 Needs minor work
    < 60  →  🔴 Blocking work required

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
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Optional

# ── OTel coherence wiring (S144) ─────────────────────────────────────────────
# Emit a coherence observation each time the consolidator records workflow
# outcomes so the in-memory histogram tracks CI policy alignment over time.
try:
    _CONSOLIDATOR_ROOT = __file__
    import pathlib as _pathlib
    _SRC_DIR = str(_pathlib.Path(_CONSOLIDATOR_ROOT).resolve().parents[2] / "src")
    if _SRC_DIR not in sys.path:
        sys.path.insert(0, _SRC_DIR)
    from codex.monitoring.otel_metrics import (  # noqa: E402
        compute_coherence,
        workflow_coherence_score,
    )
    _OTEL_AVAILABLE = True
except Exception:
    _OTEL_AVAILABLE = False

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
) -> Any:
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
            raw = resp.read()
            return json.loads(raw) if raw else None  # 204 No Content → None
    except urllib.error.HTTPError:
        raise  # callers catch urllib.error.HTTPError directly


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
    """Return the most recently updated dashboard comment, or None.

    Returning the most-recently-updated comment (rather than the first/oldest)
    ensures that when duplicates exist the canonical comment is the freshest
    one.  The older duplicates are then deleted by the caller.
    """
    candidates = [
        c for c in _list_comments(pr_number, token)
        if _MARKER in c.get("body", "")
    ]
    if not candidates:
        return None
    # Prefer the most recently updated; fall back to created_at if equal.
    return max(
        candidates,
        key=lambda c: (c.get("updated_at") or c.get("created_at") or ""),
    )


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


# ── Merge Readiness Score ─────────────────────────────────────────────────────
#
# Hardened implementation (S144): every dashboard update computes and displays
# a numeric 0–100 merge readiness score so reviewers always know the PR state.
#
# Weight table (matches design doc from mbaetiong comment 4077667928):
#   CI checks passing       35%
#   Review approvals        20%
#   No merge conflicts      15%
#   Unresolved comments     15%
#   Test quality gate       10%
#   CI freshness (run age)   5%

_READINESS_THRESHOLD_GREEN  = 85   # ≥ 85 → merge-ready
_READINESS_THRESHOLD_YELLOW = 60   # 60–84 → needs minor work  / < 60 → blocking


def _fetch_pr_data(pr_number: int, token: str) -> Optional[dict]:
    """Fetch PR metadata (mergeability, reviews, checks) from GitHub API."""
    repo = _repo()
    try:
        return _api_request("GET", f"/repos/{repo}/pulls/{pr_number}", token=token)
    except Exception:  # noqa: BLE001
        return None


def _fetch_check_runs(ref: str, token: str) -> list[dict]:
    """Fetch check runs for a commit ref."""
    repo = _repo()
    try:
        result = _api_request("GET", f"/repos/{repo}/commits/{ref}/check-runs?per_page=100", token=token)
        return (result or {}).get("check_runs", [])
    except Exception:  # noqa: BLE001
        return []


def _fetch_reviews(pr_number: int, token: str) -> list[dict]:
    """Fetch PR reviews."""
    repo = _repo()
    try:
        return _api_request("GET", f"/repos/{repo}/pulls/{pr_number}/reviews?per_page=100", token=token) or []
    except Exception:  # noqa: BLE001
        return []


def _fetch_review_comments(pr_number: int, token: str) -> list[dict]:
    """Fetch review (inline) comments to estimate unresolved count."""
    repo = _repo()
    try:
        return _api_request("GET", f"/repos/{repo}/pulls/{pr_number}/comments?per_page=100", token=token) or []
    except Exception:  # noqa: BLE001
        return []


def compute_readiness(pr_number: int, token: str, sections: dict) -> dict:
    """Compute a merge readiness score (0–100) for the PR.

    Returns a dict with:
        score          int   0–100
        label          str   "Merge-ready ✅" / "Needs work ⚠️" / "Blocking ❌"
        color          str   "🟢" / "🟡" / "🔴"
        components     dict  per-component sub-scores and weights
        gaps           list  top actionable gaps (for follow-up prompt)
    """
    pr = _fetch_pr_data(pr_number, token)

    # ── component 1: CI checks (35%) ─────────────────────────────────────────
    ci_score = 0.0
    ci_detail = "unknown"
    if pr:
        checks = _fetch_check_runs(pr.get("head", {}).get("sha", ""), token)
        if checks:
            required = [c for c in checks if c.get("status") == "completed"]
            passed   = [c for c in required if c.get("conclusion") in ("success", "neutral", "skipped")]
            ci_score = len(passed) / len(required) if required else 1.0
            ci_detail = f"{len(passed)}/{len(required)} checks passing"
        else:
            # Fall back to sections in the dashboard: any failure → penalise
            failure_count = sum(1 for v in sections.values() if v.get("status") == "failure")
            total_count   = len(sections) or 1
            ci_score  = 1.0 - (failure_count / total_count)
            ci_detail = f"{total_count - failure_count}/{total_count} workflows OK (from dashboard)"
    else:
        # No PR data — use dashboard sections as proxy
        failure_count = sum(1 for v in sections.values() if v.get("status") == "failure")
        total_count   = len(sections) or 1
        ci_score  = 1.0 - (failure_count / total_count)
        ci_detail = f"{total_count - failure_count}/{total_count} workflows OK (from dashboard)"

    # ── component 2: Review approvals (20%) ──────────────────────────────────
    review_score = 0.0
    review_detail = "unknown"
    required_approvals = 1  # default; adjust if branch protection available
    if pr:
        reviews = _fetch_reviews(pr_number, token)
        # Count unique approvals (most recent review per reviewer)
        reviewer_states: dict[str, str] = {}
        for r in reviews:
            login = r.get("user", {}).get("login", "")
            state = r.get("state", "")
            if login:
                reviewer_states[login] = state
        approvals = sum(1 for s in reviewer_states.values() if s == "APPROVED")
        review_score = min(1.0, approvals / required_approvals)
        review_detail = f"{approvals} approval(s)"
    else:
        review_score = 0.5  # neutral when PR data unavailable
        review_detail = "could not fetch reviews"

    # ── component 3: No merge conflicts (15%) ─────────────────────────────────
    conflict_score = 0.0
    conflict_detail = "unknown"
    if pr:
        mergeable = pr.get("mergeable")
        if mergeable is True:
            conflict_score = 1.0
            conflict_detail = "no conflicts"
        elif mergeable is False:
            conflict_score = 0.0
            conflict_detail = "merge conflicts detected"
        else:
            # None → GitHub still computing; treat as neutral
            conflict_score = 0.5
            conflict_detail = "mergeability pending"
    else:
        conflict_score = 0.5
        conflict_detail = "could not fetch PR"

    # ── component 4: Unresolved review comments (15%) ─────────────────────────
    comment_score = 1.0
    comment_detail = "no unresolved comments"
    if pr:
        review_comments = _fetch_review_comments(pr_number, token)
        # GitHub review comments don't expose "resolved" state in REST API;
        # use count as a proxy: 0 → 1.0, each comment reduces by 0.1 (floor 0).
        unresolved_estimate = len(review_comments)
        comment_score  = max(0.0, 1.0 - unresolved_estimate * 0.1)
        comment_detail = f"~{unresolved_estimate} review comment(s)"
    else:
        comment_score  = 0.5
        comment_detail = "could not fetch review comments"

    # ── component 5: Test / quality gate (10%) ────────────────────────────────
    quality_score  = 1.0  # default pass when not measurable
    quality_detail = "not measured (default pass)"
    # If dashboard has a test/coverage section, check its status.
    for name, info in sections.items():
        if any(k in name.lower() for k in ("test", "coverage", "quality", "pytest")):
            quality_score  = 1.0 if info.get("status") == "success" else 0.0
            quality_detail = f"{name}: {info.get('status', '?')}"
            break

    # ── component 6: Freshness (CI run age) (5%) ──────────────────────────────
    freshness_score  = 1.0  # assume fresh if we can't determine otherwise
    freshness_detail = "assumed fresh"
    if pr:
        updated_at = pr.get("updated_at", "")
        if updated_at:
            try:
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                age_hours = (datetime.now(timezone.utc) - updated).total_seconds() / 3600
                if age_hours < 24:
                    freshness_score  = 1.0
                    freshness_detail = f"last update {age_hours:.1f}h ago"
                elif age_hours < 72:
                    freshness_score  = 0.5
                    freshness_detail = f"last update {age_hours:.1f}h ago (>24h)"
                else:
                    freshness_score  = 0.0
                    freshness_detail = f"last update {age_hours:.1f}h ago (>72h, stale)"
            except ValueError:
                pass

    # ── weighted composite ────────────────────────────────────────────────────
    score = round(100 * (
        0.35 * ci_score
        + 0.20 * review_score
        + 0.15 * conflict_score
        + 0.15 * comment_score
        + 0.10 * quality_score
        + 0.05 * freshness_score
    ))

    # ── label + color ─────────────────────────────────────────────────────────
    if score >= _READINESS_THRESHOLD_GREEN:
        color = "🟢"
        label = "Merge-ready ✅"
    elif score >= _READINESS_THRESHOLD_YELLOW:
        color = "🟡"
        label = "Needs minor work ⚠️"
    else:
        color = "🔴"
        label = "Blocking work required ❌"

    # ── actionable gaps (top 3 for follow-up prompt) ──────────────────────────
    gaps: list[str] = []
    if ci_score < 1.0:
        gaps.append(f"Fix failing CI checks ({ci_detail})")
    if review_score < 1.0:
        gaps.append(f"Obtain required review approval(s) ({review_detail})")
    if conflict_score < 1.0:
        gaps.append(f"Resolve merge conflicts ({conflict_detail})")
    if comment_score < 0.9:
        gaps.append(f"Address review comments ({comment_detail})")
    if quality_score < 1.0:
        gaps.append(f"Fix test/quality gate ({quality_detail})")

    return {
        "score":      score,
        "label":      label,
        "color":      color,
        "components": {
            "CI checks (35%)":             {"score": round(ci_score * 100), "detail": ci_detail},
            "Reviews (20%)":               {"score": round(review_score * 100), "detail": review_detail},
            "No conflicts (15%)":          {"score": round(conflict_score * 100), "detail": conflict_detail},
            "Unresolved comments (15%)":   {"score": round(comment_score * 100), "detail": comment_detail},
            "Test/quality gate (10%)":     {"score": round(quality_score * 100), "detail": quality_detail},
            "CI freshness (5%)":           {"score": round(freshness_score * 100), "detail": freshness_detail},
        },
        "gaps": gaps[:3],  # top 3 most impactful
    }


def _render_readiness_block(readiness: dict) -> list[str]:
    """Render the top-of-dashboard readiness score block."""
    score  = readiness["score"]
    label  = readiness["label"]
    color  = readiness["color"]
    gaps   = readiness.get("gaps", [])
    comps  = readiness.get("components", {})

    lines = [
        f"### {color} Merge Readiness: **{score} / 100** — {label}",
        "",
    ]

    if gaps:
        follow_up = "; ".join(gaps)
        lines += [
            f"> **Implementation gaps:** {follow_up}",
            "> Suggested next steps: address the items above then re-run CI.",
            "> Reply `ACTION: create checklist` to have the bot open tasks automatically.",
            "",
        ]

    if comps:
        lines += [
            "<details>",
            "<summary>📊 Readiness score breakdown</summary>",
            "",
            "| Component | Score | Detail |",
            "|-----------|------:|--------|",
        ]
        for comp_name, comp_data in comps.items():
            lines.append(f"| {comp_name} | {comp_data['score']}% | {comp_data['detail']} |")
        lines += ["", "</details>", ""]

    return lines


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


def _build_body(
    sections: dict[str, dict[str, str]],
    run_url: str = "",
    readiness: Optional[dict] = None,
) -> str:
    """Render the full consolidated dashboard comment body.

    ``readiness`` is the dict returned by ``compute_readiness()``.  When
    provided the score is rendered at the very top of the comment (hardened
    S144 requirement: every dashboard update shows the merge readiness score).
    """
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

    # ── Merge Readiness Score (always shown at top — S144 hardened) ──────────
    if readiness:
        lines += _render_readiness_block(readiness)
        lines += ["---", ""]

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
    max_retries: int = 4,
) -> None:
    """Update (or create) the consolidated PR Status Dashboard comment.

    Race-condition safe: when two workflows post simultaneously and both see
    no existing comment, the second create call will produce a 422 (if unique
    enforcement were possible) or a duplicate.  We defend against this with an
    optimistic-concurrency retry loop:

      1. Fetch the list of existing comments (find dashboard comment).
      2. Build the new body with this workflow's section merged in.
      3. If an existing comment was found  → PATCH it.
         If no comment was found           → POST a new one.
      4. On any HTTP error (conflict/rate-limit) back off and retry.
      5. After POST succeeds, immediately check for a duplicate (another
         concurrent create) and delete the older one so at most one survives.
    """
    if not token:
        token = _token()

    backoff_s = (2, 4, 8, 16)  # back-off schedule between retry attempts

    for attempt in range(max_retries + 1):
        try:
            # ── fetch ──────────────────────────────────────────────────────
            existing = _find_dashboard_comment(pr_number, token)
            if existing:
                sections = _decode_sections(existing["body"])
            else:
                sections = {}

            # ── merge ──────────────────────────────────────────────────────
            sections[workflow_name] = {
                "status": status,
                "summary": summary,
                "details": details,
            }

            # ── readiness score (hardened — always computed) ────────────────
            readiness: Optional[dict] = None
            try:
                readiness = compute_readiness(pr_number, token, sections)
            except Exception:  # noqa: BLE001
                pass  # score is best-effort; dashboard renders without it

            # ── OTel coherence emission ─────────────────────────────────────
            if _OTEL_AVAILABLE and sections:
                actual_outcomes   = {n: "success" if v.get("status") == "success" else "failure"
                                     for n, v in sections.items()}
                expected_outcomes = {n: "success" for n in sections}
                try:
                    coherence = compute_coherence(actual_outcomes, expected_outcomes)
                    workflow_coherence_score.observe(coherence)
                except Exception:  # noqa: BLE001
                    pass

            visible = _build_body(sections, run_url=run_url, readiness=readiness)
            hidden_blobs = "\n".join(
                _encode_section(name, info["status"], info["summary"], info["details"])
                for name, info in sections.items()
            )
            full_body = visible + "\n\n<!-- SECTIONS_DATA -->\n" + hidden_blobs

            # ── write ──────────────────────────────────────────────────────
            if existing:
                # Run dedup even on the update path: another concurrent
                # workflow may have created an extra copy in the time between
                # our fetch and this update.  Merge any extra sections first,
                # preferring the section from the most-recently-updated comment
                # so we never discard newer workflow status.
                all_comments = _list_comments(pr_number, token)
                dupes = [
                    c for c in all_comments
                    if _MARKER in c.get("body", "") and c["id"] != existing["id"]
                ]
                for dup in sorted(dupes, key=lambda c: c.get("updated_at") or c.get("created_at") or ""):
                    dup_ts = dup.get("updated_at") or dup.get("created_at") or ""
                    canonical_ts = existing.get("updated_at") or existing.get("created_at") or ""
                    extra_sections = _decode_sections(dup["body"])
                    for k, v in extra_sections.items():
                        # Prefer whichever comment is newer for this workflow key.
                        if k not in sections or dup_ts > canonical_ts:
                            sections[k] = v
                if dupes:
                    # Rebuild body with merged sections before updating.
                    visible = _build_body(sections, run_url=run_url, readiness=readiness)
                    hidden_blobs = "\n".join(
                        _encode_section(name, info["status"], info["summary"], info["details"])
                        for name, info in sections.items()
                    )
                    full_body = visible + "\n\n<!-- SECTIONS_DATA -->\n" + hidden_blobs
                _update_comment(existing["id"], full_body, token)
                print(f"✅ Updated PR #{pr_number} dashboard comment (id {existing['id']})")
                for dup in dupes:
                    try:
                        _api_request(
                            "DELETE",
                            f"/repos/{_repo()}/issues/comments/{dup['id']}",
                            token=token,
                        )
                        print(
                            f"🗑  Removed duplicate dashboard comment {dup['id']} "
                            f"(kept {existing['id']})"
                        )
                    except Exception as exc:  # noqa: BLE001
                        print(f"⚠️  Could not delete duplicate {dup['id']}: {exc}")
            else:
                result = _create_comment(pr_number, full_body, token)
                created_id = result["id"]
                print(f"✅ Created PR #{pr_number} dashboard comment (id {created_id})")

                # ── dedup guard: merge sections from any concurrent duplicate
                # then delete the extras so no status rows are lost ──────────
                all_comments = _list_comments(pr_number, token)
                dupes = [
                    c for c in all_comments
                    if _MARKER in c.get("body", "") and c["id"] != created_id
                ]
                if dupes:
                    # Prefer sections from more-recently-updated duplicates so
                    # that newer workflow statuses are never discarded.
                    canonical_ts = ""  # newly created — all dupes are at least as recent
                    for dup in sorted(dupes, key=lambda c: c.get("updated_at") or c.get("created_at") or ""):
                        dup_ts = dup.get("updated_at") or dup.get("created_at") or ""
                        extra_sections = _decode_sections(dup["body"])
                        for k, v in extra_sections.items():
                            if k not in sections or dup_ts > canonical_ts:
                                sections[k] = v
                    # Rebuild and update the canonical comment with merged data.
                    visible = _build_body(sections, run_url=run_url, readiness=readiness)
                    hidden_blobs = "\n".join(
                        _encode_section(name, info["status"], info["summary"], info["details"])
                        for name, info in sections.items()
                    )
                    merged_body = visible + "\n\n<!-- SECTIONS_DATA -->\n" + hidden_blobs
                    _update_comment(created_id, merged_body, token)
                    for dup in dupes:
                        try:
                            _api_request(
                                "DELETE",
                                f"/repos/{_repo()}/issues/comments/{dup['id']}",
                                token=token,
                            )
                            print(
                                f"🗑  Removed duplicate dashboard comment {dup['id']} "
                                f"(kept {created_id})"
                            )
                        except Exception as exc:  # noqa: BLE001
                            print(f"⚠️  Could not delete duplicate {dup['id']}: {exc}")

            return  # success — exit retry loop

        except urllib.error.HTTPError as exc:
            if attempt == max_retries:
                raise
            delay = backoff_s[min(attempt, len(backoff_s) - 1)]
            print(
                f"⚠️  Attempt {attempt + 1}/{max_retries} failed "
                f"(HTTP {exc.code}); retrying in {delay}s…",
                file=sys.stderr,
            )
            time.sleep(delay)


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
