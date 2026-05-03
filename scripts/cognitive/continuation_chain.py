#!/usr/bin/env python3
"""
Continuation Chain Generator — Phase 8 (Tokenized Cognitive-Brain Prompts)

Builds a structured, tokenized ``@copilot continue`` prompt by reading live
cognitive-brain state from three authoritative sources:

1. ``CODEX_MANIFEST.json``                — ci_patterns knowledge graph
2. ``scripts/ci/pattern_recorder.py``     — SQLite pattern DB (high-recurrence,
                                            cross-PR correlation, trend)
3. ``.codex/docs/COGNITIVE_BRAIN_STATUS_*.md`` — latest phase completion state

The output is a Markdown "continuation chain" document with clearly labelled
token sections that a Copilot Coding Agent or Copilot Assistant can parse to
instantly reconstruct session context without reading the entire repo.

Usage
-----
    # Print chain to stdout:
    python scripts/cognitive/continuation_chain.py

    # Save to a file:
    python scripts/cognitive/continuation_chain.py --output /tmp/chain.md

    # Post directly to GitHub Discussions (requires CODEX_MASTER_KEY):
    python scripts/cognitive/continuation_chain.py \\
        --post-to-discussion \\
        --repo Aries-Serpent/_codex_ \\
        --discussion-number 3673

    # Control which DB and manifest to read:
    python scripts/cognitive/continuation_chain.py \\
        --db ~/.codex/cli_history.db \\
        --manifest CODEX_MANIFEST.json

Environment
-----------
    CODEX_DB_PATH           Path to SQLite pattern DB
    CODEX_MASTER_KEY        GitHub token for Discussion posting
    CODEX_BACKUP_KEY        Fallback GitHub token
    GITHUB_SHA              Current commit SHA (injected by GitHub Actions)
    GITHUB_RUN_ID           Current workflow run ID
    COPILOT_SESSION_ID      Copilot session identifier
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_DB = os.environ.get(
    "CODEX_DB_PATH",
    str(Path.home() / ".codex" / "cli_history.db"),
)
_DEFAULT_MANIFEST = _REPO_ROOT / "CODEX_MANIFEST.json"
_STATUS_DIR = _REPO_ROOT / ".codex" / "docs"

# Marker for upsert-based deduplication when posting to Discussions
_CHAIN_MARKER_PREFIX = "<!-- codex-continuation-chain:"

# ---------------------------------------------------------------------------
# Token section builders
# ---------------------------------------------------------------------------


def _token(name: str, content: str) -> str:
    """Wrap *content* in a labelled token section."""
    bar = "─" * 60
    return f"<!-- TOKEN:{name} -->\n{bar}\n{content.strip()}\n{bar}\n"


def _build_meta_token(session_id: str, sha: str, ts: str) -> str:
    return _token(
        "META",
        f"**Session:** `{session_id or 'unknown'}`  \n"
        f"**SHA:** `{sha or 'unknown'}`  \n"
        f"**Generated:** `{ts}`  \n"
        f"**Repo:** `Aries-Serpent/_codex_`  \n"
        f"**PR:** `#3741` (0D_base_ → main)",
    )


def _build_phase_token() -> str:
    """Read the latest COGNITIVE_BRAIN_STATUS_*.md and extract the phase table."""
    status_files = sorted(_STATUS_DIR.glob("COGNITIVE_BRAIN_STATUS_S*.md"), reverse=True)
    if not status_files:
        return _token("PHASE", "_No COGNITIVE_BRAIN_STATUS file found._")
    latest = status_files[0]
    text = latest.read_text(encoding="utf-8")
    # Extract lines up to first blank line after the first table
    lines: list[str] = []
    in_table = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("|"):
            in_table = True
            lines.append(line)
        elif in_table and not stripped:
            break
        elif not in_table and stripped:
            lines.append(line)
        if len(lines) > 40:
            break
    excerpt = "\n".join(lines) if lines else text[:800]
    return _token("PHASE", f"**Source:** `{latest.name}`\n\n{excerpt}")


def _build_manifest_token(manifest_path: Path) -> str:
    """Extract ci_patterns summary from CODEX_MANIFEST.json."""
    if not manifest_path.exists():
        return _token("MANIFEST", "_CODEX_MANIFEST.json not found._")
    try:
        manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return _token("MANIFEST", f"_Error reading manifest: {exc}_")

    ci = manifest.get("ci_patterns", {})
    if not ci:
        return _token("MANIFEST", "_No `ci_patterns` key in manifest._")

    pattern_count = len(ci.get("patterns", []))
    auto_fix_count = ci.get("auto_fixable_count", "?")
    strict_gate = ci.get("strict_gate", {}).get("step", "?")
    db_table = ci.get("db_schema", {}).get("table", "patterns")

    lines = [
        f"**Patterns:** {pattern_count}  ",
        f"**Auto-fixable:** {auto_fix_count}  ",
        f"**Strict gate:** {strict_gate}  ",
        f"**DB table:** `{db_table}`  ",
        "",
        "| # | Pattern | Auto-fix |",
        "|---|---------|----------|",
    ]
    for p in ci.get("patterns", [])[:10]:
        af = "✅" if p.get("auto_fixable") else "⚠️"
        lines.append(f"| {p.get('id','?')} | {p.get('name','?')} | {af} |")
    if pattern_count > 10:
        lines.append(f"| … | _{pattern_count - 10} more_ | |")

    return _token("MANIFEST", "\n".join(lines))


def _load_recorder() -> Optional[Any]:
    """Import pattern_recorder module dynamically."""
    path = _REPO_ROOT / "scripts" / "ci" / "pattern_recorder.py"
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location("pattern_recorder", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _build_patterns_token(db_path: str) -> str:
    """Query pattern DB for high-recurrence and cross-PR correlation."""
    recorder = _load_recorder()
    if recorder is None:
        return _token("PATTERNS", "_pattern_recorder.py not found._")

    db = Path(db_path)
    if not db.exists():
        return _token("PATTERNS", f"_Pattern DB not found at `{db_path}`. No runs recorded yet._")

    try:
        conn = recorder._open_db(db_path)
    except Exception as exc:  # noqa: BLE001
        return _token("PATTERNS", f"_Cannot open pattern DB: {exc}_")

    try:
        # High-recurrence (≥3 occurrences, ≥50% fix rate)
        high_rec: list[dict[str, Any]] = recorder.high_recurrence(conn, min_occurrences=3)
        # Cross-PR correlation (same pattern in ≥3 distinct SHAs)
        cross_pr: list[dict[str, Any]] = recorder.cross_pr_correlation(conn, min_prs=3)
        # 7-day trend totals
        trend: list[dict[str, Any]] = recorder.pattern_trend(conn, days=7)
        total_7d = sum(r.get("count", 0) for r in trend)
    except Exception as exc:  # noqa: BLE001
        return _token("PATTERNS", f"_Error querying pattern DB: {exc}_")
    finally:
        conn.close()

    lines: list[str] = [f"**7-day total occurrences:** {total_7d}  ", ""]

    if high_rec:
        lines += [
            "### 🔴 High-Recurrence Patterns (≥3 occ, ≥50% fix-rate)",
            "| Pattern | Total | Fix% |",
            "|---------|-------|------|",
        ]
        for r in high_rec[:8]:
            lines.append(
                f"| {r['pattern_name']} | {r['total']} | {r['fix_rate']*100:.0f}% |"
            )
        lines.append("")
    else:
        lines.append("_No high-recurrence patterns detected._\n")

    if cross_pr:
        lines += [
            "### 🔁 Cross-PR Recurring Patterns (≥3 distinct SHAs)",
            "| Pattern | PRs | Total |",
            "|---------|-----|-------|",
        ]
        for r in cross_pr[:8]:
            lines.append(f"| {r['pattern_name']} | {r['pr_count']} | {r['total']} |")
        lines.append("")
    else:
        lines.append("_No cross-PR recurring patterns (needs ≥3 distinct SHAs in DB)._\n")

    return _token("PATTERNS", "\n".join(lines))


def _build_next_steps_token(manifest_path: Path) -> str:
    """Build next-steps token from manifest phase_8 roadmap if present."""
    try:
        manifest: dict[str, Any] = json.loads(manifest_path.read_text(encoding="utf-8"))
        roadmap = manifest.get("phase_8_roadmap", [])
        if roadmap:
            lines = ["### Phase 8 Roadmap", ""]
            for item in roadmap:
                status = "✅" if item.get("done") else "- [ ]"
                lines.append(f"{status} **P{item.get('priority','?')}**: {item.get('title','?')}")
            return _token("NEXT_STEPS", "\n".join(lines))
    except Exception:  # noqa: BLE001
        import warnings
        warnings.warn("continuation_chain: failed to read phase roadmap from manifest", stacklevel=2)

    # Fallback: hard-coded known Phase 8 tasks
    return _token(
        "NEXT_STEPS",
        "\n".join([
            "### Phase 8 Roadmap (S192+)",
            "",
            "- [x] **P1** Cross-PR pattern correlation → `pattern_recorder.cross_pr_correlation()`",
            "- [ ] **P2** Snapshot pattern DB → workflow artifact (cross-run persistence)",
            "- [ ] **P3** `cross_pr_correlation()` results → `iterative-self-healing-ci.yml` escalation",
            "- [ ] **P4** Add `pattern_id` filter to `GET /api/patterns/recent`",
            "- [ ] **P5** `google-home-script-agent.md` + smart-home template guardian",
            "- [ ] **P6** GitHub Discussions hardened posting pipeline",
        ]),
    )


def _build_continuation_cta(session_id: str, sha: str) -> str:
    """Build the @copilot continue call-to-action block."""
    lines = [
        "## 🔄 Continuation Chain — Call to Action",
        "",
        "```",
        "@copilot continue https://github.com/Aries-Serpent/_codex_/tasks/560fd417-ae35-4d0f-a39d-498cafb02960",
        "",
        "Working on PR #3741 (head=0D_base_, base=main).",
        f"HEAD: {sha or 'see latest push'}",
        f"Session: {session_id or 'see CODEX_SESSION_ID'}",
        "",
        "Instructions:",
        "1. Load .codex/CODEBASE_AGENCY_POLICY.md §0",
        "2. Read TOKEN:META, TOKEN:PHASE, TOKEN:PATTERNS above for full context",
        "3. Check CI status: gh pr checks 3741",
        "4. Run code_review + codeql_checker",
        "5. Continue Phase 8 from TOKEN:NEXT_STEPS",
        "```",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main chain builder
# ---------------------------------------------------------------------------


def build_chain(
    db_path: str = _DEFAULT_DB,
    manifest_path: Path = _DEFAULT_MANIFEST,
    session_id: str = "",
    sha: str = "",
) -> str:
    """Build the full tokenized continuation chain Markdown document."""
    session_id = (
        session_id
        or os.environ.get("COPILOT_SESSION_ID")
        or os.environ.get("GITHUB_RUN_ID")
        or ""
    )
    sha = sha or os.environ.get("GITHUB_SHA") or os.environ.get("CODEX_GIT_SHA") or ""
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    marker = f"{_CHAIN_MARKER_PREFIX}{session_id or ts} -->"
    parts = [
        f"{marker}",
        "# 🧠 Codex Cognitive-Brain Continuation Chain",
        "",
        "> **Auto-generated** by `scripts/cognitive/continuation_chain.py`  ",
        "> Tokenized sections below allow Copilot Agents to restore full context in one read.",
        "",
        _build_meta_token(session_id, sha, ts),
        _build_phase_token(),
        _build_manifest_token(manifest_path),
        _build_patterns_token(db_path),
        _build_next_steps_token(manifest_path),
        "",
        _build_continuation_cta(session_id, sha),
    ]
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Build and optionally post a tokenized Cognitive-Brain continuation "
            "chain prompt to GitHub Discussions."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument(
        "--db",
        default=_DEFAULT_DB,
        help=f"Path to pattern SQLite DB (default: $CODEX_DB_PATH or {_DEFAULT_DB})",
    )
    p.add_argument(
        "--manifest",
        default=str(_DEFAULT_MANIFEST),
        help=f"Path to CODEX_MANIFEST.json (default: {_DEFAULT_MANIFEST})",
    )
    p.add_argument(
        "--session-id",
        default="",
        help="Session identifier (overrides COPILOT_SESSION_ID / GITHUB_RUN_ID env vars)",
    )
    p.add_argument(
        "--sha",
        default="",
        help="Git SHA (overrides GITHUB_SHA / CODEX_GIT_SHA env vars)",
    )
    p.add_argument(
        "--output",
        default="",
        help="Write chain to this file path instead of stdout",
    )
    p.add_argument(
        "--post-to-discussion",
        action="store_true",
        help=(
            "Post the chain to a GitHub Discussion via mcp_poster "
            "(requires CODEX_MASTER_KEY and --repo + --discussion-number)"
        ),
    )
    p.add_argument(
        "--repo",
        default="Aries-Serpent/_codex_",
        help="GitHub repo in owner/repo format (default: Aries-Serpent/_codex_)",
    )
    p.add_argument(
        "--discussion-number",
        type=int,
        default=3673,
        help="Target Discussion number for posting (default: 3673)",
    )
    p.add_argument(
        "--upsert",
        action="store_true",
        help=(
            "Upsert by session marker instead of always creating a new comment "
            "(prevents duplicates when running in CI)"
        ),
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    chain_md = build_chain(
        db_path=args.db,
        manifest_path=Path(args.manifest),
        session_id=args.session_id,
        sha=args.sha,
    )

    if args.output:
        Path(args.output).write_text(chain_md, encoding="utf-8")
        print(f"✅ Continuation chain written to {args.output}")
    else:
        print(chain_md)

    if args.post_to_discussion:
        # Import mcp_poster dynamically so this script stays standalone
        poster_path = _REPO_ROOT / "src" / "codex" / "github" / "mcp_poster.py"
        if not poster_path.exists():
            print("❌ mcp_poster.py not found — cannot post to Discussion.", file=sys.stderr)
            return 1
        spec = importlib.util.spec_from_file_location("mcp_poster", poster_path)
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        poster = mod.GitHubMCPPoster()

        try:
            if args.upsert:
                # Detect the marker line from the chain header
                marker_line = chain_md.splitlines()[0] if chain_md else ""
                result = poster.upsert_discussion_comment(
                    args.repo, args.discussion_number, chain_md, marker_line
                )
            else:
                result = poster.post_continuation_chain(
                    args.repo, args.discussion_number, chain_md
                )
            url = result.get("url", "") if isinstance(result, dict) else str(result)
            print(f"✅ Posted to discussion #{args.discussion_number}: {url}")
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Failed to post to Discussion: {exc}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
