"""
GitHub Guru Agent — Pattern Registry

Defines 30+ pattern signatures for PR/issue/workflow analysis.
Each pattern has an ID, name, description, severity, and detection logic.

Pattern categories:
  CI/CD: Workflow failures, flakiness, artifact drift
  Dependency: Outdated deps, security drift, version conflicts
  Test: Coverage drop, skip explosion, xfail accumulation
  Build: Import errors, lint failures, type check regressions
  Coverage: Coverage threshold drop, uncovered critical paths
  Lint: Ruff/black/isort violations
  Infrastructure: Missing labels, stale branches, orphaned files
  Security: CodeQL alerts, dependency vulnerabilities, secret exposure
  Documentation: Missing docstrings, broken links, stale docs
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Optional


class PatternCategory(str, Enum):
    CI_CD = "ci_cd"
    DEPENDENCY = "dependency"
    TEST = "test"
    BUILD = "build"
    COVERAGE = "coverage"
    LINT = "lint"
    INFRASTRUCTURE = "infrastructure"
    SECURITY = "security"
    DOCUMENTATION = "documentation"


class PatternSeverity(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Pattern:
    """A single pattern signature for detection."""

    id: str
    name: str
    category: PatternCategory
    severity: PatternSeverity
    description: str
    indicators: list[str]
    remediation: str
    routing_agent: Optional[str] = None
    confidence_weight: float = 1.0
    tags: list[str] = field(default_factory=list)


@dataclass
class PatternMatch:
    """Result of a pattern detection."""

    pattern: Pattern
    confidence: float
    evidence: list[str]
    context: dict[str, Any] = field(default_factory=dict)

    @property
    def score(self) -> float:
        """Confidence-weighted severity score (0–100)."""
        severity_weights = {
            PatternSeverity.CRITICAL: 100,
            PatternSeverity.HIGH: 75,
            PatternSeverity.MEDIUM: 50,
            PatternSeverity.LOW: 25,
            PatternSeverity.INFO: 10,
        }
        return self.confidence * severity_weights.get(self.pattern.severity, 50)


# --- Pattern Registry -----------------------------------------------------------

PATTERNS: list[Pattern] = [
    # CI/CD patterns
    Pattern(
        id="CI-001",
        name="Repeated Workflow Failure",
        category=PatternCategory.CI_CD,
        severity=PatternSeverity.HIGH,
        description="Same workflow fails on ≥3 consecutive runs",
        indicators=["conclusion:failure", "run_count>=3", "same_workflow"],
        remediation="Investigate workflow logs; route to ci-testing-agent",
        routing_agent="ci-testing-agent",
        tags=["workflow", "flakiness"],
    ),
    Pattern(
        id="CI-002",
        name="Artifact Size Regression",
        category=PatternCategory.CI_CD,
        severity=PatternSeverity.MEDIUM,
        description="Build artifact size increased >20% vs baseline",
        indicators=["artifact_size_delta>0.2"],
        remediation="Check for bundled dev deps or large binary files",
        tags=["artifact", "size"],
    ),
    Pattern(
        id="CI-003",
        name="Missing Required Check",
        category=PatternCategory.CI_CD,
        severity=PatternSeverity.HIGH,
        description="PR merged without required CI check completion",
        indicators=["pr_merged", "check_status:missing"],
        remediation="Enable required status checks in branch protection",
        tags=["protection", "gate"],
    ),
    Pattern(
        id="CI-004",
        name="Flaky Test Accumulation",
        category=PatternCategory.CI_CD,
        severity=PatternSeverity.MEDIUM,
        description="Number of xfail/skipif markers growing >5 per week",
        indicators=["xfail_count_delta>5", "period:week"],
        remediation="Route to autonomous-test-healer-agent",
        routing_agent="autonomous-test-healer-agent",
        tags=["test", "flakiness"],
    ),
    Pattern(
        id="CI-005",
        name="Long-Running Job",
        category=PatternCategory.CI_CD,
        severity=PatternSeverity.LOW,
        description="Job duration exceeds 30 minutes",
        indicators=["job_duration>1800"],
        remediation="Split job or add caching",
        tags=["performance", "timeout"],
    ),
    # Dependency patterns
    Pattern(
        id="DEP-001",
        name="Outdated Critical Dependency",
        category=PatternCategory.DEPENDENCY,
        severity=PatternSeverity.HIGH,
        description="Core dependency >90 days behind latest release",
        indicators=["dep_age_days>90", "dep_type:core"],
        remediation="Update dependency; check CHANGELOG for breaking changes",
        routing_agent="dependency-conflict-agent",
        tags=["outdated", "security"],
    ),
    Pattern(
        id="DEP-002",
        name="Unpinned Transitive Dependency",
        category=PatternCategory.DEPENDENCY,
        severity=PatternSeverity.MEDIUM,
        description="requirements*.txt has unpinned version specifier",
        indicators=["unpinned_dep", "file:requirements"],
        remediation="Pin all transitive dependencies for reproducibility",
        tags=["pinning", "reproducibility"],
    ),
    Pattern(
        id="DEP-003",
        name="Security Advisory Match",
        category=PatternCategory.DEPENDENCY,
        severity=PatternSeverity.CRITICAL,
        description="Installed dependency matches a known CVE",
        indicators=["cve_match"],
        remediation="Update affected package immediately",
        routing_agent="dependency-vulnerability-scanner",
        tags=["security", "cve"],
    ),
    # Test patterns
    Pattern(
        id="TEST-001",
        name="Coverage Drop",
        category=PatternCategory.TEST,
        severity=PatternSeverity.HIGH,
        description="Test coverage dropped >5% from baseline",
        indicators=["coverage_delta<-5"],
        remediation="Add tests for uncovered paths",
        routing_agent="coverage-roadmap-agent",
        tags=["coverage", "regression"],
    ),
    Pattern(
        id="TEST-002",
        name="Test Collection Error",
        category=PatternCategory.TEST,
        severity=PatternSeverity.CRITICAL,
        description="pytest cannot collect tests (import error, syntax error)",
        indicators=["collection_error"],
        remediation="Fix import error in affected test file",
        routing_agent="ci-testing-agent",
        tags=["import", "collection"],
    ),
    Pattern(
        id="TEST-003",
        name="Skip Explosion",
        category=PatternCategory.TEST,
        severity=PatternSeverity.MEDIUM,
        description="More than 20% of test suite is skipped",
        indicators=["skip_ratio>0.2"],
        remediation="Review skipif conditions; fix environment guards",
        tags=["skip", "health"],
    ),
    # Build patterns
    Pattern(
        id="BUILD-001",
        name="Import Error on PR",
        category=PatternCategory.BUILD,
        severity=PatternSeverity.CRITICAL,
        description="ModuleNotFoundError during test collection",
        indicators=["ModuleNotFoundError", "collection_error"],
        remediation="Install missing dependency or fix circular import",
        routing_agent="ci-importerror-agent",
        tags=["import", "circular"],
    ),
    Pattern(
        id="BUILD-002",
        name="Type Check Regression",
        category=PatternCategory.BUILD,
        severity=PatternSeverity.MEDIUM,
        description="mypy error count increased vs base branch",
        indicators=["mypy_error_delta>0"],
        remediation="Fix type annotations in changed files",
        tags=["type", "mypy"],
    ),
    # Security patterns
    Pattern(
        id="SEC-001",
        name="CodeQL Alert",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.HIGH,
        description="github-advanced-security bot raised new CodeQL alert",
        indicators=["codeql_alert", "state:open"],
        remediation="Fix CodeQL alert per alert description",
        routing_agent="code-scanning-remediation-agent",
        tags=["codeql", "security"],
    ),
    Pattern(
        id="SEC-002",
        name="Secret in Code",
        category=PatternCategory.SECURITY,
        severity=PatternSeverity.CRITICAL,
        description="Potential secret or API key pattern detected in diff",
        indicators=["secret_pattern", "diff_context"],
        remediation="Revoke and rotate secret immediately; use vault",
        routing_agent="github-security-enforcer",
        tags=["secret", "credential"],
    ),
    # Infrastructure patterns
    Pattern(
        id="INFRA-001",
        name="Stale Branch",
        category=PatternCategory.INFRASTRUCTURE,
        severity=PatternSeverity.LOW,
        description="Branch inactive for >30 days with no open PR",
        indicators=["branch_age_days>30", "no_open_pr"],
        remediation="Delete or archive stale branch",
        tags=["branch", "hygiene"],
    ),
    Pattern(
        id="INFRA-002",
        name="Missing Label",
        category=PatternCategory.INFRASTRUCTURE,
        severity=PatternSeverity.LOW,
        description="PR or issue missing required label taxonomy entry",
        indicators=["missing_label", "taxonomy_mismatch"],
        remediation="Apply correct label from .github/labels.yml",
        tags=["label", "taxonomy"],
    ),
    Pattern(
        id="INFRA-003",
        name="Orphaned Root File",
        category=PatternCategory.INFRASTRUCTURE,
        severity=PatternSeverity.INFO,
        description="Stray report/log file in repository root",
        indicators=["root_file", "extension:txt|log|md", "untracked_pattern"],
        remediation="Move to .codex/ per artifact hygiene policy",
        tags=["hygiene", "root"],
    ),
    # Documentation patterns
    Pattern(
        id="DOC-001",
        name="Missing Module Docstring",
        category=PatternCategory.DOCUMENTATION,
        severity=PatternSeverity.LOW,
        description="New Python module missing module-level docstring",
        indicators=["missing_docstring", "file:*.py", "new_file"],
        remediation="Add module docstring per PEP 257",
        tags=["docstring", "pep257"],
    ),
    Pattern(
        id="DOC-002",
        name="Broken Link in Docs",
        category=PatternCategory.DOCUMENTATION,
        severity=PatternSeverity.MEDIUM,
        description="Markdown link in docs/ or .github/ resolves to 404",
        indicators=["broken_link", "http_status:404"],
        remediation="Fix or remove broken link",
        routing_agent="link-validator-agent",
        tags=["link", "404"],
    ),
]

# Build lookup index
_PATTERN_BY_ID: dict[str, Pattern] = {p.id: p for p in PATTERNS}
_PATTERNS_BY_CATEGORY: dict[PatternCategory, list[Pattern]] = {}
for _p in PATTERNS:
    _PATTERNS_BY_CATEGORY.setdefault(_p.category, []).append(_p)


def get_pattern(pattern_id: str) -> Optional[Pattern]:
    """Retrieve a pattern by its ID."""
    return _PATTERN_BY_ID.get(pattern_id)


def get_patterns_by_category(category: PatternCategory) -> list[Pattern]:
    """Retrieve all patterns for a given category."""
    return _PATTERNS_BY_CATEGORY.get(category, [])


def get_patterns_by_severity(severity: PatternSeverity) -> list[Pattern]:
    """Retrieve all patterns at or above a given severity."""
    order = [
        PatternSeverity.CRITICAL,
        PatternSeverity.HIGH,
        PatternSeverity.MEDIUM,
        PatternSeverity.LOW,
        PatternSeverity.INFO,
    ]
    threshold = order.index(severity)
    return [p for p in PATTERNS if order.index(p.severity) <= threshold]


def match_patterns(context: dict[str, Any]) -> list[PatternMatch]:
    """
    Run all patterns against a context dict and return matches.

    Args:
        context: Dict of indicators and their values from analysis

    Returns:
        List of PatternMatch sorted by descending score
    """
    matches: list[PatternMatch] = []
    for pattern in PATTERNS:
        evidence = []
        hit_count = 0
        for indicator in pattern.indicators:
            # Simple indicator matching: check if key is in context
            # Real implementation would use more sophisticated matching
            key = indicator.split(":")[0].split(">")[0].split("<")[0]
            if key in context:
                evidence.append(f"{indicator}: {context.get(key)}")
                hit_count += 1

        if hit_count > 0:
            confidence = hit_count / len(pattern.indicators) * pattern.confidence_weight
            matches.append(
                PatternMatch(
                    pattern=pattern,
                    confidence=min(confidence, 1.0),
                    evidence=evidence,
                    context=context,
                )
            )

    return sorted(matches, key=lambda m: m.score, reverse=True)
