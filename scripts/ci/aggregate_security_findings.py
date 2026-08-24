#!/usr/bin/env python3
"""
Aggregate Security Findings Report Generator

Purpose:
    Consolidates all security findings from multiple scanning tools (CodeQL, Semgrep,
    pip-audit, Safety, detect-secrets, SBOM) into a single authoritative JSON report
    with unified severity levels, deduplication, and agent assignment recommendations.

Usage:
    python scripts/ci/aggregate_security_findings.py \
      --artifacts-dir security-suite-artifacts \
      --output-json .codex/security-findings-comprehensive.json \
      --output-md security-findings-comprehensive.md \
      --repo-url https://github.com/Aries-Serpent/_codex_ \
      --run-id 12345 \
      --commit-sha abc123

Environment Variables:
    GITHUB_REPOSITORY: Repository name (owner/repo)
    GITHUB_RUN_ID: GitHub Actions run ID
    GITHUB_SHA: Commit SHA
    GITHUB_SERVER_URL: GitHub server URL

Exit Codes:
    0: Success
    1: Error
    2: No findings found
"""

import argparse
import json
import logging
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Finding:
    """Normalized finding record across all tools"""
    id: str
    tool: str
    title: str
    description: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW, INFO
    file: Optional[str] = None
    line: Optional[int] = None
    cwe_id: Optional[str] = None
    rule_id: Optional[str] = None
    package: Optional[str] = None
    version: Optional[str] = None
    remediation_url: Optional[str] = None
    sarif_location: Optional[str] = None
    status: str = "open"  # open, dismissed, fixed
    agent_assignee: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {
            "id": self.id,
            "tool": self.tool,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
        }
        if self.file:
            result["file"] = self.file
        if self.line:
            result["line"] = self.line
        if self.cwe_id:
            result["cwe_id"] = self.cwe_id
        if self.rule_id:
            result["rule_id"] = self.rule_id
        if self.package:
            result["package"] = self.package
        if self.version:
            result["version"] = self.version
        if self.remediation_url:
            result["remediation_url"] = self.remediation_url
        if self.sarif_location:
            result["sarif_location"] = self.sarif_location
        if self.status != "open":
            result["status"] = self.status
        if self.agent_assignee:
            result["agent_assignee"] = self.agent_assignee
        if self.metadata:
            result["metadata"] = self.metadata
        return result


