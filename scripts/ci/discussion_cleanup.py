#!/usr/bin/env python3
"""
discussion_cleanup.py — CLI to scan and remove duplicate Discussion comments. (S297)

The `_find_discussion_comment` pagination bug in GitHubMCPPoster (fixed in S297)
caused every upsert to fall through to `addDiscussionComment`, producing one new
post per workflow run.  This tool identifies those duplicates and deletes the older
copies, leaving only the NEWEST comment per dedup-marker group.

MANIFEST WORKFLOW (recommended for large cleanups)
──────────────────────────────────────────────────
  1. Copilot Agent generates a manifest (audit file) listing every comment to delete.
  2. Manifest is committed to `.codex/cleanup/` for maintainer review.
  3. Either Copilot or the `discussion-cleanup.yml` workflow executes from the manifest.

  This separates "decide what to delete" from "actually delete" — giving a clear,
  reviewable record before any destructive operation runs.

SAFETY RULES (always enforced, cannot be overridden)
─────────────────────────────────────────────────────
1. Newest comment per marker is ALWAYS kept — only older copies are deleted.
2. Comments with replies are SKIPPED (never deleted) — listed as warnings.
3. Dry-run is the DEFAULT for `dedup` — pass --execute to make real changes.
4. A 300 ms delay is inserted between deletions to avoid secondary rate-limit.
5. Comments without any HTML marker are NEVER deleted by `dedup`.
6. Comments whose body contains "NEVER DELETE", "DO NOT DELETE", or
   "pr-discussion-registry:" are always skipped.

Commands
────────
  stats              Print total/unique/duplicate counts for a discussion.
  scan               Audit and print a duplicate report (no changes).
  generate-manifest  Scan and write a JSON manifest of all comments to delete.
  execute-manifest   Read a manifest file and delete every comment listed in it.
  dedup              Scan + optionally delete in one step (manifest not required).

Manifest-based workflow
───────────────────────
  # Step 1: Generate the manifest (Copilot runs this, commits the file)
  python scripts/ci/discussion_cleanup.py generate-manifest \\
      --discussions 3756 3673 \\
      --output .codex/cleanup/discussion_cleanup_manifest.json

  # Step 2a: Execute directly from manifest
  python scripts/ci/discussion_cleanup.py execute-manifest \\
      --manifest .codex/cleanup/discussion_cleanup_manifest.json

  # Step 2b: OR trigger the workflow and let it execute
  gh workflow run discussion-cleanup.yml \\
      -f manifest_path=.codex/cleanup/discussion_cleanup_manifest.json \\
      -f execute=true

Legacy (scan-and-delete in one step)
─────────────────────────────────────
  python scripts/ci/discussion_cleanup.py dedup --discussion 3756 3673 --execute

Environment
───────────
  GH_TOKEN, CODEX_MASTER_KEY, GITHUB_TOKEN, CODEX_BACKUP_KEY  (any one required)

Exit codes
──────────
  0   No duplicates found / all deletions succeeded.
  1   Duplicates found (scan/generate-manifest) or partial failure (execute).
  2   Fatal error (no token, API auth failure, manifest not found).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_OWNER = "Aries-Serpent"
_REPO  = "_codex_"

# Marker extraction: capture the FIRST <!-- ... --> HTML comment in a body
_MARKER_RE = re.compile(r"<!--\s*([\w][^>]{2,80}?)\s*-->")

# Safety: never delete a comment whose body contains any of these strings
_PROTECTED_BODY_FRAGMENTS = (
    "NEVER DELETE",
    "DO NOT DELETE",
    "pr-discussion-registry:",   # from find_or_create_pr_discussion
)


# ─────────────────────────────────────────────────────────────────────────────
# GitHub GraphQL helpers
# ─────────────────────────────────────────────────────────────────────────────

def _token() -> str:
    for var in ("GH_TOKEN", "CODEX_MASTER_KEY", "GITHUB_TOKEN", "CODEX_BACKUP_KEY"):
        val = os.environ.get(var, "")
        if val:
            return val
    return ""


def _gql(query: str, variables: dict[str, Any], token: str) -> dict[str, Any]:
    payload = json.dumps({"query": query, "variables": variables}).encode()
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
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as exc:
        snippet = exc.read()[:400].decode("utf-8", errors="replace")
        return {"errors": [{"message": f"HTTP {exc.code}: {snippet}"}]}
    except Exception as exc:
        return {"errors": [{"message": str(exc)}]}


# ─────────────────────────────────────────────────────────────────────────────
# Fetch all discussion comments (paginated, newest-first then reversed)
# ─────────────────────────────────────────────────────────────────────────────

def fetch_all_comments(discussion_number: int, token: str) -> list[dict[str, Any]]:
    """
    Fetch every comment in a discussion, returning them oldest-first.
    Uses forward pagination (first: 100, after: cursor) to guarantee completeness.
    Also fetches each comment's reply count so we can skip threaded replies safely.
    """
    query = """
    query FetchComments($owner: String!, $repo: String!, $n: Int!, $cursor: String) {
      repository(owner: $owner, name: $repo) {
        discussion(number: $n) {
          comments(first: 100, after: $cursor) {
            pageInfo { hasNextPage endCursor }
            nodes {
              id
              databaseId
              body
              createdAt
              author { login }
              replies { totalCount }
            }
          }
        }
      }
    }
    """
    all_comments: list[dict] = []
    cursor: str | None = None
    page = 0
    while True:
        page += 1
        result = _gql(
            query,
            {
                "owner": _OWNER,
                "repo": _REPO,
                "n": discussion_number,
                "cursor": cursor,
            },
            token,
        )
        errors = result.get("errors")
        if errors:
            print(f"  ⚠️  GraphQL error on page {page}: {errors[0]['message']}", file=sys.stderr)
            break
        page_data = (
            result.get("data", {})
            .get("repository", {})
            .get("discussion", {})
            .get("comments", {})
        )
        nodes = page_data.get("nodes", [])
        all_comments.extend(nodes)
        page_info = page_data.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")
        # Small delay to avoid secondary rate-limit on large discussions
        time.sleep(0.1)

    return all_comments


# ─────────────────────────────────────────────────────────────────────────────
# Duplicate detection
# ─────────────────────────────────────────────────────────────────────────────

def _extract_marker(body: str) -> str:
    """Return the first HTML comment marker from a comment body, or ''."""
    m = _MARKER_RE.search(body or "")
    return m.group(1).strip() if m else ""


def _is_protected(body: str) -> bool:
    """Return True if the comment body contains a protected fragment."""
    for frag in _PROTECTED_BODY_FRAGMENTS:
        if frag in (body or ""):
            return True
    return False


def find_duplicates(
    comments: list[dict],
    marker_prefix: str = "",
) -> dict[str, list[dict]]:
    """
    Group comments by their dedup marker.
    Returns only groups that have MORE than one comment (duplicates).
    Groups are sorted oldest-first within each key.
    If *marker_prefix* is set, only groups whose key starts with that prefix are included.
    """
    groups: dict[str, list[dict]] = defaultdict(list)
    for c in comments:
        marker = _extract_marker(c.get("body", ""))
        if not marker:
            continue  # no marker → not managed by upsert, skip
        if marker_prefix and not marker.startswith(marker_prefix):
            continue
        groups[marker].append(c)

    # Sort each group oldest-first and return only true duplicates
    return {
        k: sorted(v, key=lambda c: c.get("createdAt", ""))
        for k, v in groups.items()
        if len(v) > 1
    }


# ─────────────────────────────────────────────────────────────────────────────
# Deletion
# ─────────────────────────────────────────────────────────────────────────────

def delete_comment(node_id: str, token: str) -> bool:
    """Delete a single discussion comment by its GraphQL node ID. Returns True on success."""
    mutation = """
    mutation DeleteComment($id: ID!) {
      deleteDiscussionComment(input: { id: $id }) {
        comment { id }
      }
    }
    """
    result = _gql(mutation, {"id": node_id}, token)
    errors = result.get("errors")
    if errors:
        print(f"    ⚠️  Delete failed for {node_id}: {errors[0]['message']}", file=sys.stderr)
        return False
    return True


# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────

def cmd_stats(disc: int, token: str) -> int:
    print(f"\n📊 Fetching all comments from Discussion #{disc}…")
    comments = fetch_all_comments(disc, token)
    total = len(comments)

    groups: dict[str, list] = defaultdict(list)
    no_marker: list[dict] = []
    for c in comments:
        m = _extract_marker(c.get("body", ""))
        if m:
            groups[m].append(c)
        else:
            no_marker.append(c)

    dup_groups = {k: v for k, v in groups.items() if len(v) > 1}
    dup_count = sum(len(v) - 1 for v in dup_groups.values())
    unique_markers = len(groups)

    print(f"\n### Discussion #{disc} — Statistics")
    print(f"  Total comments    : {total}")
    print(f"  Unique markers    : {unique_markers}")
    print(f"  No-marker comments: {len(no_marker)}")
    print(f"  Duplicate groups  : {len(dup_groups)}")
    print(f"  Deletable dupes   : {dup_count}")
    print(f"  Would keep        : {total - dup_count}")
    return 1 if dup_count > 0 else 0


def cmd_scan(disc: int, marker_prefix: str, token: str) -> int:
    print(f"\n🔍 Scanning Discussion #{disc} for duplicates…")
    if marker_prefix:
        print(f"   Filtering to markers starting with: {marker_prefix!r}")
    comments = fetch_all_comments(disc, token)
    print(f"   Fetched {len(comments)} comments total.")

    dupes = find_duplicates(comments, marker_prefix)
    if not dupes:
        print("✅ No duplicates found.")
        return 0

    total_to_delete = sum(len(v) - 1 for v in dupes.values())
    print(f"\n⚠️  Found {len(dupes)} duplicate group(s) — {total_to_delete} comment(s) would be deleted:\n")
    print(f"  {'GROUP MARKER':<60}  {'TOTAL':>5}  {'DELETE':>6}  {'KEEP':>4}")
    print(f"  {'-'*60}  {'-----':>5}  {'------':>6}  {'----':>4}")
    for marker, group in sorted(dupes.items(), key=lambda x: -len(x[1])):
        keep = group[-1]  # newest
        keep_ts = keep.get("createdAt", "")[:10]
        has_replies = any((c.get("replies") or {}).get("totalCount", 0) > 0 for c in group[:-1])
        reply_warn = " ⚠️ has replies" if has_replies else ""
        print(f"  {marker[:60]:<60}  {len(group):>5}  {len(group)-1:>6}  {keep_ts}{reply_warn}")

    print(f"\n  Run with `dedup --execute` to delete the {total_to_delete} older copies.")
    return 1  # duplicates found → non-zero for CI gating


def cmd_dedup(
    discs: list[int],
    marker_prefix: str,
    execute: bool,
    token: str,
    delay_ms: int = 300,
) -> int:
    mode = "EXECUTE" if execute else "DRY RUN"
    overall_deleted = 0
    overall_skipped = 0
    overall_errors = 0

    for disc in discs:
        print(f"\n{'🗑️ ' if execute else '🔎 '}[{mode}] Discussion #{disc}")
        comments = fetch_all_comments(disc, token)
        print(f"   Fetched {len(comments)} comments.")

        dupes = find_duplicates(comments, marker_prefix)
        if not dupes:
            print("   ✅ No duplicates.")
            continue

        to_delete_count = sum(len(v) - 1 for v in dupes.values())
        print(f"   Found {len(dupes)} duplicate group(s), {to_delete_count} comment(s) to delete.\n")

        for marker, group in sorted(dupes.items(), key=lambda x: -len(x[1])):
            keep = group[-1]   # newest is always kept
            to_delete = group[:-1]  # all older copies

            keep_ts    = keep.get("createdAt", "")[:16]
            keep_id    = keep.get("databaseId", "?")
            keep_login = (keep.get("author") or {}).get("login", "?")
            print(f"  MARKER: {marker[:70]}")
            print(f"    Keep  [{keep_ts}] db#{keep_id} by @{keep_login}")

            for c in to_delete:
                c_ts    = c.get("createdAt", "")[:16]
                c_db    = c.get("databaseId", "?")
                c_id    = c.get("id", "")
                c_login = (c.get("author") or {}).get("login", "?")
                reply_count = (c.get("replies") or {}).get("totalCount", 0)
                protected   = _is_protected(c.get("body", ""))

                if reply_count > 0:
                    print(f"    Skip  [{c_ts}] db#{c_db}  ⚠️  has {reply_count} reply/replies — will not delete")
                    overall_skipped += 1
                    continue
                if protected:
                    print(f"    Skip  [{c_ts}] db#{c_db}  🔒  protected body fragment")
                    overall_skipped += 1
                    continue

                if execute:
                    ok = delete_comment(c_id, token)
                    if ok:
                        print(f"    Del ✅ [{c_ts}] db#{c_db} by @{c_login}")
                        overall_deleted += 1
                    else:
                        print(f"    Del ❌ [{c_ts}] db#{c_db} — failed")
                        overall_errors += 1
                    time.sleep(delay_ms / 1000)
                else:
                    print(f"    Del 🔎 [{c_ts}] db#{c_db} by @{c_login}  [dry run]")
                    overall_deleted += 1   # count as "would delete" in dry-run
            print()

    # Summary
    if execute:
        print(f"\n{'─'*60}")
        print(f"✅ Deleted  : {overall_deleted}")
        print(f"⏭️  Skipped  : {overall_skipped}  (have replies or protected)")
        print(f"❌ Errors   : {overall_errors}")
        if overall_errors:
            return 1
    else:
        print(f"\n{'─'*60}")
        print(f"🔎 Would delete : {overall_deleted}")
        print(f"⏭️  Would skip   : {overall_skipped}")
        print("\nRe-run with --execute to apply these deletions.")
        return 1 if overall_deleted > 0 else 0

    return 0


# ─────────────────────────────────────────────────────────────────────────────
# Manifest: generate and execute
# ─────────────────────────────────────────────────────────────────────────────

def _build_manifest(
    discs: list[int],
    marker_prefix: str,
    token: str,
) -> dict[str, Any]:
    """
    Scan one or more discussions and return a manifest dict describing every
    comment that should be deleted.  Does NOT delete anything.

    Manifest schema
    ───────────────
    {
      "schema_version": "1",
      "generated_at": "<ISO-8601>",
      "generated_by": "discussion_cleanup.py generate-manifest",
      "repo": "Aries-Serpent/_codex_",
      "summary": {
        "total_to_delete": N,
        "total_to_keep":   N,
        "total_skipped":   N,
        "discussions_scanned": [3756, 3673]
      },
      "discussions": {
        "3756": {
          "title": "...",
          "total_comments": N,
          "groups": [
            {
              "marker": "agent-checkin-open:auto-open-pr3854-20260403",
              "count": 28,
              "keep": {
                "node_id":     "DC_kwDO...",
                "database_id": 16438872,
                "created_at":  "2026-04-03T14:20Z",
                "author":      "mbaetiong",
                "url":         "https://github.com/..."
              },
              "delete": [
                {
                  "node_id":     "DC_kwDO...",
                  "database_id": 16435876,
                  "created_at":  "2026-04-03T09:12Z",
                  "author":      "mbaetiong",
                  "has_replies": false,
                  "skip_reason": null
                },
                ...
              ]
            }
          ]
        }
      }
    }
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest: dict[str, Any] = {
        "schema_version": "1",
        "generated_at": now,
        "generated_by": "discussion_cleanup.py generate-manifest",
        "repo": f"{_OWNER}/{_REPO}",
        "summary": {
            "total_to_delete": 0,
            "total_to_keep": 0,
            "total_skipped": 0,
            "discussions_scanned": discs,
        },
        "discussions": {},
    }

    for disc in discs:
        print(f"  Scanning Discussion #{disc}…", file=sys.stderr)
        comments = fetch_all_comments(disc, token)
        dupes = find_duplicates(comments, marker_prefix)

        disc_entry: dict[str, Any] = {
            "total_comments": len(comments),
            "groups": [],
        }

        for marker, group in sorted(dupes.items(), key=lambda x: -len(x[1])):
            keep = group[-1]
            to_delete = group[:-1]

            delete_entries: list[dict[str, Any]] = []
            for c in to_delete:
                reply_count = (c.get("replies") or {}).get("totalCount", 0)
                protected   = _is_protected(c.get("body", ""))
                skip_reason: str | None = None
                if reply_count > 0:
                    skip_reason = f"has {reply_count} reply/replies"
                elif protected:
                    skip_reason = "protected body fragment"

                delete_entries.append({
                    "node_id":     c.get("id", ""),
                    "database_id": c.get("databaseId"),
                    "created_at":  c.get("createdAt", ""),
                    "author":      (c.get("author") or {}).get("login", ""),
                    "has_replies": reply_count > 0,
                    "skip_reason": skip_reason,
                })
                if skip_reason:
                    manifest["summary"]["total_skipped"] += 1
                else:
                    manifest["summary"]["total_to_delete"] += 1

            manifest["summary"]["total_to_keep"] += 1

            disc_entry["groups"].append({
                "marker": marker,
                "count":  len(group),
                "keep": {
                    "node_id":     keep.get("id", ""),
                    "database_id": keep.get("databaseId"),
                    "created_at":  keep.get("createdAt", ""),
                    "author":      (keep.get("author") or {}).get("login", ""),
                    "url":         keep.get("url", ""),
                },
                "delete": delete_entries,
            })

        manifest["discussions"][str(disc)] = disc_entry

    return manifest


