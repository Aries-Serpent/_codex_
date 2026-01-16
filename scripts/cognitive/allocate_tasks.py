#!/usr/bin/env python3
"""
Allocate Tasks

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/allocate_tasks.py [options]
    
    Examples:
    $ python scripts/cognitive/allocate_tasks.py --help

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
Cognitive Brain - Task Allocation
Part of Decision Engine - integrates with R16 (Task Decomposition)
"""
import argparse
import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


def allocate_tasks(
    perception_data_dir: str,
    causal_analysis_path: str,
    output_path: str,
    agents: str = "all"
) -> Dict[str, Any]:
    """
    Allocate tasks to agents based on analysis and agent capabilities.
    
    Args:
        perception_data_dir: Directory with perception data
        causal_analysis_path: Path to causal analysis results
        output_path: Path to save task allocation
        agents: Which agents to include ("all" or specific)
    
    Returns:
        Dictionary with task allocations
    """
    input_path = Path(perception_data_dir)
    
    # Load analysis data
    causal_analysis = {}
    if Path(causal_analysis_path).exists():
        with open(causal_analysis_path) as f:
            causal_analysis = json.load(f)
    
    anomalies = {}
    anomalies_file = input_path / "anomalies.json"
    if anomalies_file.exists():
        with open(anomalies_file) as f:
            anomalies = json.load(f)
    
    patterns = {}
    patterns_file = input_path / "patterns.json"
    if patterns_file.exists():
        with open(patterns_file) as f:
            patterns = json.load(f)
    
    # Task allocation
    allocation = {
        "allocation_timestamp": datetime.now().isoformat(),
        "agents_included": agents,
        "task_allocations": {},
        "total_tasks": 0
    }
    
    # Agent 1: Emergent Intelligence - Pattern Analysis
    agent_1_tasks = []
    for pattern in patterns.get("patterns_detected", []):
        agent_1_tasks.append({
            "task_id": f"pattern_analysis_{len(agent_1_tasks)+1}",
            "task_type": "analyze_pattern",
            "pattern_type": pattern["pattern_type"],
            "priority": "high" if pattern["confidence"] > 0.9 else "medium",
            "estimated_duration_minutes": 15
        })
    
    allocation["task_allocations"]["agent_1"] = {
        "agent_name": "Emergent Intelligence",
        "seed": 46,
        "tasks": agent_1_tasks,
        "total_tasks": len(agent_1_tasks),
        "estimated_total_duration_minutes": sum(t["estimated_duration_minutes"] for t in agent_1_tasks)
    }
    
    # Agent 2: Performance Monitor - Anomaly Investigation
    agent_2_tasks = []
    for anomaly in anomalies.get("anomalies_detected", []):
        if anomaly["severity"] in ["high", "medium"]:
            agent_2_tasks.append({
                "task_id": f"performance_check_{len(agent_2_tasks)+1}",
                "task_type": "investigate_anomaly",
                "anomaly_type": anomaly["anomaly_type"],
                "severity": anomaly["severity"],
                "priority": "critical" if anomaly["severity"] == "high" else "high",
                "estimated_duration_minutes": 20
            })
    
    allocation["task_allocations"]["agent_2"] = {
        "agent_name": "Performance Monitor",
        "seed": 47,
        "tasks": agent_2_tasks,
        "total_tasks": len(agent_2_tasks),
        "estimated_total_duration_minutes": sum(t["estimated_duration_minutes"] for t in agent_2_tasks)
    }
    
    # Agent 3: Documentation - Report Generation
    agent_3_tasks = [{
        "task_id": "doc_update_1",
        "task_type": "update_documentation",
        "scope": "perception_findings",
        "priority": "medium",
        "estimated_duration_minutes": 30
    }]
    
    allocation["task_allocations"]["agent_3"] = {
        "agent_name": "Documentation",
        "seed": 48,
        "tasks": agent_3_tasks,
        "total_tasks": len(agent_3_tasks),
        "estimated_total_duration_minutes": 30
    }
    
    # Agent 4: CI Optimizer - Workflow Improvements
    agent_4_tasks = []
    for root_cause in causal_analysis.get("root_causes", []):
        if "ci" in root_cause["effect"].lower() or "test" in root_cause["effect"].lower():
            agent_4_tasks.append({
                "task_id": f"ci_optimize_{len(agent_4_tasks)+1}",
                "task_type": "optimize_workflow",
                "target": root_cause["effect"],
                "priority": "high",
                "estimated_duration_minutes": 25
            })
    
    allocation["task_allocations"]["agent_4"] = {
        "agent_name": "CI Optimizer",
        "seed": 49,
        "tasks": agent_4_tasks,
        "total_tasks": len(agent_4_tasks),
        "estimated_total_duration_minutes": sum(t["estimated_duration_minutes"] for t in agent_4_tasks)
    }
    
    # Agent 5: Reasoning Advisor - Causal Analysis Review
    agent_5_tasks = [{
        "task_id": "reasoning_review_1",
        "task_type": "validate_causal_relationships",
        "relationships_count": len(causal_analysis.get("causal_relationships", [])),
        "priority": "high",
        "estimated_duration_minutes": 20
    }]
    
    allocation["task_allocations"]["agent_5"] = {
        "agent_name": "Reasoning Advisor",
        "seed": 50,
        "tasks": agent_5_tasks,
        "total_tasks": len(agent_5_tasks),
        "estimated_total_duration_minutes": 20
    }
    
    # Calculate totals
    allocation["total_tasks"] = sum(
        agent_data["total_tasks"]
        for agent_data in allocation["task_allocations"].values()
    )
    
    allocation["total_estimated_duration_minutes"] = sum(
        agent_data["estimated_total_duration_minutes"]
        for agent_data in allocation["task_allocations"].values()
    )
    
    # Save results
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(allocation, f, indent=2)
    
    print(f"✅ Task allocation complete")
    print(f"   Total tasks allocated: {allocation['total_tasks']}")
    print(f"   Agents involved: {len(allocation['task_allocations'])}")
    print(f"   Total estimated duration: {allocation['total_estimated_duration_minutes']} minutes")
    for agent_id, agent_data in allocation["task_allocations"].items():
        print(f"   - {agent_id} ({agent_data['agent_name']}): {agent_data['total_tasks']} tasks")
    print(f"   Saved to: {output_path}")
    
    return allocation


def main():
    parser = argparse.ArgumentParser(
        description="Allocate tasks to agents"
    )
    parser.add_argument(
        "--perception-data",
        required=True,
        help="Directory with perception data"
    )
    parser.add_argument(
        "--causal-analysis",
        required=True,
        help="Path to causal analysis JSON"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path"
    )
    parser.add_argument(
        "--agents",
        default="all",
        help="Which agents to include (default: all)"
    )
    
    args = parser.parse_args()
    
    allocate_tasks(
        args.perception_data,
        args.causal_analysis,
        args.output,
        args.agents
    )


if __name__ == "__main__":
    main()
