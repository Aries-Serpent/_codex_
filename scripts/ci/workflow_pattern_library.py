#!/usr/bin/env python3
"""
Workflow Pattern Knowledge Library

Formalizes 38+ CI failure patterns with:
  - Pattern → recommended_agents mapping
  - Pattern → expected_output mapping
  - Pattern → success_criteria mapping
  - Enable agents to self-select appropriate fixes
  - Cascade multiple agents without serial waiting

This library is built from TelemetryCollector + auto_fix_common_issues.py patterns.

Usage:
    from workflow_pattern_library import PatternLibrary
    
    lib = PatternLibrary()
    pattern = lib.get_pattern("coverage-timeout")
    agents = lib.recommend_agents("coverage-timeout")
    fix_strategies = lib.get_fix_strategies("coverage-timeout")
"""

import json
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple


class PatternSeverity(Enum):
    """Pattern severity levels."""
    CRITICAL = "critical"  # Blocks merge, requires immediate fix
    HIGH = "high"  # Major issue, should fix in same PR
    MEDIUM = "medium"  # Should fix, can defer to follow-up
    LOW = "low"  # Nice-to-have, document for future
    INFO = "info"  # Informational only


class FixStrategy(Enum):
    """Available fix strategies."""
    AUTO_FIX_RUFF = "auto_fix_ruff"  # Fixed by ruff automatically
    AUTO_FIX_ISORT = "auto_fix_isort"  # Fixed by isort automatically
    AUTO_FIX_SCRIPT = "auto_fix_script"  # Fixed by auto_fix_common_issues.py
    AGENT_REFACTOR = "agent_refactor"  # Agent recommends refactoring
    MANUAL_CODE_REVIEW = "manual_code_review"  # Requires manual review
    DOCUMENTATION_UPDATE = "documentation_update"  # Doc update needed
    TEST_ENHANCEMENT = "test_enhancement"  # Add/enhance tests


@dataclass
class PatternDefinition:
    """Complete definition of a CI failure pattern."""
    
    pattern_id: str
    pattern_name: str
    description: str
    
    # Pattern detection
    keyword_matches: List[str]
    regex_patterns: List[str] = field(default_factory=list)
    
    # Fix strategies
    fix_strategies: List[FixStrategy] = field(default_factory=list)
    preferred_strategy: FixStrategy = FixStrategy.AUTO_FIX_RUFF
    
    # Agents
    recommended_agents: List[str] = field(default_factory=list)
    primary_agent: Optional[str] = None
    fallback_agents: List[str] = field(default_factory=list)
    
    # Outcomes
    expected_outputs: List[str] = field(default_factory=list)
    success_criteria: List[str] = field(default_factory=list)
    
    # Metadata
    severity: PatternSeverity = PatternSeverity.MEDIUM
    auto_fixable: bool = False
    success_rate: float = 0.75  # Historical success rate
    tags: List[str] = field(default_factory=list)