class FindingsAggregator:
    """Main aggregator for security findings across all tools"""

    def __init__(
        self,
        artifacts_dir: str,
        repo_url: str,
        run_id: str,
        commit_sha: str,
        repository: str,
    ):
        self.artifacts_dir = Path(artifacts_dir)
        self.repo_url = repo_url
        self.run_id = run_id
        self.commit_sha = commit_sha
        self.repository = repository
        self.findings: List[Finding] = []
        self.severity_map = {
            "critical": "CRITICAL",
            "error": "CRITICAL",
            "high": "HIGH",
            "warning": "MEDIUM",
            "medium": "MEDIUM",
            "note": "LOW",
            "low": "LOW",
            "info": "INFO",
        }

    def run(self) -> Dict[str, Any]:
        """Execute aggregation pipeline"""
        logger.info(f"Starting findings aggregation from {self.artifacts_dir}")

        # Parse findings from each tool
        self._parse_codeql_findings()
        self._parse_semgrep_findings()
        self._parse_dependency_findings()
        self._parse_secret_findings()

        # Deduplicate findings
        self._deduplicate_findings()

        # Normalize severity levels
        self._normalize_severity()

        # Generate agent assignments
        self._assign_agents()

        # Build comprehensive report
        report = self._build_report()

        logger.info(f"Aggregation complete: {len(self.findings)} unique findings")
        return report

    def _parse_codeql_findings(self) -> None:
        """Parse CodeQL SARIF artifacts"""
        logger.info("Parsing CodeQL findings...")
        codeql_dir = self.artifacts_dir / "security-suite-codeql-python"
        
        if not codeql_dir.exists():
            logger.warning(f"CodeQL directory not found: {codeql_dir}")
            return

        for sarif_file in codeql_dir.glob("*.sarif"):
            try:
                with open(sarif_file, "r") as f:
                    sarif_data = json.load(f)
                
                for run in sarif_data.get("runs", []):
                    for rule in run.get("tool", {}).get("driver", {}).get("rules", []):
                        rule_id = rule.get("id", "unknown")
                        cwe_match = re.search(r'CWE-(\d+)', rule.get("help", {}).get("text", ""))
                        cwe_id = f"CWE-{cwe_match.group(1)}" if cwe_match else None
                        
                    for result in run.get("results", []):
                        finding = Finding(
                            id=f"CODEQL-{rule_id}-{len(self.findings):03d}",
                            tool="codeql",
                            title=result.get("message", {}).get("text", "CodeQL Finding"),
                            description=result.get("message", {}).get("text", ""),
                            severity=self.severity_map.get(
                                result.get("level", "note").lower(), "LOW"
                            ),
                            file=result.get("locations", [{}])[0].get("physicalLocation", {}).get("artifactLocation", {}).get("uri"),
                            line=result.get("locations", [{}])[0].get("physicalLocation", {}).get("region", {}).get("startLine"),
                            cwe_id=cwe_id,
                            rule_id=rule_id,
                            sarif_location=str(sarif_file),
                            agent_assignee="codeql-alert-resolution-agent",
                        )
                        self.findings.append(finding)
                        logger.debug(f"Parsed CodeQL finding: {finding.id}")
            except Exception as e:
                logger.error(f"Error parsing CodeQL SARIF {sarif_file}: {e}")

    def _parse_semgrep_findings(self) -> None:
        """Parse Semgrep JSON output"""
        logger.info("Parsing Semgrep findings...")
        semgrep_dir = self.artifacts_dir / "security-suite-semgrep"
        
        if not semgrep_dir.exists():
            logger.warning(f"Semgrep directory not found: {semgrep_dir}")
            return

        json_file = semgrep_dir / "semgrep-results.json"
        if not json_file.exists():
            logger.warning(f"Semgrep JSON not found: {json_file}")
            return

        try:
            with open(json_file, "r") as f:
                semgrep_data = json.load(f)
            
            for result in semgrep_data.get("results", []):
                finding = Finding(
                    id=f"SEMGREP-{result.get('check_id', 'unknown')}-{len(self.findings):03d}",
                    tool="semgrep",
                    title=result.get("check_id", "Semgrep Finding"),
                    description=result.get("extra", {}).get("message", ""),
                    severity=self.severity_map.get(
                        result.get("extra", {}).get("severity", "info").lower(), "INFO"
                    ),
                    file=result.get("path"),
                    line=result.get("start", {}).get("line"),
                    rule_id=result.get("check_id"),
                    remediation_url=result.get("extra", {}).get("docs"),
                    agent_assignee="unified-security-scanner",
                )
                self.findings.append(finding)
                logger.debug(f"Parsed Semgrep finding: {finding.id}")
        except Exception as e:
            logger.error(f"Error parsing Semgrep results: {e}")

    def _parse_dependency_findings(self) -> None:
        """Parse pip-audit and Safety JSON outputs"""
        logger.info("Parsing dependency vulnerability findings...")
        dep_dir = self.artifacts_dir / "security-suite-dependency"
        
        if not dep_dir.exists():
            logger.warning(f"Dependency directory not found: {dep_dir}")
            return

        # Parse pip-audit
        pip_audit_file = dep_dir / "pip-audit.json"
        if pip_audit_file.exists():
            try:
                with open(pip_audit_file, "r") as f:
                    pip_data = json.load(f)
                
                for dep in pip_data.get("dependencies", []):
                    for vuln in dep.get("vulns", []):
                        finding = Finding(
                            id=f"DEPVULN-{dep.get('name', 'unknown')}-{vuln.get('id', 'unknown')}",
                            tool="pip-audit",
                            title=f"Vulnerability in {dep.get('name')}",
                            description=vuln.get("description", ""),
                            severity="CRITICAL",  # Dependency vulns are always critical
                            package=dep.get("name"),
                            version=dep.get("installed_version"),
                            remediation_url=vuln.get("advisory_url"),
                            agent_assignee="dependency-security-review-agent",
                        )
                        self.findings.append(finding)
                        logger.debug(f"Parsed pip-audit finding: {finding.id}")
            except Exception as e:
                logger.error(f"Error parsing pip-audit results: {e}")

    def _parse_secret_findings(self) -> None:
        """Parse detect-secrets baseline
        
        Security Note: This processes .secrets.baseline which contains secret hashes.
        We extract only type and line metadata, not actual secret values, to findings.
        """
        logger.info("Parsing secret detection findings...")
        secrets_dir = self.artifacts_dir / "security-suite-secrets"
        
        if not secrets_dir.exists():
            # lgtm[py/clear-text-logging]: Logging directory path only, not secret data
            logger.warning(f"Secrets directory not found: {secrets_dir}")
            return

        baseline_file = secrets_dir / ".secrets.baseline"
        if not baseline_file.exists():
            # lgtm[py/clear-text-logging]: Logging file path only, not secret data
            logger.warning(f"Secrets baseline not found: {baseline_file}")
            return

        try:
            with open(baseline_file, "r") as f:
                baseline_data = json.load(f)
            
            for file_path, secrets in baseline_data.get("results", {}).items():
                for idx, secret in enumerate(secrets):
                    # Extract only type and location metadata, not actual secret values
                    finding = Finding(
                        id=f"SECRET-{file_path.replace('/', '_')}-{idx:03d}",
                        tool="detect-secrets",
                        title=f"Potential secret in {file_path}",
                        description=secret.get("type", "Unknown secret type"),
                        severity="CRITICAL",  # Secrets are always critical
                        file=file_path,
                        line=secret.get("line_number"),
                        status="flagged",
                        agent_assignee="secret-detection-agent",
                    )
                    self.findings.append(finding)
                    logger.debug(f"Parsed secret finding: {finding.id}")
        except Exception as e:
            logger.error(f"Error parsing secret findings: {e}")

    def _deduplicate_findings(self) -> None:
        """Remove duplicate findings across tools"""
        logger.info("Deduplicating findings...")
        seen = {}
        unique_findings = []
        duplicates = 0

        for finding in self.findings:
            # Create dedup key based on file, line, and description hash
            dedup_key = (finding.file, finding.line, hash(finding.description))
            
            if dedup_key not in seen:
                seen[dedup_key] = finding
                unique_findings.append(finding)
            else:
                duplicates += 1
                logger.debug(f"Duplicate found: {finding.id} (matches {seen[dedup_key].id})")

        self.findings = unique_findings
        logger.info(f"Deduplicated: removed {duplicates} duplicates, {len(self.findings)} unique findings remain")

    def _normalize_severity(self) -> None:
        """Ensure all severity levels are in standard format"""
        for finding in self.findings:
            finding.severity = self.severity_map.get(finding.severity.lower(), "LOW")

    def _assign_agents(self) -> None:
        """Assign agent responsibilities based on finding type"""
        for finding in self.findings:
            if finding.tool == "codeql":
                finding.agent_assignee = "codeql-alert-resolution-agent"
            elif finding.tool == "semgrep":
                finding.agent_assignee = "unified-security-scanner"
            elif finding.tool == "pip-audit" or finding.tool == "safety":
                finding.agent_assignee = "dependency-security-review-agent"
            elif finding.tool == "detect-secrets":
                finding.agent_assignee = "secret-detection-agent"

    def _build_report(self) -> Dict[str, Any]:
        """Build comprehensive findings report"""
        logger.info("Building comprehensive findings report...")

        # Group findings by severity
        findings_by_severity = defaultdict(list)
        for finding in self.findings:
            findings_by_severity[finding.severity].append(finding)

        # Group findings by tool
        findings_by_tool = defaultdict(list)
        for finding in self.findings:
            findings_by_tool[finding.tool].append(finding)

        # Count by severity
        severity_counts = {
            "CRITICAL": len(findings_by_severity.get("CRITICAL", [])),
            "HIGH": len(findings_by_severity.get("HIGH", [])),
            "MEDIUM": len(findings_by_severity.get("MEDIUM", [])),
            "LOW": len(findings_by_severity.get("LOW", [])),
            "INFO": len(findings_by_severity.get("INFO", [])),
        }

        # Agent assignment recommendations
        agent_assignments = defaultdict(int)
        for finding in self.findings:
            if finding.agent_assignee:
                agent_assignments[finding.agent_assignee] += 1

        failure_classification = (
            "blocked_by_critical_or_high_vulnerabilities"
            if severity_counts["CRITICAL"] > 0 or severity_counts["HIGH"] > 0
            else "warning_only"
            if severity_counts["MEDIUM"] > 0 or severity_counts["LOW"] > 0
            else "clean"
        )
        raw_evidence_artifacts = sorted(
            str(path)
            for path in self.artifacts_dir.rglob("*")
            if path.is_file()
        )

        # Build report structure
        report = {
            "scan_metadata": {
                "repository": self.repository,
                "commit": self.commit_sha,
                "run_id": self.run_id,
                "run_url": f"{self.repo_url}/actions/runs/{self.run_id}",
                "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "security_tab_url": f"{self.repo_url}/security/code-scanning",
            },
            "findings_by_severity": {
                severity: [f.to_dict() for f in findings_by_severity.get(severity, [])]
                for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
            },
            "findings_by_tool": {
                tool: [f.to_dict() for f in findings_by_tool.get(tool, [])]
                for tool in sorted(findings_by_tool.keys())
            },
            "finding_index": [f.to_dict() for f in self.findings],
            "severity_summary": severity_counts,
            "failure_classification": failure_classification,
            "raw_evidence_artifacts": raw_evidence_artifacts,
            "summary": {
                "total_findings": len(self.findings),
                "critical_count": severity_counts["CRITICAL"],
                "high_count": severity_counts["HIGH"],
                "medium_count": severity_counts["MEDIUM"],
                "low_count": severity_counts["LOW"],
                "info_count": severity_counts["INFO"],
                "remediable_findings": len([f for f in self.findings if f.status == "open"]),
                "auto_fixable_findings": len([f for f in self.findings if f.agent_assignee]),
                "requires_manual_review": len([f for f in self.findings if not f.agent_assignee]),
                "recommended_agent_handoffs": [
                    {"agent": agent, "findings_count": count}
                    for agent, count in sorted(agent_assignments.items(), key=lambda x: x[1], reverse=True)
                ],
                "severity_summary": severity_counts,
                "failure_classification": failure_classification,
                "raw_evidence_artifacts": raw_evidence_artifacts,
            },
        }

        return report

    def save_json(self, output_path: str) -> None:
        """Save report as JSON"""
        report = self.run()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"JSON report saved to {output_file}")

    def save_markdown(self, output_path: str) -> None:
        """Save report as Markdown"""
        report = self.run()
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        md_lines = [
            "# 🔐 Security Findings Comprehensive Report",
            "",
            f"**Repository:** `{report['scan_metadata']['repository']}`",
            f"**Commit:** `{report['scan_metadata']['commit']}`",
            f"**Run:** [{report['scan_metadata']['run_id']}]({report['scan_metadata']['run_url']})",
            f"**Generated:** {report['scan_metadata']['timestamp']}",
            "",
            "## Summary",
            "",
            f"- **Total Findings:** {report['summary']['total_findings']}",
            f"- **Critical:** {report['summary']['critical_count']}",
            f"- **High:** {report['summary']['high_count']}",
            f"- **Medium:** {report['summary']['medium_count']}",
            f"- **Low:** {report['summary']['low_count']}",
            "",
            "## Findings by Severity",
            "",
        ]

        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            findings = report["findings_by_severity"].get(severity, [])
            if findings:
                md_lines.append(f"### {severity} ({len(findings)})")
                md_lines.append("")
                for finding in findings:
                    md_lines.append(f"- **{finding['title']}** ({finding['tool']})")
                    md_lines.append(f"  - File: `{finding.get('file', 'N/A')}`")
                    md_lines.append(f"  - Description: {finding.get('description', 'N/A')}")
                    if finding.get('agent_assignee'):
                        md_lines.append(f"  - Assigned to: `{finding['agent_assignee']}`")
                md_lines.append("")

        md_lines.extend([
            "## Recommended Agent Handoffs",
            "",
        ])

        for handoff in report["summary"]["recommended_agent_handoffs"]:
            md_lines.append(f"- `{handoff['agent']}`: {handoff['findings_count']} findings")

        md_lines.append("")
        md_lines.append("[View full security report](reports/security-findings-comprehensive.json)")

        with open(output_file, "w") as f:
            f.write("\n".join(md_lines))

        logger.info(f"Markdown report saved to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate security findings from all scanning tools"
    )
    parser.add_argument(
        "--artifacts-dir",
        default="security-suite-artifacts",
        help="Directory containing security-suite-* artifacts",
    )
    parser.add_argument(
        "--output-json",
        default=".codex/security-findings-comprehensive.json",
        help="Output JSON file path",
    )
    parser.add_argument(
        "--output-md",
        default="security-findings-comprehensive.md",
        help="Output Markdown file path",
    )
    parser.add_argument(
        "--repo-url",
        default=os.getenv("GITHUB_SERVER_URL", "https://github.com") + "/" + os.getenv("GITHUB_REPOSITORY", "unknown/repo"),
        help="Repository URL",
    )
    parser.add_argument(
        "--run-id",
        default=os.getenv("GITHUB_RUN_ID", "unknown"),
        help="GitHub Actions run ID",
    )
    parser.add_argument(
        "--commit-sha",
        default=os.getenv("GITHUB_SHA", "unknown"),
        help="Commit SHA",
    )
    parser.add_argument(
        "--repository",
        default=os.getenv("GITHUB_REPOSITORY", "unknown/repo"),
        help="Repository name (owner/repo)",
    )

    args = parser.parse_args()

    # Create aggregator and generate reports
    aggregator = FindingsAggregator(
        artifacts_dir=args.artifacts_dir,
        repo_url=args.repo_url,
        run_id=args.run_id,
        commit_sha=args.commit_sha,
        repository=args.repository,
    )

    try:
        aggregator.save_json(args.output_json)
        aggregator.save_markdown(args.output_md)
        logger.info("✅ Aggregation complete")
        return 0
    except Exception as e:
        logger.error(f"❌ Aggregation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
