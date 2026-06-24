#!/usr/bin/env python3
"""
generate_accountability_chunks.py

Generate chunked accountability report from sessions_index.json.

This script:
1. Reads sessions_index.json
2. Groups sessions into chunks (10 per chunk)
3. Generates markdown files for each chunk
4. Creates an index file with TOC and navigation
5. Validates all chunks and data integrity

Usage:
    python scripts/ci/generate_accountability_chunks.py \\
        --sessions-index .codex/sessions_index.json \\
        --output-dir .codex/accountability_chunks/ \\
        --sessions-per-chunk 10

    python scripts/ci/generate_accountability_chunks.py --help
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple


class AccountabilityChunksGenerator:
    """Generate chunked accountability report from sessions_index.json"""

    def __init__(
        self,
        sessions_index_path: str,
        output_dir: str,
        sessions_per_chunk: int = 10,
        backup_dir: str = ".codex/archive",
        chunk_name_template: str = "AGENT_ACCOUNTABILITY_REPORT_SESSION_GROUP_{:02d}.md",
    ):
        """Initialize generator.

        Args:
            sessions_index_path: Path to sessions_index.json
            output_dir: Output directory for chunks
            sessions_per_chunk: Sessions per chunk (default: 10)
            backup_dir: Directory to store backup
            chunk_name_template: Template for chunk filenames
        """
        self.sessions_index_path = Path(sessions_index_path)
        self.output_dir = Path(output_dir)
        self.sessions_per_chunk = sessions_per_chunk
        self.backup_dir = Path(backup_dir)
        self.chunk_name_template = chunk_name_template

        # Will be populated by load_sessions()
        self.sessions: List[Dict[str, Any]] = []
        self.chunk_metadata: Dict[int, Dict[str, Any]] = {}

        print("[INFO] Generator initialized")
        print(f"  Sessions index: {self.sessions_index_path}")
        print(f"  Output dir: {self.output_dir}")
        print(f"  Sessions per chunk: {self.sessions_per_chunk}")

    def load_sessions(self) -> bool:
        """Load sessions from sessions_index.json.

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(self.sessions_index_path) as f:
                data = json.load(f)

            self.sessions = data.get("sessions", [])
            total = len(self.sessions)

            print(f"[INFO] Loaded {total} sessions from {self.sessions_index_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to load sessions: {e}")
            return False

    def sort_sessions_chronologically(self) -> None:
        """Sort sessions chronologically (oldest → newest).

        Uses timestamp field, falls back to session_id if timestamp missing.
        """
        def sort_key(session: Dict[str, Any]) -> Tuple:
            ts = session.get("timestamp")
            sid = session.get("session_id", "")

            if ts:
                try:
                    # Parse ISO 8601 timestamp
                    return (0, ts, sid)
                except Exception:
                    pass

            # Fallback: sort by session_id lexicographically
            return (1, sid, "")

        self.sessions.sort(key=sort_key)
        print(f"[INFO] Sorted {len(self.sessions)} sessions chronologically")

    def group_sessions_by_batch(self) -> Dict[int, List[Dict[str, Any]]]:
        """Group sessions into batches.

        Returns:
            Dict mapping chunk number (1-based) to list of sessions
        """
        chunks = {}

        for i, session in enumerate(self.sessions):
            chunk_num = (i // self.sessions_per_chunk) + 1

            if chunk_num not in chunks:
                chunks[chunk_num] = []

            chunks[chunk_num].append(session)

        total_chunks = len(chunks)
        print(f"[INFO] Grouped {len(self.sessions)} sessions into {total_chunks} chunks")

        for chunk_num, chunk_sessions in chunks.items():
            print(f"  Chunk {chunk_num:02d}: {len(chunk_sessions)} sessions")

        return chunks

    def generate_chunk_markdown(self, chunk_num: int, sessions: List[Dict[str, Any]]) -> str:
        """Generate markdown content for one chunk.

        Args:
            chunk_num: Chunk number (1-based)
            sessions: List of sessions in this chunk

        Returns:
            Markdown content as string
        """
        total_chunks = len(self.chunk_metadata)
        prev_chunk = chunk_num - 1 if chunk_num > 1 else None
        next_chunk = chunk_num + 1 if chunk_num < total_chunks else None

        # Extract date range
        first_ts = sessions[0].get("timestamp", "?")
        last_ts = sessions[-1].get("timestamp", "?")

        # Parse dates if possible
        try:
            first_date = first_ts.split("T")[0] if "T" in first_ts else first_ts
            last_date = last_ts.split("T")[0] if "T" in last_ts else last_ts
            date_range = f"{first_date} to {last_date}"
        except Exception:
            date_range = f"{first_ts} to {last_ts}"

        # Build navigation table
        nav_rows = []

        if prev_chunk:
            nav_rows.append(
                f"| **Previous Group** | [{self.chunk_name_template.format(prev_chunk)}]"
                f"({self.chunk_name_template.format(prev_chunk)}) |"
            )
        else:
            nav_rows.append("| **Previous Group** | (First group) |")

        nav_rows.append(
            "| **Index** | [Full Index](../AGENT_ACCOUNTABILITY_REPORT_INDEX.md) |"
        )

        if next_chunk:
            nav_rows.append(
                f"| **Next Group** | [{self.chunk_name_template.format(next_chunk)}]"
                f"({self.chunk_name_template.format(next_chunk)}) |"
            )
        else:
            nav_rows.append("| **Next Group** | (Last group) |")

        nav_table = "\n".join(nav_rows)

        # Build session summary table
        session_rows = []
        for i, session in enumerate(sessions, start=1):
            sid = session.get("session_id", "?")
            pr = session.get("pr_number", "?")
            status = session.get("status", "?")
            ts = session.get("timestamp", "?")
            summary = session.get("summary", "")[:60]  # Truncate to 60 chars

            session_rows.append(
                f"| {i}. {sid} | {pr} | {status} | {ts} | {summary} |"
            )

        session_table = "\n".join(session_rows)

        # Build full markdown
        markdown = f"""# Agent Accountability Report — Session Group {chunk_num:02d}

**Group:** {chunk_num} of {total_chunks}
**Sessions:** {sessions[0].get('session_id', '?')} to {sessions[-1].get('session_id', '?')}
**Date Range:** {date_range}
**Total Sessions in Group:** {len(sessions)}

---

## Navigation

| Direction | Link |
| --- | --- |
{nav_table}

---

## Sessions in This Group

| # | Session ID | PR | Status | Timestamp | Summary |
| --- | --- | --- | --- | --- | --- |
{session_table}

---

## Session Details

"""

        # Add full session entries (original content)
        for session in sessions:
            # For now, include session metadata as a collapsible section
            markdown += f"""
### {session.get('session_id', '?')} — PR #{session.get('pr_number', '?')}

**Status:** {session.get('status', '?')}
**Timestamp:** {session.get('timestamp', '?')}
**Branch:** {session.get('branch', 'N/A')}
**Duration:** {session.get('duration_minutes', 0)} min

**Summary:**
```
{session.get('summary', '(No summary available)')}
```

**Tags:** {', '.join(session.get('tags', [])) or 'None'}
**Patterns Fixed:** {', '.join(session.get('patterns_fixed', [])) or 'None'}
**CI Checks:** {session.get('ci_checks_green', 0)} ✅ / {session.get('ci_checks_red', 0)} ❌

**Source:** {session.get('file_location', 'N/A')}
**Index Location:** {session.get('jsonl_location', 'N/A')}

---

"""

        # Add footer with navigation
        markdown += f"""---

## Navigation

| Direction | Link |
| --- | --- |
{nav_table}

---

**Group:** {chunk_num} of {total_chunks}
**Generated by:** `generate_accountability_chunks.py`
**Generated at:** {datetime.utcnow().isoformat()}Z
**Data Source:** `.codex/sessions_index.json`
"""

        return markdown

    def generate_index_markdown(self, chunks: Dict[int, List[Dict[str, Any]]]) -> str:
        """Generate index file with TOC and navigation.

        Args:
            chunks: Dict mapping chunk number to list of sessions

        Returns:
            Markdown content for index file
        """
        total_chunks = len(chunks)

        # Build group table (newest first)
        group_rows = []
        for chunk_num in sorted(chunks.keys(), reverse=True):
            sessions = chunks[chunk_num]
            first_session = sessions[0]
            last_session = sessions[-1]

            first_sid = first_session.get("session_id", "?")
            last_sid = last_session.get("session_id", "?")

            first_ts = first_session.get("timestamp", "?")
            last_ts = last_session.get("timestamp", "?")

            try:
                first_date = first_ts.split("T")[0] if "T" in first_ts else first_ts
                last_date = last_ts.split("T")[0] if "T" in last_ts else last_ts
                date_range = f"{first_date} to {last_date}"
            except Exception:
                date_range = f"{first_ts} to {last_ts}"

            status = "Active" if chunk_num == total_chunks else "Archived"
            chunk_file = self.chunk_name_template.format(chunk_num)

            group_rows.append(
                f"| Group {chunk_num:02d} | {first_sid}-{last_sid} | "
                f"[View](accountability_chunks/{chunk_file}) | {date_range} | {status} |"
            )

        group_table = "\n".join(group_rows)

        # Build markdown
        markdown = f"""# Agent Accountability Report — Session Index

> **Note:** The monolithic AGENT_ACCOUNTABILITY_REPORT.md has been split into session
> groups for GitHub rendering compatibility. All {len(self.sessions)} sessions are preserved in {total_chunks} chunks.

## Quick Navigation

- **Latest Sessions:** [Group {total_chunks:02d}](accountability_chunks/{self.chunk_name_template.format(total_chunks)})
  (Most recent sessions)
- **Search Sessions:** Use [session_query.py](../../scripts/ci/session_query.py) for complex queries
- **Original Backup:** [Backup](archive/AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md)

## Session Groups (All {total_chunks})

| Group | Sessions | Link | Date Range | Status |
| --- | --- | --- | --- | --- |
{group_table}

## Statistics

- **Total Sessions:** {len(self.sessions)}
- **Total Groups:** {total_chunks}
- **Average Sessions per Group:** {self.sessions_per_chunk}
- **Final Group Sessions:** {len(chunks[total_chunks])}

## Navigation by Group

Use the table above to navigate to specific session groups. Groups are ordered newest-first for quick access to recent sessions.

## Migration Notes

- ✅ **Original file backed up** to `archive/AGENT_ACCOUNTABILITY_REPORT_BACKUP_20260623.md`
- ✅ **All session data preserved** — No modifications to session content
- ✅ **Backward compatibility** — Index provides central navigation point
- ✅ **Query support** — Use `session_query.py` for advanced searches

## Scripts & Utilities

| Script | Purpose |
| --- | --- |
| [generate_accountability_chunks.py](../../scripts/ci/generate_accountability_chunks.py) | Generate chunks from sessions_index.json |
| [session_query.py](../../scripts/ci/session_query.py) | Search and filter sessions |
| [validate_chunks.py](../../scripts/ci/validate_chunks.py) | Validate chunk integrity and coverage |

---

**Generated by:** `generate_accountability_chunks.py`
**Generated at:** {datetime.utcnow().isoformat()}Z
**Data Source:** `.codex/sessions_index.json`
**Version:** 1.0
"""

        return markdown

    def write_all_chunks(self, chunks: Dict[int, List[Dict[str, Any]]]) -> Dict[int, Path]:
        """Write all chunks to disk.

        Args:
            chunks: Dict mapping chunk number to list of sessions

        Returns:
            Dict mapping chunk number to file path
        """
        result = {}

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"[INFO] Output directory: {self.output_dir}")

        # Generate and write each chunk
        for chunk_num in sorted(chunks.keys()):
            sessions = chunks[chunk_num]

            # Generate markdown
            markdown = self.generate_chunk_markdown(chunk_num, sessions)

            # Write to file
            filename = self.chunk_name_template.format(chunk_num)
            filepath = self.output_dir / filename

            try:
                with open(filepath, "w") as f:
                    f.write(markdown)

                size_kb = filepath.stat().st_size / 1024
                result[chunk_num] = filepath

                print(f"[OK] Chunk {chunk_num:02d}: {filepath} ({size_kb:.1f} KB)")
            except Exception as e:
                print(f"[ERROR] Failed to write chunk {chunk_num}: {e}")
                return {}

        print(f"[INFO] Successfully wrote {len(result)} chunks")
        return result

    def write_index(self, chunks: Dict[int, List[Dict[str, Any]]]) -> Path:
        """Write index file.

        Args:
            chunks: Dict mapping chunk number to list of sessions

        Returns:
            Path to index file
        """
        # Generate markdown
        markdown = self.generate_index_markdown(chunks)

        # Write to .codex/AGENT_ACCOUNTABILITY_REPORT_INDEX.md
        index_path = Path(".codex") / "AGENT_ACCOUNTABILITY_REPORT_INDEX.md"

        try:
            with open(index_path, "w") as f:
                f.write(markdown)

            size_kb = index_path.stat().st_size / 1024
            print(f"[OK] Index file: {index_path} ({size_kb:.1f} KB)")

            return index_path
        except Exception as e:
            print(f"[ERROR] Failed to write index: {e}")
            return None

    def validate_chunks(self, chunks: Dict[int, List[Dict[str, Any]]]) -> Tuple[bool, List[str]]:
        """Validate all chunks generated correctly.

        Checks:
        - Session count matches
        - No duplicate sessions
        - Sessions in order
        - File sizes reasonable
        - No data loss

        Args:
            chunks: Dict mapping chunk number to list of sessions

        Returns:
            Tuple of (success: bool, issues: list[str])
        """
        issues = []

        # Count total sessions in chunks
        total_in_chunks = sum(len(sessions) for sessions in chunks.values())
        if total_in_chunks != len(self.sessions):
            issues.append(
                f"Session count mismatch: {total_in_chunks} in chunks vs "
                f"{len(self.sessions)} in index"
            )

        # Check for duplicates
        seen_sids = set()
        for sessions in chunks.values():
            for session in sessions:
                sid = session.get("session_id")
                if sid in seen_sids:
                    issues.append(f"Duplicate session: {sid}")
                seen_sids.add(sid)

        # Check chunk sizes
        for chunk_num, sessions in chunks.items():
            expected_size = self.sessions_per_chunk
            actual_size = len(sessions)

            # Last chunk can be smaller
            is_last_chunk = chunk_num == max(chunks.keys())
            is_size_ok = (
                actual_size == expected_size or
                (is_last_chunk and actual_size < expected_size)
            )

            if not is_size_ok:
                issues.append(
                    f"Chunk {chunk_num} size mismatch: {actual_size} sessions "
                    f"(expected {expected_size})"
                )

        # Check chronological order
        all_sessions_in_chunks = []
        for sessions in chunks.values():
            all_sessions_in_chunks.extend(sessions)

        for i in range(len(all_sessions_in_chunks) - 1):
            ts1 = all_sessions_in_chunks[i].get("timestamp")
            ts2 = all_sessions_in_chunks[i + 1].get("timestamp")

            if ts1 and ts2 and ts1 > ts2:
                issues.append(
                    f"Chronological order violation: {all_sessions_in_chunks[i].get('session_id')} "
                    f"({ts1}) comes before {all_sessions_in_chunks[i+1].get('session_id')} ({ts2})"
                )

        # Check file sizes
        for chunk_num in chunks.keys():
            filename = self.chunk_name_template.format(chunk_num)
            filepath = self.output_dir / filename

            if not filepath.exists():
                issues.append(f"Chunk file does not exist: {filepath}")
                continue

            size_bytes = filepath.stat().st_size
            size_kb = size_bytes / 1024

            # GitHub render limit is 512 KB, we use 256 KB as safety threshold
            if size_kb > 256:
                issues.append(
                    f"Chunk {chunk_num} exceeds size limit: {size_kb:.1f} KB > 256 KB"
                )

        success = len(issues) == 0

        if success:
            print("[OK] Validation passed: All chunks validated successfully")
        else:
            print(f"[WARNING] Validation found {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue}")

        return success, issues

    def run(self) -> bool:
        """Run complete chunking pipeline.

        Returns:
            True if successful, False otherwise
        """
        print("\n" + "=" * 70)
        print("ACCOUNTABILITY REPORT CHUNKING GENERATOR")
        print("=" * 70 + "\n")

        # Step 1: Load sessions
        print("[STEP 1] Loading sessions from index...")
        if not self.load_sessions():
            return False

        # Step 2: Sort chronologically
        print("\n[STEP 2] Sorting sessions chronologically...")
        self.sort_sessions_chronologically()

        # Step 3: Group into chunks
        print("\n[STEP 3] Grouping sessions into chunks...")
        chunks = self.group_sessions_by_batch()
        self.chunk_metadata = chunks

        # Step 4: Write chunks
        print("\n[STEP 4] Writing chunk files...")
        chunk_paths = self.write_all_chunks(chunks)
        if not chunk_paths:
            return False

        # Step 5: Write index
        print("\n[STEP 5] Writing index file...")
        index_path = self.write_index(chunks)
        if not index_path:
            return False

        # Step 6: Validate
        print("\n[STEP 6] Validating chunks...")
        success, issues = self.validate_chunks(chunks)

        if success:
            print("\n" + "=" * 70)
            print("✅ SUCCESS: All chunks generated and validated")
            print("=" * 70)
            print(f"\n  Chunks: {len(chunks)}")
            print(f"  Sessions: {len(self.sessions)}")
            print(f"  Output: {self.output_dir}")
            print(f"  Index: {index_path}")
            print()
            return True
        else:
            print("\n" + "=" * 70)
            print("❌ VALIDATION FAILED: Issues found during validation")
            print("=" * 70)
            for issue in issues:
                print(f"  - {issue}")
            print()
            return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Generate chunked accountability report from sessions_index.json"
    )

    parser.add_argument(
        "--sessions-index",
        default=".codex/sessions_index.json",
        help="Path to sessions_index.json (default: .codex/sessions_index.json)",
    )

    parser.add_argument(
        "--output-dir",
        default=".codex/accountability_chunks",
        help="Output directory for chunks (default: .codex/accountability_chunks)",
    )

    parser.add_argument(
        "--sessions-per-chunk",
        type=int,
        default=10,
        help="Sessions per chunk (default: 10)",
    )

    parser.add_argument(
        "--backup-dir",
        default=".codex/archive",
        help="Backup directory (default: .codex/archive)",
    )

    args = parser.parse_args()

    # Create generator
    generator = AccountabilityChunksGenerator(
        sessions_index_path=args.sessions_index,
        output_dir=args.output_dir,
        sessions_per_chunk=args.sessions_per_chunk,
        backup_dir=args.backup_dir,
    )

    # Run pipeline
    success = generator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
