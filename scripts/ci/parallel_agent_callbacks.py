#!/usr/bin/env python3
"""
Callback Aggregator for Parallel Agent Delegation

Collects and coalesces results from N agents executing in parallel.
Enables fire-and-forget delegation without waiting for serial completion.

Usage:
    python scripts/ci/parallel_agent_callbacks.py --init
    python scripts/ci/parallel_agent_callbacks.py --register agent-id-1
    python scripts/ci/parallel_agent_callbacks.py --collect agent-id-1 result.json
    python scripts/ci/parallel_agent_callbacks.py --status  # Show all in-flight
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class CallbackAggregator:
    """Aggregates results from parallel agent executions."""

    def __init__(self, registry_path: Path = None):
        """Initialize aggregator with callback registry."""
        self.registry_path = registry_path or Path(".codex/agent_callbacks.json")
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry: Dict[str, Any] = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Load or initialize callback registry."""
        if self.registry_path.exists():
            with open(self.registry_path) as f:
                return json.load(f)
        return {"timestamp": datetime.now(timezone.utc).isoformat(), "agents": {}, "completed": []}

    def _save_registry(self) -> None:
        """Persist registry to disk."""
        with open(self.registry_path, "w") as f:
            json.dump(self.registry, f, indent=2)

    def register_agent(self, agent_id: str, expected_outputs: Optional[List[str]] = None) -> Dict[str, Any]:
        """Register a new agent for parallel execution tracking."""
        entry = {
            "agent_id": agent_id,
            "registered_at": datetime.now(timezone.utc).isoformat(),
            "status": "running",
            "expected_outputs": expected_outputs or [],
            "received_outputs": [],
            "error": None,
        }
        self.registry["agents"][agent_id] = entry
        self._save_registry()
        return entry

    def record_result(self, agent_id: str, result_file: Path) -> Dict[str, Any]:
        """Record a result callback from an agent."""
        if agent_id not in self.registry["agents"]:
            return {"error": f"Agent {agent_id} not registered"}

        result_file = Path(result_file)
        if not result_file.exists():
            return {"error": f"Result file not found: {result_file}"}

        try:
            with open(result_file) as f:
                result_data = json.load(f)

            agent_entry = self.registry["agents"][agent_id]
            agent_entry["received_outputs"].append(
                {
                    "file": str(result_file),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "size_kb": result_file.stat().st_size / 1024,
                    "keys": list(result_data.keys()) if isinstance(result_data, dict) else None,
                }
            )
            agent_entry["status"] = "completed"
            self._save_registry()
            return {"status": "recorded", "agent_id": agent_id}
        except Exception as e:
            agent_entry = self.registry["agents"][agent_id]
            agent_entry["error"] = str(e)
            agent_entry["status"] = "failed"
            self._save_registry()
            return {"error": str(e), "agent_id": agent_id}

    def get_status(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Get status of agent(s)."""
        if agent_id:
            return self.registry["agents"].get(agent_id, {"error": "Not found"})

        # Summary across all agents
        total = len(self.registry["agents"])
        completed = sum(
            1 for a in self.registry["agents"].values() if a.get("status") == "completed"
        )
        failed = sum(1 for a in self.registry["agents"].values() if a.get("status") == "failed")

        return {
            "total_agents": total,
            "completed": completed,
            "running": total - completed - failed,
            "failed": failed,
            "agents": self.registry["agents"],
        }

    def coalesce_results(self, agent_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """Coalesce results from completed agents into unified output."""
        if agent_ids is None:
            agent_ids = list(self.registry["agents"].keys())

        coalesced = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "agents_processed": len(agent_ids),
            "combined_results": {},
            "errors": [],
        }

        for agent_id in agent_ids:
            agent_entry = self.registry["agents"].get(agent_id)
            if not agent_entry:
                coalesced["errors"].append(f"Agent {agent_id} not found")
                continue

            if agent_entry.get("status") != "completed":
                coalesced["errors"].append(
                    f"Agent {agent_id} not complete (status: {agent_entry.get('status')})"
                )
                continue

            # Try to load and merge results
            for output in agent_entry.get("received_outputs", []):
                try:
                    result_file = Path(output["file"])
                    if result_file.exists():
                        with open(result_file) as f:
                            data = json.load(f)
                            coalesced["combined_results"][agent_id] = data
                except Exception as e:
                    coalesced["errors"].append(f"Failed to load {agent_id} results: {str(e)}")

        return coalesced

    def mark_completed(self, agent_id: str) -> Dict[str, Any]:
        """Mark an agent as completed."""
        if agent_id not in self.registry["agents"]:
            return {"error": f"Agent {agent_id} not registered"}

        self.registry["agents"][agent_id]["status"] = "completed"
        self.registry["agents"][agent_id]["completed_at"] = datetime.now(timezone.utc).isoformat()
        self._save_registry()
        return {"status": "marked_complete", "agent_id": agent_id}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Parallel Agent Callback Aggregator")
    parser.add_argument(
        "--registry",
        default=".codex/agent_callbacks.json",
        help="Callback registry path",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Initialize command
    subparsers.add_parser("init", help="Initialize callback registry")

    # Register command
    register_parser = subparsers.add_parser("register", help="Register an agent")
    register_parser.add_argument("agent_id", help="Agent identifier")
    register_parser.add_argument(
        "--outputs",
        nargs="*",
        help="Expected output files",
    )

    # Collect command
    collect_parser = subparsers.add_parser("collect", help="Record a result callback")
    collect_parser.add_argument("agent_id", help="Agent identifier")
    collect_parser.add_argument("result_file", help="Result file path")

    # Status command
    status_parser = subparsers.add_parser("status", help="Show aggregation status")
    status_parser.add_argument(
        "--agent",
        help="Specific agent to query",
    )

    # Coalesce command
    coalesce_parser = subparsers.add_parser("coalesce", help="Coalesce completed results")
    coalesce_parser.add_argument(
        "--agents",
        nargs="*",
        help="Specific agents to coalesce (default: all)",
    )
    coalesce_parser.add_argument(
        "--output",
        help="Output file for coalesced results",
    )

    # Mark complete command
    complete_parser = subparsers.add_parser("complete", help="Mark agent as completed")
    complete_parser.add_argument("agent_id", help="Agent identifier")

    args = parser.parse_args()

    aggregator = CallbackAggregator(registry_path=Path(args.registry))

    if args.command == "init":
        aggregator._save_registry()
        print("✅ Callback registry initialized", file=sys.stderr)
        return 0

    elif args.command == "register":
        result = aggregator.register_agent(args.agent_id, args.outputs)
        print(json.dumps(result, indent=2))
        return 0

    elif args.command == "collect":
        result = aggregator.record_result(args.agent_id, args.result_file)
        if "error" in result:
            print(json.dumps(result, indent=2), file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2))
        return 0

    elif args.command == "status":
        result = aggregator.get_status(args.agent)
        print(json.dumps(result, indent=2))
        return 0

    elif args.command == "coalesce":
        result = aggregator.coalesce_results(args.agents)
        output_data = json.dumps(result, indent=2)

        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                f.write(output_data)
            print(f"✅ Coalesced results saved: {args.output}", file=sys.stderr)
        else:
            print(output_data)

        return 0

    elif args.command == "complete":
        result = aggregator.mark_completed(args.agent_id)
        if "error" in result:
            print(json.dumps(result, indent=2), file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2))
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
