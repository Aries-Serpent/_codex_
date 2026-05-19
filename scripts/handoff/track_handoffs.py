#!/usr/bin/env python3
"""
Hand-off Tracking Utility

Tracks agent hand-off state, metrics, and history for PR #3145 workflow resolution.
Provides commands to update, view, and analyze hand-off progress.

Usage:
    python track_handoffs.py --show                     # Show current tracking table
    python track_handoffs.py --metrics                  # Show metrics summary
    python track_handoffs.py --update HO-002 complete   # Update hand-off status
    python track_handoffs.py --init                     # Initialize tracking file
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# Constants
TRACKING_FILE = Path(".codex/handoff_tracking.json")
PR_NUMBER = 3145


def init_tracking_file() -> dict:
    """Initialize empty tracking file with structure."""
    data = {
        "pr_number": PR_NUMBER,
        "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "handoffs": [
            {
                "id": "HO-001",
                "from_agent": "User",
                "to_agent": "Copilot",
                "phase": "Pre-commit 3-4",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-002",
                "from_agent": "Copilot",
                "to_agent": "Codex",
                "phase": "Pre-commit 3-4 Review",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-003",
                "from_agent": "Codex",
                "to_agent": "Copilot",
                "phase": "Pre-commit 5-8",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-004",
                "from_agent": "Copilot",
                "to_agent": "Codex",
                "phase": "Pre-commit 5-8 Review",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-005",
                "from_agent": "Codex",
                "to_agent": "Copilot",
                "phase": "Pre-commit 9-12",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-006",
                "from_agent": "Copilot",
                "to_agent": "Codex",
                "phase": "Pre-commit 9-12 Review",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-007",
                "from_agent": "Codex",
                "to_agent": "Copilot",
                "phase": "Pre-commit 13-16",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-008",
                "from_agent": "Copilot",
                "to_agent": "Codex",
                "phase": "Pre-commit 13-16 Review",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-009",
                "from_agent": "Codex",
                "to_agent": "Copilot",
                "phase": "Pre-commit 17-20 (Pass 1-3)",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-010",
                "from_agent": "Copilot",
                "to_agent": "Codex",
                "phase": "Pre-commit 17-20 Review",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-011",
                "from_agent": "Codex",
                "to_agent": "Copilot",
                "phase": "Pre-commit 17-20 (Pass 4-5)",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-012",
                "from_agent": "Copilot",
                "to_agent": "Codex",
                "phase": "Pre-commit 17-20 Approval",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-013",
                "from_agent": "Codex",
                "to_agent": "Copilot",
                "phase": "Pre-commit 21-24",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-014",
                "from_agent": "Copilot",
                "to_agent": "Codex",
                "phase": "Merge Approval",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            },
            {
                "id": "HO-015",
                "from_agent": "Codex",
                "to_agent": "Copilot",
                "phase": "Follow-up Generation",
                "status": "pending",
                "comment_link": None,
                "timestamp": None,
                "response_time": None,
                "deliverables": []
            }
        ],
        "metrics": {
            "total_handoffs": 15,
            "completed": 0,
            "in_progress": 0,
            "pending": 15,
            "failed": 0,
            "success_rate": 0.0,
            "average_response_time": None
        }
    }

    # Create directory if it doesn't exist
    TRACKING_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write file
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"✅ Initialized tracking file: {TRACKING_FILE}")
    return data


def load_tracking_data() -> dict:
    """Load tracking data from JSON file."""
    if not TRACKING_FILE.exists():
        print("⚠️  Tracking file not found. Initializing...")
        return init_tracking_file()

    with open(TRACKING_FILE) as f:
        return json.load(f)


def save_tracking_data(data: dict):
    """Save tracking data to JSON file."""
    data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def calculate_metrics(data: dict) -> dict:
    """Calculate metrics from hand-off data."""
    handoffs = data["handoffs"]

    total = len(handoffs)
    completed = sum(1 for h in handoffs if h["status"] == "complete")
    in_progress = sum(1 for h in handoffs if h["status"] == "in_progress")
    pending = sum(1 for h in handoffs if h["status"] == "pending")
    failed = sum(1 for h in handoffs if h["status"] == "failed")

    success_rate = (completed / total * 100) if total > 0 else 0.0

    # Calculate average response time (for completed hand-offs with response time)
    response_times = [
        h["response_time"] for h in handoffs
        if h["status"] == "complete" and h["response_time"]
    ]

    avg_response = None
    if response_times:
        # Simple average (assuming format like "30min" or "2hours")
        # For now, just count them
        avg_response = f"{len(response_times)} recorded"

    metrics = {
        "total_handoffs": total,
        "completed": completed,
        "in_progress": in_progress,
        "pending": pending,
        "failed": failed,
        "success_rate": round(success_rate, 1),
        "average_response_time": avg_response
    }

    data["metrics"] = metrics
    return metrics


def show_tracking_table(data: dict):
    """Display tracking table in markdown format."""
    print("\n## 📊 Hand-off Tracking Table\n")
    print("| **HO-ID** | **From** | **To** | **Phase** | **Status** | **Comment Link** | **Timestamp** | **Response Time** |")
    print("|-----------|----------|--------|-----------|------------|------------------|---------------|-------------------|")

    status_icons = {
        "pending": "⏳ Pending",
        "in_progress": "🔄 In Progress",
        "complete": "✅ Complete",
        "failed": "❌ Failed",
        "retry": "🔁 Retry",
        "paused": "⏸️ Paused",
        "skipped": "⏭️ Skipped"
    }

    for handoff in data["handoffs"]:
        ho_id = handoff["id"]
        from_agent = handoff["from_agent"]
        to_agent = handoff["to_agent"]
        phase = handoff["phase"]
        status = status_icons.get(handoff["status"], handoff["status"])

        comment = handoff["comment_link"] or "-"
        if comment != "-":
            comment_num = comment.split("#")[-1] if "#" in comment else "link"
            comment = f"[Comment #{comment_num}]({comment})"

        timestamp = handoff["timestamp"] or "-"
        response_time = handoff["response_time"] or "-"

        print(f"| {ho_id} | {from_agent} | {to_agent} | {phase} | {status} | {comment} | {timestamp} | {response_time} |")

    print()


def show_metrics(data: dict):
    """Display metrics summary."""
    metrics = calculate_metrics(data)
    save_tracking_data(data)

    print("\n## 📊 Metrics Summary\n")
    print("### Overall Statistics\n")
    print("| Metric | Value |")
    print("|--------|-------|")
    print(f"| **Total Hand-offs** | {metrics['total_handoffs']} |")
    print(f"| **Completed** | {metrics['completed']} (✅) |")
    print(f"| **In Progress** | {metrics['in_progress']} (🔄) |")
    print(f"| **Pending** | {metrics['pending']} (⏳) |")
    print(f"| **Failed** | {metrics['failed']} (❌) |")
    print(f"| **Success Rate** | {metrics['success_rate']}% |")
    print(f"| **Avg Response Time** | {metrics['average_response_time'] or 'N/A'} |")
    print()


def update_handoff(data: dict, handoff_id: str, status: str,
                   comment_link: Optional[str] = None,
                   timestamp: Optional[str] = None,
                   response_time: Optional[str] = None,
                   deliverables: Optional[list[str]] = None):
    """Update a specific hand-off."""
    handoff = next((h for h in data["handoffs"] if h["id"] == handoff_id), None)

    if not handoff:
        print(f"❌ Hand-off {handoff_id} not found")
        return False

    handoff["status"] = status

    if comment_link:
        handoff["comment_link"] = comment_link

    if timestamp:
        handoff["timestamp"] = timestamp
    elif status in ["complete", "in_progress"]:
        handoff["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if response_time:
        handoff["response_time"] = response_time

    if deliverables:
        handoff["deliverables"] = deliverables

    calculate_metrics(data)
    save_tracking_data(data)

    print(f"✅ Updated {handoff_id} to '{status}'")
    return True


def main():
    parser = argparse.ArgumentParser(description="Hand-off tracking utility")
    parser.add_argument("--init", action="store_true", help="Initialize tracking file")
    parser.add_argument("--show", action="store_true", help="Show tracking table")
    parser.add_argument("--metrics", action="store_true", help="Show metrics summary")
    parser.add_argument("--update", nargs="+", help="Update hand-off: HO-ID status [comment_link] [timestamp] [response_time]")
    parser.add_argument("--deliverables", nargs="+", help="Add deliverables to hand-off")

    args = parser.parse_args()

    if args.init:
        init_tracking_file()
        return

    # Load data
    data = load_tracking_data()

    if args.show:
        show_tracking_table(data)

    if args.metrics:
        show_metrics(data)

    if args.update:
        if len(args.update) < 2:
            print("❌ Usage: --update HO-ID status [comment_link] [timestamp] [response_time]")
            sys.exit(1)

        handoff_id = args.update[0]
        status = args.update[1]
        comment_link = args.update[2] if len(args.update) > 2 else None
        timestamp = args.update[3] if len(args.update) > 3 else None
        response_time = args.update[4] if len(args.update) > 4 else None

        update_handoff(data, handoff_id, status, comment_link, timestamp, response_time, args.deliverables)

    # If no arguments, show help
    if not any([args.init, args.show, args.metrics, args.update]):
        parser.print_help()


if __name__ == "__main__":
    main()
