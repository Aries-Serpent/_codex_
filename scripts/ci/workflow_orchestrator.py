#!/usr/bin/env python3
"""
Telemetry-Driven Workflow Orchestrator

Analyzes telemetry data to determine which workflows should run
based on historical failure patterns and current PR characteristics.

Usage:
    python scripts/ci/workflow_orchestrator.py \
        --pr-number 1234 \
        --telemetry-file telemetry_report.json \
        --output workflow_plan.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


class WorkflowOrchestrator:
    """Orchestrates workflow execution based on telemetry and PR characteristics."""

    # Workflow categories and their triggers
    WORKFLOW_CATEGORIES = {
        "critical": {
            "workflows": ["smoke-tests", "pr-size-analyzer", "security-scan"],
            "trigger": "always",
            "reason": "Essential validation for all PRs",
        },
        "standard": {
            "workflows": ["unit-tests", "linting", "type-checking"],
            "trigger": "small|medium",
            "reason": "Standard validation for manageable PRs",
        },
        "comprehensive": {
            "workflows": ["integration-tests", "coverage-report", "performance"],
            "trigger": "small",
            "reason": "Full validation for small PRs",
        },
        "on-demand": {
            "workflows": ["slow-tests", "e2e-tests", "load-testing"],
            "trigger": "manual",
            "reason": "Resource-intensive tests, manual trigger only",
        },
    }

    # Pattern-based workflow adjustments
    PATTERN_WORKFLOWS = {
        "auto-fix": ["auto-fix-validation", "linting-extra"],
        "test-infrastructure": ["import-validation", "dependency-audit"],
        "coverage-timeout": ["coverage-with-timeout", "test-profiling"],
        "filesystem-deadlock": ["filesystem-validation", "concurrent-ops-test"],
        "pre-merge-cascade": ["integration-tests", "dependency-graph"],
    }

    def __init__(self, pr_size: str, telemetry_data: dict, changed_files: list[str]):
        self.pr_size = pr_size
        self.telemetry = telemetry_data
        self.changed_files = changed_files
        self.workflow_plan = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pr_size": pr_size,
            "workflows_to_run": [],
            "workflows_to_skip": [],
            "reasons": {},
        }

    def analyze_patterns(self) -> dict[str, int]:
        """Analyze telemetry for failure patterns.

        Returns:
            Dictionary mapping pattern names to occurrence counts
        """
        if "pattern_distribution" in self.telemetry:
            return self.telemetry["pattern_distribution"]

        # Fallback: analyze failed runs manually
        patterns = {}
        for run in self.telemetry.get("failed_runs", []):
            pattern = run.get("pattern", "unknown")
            patterns[pattern] = patterns.get(pattern, 0) + 1

        return patterns

    def should_run_workflow(self, workflow: str, trigger: str) -> bool:
        """Determine if a workflow should run based on trigger conditions.

        Args:
            workflow: Workflow name
            trigger: Trigger condition (always, small, small|medium, manual)

        Returns:
            True if workflow should run
        """
        if trigger == "always":
            return True

        if trigger == "manual":
            return False

        # Parse trigger conditions
        allowed_sizes = trigger.split("|")
        return self.pr_size in allowed_sizes

    def get_pattern_workflows(self, patterns: dict[str, int]) -> set[str]:
        """Get additional workflows based on detected patterns.

        Args:
            patterns: Pattern occurrence counts

        Returns:
            Set of workflow names to add
        """
        additional_workflows = set()

        for pattern, count in patterns.items():
            if count > 0 and pattern in self.PATTERN_WORKFLOWS:
                additional_workflows.update(self.PATTERN_WORKFLOWS[pattern])

        return additional_workflows

    def analyze_changed_files(self) -> set[str]:
        """Analyze changed files to determine relevant workflows.

        Returns:
            Set of workflow names based on file changes
        """
        workflows = set()

        # Check file patterns
        has_python = any(f.endswith(".py") for f in self.changed_files)
        has_yaml = any(f.endswith((".yml", ".yaml")) for f in self.changed_files)
        has_docker = any("Dockerfile" in f or f.endswith(".dockerignore") for f in self.changed_files)
        has_docs = any(f.startswith("docs/") or f.endswith(".md") for f in self.changed_files)

        if has_python:
            workflows.update(["python-tests", "type-checking", "linting"])

        if has_yaml:
            workflows.add("yaml-validation")

        if has_docker:
            workflows.add("container-build")

        if has_docs:
            workflows.add("docs-build")

        return workflows

    def generate_plan(self) -> dict:
        """Generate workflow execution plan.

        Returns:
            Workflow execution plan with recommendations
        """
        # Analyze patterns from telemetry
        patterns = self.analyze_patterns()

        # Start with category-based workflows
        for _, config in self.WORKFLOW_CATEGORIES.items():
            for workflow in config["workflows"]:
                should_run = self.should_run_workflow(workflow, config["trigger"])

                if should_run:
                    self.workflow_plan["workflows_to_run"].append(workflow)
                    self.workflow_plan["reasons"][workflow] = config["reason"]
                else:
                    self.workflow_plan["workflows_to_skip"].append(workflow)
                    self.workflow_plan["reasons"][workflow] = f"Skipped: {config['trigger']}"

        # Add pattern-based workflows
        pattern_workflows = self.get_pattern_workflows(patterns)
        for workflow in pattern_workflows:
            if workflow not in self.workflow_plan["workflows_to_run"]:
                self.workflow_plan["workflows_to_run"].append(workflow)
                matching_patterns = [
                    p for p, wfs in self.PATTERN_WORKFLOWS.items() if workflow in wfs
                ]
                self.workflow_plan["reasons"][workflow] = (
                    f"Added due to patterns: {', '.join(matching_patterns)}"
                )

        # Add file-based workflows
        file_workflows = self.analyze_changed_files()
        for workflow in file_workflows:
            if workflow not in self.workflow_plan["workflows_to_run"]:
                self.workflow_plan["workflows_to_run"].append(workflow)
                self.workflow_plan["reasons"][workflow] = "Added based on file changes"

        # Add metadata
        self.workflow_plan["total_to_run"] = len(self.workflow_plan["workflows_to_run"])
        self.workflow_plan["total_skipped"] = len(self.workflow_plan["workflows_to_skip"])
        self.workflow_plan["patterns_detected"] = patterns

        return self.workflow_plan

    def estimate_duration(self) -> dict[str, int]:
        """Estimate execution duration for planned workflows.

        Returns:
            Dictionary with duration estimates
        """
        # Rough estimates in minutes
        duration_estimates = {
            "smoke-tests": 5,
            "unit-tests": 15,
            "integration-tests": 25,
            "slow-tests": 50,
            "coverage-report": 20,
            "security-scan": 10,
            "linting": 3,
            "type-checking": 5,
        }

        total_duration = 0
        workflow_durations = {}

        for workflow in self.workflow_plan["workflows_to_run"]:
            # Use estimate or default to 10 minutes
            duration = duration_estimates.get(workflow, 10)
            workflow_durations[workflow] = duration
            total_duration += duration

        return {
            "total_minutes": total_duration,
            "total_hours": round(total_duration / 60, 2),
            "workflow_durations": workflow_durations,
        }


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Orchestrate workflow execution based on telemetry"
    )
    parser.add_argument("--pr-size", required=True, choices=["small", "medium", "large", "refactor"])
    parser.add_argument("--telemetry-file", required=True, help="Path to telemetry JSON file")
    parser.add_argument("--changed-files", nargs="*", default=[], help="List of changed files")
    parser.add_argument("--output", default="workflow_plan.json", help="Output file path")
    parser.add_argument("--estimate-duration", action="store_true", help="Include duration estimates")

    args = parser.parse_args()

    # Load telemetry data
    if not Path(args.telemetry_file).exists():
        print(f"Error: Telemetry file not found: {args.telemetry_file}")
        sys.exit(1)

    with open(args.telemetry_file) as f:
        telemetry_data = json.load(f)

    # Create orchestrator
    orchestrator = WorkflowOrchestrator(
        pr_size=args.pr_size,
        telemetry_data=telemetry_data,
        changed_files=args.changed_files,
    )

    # Generate plan
    plan = orchestrator.generate_plan()

    # Add duration estimates if requested
    if args.estimate_duration:
        plan["duration_estimate"] = orchestrator.estimate_duration()

    # Write plan
    with open(args.output, "w") as f:
        json.dump(plan, f, indent=2)

    # Print summary
    print(f"✓ Workflow plan generated: {args.output}")
    print(f"\nWorkflows to run: {plan['total_to_run']}")
    print(f"Workflows skipped: {plan['total_skipped']}")

    if args.estimate_duration:
        duration = plan["duration_estimate"]
        print(f"Estimated duration: {duration['total_hours']} hours ({duration['total_minutes']} minutes)")

    # Print workflow list
    print("\n📋 Workflows to execute:")
    for workflow in plan["workflows_to_run"]:
        reason = plan["reasons"].get(workflow, "No reason provided")
        print(f"  - {workflow}: {reason}")


if __name__ == "__main__":
    main()
