#!/usr/bin/env python3
"""
Cognitive Brain - Execution Monitor
Monitors real-time execution status across all agents
"""
import argparse
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime


def monitor_execution(results_dir: str, output_path: str, real_time: bool = False) -> Dict[str, Any]:
    """
    Monitor execution status across all agents.
    
    Args:
        results_dir: Directory with agent results
        output_path: Path to save monitoring data
        real_time: Enable real-time monitoring
    
    Returns:
        Execution status summary
    """
    results_path = Path(results_dir)
    
    # Collect all agent results
    agent_results = {}
    for result_file in results_path.glob("agent*_results.json"):
        with open(result_file) as f:
            data = json.load(f)
            agent_id = data.get("agent_id", "unknown")
            agent_results[f"agent_{agent_id}"] = data
    
    # Calculate overall status
    status = {
        "monitoring_timestamp": datetime.now().isoformat(),
        "real_time_mode": real_time,
        "total_agents": len(agent_results),
        "agent_statuses": {},
        "overall_metrics": {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_success_rate": 0,
            "total_execution_time": 0
        }
    }
    
    # Process each agent's results
    for agent_key, agent_data in agent_results.items():
        agent_id = agent_data.get("agent_id")
        
        status["agent_statuses"][agent_key] = {
            "agent_id": agent_id,
            "agent_name": agent_data.get("agent_name"),
            "tasks_received": agent_data.get("tasks_received", 0),
            "tasks_completed": agent_data.get("tasks_completed", 0),
            "tasks_failed": agent_data.get("tasks_failed", 0),
            "success_rate": agent_data.get("success_rate", 0),
            "status": "completed" if agent_data.get("tasks_completed") == agent_data.get("tasks_received") else "in_progress"
        }
        
        # Update overall metrics
        status["overall_metrics"]["total_tasks"] += agent_data.get("tasks_received", 0)
        status["overall_metrics"]["completed_tasks"] += agent_data.get("tasks_completed", 0)
        status["overall_metrics"]["failed_tasks"] += agent_data.get("tasks_failed", 0)
        
        # Sum execution times
        for task_result in agent_data.get("task_results", []):
            status["overall_metrics"]["total_execution_time"] += task_result.get("execution_time_seconds", 0)
    
    # Calculate average success rate
    if status["total_agents"] > 0:
        total_success_rate = sum(
            agent_status["success_rate"]
            for agent_status in status["agent_statuses"].values()
        )
        status["overall_metrics"]["average_success_rate"] = total_success_rate / status["total_agents"]
    
    # Overall execution status
    all_completed = all(
        agent_status["status"] == "completed"
        for agent_status in status["agent_statuses"].values()
    )
    status["overall_status"] = "completed" if all_completed else "in_progress"
    
    # Save monitoring data
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"✅ Execution monitoring complete")
    print(f"   Overall status: {status['overall_status']}")
    print(f"   Agents monitored: {status['total_agents']}")
    print(f"   Total tasks: {status['overall_metrics']['total_tasks']}")
    print(f"   Completed: {status['overall_metrics']['completed_tasks']}")
    print(f"   Average success rate: {status['overall_metrics']['average_success_rate']:.1%}")
    
    return status


def main():
    parser = argparse.ArgumentParser(description="Monitor execution status")
    parser.add_argument("--results", required=True, help="Directory with agent results")
    parser.add_argument("--output", required=True, help="Output path")
    parser.add_argument("--real-time", action="store_true", help="Enable real-time monitoring")
    args = parser.parse_args()
    
    monitor_execution(args.results, args.output, args.real_time)


if __name__ == "__main__":
    main()
