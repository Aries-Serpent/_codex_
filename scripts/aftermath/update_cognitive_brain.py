#! /usr/bin/env python3
"""
Update Cognitive Brain

Purpose:
    Updates cognitive_brain

Usage:
    python scripts/aftermath/update_cognitive_brain.py [options]

    Examples:
    $ python scripts/aftermath/update_cognitive_brain.py --help

Arguments:
    [To be documented]

Environment Variables:
    [To be documented]

Dependencies:
    [To be documented]

Exit Codes:
    0: Success
    1: Error

Author: Codex Team
Last Updated: 2026-01-16
"""



import argparse
import hashlib
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml


class CognitiveBrainUpdater:
    """Updates cognitive brain with aftermath insights."""

    def __init__(self, lessons_dir: Path, dashboard_path: Path):
        self.lessons_dir = lessons_dir
        self.dashboard_path = dashboard_path

    def load_recent_sessions(self, limit: int = 5) -> list[dict]:
        """Load most recent session files."""
        session_files = sorted(
            self.lessons_dir.glob('session_*.yaml'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]

        sessions = []
        for file in session_files:
            try:
                with open(file, encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    sessions.append(data)
            except (OSError, yaml.YAMLError) as e:
                print(f"Error loading {file}: {e}", file=sys.stderr)

        return sessions

    def aggregate_metrics(self, sessions: list[dict]) -> dict:
        """Aggregate metrics across sessions."""
        totals = {
            'sessions': len(sessions),
            'commits': 0,
            'files_changed': 0,
            'documentation_kb': 0,
            'tokens_used': 0,
            'duration_minutes': 0,
            'tests_added': 0,
            'lessons_learned': 0,
            'decisions_made': 0
        }

        for session in sessions:
            metrics = session.get('metrics', {})
            totals['commits'] += metrics.get('commits', 0)
            totals['files_changed'] += metrics.get('files_changed', 0)
            totals['documentation_kb'] += metrics.get('documentation_kb', 0)
            totals['tokens_used'] += metrics.get('tokens_used', 0)
            totals['duration_minutes'] += metrics.get('session_duration_minutes', 0)

            totals['lessons_learned'] += len(session.get('lessons', []))
            totals['decisions_made'] += len(session.get('decisions', []))

        return totals

    def extract_key_patterns(self, sessions: list[dict]) -> list[str]:
        """Extract recurring patterns from lessons learned."""
        patterns = {}

        for session in sessions:
            for lesson in session.get('lessons', []):
                root_cause = lesson.get('root_cause', '')
                if root_cause:
                    patterns[root_cause] = patterns.get(root_cause, 0) + 1

        # Return patterns seen multiple times, sorted by frequency
        recurring = [(cause, count) for cause, count in patterns.items() if count > 1]
        recurring.sort(key=lambda x: x[1], reverse=True)

        return [f"{cause} ({count}x)" for cause, count in recurring[:5]]

    def update_dashboard(self, sessions: list[dict]):
        """Update dashboard with AfterMath insights."""
        if not self.dashboard_path.exists():
            print(f"Dashboard not found: {self.dashboard_path}", file=sys.stderr)
            return

        content = self.dashboard_path.read_text(encoding='utf-8')

        # Aggregate data
        metrics = self.aggregate_metrics(sessions)
        patterns = self.extract_key_patterns(sessions)

        # Build insights section
        insights = [
            "\n## 🧠 AfterMath Insights (Last 5 Sessions)\n",
            f"**Last Updated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n\n",
            "### Session Metrics\n",
            f"- **Total Sessions**: {metrics['sessions']}\n",
            f"- **Commits**: {metrics['commits']}\n",
            f"- **Files Changed**: {metrics['files_changed']}\n",
            f"- **Documentation Added**: {metrics['documentation_kb']} KB\n",
            f"- **Tokens Used**: {metrics['tokens_used']:,} / 1,000,000\n",
            f"- **Total Duration**: {metrics['duration_minutes']} minutes\n",
            f"- **Lessons Learned**: {metrics['lessons_learned']}\n",
            f"- **Decisions Made**: {metrics['decisions_made']}\n\n"
        ]

        if patterns:
            insights.append("### Recurring Patterns\n")
            for pattern in patterns:
                insights.append(f"- {pattern}\n")
            insights.append("\n")

        insights.append("### Latest Session\n")
        if sessions:
            latest = sessions[0]
            insights.append(f"- **ID**: {latest.get('meta', {}).get('session_id', 'N/A')}\n")
            insights.append(f"- **Status**: {latest.get('status', 'N/A')}\n")
            insights.append(f"- **Context**: {latest.get('meta', {}).get('context', 'N/A')}\n")

        insights_text = ''.join(insights)

        # Find or create AfterMath section
        aftermath_marker = "## 🧠 AfterMath Insights"
        if aftermath_marker in content:
            # Replace existing section
            start = content.find(aftermath_marker)
            # Find next heading or end of file
            end = content.find("\n## ", start + len(aftermath_marker))
            if end == -1:
                end = len(content)

            content = content[:start] + insights_text + content[end:]
        else:
            # Append to end
            content += "\n" + insights_text

        # Write updated dashboard
        self.dashboard_path.write_text(content, encoding='utf-8')
        print(f"Updated dashboard: {self.dashboard_path}")


def main():
    parser = argparse.ArgumentParser(description='Update cognitive brain with AfterMath insights')
    parser.add_argument('--lessons', required=False, help='Lessons learned directory')
    parser.add_argument('--dashboard', required=False, help='Dashboard file path')
    parser.add_argument(
        '--mode',
        choices=['dashboard', 'living-doc-sync'],
        default='dashboard',
        help=(
            'dashboard: update AfterMath insights section (default). '
            'living-doc-sync: read latest session_end event from SQLite and '
            'auto-populate living docs (accountability, changelog, PR whats_next, PDA feed).'
        ),
    )
    parser.add_argument(
        '--db',
        default='.codex/session_logs.db',
        help='Path to session logs SQLite database (used by living-doc-sync mode)',
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Print what would be written without actually writing (living-doc-sync only)',
    )
    args = parser.parse_args()

    if args.mode == 'living-doc-sync':
        return living_doc_sync(
            db_path=Path(args.db),
            repo_root=Path('.'),
            dry_run=args.dry_run,
        )

    # --- dashboard mode (original behaviour) ---
    if not args.lessons or not args.dashboard:
        print(
            "Error: --lessons and --dashboard are required for dashboard mode",
            file=sys.stderr,
        )
        return 1

    lessons_dir = Path(args.lessons)
    dashboard_path = Path(args.dashboard)

    if not lessons_dir.exists():
        print(f"Error: Lessons directory not found: {lessons_dir}", file=sys.stderr)
        return 1

    updater = CognitiveBrainUpdater(lessons_dir, dashboard_path)
    sessions = updater.load_recent_sessions()

    if not sessions:
        print("No session data found", file=sys.stderr)
        return 1

    updater.update_dashboard(sessions)
    print(f"Cognitive brain updated with {len(sessions)} sessions")

    return 0


# ---------------------------------------------------------------------------
# Living-doc sync: reads latest session_end event from SQLite and writes
# structured delta blocks to each living-doc target.
# ---------------------------------------------------------------------------


def _db_query_latest_session_end(db_path: Path) -> Optional[dict]:
    """Return meta dict from the most recent session_end event, or None."""
    if not db_path.exists():
        print(
            f"living-doc-sync: database not found at {db_path}; no session events to sync.",
            file=sys.stderr,
        )
        return None
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.execute(
            """
            SELECT session_id, meta, ts
            FROM session_events
            WHERE message LIKE '%session_end%' OR meta LIKE '%session_end%'
            ORDER BY ts DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()
        con.close()
        if not row:
            return None
        meta_raw = row[1] or '{}'
        try:
            meta = json.loads(meta_raw)
        except (json.JSONDecodeError, TypeError):
            meta = {}
        meta.setdefault('session_id', row[0] or 'unknown')
        meta.setdefault('_ts', row[2])
        return meta
    except sqlite3.Error:
        return None


def _section_hash(text: str) -> str:
    """Return MD5 hex digest of a text block (idempotency check)."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def _upsert_section(
    doc_path: Path,
    section_marker: str,
    new_content: str,
    dry_run: bool,
) -> bool:
    """
    Insert or replace a named section in doc_path.

    The section is delimited by:
      <!-- living-doc-sync:<section_marker>:start -->
      ...content...
      <!-- living-doc-sync:<section_marker>:end -->

    Returns True if the file was (or would be) changed.
    """
    start_tag = f"<!-- living-doc-sync:{section_marker}:start -->"
    end_tag = f"<!-- living-doc-sync:{section_marker}:end -->"
    block = f"{start_tag}\n{new_content.rstrip()}\n{end_tag}"

    if not doc_path.exists():
        if dry_run:
            print(f"[dry-run] Would create section '{section_marker}' in {doc_path}")
        return False  # don't create new docs, only update existing

    existing = doc_path.read_text(encoding='utf-8')
    if start_tag in existing:
        # Replace existing block
        s = existing.find(start_tag)
        e = existing.find(end_tag)
        if e == -1:
            e = len(existing)
        else:
            e += len(end_tag)
        current_block = existing[s:e]
        if _section_hash(current_block) == _section_hash(block):
            return False  # idempotent: no change needed
        new_doc = existing[:s] + block + existing[e:]
    else:
        # Append at end
        new_doc = existing.rstrip() + '\n\n' + block + '\n'

    if dry_run:
        print(f"[dry-run] Would update section '{section_marker}' in {doc_path}")
        return True

    doc_path.write_text(new_doc, encoding='utf-8')
    print(f"Updated section '{section_marker}' in {doc_path}")
    return True


def living_doc_sync(db_path: Path, repo_root: Path, dry_run: bool = False) -> int:
    """
    Read the latest session_end event from SQLite and write deterministic
    delta blocks to each living-doc target.

    Living-doc targets:
      - docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md
      - CHANGELOG.md  (prepends to [Unreleased] block)
      - .codex/aftermath/pda_iterations.jsonl  (appends JSONL record)
    """
    meta = _db_query_latest_session_end(db_path)
    if not meta:
        print(
            "living-doc-sync: no session_end event found in DB; nothing to sync.",
            file=sys.stderr,
        )
        # Not a hard error — session may not have logged yet
        return 0

    session_id = meta.get('session_id', 'unknown')
    ts = meta.get('_ts', datetime.now(timezone.utc).isoformat())
    completed = meta.get('completed_tasks', [])
    pending = meta.get('pending_tasks', [])
    compliance = meta.get('pattern_compliance', {})
    living_docs_updated = meta.get('living_docs_updated', [])
    branch = meta.get('branch', 'unknown')
    pr_number = meta.get('pr_number')

    # ------------------------------------------------------------------
    # 1. AGENT_ACCOUNTABILITY_REPORT.md — append session summary block
    # ------------------------------------------------------------------
    accountability_path = repo_root / 'docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md'
    completed_lines = '\n'.join(f'- {t}' for t in completed) if completed else '- (none recorded)'
    pending_lines = '\n'.join(f'- {t}' for t in pending) if pending else '- (none)'
    compliance_lines = '\n'.join(
        f'- Pattern {k}: {v}' for k, v in compliance.items()
    ) if compliance else '- (none recorded)'
    docs_lines = '\n'.join(f'- {d}' for d in living_docs_updated) if living_docs_updated else '- (none)'

    accountability_block = f"""\
## SESSION SUMMARY — {ts} [{session_id}]

**Session:** {session_id} | **Branch:** `{branch}` | **PR:** {"#" + str(pr_number) if pr_number else "N/A"}

### Completed
{completed_lines}

### Pending
{pending_lines}

### Pattern Compliance
{compliance_lines}

### Living Docs Updated
{docs_lines}

---
"""

    _upsert_section(
        accountability_path,
        f'session-{session_id}',
        accountability_block,
        dry_run,
    )

    # ------------------------------------------------------------------
    # 2. CHANGELOG.md — prepend entry to [Unreleased] block
    # ------------------------------------------------------------------
    changelog_path = repo_root / 'CHANGELOG.md'
    if changelog_path.exists():
        changelog_entry = (
            f"\n### Added ({session_id} — `{branch}` — {ts})\n"
            + (
                '\n'.join(f'- {t}' for t in completed)
                if completed
                else '- (living-doc-sync auto-entry; no completed tasks recorded)'
            )
            + '\n'
        )
        existing_cl = changelog_path.read_text(encoding='utf-8')
        unreleased_marker = '## [Unreleased]'
        if unreleased_marker in existing_cl and session_id not in existing_cl:
            ins = existing_cl.find(unreleased_marker) + len(unreleased_marker)
            new_cl = existing_cl[:ins] + changelog_entry + existing_cl[ins:]
            if not dry_run:
                changelog_path.write_text(new_cl, encoding='utf-8')
                print(f"Updated CHANGELOG.md with session {session_id}")
            else:
                print(f"[dry-run] Would prepend session {session_id} to CHANGELOG.md")

    # ------------------------------------------------------------------
    # 3. .codex/aftermath/pda_iterations.jsonl — append JSONL record
    # ------------------------------------------------------------------
    pda_path = repo_root / '.codex/aftermath/pda_iterations.jsonl'
    if pda_path.parent.exists():
        pda_record = json.dumps({
            'session_id': session_id,
            'ts': ts,
            'branch': branch,
            'pr_number': pr_number,
            'completed_count': len(completed),
            'pending_count': len(pending),
            'pattern_compliance': compliance,
        })
        # Check idempotency: don't append the same session_id twice
        existing_pda = pda_path.read_text(encoding='utf-8') if pda_path.exists() else ''
        if session_id not in existing_pda:
            if not dry_run:
                with open(pda_path, 'a', encoding='utf-8') as f:
                    f.write(pda_record + '\n')
                print(f"Appended PDA record for {session_id}")
            else:
                print(f"[dry-run] Would append PDA record for {session_id}")

    return 0


if __name__ == '__main__':
    sys.exit(main())
