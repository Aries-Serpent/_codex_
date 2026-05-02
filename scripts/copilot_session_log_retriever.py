#!/usr/bin/env python3
"""
Copilot Session Log Retriever and Verification System

This module provides functionality to:
1. Retrieve the last N Copilot coding agent session logs
2. Process them in configurable batches
3. Verify all expected files from logs were correctly implemented
4. Report missing or incomplete implementations

Usage:
    python scripts/copilot_session_log_retriever.py --last 20 --batch-size 5
    python scripts/copilot_session_log_retriever.py --session-id <ID> --verify-only
    python scripts/copilot_session_log_retriever.py --list-sessions
"""

import argparse
import json
import logging
import os
import re
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import contextlib

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SessionLogEntry:
    """Represents a single session log entry."""
    session_id: str
    timestamp: str
    role: str
    message: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExpectedFile:
    """Represents a file that should exist based on session logs."""
    path: str
    operation: str  # 'create', 'edit', 'view', etc.
    session_id: str
    timestamp: str
    exists: bool = False
    verified: bool = False
    notes: str = ""


@dataclass
class SessionSummary:
    """Summary of a session's activities."""
    session_id: str
    start_time: str
    end_time: Optional[str]
    message_count: int
    expected_files: List[ExpectedFile]
    verified_files: int
    missing_files: int
    notes: List[str] = field(default_factory=list)


