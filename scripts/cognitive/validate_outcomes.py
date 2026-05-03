#!/usr/bin/env python3
"""
Validate Outcomes

Purpose:
    Validates outcomes

Usage:
    python scripts/cognitive/validate_outcomes.py [options]

    Examples:
    $ python scripts/cognitive/validate_outcomes.py --help

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


import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any


def validate_outcomes(results_dir: str, expectations_path: str, output_path: str) -> dict[str, Any]:
    """
    Validate execution outcomes against expected results.

    Args:
        results_dir: Directory with execution results
        expectations_path: Path to task_allocation.json with expectations
        output_path: Path to save validation report

    Returns:
        Validation report
    """
    results_path = Path(results_dir)

    # Load expectations
    with open(expectations_path) as f:
        expectations = json.load(f)

    # Load execution status
    status_file = results_path / "execution_status.json"
    execution_status = {}
    if status_file.exists():
        with open(status_file) as f:
            execution_status = json.load(f)

    # Validation report
    report = {
        "validation_timestamp": datetime.now().isoformat(),
        "validations": [],
        "discrepancies": [],
        "overall_validation_status": "pass"
    }

    # Validate task completion
    expected_tasks = expectations.get("total_tasks", 0)
    completed_tasks = execution_status.get("overall_metrics", {}).get("completed_tasks", 0)

    report["validations"].append({
        "check": "task_completion",
        "expected": expected_tasks,
        "actual": completed_tasks,
        "status": "pass" if completed_tasks >= expected_tasks * 0.95 else "fail",
        "completion_rate": completed_tasks / expected_tasks if expected_tasks > 0 else 0
    })

    # Validate success rate
    success_rate = execution_status.get("overall_metrics", {}).get("average_success_rate", 0)

    report["validations"].append({
        "check": "success_rate",
        "expected": 0.95,
        "actual": success_rate,
        "status": "pass" if success_rate >= 0.95 else "warning" if success_rate >= 0.85 else "fail"
    })

    # Validate agent participation
    expected_agents = len(expectations.get("task_allocations", {}))
    actual_agents = execution_status.get("total_agents", 0)

    report["validations"].append({
        "check": "agent_participation",
        "expected": expected_agents,
        "actual": actual_agents,
        "status": "pass" if actual_agents >= expected_agents else "fail"
    })

    # Check for discrepancies
    for agent_id, agent_allocation in expectations.get("task_allocations", {}).items():
        agent_status = execution_status.get("agent_statuses", {}).get(agent_id)

        if not agent_status:
            report["discrepancies"].append({
                "agent": agent_id,
                "issue": "agent_not_executed",
                "expected_tasks": agent_allocation.get("total_tasks"),
                "severity": "high"
            })
            continue

        expected_agent_tasks = agent_allocation.get("total_tasks", 0)
        actual_agent_tasks = agent_status.get("tasks_completed", 0)

        if actual_agent_tasks < expected_agent_tasks:
            report["discrepancies"].append({
                "agent": agent_id,
                "issue": "incomplete_tasks",
                "expected": expected_agent_tasks,
                "actual": actual_agent_tasks,
                "missing": expected_agent_tasks - actual_agent_tasks,
                "severity": "medium"
            })

    # Determine overall status
    failed_validations = sum(1 for v in report["validations"] if v["status"] == "fail")
    high_severity_discrepancies = sum(1 for d in report["discrepancies"] if d.get("severity") == "high")

    if failed_validations > 0 or high_severity_discrepancies > 0:
        report["overall_validation_status"] = "fail"
    elif len(report["discrepancies"]) > 0:
        report["overall_validation_status"] = "warning"
    else:
        report["overall_validation_status"] = "pass"

    # Summary
    report["summary"] = {
        "total_validations": len(report["validations"]),
        "passed_validations": sum(1 for v in report["validations"] if v["status"] == "pass"),
        "failed_validations": failed_validations,
        "total_discrepancies": len(report["discrepancies"]),
        "high_severity_discrepancies": high_severity_discrepancies
    }

    # Save report
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print("✅ Outcome validation complete")
    print(f"   Overall status: {report['overall_validation_status'].upper()}")
    print(f"   Validations passed: {report['summary']['passed_validations']}/{report['summary']['total_validations']}")
    print(f"   Discrepancies found: {report['summary']['total_discrepancies']}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Validate execution outcomes")
    parser.add_argument("--results", required=True, help="Directory with results")
    parser.add_argument("--expectations", required=True, help="Task allocation JSON")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    validate_outcomes(args.results, args.expectations, args.output)


if __name__ == "__main__":
    main()
