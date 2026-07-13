"""Issue Generator — Auto-generate GitHub issues for detected problems.

This module implements:
- Auto-generate issues for SLO breaches
- Auto-generate issues for drift detected
- Auto-generate issues for regressions >5%
- Auto-generate issues for canary drill failures
- Link issues to lane owners
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GeneratedIssue:
    """Generated GitHub issue."""

    issue_id: str  # GitHub issue number (populated after creation)
    title: str
    body: str
    assignee: Optional[str]  # Lane owner or team
    labels: List[str]
    priority: str  # "critical", "high", "medium", "low"
    created_at: datetime
    github_link: Optional[str] = None


class IssueGenerator:
    """Generates GitHub issues for detected problems."""

    LANE_OWNERS = {
        "A": "@mbaetiong",
        "B": "@mbaetiong",
        "C": "@team-orchestration",
        "D": "@team-governance",
        "E": "@team-execution",
        "H": "@team-sre",  # SRE lane
        "I": "@team-quality",  # Quality gates lane
        "J": "@team-monitoring",
        "K": "@team-tools",
    }

    def __init__(self):
        """Initialize issue generator."""
        self.generated_issues: List[GeneratedIssue] = []
        self.created_at = datetime.now(timezone.utc)

    def generate_slo_breach_issue(self, slo_name: str, current_pct: float, target_pct: float) -> GeneratedIssue:
        """Generate issue for SLO breach."""
        issue_id = f"slo-breach-{datetime.now(timezone.utc).timestamp()}"

        title = f"🚨 SLO Breach: {slo_name} at {current_pct:.2f}% (target: {target_pct:.2f}%)"

        body = f"""## SLO Breach Alert

**SLO:** {slo_name}
**Current:** {current_pct:.2f}%
**Target:** {target_pct:.2f}%
**Breach:** {target_pct - current_pct:.2f}%

### Impact
This SLO breach affects production reliability and may impact customers.

### Required Action
1. Investigate root cause
2. Apply immediate mitigation if available
3. Plan remediation
4. Monitor for recovery

### Investigation Steps
- Check error logs for failure patterns
- Review recent deployments
- Monitor error budget consumption
- Contact on-call SRE team if critical
"""

        issue = GeneratedIssue(
            issue_id=issue_id,
            title=title,
            body=body,
            assignee="@mbaetiong",  # Critical - escalate to authority
            labels=["sre", "slo-breach", "critical"],
            priority="critical",
            created_at=datetime.now(timezone.utc),
        )

        self.generated_issues.append(issue)
        logger.info(f"Generated SLO breach issue: {issue.title}")
        return issue

    def generate_drift_issue(self, metric_name: str, drift_magnitude_pct: float, observed: float, expected: float) -> GeneratedIssue:
        """Generate issue for detected drift."""
        issue_id = f"drift-{datetime.now(timezone.utc).timestamp()}"

        title = f"⚠️ Drift Detected: {metric_name} ({drift_magnitude_pct:.2f}% deviation)"

        body = f"""## Drift Detection Alert

**Metric:** {metric_name}
**Expected:** {expected:.2f}
**Observed:** {observed:.2f}
**Drift:** {drift_magnitude_pct:.2f}%

### Description
Baseline drift detection identified a significant deviation from expected behavior.

### Investigation Required
1. Verify observation is accurate
2. Check for system changes that explain drift
3. Determine if this represents a real issue or expected variation
4. Update baseline if appropriate

### Possible Causes
- System configuration changes
- Load pattern changes
- Infrastructure changes
- Code deployment
- External dependencies changed
"""

        issue = GeneratedIssue(
            issue_id=issue_id,
            title=title,
            body=body,
            assignee="@team-sre",
            labels=["governance", "drift-detection", "investigation"],
            priority="high",
            created_at=datetime.now(timezone.utc),
        )

        self.generated_issues.append(issue)
        logger.info(f"Generated drift issue: {issue.title}")
        return issue

    def generate_regression_issue(self, metric_name: str, regression_pct: float, baseline: float, current: float) -> GeneratedIssue:
        """Generate issue for regression >5%."""
        issue_id = f"regression-{datetime.now(timezone.utc).timestamp()}"

        title = f"📉 Performance Regression: {metric_name} down {regression_pct:.1f}%"

        body = f"""## Performance Regression Alert

