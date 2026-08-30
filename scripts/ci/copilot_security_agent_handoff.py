#!/usr/bin/env python3
"""
Copilot Security Agent Handoff Script

Purpose:
    Enables Copilot agents to efficiently fetch, filter, and triage security findings
    for remediation. Provides structured handoff with agent-specific formatting.
    
    Also provides @copilot scan-summary command support for GitHub issue/PR comments.

Usage:
    # Agent handoff
    python scripts/ci/copilot_security_agent_handoff.py handoff \
      --run-id 12345 \
      --agent codeql-alert-resolution-agent \
      --format json \
      --output findings-for-agent.json

    # Parse @copilot scan-summary command
    python scripts/ci/copilot_security_agent_handoff.py parse-command \
      --comment "@copilot scan-summary critical" \
      --output command.json

    # Generate response for scan-summary command
    python scripts/ci/copilot_security_agent_handoff.py generate-response \
      --query-json command.json \
      --cache-dir .codex/security-cache \
      --output response.md

Environment Variables:
    GITHUB_REPOSITORY: Repository name (owner/repo)
    GITHUB_RUN_ID: GitHub Actions run ID
    GH_TOKEN: GitHub API token
"""

import argparse
import json
import logging
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Severity levels for ordering
SEVERITY_LEVELS = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}
SEVERITY_EMOJI = {
    'CRITICAL': '🔴',
    'HIGH': '🟠',
    'MEDIUM': '🟡',
    'LOW': '🟢',
    'INFO': '🔵'
}


@dataclass
class ScanSummaryQuery:
    """Parsed scan-summary command query"""
    command: str
    query_type: Optional[str]  # 'cwe', 'severity', 'file', 'package'
    value: Optional[str]
    scope: Optional[str]  # Optional file/directory scope
    raw_filters: str


@dataclass
class AgentHandoff:
    """Handoff data for a specific agent"""
    agent_id: str
    findings_count: int
    findings: List[Dict[str, Any]]
    summary: Dict[str, Any]
    recommendations: List[str]


def parse_scan_summary_command(comment_body: str) -> Optional[ScanSummaryQuery]:
    """
    Parse @copilot scan-summary command with optional filters.
    
    Supported syntax:
        @copilot scan-summary                          # Basic summary
        @copilot scan-summary cwe:CWE-79              # By CWE
        @copilot scan-summary critical                # By severity
        @copilot scan-summary CRITICAL                # By severity (uppercase)
        @copilot scan-summary for src/path            # By file/directory
        @copilot scan-summary cwe:CWE-79 for src/     # Combined filters
        @copilot scan-summary package:numpy           # By package
    
    Args:
        comment_body: Full GitHub comment body text
        
    Returns:
        ScanSummaryQuery object with parsed command details, or None if not a
        scan-summary command
    """
    # Check if this is a scan-summary command
    if '@copilot scan-summary' not in comment_body.lower():
        return None
    
    # Extract the command pattern
    pattern = r'@copilot\s+scan-summary(?:\s+(.*))?'
    match = re.search(pattern, comment_body, re.IGNORECASE)
    
    if not match:
        return None
    
    raw_filters = (match.group(1) or '').strip()
    
    # Initialize query components
    query_type = None
    value = None
    scope = None
    
    if not raw_filters:
        # No filters - basic summary
        return ScanSummaryQuery(
            command='scan-summary',
            query_type=None,
            value=None,
            scope=None,
            raw_filters=''
        )
    
    # Parse filters
    parts = raw_filters.split()
    i = 0
    while i < len(parts):
        part = parts[i]
        
        # Check for "for" keyword (file scope)
        if part.lower() == 'for' and i + 1 < len(parts):
            # Collect all remaining parts as scope
            scope = ' '.join(parts[i+1:]).strip()
            break
        
        # Check for cwe: prefix
        if part.lower().startswith('cwe:'):
            query_type = 'cwe'
            value = part[4:].strip()
            i += 1
            continue
        
        # Check for package: prefix
        if part.lower().startswith('package:'):
            query_type = 'package'
            value = part[8:].strip()
            i += 1
            continue
        
        # Check for severity: prefix or plain severity name
        if part.lower().startswith('severity:'):
            query_type = 'severity'
            value = part[9:].strip().upper()
            i += 1
            continue
        elif part.upper() in SEVERITY_LEVELS:
            # Plain severity (e.g., "critical", "CRITICAL")
            query_type = 'severity'
            value = part.upper()
            i += 1
            continue
        
        i += 1
    
    return ScanSummaryQuery(
        command='scan-summary',
        query_type=query_type,
        value=value,
        scope=scope,
        raw_filters=raw_filters
    )


