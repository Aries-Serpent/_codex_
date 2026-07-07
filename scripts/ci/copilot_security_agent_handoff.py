#!/usr/bin/env python3
"""
Copilot Security Agent Handoff Script

Purpose:
    Enables Copilot agents to efficiently fetch, filter, and triage security findings
    for remediation. Provides structured handoff with agent-specific formatting.

Usage:
    python scripts/ci/copilot_security_agent_handoff.py \
      --run-id 12345 \
      --agent codeql-alert-resolution-agent \
      --format json \
      --output findings-for-agent.json

Environment Variables:
    GITHUB_REPOSITORY: Repository name (owner/repo)
    GITHUB_RUN_ID: GitHub Actions run ID
    GH_TOKEN: GitHub API token
"""

import argparse
import json
import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AgentHandoff:
    """Handoff data for a specific agent"""
    agent_id: str
    findings_count: int
    findings: List[Dict[str, Any]]
    summary: Dict[str, Any]
    recommendations: List[str]


class CopilotSecurityAgentHandoff:
    """Manages security findings handoff to Copilot agents"""

    def __init__(self, findings_json: str):
        self.findings_data = None
        self.findings_json = Path(findings_json)
        self._load_findings()

    def _load_findings(self) -> None:
        """Load findings from JSON file"""
        if not self.findings_json.exists():
            logger.error(f"Findings file not found: {self.findings_json}")
            raise FileNotFoundError(f"Findings file not found: {self.findings_json}")

        with open(self.findings_json, "r") as f:
            self.findings_data = json.load(f)

        logger.info(f"Loaded {self.findings_data['summary']['total_findings']} findings")

    def handoff_for_agent(self, agent_id: str) -> AgentHandoff:
        """Prepare findings handoff for specific agent"""
        logger.info(f"Preparing handoff for agent: {agent_id}")

        # Filter findings for this agent
        all_findings = self.findings_data.get("finding_index", [])
        agent_findings = [f for f in all_findings if f.get("agent_assignee") == agent_id]

        logger.info(f"Found {len(agent_findings)} findings for agent {agent_id}")

        # Build agent-specific handoff
        handoff = self._format_for_agent(agent_id, agent_findings)
        return handoff

    def _format_for_agent(self, agent_id: str, findings: List[Dict[str, Any]]) -> AgentHandoff:
        """Format findings specific to agent type"""
        if agent_id == "codeql-alert-resolution-agent":
            return self._format_for_codeql(findings)
        elif agent_id == "dependency-security-review-agent":
            return self._format_for_dependency(findings)
        elif agent_id == "unified-security-scanner":
            return self._format_for_semgrep(findings)
        elif agent_id == "secret-detection-agent":
            return self._format_for_secrets(findings)
        else:
            return self._format_generic(agent_id, findings)

    def _format_for_codeql(self, findings: List[Dict[str, Any]]) -> AgentHandoff:
        """Format for CodeQL alert resolution agent"""
        # Group by CWE
        by_cwe = {}
        for f in findings:
            cwe = f.get("cwe_id", "UNKNOWN")
            if cwe not in by_cwe:
                by_cwe[cwe] = []
            by_cwe[cwe].append(f)

        recommendations = [
            "1. Start with CRITICAL CWE findings",
            "2. For each CWE, identify common pattern across instances",
            "3. Apply fix pattern once, validate with codeql-action/analyze",
            "4. Use codeql --disable-default-queries if fixing specific CWE",
            "5. Dismiss false positives with evidence comment",
            "6. Document all fixes in PR description",
        ]

        summary = {
            "total": len(findings),
            "by_severity": self._count_by_severity(findings),
            "by_cwe": {cwe: len(instances) for cwe, instances in by_cwe.items()},
            "top_cwe": sorted(by_cwe.items(), key=lambda x: len(x[1]), reverse=True)[:5],
        }

        return AgentHandoff(
            agent_id="codeql-alert-resolution-agent",
            findings_count=len(findings),
            findings=findings,
            summary=summary,
            recommendations=recommendations,
        )

    def _format_for_dependency(self, findings: List[Dict[str, Any]]) -> AgentHandoff:
        """Format for dependency security review agent"""
        # Group by package
        by_package = {}
        for f in findings:
            pkg = f.get("package", "UNKNOWN")
            if pkg not in by_package:
                by_package[pkg] = []
            by_package[pkg].append(f)

        recommendations = [
            "1. For each package, check if safe upgrade available",
            "2. Prioritize CRITICAL severity vulnerabilities",
            "3. Update requirements.txt with pinned versions",
            "4. Run pip-audit locally to verify fix",
            "5. Check for transitive dependency conflicts",
            "6. Document why upgrade needed vs why cannot upgrade",
        ]

        summary = {
            "total": len(findings),
            "by_severity": self._count_by_severity(findings),
            "by_package": {pkg: len(instances) for pkg, instances in by_package.items()},
            "packages_affected": len(by_package),
        }

        return AgentHandoff(
            agent_id="dependency-security-review-agent",
            findings_count=len(findings),
            findings=findings,
            summary=summary,
            recommendations=recommendations,
        )

    def _format_for_semgrep(self, findings: List[Dict[str, Any]]) -> AgentHandoff:
        """Format for Semgrep SAST scanner"""
        # Group by rule
        by_rule = {}
        for f in findings:
            rule = f.get("rule_id", "UNKNOWN")
            if rule not in by_rule:
                by_rule[rule] = []
            by_rule[rule].append(f)

        recommendations = [
            "1. Review rule documentation for fix guidance",
            "2. Identify common anti-pattern across instances",
            "3. Propose PR with pattern-based fix",
            "4. Run semgrep locally to validate fix",
            "5. For false positives, update .semgrep.yml inline-comments",
            "6. Consider relaxing rule if too many FP",
        ]

        summary = {
            "total": len(findings),
            "by_severity": self._count_by_severity(findings),
            "by_rule": {rule: len(instances) for rule, instances in by_rule.items()},
        }

        return AgentHandoff(
            agent_id="unified-security-scanner",
            findings_count=len(findings),
            findings=findings,
            summary=summary,
            recommendations=recommendations,
        )

    def _format_for_secrets(self, findings: List[Dict[str, Any]]) -> AgentHandoff:
        """Format for secret detection agent"""
        recommendations = [
            "1. For each finding, determine if real secret or false positive",
            "2. If real secret: rotate credential immediately in vault",
            "3. Remove secret from file (do NOT commit hash)",
            "4. Add <!-- pragma: allowlist secret --> for FP",
            "5. Update .secrets.baseline",
            "6. Document why secret was in repo in PR",
        ]

        summary = {
            "total": len(findings),
            "requires_rotation": len([f for f in findings if not f.get("status", "").startswith("flagged")]),
            "can_allowlist": len([f for f in findings if f.get("status", "").startswith("flagged")]),
        }

        return AgentHandoff(
            agent_id="secret-detection-agent",
            findings_count=len(findings),
            findings=findings,
            summary=summary,
            recommendations=recommendations,
        )

    def _format_generic(self, agent_id: str, findings: List[Dict[str, Any]]) -> AgentHandoff:
        """Generic format for unknown agents"""
        recommendations = [
            "1. Review all findings carefully",
            "2. Identify common pattern or root cause",
            "3. Propose comprehensive fix",
            "4. Validate fix with re-scan",
            "5. Document changes in PR",
        ]

        summary = {
            "total": len(findings),
            "by_severity": self._count_by_severity(findings),
            "by_tool": self._count_by_tool(findings),
        }

        return AgentHandoff(
            agent_id=agent_id,
            findings_count=len(findings),
            findings=findings,
            summary=summary,
            recommendations=recommendations,
        )

    def _count_by_severity(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count findings by severity"""
        counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0, "INFO": 0}
        for f in findings:
            severity = f.get("severity", "INFO")
            counts[severity] = counts.get(severity, 0) + 1
        return counts

    def _count_by_tool(self, findings: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count findings by tool"""
        counts = {}
        for f in findings:
            tool = f.get("tool", "unknown")
            counts[tool] = counts.get(tool, 0) + 1
        return counts

    def save_handoff(self, agent_id: str, output_path: str, format: str = "json") -> None:
        """Save handoff for agent"""
        handoff = self.handoff_for_agent(agent_id)
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        if format == "json":
            output_dict = {
                "agent_id": handoff.agent_id,
                "findings_count": handoff.findings_count,
                "findings": handoff.findings,
                "summary": handoff.summary,
                "recommendations": handoff.recommendations,
            }
            with open(output_file, "w") as f:
                json.dump(output_dict, f, indent=2)
        elif format == "markdown":
            md_lines = [
                f"# Security Findings Handoff for {handoff.agent_id}",
                "",
                f"## Summary",
                f"- **Total Findings:** {handoff.findings_count}",
            ]
            
            for key, value in handoff.summary.items():
                if isinstance(value, dict):
                    md_lines.append(f"- **{key}:** {value}")
                elif isinstance(value, list):
                    md_lines.append(f"- **{key}:** {len(value)} items")
                else:
                    md_lines.append(f"- **{key}:** {value}")
            
            md_lines.extend([
                "",
                "## Recommendations",
                "",
            ])
            
            for rec in handoff.recommendations:
                md_lines.append(f"- {rec}")
            
            md_lines.extend([
                "",
                "## Findings",
                "",
            ])
            
            for finding in handoff.findings:
                md_lines.append(f"### {finding.get('title', 'Untitled')}")
                md_lines.append(f"- **Severity:** {finding.get('severity', 'UNKNOWN')}")
                md_lines.append(f"- **File:** `{finding.get('file', 'N/A')}`")
                md_lines.append(f"- **Tool:** {finding.get('tool', 'N/A')}")
                md_lines.append("")
            
            with open(output_file, "w") as f:
                f.write("\n".join(md_lines))

        logger.info(f"Handoff saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Prepare security findings handoff for Copilot agents"
    )
    parser.add_argument(
        "--findings-json",
        default=".codex/security-findings-comprehensive.json",
        help="Path to comprehensive findings JSON file",
    )
    parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID to prepare handoff for",
    )
    parser.add_argument(
        "--format",
        default="json",
        choices=["json", "markdown"],
        help="Output format",
    )
    parser.add_argument(
        "--output",
        help="Output file path (defaults to agent-specific path)",
    )

    args = parser.parse_args()

    if not args.output:
        args.output = f".codex/security-handoff-{args.agent}.{args.format}"

    try:
        handoff = CopilotSecurityAgentHandoff(args.findings_json)
        handoff.save_handoff(args.agent, args.output, args.format)
        logger.info("✅ Handoff preparation complete")
        return 0
    except Exception as e:
        logger.error(f"❌ Handoff preparation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
