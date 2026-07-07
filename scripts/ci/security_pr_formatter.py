#!/usr/bin/env python3
"""
Security PR Formatter

Purpose:
    Formats security findings into PR-friendly markdown sections.
    Generates summary tables, top issues lists, and agent assignment recommendations.

Usage:
    python scripts/ci/security_pr_formatter.py generate \
      --findings .codex/security-findings-comprehensive.json \
      --output pr-findings.md \
      --limit 5

Environment Variables:
    SECURITY_FINDINGS_FILE: Override default findings file path
"""

import argparse
import json
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
DEFAULT_FINDINGS_FILE = Path(".codex/security-findings-comprehensive.json")
SEVERITY_LEVELS = {'CRITICAL': 4, 'HIGH': 3, 'MEDIUM': 2, 'LOW': 1, 'INFO': 0}
SEVERITY_EMOJIS = {
    'CRITICAL': '🔴',
    'HIGH': '🟠',
    'MEDIUM': '🟡',
    'LOW': '🟢',
    'INFO': '🔵'
}
SEVERITY_TREND = {
    'improved': '🟢 Improving',
    'stable': '🟡 Stable',
    'increased': '🔴 New!',
    'unknown': '⚫ Unknown'
}


@dataclass
class SecurityFinding:
    """Represents a security finding."""
    cwe: str
    severity: str
    description: str
    file_path: str
    line_number: int
    tool: str
    fix_recommendation: str
    confidence: float = 1.0
    timestamp: Optional[str] = None
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'SecurityFinding':
        """Create Finding from dictionary."""
        return SecurityFinding(
            cwe=data.get('cwe', 'UNKNOWN'),
            severity=data.get('severity', 'UNKNOWN').upper(),
            description=data.get('description', 'No description'),
            file_path=data.get('file_path', 'unknown'),
            line_number=data.get('line_number', 0),
            tool=data.get('tool', 'unknown'),
            fix_recommendation=data.get('fix_recommendation', 'See tool documentation'),
            confidence=float(data.get('confidence', 1.0)),
            timestamp=data.get('timestamp')
        )


def load_findings(findings_path: Path) -> List[SecurityFinding]:
    """
    Load security findings from JSON file.
    
    Args:
        findings_path: Path to security-findings-comprehensive.json
        
    Returns:
        List of SecurityFinding objects
    """
    if not findings_path.exists():
        logger.warning(f"Findings file not found: {findings_path}")
        return []
    
    try:
        with open(findings_path) as f:
            data = json.load(f)
        
        findings_data = data.get('findings', [])
        findings = [SecurityFinding.from_dict(f) for f in findings_data]
        logger.info(f"Loaded {len(findings)} findings from {findings_path}")
        return findings
    except (json.JSONDecodeError, KeyError) as e:
        logger.error(f"Error loading findings: {e}")
        return []


def format_findings_table(findings: List[SecurityFinding]) -> str:
    """
    Format findings grouped by severity into markdown table.
    
    Args:
        findings: List of SecurityFinding objects
        
    Returns:
        Markdown table string
    """
    if not findings:
        return "No findings detected."
    
    # Group by severity
    by_severity = defaultdict(lambda: defaultdict(int))
    tools_by_severity = defaultdict(set)
    
    for finding in findings:
        severity = finding.severity
        by_severity[severity]['count'] += 1
        tools_by_severity[severity].add(finding.tool)
    
    # Sort by severity level
    sorted_severities = sorted(
        by_severity.keys(),
        key=lambda x: SEVERITY_LEVELS.get(x, -1),
        reverse=True
    )
    
    # Build table
    table = "### Severity Distribution\n\n"
    table += "| Severity | Count | Tools | Trend |\n"
    table += "|----------|-------|-------|-------|\n"
    
    for severity in sorted_severities:
        if severity in by_severity:
            count = by_severity[severity]['count']
            tools = ', '.join(sorted(tools_by_severity[severity]))
            # Determine trend (this would be enhanced with historical data)
            trend = SEVERITY_TREND.get('unknown', 'Unknown')
            emoji = SEVERITY_EMOJIS.get(severity, '⚫')
            
            table += f"| {emoji} {severity} | {count} | {tools} | {trend} |\n"
    
    return table


def list_top_issues(findings: List[SecurityFinding], limit: int = 5) -> str:
    """
    List top issues sorted by severity and recency.
    
    Args:
        findings: List of SecurityFinding objects
        limit: Maximum number of issues to list
        
    Returns:
        Markdown formatted list
    """
    if not findings:
        return "No findings to display."
    
    # Sort by severity (high to low), then by confidence (high to low)
    sorted_findings = sorted(
        findings,
        key=lambda f: (
            SEVERITY_LEVELS.get(f.severity, -1),
            f.confidence
        ),
        reverse=True
    )
    
    # Take top N
    top_findings = sorted_findings[:limit]
    
    if not top_findings:
        return "No findings to display."
    
    output = "### Top Security Issues\n\n"
    
    for i, finding in enumerate(top_findings, 1):
        emoji = SEVERITY_EMOJIS.get(finding.severity, '⚫')
        output += f"{i}. **[{emoji} {finding.severity}]** {finding.cwe}: {finding.description}\n"
        output += f"   - **File**: `{finding.file_path}:{finding.line_number}`\n"
        output += f"   - **Tool**: {finding.tool}\n"
        output += f"   - **Confidence**: {finding.confidence:.0%}\n"
        output += f"   - **Fix**: {finding.fix_recommendation}\n"
        output += "\n"
    
    return output