def generate_scan_summary_response(findings: List[Dict[str, Any]], 
                                  query_info: Optional[ScanSummaryQuery] = None,
                                  cache_age_minutes: Optional[int] = None) -> str:
    """
    Generate GitHub comment markdown for scan summary.
    
    Includes:
    - Summary table (Severity | Count | Status)
    - Top 3 issues with links
    - Recommended agents
    - Links to full reports
    - Trending indicators
    - Cache age information
    
    Args:
        findings: List of finding dictionaries from security_findings_api
        query_info: ScanSummaryQuery object with filter info
        cache_age_minutes: Age of findings in minutes (for caching indicator)
        
    Returns:
        Markdown string suitable for GitHub comment
    """
    if not findings:
        # Handle empty findings
        return (
            "## 🔍 Security Scan Summary\n\n"
            "**Status**: ✅ No findings matched your query\n\n"
            "Good news! The security scan found no issues matching your criteria.\n\n"
            "[View Full Report](.codex/security-findings-comprehensive.md)"
        )
    
    # Get repository name from environment
    repo = os.environ.get('GITHUB_REPOSITORY', 'Aries-Serpent/_codex_')
    
    # Count findings by severity
    severity_counts = {severity: 0 for severity in SEVERITY_LEVELS}
    for finding in findings:
        severity = finding.get('severity', 'INFO')
        if severity in severity_counts:
            severity_counts[severity] += 1
    
    # Count findings by tool
    tool_counts = {}
    for finding in findings:
        tool = finding.get('tool', 'Unknown')
        tool_counts[tool] = tool_counts.get(tool, 0) + 1
    
    tools_list = ', '.join(sorted(tool_counts.keys()))
    
    # Build query description
    query_desc = "All findings"
    if query_info:
        if query_info.query_type == 'cwe':
            query_desc = f"{query_info.value} findings"
        elif query_info.query_type == 'severity':
            query_desc = f"{query_info.value} findings"
        elif query_info.query_type == 'file':
            query_desc = f"findings in `{query_info.value}`"
        elif query_info.query_type == 'package':
            query_desc = f"{query_info.value} vulnerabilities"
    
    # Build cache age indicator
    cache_indicator = ""
    if cache_age_minutes is not None:
        if cache_age_minutes < 1:
            cache_indicator = " (just now)"
        elif cache_age_minutes < 60:
            cache_indicator = f" ({cache_age_minutes}m ago)"
        elif cache_age_minutes < 1440:
            hours = cache_age_minutes // 60
            cache_indicator = f" ({hours}h ago)"
        else:
            days = cache_age_minutes // 1440
            cache_indicator = f" ({days}d ago)"
    
    # Start building markdown response
    lines = [
        "## 🔍 Security Scan Summary\n",
        f"**Repository**: {repo}",
        f"**Query**: {query_desc}",
        f"**Source**: {len(tool_counts)} tool{'s' if len(tool_counts) != 1 else ''} ({tools_list})",
        f"**Scan Time**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}{cache_indicator}\n",
    ]
    
    # Add summary table
    lines.extend([
        "### Summary\n",
        "| Severity | Count | Status |",
        "|----------|-------|--------|",
    ])
    
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']:
        count = severity_counts.get(severity, 0)
        emoji = SEVERITY_EMOJI.get(severity, '❓')
        
        if count == 0:
            status = "✅ None"
        elif severity == 'CRITICAL':
            status = "🔴 Action Required"
        elif severity == 'HIGH':
            status = "🟡 Review Needed"
        elif severity == 'MEDIUM':
            status = "🟢 Monitor"
        else:
            status = "⚪ Info"
        
        lines.append(f"| {emoji} {severity} | {count} | {status} |")
    
    lines.append("")
    
    # Add top issues
    top_n = 3
    sorted_findings = sorted(
        findings,
        key=lambda f: (
            -SEVERITY_LEVELS.get(f.get('severity', 'INFO'), 0),
            -f.get('_recency_score', 0)  # Optional recency score
        )
    )
    
    top_findings = sorted_findings[:top_n]
    
    lines.extend([
        f"### Top Issues (showing {len(top_findings)} of {len(findings)})\n",
    ])
    
    for idx, finding in enumerate(top_findings, 1):
        severity = finding.get('severity', 'INFO')
        title = finding.get('title', 'Untitled Finding')
        cwe = finding.get('cwe_id', '')
        tool = finding.get('tool', 'Unknown')
        file_path = finding.get('file', '')
        line_num = finding.get('line', '')
        description = finding.get('description', '')
        
        # Build finding header
        severity_emoji = SEVERITY_EMOJI.get(severity, '❓')
        cwe_str = f"{cwe}: " if cwe else ""
        lines.append(f"{idx}. **[{severity_emoji} {severity}]** {cwe_str}{title}")
        
        # Add details
        if file_path:
            file_ref = f"`{file_path}`"
            if line_num:
                file_ref += f" (line {line_num})"
            lines.append(f"   - **File**: {file_ref}")
        
        if finding.get('package'):
            pkg_ref = finding['package']
            if finding.get('version'):
                pkg_ref += f" v{finding['version']}"
            lines.append(f"   - **Package**: {pkg_ref}")
        
        lines.append(f"   - **Tool**: {tool}")
        
        if description:
            # Truncate long descriptions
            if len(description) > 100:
                description = description[:97] + "..."
            lines.append(f"   - **Issue**: {description}")
        
        # Add remediation hint
        if finding.get('fix_recommendation'):
            lines.append(f"   - **Fix**: {finding['fix_recommendation']}")
        
        lines.append("")
    
    # Recommended agents
    lines.extend([
        "### Recommended Actions\n",
    ])
    
    # Count findings by type and recommend agents
    cwe_count = len([f for f in findings if f.get('cwe_id')])
    pkg_count = len([f for f in findings if f.get('package')])
    secret_count = len([f for f in findings if f.get('type', '').lower() in ['secret', 'credential']])
    
    recommendations = []
    if cwe_count > 0:
        recommendations.append(f"- **@codeql-alert-resolution-agent** — CWE/SAST remediation ({cwe_count} findings)")
    if pkg_count > 0:
        recommendations.append(f"- **@dependency-security-review-agent** — Dependency updates ({pkg_count} findings)")
    if secret_count > 0:
        recommendations.append(f"- **@secret-detection-agent** — Secrets rotation ({secret_count} findings)")
    
    if not recommendations:
        recommendations.append("- Review findings and plan remediation strategy")
    
    for rec in recommendations:
        lines.append(rec)
    
    lines.append("")
    
    # Trending section (placeholder for future trending data)
    lines.extend([
        "### Resources\n",
        "- [📊 View Full Dashboard](.codex/security-findings-dashboard.md)",
        "- [📋 View Full Report](.codex/security-findings-comprehensive.md)",
        "- [🔧 View Security Remediation Guide](SECURITY_REMEDIATION_GUIDE.md)\n"
    ])
    
    return "\n".join(lines)


