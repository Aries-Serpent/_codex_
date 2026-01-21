#!/usr/bin/env python3
"""
Cognitive Brain CLI Tool
Command-line interface for querying and managing the cognitive brain database.

Usage:
    python brain_cli.py stats
    python brain_cli.py sessions --agent ci-testing-agent
    python brain_cli.py patterns --type exception
    python brain_cli.py lessons --category testing
    python brain_cli.py export --format json
"""
import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from github.agents.core import CognitiveBrain


def format_timestamp(ts_str: str) -> str:
    """Format ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(ts_str)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, TypeError):
        return ts_str or "N/A"


def cmd_stats(brain: CognitiveBrain, args):
    """Show cognitive brain statistics."""
    stats = brain.get_stats()
    
    print("=" * 60)
    print("🧠 Cognitive Brain Statistics")
    print("=" * 60)
    print()
    print(f"Database: {stats['database_path']}")
    print()
    print(f"📊 Totals:")
    print(f"  Sessions:  {stats['total_sessions']:>6}")
    print(f"  Patterns:  {stats['total_patterns']:>6}")
    print(f"  Lessons:   {stats['total_lessons']:>6}")
    print(f"  Decisions: {stats['total_decisions']:>6}")
    print()
    
    if stats.get("top_patterns"):
        print(f"🔥 Top Patterns:")
        for i, pattern in enumerate(stats["top_patterns"][:10], 1):
            print(f"  {i:2}. {pattern['pattern_name']:<30} {pattern['occurrences']:>4}x")
    
    print()


def cmd_sessions(brain: CognitiveBrain, args):
    """List agent sessions."""
    sessions = brain.get_session_history(
        agent_name=args.agent,
        limit=args.limit
    )
    
    if not sessions:
        print("No sessions found.")
        return
    
    print("=" * 80)
    print(f"📋 Sessions (showing {len(sessions)})")
    if args.agent:
        print(f"    Filtered by agent: {args.agent}")
    print("=" * 80)
    print()
    
    for session in sessions:
        status_emoji = "✅" if session["status"] == "success" else "❌"
        print(f"{status_emoji} {session['session_id']}")
        print(f"   Agent: {session['agent_name']} v{session['agent_version']}")
        print(f"   Task:  {session['task_type']}")
        print(f"   Start: {format_timestamp(session['start_time'])}")
        if session['end_time']:
            print(f"   End:   {format_timestamp(session['end_time'])}")
        print(f"   Status: {session['status']}")
        
        if session.get('metrics'):
            print(f"   Metrics: {json.dumps(session['metrics'], indent=11)[11:]}")
        
        print()


def cmd_patterns(brain: CognitiveBrain, args):
    """List detected patterns."""
    if args.type:
        # Filter would require additional query - showing all for now
        print(f"Filtering by type: {args.type}")
    
    # Get all patterns via stats
    stats = brain.get_stats()
    patterns = stats.get("top_patterns", [])
    
    if not patterns:
        print("No patterns found.")
        return
    
    print("=" * 70)
    print(f"🔍 Patterns (showing top {args.limit})")
    print("=" * 70)
    print()
    print(f"{'#':<4} {'Pattern Name':<35} {'Type':<15} {'Count':>8}")
    print("-" * 70)
    
    for i, pattern in enumerate(patterns[:args.limit], 1):
        print(f"{i:<4} {pattern['pattern_name']:<35} {'N/A':<15} {pattern['occurrences']:>8}")
    
    print()


def cmd_lessons(brain: CognitiveBrain, args):
    """List lessons learned."""
    lessons = brain.get_recent_lessons(
        category=args.category,
        limit=args.limit
    )
    
    if not lessons:
        print("No lessons found.")
        return
    
    print("=" * 80)
    print(f"📚 Lessons Learned (showing {len(lessons)})")
    if args.category:
        print(f"    Category: {args.category}")
    print("=" * 80)
    print()
    
    for i, lesson in enumerate(lessons, 1):
        confidence_bar = "█" * int(lesson['confidence'] * 10)
        print(f"{i}. {lesson['lesson_text']}")
        print(f"   Category: {lesson['category'] or 'N/A'}")
        print(f"   Confidence: {confidence_bar} {lesson['confidence']:.1%}")
        print(f"   Timestamp: {format_timestamp(lesson['timestamp'])}")
        print()


def cmd_export(brain: CognitiveBrain, args):
    """Export cognitive brain data."""
    stats = brain.get_stats()
    sessions = brain.get_session_history(limit=1000)
    lessons = brain.get_recent_lessons(limit=1000)
    
    export_data = {
        "export_date": datetime.now().isoformat(),
        "statistics": stats,
        "sessions": sessions,
        "lessons": lessons
    }
    
    if args.format == "json":
        output = json.dumps(export_data, indent=2)
        
        if args.output:
            Path(args.output).write_text(output)
            print(f"✅ Exported to {args.output}")
        else:
            print(output)
    else:
        print(f"❌ Unsupported format: {args.format}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cognitive Brain CLI - Query and manage the cognitive brain database",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--db",
        default=".codex/brain.db",
        help="Path to cognitive brain database (default: .codex/brain.db)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # stats command
    subparsers.add_parser("stats", help="Show database statistics")
    
    # sessions command
    sessions_parser = subparsers.add_parser("sessions", help="List agent sessions")
    sessions_parser.add_argument("--agent", help="Filter by agent name")
    sessions_parser.add_argument("--limit", type=int, default=10, help="Max results")
    
    # patterns command
    patterns_parser = subparsers.add_parser("patterns", help="List detected patterns")
    patterns_parser.add_argument("--type", help="Filter by pattern type")
    patterns_parser.add_argument("--limit", type=int, default=20, help="Max results")
    
    # lessons command
    lessons_parser = subparsers.add_parser("lessons", help="List lessons learned")
    lessons_parser.add_argument("--category", help="Filter by category")
    lessons_parser.add_argument("--limit", type=int, default=20, help="Max results")
    
    # export command
    export_parser = subparsers.add_parser("export", help="Export database")
    export_parser.add_argument("--format", default="json", choices=["json"], help="Export format")
    export_parser.add_argument("--output", help="Output file (default: stdout)")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Initialize brain
    db_path = Path(args.db)
    if not db_path.exists():
        print(f"❌ Database not found: {db_path}")
        print(f"   Run an agent first to create the database.")
        sys.exit(1)
    
    brain = CognitiveBrain(db_path)
    
    # Execute command
    commands = {
        "stats": cmd_stats,
        "sessions": cmd_sessions,
        "patterns": cmd_patterns,
        "lessons": cmd_lessons,
        "export": cmd_export
    }
    
    commands[args.command](brain, args)


if __name__ == "__main__":
    main()
