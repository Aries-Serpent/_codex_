#!/usr/bin/env python3
"""
Adaptive Agent Delegation Framework

Semantic capability matching and parallel agent delegation based on aggregated context.
Enables fire-and-forget delegation with dependency tracking and result coalescing.

Usage:
    python scripts/ci/adaptive_agent_delegation.py --context .codex/session_context_manifest.json
    python scripts/ci/adaptive_agent_delegation.py --suggest-agents --problem "CI failures in coverage"
    python scripts/ci/adaptive_agent_delegation.py --delegate-parallel --agents agent1,agent2,agent3
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class AgentCapability:
    """Describes what an agent can do."""

    agent_id: str
    name: str
    category: str
    autonomy_model: str
    tags: List[str]
    success_criteria: List[str]
    estimated_duration_minutes: int
    fallback_agents: Optional[List[str]] = None


class AdaptiveAgentDelegator:
    """Semantic capability matching and adaptive delegation."""

    # Hardcoded capability map (would be loaded from AGENT_REGISTRY in production)
    CAPABILITY_MAP = {
        "unified-coverage-agent": AgentCapability(
            agent_id="unified-coverage-agent",
            name="Unified Coverage Agent",
            category="testing",
            autonomy_model="D_CAPABLE",
            tags=["coverage", "testing", "gap-fill", "maintenance", "roadmap"],
            success_criteria=["coverage_increased", "tests_passing", "no_regressions"],
            estimated_duration_minutes=45,
            fallback_agents=["test-enhancement-agent", "coverage-gapfill-agent"],
        ),
        "ci-failure-resolution-agent": AgentCapability(
            agent_id="ci-failure-resolution-agent",
            name="CI Failure Resolution Agent",
            category="ci",
            autonomy_model="D_CAPABLE",
            tags=["ci", "failures", "debugging", "logs", "patterns"],
            success_criteria=["failures_resolved", "root_cause_found", "fix_validated"],
            estimated_duration_minutes=30,
            fallback_agents=["ci-emergency-response-agent", "ci-testing-agent"],
        ),
        "unified-doc-agent": AgentCapability(
            agent_id="unified-doc-agent",
            name="Unified Doc Agent",
            category="documentation",
            autonomy_model="E_ADVISORY",
            tags=["docs", "consolidation", "freshness", "links", "quality"],
            success_criteria=["docs_updated", "links_valid", "no_broken_refs"],
            estimated_duration_minutes=40,
            fallback_agents=["doc-freshness-checker", "link-validator-agent"],
        ),
        "unified-security-scanner": AgentCapability(
            agent_id="unified-security-scanner",
            name="Unified Security Scanner",
            category="security",
            autonomy_model="D_CAPABLE",
            tags=["security", "vulnerabilities", "secrets", "dependencies", "sast"],
            success_criteria=["vulns_fixed", "secrets_not_committed", "deps_safe"],
            estimated_duration_minutes=35,
            fallback_agents=["code-scanning-remediation-agent", "secret-detection-agent"],
        ),
        "autonomous-test-healer-agent": AgentCapability(
            agent_id="autonomous-test-healer-agent",
            name="Autonomous Test Healer",
            category="testing",
            autonomy_model="D_CAPABLE",
            tags=["tests", "failures", "flaky", "healing", "stabilization"],
            success_criteria=["tests_fixed", "flakiness_reduced", "no_new_failures"],
            estimated_duration_minutes=25,
            fallback_agents=["test-failure-analyzer-agent", "fragile-test-guardian"],
        ),
        "self-healing-orchestrator-agent": AgentCapability(
            agent_id="self-healing-orchestrator-agent",
            name="Self-Healing Orchestrator",
            category="orchestration",
            autonomy_model="D_CAPABLE",
            tags=["orchestration", "cascades", "patterns", "coordination", "multi-agent"],
            success_criteria=["cascade_completed", "all_patterns_handled", "no_conflicts"],
            estimated_duration_minutes=60,
            fallback_agents=["agent-orchestrator", "ci-triage-pipeline-agent"],
        ),
    }

    def __init__(self, context_manifest: Optional[Dict[str, Any]] = None):
        """Initialize delegator with context."""
        self.context = context_manifest or {}
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.delegation_plan: Dict[str, Any] = {
            "timestamp": self.timestamp,
            "context_based": True,
            "suggested_agents": [],
            "dependency_graph": {},
            "parallel_batches": [],
        }

    def load_context_manifest(self, manifest_path: Path) -> Dict[str, Any]:
        """Load aggregated context from manifest."""
        with open(manifest_path) as f:
            self.context = json.load(f)
        return self.context

    def suggest_agents(self, problem_description: str) -> List[AgentCapability]:
        """Suggest agents based on problem description (keyword matching)."""
        keywords = problem_description.lower().split()
        scored_agents: Dict[str, int] = {}

        for agent_id, capability in self.CAPABILITY_MAP.items():
            score = 0
            # Match against tags
            for tag in capability.tags:
                if tag in keywords:
                    score += 3
            # Match against category
            if capability.category in problem_description.lower():
                score += 2
            # Match against name
            if capability.name.lower() in problem_description.lower():
                score += 2

            if score > 0:
                scored_agents[agent_id] = score

        # Sort by score and return
        sorted_agents = sorted(scored_agents.items(), key=lambda x: x[1], reverse=True)
        return [self.CAPABILITY_MAP[agent_id] for agent_id, _ in sorted_agents[:3]]

    def suggest_agents_from_context(self) -> List[AgentCapability]:
        """Suggest agents based on aggregated context."""
        recommendations: Set[str] = set()

        # Check phase status
        phase_info = self.context.get("sources", {}).get("phase_tracking", {})
        if phase_info.get("phase_2_1_status") == "COMPLETE":
            recommendations.add("unified-governance-gate")  # Would need to be in map

        # Check for CI failures
        if self.context.get("aggregation_summary", {}).get("recommendations"):
            recommendations.add("ci-failure-resolution-agent")

        # Check coverage status
        if "coverage" in str(self.context).lower():
            recommendations.add("unified-coverage-agent")

        # Check for security issues
        if any(
            k in str(self.context).lower() for k in ["security", "vulnerability", "secret"]
        ):
            recommendations.add("unified-security-scanner")

        # Return capabilities for recommended agents
        return [
            self.CAPABILITY_MAP[agent_id]
            for agent_id in recommendations
            if agent_id in self.CAPABILITY_MAP
        ]

    def build_delegation_plan(
        self, agents: List[AgentCapability], dependencies: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """Build parallel delegation plan with dependency tracking."""
        plan = {
            "timestamp": self.timestamp,
            "agents": [asdict(a) for a in agents],
            "dependencies": dependencies or {},
            "execution_strategy": "parallel_with_dependencies",
        }

        # Build parallel batches (topological sort)
        executed: Set[str] = set()
        batches: List[List[str]] = []

        while len(executed) < len(agents):
            batch: List[str] = []
            for agent in agents:
                if agent.agent_id in executed:
                    continue

                # Check if dependencies are met
                agent_deps = (dependencies or {}).get(agent.agent_id, [])
                if all(dep in executed for dep in agent_deps):
                    batch.append(agent.agent_id)

            if not batch:
                # Circular dependency or no progress
                batch = [a.agent_id for a in agents if a.agent_id not in executed]

            batches.append(batch)
            executed.update(batch)

        plan["parallel_batches"] = batches
        plan["estimated_total_minutes"] = sum(
            max(
                self.CAPABILITY_MAP[agent_id].estimated_duration_minutes
                for agent_id in batch
                if agent_id in self.CAPABILITY_MAP
            )
            for batch in batches
        )

        return plan

    def recommend_delegation_order(self) -> List[List[str]]:
        """Recommend order of agent delegation (parallel batches)."""
        suggested = self.suggest_agents_from_context()
        plan = self.build_delegation_plan(suggested)
        return plan.get("parallel_batches", [])

    def get_fallback_chain(self, primary_agent: str) -> List[str]:
        """Get fallback agent chain for a primary agent."""
        capability = self.CAPABILITY_MAP.get(primary_agent)
        if not capability or not capability.fallback_agents:
            return []
        return capability.fallback_agents


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Adaptive Agent Delegation Framework")
    parser.add_argument(
        "--context",
        help="Path to context manifest JSON",
    )
    parser.add_argument(
        "--problem",
        help="Problem description for agent suggestion",
    )
    parser.add_argument(
        "--suggest-agents",
        action="store_true",
        help="Get suggested agents",
    )
    parser.add_argument(
        "--recommend-order",
        action="store_true",
        help="Recommend delegation order",
    )
    parser.add_argument(
        "--output",
        help="Output file for delegation plan",
    )

    args = parser.parse_args()

    delegator = AdaptiveAgentDelegator()

    if args.context:
        delegator.load_context_manifest(Path(args.context))

    if args.problem and args.suggest_agents:
        agents = delegator.suggest_agents(args.problem)
        output = json.dumps([asdict(a) for a in agents], indent=2)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        return 0

    if args.recommend_order:
        batches = delegator.recommend_delegation_order()
        output = json.dumps({"parallel_batches": batches}, indent=2)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        return 0

    if args.suggest_agents:
        agents = delegator.suggest_agents_from_context()
        output = json.dumps([asdict(a) for a in agents], indent=2)
        if args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w") as f:
                f.write(output)
        else:
            print(output)
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
