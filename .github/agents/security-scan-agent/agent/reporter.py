"""
Security Reporter Module - AFTERMATH Phase

#AFTERMATH_PATTERN_IDENTIFIED: security_metrics_and_learning
Implements comprehensive security metrics tracking and lesson learning.
"""

import json
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

# Add core to path for CognitiveBrain access
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "core"))
from cognitive_brain import CognitiveBrain


@dataclass
class SecurityReport:
    """Comprehensive security scan report."""
    scan_date: str
    repository: str
    total_vulnerabilities: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    auto_fixed_count: int
    remediations_applied: int
    cvss_scores: list[float]
    average_cvss: float
    risk_score: float
    compliance_status: dict[str, bool]
    top_issues: list[dict[str, Any]]
    recommendations: list[str]
    lessons_learned: list[str]
    metadata: dict[str, Any]


class SecurityReporter:
    """
    Security Reporter - AFTERMATH Phase

    #AFTERMATH_PATTERN_IDENTIFIED: security_outcome_analysis

    Generates comprehensive reports and updates cognitive brain:
    - Security metrics tracking
    - Vulnerability trend analysis
    - Remediation effectiveness
    - Lesson learning
    - Recommendations for future scans
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.brain = CognitiveBrain(Path(".codex/brain.db"))

    def aftermath(self, result: dict[str, Any], context: dict[str, Any],
                  decision: dict[str, Any]) -> None:
        """
        AFTERMATH: Generate reports, record metrics, and learn.

        #AFTERMATH_PATTERN_IDENTIFIED: comprehensive_security_reporting

        Args:
            result: Remediation results from ACT phase
            context: Scan context from PERCEIVE phase
            decision: Analysis from DECIDE phase
        """
        # Generate comprehensive report
        report = self._generate_report(result, context, decision)

        # Record metrics in cognitive brain
        self._record_metrics(report)

        # Store security patterns
        self._store_patterns(context, decision)

        # Generate lessons learned
        lessons = self._generate_lessons(result, context, decision)

        # Store lessons in cognitive brain
        for lesson in lessons:
            self._store_lesson(lesson)

        # Generate recommendations
        recommendations = self._generate_recommendations(report)

        # Save report files
        self._save_report_json(report)
        self._save_report_markdown(report, recommendations)

        #AFTERMATH_METRIC: scan_completed = True
        #AFTERMATH_METRIC: total_vulnerabilities = report.total_vulnerabilities
        #AFTERMATH_METRIC: critical_vulnerabilities = report.critical_count
        #AFTERMATH_LESSON_LEARNED: security_scan_patterns_identified

        print(f"✅ Security scan complete: {report.total_vulnerabilities} vulnerabilities found")
        print(f"   Critical: {report.critical_count}, High: {report.high_count}")
        print(f"   Auto-fixed: {report.auto_fixed_count}")

    def _generate_report(self, result: dict[str, Any], context: dict[str, Any],
                        decision: dict[str, Any]) -> SecurityReport:
        """
        Generate comprehensive security report.

        #AFTERMATH_PATTERN_IDENTIFIED: security_report_generation
        """
        analyses = decision.get("analyses", [])

        # Count by severity
        critical = sum(1 for a in analyses if a.severity.value == "critical")
        high = sum(1 for a in analyses if a.severity.value == "high")
        medium = sum(1 for a in analyses if a.severity.value == "medium")
        low = sum(1 for a in analyses if a.severity.value == "low")

        # Collect CVSS scores
        cvss_scores = [a.cvss_score for a in analyses]
        avg_cvss = sum(cvss_scores) / len(cvss_scores) if cvss_scores else 0.0

        # Calculate overall risk score
        risk_score = self._calculate_risk_score(analyses)

        # Assess compliance
        compliance = self._assess_compliance(analyses)

        # Get top issues
        top_issues = self._get_top_issues(analyses)

        # Generate lessons
        lessons = self._generate_lessons(result, context, decision)

        return SecurityReport(
            scan_date=datetime.now().isoformat(),
            repository=str(self.repo_path),
            total_vulnerabilities=len(analyses),
            critical_count=critical,
            high_count=high,
            medium_count=medium,
            low_count=low,
            auto_fixed_count=result.get("auto_fixed_count", 0),
            remediations_applied=result.get("auto_fixed_count", 0),
            cvss_scores=cvss_scores,
            average_cvss=avg_cvss,
            risk_score=risk_score,
            compliance_status=compliance,
            top_issues=top_issues,
            recommendations=decision.get("recommendations", []),
            lessons_learned=lessons,
            metadata={
                "tools_used": context.get("scan_metadata", {}).get("tools_used", []),
                "scan_duration": "N/A"  # Would track in real implementation
            }
        )

    def _record_metrics(self, report: SecurityReport) -> None:
        """
        Record security metrics in cognitive brain.

        #AFTERMATH_METRIC: security_scan_metrics
        """
        try:
            session_id = self.brain.start_session(
                agent_name="security-scan-agent",
                task_description="Security vulnerability scan"
            )

            # Record metrics
            metrics = {
                "total_vulnerabilities": report.total_vulnerabilities,
                "critical_count": report.critical_count,
                "high_count": report.high_count,
                "medium_count": report.medium_count,
                "low_count": report.low_count,
                "average_cvss": report.average_cvss,
                "risk_score": report.risk_score,
                "auto_fixed": report.auto_fixed_count,
                "compliance_passing": sum(1 for v in report.compliance_status.values() if v)
            }

            for key, value in metrics.items():
                self.brain.record_metric(
                    session_id=session_id,
                    metric_name=key,
                    metric_value=value
                )

            self.brain.end_session(session_id, success=True)
        except Exception as e:
            print(f"Warning: Failed to record metrics: {e}")

    def _store_patterns(self, context: dict[str, Any], decision: dict[str, Any]) -> None:
        """
        Store security patterns in cognitive brain.

        #AFTERMATH_PATTERN_IDENTIFIED: pattern_storage
        """
        try:
            analyses = decision.get("analyses", [])

            for analysis in analyses[:10]:  # Top 10
                pattern_data = {
                    "severity": analysis.severity.value,
                    "cwe_id": analysis.metadata.get("cwe_id"),
                    "cvss_score": analysis.cvss_score,
                    "exploitability": analysis.exploitability,
                    "remediation_strategy": analysis.remediation_strategy
                }

                self.brain.store_pattern(
                    pattern_type="security_vulnerability",
                    pattern_data=pattern_data,
                    confidence=0.8,
                    source="security-scan-agent"
                )
        except Exception as e:
            print(f"Warning: Failed to store patterns: {e}")

    def _generate_lessons(self, result: dict[str, Any], context: dict[str, Any],
                         decision: dict[str, Any]) -> list[str]:
        """
        Generate lessons learned from security scan.

        #AFTERMATH_LESSON_LEARNED: security_scan_insights
        """
        lessons = []

        analyses = decision.get("analyses", [])

        # Lesson 1: Most common vulnerability types
        if analyses:
            cwe_counts = {}
            for a in analyses:
                cwe = a.metadata.get("cwe_id", "Unknown")
                cwe_counts[cwe] = cwe_counts.get(cwe, 0) + 1

            top_cwe = max(cwe_counts.items(), key=lambda x: x[1])
            lessons.append(f"Most common vulnerability type: {top_cwe[0]} ({top_cwe[1]} occurrences)")

        # Lesson 2: Auto-fixable ratio
        auto_fixable = sum(1 for a in analyses if a.auto_fixable)
        if analyses:
            ratio = auto_fixable / len(analyses)
            lessons.append(f"Auto-fixable vulnerabilities: {ratio:.1%} ({auto_fixable}/{len(analyses)})")

        # Lesson 3: Dependency vulnerabilities
        dep_vulns = [a for a in analyses if a.remediation_strategy == "dependency_upgrade"]
        if dep_vulns:
            lessons.append(f"Dependency vulnerabilities found: {len(dep_vulns)} - recommend regular updates")

        # Lesson 4: Critical vulnerabilities
        critical = [a for a in analyses if a.severity.value == "critical"]
        if critical:
            lessons.append(f"Critical vulnerabilities require immediate attention: {len(critical)}")

        # Lesson 5: Compliance gaps
        compliance = self._assess_compliance(analyses)
        failing = [k for k, v in compliance.items() if not v]
        if failing:
            lessons.append(f"Compliance gaps identified: {', '.join(failing)}")

        return lessons

    def _store_lesson(self, lesson: str) -> None:
        """Store individual lesson in cognitive brain."""
        try:
            self.brain.store_lesson(
                category="security_scanning",
                content=lesson,
                confidence=0.85,
                source="security-scan-agent"
            )
        except Exception as e:
            print(f"Warning: Failed to store lesson: {e}")

    def _calculate_risk_score(self, analyses: list[Any]) -> float:
        """Calculate overall risk score (0.0-10.0)."""
        if not analyses:
            return 0.0

        # Weighted average of risk scores
        total_risk = sum(a.risk_score for a in analyses)
        return min(10.0, total_risk / len(analyses))

    def _assess_compliance(self, analyses: list[Any]) -> dict[str, bool]:
        """Assess compliance with security frameworks."""
        compliance = {
            "OWASP_TOP_10": True,
            "PCI_DSS": True,
            "SOC2": True,
            "HIPAA": True
        }

        for analysis in analyses:
            # Check for OWASP violations
            if "OWASP_TOP_10" in analysis.compliance_impact:
                compliance["OWASP_TOP_10"] = False

            # Check for PCI-DSS violations
            if "PCI_DSS" in analysis.compliance_impact:
                compliance["PCI_DSS"] = False

            # Check for SOC2 violations
            if "SOC2" in analysis.compliance_impact:
                compliance["SOC2"] = False

            # Critical/high = HIPAA concern
            if analysis.severity.value in ["critical", "high"]:
                compliance["HIPAA"] = False

        return compliance

    def _get_top_issues(self, analyses: list[Any], limit: int = 5) -> list[dict[str, Any]]:
        """Get top security issues by risk score."""
        sorted_analyses = sorted(analyses, key=lambda a: a.risk_score, reverse=True)

        return [
            {
                "id": a.finding_id,
                "severity": a.severity.value,
                "cvss_score": a.cvss_score,
                "risk_score": a.risk_score,
                "strategy": a.remediation_strategy,
                "auto_fixable": a.auto_fixable
            }
            for a in sorted_analyses[:limit]
        ]

    def _generate_recommendations(self, report: SecurityReport) -> list[str]:
        """Generate actionable recommendations."""
        recommendations = []

        # Critical vulnerabilities
        if report.critical_count > 0:
            recommendations.append(
                f"🔴 URGENT: Address {report.critical_count} critical vulnerabilities immediately"
            )

        # Auto-fixable issues
        if report.auto_fixed_count < report.total_vulnerabilities:
            remaining = report.total_vulnerabilities - report.auto_fixed_count
            recommendations.append(
                f"Apply automated fixes to reduce {remaining} remaining vulnerabilities"
            )

        # Compliance
        failing_compliance = [k for k, v in report.compliance_status.items() if not v]
        if failing_compliance:
            recommendations.append(
                f"Address compliance gaps: {', '.join(failing_compliance)}"
            )

        # Risk score
        if report.risk_score > 7.0:
            recommendations.append(
                f"Overall risk score is high ({report.risk_score:.1f}/10.0) - prioritize remediation"
            )

        # Regular scanning
        recommendations.append(
            "Schedule regular security scans (weekly recommended)"
        )

        return recommendations

    def _save_report_json(self, report: SecurityReport) -> None:
        """Save report as JSON."""
        report_path = self.repo_path / ".codex" / "security_scan_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report_dict = {
            "scan_date": report.scan_date,
            "repository": report.repository,
            "summary": {
                "total": report.total_vulnerabilities,
                "critical": report.critical_count,
                "high": report.high_count,
                "medium": report.medium_count,
                "low": report.low_count,
                "auto_fixed": report.auto_fixed_count
            },
            "metrics": {
                "average_cvss": report.average_cvss,
                "risk_score": report.risk_score
            },
            "compliance": report.compliance_status,
            "top_issues": report.top_issues,
            "recommendations": report.recommendations,
            "lessons_learned": report.lessons_learned
        }

        report_path.write_text(json.dumps(report_dict, indent=2))

    def _save_report_markdown(self, report: SecurityReport, recommendations: list[str]) -> None:
        """Save report as Markdown."""
        report_path = self.repo_path / ".codex" / "SECURITY_SCAN_REPORT.md"

        content = f"""# Security Scan Report

