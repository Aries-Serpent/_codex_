#!/usr/bin/env python3
"""
Demo script showing how to use the Copilot Session Log Retriever.

This creates sample session data and demonstrates all features.
"""

import sqlite3
import sys
import tempfile
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from copilot_session_log_retriever import CopilotSessionRetriever


def create_demo_data():
    """Create demo database with sample session data."""
    # Create temporary database
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as temp_db:
        db_path = Path(temp_db.name)

    print(f"Creating demo database at: {db_path}")

    # Connect and create schema
    conn = sqlite3.connect(str(db_path))

    conn.execute("""
        CREATE TABLE logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            role TEXT NOT NULL,
            message TEXT,
            metadata TEXT
        )
    """)

    # Insert sample data
    sample_sessions = [
        # Session 1: Creating a new module
        ("session-001", "2026-02-05T08:00:00Z", "user", "Please create a new authentication module", "{}"),
        ("session-001", "2026-02-05T08:01:00Z", "assistant", 'I will create the authentication module. Created file: "src/auth/authenticator.py"', "{}"),
        ("session-001", "2026-02-05T08:02:00Z", "assistant", 'Created file: "src/auth/__init__.py" to make it a package', "{}"),
        ("session-001", "2026-02-05T08:03:00Z", "assistant", 'Updated file: "README.md" to document the new module', "{}"),
        ("session-001", "2026-02-05T08:04:00Z", "user", "Great! Can you add tests?", "{}"),
        ("session-001", "2026-02-05T08:05:00Z", "assistant", 'Created file: "tests/test_authenticator.py" with comprehensive tests', "{}"),

        # Session 2: Fixing bugs
        ("session-002", "2026-02-05T09:00:00Z", "user", "The authentication is failing", "{}"),
        ("session-002", "2026-02-05T09:01:00Z", "assistant", 'Let me check. Modified file: "src/auth/authenticator.py" to fix the validation logic', "{}"),
        ("session-002", "2026-02-05T09:02:00Z", "assistant", 'Updated file: "tests/test_authenticator.py" to add edge case tests', "{}"),

        # Session 3: Documentation update
        ("session-003", "2026-02-05T10:00:00Z", "user", "Update the documentation", "{}"),
        ("session-003", "2026-02-05T10:01:00Z", "assistant", 'Created file: "docs/authentication.md" with detailed guide', "{}"),
        ("session-003", "2026-02-05T10:02:00Z", "assistant", 'Modified file: "README.md" to link to new docs', "{}"),
        ("session-003", "2026-02-05T10:03:00Z", "assistant", 'Created file: "docs/api_reference.md" with API docs', "{}"),
    ]

    for entry in sample_sessions:
        conn.execute(
            "INSERT INTO logs (session_id, timestamp, role, message, metadata) VALUES (?, ?, ?, ?, ?)",
            entry
        )

    conn.commit()
    conn.close()

    print(f"✅ Created {len(sample_sessions)} log entries across 3 sessions")
    return db_path


def demo_list_sessions(retriever):
    """Demo: List available sessions."""
    print("\n" + "=" * 80)
    print("DEMO 1: List Available Sessions")
    print("=" * 80)

    sessions = retriever.list_sessions(limit=10)

    print(f"\nFound {len(sessions)} sessions:")
    for i, session in enumerate(sessions, 1):
        print(f"\n{i}. Session ID: {session['session_id']}")
        print(f"   Start: {session['start_time']}")
        print(f"   End: {session['end_time']}")
        print(f"   Messages: {session['message_count']}")


def demo_analyze_single_session(retriever, session_id):
    """Demo: Analyze a single session."""
    print("\n" + "=" * 80)
    print(f"DEMO 2: Analyze Single Session ({session_id})")
    print("=" * 80)

    summary = retriever.analyze_session(session_id)

    print("\nSession Summary:")
    print(f"  Session ID: {summary.session_id}")
    print(f"  Start Time: {summary.start_time}")
    print(f"  End Time: {summary.end_time}")
    print(f"  Messages: {summary.message_count}")
    print(f"  Expected Files: {len(summary.expected_files)}")
    print(f"  Verified: {summary.verified_files} ✅")
    print(f"  Missing: {summary.missing_files} ❌")

    if summary.expected_files:
        print("\nExpected Files:")
        for f in summary.expected_files:
            status = "✅" if f.verified else "❌"
            print(f"  {status} {f.path} ({f.operation})")
            if not f.verified:
                print(f"      Note: {f.notes}")


def demo_batch_processing(retriever):
    """Demo: Process multiple sessions in batches."""
    print("\n" + "=" * 80)
    print("DEMO 3: Batch Processing (3 sessions, batch size 2)")
    print("=" * 80)

    session_ids = retriever.get_last_n_sessions(n=3)
    print(f"\nRetrieved {len(session_ids)} session IDs: {session_ids}")

    summaries = retriever.process_sessions_in_batches(
        session_ids,
        batch_size=2
    )

    print(f"\nProcessed {len(summaries)} sessions:")
    for summary in summaries:
        print(f"\n  Session {summary.session_id}:")
        print(f"    Messages: {summary.message_count}")
        print(f"    Expected files: {len(summary.expected_files)}")
        print(f"    Verified: {summary.verified_files}")
        print(f"    Missing: {summary.missing_files}")


def demo_generate_report(retriever):
    """Demo: Generate comprehensive report."""
    print("\n" + "=" * 80)
    print("DEMO 4: Generate Comprehensive Report")
    print("=" * 80)

    session_ids = retriever.get_last_n_sessions(n=3)
    summaries = retriever.process_sessions_in_batches(session_ids, batch_size=3)

    # Generate report
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        report_path = f.name

    report = retriever.generate_report(summaries, output_path=report_path)

    print(f"\n✅ Report saved to: {report_path}")
    print("\nReport preview (first 50 lines):")
    print("-" * 80)

    lines = report.split('\n')
    for line in lines[:50]:
        print(line)

    if len(lines) > 50:
        print(f"\n... ({len(lines) - 50} more lines)")

    return report_path


def main():
    """Run all demos."""
    print("\n" + "=" * 80)
    print("🎯 Copilot Session Log Retriever - DEMO")
    print("=" * 80)

    # Create demo data
    db_path = create_demo_data()

    try:
        # Initialize retriever
        retriever = CopilotSessionRetriever(
            db_path=str(db_path),
            repo_root="."
        )

        # Run demos
        demo_list_sessions(retriever)
        demo_analyze_single_session(retriever, "session-001")
        demo_batch_processing(retriever)
        report_path = demo_generate_report(retriever)

        # Final summary
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE")
        print("=" * 80)
        print(f"\nDemo database: {db_path}")
        print(f"Demo report: {report_path}")
        print("\nTo clean up:")
        print(f"  rm {db_path}")
        print(f"  rm {report_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
