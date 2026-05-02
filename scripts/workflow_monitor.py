#!/usr/bin/env python3
"""
Workflow Monitor - Monitor GitHub Actions workflows for a specific commit.

This script monitors all workflow runs for a given commit on the main branch
and reports their status until all workflows complete.
"""

import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List


@dataclass
class WorkflowRun:
    """Represents a GitHub Actions workflow run."""
    id: int
    name: str
    status: str
    conclusion: str | None
    html_url: str
    created_at: str
    updated_at: str
    run_number: int
    event: str

    @property
    def is_complete(self) -> bool:
        """Check if workflow is complete."""
        return self.status == "completed"

    @property
    def is_successful(self) -> bool:
        """Check if workflow completed successfully."""
        return self.is_complete and self.conclusion in ["success", "skipped"]

    @property
    def display_status(self) -> str:
        """Get display-friendly status."""
        if self.status == "completed":
            emoji = {
                "success": "✅",
                "failure": "❌",
                "cancelled": "🚫",
                "skipped": "⏭️",
                "action_required": "⚠️",
            }.get(self.conclusion or "", "❓")
            return f"{emoji} {self.conclusion or 'unknown'}"
        if self.status == "in_progress":
            return "🔄 in_progress"
        if self.status == "queued":
            return "⏳ queued"
        return f"❓ {self.status}"


@dataclass
class WorkflowMonitorReport:
    """Summary report for workflow monitoring."""
    commit_sha: str
    total_workflows: int = 0
    completed: int = 0
    in_progress: int = 0
    queued: int = 0
    failed: int = 0
    successful: int = 0
    skipped: int = 0
    action_required: int = 0
    workflows: List[WorkflowRun] = field(default_factory=list)

    @property
    def all_complete(self) -> bool:
        """Check if all workflows are complete."""
        return self.in_progress == 0 and self.queued == 0

    @property
    def has_failures(self) -> bool:
        """Check if any workflows failed."""
        return self.failed > 0

    def update_from_workflows(self, workflows: List[WorkflowRun]):
        """Update statistics from workflow list."""
        self.workflows = workflows
        self.total_workflows = len(workflows)
        self.completed = sum(1 for w in workflows if w.is_complete)
        self.in_progress = sum(1 for w in workflows if w.status == "in_progress")
        self.queued = sum(1 for w in workflows if w.status == "queued")
        self.failed = sum(1 for w in workflows if w.conclusion == "failure")
        self.successful = sum(1 for w in workflows if w.conclusion == "success")
        self.skipped = sum(1 for w in workflows if w.conclusion == "skipped")
        self.action_required = sum(1 for w in workflows if w.conclusion == "action_required")

    def print_summary(self):
        """Print a summary report."""
        print("\n" + "="*80)
        print("📊 WORKFLOW MONITORING REPORT")
        print(f"Commit SHA: {self.commit_sha[:8]}")
        print(f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print("="*80)
        print("\n📈 Overall Status:")
        print(f"  Total Workflows: {self.total_workflows}")
        print(f"  ✅ Successful: {self.successful}")
        print(f"  ⏭️  Skipped: {self.skipped}")
        print(f"  ❌ Failed: {self.failed}")
        print(f"  ⚠️  Action Required: {self.action_required}")
        print(f"  🔄 In Progress: {self.in_progress}")
        print(f"  ⏳ Queued: {self.queued}")

        if self.all_complete:
            print(f"\n{'='*80}")
            print("✅ ALL WORKFLOWS COMPLETE!")
            print(f"{'='*80}")
        else:
            print(f"\n{'='*80}")
            print(f"⏳ WAITING: {self.in_progress + self.queued} workflows still running")
            print(f"{'='*80}")

    def print_detailed_status(self):
        """Print detailed status for each workflow."""
        print("\n📋 Detailed Workflow Status:")
        print("-"*80)

        # Group by status
        groups = {
            "In Progress": [w for w in self.workflows if w.status == "in_progress"],
            "Queued": [w for w in self.workflows if w.status == "queued"],
            "Failed": [w for w in self.workflows if w.conclusion == "failure"],
            "Action Required": [w for w in self.workflows if w.conclusion == "action_required"],
            "Successful": [w for w in self.workflows if w.conclusion == "success"],
            "Skipped": [w for w in self.workflows if w.conclusion == "skipped"],
        }

        for group_name, group_workflows in groups.items():
            if group_workflows:
                print(f"\n{group_name} ({len(group_workflows)}):")
                for w in sorted(group_workflows, key=lambda x: x.name):
                    print(f"  {w.display_status} {w.name}")
                    print(f"    Run #{w.run_number} | Event: {w.event}")
                    print(f"    URL: {w.html_url}")

    def save_to_file(self, filepath: str):
        """Save report to JSON file."""
        data = {
            "commit_sha": self.commit_sha,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "summary": {
                "total_workflows": self.total_workflows,
                "completed": self.completed,
                "in_progress": self.in_progress,
                "queued": self.queued,
                "failed": self.failed,
                "successful": self.successful,
                "skipped": self.skipped,
                "action_required": self.action_required,
                "all_complete": self.all_complete,
            },
            "workflows": [
                {
                    "id": w.id,
                    "name": w.name,
                    "status": w.status,
                    "conclusion": w.conclusion,
                    "html_url": w.html_url,
                    "created_at": w.created_at,
                    "updated_at": w.updated_at,
                    "run_number": w.run_number,
                    "event": w.event,
                }
                for w in self.workflows
            ]
        }
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n💾 Report saved to: {filepath}")


def parse_workflow_data(workflow_data: Dict[str, Any]) -> WorkflowRun:
    """Parse workflow data from GitHub API response."""
    return WorkflowRun(
        id=workflow_data["id"],
        name=workflow_data["name"],
        status=workflow_data["status"],
        conclusion=workflow_data.get("conclusion"),
        html_url=workflow_data["html_url"],
        created_at=workflow_data["created_at"],
        updated_at=workflow_data["updated_at"],
        run_number=workflow_data["run_number"],
        event=workflow_data["event"],
    )


def load_workflow_runs(json_file: str) -> List[WorkflowRun]:
    """Load workflow runs from JSON file."""
    with open(json_file, 'r') as f:
        data = json.load(f)

    workflows = []
    for run in data.get("workflow_runs", []):
        workflows.append(parse_workflow_data(run))

    return workflows


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python workflow_monitor.py <workflow_runs.json> [commit_sha]")
        print("\nExpects a JSON file containing workflow runs data from GitHub API.")
        sys.exit(1)

    json_file = sys.argv[1]
    commit_sha = sys.argv[2] if len(sys.argv) > 2 else "main"

    # Load workflows
    workflows = load_workflow_runs(json_file)

    # Create report
    report = WorkflowMonitorReport(commit_sha=commit_sha)
    report.update_from_workflows(workflows)

    # Print report
    report.print_summary()
    report.print_detailed_status()

    # Save report
    output_file = json_file.replace(".json", "_report.json")
    report.save_to_file(output_file)

    # Exit code based on status
    if not report.all_complete:
        print("\n⏳ Some workflows are still running. Please wait and check again.")
        sys.exit(2)  # Still running
    elif report.has_failures:
        print("\n❌ Some workflows failed. Please investigate.")
        sys.exit(1)  # Failed
    else:
        print("\n✅ All workflows completed successfully!")
        sys.exit(0)  # Success


if __name__ == "__main__":
    main()