**Metric:** {metric_name}
**Baseline:** {baseline:.2f}
**Current:** {current:.2f}
**Regression:** {regression_pct:.1f}%

### Description
Performance regression detected that exceeds 5% threshold.

### Required Actions
1. Identify change that caused regression
2. Verify impact on production workload
3. Determine if regression is acceptable or requires fix
4. Document decision in issue

### Investigation Checklist
- [ ] Recent code changes
- [ ] Dependency updates
- [ ] Infrastructure changes
- [ ] Load pattern changes
- [ ] Cache invalidation
"""

        issue = GeneratedIssue(
            issue_id=issue_id,
            title=title,
            body=body,
            assignee="@team-orchestration",
            labels=["performance", "regression", "investigation"],
            priority="high",
            created_at=datetime.now(timezone.utc),
        )

        self.generated_issues.append(issue)
        logger.info(f"Generated regression issue: {issue.title}")
        return issue

    def generate_canary_drill_failure_issue(self, drill_type: str, failure_count: int, success_rate_pct: float) -> GeneratedIssue:
        """Generate issue for canary drill failures."""
        issue_id = f"canary-{datetime.now(timezone.utc).timestamp()}"

        title = f"🔥 Canary Drill Failure: {drill_type} ({success_rate_pct:.1f}% success)"

        body = f"""## Canary Drill Failure

**Drill Type:** {drill_type}
**Success Rate:** {success_rate_pct:.1f}%
**Failed Tests:** {failure_count}

### Description
Canary drill revealed failures in resilience test cases.

### Impact
System may not recover properly from failures. Production resilience may be compromised.

### Required Actions
1. Investigate each failed test case
2. Identify systemic issues
3. Apply fixes before next drill
4. Re-run drill to verify fixes

### Severity
This is a critical reliability issue that must be addressed.
"""

        issue = GeneratedIssue(
            issue_id=issue_id,
            title=title,
            body=body,
            assignee="@mbaetiong",  # Critical - needs immediate attention
            labels=["canary-drill", "reliability", "critical"],
            priority="critical",
            created_at=datetime.now(timezone.utc),
        )

        self.generated_issues.append(issue)
        logger.info(f"Generated canary drill failure issue: {issue.title}")
        return issue

    def get_generated_issues(self) -> List[GeneratedIssue]:
        """Get all generated issues."""
        return self.generated_issues

    def get_issues_by_priority(self, priority: str) -> List[GeneratedIssue]:
        """Get issues by priority level."""
        return [i for i in self.generated_issues if i.priority == priority]

    def get_unassigned_issues(self) -> List[GeneratedIssue]:
        """Get issues that haven't been assigned a GitHub link yet."""
        return [i for i in self.generated_issues if i.github_link is None]

    def mark_issue_created(self, issue_id: str, github_link: str) -> bool:
        """Mark issue as created in GitHub. Returns True if successful."""
        for issue in self.generated_issues:
            if issue.issue_id == issue_id:
                issue.github_link = github_link
                logger.info(f"Marked issue {issue_id} as created: {github_link}")
                return True
        return False

    def get_issue_summary(self) -> dict:
        """Get summary of generated issues."""
        by_priority = {}
        for issue in self.generated_issues:
            by_priority.setdefault(issue.priority, 0)
            by_priority[issue.priority] += 1

        return {
            "total_issues": len(self.generated_issues),
            "by_priority": by_priority,
            "created_in_github": sum(1 for i in self.generated_issues if i.github_link is not None),
            "pending_creation": sum(1 for i in self.generated_issues if i.github_link is None),
        }
