#!/usr/bin/env python3
"""
Agent Orchestrator - Routes failures and tasks to specialized custom agents.

This module:
- Routes failures to appropriate specialized agents based on category
- Routes general tasks to agents via keyword→agent classification (PS-13)
- Invokes agents with failure context
- Aggregates recommendations from multiple agents
- Manages agent timeouts and retries

Usage:
    from scripts.monitoring.agent_orchestrator import AgentOrchestrator, TaskRouter

    orchestrator = AgentOrchestrator(config)
    recommendations = orchestrator.route_failure(failure_data)

    router = TaskRouter()
    result = router.route_task("fix the CI test failures")

Author: Artifact Monitor Agent
Version: 2.0.0
Created: 2026-01-22
Updated: 2026-02-12 (PS-13: Agent Task Router)
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Orchestrates routing of failures to specialized agents."""

    def __init__(self, config: Dict[str, Any], dry_run: bool = False):
        """
        Initialize agent orchestrator.

        Args:
            config: Monitoring configuration
            dry_run: If True, simulate agent invocation
        """
        self.config = config
        self.dry_run = dry_run
        self.agent_routing_config = config['monitoring']['agent_routing']
        self.routing_map = self.agent_routing_config['routing_map']

        logger.info(f"AgentOrchestrator initialized, dry_run={dry_run}")

    def route_failure(
        self,
        failure_data: Dict[str, Any],
        pattern_matches: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Route failure to appropriate specialized agents.

        Args:
            failure_data: Failure information (workflow, run, metrics)
            pattern_matches: List of matched error patterns

        Returns:
            List of agent recommendations
        """
        if not self.agent_routing_config['enabled']:
            logger.info("Agent routing is disabled")
            return []

        # Determine which agents to invoke
        agents_to_invoke = self._select_agents(failure_data, pattern_matches)

        if not agents_to_invoke:
            logger.warning("No agents selected for routing")
            return []

        # Limit number of agents
        max_agents = self.agent_routing_config['max_agents_per_failure']
        agents_to_invoke = agents_to_invoke[:max_agents]

        logger.info(f"Routing failure to {len(agents_to_invoke)} agents: {agents_to_invoke}")

        # Invoke each agent
        recommendations = []
        for agent_name in agents_to_invoke:
            try:
                recommendation = self._invoke_agent(agent_name, failure_data, pattern_matches)
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Failed to invoke agent {agent_name}: {e}")

        return recommendations

    def _select_agents(
        self,
        failure_data: Dict[str, Any],
        pattern_matches: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Select which agents should be invoked based on patterns.

        Args:
            failure_data: Failure information
            pattern_matches: Matched patterns

        Returns:
            List of agent names to invoke
        """
        agents = []
        confidence_threshold = self.agent_routing_config['confidence_threshold']

        # Get agents from high-confidence patterns
        for match in pattern_matches:
            if match.get('confidence', 0) >= confidence_threshold:
                # Check if pattern specifies an agent
                agent = match.get('agent')
                if agent and agent not in agents:
                    agents.append(agent)

                # Also check routing map for category
                category = match.get('category')
                if category and category in self.routing_map:
                    mapped_agent = self.routing_map[category]
                    if mapped_agent not in agents:
                        agents.append(mapped_agent)

        # If no agents selected, use default (ci-testing-agent)
        if not agents:
            default_agent = 'ci-testing-agent'
            logger.info(f"No specific agents matched, using default: {default_agent}")
            agents.append(default_agent)

        return agents

    def _invoke_agent(
        self,
        agent_name: str,
        failure_data: Dict[str, Any],
        pattern_matches: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Invoke a specialized agent with failure context.

        Args:
            agent_name: Name of the agent to invoke
            failure_data: Failure information
            pattern_matches: Matched patterns

        Returns:
            Agent recommendation or None
        """
        # Load agent definition — prefer .agent.md to avoid shadowing by deprecated .md files
        agent_path = Path(f'.github/agents/{agent_name}.agent.md')
        if not agent_path.exists():
            agent_path = Path(f'.github/agents/{agent_name}.agent.yml')
            if not agent_path.exists():
                agent_path = Path(f'.github/agents/{agent_name}.md')
                if not agent_path.exists():
                    logger.warning(f"Agent definition not found: {agent_name}")
                    return self._generate_fallback_recommendation(agent_name, failure_data, pattern_matches)

        # Read agent definition
        try:
            with open(agent_path) as f:
                agent_definition = f.read()
            logger.debug(
                "Loaded agent definition for %s from %s (length=%d)",
                agent_name,
                agent_path,
                len(agent_definition),
            )
        except Exception as e:
            logger.error(f"Failed to read agent definition {agent_path}: {e}")
            return None

        # Check for deprecated front-matter and redirect to superseded_by agent
        canonical_name = self._resolve_canonical_agent(agent_name, agent_definition)
        if canonical_name and canonical_name != agent_name:
            logger.info(
                "Agent '%s' is deprecated, redirecting to canonical agent '%s'",
                agent_name,
                canonical_name,
            )
            return self._invoke_agent(canonical_name, failure_data, pattern_matches)

        # In dry-run mode or for this implementation,
        # generate simulated recommendations based on patterns
        if self.dry_run:
            logger.info(f"[DRY-RUN] Would invoke agent: {agent_name}")
            return self._generate_simulated_recommendation(agent_name, failure_data, pattern_matches)

        # For now, generate recommendations based on patterns
        # In a full implementation, this would invoke the actual agent
        # through subprocess, API, or GitHub Copilot mechanism
        return self._generate_recommendation_from_patterns(agent_name, failure_data, pattern_matches)

    def _resolve_canonical_agent(
        self, agent_name: str, agent_definition: str
    ) -> Optional[str]:
        """Parse YAML front-matter to detect deprecated agents and return canonical name.

        When an agent definition contains ``deprecated: true`` and a
        ``superseded_by`` field in its YAML front-matter, this method returns
        the name of the canonical agent so the caller can redirect.  The
        ``superseded_by`` value may include a version/date suffix
        (e.g. ``unified-governance-gate.md (v1.0.0-m05, 2026-02-22)``); only
        the base filename stem is extracted.

        Args:
            agent_name: Name of the agent that was originally requested.
            agent_definition: Raw file contents (may start with ``---`` front-matter).

        Returns:
            Canonical agent name to redirect to, or ``None`` if the agent is
            not deprecated / no redirect is needed.
        """
        # Only inspect YAML front-matter (between the first pair of ``---`` delimiters).
        # Use \s* (zero or more) to tolerate CRLF line endings, empty front-matter,
        # and varying whitespace around the --- delimiters.
        fm_match = re.match(r'^---\s*(.*?)\s*---', agent_definition, re.DOTALL)
        if not fm_match:
            return None
        front_matter = fm_match.group(1)

        # Check for deprecated: true (YAML convention is lowercase; reject any other case)
        if not re.search(r'^\s*deprecated\s*:\s*true\s*$', front_matter, re.MULTILINE):
            return None

        # Extract superseded_by value (take only the first word/token before space/paren)
        sb_match = re.search(r'^\s*superseded_by\s*:\s*(.+)$', front_matter, re.MULTILINE)
        if not sb_match:
            return None
        superseded_raw = sb_match.group(1).strip()
        # Strip optional version suffix like " (v1.0.0-m05, 2026-02-22)" and ".md" extension
        canonical = re.split(r'[\s(]', superseded_raw)[0]
        canonical = re.sub(r'\.(?:agent\.)?md$', '', canonical)
        if canonical and canonical != agent_name:
            return canonical
        return None


    def _generate_recommendation_from_patterns(
        self,
        agent_name: str,
        failure_data: Dict[str, Any],
        pattern_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate agent recommendation based on matched patterns.

        Args:
            agent_name: Name of the agent
            failure_data: Failure information
            pattern_matches: Matched patterns

        Returns:
            Recommendation dictionary
        """
        workflow_name = failure_data['workflow_name']

        # Use top pattern match if available
        if pattern_matches:
            top_match = pattern_matches[0]
            confidence = top_match.get('confidence', 0.7)
            root_cause = top_match.get('description', 'Unknown root cause')
            suggested_fix = top_match.get('suggestion', 'No specific suggestion available')

            actions = [suggested_fix]

            # Add category-specific recommendations
            category = top_match.get('category')
            if category == 'dependency':
                actions.append("Review requirements.txt and pyproject.toml for version conflicts")
                actions.append("Check if dependency is in GitHub Actions cache")
            elif category == 'test':
                actions.append("Run tests locally to reproduce the failure")
                actions.append("Check for non-deterministic behavior or timing issues")
            elif category == 'coverage':
                actions.append("Add tests to increase coverage for uncovered modules")
                actions.append("Review coverage threshold configuration")
        else:
            confidence = 0.5
            root_cause = "No specific pattern matched - manual investigation required"
            suggested_fix = f"Review workflow logs for {workflow_name}"
            actions = [
                "Check workflow logs for error messages",
                "Compare with previous successful runs",
                "Review recent code changes"
            ]

        recommendation = {
            'agent': agent_name,
            'workflow': workflow_name,
            'confidence': confidence,
            'root_cause': root_cause,
            'suggested_fix': suggested_fix,
            'recommended_actions': actions,
            'timestamp': failure_data.get('run').created_at.isoformat() if failure_data.get('run') else None
        }

        logger.info(f"Generated recommendation from {agent_name} (confidence: {confidence:.2f})")
        return recommendation

    def _generate_simulated_recommendation(
        self,
        agent_name: str,
        failure_data: Dict[str, Any],
        pattern_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate simulated recommendation for dry-run mode."""
        return self._generate_recommendation_from_patterns(agent_name, failure_data, pattern_matches)

    def _generate_fallback_recommendation(
        self,
        agent_name: str,
        failure_data: Dict[str, Any],
        pattern_matches: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate fallback recommendation when agent not found."""
        workflow_name = failure_data['workflow_name']

        return {
            'agent': agent_name,
            'workflow': workflow_name,
            'confidence': 0.5,
            'root_cause': f"Agent {agent_name} not available - fallback analysis",
            'suggested_fix': f"Manual investigation required for {workflow_name}",
            'recommended_actions': [
                "Review workflow logs manually",
                "Check recent code changes",
                "Compare with successful runs"
            ],
            'note': f"Agent {agent_name} definition not found, using fallback"
        }

    def aggregate_recommendations(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Aggregate recommendations from multiple agents.

        Args:
            recommendations: List of agent recommendations

        Returns:
            Aggregated recommendation
        """
        if not recommendations:
            return {
                'overall_confidence': 0.0,
                'primary_root_cause': 'Unknown',
                'recommended_actions': [],
                'agents_consulted': []
            }

        # Calculate overall confidence (weighted average)
        total_confidence = sum(r.get('confidence', 0) for r in recommendations)
        overall_confidence = total_confidence / len(recommendations)

        # Use highest confidence recommendation as primary
        recommendations_sorted = sorted(
            recommendations,
            key=lambda r: r.get('confidence', 0),
            reverse=True
        )
        primary = recommendations_sorted[0]

        # Aggregate all unique actions
        all_actions = []
        for rec in recommendations:
            for action in rec.get('recommended_actions', []):
                if action not in all_actions:
                    all_actions.append(action)

        # Get all consulted agents
        agents_consulted = [r.get('agent') for r in recommendations]

        aggregated = {
            'overall_confidence': overall_confidence,
            'primary_root_cause': primary.get('root_cause'),
            'primary_suggested_fix': primary.get('suggested_fix'),
            'recommended_actions': all_actions,
            'agents_consulted': agents_consulted,
            'detailed_recommendations': recommendations
        }

        logger.info(
            f"Aggregated {len(recommendations)} recommendations "
            f"(confidence: {overall_confidence:.2f})"
        )

        return aggregated

    def generate_agent_analysis_section(
        self,
        recommendations: List[Dict[str, Any]]
    ) -> str:
        """
        Generate formatted agent analysis section for issue body.

        Args:
            recommendations: List of agent recommendations

        Returns:
            Markdown formatted agent analysis
        """
        if not recommendations:
            return "_No agent analysis available. Manual investigation required._"

        section = ""

        for i, rec in enumerate(recommendations, 1):
            agent = rec.get('agent', 'Unknown Agent')
            confidence = rec.get('confidence', 0) * 100

            section += f"### {i}. {agent.replace('-', ' ').title()} Analysis\n"
            section += f"**Confidence**: {confidence:.0f}%\n\n"

            if rec.get('root_cause'):
                section += f"**Root Cause**: {rec['root_cause']}\n\n"

            if rec.get('suggested_fix'):
                section += f"**Suggested Fix**: {rec['suggested_fix']}\n\n"

            if rec.get('recommended_actions'):
                section += "**Recommended Actions**:\n"
                for action in rec['recommended_actions']:
                    section += f"- {action}\n"
                section += "\n"

            section += "---\n\n"

        # Add aggregated summary
        aggregated = self.aggregate_recommendations(recommendations)
        section += "### Overall Assessment\n"
        section += f"**Overall Confidence**: {aggregated['overall_confidence'] * 100:.0f}%\n"
        section += f"**Agents Consulted**: {', '.join(aggregated['agents_consulted'])}\n"

        return section


# --- PS-13: Agent Task Router (L4 Automatic Classification) ---

# Task classification taxonomy: 7 categories with keyword→agent mappings.
# Each category maps keywords to an ordered list of agents (primary + fallbacks).
TASK_ROUTING_TABLE: Dict[str, Dict[str, Any]] = {
    "ci_cd": {
        "keywords": [
            "ci", "cd", "pipeline", "workflow", "build", "deploy", "github actions",
            "workflow failure", "build failure", "ci failure", "action",
        ],
        "agents": ["ci-testing-agent", "ci-emergency-response-agent", "workflow-ci-fixer"],
        "description": "CI/CD pipeline issues, workflow failures, build problems",
    },
    "testing": {
        "keywords": [
            "test", "pytest", "unittest", "coverage", "assertion", "fixture",
            "test failure", "flaky test", "test coverage", "mutation test",
        ],
        "agents": ["ci-testing-agent", "coverage-gapfill-agent", "test-alignment-fixer"],
        "description": "Test failures, coverage gaps, test quality issues",
    },
    "security": {
        "keywords": [
            "security", "vulnerability", "cve", "secret", "credential", "token",
            "codeql", "semgrep", "sast", "pii", "injection", "xss",
        ],
        "agents": ["security-alert-verification-agent", "code-scanning-remediation-agent", "pii-scrubber"],
        "description": "Security vulnerabilities, secret scanning, code scanning alerts",
    },
    "documentation": {
        "keywords": [
            "doc", "documentation", "readme", "mkdocs", "link", "markdown",
            "stale doc", "broken link", "api doc",
        ],
        "agents": ["documentation-quality-agent", "doc-freshness-checker", "link-validator-agent"],
        "description": "Documentation quality, freshness, link validation",
    },
    "rag_ml": {
        "keywords": [
            "rag", "embedding", "model", "tensor", "torch", "training",
            "sentence transformer", "indexer", "retriever", "meta tensor",
        ],
        "agents": ["meta-tensor-validator", "rag-index-manager", "rag-meta-tensor-regression-agent"],
        "description": "RAG pipeline, ML model initialization, tensor handling",
    },
    "configuration": {
        "keywords": [
            "config", "configuration", "hydra", "yaml", "settings", "migration",
            "environment", "variable",
        ],
        "agents": ["config-validator", "config-migration-assistant"],
        "description": "Configuration management, Hydra configs, settings validation",
    },
    "repository": {
        "keywords": [
            "repo", "repository", "cleanup", "hygiene", "organize", "refactor",
            "dependency", "import", "lint", "format", "style",
        ],
        "agents": ["repository-hygiene-agent", "dependency-conflict-agent", "root-organizer-agent"],
        "description": "Repository maintenance, dependency management, code quality",
    },
}


class TaskRouter:
    """Routes tasks to specialized agents based on keyword classification.

    Implements PS-13 Agent Task Router (L4 Automatic Classification).
    Uses keyword matching against a task classification taxonomy to select
    the best agent with confidence scoring and fallback chains.

    Usage::

        router = TaskRouter()
        result = router.route_task("fix the CI test failures in pytest")
        print(result["agent"])       # "ci-testing-agent"
        print(result["confidence"])  # 0.85
        print(result["category"])    # "testing"
    """

    def __init__(
        self,
        routing_table: Optional[Dict[str, Dict[str, Any]]] = None,
        default_agent: str = "ci-testing-agent",
        confidence_threshold: float = 0.3,
    ):
        """Initialize the task router.

        Args:
            routing_table: Custom routing table (defaults to TASK_ROUTING_TABLE).
            default_agent: Agent to use when no keywords match.
            confidence_threshold: Minimum confidence to select a category.
        """
        self.routing_table = routing_table or TASK_ROUTING_TABLE
        self.default_agent = default_agent
        self.confidence_threshold = confidence_threshold

    def route_task(self, task_description: str) -> Dict[str, Any]:
        """Route a task description to the best-matching agent.

        Tokenizes the task description, scores each category by keyword
        overlap, and returns the top agent with confidence and fallbacks.

        Args:
            task_description: Free-text description of the task.

        Returns:
            Dictionary with keys: agent, category, confidence, fallbacks,
            description, all_scores.
        """
        scores = self._score_categories(task_description)

        if not scores or scores[0][1] < self.confidence_threshold:
            return {
                "agent": self.default_agent,
                "category": "general",
                "confidence": 0.0,
                "fallbacks": [],
                "description": "No specific category matched — using default agent",
                "all_scores": scores,
            }

        top_category, top_score = scores[0]
        entry = self.routing_table[top_category]

        return {
            "agent": entry["agents"][0],
            "category": top_category,
            "confidence": top_score,
            "fallbacks": entry["agents"][1:],
            "description": entry["description"],
            "all_scores": scores,
        }

    def _score_categories(
        self, task_description: str
    ) -> List[tuple]:
        """Score every category by keyword match ratio.

        Returns a list of ``(category, score)`` tuples sorted descending by
        score.  Score is the fraction of the category's keywords found in the
        lowercased task description.
        """
        text = task_description.lower()
        scores: List[tuple] = []

        for category, entry in self.routing_table.items():
            keywords = entry["keywords"]
            matches = sum(1 for kw in keywords if kw in text)
            score = matches / len(keywords) if keywords else 0.0
            if score > 0:
                scores.append((category, round(score, 4)))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

    def list_categories(self) -> List[Dict[str, Any]]:
        """Return a summary of all routing categories.

        Returns:
            List of dicts with category, description, agent_count, keywords_count.
        """
        return [
            {
                "category": cat,
                "description": entry["description"],
                "primary_agent": entry["agents"][0],
                "agent_count": len(entry["agents"]),
                "keywords_count": len(entry["keywords"]),
            }
            for cat, entry in self.routing_table.items()
        ]


def route_task(task_description: str, **kwargs: Any) -> Dict[str, Any]:
    """Convenience function — creates a TaskRouter and routes a single task.

    Args:
        task_description: Free-text description of the task.
        **kwargs: Forwarded to ``TaskRouter.__init__``.

    Returns:
        Routing result dictionary.
    """
    return TaskRouter(**kwargs).route_task(task_description)


def main():
    """Test agent orchestrator."""
    import argparse

    import yaml

    parser = argparse.ArgumentParser(description='Test agent orchestrator')
    parser.add_argument(
        '--config',
        type=Path,
        default=Path('.codex/config/monitoring.yaml'),
        help='Path to monitoring config'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Simulate agent invocation'
    )

    args = parser.parse_args()

    # Load config
    with open(args.config) as f:
        config = yaml.safe_load(f)

    # Initialize orchestrator
    orchestrator = AgentOrchestrator(config, args.dry_run)

    # Test with sample data
    failure_data = {
        'workflow_name': 'test-comprehensive.yml',
        'run': type('obj', (object,), {
            'id': 12345678,
            'created_at': '2026-01-22T06:00:00Z'
        })()
    }

    pattern_matches = [
        {
            'id': 'import_error_001',
            'name': 'Missing Python Module',
            'category': 'dependency',
            'confidence': 0.95,
            'agent': 'dependency-conflict-agent',
            'description': 'Missing pytest-rerunfailures package',
            'suggestion': 'Install pytest-rerunfailures'
        }
    ]

    # Route failure
    recommendations = orchestrator.route_failure(failure_data, pattern_matches)

    # Print results
    print("\nAgent Orchestration Results")
    print("=" * 60)
    print(f"Agents invoked: {len(recommendations)}")

    if recommendations:
        aggregated = orchestrator.aggregate_recommendations(recommendations)
        print(f"Overall confidence: {aggregated['overall_confidence']:.2f}")
        print(f"Primary root cause: {aggregated['primary_root_cause']}")
        print("\nAgent Analysis Section:\n")
        print(orchestrator.generate_agent_analysis_section(recommendations))

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