**Date**: {report.scan_date}
**Repository**: {report.repository}

## Executive Summary

- **Total Vulnerabilities**: {report.total_vulnerabilities}
- **Critical**: {report.critical_count}
- **High**: {report.high_count}
- **Medium**: {report.medium_count}
- **Low**: {report.low_count}
- **Auto-Fixed**: {report.auto_fixed_count}

## Risk Assessment

- **Average CVSS Score**: {report.average_cvss:.1f}/10.0
- **Overall Risk Score**: {report.risk_score:.1f}/10.0

## Compliance Status

"""
        for framework, passing in report.compliance_status.items():
            status = "✅ PASS" if passing else "❌ FAIL"
            content += f"- **{framework}**: {status}\n"

        content += f"""
## Top {len(report.top_issues)} Security Issues

"""
        for i, issue in enumerate(report.top_issues, 1):
            content += f"""
### {i}. Issue {issue['id']}

- **Severity**: {issue['severity'].upper()}
- **CVSS Score**: {issue['cvss_score']:.1f}
- **Risk Score**: {issue['risk_score']:.1f}
- **Strategy**: {issue['strategy']}
- **Auto-fixable**: {'Yes' if issue['auto_fixable'] else 'No'}

"""

        content += """
## Recommendations

"""
        for rec in recommendations:
            content += f"- {rec}\n"

        content += """
## Lessons Learned

"""
        for lesson in report.lessons_learned:
            content += f"- {lesson}\n"

        report_path.write_text(content)
