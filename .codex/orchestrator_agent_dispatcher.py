#!/usr/bin/env python3
"""
Phase 3 Campaign Orchestrator — Agent Dispatcher & Failure Router
Routes Tier 1 failures to appropriate specialist agents based on pattern matching
"""

import json
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Optional

class FailurePattern(Enum):
    """Recognized failure patterns and their routing"""
    ATTRIBUTE_ERROR = "AttributeError|ImportError"
    XFAIL_VIOLATION = "xfail\\(strict=False\\)"
    CODEQL_ALERT = "codeql.*alert|security.*finding"
    RUFF_VIOLATION = "F401|I001|ruff"
    WORKFLOW_SYNTAX = "workflow.*syntax|yaml.*error"
    MODEL_UNAVAILABLE = "HFModelUnavailableError|ModelNotFound"
    COVERAGE_DROP = "coverage.*drop|coverage.*threshold"
    CIRCULAR_IMPORT = "circular.*import|import.*cycle"
    COVERAGE_REGRESSION = "coverage.*regression"
    DEPENDENCY_CONFLICT = "dependency.*conflict|version.*mismatch"

class AgentType(Enum):
    """Specialized agent types and their capabilities"""
    CI_TESTING = "ci-testing-agent"
    CODEBASE_HEALTH = "codebase-health-guardian"
    SECURITY_ALERT = "security-alert-verification-agent"
    CI_AUTO_HEALER = "ci-auto-healer-agent"
    WORKFLOW_COMPLIANCE = "workflow-compliance-guardian"
    COVERAGE_ROADMAP = "coverage-roadmap-agent"
    DOC_FRESHNESS = "doc-freshness-checker"
    DEPENDENCY_CONFLICT = "dependency-conflict-agent"
    TEST_FAILURE = "test-failure-analyzer-agent"
    PYTHON_312_FIXER = "python-312-type-fixer"
    ESCALATION = "human-escalation"

@dataclass
class FailureRoute:
    """Route configuration for a failure pattern"""
    pattern: FailurePattern
    agent: AgentType
    priority: int  # P0=critical, P1=high, P2=medium, P3=low
    heal_window_sec: int  # Time allowed for agent to fix
    
ROUTING_TABLE = [
    # P0 - Critical failures (immediate auto-heal)
    FailureRoute(FailurePattern.ATTRIBUTE_ERROR, AgentType.CI_TESTING, 0, 120),
    FailureRoute(FailurePattern.XFAIL_VIOLATION, AgentType.CODEBASE_HEALTH, 0, 120),
    FailureRoute(FailurePattern.CODEQL_ALERT, AgentType.SECURITY_ALERT, 0, 180),
    
    # P1 - High priority
    FailureRoute(FailurePattern.RUFF_VIOLATION, AgentType.CODEBASE_HEALTH, 1, 120),
    FailureRoute(FailurePattern.WORKFLOW_SYNTAX, AgentType.WORKFLOW_COMPLIANCE, 1, 120),
    FailureRoute(FailurePattern.MODEL_UNAVAILABLE, AgentType.CI_TESTING, 1, 120),
    
    # P2 - Medium priority
    FailureRoute(FailurePattern.COVERAGE_DROP, AgentType.COVERAGE_ROADMAP, 2, 180),
    FailureRoute(FailurePattern.CIRCULAR_IMPORT, AgentType.CI_TESTING, 2, 180),
    
    # P3 - Lower priority
    FailureRoute(FailurePattern.COVERAGE_REGRESSION, AgentType.COVERAGE_ROADMAP, 3, 240),
    FailureRoute(FailurePattern.DEPENDENCY_CONFLICT, AgentType.DEPENDENCY_CONFLICT, 3, 240),
]

def route_failure(failure_log: str, workflow_name: str) -> Optional[FailureRoute]:
    """
    Analyze failure log and determine routing target agent
    Returns matched FailureRoute or None if no pattern matches
    """
    failure_log_lower = failure_log.lower()
    
    for route in ROUTING_TABLE:
        pattern_str = route.pattern.value
        if pattern_str.lower() in failure_log_lower:
            return route
    
    # Default: escalate unrecognized patterns
    return None

def format_agent_prompt(failure: dict, route: Optional[FailureRoute]) -> str:
    """Format a prompt for delegating to a specialist agent"""
    
    if not route:
        return f"""
MANUAL ESCALATION REQUIRED

Workflow: {failure['workflow']}
Run ID: {failure['run_id']}
Log Summary: {failure['log_snippet'][:500]}...

No auto-fixable pattern detected.
Requires human review and specialized agent routing.
"""
    
    return f"""
DELEGATED TO: {route.agent.value}
Priority: P{route.priority}
Heal Window: {route.heal_window_sec}s
Failure Pattern: {route.pattern.name}

Workflow: {failure['workflow']}
Run ID: {failure['run_id']}
Branch: copilot/explore-codebase-implement-tasks
Commit SHA: 05dde76e0dff851481b0a072c09acafe1dea44e5

Log Excerpt:
{failure['log_snippet']}

Action Items:
1. Analyze failure pattern
2. Apply targeted fix
3. Verify fix with test run
4. Report back with grade (0-100)
"""

# Example failures (for testing)
EXAMPLE_FAILURES = [
    {
        'workflow': 'Validation Pipeline',
        'run_id': 28614560814,
        'log_snippet': 'AttributeError: module has no attribute _version',
        'pattern': FailurePattern.ATTRIBUTE_ERROR
    },
    {
        'workflow': 'Code Quality: PR #5194',
        'run_id': 28614560868,
        'log_snippet': 'E001: F401 unused import in src/codex/__init__.py',
        'pattern': FailurePattern.RUFF_VIOLATION
    }
]

if __name__ == '__main__':
    print("=" * 80)
    print("PHASE 3 CAMPAIGN ORCHESTRATOR — AGENT DISPATCHER CONFIGURATION")
    print("=" * 80)
    print(f"\nRouting Table: {len(ROUTING_TABLE)} patterns registered")
    print("\nPattern → Agent Mappings:")
    for route in ROUTING_TABLE:
        print(f"  P{route.priority} {route.pattern.name:25} → {route.agent.value:35} ({route.heal_window_sec}s window)")
    
    print("\n\nExample Failure Routing (Simulation):")
    print("-" * 80)
    for failure in EXAMPLE_FAILURES:
        print(f"\nFailure: {failure['workflow']}")
        route = route_failure(failure['log_snippet'], failure['workflow'])
        if route:
            print(f"✅ Route: {route.agent.value} (P{route.priority})")
        else:
            print("⚠️  No pattern match - escalate to human")
