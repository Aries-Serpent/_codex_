#!/usr/bin/env python3
"""
Phase 8.2: Issue Severity & Category Scorer

Detects severity (P0-P4) and category of GitHub issues using:
- Keyword analysis
- Issue title/body parsing
- Historical precedent matching
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Severity(Enum):
    """Issue severity levels."""
    P0 = "P0"  # Critical: Production outage, data loss, security breach
    P1 = "P1"  # Urgent: Major feature broken, test failures, deployment blocked
    P2 = "P2"  # High: Significant issue, workaround exists
    P3 = "P3"  # Medium: Minor bug, performance degradation
    P4 = "P4"  # Low: Documentation, feature request, cosmetic issue


class Category(Enum):
    """Issue categories."""
    BUG = "Bug"
    FEATURE_REQUEST = "Feature Request"
    DOCUMENTATION = "Documentation"
    INFRASTRUCTURE = "Infrastructure"
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    TESTING = "Testing"
    OTHER = "Other"


@dataclass
class SeverityScore:
    """Severity detection result."""
    severity: Severity
    category: Category
    confidence: float  # 0.0-1.0
    reasoning: str
    keywords_matched: list[str]


class SeverityScorer:
    """Detects issue severity and category."""

    # P0 (Critical) keywords
    P0_KEYWORDS = {
        "production": 3.0,
        "outage": 3.0,
        "data loss": 3.0,
        "security breach": 3.0,
        "critical": 2.5,
        "broken": 2.0,
        "crash": 2.5,
        "panic": 2.5,
        "segfault": 2.5,
        "deploy blocked": 3.0,
        "cannot deploy": 3.0,
        "emergency": 2.5,
        "down": 2.0,
        "offline": 2.0,
        "unreachable": 2.0,
    }

    # P1 (Urgent) keywords
    P1_KEYWORDS = {
        "urgent": 2.5,
        "test failure": 2.0,
        "tests failing": 2.0,
        "ci broken": 2.0,
        "regression": 2.0,
        "blocking": 2.0,
        "blocked": 1.8,
        "unable": 1.5,
        "doesn't work": 1.5,
        "broken": 1.5,
        "major feature": 1.5,
        "not working": 1.5,
    }

    # P2 (High) keywords
    P2_KEYWORDS = {
        "workaround": -1.0,  # Reduces severity
        "significant": 1.5,
        "serious": 1.5,
        "high priority": 1.5,
        "issue": 1.0,
        "bug": 1.0,
        "defect": 1.0,
        "failure": 1.0,
        "error": 1.0,
    }

    # Category keywords
    CATEGORY_KEYWORDS = {
        Category.BUG: {
            "bug", "defect", "error", "failure", "crash", "panic", "broken",
            "doesn't work", "not working", "exception", "traceback", "stack trace"
        },
        Category.FEATURE_REQUEST: {
            "feature", "enhancement", "request", "add", "implement", "support",
            "wanted", "should", "could", "would be nice"
        },
        Category.DOCUMENTATION: {
            "doc", "documentation", "readme", "guide", "tutorial", "example",
            "comment", "docstring", "clarify", "explain"
        },
        Category.INFRASTRUCTURE: {
            "ci", "deployment", "deploy", "workflow", "github actions", "docker",
            "kubernetes", "k8s", "terraform", "infrastructure", "buildprocess"
        },
        Category.SECURITY: {
            "security", "vulnerability", "cve", "exploit", "breach", "password",
            "token", "credential", "auth", "injection", "xss", "csrf", "ssl"
        },
        Category.PERFORMANCE: {
            "performance", "slow", "speed", "optimize", "optimization", "efficient",
            "latency", "throughput", "memory", "cpu", "bottleneck", "improve"
        },
        Category.TESTING: {
            "test", "pytest", "coverage", "assertion", "mock", "unit test",
            "integration test", "e2e", "qa", "flaky"
        },
    }

    def __init__(self):
        """Initialize the scorer."""
        pass

    def score(
        self,
        title: str,
        body: str,
        labels: Optional[list[str]] = None,
    ) -> SeverityScore:
        """
        Score an issue for severity and category.

        Args:
            title: Issue title
            body: Issue body/description
            labels: Existing GitHub labels (optional)

        Returns:
            SeverityScore with severity, category, confidence, and reasoning
        """
        labels = labels or []
        combined_text = f"{title} {body}".lower()

        # Score severity
        severity, severity_score, matched_keywords = self._score_severity(
            combined_text, labels
        )

        # Determine category
        category = self._determine_category(combined_text, labels)

        # Calculate confidence
        confidence = min(1.0, max(0.0, 0.6 + (severity_score / 10.0)))

        # Build reasoning
        reasoning = self._build_reasoning(
            severity, category, matched_keywords, severity_score
        )

        return SeverityScore(
            severity=severity,
            category=category,
            confidence=confidence,
            reasoning=reasoning,
            keywords_matched=matched_keywords,
        )

    def _score_severity(
        self, text: str, labels: list[str]
    ) -> tuple[Severity, float, list[str]]:
        """Score severity and return severity level, score, and matched keywords."""
        score = 0.0
        matched_keywords: list[str] = []

        # Check P0 keywords
        for keyword, weight in self.P0_KEYWORDS.items():
            if keyword in text:
                score += weight
                matched_keywords.append(f"{keyword}(P0)")

        # Check P1 keywords
        for keyword, weight in self.P1_KEYWORDS.items():
            if keyword in text:
                score += weight
                matched_keywords.append(f"{keyword}(P1)")

        # Check P2 keywords
        for keyword, weight in self.P2_KEYWORDS.items():
            if keyword in text:
                score += weight
                if weight < 0:
                    matched_keywords.append(f"{keyword}(reduce)")

        # Check for existing severity labels
        for label in labels:
            if label.startswith("severity-"):
                return Severity[label.split("-")[1]], score + 5.0, matched_keywords

        # Determine severity from score
        if score >= 4.0:
            return Severity.P0, score, matched_keywords
        elif score >= 2.5:
            return Severity.P1, score, matched_keywords
        elif score >= 1.5:
            return Severity.P2, score, matched_keywords
        elif score >= 0.5:
            return Severity.P3, score, matched_keywords
        else:
            return Severity.P4, score, matched_keywords

    def _determine_category(self, text: str, labels: list[str]) -> Category:
        """Determine the issue category."""
        # Check for existing category labels
        for label in labels:
            if label.startswith("category-"):
                category_str = label.split("-", 1)[1].replace("-", " ").title()
                for cat in Category:
                    if cat.value.replace(" ", "-").lower() == label.split("-", 1)[
                        1
                    ].lower():
                        return cat
                return Category.OTHER

        # Score each category by keyword matches
        category_scores: dict[Category, int] = {}
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                category_scores[category] = score

        # Return highest scoring category
        if category_scores:
            return max(category_scores, key=category_scores.get)

        return Category.OTHER

    def _build_reasoning(
        self,
        severity: Severity,
        category: Category,
        keywords: list[str],
        score: float,
    ) -> str:
        """Build a human-readable reasoning string."""
        keyword_str = ", ".join(keywords[:3])
        if len(keywords) > 3:
            keyword_str += f", +{len(keywords) - 3} more"

        return (
            f"Classified as {severity.value} {category.value}. "
            f"Score: {score:.1f}, Matched keywords: {keyword_str or 'none'}"
        )


def score_issue(
    title: str,
    body: str,
    labels: Optional[list[str]] = None,
) -> SeverityScore:
    """
    Convenience function to score a single issue.

    Args:
        title: Issue title
        body: Issue body
        labels: GitHub labels (optional)

    Returns:
        SeverityScore result
    """
    scorer = SeverityScorer()
    return scorer.score(title, body, labels)


if __name__ == "__main__":
    # Example usage
    test_cases = [
        {
            "title": "Production database is down",
            "body": "Users cannot access the platform. Outage started 5 min ago.",
            "expected_severity": "P0",
        },
        {
            "title": "CI tests failing in main branch",
            "body": "All tests are failing with import errors. Blocking deployments.",
            "expected_severity": "P1",
        },
        {
            "title": "Slow query on user list endpoint",
            "body": "Query takes 5+ seconds. Need optimization.",
            "expected_severity": "P2",
        },
        {
            "title": "Typo in README",
            "body": "Found a typo in line 42.",
            "expected_severity": "P4",
        },
    ]

    scorer = SeverityScorer()
    for test in test_cases:
        result = scorer.score(test["title"], test["body"])
        print(
            f"\nTitle: {test['title']}\n"
            f"Expected: {test['expected_severity']}, "
            f"Got: {result.severity.value}\n"
            f"Category: {result.category.value}\n"
            f"Confidence: {result.confidence:.2f}\n"
            f"Reasoning: {result.reasoning}"
        )
