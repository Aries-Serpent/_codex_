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


"""
AfterMath Cognitive Brain Updater

Updates CODEBASE_DASHBOARD.md with lessons learned and metrics
from AfterMath session artifacts.

Usage:
    python scripts/aftermath/update_cognitive_brain.py \
        --lessons=.codex/lessons_learned/ \
        --dashboard=docs/system/CODEBASE_DASHBOARD.md
"""

import argparse
import sys
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class CognitiveBrainUpdater:
    """Updates cognitive brain with aftermath insights."""
    
    def __init__(self, lessons_dir: Path, dashboard_path: Path):
        self.lessons_dir = lessons_dir
        self.dashboard_path = dashboard_path
    
    def load_recent_sessions(self, limit: int = 5) -> List[Dict]:
        """Load most recent session files."""
        session_files = sorted(
            self.lessons_dir.glob('session_*.yaml'),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:limit]
        
        sessions = []
        for file in session_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    sessions.append(data)
            except (OSError, yaml.YAMLError) as e:
                print(f"Error loading {file}: {e}", file=sys.stderr)
        
        return sessions
    
    def aggregate_metrics(self, sessions: List[Dict]) -> Dict:
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
    
    def extract_key_patterns(self, sessions: List[Dict]) -> List[str]:
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
    
    def update_dashboard(self, sessions: List[Dict]):
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
            f"**Last Updated**: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}\n\n",
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
    parser.add_argument('--lessons', required=True, help='Lessons learned directory')
    parser.add_argument('--dashboard', required=True, help='Dashboard file path')
    args = parser.parse_args()
    
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


if __name__ == '__main__':
    sys.exit(main())
