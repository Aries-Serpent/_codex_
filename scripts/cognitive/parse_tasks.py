#!/usr/bin/env python3
"""
Parse Tasks

Purpose:
    Command-line utility (see argument parser for details)

Usage:
    python scripts/cognitive/parse_tasks.py [options]

    Examples:
    $ python scripts/cognitive/parse_tasks.py --help

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
from pathlib import Path
from typing import Any, Dict


def parse_tasks(allocation_path: str, output_path: str) -> Dict[str, Any]:
    """
    Parse task allocation into execution-ready format.

    Args:
        allocation_path: Path to task_allocation.json
        output_path: Path to save parsed tasks

    Returns:
        Parsed task structure
    """
    # Load allocation
    with open(allocation_path) as f:
        allocation = json.load(f)

    # Parse into execution format
    parsed = {
        "parsing_timestamp": allocation.get("allocation_timestamp"),
        "agents": {}
    }

    for agent_id, agent_data in allocation.get("task_allocations", {}).items():
        parsed["agents"][agent_id] = {
            "agent_name": agent_data["agent_name"],
            "seed": agent_data["seed"],
            "tasks": agent_data["tasks"],
            "task_count": agent_data["total_tasks"],
            "status": "pending"
        }

    # Save parsed tasks
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(parsed, f, indent=2)

    print(f"✅ Parsed {len(parsed['agents'])} agents with tasks")
    return parsed


def main():
    parser = argparse.ArgumentParser(description="Parse task allocation")
    parser.add_argument("--allocation", required=True, help="Task allocation JSON")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    parse_tasks(args.allocation, args.output)


if __name__ == "__main__":
    main()