def get_agent_assignments(findings: List[SecurityFinding]) -> str:
    """
    Determine which agents should handle the findings.
    
    Args:
        findings: List of SecurityFinding objects
        
    Returns:
        Markdown formatted agent recommendations
    """
    if not findings:
        return "No agent assignments needed."
    
    # Count findings by tool/type
    tool_counts = defaultdict(int)
    for finding in findings:
        tool_counts[finding.tool] += 1
    
    # Map tools to recommended agents
    agent_mappings = {
        'CodeQL': {
            'agent': '@codeql-alert-resolution-agent',
            'description': 'CodeQL security alerts'
        },
        'Semgrep': {
            'agent': '@code-scanning-remediation-agent',
            'description': 'Semgrep policy violations'
        },
        'pip-audit': {
            'agent': '@dependency-security-review-agent',
            'description': 'Dependency vulnerabilities'
        },
        'Safety': {
            'agent': '@dependency-security-review-agent',
            'description': 'Dependency vulnerabilities'
        },
        'detect-secrets': {
            'agent': '@secret-detection-agent',
            'description': 'Leaked secrets/credentials'
        },
        'Bandit': {
            'agent': '@code-scanning-remediation-agent',
            'description': 'Python security issues'
        }
    }
    
    # Find relevant agents
    assigned_agents = {}
    for tool, count in tool_counts.items():
        if tool in agent_mappings:
            mapping = agent_mappings[tool]
            agent_name = mapping['agent']
            if agent_name not in assigned_agents:
                assigned_agents[agent_name] = {
                    'count': 0,
                    'description': mapping['description']
                }
            assigned_agents[agent_name]['count'] += count
    
    if not assigned_agents:
        return "No specific agents needed for remediation."
    
    output = "### Recommended Security Agents\n\n"
    for agent, info in sorted(assigned_agents.items(), key=lambda x: x[1]['count'], reverse=True):
        output += f"- **{agent}** ({info['count']} findings)\n"
        output += f"  - Task: {info['description']}\n"
    
    return output


def generate_pr_summary(findings: List[SecurityFinding]) -> str:
    """
    Generate one-line summary with counts and timestamp.
    
    Args:
        findings: List of SecurityFinding objects
        
    Returns:
        Markdown formatted summary
    """
    if not findings:
        return "✅ No security findings detected."
    
    # Count by severity
    severity_counts = defaultdict(int)
    for finding in findings:
        severity_counts[finding.severity] += 1
    
    # Build summary line
    summary_parts = []
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        if severity in severity_counts:
            count = severity_counts[severity]
            emoji = SEVERITY_EMOJIS.get(severity, '⚫')
            summary_parts.append(f"{count} {emoji} {severity}")
    
    summary = ", ".join(summary_parts)
    timestamp = datetime.now(timezone.utc).isoformat(timespec='minutes')
    
    return f"**Summary**: {summary}\n\n_Last scan: {timestamp}_"


def generate_findings_section(findings_path: Path, limit: int = 5) -> str:
    """
    Generate complete findings section for PR.
    
    Args:
        findings_path: Path to security-findings-comprehensive.json
        limit: Maximum number of top issues to show
        
    Returns:
        Complete markdown section
    """
    findings = load_findings(findings_path)
    
    # Generate sections
    output = ""
    
    # Summary
    output += generate_pr_summary(findings) + "\n\n"
    
    if findings:
        # Severity distribution
        output += format_findings_table(findings) + "\n\n"
        
        # Top issues
        output += list_top_issues(findings, limit) + "\n"
        
        # Agent recommendations
        agents_section = get_agent_assignments(findings)
        if agents_section != "No agent assignments needed.":
            output += agents_section + "\n"
        
        # Link to full report
        output += "---\n\n"
        output += "_For detailed analysis, see [Security Findings Report](.codex/security-findings-comprehensive.md) (if available)_\n"
    
    return output


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Format security findings for PR enhancement'
    )
    parser.add_argument(
        'command',
        choices=['generate', 'summary', 'validate'],
        help='Command to execute'
    )
    parser.add_argument(
        '--findings',
        type=Path,
        default=DEFAULT_FINDINGS_FILE,
        help='Path to security-findings-comprehensive.json'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file for markdown (default: stdout)'
    )
    parser.add_argument(
        '--limit',
        type=int,
        default=5,
        help='Number of top issues to display'
    )
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        findings_section = generate_findings_section(args.findings, args.limit)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(findings_section)
            logger.info(f"Generated findings section to {args.output}")
        else:
            print(findings_section)
            
    elif args.command == 'summary':
        findings = load_findings(args.findings)
        summary = generate_pr_summary(findings)
        print(summary)
        
    elif args.command == 'validate':
        findings = load_findings(args.findings)
        print(f"Loaded {len(findings)} findings")
        print(f"Valid format: {len(findings) >= 0}")
        return 0 if findings else 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