class CopilotSessionRetriever:
    """Retrieve and analyze Copilot session logs."""

    # Patterns to detect file operations in messages
    FILE_OPERATION_PATTERNS = [
        (r'create.*?[`\'"]([^`\'"]+)[`\'"]', 'create'),
        (r'edit.*?[`\'"]([^`\'"]+)[`\'"]', 'edit'),
        (r'Created file:?\s*[`\'"]?([^\s`\'"]+)', 'create'),
        (r'Modified file:?\s*[`\'"]?([^\s`\'"]+)', 'edit'),
        (r'Updated file:?\s*[`\'"]?([^\s`\'"]+)', 'edit'),
        (r'Writing to\s+[`\'"]?([^\s`\'"]+)', 'create'),
        (r'path=[`\'"]([^`\'"]+)[`\'"].*create', 'create'),
        (r'path=[`\'"]([^`\'"]+)[`\'"].*edit', 'edit'),
    ]

    def __init__(self, db_path: Optional[str] = None, repo_root: Optional[str] = None):
        """
        Initialize the session retriever.

        Args:
            db_path: Path to SQLite database with session logs
            repo_root: Root directory of repository for file verification
        """
        self.db_path = Path(db_path or os.getenv(
            "CODEX_LOG_DB_PATH",
            ".codex/session_logs.db"
        ))
        self.repo_root = Path(repo_root or os.getcwd())
        logger.info(f"Database path: {self.db_path}")
        logger.info(f"Repository root: {self.repo_root}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if not self.db_path.exists():
            logger.warning(f"Database not found at {self.db_path}")
            # Create empty database with schema
            self._create_schema()

        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _create_schema(self):
        """Create database schema if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.db_path))
        conn.execute("""
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                message TEXT,
                metadata TEXT
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_timestamp
            ON logs(session_id, timestamp)
        """)
        conn.commit()
        conn.close()
        logger.info(f"Created schema at {self.db_path}")

    def list_sessions(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        List available sessions with metadata.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of session metadata dictionaries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT
                session_id,
                MIN(timestamp) as start_time,
                MAX(timestamp) as end_time,
                COUNT(*) as message_count
            FROM logs
            GROUP BY session_id
            ORDER BY MAX(timestamp) DESC
            LIMIT ?
        """

        cursor.execute(query, (limit,))
        sessions = []

        for row in cursor.fetchall():
            sessions.append({
                'session_id': row['session_id'],
                'start_time': row['start_time'],
                'end_time': row['end_time'],
                'message_count': row['message_count']
            })

        conn.close()
        return sessions

    def get_last_n_sessions(self, n: int = 20) -> List[str]:
        """
        Get the last N session IDs.

        Args:
            n: Number of sessions to retrieve

        Returns:
            List of session IDs
        """
        sessions = self.list_sessions(limit=n)
        return [s['session_id'] for s in sessions]

    def get_session_logs(self, session_id: str) -> List[SessionLogEntry]:
        """
        Retrieve all log entries for a session.

        Args:
            session_id: Session identifier

        Returns:
            List of log entries
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = """
            SELECT session_id, timestamp, role, message, metadata
            FROM logs
            WHERE session_id = ?
            ORDER BY timestamp ASC
        """

        cursor.execute(query, (session_id,))
        entries = []

        for row in cursor.fetchall():
            metadata = {}
            if row['metadata']:
                with contextlib.suppress(json.JSONDecodeError):
                    metadata = json.loads(row['metadata'])

            entries.append(SessionLogEntry(
                session_id=row['session_id'],
                timestamp=row['timestamp'],
                role=row['role'],
                message=row['message'] or "",
                metadata=metadata
            ))

        conn.close()
        return entries

    def extract_expected_files(self, logs: List[SessionLogEntry]) -> List[ExpectedFile]:
        """
        Extract expected file operations from session logs.

        Args:
            logs: List of session log entries

        Returns:
            List of expected files
        """
        expected_files = []
        seen_files: Set[Tuple[str, str]] = set()  # (path, operation)

        for log in logs:
            if log.role not in ['assistant', 'tool']:
                continue

            # Try each pattern
            for pattern, operation in self.FILE_OPERATION_PATTERNS:
                matches = re.findall(pattern, log.message, re.IGNORECASE)
                for match in matches:
                    # Clean up the path
                    file_path = match.strip()

                    # Skip if already seen
                    if (file_path, operation) in seen_files:
                        continue

                    seen_files.add((file_path, operation))

                    expected_files.append(ExpectedFile(
                        path=file_path,
                        operation=operation,
                        session_id=log.session_id,
                        timestamp=log.timestamp,
                        exists=False,
                        verified=False
                    ))

        return expected_files

    def verify_files(self, expected_files: List[ExpectedFile]) -> List[ExpectedFile]:
        """
        Verify that expected files exist in the repository.

        Args:
            expected_files: List of expected files

        Returns:
            Updated list with verification status
        """
        for expected in expected_files:
            # Convert path to absolute
            if expected.path.startswith('/'):
                file_path = Path(expected.path)
            else:
                file_path = self.repo_root / expected.path

            # Check existence
            expected.exists = file_path.exists()

            if expected.exists:
                expected.verified = True
                expected.notes = f"File exists at {file_path}"
            else:
                expected.verified = False
                expected.notes = f"File NOT FOUND at {file_path}"
                logger.warning(f"Missing file: {expected.path}")

        return expected_files

    def analyze_session(self, session_id: str) -> SessionSummary:
        """
        Analyze a single session for file operations and verification.

        Args:
            session_id: Session identifier

        Returns:
            Session summary with verification results
        """
        logs = self.get_session_logs(session_id)

        if not logs:
            logger.warning(f"No logs found for session {session_id}")
            return SessionSummary(
                session_id=session_id,
                start_time="",
                end_time=None,
                message_count=0,
                expected_files=[],
                verified_files=0,
                missing_files=0,
                notes=["No logs found"]
            )

        start_time = logs[0].timestamp
        end_time = logs[-1].timestamp

        # Extract expected files
        expected_files = self.extract_expected_files(logs)

        # Verify files
        verified_files = self.verify_files(expected_files)

        # Count results
        verified_count = sum(1 for f in verified_files if f.verified)
        missing_count = len(verified_files) - verified_count

        return SessionSummary(
            session_id=session_id,
            start_time=start_time,
            end_time=end_time,
            message_count=len(logs),
            expected_files=verified_files,
            verified_files=verified_count,
            missing_files=missing_count
        )

    def process_sessions_in_batches(
        self,
        session_ids: List[str],
        batch_size: int = 5
    ) -> List[SessionSummary]:
        """
        Process multiple sessions in batches.

        Args:
            session_ids: List of session IDs to process
            batch_size: Number of sessions to process per batch

        Returns:
            List of session summaries
        """
        summaries = []
        total_sessions = len(session_ids)

        logger.info(f"Processing {total_sessions} sessions in batches of {batch_size}")

        for i in range(0, total_sessions, batch_size):
            batch = session_ids[i:i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total_sessions + batch_size - 1) // batch_size

            logger.info(f"Processing batch {batch_num}/{total_batches}: {len(batch)} sessions")

            for session_id in batch:
                logger.info(f"  Analyzing session: {session_id}")
                summary = self.analyze_session(session_id)
                summaries.append(summary)

                # Log summary
                logger.info(
                    f"    Messages: {summary.message_count}, "
                    f"Expected files: {len(summary.expected_files)}, "
                    f"Verified: {summary.verified_files}, "
                    f"Missing: {summary.missing_files}"
                )

        return summaries

    def generate_report(
        self,
        summaries: List[SessionSummary],
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate a detailed report of session analysis.

        Args:
            summaries: List of session summaries
            output_path: Optional path to save report

        Returns:
            Report as markdown string
        """
        report_lines = [
            "# Copilot Session Log Verification Report",
            f"\nGenerated: {datetime.utcnow().isoformat()}Z",
            f"\nTotal Sessions Analyzed: {len(summaries)}",
            "\n---\n"
        ]

        # Overall statistics
        total_expected = sum(len(s.expected_files) for s in summaries)
        total_verified = sum(s.verified_files for s in summaries)
        total_missing = sum(s.missing_files for s in summaries)

        report_lines.extend([
            "## Overall Statistics",
            f"- Total Expected Files: {total_expected}",
            f"- Verified Files: {total_verified}",
            f"- Missing Files: {total_missing}",
            f"- Verification Rate: {(total_verified / total_expected * 100) if total_expected > 0 else 0:.1f}%",
            "\n---\n"
        ])

        # Per-session details
        report_lines.append("## Session Details\n")

        for summary in summaries:
            report_lines.extend([
                f"### Session: `{summary.session_id}`",
                f"- Start Time: {summary.start_time}",
                f"- End Time: {summary.end_time or 'N/A'}",
                f"- Messages: {summary.message_count}",
                f"- Expected Files: {len(summary.expected_files)}",
                f"- Verified: {summary.verified_files} ✅",
                f"- Missing: {summary.missing_files} ❌",
                ""
            ])

            if summary.missing_files > 0:
                report_lines.append("#### Missing Files:")
                for expected in summary.expected_files:
                    if not expected.verified:
                        report_lines.append(
                            f"- `{expected.path}` ({expected.operation}) - {expected.notes}"
                        )
                report_lines.append("")

            if summary.notes:
                report_lines.append("#### Notes:")
                for note in summary.notes:
                    report_lines.append(f"- {note}")
                report_lines.append("")

        report = "\n".join(report_lines)

        # Save to file if requested
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(report)
            logger.info(f"Report saved to {output_path}")

        return report


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Retrieve and verify Copilot session logs"
    )

    parser.add_argument(
        "--db-path",
        help="Path to session logs database"
    )
    parser.add_argument(
        "--repo-root",
        help="Repository root directory"
    )
    parser.add_argument(
        "--last",
        type=int,
        default=20,
        help="Number of recent sessions to retrieve (default: 20)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of sessions to process per batch (default: 5)"
    )
    parser.add_argument(
        "--session-id",
        help="Analyze specific session ID"
    )
    parser.add_argument(
        "--list-sessions",
        action="store_true",
        help="List available sessions"
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only verify files, don't retrieve logs"
    )
    parser.add_argument(
        "--output",
        help="Output report file path"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    retriever = CopilotSessionRetriever(
        db_path=args.db_path,
        repo_root=args.repo_root
    )

    # List sessions
    if args.list_sessions:
        sessions = retriever.list_sessions(limit=args.last)
        print(f"\n{'=' * 80}")
        print(f"Available Sessions (Last {args.last})")
        print(f"{'=' * 80}\n")

        for i, session in enumerate(sessions, 1):
            print(f"{i}. Session ID: {session['session_id']}")
            print(f"   Start: {session['start_time']}")
            print(f"   End: {session['end_time']}")
            print(f"   Messages: {session['message_count']}")
            print()
        return

    # Analyze specific session
    if args.session_id:
        logger.info(f"Analyzing session: {args.session_id}")
        summary = retriever.analyze_session(args.session_id)
        report = retriever.generate_report(
            [summary],
            output_path=args.output
        )
        print(report)
        return

    # Process last N sessions in batches
    session_ids = retriever.get_last_n_sessions(args.last)

    if not session_ids:
        logger.warning("No sessions found in database")
        return

    logger.info(f"Retrieved {len(session_ids)} session IDs")

    summaries = retriever.process_sessions_in_batches(
        session_ids,
        batch_size=args.batch_size
    )

    # Generate and display report
    report = retriever.generate_report(
        summaries,
        output_path=args.output or ".codex/session_verification_report.md"
    )

    print("\n" + "=" * 80)
    print(report)
    print("=" * 80)


if __name__ == "__main__":
    main()