def cmd_generate_manifest(
    discs: list[int],
    marker_prefix: str,
    output_path: str,
    token: str,
) -> int:
    """
    Scan discussions and write a JSON manifest listing every comment to delete.
    Does NOT delete anything — safe to run at any time.

    The manifest file is intended to be:
      1. Committed to the repo at `.codex/cleanup/` for maintainer review.
      2. Passed to `execute-manifest` (or the workflow) when ready to execute.
    """
    print(f"\n📋 Generating deletion manifest for discussions: {discs}")
    if marker_prefix:
        print(f"   Filtering to markers starting with: {marker_prefix!r}")

    manifest = _build_manifest(discs, marker_prefix, token)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=2) + "\n")

    td = manifest["summary"]["total_to_delete"]
    tk = manifest["summary"]["total_to_keep"]
    ts = manifest["summary"]["total_skipped"]

    print(f"\n✅ Manifest written to: {output_path}")
    print(f"   To delete : {td}")
    print(f"   To keep   : {tk}")
    print(f"   Skipped   : {ts}  (have replies or protected)")
    print()
    print("Next steps:")
    print("  # Review the manifest:")
    print(f"  cat {output_path}")
    print()
    print("  # Execute directly:")
    print(f"  python scripts/ci/discussion_cleanup.py execute-manifest --manifest {output_path}")
    print()
    print("  # OR trigger the cleanup workflow:")
    print("  gh workflow run discussion-cleanup.yml \\")
    print(f"      -f manifest_path={output_path} \\")
    print("      -f execute=true")

    return 1 if td > 0 else 0


