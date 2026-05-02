#!/usr/bin/env python3
"""
Automated Agent Handoff Generator

Automates agent-to-agent handoff with structured templates, context packaging,
and integration with cognitive brain infrastructure.

Features:
- Auto-detect session state from action_log.ndjson
- Load patterns and metrics from cognitive brain
- Generate appropriate handoff comments
- Track handoff state in handoff_tracking.json
- Integrate with session manager and continuation prompts

Usage:
    python auto_handoff.py --from-session --output comment.md
    python auto_handoff.py --to-agent codex --phase "Plan 1 Review"
    python auto_handoff.py --generate --pr 3160
"""

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Constants
REPO_ROOT = Path(__file__).parent.parent.parent
ACTION_LOG_PATH = REPO_ROOT / ".codex" / "action_log.ndjson"
TRACKING_FILE = REPO_ROOT / ".codex" / "handoff_tracking.json"
PATTERN_STORE = REPO_ROOT / ".codex" / "cognitive_brain" / "pattern_learning_store.json"
METRICS_FILE = REPO_ROOT / ".codex" / "cognitive_brain" / "dashboard.md"
TEMPLATES_DIR = REPO_ROOT / ".codex" / "templates" / "handoff"
OUTPUT_DIR = REPO_ROOT / ".codex" / "handoffs"


