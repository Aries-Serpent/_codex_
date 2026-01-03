#!/usr/bin/env python3
"""
Cognitive Brain CLI - Command Line Interface for Brain Database.

Provides commands to inspect and manage the cognitive brain database.

Usage:
    python brain_cli.py stats
    python brain_cli.py sessions [--agent NAME] [--limit N]
    python brain_cli.py patterns [--type TYPE] [--limit N]
    python brain_cli.py lessons [--category CAT] [--limit N]
    python brain_cli.py export [--format json|csv] [--output FILE]
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from cognitive_brain import CognitiveBrain


def get_brain(db_path: Optional[str] = None) -> CognitiveBrain:
    """Get cognitive brain instance."""
    path = Path(db_path) if db_path else Path(".codex/brain.db")
    return CognitiveBrain(path)


def cmd_stats(args):
    """Show brain statistics."""
    brain = get_brain(args.db)
    
    with brain._get_connection() as conn:
        cursor = conn.cursor()
        
        # Count sessions
        cursor.execute("SELECT COUNT(*) FROM sessions")
        session_count = cursor.fetchone()[0]
        
        # Count patterns
        cursor.execute("SELECT COUNT(*) FROM patterns")
        pattern_count = cursor.fetchone()[0]
        
        # Count lessons
        cursor.execute("SELECT COUNT(*) FROM lessons")
        lesson_count = cursor.fetchone()[0]
        
        # Count decisions
        cursor.execute("SELECT COUNT(*) FROM decisions")
        decision_count = cursor.fetchone()[0]
        
        # Get unique agents
        cursor.execute("SELECT DISTINCT agent_name FROM sessions")
        agents = [row[0] for row in cursor.fetchall()]
        
        # Get date range
        cursor.execute("SELECT MIN(start_time), MAX(start_time) FROM sessions")
        date_range = cursor.fetchone()
    
    print("=" * 50)
    print("COGNITIVE BRAIN STATISTICS")
    print("=" * 50)
    print(f"Database: {brain.db_path}")
    print()
    print(f"Sessions:  {session_count:,}")
    print(f"Patterns:  {pattern_count:,}")
    print(f"Lessons:   {lesson_count:,}")
    print(f"Decisions: {decision_count:,}")
    print()
    print(f"Agents: {', '.join(agents) if agents else 'None'}")
    if date_range[0]:
        print(f"Date Range: {date_range[0]} to {date_range[1]}")
    print("=" * 50)


def cmd_sessions(args):
    """List sessions."""
    brain = get_brain(args.db)
    
    sessions = brain.get_session_history(
        agent_name=args.agent,
        limit=args.limit
    )
    
    if not sessions:
        print("No sessions found.")
        return
    
    print(f"{'SESSION ID':<20} {'AGENT':<25} {'STATUS':<10} {'TASK TYPE':<15} {'START TIME'}")
    print("-" * 90)
    
    for session in sessions:
        print(
            f"{session['session_id']:<20} "
            f"{session['agent_name']:<25} "
            f"{session.get('status', 'N/A'):<10} "
            f"{session.get('task_type', 'N/A'):<15} "
            f"{session['start_time']}"
        )


def cmd_patterns(args):
    """List patterns."""
    brain = get_brain(args.db)
    
    with brain._get_connection() as conn:
        cursor = conn.cursor()
        
        query = "SELECT pattern_name, pattern_type, occurrences, confidence_score, last_seen FROM patterns"
        params = []
        
        if args.type:
            query += " WHERE pattern_type = ?"
            params.append(args.type)
        
        query += " ORDER BY occurrences DESC LIMIT ?"
        params.append(args.limit)
        
        cursor.execute(query, params)
        patterns = cursor.fetchall()
    
    if not patterns:
        print("No patterns found.")
        return
    
    print(f"{'PATTERN NAME':<35} {'TYPE':<20} {'COUNT':<8} {'CONFIDENCE':<12} {'LAST SEEN'}")
    print("-" * 95)
    
    for pattern in patterns:
        print(
            f"{pattern[0]:<35} "
            f"{pattern[1]:<20} "
            f"{pattern[2]:<8} "
            f"{pattern[3]:<12.2f} "
            f"{pattern[4]}"
        )


def cmd_lessons(args):
    """List lessons."""
    brain = get_brain(args.db)
    
    lessons = brain.get_recent_lessons(
        category=args.category,
        limit=args.limit
    )
    
    if not lessons:
        print("No lessons found.")
        return
    
    print(f"{'LESSON':<60} {'CATEGORY':<15} {'CONFIDENCE'}")
    print("-" * 90)
    
    for lesson in lessons:
        # Truncate long lessons
        text = lesson['lesson_text']
        if len(text) > 57:
            text = text[:57] + "..."
        
        print(
            f"{text:<60} "
            f"{lesson.get('category', 'N/A'):<15} "
            f"{lesson.get('confidence', 0):.2f}"
        )


def cmd_export(args):
    """Export brain data."""
    brain = get_brain(args.db)
    
    with brain._get_connection() as conn:
        cursor = conn.cursor()
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "database": str(brain.db_path),
            "sessions": [],
            "patterns": [],
            "lessons": [],
            "decisions": []
        }
        
        # Export sessions
        cursor.execute("SELECT * FROM sessions")
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            data["sessions"].append(dict(zip(columns, row)))
        
        # Export patterns
        cursor.execute("SELECT * FROM patterns")
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            data["patterns"].append(dict(zip(columns, row)))
        
        # Export lessons
        cursor.execute("SELECT * FROM lessons")
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            data["lessons"].append(dict(zip(columns, row)))
        
        # Export decisions
        cursor.execute("SELECT * FROM decisions")
        columns = [desc[0] for desc in cursor.description]
        for row in cursor.fetchall():
            data["decisions"].append(dict(zip(columns, row)))
    
    if args.format == "json":
        output = json.dumps(data, indent=2, default=str)
    else:
        # CSV format - simplified
        lines = ["type,count"]
        lines.append(f"sessions,{len(data['sessions'])}")
        lines.append(f"patterns,{len(data['patterns'])}")
        lines.append(f"lessons,{len(data['lessons'])}")
        lines.append(f"decisions,{len(data['decisions'])}")
        output = "\n".join(lines)
    
    if args.output:
        Path(args.output).write_text(output)
        print(f"Exported to {args.output}")
    else:
        print(output)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Cognitive Brain CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    %(prog)s stats                           Show brain statistics
    %(prog)s sessions --agent ci-testing     List sessions for agent
    %(prog)s patterns --type exception       List exception patterns
    %(prog)s lessons --category testing      List testing lessons
    %(prog)s export --format json            Export all data as JSON
        """
    )
    
    parser.add_argument(
        "--db",
        default=".codex/brain.db",
        help="Path to brain database (default: .codex/brain.db)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show brain statistics")
    stats_parser.set_defaults(func=cmd_stats)
    
    # Sessions command
    sessions_parser = subparsers.add_parser("sessions", help="List sessions")
    sessions_parser.add_argument("--agent", help="Filter by agent name")
    sessions_parser.add_argument("--limit", type=int, default=20, help="Max results")
    sessions_parser.set_defaults(func=cmd_sessions)
    
    # Patterns command
    patterns_parser = subparsers.add_parser("patterns", help="List patterns")
    patterns_parser.add_argument("--type", help="Filter by pattern type")
    patterns_parser.add_argument("--limit", type=int, default=20, help="Max results")
    patterns_parser.set_defaults(func=cmd_patterns)
    
    # Lessons command
    lessons_parser = subparsers.add_parser("lessons", help="List lessons")
    lessons_parser.add_argument("--category", help="Filter by category")
    lessons_parser.add_argument("--limit", type=int, default=20, help="Max results")
    lessons_parser.set_defaults(func=cmd_lessons)
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export brain data")
    export_parser.add_argument("--format", choices=["json", "csv"], default="json")
    export_parser.add_argument("--output", "-o", help="Output file path")
    export_parser.set_defaults(func=cmd_export)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        args.func(args)
    except FileNotFoundError:
        print(f"Error: Database not found at {args.db}")
        print("Initialize by running an agent first, or specify --db path")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
