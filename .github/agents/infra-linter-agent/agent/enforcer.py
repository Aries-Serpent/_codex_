"""
Infrastructure Linter Agent - ACT Phase (enforcer.py)

Purpose: Generate reports, block CI if needed, and suggest fixes for IaC issues.

This module takes validation results from validator.py and:
1. Generates human-readable reports (Markdown, JSON, HTML)
2. Creates GitHub PR annotations for code review
3. Suggests automated fixes for common issues
4. Determines CI blocking behavior

Part of the Cognitive Brain Phase 6 agent ecosystem.
"""

import json
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

# #AFTERMATH_PATTERN_IDENTIFIED: iac_enforcement_actions
# #AFTERMATH_METRIC: reports_generated

logger = logging.getLogger(__name__)


@dataclass
class EnforcementResult:
    """Result of IaC enforcement actions"""
    report_generated: bool
    report_path: str
    ci_blocked: bool
    exit_code: int
    github_annotations: List[Dict[str, Any]]
    suggested_fixes: List[Dict[str, Any]]


class IaCEnforcer:
    """
    ACT phase: Generate reports and enforce IaC policies.
    
    Responsibilities:
    - Create reports in multiple formats
    - Generate GitHub PR annotations
    - Suggest automated fixes
    - Determine CI blocking behavior
    """
    
    def __init__(self):
        """Initialize IaC enforcer"""
        logger.info("IaCEnforcer initialized")
    
    def enforce(
        self,
        validation_results: Dict[str, Any],
        scan_results: Dict[str, Any],
        config: Optional[Dict[str, Any]] = None
    ) -> EnforcementResult:
        """
        Generate reports and enforce policies based on validation results.
        
        Args:
            validation_results: Output from validator.py
            scan_results: Original scan data from scanner.py
            config: Configuration (output_format, report_path, etc.)
        
        Returns:
            EnforcementResult with report paths, annotations, and exit code
        """
        if config is None:
            config = {}
        
        output_format = config.get("output_format", "markdown")
        report_dir = config.get("report_dir", "/tmp")
        
        # Generate report in requested format
        report_path = self._generate_report(
            validation_results,
            scan_results,
            output_format,
            report_dir
        )
        
        # Create GitHub annotations for PR review
        annotations = self._create_github_annotations(validation_results)
        
        # Generate suggested fixes
        fixes = self._suggest_fixes(scan_results)
        
        # Determine if CI should be blocked
        should_block = validation_results.get("recommendation") == "BLOCK"
        exit_code = 1 if should_block else 0
        
        result = EnforcementResult(
            report_generated=True,
            report_path=report_path,
            ci_blocked=should_block,
            exit_code=exit_code,
            github_annotations=annotations,
            suggested_fixes=fixes
        )
        
        logger.info(f"Enforcement complete: {'BLOCKED' if should_block else 'PASSED'} (report={report_path})")
        return result
    
    def _generate_report(
        self,
        validation: Dict[str, Any],
        scan: Dict[str, Any],
        format: str,
        output_dir: str
    ) -> str:
        """
        Generate report in specified format.
        
        Args:
            validation: Validation results
            scan: Scan results
            format: Output format (markdown/json/html)
            output_dir: Directory to write report
        
        Returns:
            Path to generated report file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format == "markdown":
            filename = f"iac-lint-report-{timestamp}.md"
            content = self._generate_markdown_report(validation, scan)
        elif format == "json":
            filename = f"iac-lint-report-{timestamp}.json"
            content = self._generate_json_report(validation, scan)
        elif format == "html":
            filename = f"iac-lint-report-{timestamp}.html"
            content = self._generate_html_report(validation, scan)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Write report to disk
        report_path = Path(output_dir) / filename
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(content)
        
        logger.info(f"Report generated: {report_path}")
        return str(report_path)
    
    def _generate_markdown_report(
        self,
        validation: Dict[str, Any],
        scan: Dict[str, Any]
    ) -> str:
        """Generate Markdown report (human-readable, PR-friendly)"""
        lines = [
            "# Infrastructure as Code Linting Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Summary",
            "",
            f"- **Recommendation:** {validation.get('recommendation', 'UNKNOWN')}",
            f"- **Risk Level:** {validation.get('risk_level', 'unknown').upper()}",
            f"- **Security Score:** {validation.get('security_score', 0)}/100",
            f"- **Confidence:** {validation.get('confidence', 0.0):.0%}",
            "",
            "## Issue Breakdown",
            "",
            f"- 🔴 Critical: {validation.get('critical_issues', 0)}",
            f"- 🟠 High: {validation.get('high_issues', 0)}",
            f"- 🟡 Medium: {validation.get('medium_issues', 0)}",
            f"- 🟢 Low: {validation.get('low_issues', 0)}",
            "",
        ]
        
        # Blockers section
        blockers = validation.get("blockers", [])
        if blockers:
            lines.extend([
                "## 🚫 Blockers (Must Fix)",
                "",
            ])
            for blocker in blockers:
                lines.extend([
                    f"### {blocker.get('rule', 'Unknown Rule')}",
                    "",
                    f"- **File:** `{blocker.get('file', 'unknown')}`",
                    f"- **Line:** {blocker.get('line', 0)}",
                    f"- **Severity:** {blocker.get('severity', 'UNKNOWN')}",
                    f"- **Message:** {blocker.get('message', '')}",
                    f"- **Reason:** {blocker.get('reason', '')}",
                    "",
                ])
        
        # Warnings section
        warnings = validation.get("warnings", [])
        if warnings:
            lines.extend([
                "## ⚠️ Warnings (Recommended Fixes)",
                "",
            ])
            for warning in warnings:
                lines.extend([
                    f"### {warning.get('rule', 'Unknown Rule')}",
                    "",
                    f"- **File:** `{warning.get('file', 'unknown')}`",
                    f"- **Line:** {warning.get('line', 0)}",
                    f"- **Severity:** {warning.get('severity', 'UNKNOWN')}",
                    f"- **Message:** {warning.get('message', '')}",
                    "",
                    f"**Suggested Fix:** {warning.get('suggested_fix', 'No fix available')}",
                    "",
                ])
        
        # Scan details
        lines.extend([
            "## Scan Details",
            "",
            f"- **Files Scanned:** {scan.get('files_scanned', 0)}",
            f"- **Tools Detected:** {', '.join(scan.get('tools_detected', []))}",
            f"- **Scan Duration:** {scan.get('duration_seconds', 0):.2f}s",
            "",
        ])
        
        # Reasoning
        lines.extend([
            "## Decision Reasoning",
            "",
            validation.get("reasoning", "No reasoning provided"),
            "",
        ])
        
        return "\n".join(lines)
    
    def _generate_json_report(
        self,
        validation: Dict[str, Any],
        scan: Dict[str, Any]
    ) -> str:
        """Generate JSON report (machine-readable, CI integration)"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "recommendation": validation.get("recommendation", "UNKNOWN"),
                "risk_level": validation.get("risk_level", "unknown"),
                "security_score": validation.get("security_score", 0),
                "confidence": validation.get("confidence", 0.0),
            },
            "issue_counts": {
                "critical": validation.get("critical_issues", 0),
                "high": validation.get("high_issues", 0),
                "medium": validation.get("medium_issues", 0),
                "low": validation.get("low_issues", 0),
            },
            "blockers": validation.get("blockers", []),
            "warnings": validation.get("warnings", []),
            "scan_details": {
                "files_scanned": scan.get("files_scanned", 0),
                "tools_detected": scan.get("tools_detected", []),
                "duration_seconds": scan.get("duration_seconds", 0),
            },
            "reasoning": validation.get("reasoning", ""),
        }
        
        return json.dumps(report, indent=2)
    
    def _generate_html_report(
        self,
        validation: Dict[str, Any],
        scan: Dict[str, Any]
    ) -> str:
        """Generate HTML report (dashboard-ready)"""
        recommendation = validation.get("recommendation", "UNKNOWN")
        risk = validation.get("risk_level", "unknown")
        score = validation.get("security_score", 0)
        
        # Color coding
        if recommendation == "BLOCK":
            status_color = "#dc3545"  # Red
        elif recommendation == "WARN":
            status_color = "#ffc107"  # Yellow
        else:
            status_color = "#28a745"  # Green
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>IaC Linting Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: {status_color}; color: white; padding: 20px; border-radius: 5px; }}
        .metric {{ display: inline-block; margin-right: 20px; }}
        .blocker {{ background: #f8d7da; border-left: 4px solid #dc3545; padding: 10px; margin: 10px 0; }}
        .warning {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px; margin: 10px 0; }}
        h1, h2 {{ color: #333; }}
    </style>
</head>
<body>
    <h1>Infrastructure as Code Linting Report</h1>
    <div class="summary">
        <h2>{recommendation}</h2>
        <div class="metric"><strong>Risk:</strong> {risk.upper()}</div>
        <div class="metric"><strong>Score:</strong> {score}/100</div>
        <div class="metric"><strong>Confidence:</strong> {validation.get('confidence', 0.0):.0%}</div>
    </div>
    
    <h2>Issue Breakdown</h2>
    <ul>
        <li>Critical: {validation.get('critical_issues', 0)}</li>
        <li>High: {validation.get('high_issues', 0)}</li>
        <li>Medium: {validation.get('medium_issues', 0)}</li>
        <li>Low: {validation.get('low_issues', 0)}</li>
    </ul>
"""
        
        # Blockers
        blockers = validation.get("blockers", [])
        if blockers:
            html += "<h2>Blockers</h2>"
            for blocker in blockers:
                html += f"""
    <div class="blocker">
        <strong>{blocker.get('rule', 'Unknown')}</strong><br>
        File: {blocker.get('file', 'unknown')}, Line: {blocker.get('line', 0)}<br>
        {blocker.get('message', '')}
    </div>
"""
        
        # Warnings
        warnings = validation.get("warnings", [])
        if warnings:
            html += "<h2>Warnings</h2>"
            for warning in warnings:
                html += f"""
    <div class="warning">
        <strong>{warning.get('rule', 'Unknown')}</strong><br>
        File: {warning.get('file', 'unknown')}, Line: {warning.get('line', 0)}<br>
        {warning.get('message', '')}
    </div>
"""
        
        html += """
    <h2>Scan Details</h2>
    <ul>
        <li>Files Scanned: """ + str(scan.get('files_scanned', 0)) + """</li>
        <li>Tools: """ + ', '.join(scan.get('tools_detected', [])) + """</li>
        <li>Duration: """ + f"{scan.get('duration_seconds', 0):.2f}s" + """</li>
    </ul>
</body>
</html>
"""
        
        return html
    
    def _create_github_annotations(
        self,
        validation: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Create GitHub PR annotations for code review.
        
        GitHub Actions annotation format:
        {
            "path": "file/path.tf",
            "start_line": 15,
            "end_line": 15,
            "annotation_level": "failure|warning|notice",
            "message": "Issue description",
            "title": "Short title"
        }
        """
        annotations = []
        
        # Annotations for blockers
        for blocker in validation.get("blockers", []):
            annotations.append({
                "path": self._normalize_path(blocker.get("file", "unknown")),
                "start_line": blocker.get("line", 1),
                "end_line": blocker.get("line", 1),
                "annotation_level": "failure",
                "message": blocker.get("message", ""),
                "title": f"Security: {blocker.get('rule', 'Unknown Rule')}"
            })
        
        # Annotations for warnings
        for warning in validation.get("warnings", []):
            annotations.append({
                "path": self._normalize_path(warning.get("file", "unknown")),
                "start_line": warning.get("line", 1),
                "end_line": warning.get("line", 1),
                "annotation_level": "warning",
                "message": warning.get("message", ""),
                "title": f"Warning: {warning.get('rule', 'Unknown Rule')}"
            })
        
        logger.info(f"Generated {len(annotations)} GitHub annotations")
        return annotations
    
    def _normalize_path(self, file_path: str) -> str:
        """Normalize file path for GitHub annotations (relative to repo root)"""
        # Remove leading slashes, handle absolute paths
        if file_path.startswith("/"):
            # Try to extract relative path
            parts = file_path.split("/")
            if len(parts) > 2:
                # Assume format like /path/to/repo/file.tf -> file.tf
                return "/".join(parts[-2:]) if len(parts) >= 2 else file_path
        
        return file_path
    
    def _suggest_fixes(
        self,
        scan_results: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Generate automated fix suggestions for common issues.
        
        Returns list of suggested fixes with:
        - file: File path
        - line: Line number
        - original: Original code snippet
        - suggested: Suggested replacement
        - auto_fixable: Whether this can be auto-applied
        """
        fixes = []
        
        for scan_result in scan_results.get("scan_results", []):
            file_path = scan_result.get("file_path", "")
            
            for finding in scan_result.get("findings", []):
                rule_id = finding.get("rule_id", "")
                line = finding.get("line", 0)
                suggested_fix = finding.get("suggested_fix", "")
                
                # Check if we have a suggested fix
                if suggested_fix:
                    fixes.append({
                        "file": file_path,
                        "line": line,
                        "rule": rule_id,
                        "suggested": suggested_fix,
                        "auto_fixable": self._is_auto_fixable(rule_id)
                    })
        
        logger.info(f"Generated {len(fixes)} suggested fixes")
        return fixes
    
    def _is_auto_fixable(self, rule_id: str) -> bool:
        """
        Determine if this rule can be automatically fixed.
        
        Some common auto-fixable patterns:
        - Missing encryption blocks
        - Missing resource limits
        - Simple RBAC additions
        """
        auto_fixable_patterns = [
            "encryption",
            "resource-limit",
            "label",
            "tag",
        ]
        
        rule_lower = rule_id.lower()
        return any(pattern in rule_lower for pattern in auto_fixable_patterns)
