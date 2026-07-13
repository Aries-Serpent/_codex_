#!/usr/bin/env python3
"""
CodeQL Alert Categorizer - Phase 5 Continuous Monitoring

Automatically categorizes and triages CodeQL security alerts.
Integrates with GitHub API to fetch, categorize, and escalate findings.

Usage:
    python scripts/security/codeql_alert_categorizer.py --repo owner/repo
    python scripts/security/codeql_alert_categorizer.py --repo owner/repo --output .codex/security/alert_triage_report.json
"""

import json
import os
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class CodeQLAlert:
    """CodeQL Alert"""
    alert_id: int
    rule_id: str
    rule_severity: str  # critical, high, medium, low, note
    rule_security_severity: str  # high, medium, low
    message: str
    location: str
    status: str  # open, dismissed, fixed
    created_at: str
    updated_at: str
    dismissed_at: Optional[str]
    dismissed_reason: Optional[str]
    age_days: int
    category: str  # injection, auth, crypto, xss, dos, etc.
    false_positive: bool


class CodeQLAlertCategorizer:
    """Categorizes and triages CodeQL alerts"""

    # Mapping of rule patterns to categories
    CATEGORY_PATTERNS = {
        "injection": [
            "sql-injection", "command-injection", "log-injection",
            "ldap-injection", "xpath-injection", "code-injection"
        ],
        "auth": [
            "authentication", "authorization", "access-control",
            "insecure-random", "weak-cryptography"
        ],
        "crypto": [
            "cryptography", "encryption", "weak-crypto",
            "insecure-hash", "tls"
        ],
        "xss": [
            "cross-site-scripting", "xss", "dom-based-xss",
            "unsafe-html"
        ],
        "dos": [
            "dos", "denial-of-service", "regex-dos",
            "infinite-loop", "unbounded-loop"
        ],
        "information-disclosure": [
            "information-disclosure", "sensitive-data", "secrets",
            "exposed-credentials", "path-disclosure"
        ],
        "other": []
    }

    def __init__(self, repo: str):
        self.repo = repo
        self.token = os.getenv("GITHUB_TOKEN", "")

    def get_alerts(self) -> List[Dict]:
        """Fetch CodeQL alerts from GitHub API"""
        logger.info(f"Fetching CodeQL alerts from {self.repo}...")

        try:
            result = subprocess.run(
                [
                    "gh", "code-scanning", "list",
                    "-R", self.repo,
                    "--json",
                    "number,rule,message,location,createdAt,updatedAt,state,dismissedAt,dismissedReason",
                    "--state", "all",
                    "--limit", "1000"
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logger.error(f"Failed to fetch alerts: {result.stderr}")
                return []

            alerts = json.loads(result.stdout) if result.stdout else []
            logger.info(f"Found {len(alerts)} CodeQL alerts")
            return alerts

        except Exception as e:
            logger.error(f"Error fetching alerts: {e}")
            return []

    def _categorize_alert(self, rule_id: str) -> str:
        """Categorize alert based on rule ID"""
        rule_id_lower = rule_id.lower()

        for category, patterns in self.CATEGORY_PATTERNS.items():
            if category == "other":
                continue
            for pattern in patterns:
                if pattern in rule_id_lower:
                    return category

        return "other"

    def _is_false_positive(self, alert: Dict) -> bool:
        """Check if alert is known false positive"""
        # TODO: Load false positive registry from file
        return False

    def _parse_alert(self, alert: Dict) -> Optional[CodeQLAlert]:
        """Parse GitHub API alert into CodeQLAlert"""
        try:
            created_at = alert.get("createdAt", "")
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            age_days = (datetime.now(created_dt.tzinfo) - created_dt).days

            rule = alert.get("rule", {})
            rule_id = rule.get("id", "unknown")

            return CodeQLAlert(
                alert_id=alert.get("number", 0),
                rule_id=rule_id,
                rule_severity=rule.get("severity", "note"),
                rule_security_severity=rule.get("security_severity", "low"),
                message=alert.get("message", {}).get("text", ""),
                location=alert.get("location", {}).get("path", ""),
                status=alert.get("state", "open"),
                created_at=created_at,
                updated_at=alert.get("updatedAt", ""),
                dismissed_at=alert.get("dismissedAt"),
                dismissed_reason=alert.get("dismissedReason"),
                age_days=age_days,
                category=self._categorize_alert(rule_id),
                false_positive=self._is_false_positive(alert)
            )
        except Exception as e:
            logger.warning(f"Failed to parse alert: {e}")
            return None

    def categorize_alerts(self, alerts: List[Dict]) -> Dict[str, List[CodeQLAlert]]:
        """Categorize alerts by severity and category"""
        categorized = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "note": [],
            "dismissed": [],
            "fixed": []
        }

        for alert in alerts:
            parsed = self._parse_alert(alert)
            if not parsed:
                continue

            if parsed.status == "dismissed":
                categorized["dismissed"].append(parsed)
            elif parsed.status == "fixed":
                categorized["fixed"].append(parsed)
            elif parsed.rule_severity == "critical":
                categorized["critical"].append(parsed)
            elif parsed.rule_severity == "high":
                categorized["high"].append(parsed)
            elif parsed.rule_severity == "medium":
                categorized["medium"].append(parsed)
            elif parsed.rule_severity == "low":
                categorized["low"].append(parsed)
            else:
                categorized["note"].append(parsed)

        return categorized

    def generate_triage_report(self, alerts: List[Dict]) -> Dict:
        """Generate comprehensive triage report"""
        categorized = self.categorize_alerts(alerts)

        report = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_alerts": len(alerts),
            "by_severity": {
                "critical": len(categorized["critical"]),
                "high": len(categorized["high"]),
                "medium": len(categorized["medium"]),
                "low": len(categorized["low"]),
                "note": len(categorized["note"]),
                "dismissed": len(categorized["dismissed"]),
                "fixed": len(categorized["fixed"])
            },
            "alerts": {
                "critical": [asdict(a) for a in categorized["critical"]],
                "high": [asdict(a) for a in categorized["high"]],
                "medium": [asdict(a) for a in categorized["medium"]],
                "low": [asdict(a) for a in categorized["low"]],
                "note": [asdict(a) for a in categorized["note"]],
            },
            "escalation_required": {
                "critical": len(categorized["critical"]),
                "high": len(categorized["high"])
            },
            "slas": {
                "critical": "1 hour response",
                "high": "24 hours response",
                "medium": "7 days response",
                "low": "quarterly review"
            },
            "recommendations": self._generate_recommendations(categorized)
        }

        return report

    def _generate_recommendations(self, categorized: Dict[str, List]) -> List[str]:
        """Generate recommendations based on alerts"""
        recommendations = []

        if len(categorized["critical"]) > 0:
            recommendations.append(
                f"🔴 URGENT: {len(categorized['critical'])} critical alert(s) require immediate attention"
            )

        if len(categorized["high"]) > 5:
            recommendations.append(
                f"⚠️ HIGH: {len(categorized['high'])} high-severity alerts - prioritize remediation"
            )

        # Check for patterns
        categories_with_alerts = {}
        for severity_list in categorized.values():
            for alert in severity_list:
                cat = alert.category
                categories_with_alerts[cat] = categories_with_alerts.get(cat, 0) + 1

        high_pattern_cats = [cat for cat, count in categories_with_alerts.items() if count > 3]
        if high_pattern_cats:
            recommendations.append(
                f"📊 Pattern: Multiple alerts in {', '.join(high_pattern_cats)} - consider architectural review"
            )

        # Check age
        old_alerts = [a for severity in categorized.values() for a in severity if a.age_days > 30]
        if old_alerts:
            recommendations.append(
                f"⏱️ {len(old_alerts)} alert(s) older than 30 days - expedite resolution"
            )

        return recommendations

    def save_report(self, report: Dict, output_file: str):
        """Save triage report to JSON"""
        logger.info(f"Saving triage report to {output_file}...")

        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"Triage report saved")

    def generate_summary_markdown(self, report: Dict) -> str:
        """Generate markdown summary from report"""
        lines = ["# CodeQL Alert Triage Summary\n"]
        lines.append(f"**Generated**: {report.get('generated_at')}\n")
        lines.append(f"**Total Alerts**: {report.get('total_alerts')}\n\n")

        # Severity summary
        by_severity = report.get("by_severity", {})
        lines.append("## Alert Distribution\n")
        lines.append("| Severity | Count | SLA | Status |")
        lines.append("|----------|-------|-----|--------|")
        
        severity_emoji = {
            "critical": "🔴",
            "high": "🟠",
            "medium": "🟡",
            "low": "🟢",
            "note": "⚪"
        }

        for severity in ["critical", "high", "medium", "low", "note"]:
            count = by_severity.get(severity, 0)
            sla = report.get("slas", {}).get(severity, "N/A")
            emoji = severity_emoji.get(severity, "")
            lines.append(f"| {emoji} {severity.upper()} | {count} | {sla} | {'⚠️' if count > 0 else '✅'} |")

        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            lines.append("\n## 🎯 Recommendations\n")
            for rec in recommendations:
                lines.append(f"- {rec}\n")

        return "".join(lines)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Categorize CodeQL alerts")
    parser.add_argument("--repo", type=str, required=True, help="Repository (owner/repo)")
    parser.add_argument("--output", type=str, default=".codex/security/alert_triage_report.json", help="Output file")
    parser.add_argument("--markdown", type=str, help="Generate markdown summary to file")

    args = parser.parse_args()

    try:
        categorizer = CodeQLAlertCategorizer(args.repo)
        alerts = categorizer.get_alerts()
        
        if not alerts:
            logger.warning("No alerts to categorize")
            sys.exit(0)

        report = categorizer.generate_triage_report(alerts)
        categorizer.save_report(report, args.output)

        # Generate markdown if requested
        if args.markdown:
            markdown = categorizer.generate_summary_markdown(report)
            os.makedirs(os.path.dirname(args.markdown) or ".", exist_ok=True)
            with open(args.markdown, "w") as f:
                f.write(markdown)
            logger.info(f"Markdown summary saved to {args.markdown}")

        # Print summary
        severity = report.get("by_severity", {})
        print("\n📊 Alert Summary:")
        print(f"  Critical: {severity.get('critical', 0)}")
        print(f"  High: {severity.get('high', 0)}")
        print(f"  Medium: {severity.get('medium', 0)}")
        print(f"  Low: {severity.get('low', 0)}")

        sys.exit(0)

    except Exception as e:
        logger.error(f"❌ Categorization failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
