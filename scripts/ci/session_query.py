#!/usr/bin/env python3
"""
Session Query API - Query interface for session index.

Provides both programmatic and CLI interfaces for querying Copilot sessions.

Example usage:
    from scripts.ci.session_query import SessionQuery
    
    sq = SessionQuery()
    recent = sq.list_recent_sessions(days=7)
    agent_sessions = sq.get_sessions_by_agent('ci-auto-healer-agent')
    stats = sq.stats_summary()

CLI usage:
    python scripts/ci/session_query.py --session-id S283
    python scripts/ci/session_query.py --pr-number 3854
    python scripts/ci/session_query.py --agent-name ci-auto-healer-agent --days 7
    python scripts/ci/session_query.py --recent --days 7
    python scripts/ci/session_query.py --stats
    python scripts/ci/session_query.py --status complete --limit 10
    python scripts/ci/session_query.py --output csv
"""

import json
import argparse
import csv
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any


class SessionQuery:
    """Query interface for session index."""

    def __init__(self, index_path: str = ".codex/sessions_index.json"):
        """Initialize query interface.
        
        Args:
            index_path: Path to sessions index file (default: .codex/sessions_index.json)
        """
        self.index_path = index_path
        self.sessions: List[Dict[str, Any]] = []
        self.session_by_id: Dict[str, Dict[str, Any]] = {}
        self.verbose = False
        
        self._load_index()

    def _load_index(self) -> None:
        """Load sessions index from file or build from session files."""
        if os.path.exists(self.index_path):
            try:
                with open(self.index_path, 'r') as f:
                    data = json.load(f)
                    self.sessions = data.get('sessions', [])
                    for session in self.sessions:
                        self.session_by_id[session.get('session_id')] = session
                    if self.verbose:
                        print(f"[DEBUG] Loaded {len(self.sessions)} sessions from index", file=sys.stderr)
            except (json.JSONDecodeError, IOError) as e:
                if self.verbose:
                    print(f"[DEBUG] Failed to load index: {e}", file=sys.stderr)
                self._build_index_from_files()
        else:
            self._build_index_from_files()

    def _build_index_from_files(self) -> None:
        """Build index from session JSONL files in .codex/sessions/."""
        sessions_dir = Path(".codex/sessions")
        
        if not sessions_dir.exists():
            if self.verbose:
                print(f"[DEBUG] Sessions directory does not exist: {sessions_dir}", file=sys.stderr)
            return

        session_data: Dict[str, Dict[str, Any]] = {}
        
        for session_file in sessions_dir.glob("session_*.jsonl"):
            session_id = session_file.stem.replace("session_", "")
            
            first_timestamp = None
            last_timestamp = None
            event_types = set()
            
            try:
                with open(session_file, 'r') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            event = json.loads(line)
                            timestamp = event.get('timestamp')
                            event_type = event.get('event_type')
                            
                            if timestamp:
                                if first_timestamp is None:
                                    first_timestamp = timestamp
                                last_timestamp = timestamp
                            
                            if event_type:
                                event_types.add(event_type)
                        except json.JSONDecodeError:
                            continue
                
                if first_timestamp:
                    session_data[session_id] = {
                        'session_id': session_id,
                        'first_timestamp': first_timestamp,
                        'last_timestamp': last_timestamp or first_timestamp,
                        'event_types': list(event_types),
                        'event_count': self._count_events(session_file),
                        'status': self._infer_status(event_types),
                        'agent_name': None,
                        'pr_number': None,
                        'branch': None,
                        'tags': [],
                    }
            except (IOError, OSError):
                continue
        
        self.sessions = list(session_data.values())
        self.session_by_id = session_data
        
        if self.verbose:
            print(f"[DEBUG] Built index with {len(self.sessions)} sessions from files", file=sys.stderr)
        
        # Save index
        self._save_index()

    def _count_events(self, session_file: Path) -> int:
        """Count lines in JSONL file."""
        try:
            with open(session_file, 'r') as f:
                return sum(1 for line in f if line.strip())
        except (IOError, OSError):
            return 0

    def _infer_status(self, event_types: set) -> str:
        """Infer session status from event types."""
        if 'app.exception' in event_types or 'cli.argparse_error' in event_types:
            return 'failed'
        elif 'cli.exit' in event_types or 'cli.finish' in event_types:
            return 'complete'
        elif 'training_start' in event_types:
            return 'in_progress'
        else:
            return 'pending'

    def _save_index(self) -> None:
        """Save index to file."""
        try:
            os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
            with open(self.index_path, 'w') as f:
                json.dump({'sessions': self.sessions}, f, indent=2)
            if self.verbose:
                print(f"[DEBUG] Saved index to {self.index_path}", file=sys.stderr)
        except (IOError, OSError) as e:
            if self.verbose:
                print(f"[DEBUG] Failed to save index: {e}", file=sys.stderr)

    def query_sessions(
        self, 
        session_id: Optional[str] = None,
        pr_number: Optional[int] = None,
        agent_name: Optional[str] = None,
        status: Optional[str] = None,
        since_timestamp: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Query sessions with filters.
        
        Args:
            session_id: Filter by session ID
            pr_number: Filter by PR number
            agent_name: Filter by agent name
            status: Filter by status (complete, pending, failed, in_progress)
            since_timestamp: ISO 8601 timestamp (YYYY-MM-DDTHH:MM:SSZ) to filter sessions after
            limit: Maximum number of results to return
            
        Returns:
            List of matching session objects
        """
        results = self.sessions.copy()
        
        if session_id:
            results = [s for s in results if s.get('session_id') == session_id]
        
        if pr_number:
            results = [s for s in results if s.get('pr_number') == pr_number]
        
        if agent_name:
            results = [s for s in results if s.get('agent_name') == agent_name]
        
        if status:
            results = [s for s in results if s.get('status') == status]
        
        if since_timestamp:
            try:
                since_dt = datetime.fromisoformat(since_timestamp.replace('Z', '+00:00'))
                results = [
                    s for s in results
                    if s.get('first_timestamp') and 
                    datetime.fromisoformat(s.get('first_timestamp').replace('Z', '+00:00')) >= since_dt
                ]
            except (ValueError, AttributeError):
                pass
        
        # Sort by most recent first
        results.sort(
            key=lambda x: x.get('last_timestamp', ''), 
            reverse=True
        )
        
        if limit:
            results = results[:limit]
        
        return results

    def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get single session by ID.
        
        Args:
            session_id: Session ID to retrieve
            
        Returns:
            Session object or None if not found
        """
        return self.session_by_id.get(session_id)

    def find_similar_sessions(self, tags: List[str], limit: int = 5) -> List[Dict[str, Any]]:
        """Find sessions with matching tags.
        
        Args:
            tags: List of tags to search for
            limit: Maximum number of results
            
        Returns:
            List of sessions with matching tags
        """
        results = []
        tag_set = set(tags)
        
        for session in self.sessions:
            session_tags = set(session.get('tags', []))
            if session_tags & tag_set:  # Intersection
                match_count = len(session_tags & tag_set)
                results.append((session, match_count))
        
        # Sort by match count descending
        results.sort(key=lambda x: x[1], reverse=True)
        
        return [s[0] for s in results[:limit]]

    def list_recent_sessions(self, days: int = 7) -> List[Dict[str, Any]]:
        """List sessions from last N days.
        
        Args:
            days: Number of days to look back (default: 7)
            
        Returns:
            Chronological list of sessions
        """
        cutoff_dt = datetime.utcnow() - timedelta(days=days)
        cutoff_iso = cutoff_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        results = self.query_sessions(since_timestamp=cutoff_iso)
        results.sort(key=lambda x: x.get('first_timestamp', ''))
        
        return results

    def get_sessions_by_agent(
        self, 
        agent_name: str, 
        days: int = 7,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get sessions for specific agent in timeframe.
        
        Args:
            agent_name: Name of the agent
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            List of sessions for the agent
        """
        cutoff_dt = datetime.utcnow() - timedelta(days=days)
        cutoff_iso = cutoff_dt.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return self.query_sessions(
            agent_name=agent_name,
            since_timestamp=cutoff_iso,
            limit=limit
        )

    def filter_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Filter sessions by status.
        
        Args:
            status: Status to filter by (complete, pending, failed, in_progress)
            
        Returns:
            List of sessions with the given status
        """
        return self.query_sessions(status=status)

    def stats_summary(self) -> Dict[str, Any]:
        """Return statistics about sessions.
        
        Returns:
            Dictionary with session statistics:
            - total_sessions: Total number of sessions
            - by_status: Count by status
            - by_agent: Count by agent name
            - by_branch: Count by branch
            - date_range: Earliest and latest session timestamps
        """
        stats: Dict[str, Any] = {
            'total_sessions': len(self.sessions),
            'by_status': {},
            'by_agent': {},
            'by_branch': {},
            'date_range': None,
        }
        
        for session in self.sessions:
            status = session.get('status', 'unknown')
            agent = session.get('agent_name', 'unknown')
            branch = session.get('branch', 'unknown')
            
            stats['by_status'][status] = stats['by_status'].get(status, 0) + 1
            stats['by_agent'][agent] = stats['by_agent'].get(agent, 0) + 1
            stats['by_branch'][branch] = stats['by_branch'].get(branch, 0) + 1
        
        # Calculate date range
        if self.sessions:
            timestamps = [
                s.get('first_timestamp') for s in self.sessions
                if s.get('first_timestamp')
            ]
            if timestamps:
                timestamps.sort()
                stats['date_range'] = {
                    'earliest': timestamps[0],
                    'latest': timestamps[-1],
                }
        
        return stats


def format_json_output(data: Any) -> str:
    """Format data as JSON."""
    return json.dumps(data, indent=2)


def format_csv_output(data: List[Dict[str, Any]]) -> str:
    """Format list of dicts as CSV."""
    if not data:
        return ""
    
    output = []
    fieldnames = set()
    
    # Collect all field names
    for row in data:
        fieldnames.update(row.keys())
    
    fieldnames = sorted(list(fieldnames))
    
    # Write CSV
    import io
    csv_buffer = io.StringIO()
    writer = csv.DictWriter(csv_buffer, fieldnames=fieldnames)
    writer.writeheader()
    
    for row in data:
        writer.writerow(row)
    
    return csv_buffer.getvalue()


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Query sessions from the session index',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/ci/session_query.py --session-id abc123
  python scripts/ci/session_query.py --pr-number 3854
  python scripts/ci/session_query.py --agent-name ci-auto-healer-agent --days 7
  python scripts/ci/session_query.py --recent --days 7
  python scripts/ci/session_query.py --stats
  python scripts/ci/session_query.py --status complete --limit 10
  python scripts/ci/session_query.py --output csv
        """
    )
    
    parser.add_argument(
        '--session-id',
        help='Query by session ID'
    )
    parser.add_argument(
        '--pr-number',
        type=int,
        help='Query by PR number'
    )
    parser.add_argument(
        '--agent-name',
        help='Query by agent name'
    )
    parser.add_argument(
        '--status',
        choices=['complete', 'pending', 'failed', 'in_progress'],
        help='Filter by status'
    )
    parser.add_argument(
        '--recent',
        action='store_true',
        help='List recent sessions (use with --days)'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to look back (default: 7)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        help='Limit number of results'
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics summary'
    )
    parser.add_argument(
        '--output',
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable debug output'
    )
    parser.add_argument(
        '--index-path',
        default='.codex/sessions_index.json',
        help='Path to session index file'
    )
    
    args = parser.parse_args()
    
    try:
        sq = SessionQuery(index_path=args.index_path)
        sq.verbose = args.verbose
        
        if args.stats:
            result = sq.stats_summary()
            print(format_json_output(result))
            return 0
        
        if args.recent:
            result = sq.list_recent_sessions(days=args.days)
        elif args.session_id:
            result = sq.get_session_by_id(args.session_id)
            if result:
                result = [result]
            else:
                result = []
        elif args.pr_number:
            result = sq.query_sessions(pr_number=args.pr_number, limit=args.limit)
        elif args.agent_name:
            result = sq.get_sessions_by_agent(
                agent_name=args.agent_name,
                days=args.days,
                limit=args.limit or 50
            )
        elif args.status:
            result = sq.filter_by_status(args.status)
            if args.limit:
                result = result[:args.limit]
        else:
            result = []
        
        if not isinstance(result, list):
            result = [result] if result else []
        
        if args.output == 'csv':
            print(format_csv_output(result))
        else:
            print(format_json_output(result))
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc(file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