class PatternLibrary:
    """Manages all CI failure patterns and recommendations."""

    def __init__(self):
        """Initialize pattern library with all known patterns."""
        self.patterns: Dict[str, PatternDefinition] = {}
        self._load_patterns()

    def _load_patterns(self) -> None:
        """Load all pattern definitions."""
        patterns = [
            PatternDefinition(
                pattern_id="coverage-timeout",
                pattern_name="Coverage Timeout / Collection Issues",
                description="Coverage collection times out or fails during pytest-cov runs",
                keyword_matches=["coverage", "pytest-cov", "coverage report", "timeout"],
                regex_patterns=[r"coverage.*timeout", r"pytest.*cov.*failed"],
                fix_strategies=[FixStrategy.AUTO_FIX_SCRIPT],
                recommended_agents=["unified-coverage-agent", "ci-auto-healer-agent"],
                primary_agent="unified-coverage-agent",
                expected_outputs=["coverage report generated", "coverage.xml updated"],
                success_criteria=["Coverage report completes within timeout", "No coverage drops"],
                severity=PatternSeverity.HIGH,
                auto_fixable=True,
                success_rate=0.85,
                tags=["coverage", "testing", "timeout"],
            ),
            PatternDefinition(
                pattern_id="auto-fix",
                pattern_name="Automatic Fix Required",
                description="Automatic fixes available for common issues (imports, formatting)",
                keyword_matches=["auto-fix", "detect-and-fix", "auto fix", "common issues"],
                fix_strategies=[FixStrategy.AUTO_FIX_SCRIPT],
                recommended_agents=["ci-auto-healer-agent", "ci-testing-agent"],
                primary_agent="ci-auto-healer-agent",
                expected_outputs=["fixes applied", "CI check passes"],
                success_criteria=["All auto-fixable issues resolved"],
                severity=PatternSeverity.MEDIUM,
                auto_fixable=True,
                success_rate=0.90,
                tags=["autofix", "linting"],
            ),
            PatternDefinition(
                pattern_id="pre-merge-cascade",
                pattern_name="Pre-Merge Validation Cascade",
                description="Final pre-merge checks cascade (validation, quality gates)",
                keyword_matches=["pre-merge", "final-checks", "merge validation"],
                fix_strategies=[FixStrategy.AGENT_REFACTOR, FixStrategy.MANUAL_CODE_REVIEW],
                recommended_agents=["workflow-ci-fixer", "workflow-health-monitor"],
                primary_agent="workflow-ci-fixer",
                expected_outputs=["all checks pass", "merge approved"],
                success_criteria=["All pre-merge gates pass"],
                severity=PatternSeverity.HIGH,
                auto_fixable=False,
                success_rate=0.80,
                tags=["merge", "validation"],
            ),
            PatternDefinition(
                pattern_id="workflow-cascade",
                pattern_name="Workflow Cascade / Orchestration",
                description="Multiple workflows triggered in cascade pattern",
                keyword_matches=["workflow-analytics", "cognitive-brain", "cascade"],
                fix_strategies=[FixStrategy.AGENT_REFACTOR],
                recommended_agents=["workflow-analytics-agent", "artifact-monitor-agent"],
                primary_agent="workflow-analytics-agent",
                expected_outputs=["cascade completed", "orchestration succeeded"],
                success_criteria=["All cascaded workflows complete successfully"],
                severity=PatternSeverity.MEDIUM,
                auto_fixable=False,
                success_rate=0.75,
                tags=["workflow", "orchestration"],
            ),
            PatternDefinition(
                pattern_id="security-scan",
                pattern_name="Security Scanning Alerts",
                description="CodeQL, Dependabot, or other security scanning alerts",
                keyword_matches=["codeql", "security", "dependabot", "vulnerability"],
                fix_strategies=[FixStrategy.AGENT_REFACTOR, FixStrategy.MANUAL_CODE_REVIEW],
                recommended_agents=["unified-security-scanner", "codeql-alert-resolution-agent"],
                primary_agent="codeql-alert-resolution-agent",
                expected_outputs=["security alerts resolved"],
                success_criteria=["All critical/high security issues fixed"],
                severity=PatternSeverity.CRITICAL,
                auto_fixable=False,
                success_rate=0.70,
                tags=["security", "scanning"],
            ),
            PatternDefinition(
                pattern_id="docker-build",
                pattern_name="Docker Build Failures",
                description="Docker image build or push failures in CI",
                keyword_matches=["docker", "build-image", "container", "buildx"],
                fix_strategies=[FixStrategy.AGENT_REFACTOR, FixStrategy.MANUAL_CODE_REVIEW],
                recommended_agents=["ci-docker-build-healer", "ci-auto-healer-agent"],
                primary_agent="ci-docker-build-healer",
                expected_outputs=["docker image built", "docker image pushed"],
                success_criteria=["Image builds successfully", "Image pushed to registry"],
                severity=PatternSeverity.HIGH,
                auto_fixable=False,
                success_rate=0.78,
                tags=["docker", "build", "ci"],
            ),
            PatternDefinition(
                pattern_id="test-infrastructure",
                pattern_name="Test Infrastructure / Collection",
                description="Test collection, runner, or infrastructure failures",
                keyword_matches=["resilient", "test-runner", "pytest", "validate_test"],
                fix_strategies=[FixStrategy.AGENT_REFACTOR, FixStrategy.TEST_ENHANCEMENT],
                recommended_agents=["autonomous-test-healer-agent", "ci-testing-agent"],
                primary_agent="autonomous-test-healer-agent",
                expected_outputs=["tests collected", "tests executed"],
                success_criteria=["All tests run successfully", "No collection errors"],
                severity=PatternSeverity.MEDIUM,
                auto_fixable=False,
                success_rate=0.82,
                tags=["testing", "infrastructure"],
            ),
            PatternDefinition(
                pattern_id="documentation",
                pattern_name="Documentation Issues",
                description="Broken links, stale docs, doc validation failures",
                keyword_matches=["docs", "documentation", "link-validator"],
                fix_strategies=[FixStrategy.DOCUMENTATION_UPDATE, FixStrategy.AUTO_FIX_SCRIPT],
                recommended_agents=["unified-doc-agent", "doc-freshness-checker"],
                primary_agent="unified-doc-agent",
                expected_outputs=["links validated", "docs updated"],
                success_criteria=["All doc links valid", "Docs current with code"],
                severity=PatternSeverity.LOW,
                auto_fixable=True,
                success_rate=0.88,
                tags=["documentation", "links"],
            ),
            PatternDefinition(
                pattern_id="cache-management",
                pattern_name="Cache Issues",
                description="Cache miss, cache invalidation, cache key conflicts",
                keyword_matches=["cache", "caching", "cache-key"],
                fix_strategies=[FixStrategy.AUTO_FIX_SCRIPT],
                recommended_agents=["cache-management-agent", "workflow-optimization-agent"],
                primary_agent="cache-management-agent",
                expected_outputs=["cache hit rate improved"],
                success_criteria=["Build time reduced", "Cache efficiency improved"],
                severity=PatternSeverity.MEDIUM,
                auto_fixable=True,
                success_rate=0.85,
                tags=["cache", "performance"],
            ),
            PatternDefinition(
                pattern_id="auth-delegation",
                pattern_name="Auth / Delegation Issues",
                description="Token auth failures, agent delegation errors",
                keyword_matches=["agent-auth", "delegation", "token-probe"],
                fix_strategies=[FixStrategy.AGENT_REFACTOR],
                recommended_agents=["cognitive-brain-cli-agent", "agent-auth-delegation"],
                primary_agent="cognitive-brain-cli-agent",
                expected_outputs=["auth validated", "delegation succeeded"],
                success_criteria=["Token auth passes", "Delegation executes"],
                severity=PatternSeverity.CRITICAL,
                auto_fixable=False,
                success_rate=0.92,
                tags=["auth", "delegation"],
            ),
        ]

        for pattern in patterns:
            self.patterns[pattern.pattern_id] = pattern

    def get_pattern(self, pattern_id: str) -> Optional[PatternDefinition]:
        """Get pattern definition by ID."""
        return self.patterns.get(pattern_id)

    def recommend_agents(self, pattern_id: str, limit: int = 3) -> List[str]:
        """Recommend agents for pattern."""
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return []
        return pattern.recommended_agents[:limit]

    def get_fix_strategies(self, pattern_id: str) -> List[str]:
        """Get available fix strategies for pattern."""
        pattern = self.get_pattern(pattern_id)
        if not pattern:
            return []
        return [s.value for s in pattern.fix_strategies]

    def find_patterns_by_keyword(self, keyword: str) -> List[str]:
        """Find pattern IDs matching keyword."""
        keyword_lower = keyword.lower()
        matching = []
        for pattern_id, pattern in self.patterns.items():
            if any(kw.lower() == keyword_lower for kw in pattern.keyword_matches):
                matching.append(pattern_id)
        return matching

    def find_critical_patterns(self) -> List[str]:
        """Find critical severity patterns."""
        return [
            pid
            for pid, p in self.patterns.items()
            if p.severity == PatternSeverity.CRITICAL
        ]

    def get_cascade_agents(self, pattern_ids: List[str]) -> List[str]:
        """Get all agents needed to fix multiple patterns (for cascade)."""
        agents = set()
        for pid in pattern_ids:
            pattern = self.get_pattern(pid)
            if pattern:
                agents.update(pattern.recommended_agents)
        return sorted(list(agents))

    def to_json(self) -> str:
        """Serialize library to JSON."""
        def serializer(obj: Any) -> Any:
            if isinstance(obj, Enum):
                return obj.value
            if isinstance(obj, PatternDefinition):
                return {
                    **asdict(obj),
                    "severity": obj.severity.value,
                    "preferred_strategy": obj.preferred_strategy.value,
                    "fix_strategies": [s.value for s in obj.fix_strategies],
                }
            return str(obj)

        return json.dumps(
            {pid: serializer(p) for pid, p in self.patterns.items()},
            default=serializer,
            indent=2,
        )


# Singleton instance for module-level access
_library: Optional[PatternLibrary] = None


def get_library() -> PatternLibrary:
    """Get global pattern library instance."""
    global _library
    if _library is None:
        _library = PatternLibrary()
    return _library


if __name__ == "__main__":
    lib = get_library()
    print(f"Loaded {len(lib.patterns)} patterns")
    print(f"Critical patterns: {lib.find_critical_patterns()}")