class HandoffContext:
    """Represents context for a handoff between agents."""

    def __init__(
        self,
        from_agent: str = "copilot",
        to_agent: str = "codex",
        phase: str = "",
        pr_number: Optional[int] = None,
        session_id: Optional[str] = None
    ):
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.phase = phase
        self.pr_number = pr_number
        self.session_id = session_id
        self.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        # Extracted data
        self.completed_tasks: List[str] = []
        self.pending_tasks: List[str] = []
        self.deliverables: List[Dict[str, str]] = []
        self.patterns_applied: List[str] = []
        self.blockers: List[str] = []
        self.metrics: Dict[str, Any] = {}
        self.files_modified: List[str] = []
        self.recommendations: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary."""
        return {
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "phase": self.phase,
            "pr_number": self.pr_number,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "completed_tasks": self.completed_tasks,
            "pending_tasks": self.pending_tasks,
            "deliverables": self.deliverables,
            "patterns_applied": self.patterns_applied,
            "blockers": self.blockers,
            "metrics": self.metrics,
            "files_modified": self.files_modified,
            "recommendations": self.recommendations
        }


class AutoHandoff:
    """Automated handoff generator with cognitive brain integration."""

    def __init__(self, hours: int = 24):
        self.hours = hours
        self.cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)

    def extract_session_context(self) -> HandoffContext:
        """Extract context from current session's action log."""
        context = HandoffContext()

        if not ACTION_LOG_PATH.exists():
            return context

        file_ops: Dict[str, List[str]] = {
            "created": [],
            "modified": [],
            "commits": []
        }

        with open(ACTION_LOG_PATH, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                except json.JSONDecodeError:
                    continue

                # Parse timestamp
                timestamp_str = entry.get("timestamp", "")
                try:
                    if timestamp_str:
                        entry_time = datetime.fromisoformat(
                            timestamp_str.replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                        if entry_time < self.cutoff_time:
                            continue
                except (ValueError, AttributeError):
                    # Timestamp parsing failed - include entry anyway
                    pass

                # Extract file operations
                action = entry.get("action", "")
                path = entry.get("path", "")

                if action == "create" and path:
                    file_ops["created"].append(path)
                elif action in ("edit", "update") and path:
                    file_ops["modified"].append(path)
                elif "commit" in action.lower() or action == "report_progress":
                    msg = entry.get("message", entry.get("commit_message", ""))
                    if msg:
                        file_ops["commits"].append(msg)

        # Build context
        context.files_modified = list(set(file_ops["created"] + file_ops["modified"]))
        context.deliverables = [
            {"path": p, "status": "created" if p in file_ops["created"] else "modified"}
            for p in context.files_modified[:20]  # Limit to 20
        ]

        # Extract completed tasks from commits
        context.completed_tasks = file_ops["commits"][:10]  # Last 10 commits

        return context

    def load_patterns(self) -> List[str]:
        """Load applied patterns from pattern store."""
        patterns: List[str] = []

        if not PATTERN_STORE.exists():
            return patterns

        try:
            with open(PATTERN_STORE, 'r') as f:
                data = json.load(f)

            for pattern_id, pattern in data.get("patterns", {}).items():
                success_rate = pattern.get("success_rate", 0)
                if success_rate > 0.8:  # High success patterns
                    patterns.append(f"{pattern_id}: {pattern.get('name', 'Unknown')}")
        except (json.JSONDecodeError, KeyError):
            # Pattern store is corrupted or empty - return empty list
            pass

        return patterns[:5]  # Top 5

    def load_tracking_data(self) -> Dict[str, Any]:
        """Load or initialize handoff tracking data."""
        if TRACKING_FILE.exists():
            try:
                with open(TRACKING_FILE, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                # File is corrupted - will reinitialize
                pass

        # Initialize new tracking data
        return self._init_tracking_data()

    def _init_tracking_data(self) -> Dict[str, Any]:
        """Initialize new tracking data structure."""
        now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return {
            "version": "1.0.0",
            "created": now_iso,
            "last_updated": now_iso,
            "handoffs": [],
            "metrics": {
                "total_handoffs": 0,
                "completed": 0,
                "in_progress": 0,
                "pending": 0,
                "failed": 0,
                "success_rate": 0.0,
                "average_response_time_minutes": None
            },
            "settings": {
                "auto_handoff_enabled": True,
                "retry_on_failure": True,
                "max_retries": 3,
                "timeout_minutes": 60
            }
        }

    def save_tracking_data(self, data: Dict[str, Any]) -> None:
        """Save tracking data to file."""
        data["last_updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(TRACKING_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def generate_handoff_id(self, data: Dict[str, Any]) -> str:
        """Generate unique handoff ID."""
        count = len(data.get("handoffs", []))
        return f"HO-{count + 1:03d}"

    def create_handoff_record(
        self,
        handoff_id: str,
        context: HandoffContext,
        status: str = "pending"
    ) -> Dict[str, Any]:
        """Create a handoff record for tracking."""
        return {
            "id": handoff_id,
            "from_agent": context.from_agent,
            "to_agent": context.to_agent,
            "phase": context.phase,
            "pr_number": context.pr_number,
            "status": status,
            "created": context.timestamp,
            "updated": context.timestamp,
            "response_time_minutes": None,
            "context_summary": {
                "completed_tasks": len(context.completed_tasks),
                "pending_tasks": len(context.pending_tasks),
                "deliverables": len(context.deliverables),
                "files_modified": len(context.files_modified),
                "blockers": len(context.blockers)
            },
            "retry_count": 0
        }

    def generate_handoff_comment(
        self,
        context: HandoffContext,
        handoff_id: str
    ) -> str:
        """Generate formatted handoff comment."""

        # Determine direction
        direction = f"{context.from_agent.capitalize()} → {context.to_agent.capitalize()}"

        # Build deliverables list
        deliverables_str = ""
        for d in context.deliverables[:10]:
            status_icon = "✅" if d.get("status") == "created" else "📝"
            deliverables_str += f"- {status_icon} `{d.get('path', 'Unknown')}`\n"

        if not deliverables_str:
            deliverables_str = "- No deliverables in this session\n"

        # Build completed tasks
        completed_str = ""
        for task in context.completed_tasks[:5]:
            completed_str += f"- ✅ {task}\n"

        if not completed_str:
            completed_str = "- No tasks recorded\n"

        # Build pending tasks
        pending_str = ""
        for task in context.pending_tasks[:5]:
            pending_str += f"- ⏳ {task}\n"

        if not pending_str:
            pending_str = "- None identified\n"

        # Build blockers
        blockers_str = ""
        for blocker in context.blockers[:3]:
            blockers_str += f"- ❌ {blocker}\n"

        if not blockers_str:
            blockers_str = "- None ✅\n"

        # Build patterns
        patterns_str = ""
        for pattern in context.patterns_applied[:3]:
            patterns_str += f"- 🎯 {pattern}\n"

        if not patterns_str:
            patterns_str = "- Standard patterns applied\n"

        # Build recommendations
        recommendations_str = ""
        for rec in context.recommendations[:3]:
            recommendations_str += f"- 💡 {rec}\n"

        if not recommendations_str:
            recommendations_str = "- Review deliverables and provide feedback\n"

        # Generate comment
        return f"""## 📤 HANDOFF: {direction}

@{context.to_agent} {context.phase} - Handoff Initiated

---

### 📊 Session Summary

**Phase**: {context.phase}
**PR**: #{context.pr_number or 'N/A'}
**Session**: {context.session_id or 'Current'}
**Timestamp**: {context.timestamp}
**Handoff ID**: {handoff_id}

---

### ✅ Completed Tasks

{completed_str}

---

### 📦 Deliverables

{deliverables_str}

---

### ⏳ Pending Tasks

{pending_str}

---

### 🚧 Blockers

{blockers_str}

---

### 🎯 Patterns Applied

{patterns_str}

---

### 📈 Session Metrics

| Metric | Value |
|--------|-------|
| Files Modified | {len(context.files_modified)} |
| Tasks Completed | {len(context.completed_tasks)} |
| Deliverables | {len(context.deliverables)} |
| Blockers | {len(context.blockers)} |

---

### 💡 Recommendations for {context.to_agent.capitalize()}

{recommendations_str}

---

### ➡️ Expected Actions

1. Review deliverables and approach
2. Validate against requirements
3. Provide approval or request changes
4. Generate response handoff comment

---

**Handoff ID**: {handoff_id}
**Direction**: {direction}
**Generated**: {context.timestamp}

`#handoff` `#{context.from_agent}-to-{context.to_agent}` `#automated`
"""

    def execute_handoff(
        self,
        from_agent: str = "copilot",
        to_agent: str = "codex",
        phase: str = "",
        pr_number: Optional[int] = None,
        output_path: Optional[Path] = None
    ) -> Tuple[str, str]:
        """Execute a complete handoff workflow."""

        # Extract context
        context = self.extract_session_context()
        context.from_agent = from_agent
        context.to_agent = to_agent
        context.phase = phase
        context.pr_number = pr_number
        context.patterns_applied = self.load_patterns()

        # Load and update tracking
        tracking_data = self.load_tracking_data()
        handoff_id = self.generate_handoff_id(tracking_data)

        # Create handoff record
        record = self.create_handoff_record(handoff_id, context)
        tracking_data["handoffs"].append(record)

        # Update metrics
        metrics = tracking_data["metrics"]
        metrics["total_handoffs"] = len(tracking_data["handoffs"])
        metrics["pending"] += 1

        # Save tracking data
        self.save_tracking_data(tracking_data)

        # Generate comment
        comment = self.generate_handoff_comment(context, handoff_id)

        # Save to output
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w') as f:
                f.write(comment)
            print(f"✅ Handoff comment saved: {output_path}")

        return handoff_id, comment

    def update_handoff_status(
        self,
        handoff_id: str,
        status: str,
        response_time_minutes: Optional[int] = None
    ) -> bool:
        """Update the status of a handoff."""
        tracking_data = self.load_tracking_data()

        for handoff in tracking_data["handoffs"]:
            if handoff["id"] == handoff_id:
                old_status = handoff["status"]
                handoff["status"] = status
                handoff["updated"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

                if response_time_minutes:
                    handoff["response_time_minutes"] = response_time_minutes

                # Update metrics
                metrics = tracking_data["metrics"]
                if old_status == "pending":
                    metrics["pending"] = max(0, metrics["pending"] - 1)
                elif old_status == "in_progress":
                    metrics["in_progress"] = max(0, metrics["in_progress"] - 1)

                if status == "complete":
                    metrics["completed"] += 1
                elif status == "in_progress":
                    metrics["in_progress"] += 1
                elif status == "failed":
                    metrics["failed"] += 1

                # Calculate success rate
                total = metrics["total_handoffs"]
                if total > 0:
                    metrics["success_rate"] = round(
                        (metrics["completed"] / total) * 100, 1
                    )

                self.save_tracking_data(tracking_data)
                print(f"✅ Updated {handoff_id} to '{status}'")
                return True

        print(f"❌ Handoff {handoff_id} not found")
        return False

    def get_handoff_status(self, handoff_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific handoff."""
        tracking_data = self.load_tracking_data()

        for handoff in tracking_data["handoffs"]:
            if handoff["id"] == handoff_id:
                return handoff

        return None

    def list_handoffs(
        self,
        status_filter: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """List recent handoffs with optional status filter."""
        tracking_data = self.load_tracking_data()
        handoffs = tracking_data.get("handoffs", [])

        if status_filter:
            handoffs = [h for h in handoffs if h["status"] == status_filter]

        # Sort by created timestamp descending
        handoffs.sort(key=lambda x: x.get("created", ""), reverse=True)

        return handoffs[:limit]


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Automated Agent Handoff Generator"
    )

    parser.add_argument(
        "--generate", "-g",
        action="store_true",
        help="Generate a handoff comment"
    )
    parser.add_argument(
        "--from-session", "-s",
        action="store_true",
        help="Extract context from current session"
    )
    parser.add_argument(
        "--from-agent",
        default="copilot",
        choices=["copilot", "codex", "user"],
        help="Source agent (default: copilot)"
    )
    parser.add_argument(
        "--to-agent",
        default="codex",
        choices=["copilot", "codex", "user"],
        help="Target agent (default: codex)"
    )
    parser.add_argument(
        "--phase",
        default="",
        help="Phase name (e.g., 'Plan 1 Review')"
    )
    parser.add_argument(
        "--pr",
        type=int,
        help="PR number"
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Hours to look back for context (default: 24)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file for handoff comment"
    )
    parser.add_argument(
        "--update",
        nargs=2,
        metavar=("HANDOFF_ID", "STATUS"),
        help="Update handoff status (e.g., --update HO-001 complete)"
    )
    parser.add_argument(
        "--status",
        help="Get status of a handoff by ID"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List recent handoffs"
    )
    parser.add_argument(
        "--list-status",
        choices=["pending", "in_progress", "complete", "failed"],
        help="Filter handoffs by status"
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="Initialize tracking file"
    )

    args = parser.parse_args()

    handoff = AutoHandoff(hours=args.hours)

    if args.init:
        data = handoff._init_tracking_data()
        handoff.save_tracking_data(data)
        print(f"✅ Initialized tracking file: {TRACKING_FILE}")
        return

    if args.generate or args.from_session:
        handoff_id, comment = handoff.execute_handoff(
            from_agent=args.from_agent,
            to_agent=args.to_agent,
            phase=args.phase,
            pr_number=args.pr,
            output_path=args.output
        )

        if not args.output:
            print(comment)

        print(f"\n✅ Handoff created: {handoff_id}")
        return

    if args.update:
        handoff_id, status = args.update
        handoff.update_handoff_status(handoff_id, status)
        return

    if args.status:
        result = handoff.get_handoff_status(args.status)
        if result:
            print(json.dumps(result, indent=2))
        else:
            print(f"❌ Handoff {args.status} not found")
        return

    if args.list:
        handoffs = handoff.list_handoffs(status_filter=args.list_status)

        print("\n## 📋 Recent Handoffs\n")
        print("| ID | From | To | Phase | Status | Created |")
        print("|-----|------|-----|-------|--------|---------|")

        status_icons = {
            "pending": "⏳",
            "in_progress": "🔄",
            "complete": "✅",
            "failed": "❌"
        }

        for h in handoffs:
            icon = status_icons.get(h["status"], "❓")
            created = h.get("created", "")[:10]
            print(
                f"| {h['id']} | {h['from_agent']} | {h['to_agent']} | "
                f"{h['phase'][:20]} | {icon} {h['status']} | {created} |"
            )

        print()
        return

    # Default: show help
    parser.print_help()


if __name__ == "__main__":
    main()