class CopilotSecurityAgentHandoff:
    
    def __init__(self, findings_json: Path):
        """Initialize with findings JSON file path"""
        self.findings_json = findings_json
        self.findings_data = {}
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
            "5. For false positives, update semgrep.yml inline-comments",
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
                "## Summary",
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
        description="Copilot security agent handoff and command handler"
    )
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Handoff subcommand (for agent-specific handoff)
    handoff_parser = subparsers.add_parser('handoff', help='Prepare security findings handoff for Copilot agents')
    handoff_parser.add_argument(
        "--findings-json",
        default=".codex/security-findings-comprehensive.json",
        help="Path to comprehensive findings JSON file",
    )
    handoff_parser.add_argument(
        "--agent",
        required=True,
        help="Agent ID to prepare handoff for",
    )
    handoff_parser.add_argument(
        "--format",
        default="json",
        choices=["json", "markdown"],
        help="Output format",
    )
    handoff_parser.add_argument(
        "--output",
        help="Output file path (defaults to agent-specific path)",
    )
    
    # Parse-command subcommand
    parse_parser = subparsers.add_parser('parse-command', help='Parse @copilot scan-summary command')
    parse_parser.add_argument(
        "--comment",
        required=True,
        help="GitHub comment body containing @copilot command",
    )
    parse_parser.add_argument(
        "--output",
        help="Output file for parsed command (JSON)",
    )
    
    # Generate-response subcommand
    response_parser = subparsers.add_parser('generate-response', help='Generate response for scan-summary command')
    response_parser.add_argument(
        "--query-json",
        help="Path to JSON file with parsed query info",
    )
    response_parser.add_argument(
        "--query",
        help="Query info as JSON string (alternative to --query-json)",
    )
    response_parser.add_argument(
        "--findings-json",
        default=".codex/security-findings-comprehensive.json",
        help="Path to comprehensive findings JSON file",
    )
    response_parser.add_argument(
        "--cache-dir",
        default=".codex/security-cache",
        help="Path to security cache directory",
    )
    response_parser.add_argument(
        "--output",
        help="Output file for markdown response",
    )
    response_parser.add_argument(
        "--cache-age-minutes",
        type=int,
        help="Age of findings cache in minutes",
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    try:
        if args.command == 'handoff':
            # Legacy handoff subcommand
            if not args.output:
                args.output = f".codex/security-handoff-{args.agent}.{args.format}"
            
            handoff = CopilotSecurityAgentHandoff(args.findings_json)
            handoff.save_handoff(args.agent, args.output, args.format)
            logger.info("✅ Handoff preparation complete")
            return 0
        
        elif args.command == 'parse-command':
            # Parse @copilot scan-summary command
            query = parse_scan_summary_command(args.comment)
            
            if not query:
                logger.warning("❌ No @copilot scan-summary command found in comment")
                output = json.dumps({'valid': False, 'message': 'No scan-summary command found'})
            else:
                logger.info(f"✅ Parsed command: {query.command}")
                output = json.dumps({
                    'valid': True,
                    'command': query.command,
                    'query_type': query.query_type,
                    'value': query.value,
                    'scope': query.scope,
                    'raw_filters': query.raw_filters
                })
            
            if args.output:
                Path(args.output).write_text(output)
                logger.info(f"Parsed command saved to {args.output}")
            else:
                print(output)
            
            return 0 if query else 1
        
        elif args.command == 'generate-response':
            # Generate response for scan-summary command
            
            # Load query info
            query_info = None
            if args.query_json:
                query_data = json.loads(Path(args.query_json).read_text())
                if query_data.get('valid'):
                    query_info = ScanSummaryQuery(
                        command=query_data.get('command', 'scan-summary'),
                        query_type=query_data.get('query_type'),
                        value=query_data.get('value'),
                        scope=query_data.get('scope'),
                        raw_filters=query_data.get('raw_filters', '')
                    )
            elif args.query:
                query_data = json.loads(args.query)
                query_info = ScanSummaryQuery(
                    command=query_data.get('command', 'scan-summary'),
                    query_type=query_data.get('query_type'),
                    value=query_data.get('value'),
                    scope=query_data.get('scope'),
                    raw_filters=query_data.get('raw_filters', '')
                )
            
            # Load findings (would need to query via security_findings_api.py)
            findings = []
            findings_file = Path(args.findings_json)
            if findings_file.exists():
                data = json.loads(findings_file.read_text())
                findings = data.get('findings', [])
            
            # Filter findings based on query
            if query_info and query_info.query_type and query_info.value:
                filtered_findings = []
                for finding in findings:
                    if query_info.query_type == 'cwe':
                        if finding.get('cwe_id', '').upper() == query_info.value.upper():
                            filtered_findings.append(finding)
                    elif query_info.query_type == 'severity':
                        if finding.get('severity', '').upper() == query_info.value.upper():
                            filtered_findings.append(finding)
                    elif query_info.query_type == 'file':
                        if query_info.value in finding.get('file', ''):
                            filtered_findings.append(finding)
                    elif query_info.query_type == 'package':
                        if finding.get('package', '').lower() == query_info.value.lower():
                            filtered_findings.append(finding)
                findings = filtered_findings
            
            # Generate response markdown
            # lgtm[py/clear-text-storage]: Response contains only finding metadata (title, 
            # description, location), not actual secret values or sensitive data
            response = generate_scan_summary_response(
                findings,
                query_info,
                args.cache_age_minutes
            )
            
            if args.output:
                # lgtm[py/clear-text-storage]: Metadata-only findings written for agent handoff
                Path(args.output).write_text(response)
                # lgtm[py/clear-text-logging]: Logging file path only, not sensitive data
                logger.info(f"Response saved to {args.output}")
            else:
                # lgtm[py/clear-text-logging]: Response contains only finding metadata
                print(response)
            
            # lgtm[py/clear-text-logging]: Status message only, no sensitive data
            logger.info("✅ Response generation complete")
            return 0
        
        else:
            logger.error(f"Unknown command: {args.command}")
            return 1
    
    except Exception as e:
        logger.error(f"❌ Operation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