def cmd_execute_manifest(
    manifest_path: str,
    token: str,
    delay_ms: int = 300,
) -> int:
    """
    Read a previously-generated manifest file and delete every comment listed
    in it (skipping any with `skip_reason` set).

    Prints a per-comment result and a final summary.
    """
    path = Path(manifest_path)
    if not path.exists():
        print(f"::error::Manifest not found: {manifest_path}", file=sys.stderr)
        return 2

    manifest: dict[str, Any] = json.loads(path.read_text())
    schema = manifest.get("schema_version", "?")
    gen_at = manifest.get("generated_at", "?")
    td     = manifest["summary"]["total_to_delete"]
    ts     = manifest["summary"]["total_skipped"]

    print(f"\n🗑️  Executing manifest (schema v{schema}, generated {gen_at})")
    print(f"   Comments to delete : {td}")
    print(f"   Comments to skip   : {ts}")
    print()

    deleted = 0
    skipped = 0
    errors  = 0

    for disc_num, disc_data in manifest.get("discussions", {}).items():
        print(f"── Discussion #{disc_num} ({len(disc_data.get('groups', []))} groups) ──")
        for group in disc_data.get("groups", []):
            marker = group.get("marker", "?")
            keep   = group.get("keep", {})
            print(f"  MARKER: {marker[:70]}")
            print(f"    Keep  [{keep.get('created_at','')[:16]}] "
                  f"db#{keep.get('database_id','?')} by @{keep.get('author','?')}")

            for entry in group.get("delete", []):
                skip_reason = entry.get("skip_reason")
                c_ts  = entry.get("created_at", "")[:16]
                c_db  = entry.get("database_id", "?")
                c_id  = entry.get("node_id", "")
                c_by  = entry.get("author", "?")

                if skip_reason:
                    print(f"    Skip  [{c_ts}] db#{c_db}  ⚠️  {skip_reason}")
                    skipped += 1
                    continue

                if not c_id:
                    print(f"    Skip  [{c_ts}] db#{c_db}  ⚠️  no node_id in manifest")
                    skipped += 1
                    continue

                ok = delete_comment(c_id, token)
                if ok:
                    print(f"    Del ✅ [{c_ts}] db#{c_db} by @{c_by}")
                    deleted += 1
                else:
                    print(f"    Del ❌ [{c_ts}] db#{c_db} — API error")
                    errors += 1
                time.sleep(delay_ms / 1000)
        print()

    print(f"{'─'*60}")
    print(f"✅ Deleted  : {deleted}")
    print(f"⏭️  Skipped  : {skipped}")
    print(f"❌ Errors   : {errors}")

    # Stamp the manifest with execution results
    manifest["executed_at"]      = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest["execution_result"] = {
        "deleted": deleted,
        "skipped": skipped,
        "errors":  errors,
    }
    path.write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"\nManifest updated with execution results: {manifest_path}")

    return 1 if errors > 0 else 0


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        prog="discussion_cleanup",
        description="Scan and remove duplicate GitHub Discussion comments (S297).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Manifest workflow (recommended for large cleanups)
            ─────────────────────────────────────────────────
            # 1. Generate a manifest (safe — no deletions)
            python scripts/ci/discussion_cleanup.py generate-manifest \\
                --discussions 3756 3673 \\
                --output .codex/cleanup/discussion_cleanup_manifest.json

            # 2a. Execute directly from the manifest
            python scripts/ci/discussion_cleanup.py execute-manifest \\
                --manifest .codex/cleanup/discussion_cleanup_manifest.json

            # 2b. OR trigger the cleanup workflow
            gh workflow run discussion-cleanup.yml \\
                -f manifest_path=.codex/cleanup/discussion_cleanup_manifest.json \\
                -f execute=true
        """),
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    # ── stats ─────────────────────────────────────────────────────────────────
    p_stats = sub.add_parser("stats", help="Print statistics for a discussion")
    p_stats.add_argument("--discussion", type=int, required=True)

    # ── scan ──────────────────────────────────────────────────────────────────
    p_scan = sub.add_parser("scan", help="List duplicate groups (no changes)")
    p_scan.add_argument("--discussion", type=int, required=True)
    p_scan.add_argument("--marker-prefix", default="",
                        help="Only show groups whose marker starts with this prefix")

    # ── generate-manifest ─────────────────────────────────────────────────────
    p_gen = sub.add_parser(
        "generate-manifest",
        help="Scan and write a JSON manifest of all comments to delete (no deletions)",
    )
    p_gen.add_argument("--discussions", type=int, nargs="+", required=True,
                       help="One or more discussion numbers to scan")
    p_gen.add_argument("--marker-prefix", default="",
                       help="Only include groups whose marker starts with this prefix")
    p_gen.add_argument(
        "--output",
        default=".codex/cleanup/discussion_cleanup_manifest.json",
        help="Path to write the manifest JSON (default: .codex/cleanup/discussion_cleanup_manifest.json)",
    )

    # ── execute-manifest ──────────────────────────────────────────────────────
    p_exec = sub.add_parser(
        "execute-manifest",
        help="Read a manifest file and delete every listed comment",
    )
    p_exec.add_argument(
        "--manifest",
        default=".codex/cleanup/discussion_cleanup_manifest.json",
        help="Path to the manifest JSON (default: .codex/cleanup/discussion_cleanup_manifest.json)",
    )
    p_exec.add_argument("--delay-ms", type=int, default=300,
                        help="Milliseconds between deletions (default: 300)")

    # ── dedup ─────────────────────────────────────────────────────────────────
    p_dedup = sub.add_parser(
        "dedup",
        help="Scan + optionally delete in one step (dry-run by default)",
    )
    p_dedup.add_argument("--discussion", type=int, nargs="+", required=True,
                         help="One or more discussion numbers to clean up")
    p_dedup.add_argument("--marker-prefix", default="",
                         help="Only process groups whose marker starts with this prefix")
    p_dedup.add_argument("--execute", action="store_true",
                         help="Actually delete comments (default is dry-run)")
    p_dedup.add_argument("--delay-ms", type=int, default=300,
                         help="Milliseconds between deletions (default: 300)")

    args = parser.parse_args()

    token = _token()
    if not token:
        print(
            "::error::No GitHub token found. "
            "Set GH_TOKEN, CODEX_MASTER_KEY, GITHUB_TOKEN, or CODEX_BACKUP_KEY.",
            file=sys.stderr,
        )
        return 2

    if args.cmd == "stats":
        return cmd_stats(args.discussion, token)
    elif args.cmd == "scan":
        return cmd_scan(args.discussion, args.marker_prefix, token)
    elif args.cmd == "generate-manifest":
        return cmd_generate_manifest(args.discussions, args.marker_prefix, args.output, token)
    elif args.cmd == "execute-manifest":
        return cmd_execute_manifest(args.manifest, token, args.delay_ms)
    elif args.cmd == "dedup":
        return cmd_dedup(args.discussion, args.marker_prefix, args.execute, token, args.delay_ms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
