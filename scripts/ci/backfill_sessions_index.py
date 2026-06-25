#!/usr/bin/env python3
"""
Backfill sessions_index.json from pda_iterations.jsonl

This script reads the PDA (Plan-Do-Act-Aftermath) iterations log and generates
a canonical session index with metadata from all 316 recorded sessions.

Usage:
    python scripts/ci/backfill_sessions_index.py

Output:
    .codex/sessions_index.json - Full session index
    Backfill report printed to stdout
"""

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class SessionIndexBackfiller:
    """Generates canonical session index from PDA iterations log."""

    def __init__(self, jsonl_path: str = ".codex/aftermath/pda_iterations.jsonl",
                 sessions_dir: str = ".codex/sessions",
                 output_path: str = ".codex/sessions_index.json"):
        """
        Initialize the backfiller.

        Args:
            jsonl_path: Path to pda_iterations.jsonl
            sessions_dir: Directory containing session markdown files
            output_path: Path to write sessions_index.json
        """
        self.jsonl_path = Path(jsonl_path)
        self.sessions_dir = Path(sessions_dir)
        self.output_path = Path(output_path)

        self.sessions: List[Dict[str, Any]] = []
        self.errors: List[Dict[str, Any]] = []
        self.stats = {
            "total_processed": 0,
            "total_valid": 0,
            "sessions_with_markdown": 0,
            "data_validation_errors": 0,
        }

    def normalize_timestamp(self, ts: str) -> str:
        """
        Normalize timestamp to RFC3339 format.

        Handles malformed timestamps like "2026-04-02T21-21Z" (hyphens instead of colons).

        Args:
            ts: Timestamp string (may be malformed)

        Returns:
            Normalized timestamp in format "%Y-%m-%dT%H:%M:%SZ"
        """
        if not ts or not isinstance(ts, str):
            return ""

        try:
            # Handle malformed timestamps with hyphens instead of colons
            # e.g., "2026-04-02T21-21Z" -> "2026-04-02T21:21Z"
            if "T" in ts and ts.count("-") > 2:
                # Likely has hyphens in time portion
                parts = ts.split("T")
                if len(parts) == 2:
                    time_part = parts[1].replace("-", ":")
                    ts = f"{parts[0]}T{time_part}"

            # Parse and re-format to ensure consistency
            if "Z" in ts:
                ts_clean = ts.replace("Z", "+00:00")
                dt = datetime.fromisoformat(ts_clean)
            else:
                dt = datetime.fromisoformat(ts)

            return dt.strftime("%Y-%m-%dT%H:%M:%SZ")
        except Exception as e:
            # Silently return empty string for missing/invalid timestamps
            return ""

    def extract_session_metadata(self, entry: Dict[str, Any],
                                 line_num: int) -> Optional[Dict[str, Any]]:
        """
        Extract session metadata from a PDA iteration entry.

        Args:
            entry: Parsed JSON entry from JSONL
            line_num: Line number in JSONL (for reference)

        Returns:
            Session metadata dict, or None if extraction fails
        """
        try:
            session_id = entry.get("session", f"S_unknown_{line_num}")
            timestamp = entry.get("timestamp", "")

            # Normalize timestamp
            normalized_ts = self.normalize_timestamp(timestamp)

            # Extract patterns
            patterns_fixed = entry.get("patterns_fixed", [])
            if not isinstance(patterns_fixed, list):
                patterns_fixed = []

            # Find corresponding markdown file
            markdown_file = None
            if session_id:
                md_path = self.sessions_dir / f"{session_id}_aftermath.md"
                if md_path.exists():
                    try:
                        markdown_file = str(md_path.relative_to(Path.cwd()))
                    except ValueError:
                        # Fallback to absolute path if not in subpath
                        markdown_file = str(md_path)
                    self.stats["sessions_with_markdown"] += 1

            # Extract duration if available (estimate from entry structure)
            # Default to 0 if not available
            duration_minutes = 0
            if "duration_minutes" in entry:
                duration_minutes = entry.get("duration_minutes", 0)

            # Determine status
            status = entry.get("status", "pending")

            # Extract CI checks
            ci_checks_green = entry.get("ci_checks_green", 0)
            ci_checks_red = entry.get("ci_checks_red", 0)

            # Build session record
            session_record = {
                "session_id": session_id,
                "pr_number": entry.get("pr_number"),
                "branch": entry.get("branch"),
                "timestamp": normalized_ts,
                "git_sha": entry.get("git_sha"),
                "status": status,
                "agent_name": entry.get("agent_name"),
                "duration_minutes": duration_minutes,
                "file_location": markdown_file,
                "jsonl_location": f".codex/aftermath/pda_iterations.jsonl:line_{line_num}",
                "patterns_fixed": patterns_fixed,
                "ci_checks_green": ci_checks_green,
                "ci_checks_red": ci_checks_red,
                "tags": self._extract_tags(entry),
                "summary": self._extract_summary(entry),
            }

            return session_record
        except Exception as e:
            self.errors.append({
                "type": "extraction_error",
                "session": entry.get("session", "unknown"),
                "line": line_num,
                "error": str(e),
            })
            self.stats["data_validation_errors"] += 1
            return None

    def _extract_tags(self, entry: Dict[str, Any]) -> List[str]:
        """
        Extract tags from entry for categorization.

        Args:
            entry: PDA iteration entry

        Returns:
            List of tags
        """
        tags = []

        # Tag by patterns fixed
        if entry.get("patterns_fixed"):
            if any("CI" in p or "WORKFLOW" in p or "GATE" in p
                   for p in entry["patterns_fixed"]):
                tags.append("ci")
            if any("MYPY" in p or "TYPE" in p for p in entry["patterns_fixed"]):
                tags.append("typing")
            if any("SECURITY" in p or "ZIP" in p or "CRYPT" in p
                   for p in entry["patterns_fixed"]):
                tags.append("security")
            if any("DOC" in p or "LINK" in p or "README" in p
                   for p in entry["patterns_fixed"]):
                tags.append("docs")

        # Tag by status
        if entry.get("status") == "complete":
            tags.append("complete")
        elif entry.get("status") == "pending":
            tags.append("pending")

        # Tag by agent
        if "healer" in entry.get("agent_name", "").lower():
            tags.append("healer")
        if "orchestrator" in entry.get("agent_name", "").lower():
            tags.append("orchestrator")

        return list(set(tags))

    def _extract_summary(self, entry: Dict[str, Any]) -> str:
        """
        Generate summary from entry metadata.

        Args:
            entry: PDA iteration entry

        Returns:
            Summary string
        """
        patterns = entry.get("patterns_fixed", [])
        if not patterns:
            return entry.get("lessons", "")[:100]

        pattern_str = ", ".join(patterns[:3])
        if len(patterns) > 3:
            pattern_str += f", +{len(patterns) - 3} more"

        return f"Fixed: {pattern_str}"

    def read_jsonl(self) -> bool:
        """
        Read and parse pda_iterations.jsonl.

        Returns:
            True if successful, False otherwise
        """
        if not self.jsonl_path.exists():
            print(f"❌ Error: {self.jsonl_path} not found")
            return False

        try:
            with open(self.jsonl_path, 'r') as f:
                for line_num, line in enumerate(f, start=1):
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        entry = json.loads(line)
                        self.stats["total_processed"] += 1

                        metadata = self.extract_session_metadata(entry, line_num)
                        if metadata:
                            self.sessions.append(metadata)
                            self.stats["total_valid"] += 1
                    except json.JSONDecodeError as e:
                        self.errors.append({
                            "type": "json_decode_error",
                            "line": line_num,
                            "error": str(e),
                        })
                        self.stats["data_validation_errors"] += 1

            return True
        except Exception as e:
            print(f"❌ Error reading JSONL: {e}")
            return False

    def generate_index(self) -> Dict[str, Any]:
        """
        Generate the canonical index structure.

        Returns:
            Index dictionary ready for serialization
        """
        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

        index = {
            "version": "1.0.0",
            "last_updated": now,
            "total_sessions": len(self.sessions),
            "sessions": self.sessions,
        }

        return index

    def write_index(self, index: Dict[str, Any]) -> bool:
        """
        Write index to JSON file.

        Args:
            index: Index dictionary

        Returns:
            True if successful, False otherwise
        """
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, 'w') as f:
                json.dump(index, f, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error writing index: {e}")
            return False

    def print_report(self) -> None:
        """Print backfill report with validation results."""
        print("\n" + "=" * 70)
        print("📊 SESSION INDEX BACKFILL REPORT")
        print("=" * 70)

        print("\n✅ PROCESSING STATS:")
        print(f"  Total entries processed: {self.stats['total_processed']}")
        print(f"  Valid sessions extracted: {self.stats['total_valid']}")
        print(f"  Sessions with markdown: {self.stats['sessions_with_markdown']}")
        print(f"  Data validation errors: {self.stats['data_validation_errors']}")

        print("\n📋 SESSION INDEX:")
        print(f"  Output file: {self.output_path}")
        print(f"  Total sessions in index: {len(self.sessions)}")

        if self.sessions:
            print("\n🔍 SAMPLE ENTRIES (First 3):")
            for i, session in enumerate(self.sessions[:3], 1):
                print(f"\n  Session {i}: {session['session_id']}")
                print(f"    - PR: #{session['pr_number']}")
                print(f"    - Branch: {session['branch']}")
                print(f"    - Timestamp: {session['timestamp']}")
                print(f"    - Status: {session['status']}")
                print(f"    - Patterns Fixed: {len(session['patterns_fixed'])}")
                print(f"    - CI Checks: {session['ci_checks_green']}✅ / "
                      f"{session['ci_checks_red']}❌")
                if session['summary']:
                    print(f"    - Summary: {session['summary'][:80]}...")

        if self.errors:
            critical_errors = [e for e in self.errors if e.get('type') != 'timestamp_error']
            if critical_errors:
                print(f"\n⚠️  CRITICAL ERRORS ({len(critical_errors)}):")
                for error in critical_errors[:5]:
                    print(f"  - {error.get('type', 'unknown')}: {error.get('error', 'N/A')}")
                if len(critical_errors) > 5:
                    print(f"  ... and {len(critical_errors) - 5} more errors")
            else:
                print("\n✅ No critical errors (some timestamp normalization warnings only)")

        print("\n✨ DATA INTEGRITY:")
        if self.stats['data_validation_errors'] == 0:
            print("  ✅ No validation errors (0 data loss)")
        else:
            print(f"  ⚠️  {self.stats['data_validation_errors']} validation errors")

        print("\n" + "=" * 70)

    def run(self) -> bool:
        """
        Execute the complete backfill process.

        Returns:
            True if successful, False otherwise
        """
        print("🚀 Starting session index backfill...\n")

        if not self.read_jsonl():
            return False

        index = self.generate_index()

        if not self.write_index(index):
            return False

        self.print_report()
        return True


def main() -> int:
    """Main entry point."""
    backfiller = SessionIndexBackfiller()
    success = backfiller.run()
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
