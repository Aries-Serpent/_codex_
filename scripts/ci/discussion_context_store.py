#!/usr/bin/env python3
"""
discussion_context_store.py — GitHub Discussions as a structured pre-session context store.
(P6-C, S297)

ARCHITECTURE (Push Model)
─────────────────────────
Rather than having the Copilot Coding Agent PULL context at session start
(multiple API calls), this script PUSHES a fully-formed, tokenized briefing
into a GitHub Discussion comment BEFORE the session begins.  The agent reads
ONE discussion entry and has complete situational awareness immediately.

Discussion target
─────────────────
  Primary target  : category "🤖 Pre-Session Context" (created on first use)
  Fallback target : Discussion #3756 — Q&A check-in thread (always available)
  Category fallback: "Show and tell" (DIC_kwDOPf23ns4C0Ue3) if create fails

Token format (embedded in HTML comment — machine-parseable, not rendered)
──────────────────────────────────────────────────────────────────────────
  <!-- psc-meta
  sha: <12-char SHA>
  pr: <PR number>
  failing_checks: <N>
  blocking_comments: <N>
  in_progress_checks: <N>
  eta_minutes: <N or null>
  patterns: <comma-separated RP-XXX IDs>
  session: <SN label>
  timestamp: <ISO-8601>
  discussion_number: <N>
  -->

Sections (human-readable + machine-parseable headers)
──────────────────────────────────────────────────────
  ## § A — Workflow Status
  ## § B — Unaddressed Blocking Comments
  ## § D — Action Queue
  ## § E — Recommended Skills

Usage
─────
  # Post context for current push/session (called by rescue-comment workflows)
  python scripts/ci/discussion_context_store.py post \\
      --pr 3854 --sha abc123def456 --repo Aries-Serpent/_codex_

  # Query latest context for a SHA (called by copilot-setup-steps.yml FIRST step)
  python scripts/ci/discussion_context_store.py query \\
      --pr 3854 --sha abc123def456 --repo Aries-Serpent/_codex_

  # List all context entries for a PR
  python scripts/ci/discussion_context_store.py list --pr 3854 --repo Aries-Serpent/_codex_

Exit codes
──────────
  0 — success
  1 — partial failure (context posted but with degraded data)
  2 — fatal error (API auth failure / network)

Environment
───────────
  GH_TOKEN, GITHUB_TOKEN, CODEX_MASTER_KEY, CODEX_BACKUP_KEY — any one required
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_OWNER = "Aries-Serpent"
_REPO = "_codex_"

# Discussion numbers for each target
_DISCUSSION_QA = 3756           # fallback — Q&A check-in thread (always exists)

# Category node IDs (resolved from the repo at time of implementation — S297)
_CAT_SHOW_AND_TELL = "DIC_kwDOPf23ns4C0Ue3"   # 🙌 Show and tell (fallback if PSC unavailable)

# Marker prefix used in all discussion comments from this script
_MARKER_PREFIX = "psc-meta"


# ─────────────────────────────────────────────────────────────────────────────
# GitHub API helpers (GraphQL + REST)
# ─────────────────────────────────────────────────────────────────────────────

def _token() -> str:
    for var in ("GH_TOKEN", "GITHUB_TOKEN", "CODEX_MASTER_KEY", "CODEX_BACKUP_KEY"):
        val = os.environ.get(var, "")
        if val:
            return val
    return ""


def _gql(query: str, variables: dict, token: str) -> dict:
    payload = json.dumps({"query": query, "variables": variables}).encode()
    # urllib imported at module level
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=payload,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        snippet = exc.read()[:300].decode("utf-8", errors="replace")
        return {"errors": [{"message": f"HTTP {exc.code}: {snippet}"}]}
    except Exception as exc:  # network error — caller handles None-like response
        return {"errors": [{"message": str(exc)}]}


def _rest(method: str, path: str, token: str, body: dict | None = None) -> tuple[int, Any]:
    # urllib imported at module level
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        f"https://api.github.com{path}",
        data=data,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        return exc.code, {}


# ─────────────────────────────────────────────────────────────────────────────
# Token encoding / decoding
# ─────────────────────────────────────────────────────────────────────────────

def encode_tokens(meta: dict[str, Any]) -> str:
    """
    Render metadata dict as an HTML comment block that is:
      - invisible to human readers (not rendered by GitHub Markdown)
      - machine-parseable with a single regex scan
      - idempotent (same inputs → same output)

    Example output:
      <!-- psc-meta
      sha: abc123def456
      pr: 3854
      failing_checks: 2
      ...
      -->
    """
    lines = [f"<!-- {_MARKER_PREFIX}"]
    for key, val in meta.items():
        lines.append(f"{key}: {val}")
    lines.append("-->")
    return "\n".join(lines)


def decode_tokens(body: str) -> dict[str, str] | None:
    """
    Parse a psc-meta HTML comment block from a discussion comment body.
    Returns None if no block found.
    """
    pattern = re.compile(
        r"<!--\s*" + re.escape(_MARKER_PREFIX) + r"\s*\n(.*?)\n-->",
        re.DOTALL,
    )
    match = pattern.search(body)
    if not match:
        return None
    tokens: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            tokens[key.strip()] = val.strip()
    return tokens


def marker_for(sha_short: str, pr: int) -> str:
    """Return the unique comment dedup marker for this (SHA, PR) pair."""
    return f"<!-- psc-sha:{sha_short}:pr:{pr} -->"


# ─────────────────────────────────────────────────────────────────────────────
# Context gathering (lightweight — §A + §B + §D only, no log fetching)
# ─────────────────────────────────────────────────────────────────────────────

def _gather_context(
    pr: int,
    sha: str,
    repo: str,
    token: str,
) -> dict[str, Any]:
    """
    Call pre_session_context functions to get §A + §B data without log fetch.
    Falls back to empty dicts on import failure (e.g., first-run before checkout).
    """
    try:
        _scripts_ci = Path(__file__).parent
        if str(_scripts_ci) not in sys.path:
            sys.path.insert(0, str(_scripts_ci))
        from pre_session_context import (  # noqa: PLC0415
            section_a_workflow_status,
            section_b_blocking_comments,
            section_d_action_queue,
            section_e_skills,
        )
        owner, repo_name = repo.split("/", 1)
        sec_a, failing, in_prog = section_a_workflow_status(owner, repo_name, sha, token)
        sec_b, blocking = section_b_blocking_comments(pr, repo, token)
        sec_d = section_d_action_queue(failing, blocking, in_prog)
        sec_e = section_e_skills(owner, repo_name)

        # Derive pattern IDs from failing check names (heuristic)
        patterns: list[str] = []
        for f in failing:
            name = f.get("name", "").lower()
            if "comment" in name or "review-gate" in name:
                patterns.append("RP-COMMENT-GATE")
            elif "rag" in name:
                patterns.append("RP-RAG-CHRONIC")
            elif "mypy" in name:
                patterns.append("RP-009")
            elif "actionlint" in name or "workflow" in name:
                patterns.append("RP-ACTIONLINT")
            elif "validation" in name or "validate" in name:
                patterns.append("RP-RUFF")
            elif "auto-fix" in name:
                patterns.append("RP-RUFF")
        patterns = sorted(set(patterns))

        eta_min = None
        for ip in in_prog:
            m = ip.get("eta_minutes")
            if m is not None and (eta_min is None or m < eta_min):
                eta_min = m

        return {
            "failing": failing,
            "blocking": blocking,
            "in_prog": in_prog,
            "patterns": patterns,
            "eta_min": eta_min,
            "sec_a": sec_a,
            "sec_b": sec_b,
            "sec_d": sec_d,
            "sec_e": sec_e,
        }
    except Exception as exc:
        print(f"[discussion_context_store] Context gather error: {exc}", file=sys.stderr)
        return {
            "failing": [], "blocking": [], "in_prog": [], "patterns": [],
            "eta_min": None,
            "sec_a": "_§ A unavailable_", "sec_b": "_§ B unavailable_",
            "sec_d": "_§ D unavailable_", "sec_e": "_§ E unavailable_",
        }


# ─────────────────────────────────────────────────────────────────────────────
# Discussion operations
# ─────────────────────────────────────────────────────────────────────────────

def _resolve_repo_id(owner: str, repo: str, token: str) -> str | None:
    res = _gql(
        "query($owner:String!,$repo:String!){repository(owner:$owner,name:$repo){id}}",
        {"owner": owner, "repo": repo},
        token,
    )
    return (res.get("data") or {}).get("repository", {}).get("id")


def _resolve_discussion_id(owner: str, repo: str, number: int, token: str) -> str | None:
    res = _gql(
        "query($owner:String!,$repo:String!,$n:Int!){"
        "repository(owner:$owner,name:$repo){discussion(number:$n){id}}}",
        {"owner": owner, "repo": repo, "n": number},
        token,
    )
    return (res.get("data") or {}).get("repository", {}).get("discussion", {}).get("id")


def _list_discussion_comments(discussion_id: str, token: str, last: int = 50) -> list[dict]:
    res = _gql(
        "query($id:ID!,$last:Int!){"
        "node(id:$id){...on Discussion{comments(last:$last){"
        "nodes{id databaseId body createdAt url}}}}}",
        {"id": discussion_id, "last": last},
        token,
    )
    node = (res.get("data") or {}).get("node") or {}
    return (node.get("comments") or {}).get("nodes") or []


def _add_discussion_comment(discussion_id: str, body: str, token: str) -> dict | None:
    res = _gql(
        "mutation($did:ID!,$body:String!){"
        "addDiscussionComment(input:{discussionId:$did,body:$body}){"
        "comment{id databaseId url}}}",
        {"did": discussion_id, "body": body},
        token,
    )
    return ((res.get("data") or {}).get("addDiscussionComment") or {}).get("comment")


def _update_discussion_comment(comment_id: str, body: str, token: str) -> bool:
    res = _gql(
        "mutation($cid:ID!,$body:String!){"
        "updateDiscussionComment(input:{commentId:$cid,body:$body}){"
        "comment{id}}}",
        {"cid": comment_id, "body": body},
        token,
    )
    return bool((res.get("data") or {}).get("updateDiscussionComment"))


def _get_or_create_psc_discussion(
    owner: str, repo: str, token: str
) -> tuple[int, str] | None:
    """
    Return (discussion_number, discussion_node_id) for the Pre-Session Context discussion.
    Tries to find an existing PSC discussion; if not found, creates one in Show-and-Tell.
    Returns None on failure.
    """
    # Search for an existing PSC discussion by title prefix
    res = _gql(
        "query($owner:String!,$repo:String!){"
        "repository(owner:$owner,name:$repo){"
        "discussions(first:20,orderBy:{field:UPDATED_AT,direction:DESC}){"
        "nodes{number id title category{name}}}}}",
        {"owner": owner, "repo": repo},
        token,
    )
    discussions = (
        (res.get("data") or {})
        .get("repository", {})
        .get("discussions", {})
        .get("nodes", [])
    )
    for d in discussions:
        if d.get("title", "").startswith("🤖 Pre-Session Context"):
            return d["number"], d["id"]

    # Not found — create it in Show-and-Tell (no admin perms needed for new discussion)
    repo_id = _resolve_repo_id(owner, repo, token)
    if not repo_id:
        return None

    create_res = _gql(
        "mutation($repoId:ID!,$catId:ID!,$title:String!,$body:String!){"
        "createDiscussion(input:{repositoryId:$repoId,categoryId:$catId,"
        "title:$title,body:$body}){discussion{number id}}}",
        {
            "repoId": repo_id,
            "catId": _CAT_SHOW_AND_TELL,
            "title": "🤖 Pre-Session Context — Copilot CI Briefing Store",
            "body": (
                "**Automatically maintained by `scripts/ci/discussion_context_store.py` (P6-C)**\n\n"
                "Each comment in this discussion is a pre-session context briefing for one commit SHA.\n"
                "Copilot reads the latest comment for its PR+SHA at session start.\n\n"
                "**Token format** (machine-parseable HTML comment in each entry):\n"
                "```\n<!-- psc-meta\nsha: <12-char>\npr: <N>\nfailing_checks: <N>\n"
                "blocking_comments: <N>\n...\n-->\n```\n\n"
                "**Never delete this discussion** — it is the pre-session knowledge store."
            ),
        },
        token,
    )
    disc = (
        (create_res.get("data") or {})
        .get("createDiscussion", {})
        .get("discussion")
    )
    if disc:
        print(
            f"[discussion_context_store] Created PSC discussion #{disc['number']}",
            file=sys.stderr,
        )
        return disc["number"], disc["id"]

    # Create failed — fall back to Q&A discussion #3756
    print(
        "[discussion_context_store] Could not create PSC discussion — "
        f"falling back to #{_DISCUSSION_QA}",
        file=sys.stderr,
    )
    disc_id = _resolve_discussion_id(owner, repo, _DISCUSSION_QA, token)
    return (_DISCUSSION_QA, disc_id) if disc_id else None


# ─────────────────────────────────────────────────────────────────────────────
# Build the structured discussion body
# ─────────────────────────────────────────────────────────────────────────────

def build_discussion_body(
    pr: int,
    sha: str,
    repo: str,
    context: dict[str, Any],
    discussion_number: int,
) -> str:
    """
    Build the full structured discussion comment body with:
      - Machine-parseable token block (HTML comment)
      - Dedup marker (for upsert detection)
      - Human-readable sections §A, §B, §D, §E
    """
    sha_short = sha[:12]
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")

    failing = context.get("failing", [])
    blocking = context.get("blocking", [])
    in_prog = context.get("in_prog", [])
    patterns = context.get("patterns", [])
    eta_min = context.get("eta_min")

    # ── Token block (machine-readable metadata) ─────────────────────────────
    meta = {
        "sha": sha_short,
        "pr": pr,
        "failing_checks": len(failing),
        "blocking_comments": len(blocking),
        "in_progress_checks": len(in_prog),
        "eta_minutes": eta_min if eta_min is not None else "null",
        "patterns": ",".join(patterns) if patterns else "none",
        "timestamp": ts,
        "discussion_number": discussion_number,
        "repo": repo,
    }
    token_block = encode_tokens(meta)

    # ── Dedup marker ─────────────────────────────────────────────────────────
    dedup = marker_for(sha_short, pr)

    # ── Status badge line ─────────────────────────────────────────────────────
    fail_badge = f"❌ {len(failing)} failing" if failing else "✅ all checks passing"
    block_badge = f"🚨 {len(blocking)} blocking" if blocking else "✅ no blocking comments"
    prog_badge = f"⏳ {len(in_prog)} in-progress" if in_prog else ""
    badges = " · ".join(filter(None, [fail_badge, block_badge, prog_badge]))

    # ── Header ────────────────────────────────────────────────────────────────
    header = "\n".join([
        token_block,
        dedup,
        "",
        "# 🧠 Pre-Session Context Briefing",
        "",
        f"> **PR:** #{pr}  ·  **SHA:** `{sha_short}`  ·  **{badges}**  ·  **{ts}**",
        ">",
        "> ⚠️ Read §D Action Queue first — it tells you exactly what to fix and in what order.",
        "> Do **not** start editing code until you have read §B (blocking comments must be replied to).",
        "",
        "---",
        "",
    ])

    # ── Sections (from pre_session_context functions) ─────────────────────────
    sections = "\n\n".join([
        context.get("sec_a", "_§ A unavailable_"),
        context.get("sec_b", "_§ B unavailable_"),
        context.get("sec_d", "_§ D unavailable_"),
        context.get("sec_e", "_§ E unavailable_"),
    ])

    # ── Footer ────────────────────────────────────────────────────────────────
    footer = "\n".join([
        "---",
        "",
        "### 📌 End-of-Session Checklist",
        "",
        "- [ ] Replied to all `<comment_new>` blocking comments with `Fixed at <SHA>`",
        "- [ ] `CHANGELOG.md` — `### Fixed (SN)` entry added under `## [Unreleased]`",
        "- [ ] `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` updated",
        "- [ ] `python scripts/ci/auto_fix_common_issues.py --check-only` → 0 issues",
        "- [ ] `python scripts/ci/mypy_baseline.py --require-baseline` → passes",
        "",
        f"_Posted by `scripts/ci/discussion_context_store.py` (P6-C, S297) · "
        f"[PR #{pr}](https://github.com/{repo}/pull/{pr})_",
    ])

    return "\n\n".join([header, sections, footer])


# ─────────────────────────────────────────────────────────────────────────────
# Public helper: compact inline context for embedding in rescue comments (RC-5)
# ─────────────────────────────────────────────────────────────────────────────

# Budget allocation: ≤600 chars for §D action queue + ~400 for header/status line.
# The total hard cap ensures GitHub comment body limits are never approached.
_MAX_INLINE_CONTEXT_LENGTH = 1000  # hard cap for full output block
_MAX_SECTION_D_LENGTH = 600       # budget for §D within the block


def build_comment_context(
    pr: int,
    sha: str,
    repo: str,
    token: str | None = None,
) -> str:
    """
    Return a compact §A + §B + §D inline context block suitable for embedding
    directly inside a rescue comment initial POST (RC-5, S299).

    Unlike `build_discussion_body()` this function:
      - Does NOT require a Discussion to exist.
      - Omits §E skills (verbose) and the machine-readable token block.
      - Returns a plain-text Markdown block of ≤ _MAX_INLINE_CONTEXT_LENGTH chars.
      - Falls back to an empty string on any error (caller must handle gracefully).

    Marker: ``<!-- rc-inline-context:{sha12}:{pr} -->`` (machine-parseable HTML comment;
    ``rc-inline`` = "rescue-comment inline context"). Not rendered; used by search/dedup.

    Usage in post_rescue_comment.py::

        from discussion_context_store import build_comment_context
        ctx = build_comment_context(pr_number, commit_sha, repo, gh_token)
        if ctx:
            first_body = ctx + "\\n\\n---\\n\\n" + rescue_body
    """
    if token is None:
        try:
            token = _token()
        except Exception as exc:
            print(
                f"[build_comment_context] GH_TOKEN unavailable — skipping inline context: {exc}",
                file=sys.stderr,
            )
            return ""
    sha_short = sha[:12]
    try:
        ctx = _gather_context(pr, sha, repo, token)
    except Exception:
        return ""

    failing = ctx.get("failing", [])
    blocking = ctx.get("blocking", [])
    in_prog = ctx.get("in_prog", [])

    # ── Brief status header ────────────────────────────────────────────────
    status_parts: list[str] = []
    if failing:
        status_parts.append(f"❌ {len(failing)} failing")
    if blocking:
        status_parts.append(f"🚨 {len(blocking)} blocking")
    if in_prog:
        status_parts.append(f"⏳ {len(in_prog)} in-progress")
    if not status_parts:
        return ""  # nothing noteworthy — omit the block to keep comment clean

    # rc-inline = rescue-comment inline context; sha12+pr uniquely identify this block.
    header = (
        f"<!-- rc-inline-context:{sha_short}:{pr} -->\n"
        f"**Session context** · `{sha_short}` · {' · '.join(status_parts)}"
    )

    # ── §D Action Queue (most actionable first) ───────────────────────────
    sec_d = ctx.get("sec_d", "")
    # Trim §D to its budget so the total stays within _MAX_INLINE_CONTEXT_LENGTH
    if len(sec_d) > _MAX_SECTION_D_LENGTH:
        sec_d = sec_d[: _MAX_SECTION_D_LENGTH - len("…")] + "…"

    lines = [header]
    if sec_d and sec_d.strip():
        lines.append("")
        lines.append(sec_d.strip())

    result = "\n".join(lines)
    # Hard cap — trim to _MAX_INLINE_CONTEXT_LENGTH characters
    if len(result) > _MAX_INLINE_CONTEXT_LENGTH:
        result = result[: _MAX_INLINE_CONTEXT_LENGTH - len("…")] + "…"
    return result


# ─────────────────────────────────────────────────────────────────────────────
# Subcommands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_post(args: argparse.Namespace, token: str) -> int:
    """
    Post (or upsert) a pre-session context briefing to the PSC discussion.
    Called by post_rescue_comment.py and copilot-agent-checkin.yml.
    """
    owner, repo_name = args.repo.split("/", 1)
    sha_short = args.sha[:12]

    # 1. Gather context (lightweight — no log fetch)
    print(f"[discussion_context_store] Gathering context for {sha_short} PR #{args.pr}…",
          file=sys.stderr)
    context = _gather_context(args.pr, args.sha, args.repo, token)

    # 2. Resolve/create PSC discussion
    result = _get_or_create_psc_discussion(owner, repo_name, token)
    if result is None:
        print("[discussion_context_store] ❌ Could not resolve/create PSC discussion",
              file=sys.stderr)
        return 2
    disc_number, disc_id = result

    # 3. Build body
    body = build_discussion_body(args.pr, args.sha, args.repo, context, disc_number)
    dedup = marker_for(sha_short, args.pr)

    # 4. Upsert — find existing comment with the dedup marker
    comments = _list_discussion_comments(disc_id, token, last=50)
    existing = next((c for c in comments if dedup in (c.get("body") or "")), None)

    if existing:
        ok = _update_discussion_comment(existing["id"], body, token)
        if ok:
            print(
                f"[discussion_context_store] ✅ Updated PSC entry "
                f"#{disc_number} (SHA {sha_short}) at {existing['url']}",
                file=sys.stderr,
            )
        else:
            print("[discussion_context_store] ⚠️ Update failed", file=sys.stderr)
            return 1
    else:
        comment = _add_discussion_comment(disc_id, body, token)
        if comment:
            print(
                f"[discussion_context_store] ✅ Posted PSC entry "
                f"#{disc_number} (SHA {sha_short}) at {comment.get('url', '?')}",
                file=sys.stderr,
            )
            # Output the discussion URL so callers can embed it in rescue comments
            print(comment.get("url", ""))
        else:
            print("[discussion_context_store] ❌ addDiscussionComment failed", file=sys.stderr)
            return 1

    # Surface token summary for the calling workflow / step log
    print(
        f"\n[psc-summary] SHA={sha_short} PR={args.pr} "
        f"failing={len(context['failing'])} "
        f"blocking={len(context['blocking'])} "
        f"in_progress={len(context['in_prog'])} "
        f"patterns={','.join(context['patterns']) or 'none'}",
        file=sys.stderr,
    )
    return 0


def cmd_query(args: argparse.Namespace, token: str) -> int:
    """
    Query the PSC discussion for the latest context entry for a given SHA+PR.
    Outputs the discussion body to stdout (for embedding in copilot-setup-steps summary).
    """
    owner, repo_name = args.repo.split("/", 1)
    sha_short = args.sha[:12]

    result = _get_or_create_psc_discussion(owner, repo_name, token)
    if result is None:
        print("_No PSC discussion available._")
        return 2
    _, disc_id = result

    comments = _list_discussion_comments(disc_id, token, last=50)
    dedup = marker_for(sha_short, args.pr)
    entry = next((c for c in reversed(comments) if dedup in (c.get("body") or "")), None)

    if not entry:
        # No exact SHA match — return the most recent entry as best-effort context
        entry = comments[-1] if comments else None
        if entry:
            print("[discussion_context_store] No exact SHA match — returning latest entry",
                  file=sys.stderr)

    if not entry:
        print(f"_No PSC context found for SHA `{sha_short}` PR #{args.pr}._")
        return 1

    tokens = decode_tokens(entry.get("body") or "")
    if tokens and args.tokens_only:
        # Machine-readable token dump for CI step output
        for k, v in tokens.items():
            print(f"{k}={v}")
    else:
        print(entry.get("body", ""))

    return 0


def cmd_list(args: argparse.Namespace, token: str) -> int:
    """List all PSC context entries for a PR (table format)."""
    owner, repo_name = args.repo.split("/", 1)

    result = _get_or_create_psc_discussion(owner, repo_name, token)
    if result is None:
        print("No PSC discussion found.")
        return 2
    disc_number, disc_id = result

    comments = _list_discussion_comments(disc_id, token, last=100)
    pr_comments = [
        c for c in comments
        if f":pr:{args.pr} -->" in (c.get("body") or "")
        or f"pr: {args.pr}" in (c.get("body") or "")
    ]

    if not pr_comments:
        print(f"No PSC entries found for PR #{args.pr} in discussion #{disc_number}.")
        return 0

    print(f"### PSC Entries for PR #{args.pr} in Discussion #{disc_number}\n")
    print("| Created | SHA | Failing | Blocking | URL |")
    print("|---------|-----|---------|----------|-----|")
    for c in pr_comments:
        tokens = decode_tokens(c.get("body") or "") or {}
        sha = tokens.get("sha", "?")
        failing = tokens.get("failing_checks", "?")
        blocking = tokens.get("blocking_comments", "?")
        ts = (c.get("createdAt") or "")[:16].replace("T", " ")
        url = c.get("url", "")
        print(f"| {ts} | `{sha}` | {failing} | {blocking} | [view]({url}) |")
    return 0


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="GitHub Discussions as a structured pre-session context store (P6-C)"
    )
    parser.add_argument("--repo", default=f"{_OWNER}/{_REPO}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    # post
    p_post = sub.add_parser("post", help="Post/upsert PSC briefing for a SHA+PR")
    p_post.add_argument("--pr",  required=True, type=int)
    p_post.add_argument("--sha", required=True)

    # query
    p_query = sub.add_parser("query", help="Query latest PSC briefing for a SHA+PR")
    p_query.add_argument("--pr",  required=True, type=int)
    p_query.add_argument("--sha", required=True)
    p_query.add_argument(
        "--tokens-only", action="store_true",
        help="Output only parsed token key=value pairs (for CI step output parsing)"
    )

    # list
    p_list = sub.add_parser("list", help="List all PSC entries for a PR")
    p_list.add_argument("--pr", required=True, type=int)

    args = parser.parse_args()

    token = _token()
    if not token:
        print(
            "::error::No GitHub token. Set GH_TOKEN, GITHUB_TOKEN, "
            "CODEX_MASTER_KEY, or CODEX_BACKUP_KEY.",
            file=sys.stderr,
        )
        return 2

    if args.cmd == "post":
        return cmd_post(args, token)
    elif args.cmd == "query":
        return cmd_query(args, token)
    elif args.cmd == "list":
        return cmd_list(args, token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
