"""
PR annotation module for security findings.

Generates PR comments and summary reports for security scan results.

#AFTERMATH_PATTERN_IDENTIFIED - Structured PR feedback for actionable security insights
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .parser import Finding

logger = logging.getLogger(__name__)


@dataclass
class Annotation:
    """PR annotation for a finding."""
    
    file_path: str
    line: int
    level: str  # "error", "warning", "notice"
    message: str
    title: str
    annotation_text: str


class PRAnnotator:
    """
    Generate PR annotations and summary reports for security findings.
    
    Creates actionable feedback for developers in PR reviews.
    
    #AFTERMATH_LESSON_LEARNED - Clear annotations drive faster security fixes
    """
    
    def __init__(self) -> None:
        """Initialize the PR annotator."""
        logger.info("PRAnnotator initialized")
    
    def generate_annotations(
        self,
        findings: list[Finding],
        max_annotations: int = 50
    ) -> list[Annotation]:
        """
        Generate PR annotations from findings.
        
        Args:
            findings: List of security findings
            max_annotations: Maximum number of annotations (GitHub limit)
            
        Returns:
            List of annotations
            
        #AFTERMATH_QUALITY_CHECK - Respects GitHub's annotation limits
        """
        annotations = []
        
        # Sort by severity: error > warning > note
        severity_order = {"error": 0, "warning": 1, "note": 2}
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.get(f.level, 3)
        )
        
        for finding in sorted_findings[:max_annotations]:
            for location in finding.locations:
                annotation = Annotation(
                    file_path=location.file_path,
                    line=location.start_line,
                    level=self._map_level(finding.level),
                    message=finding.message,
                    title=f"[{finding.tool}] {finding.rule_id}",
                    annotation_text=self._format_annotation_text(finding, location)
                )
                annotations.append(annotation)
        
        logger.info("Generated %d annotations", len(annotations))
        return annotations
    
    def _map_level(self, sarif_level: str) -> str:
        """
        Map SARIF level to GitHub annotation level.
        
        Args:
            sarif_level: SARIF level (error, warning, note)
            
        Returns:
            GitHub annotation level (error, warning, notice)
        """
        mapping = {
            "error": "error",
            "warning": "warning",
            "note": "notice",
        }
        return mapping.get(sarif_level, "notice")
    
    def _format_annotation_text(
        self,
        finding: Finding,
        location: Any
    ) -> str:
        """
        Format annotation text with finding details.
        
        Args:
            finding: Security finding
            location: Code location
            
        Returns:
            Formatted annotation text
        """
        text = f"**Security Issue: {finding.rule_id}**\n\n"
        text += f"{finding.message}\n\n"
        
        if location.region_snippet:
            text += "```\n"
            text += location.region_snippet
            text += "\n```\n\n"
        
        text += f"**Tool:** {finding.tool}\n"
        text += f"**Severity:** {finding.level}\n"
        
        return text
    
    def generate_summary(
        self,
        all_findings: list[Finding],
        valid_findings: list[Finding],
        filtered_findings: list[Finding]
    ) -> str:
        """
        Generate summary report for PR comment.
        
        Args:
            all_findings: All findings before filtering
            valid_findings: Valid findings after filtering
            filtered_findings: Filtered out findings
            
        Returns:
            Markdown formatted summary
        """
        summary = "## 🔒 Security Scan Report\n\n"
        
        # Overview
        summary += "### Overview\n\n"
        summary += f"- **Total Findings:** {len(all_findings)}\n"
        summary += f"- **Valid Findings:** {len(valid_findings)}\n"
        summary += f"- **Filtered (False Positives):** {len(filtered_findings)}\n\n"
        
        # Breakdown by severity
        if valid_findings:
            summary += "### Findings by Severity\n\n"
            severity_counts = self._count_by_severity(valid_findings)
            for level, count in sorted(severity_counts.items()):
                emoji = self._get_emoji_for_level(level)
                summary += f"- {emoji} **{level.title()}:** {count}\n"
            summary += "\n"
        
        # Breakdown by tool
        if valid_findings:
            summary += "### Findings by Tool\n\n"
            tool_counts = self._count_by_tool(valid_findings)
            for tool, count in sorted(tool_counts.items()):
                summary += f"- **{tool}:** {count}\n"
            summary += "\n"
        
        # Top issues
        if valid_findings:
            summary += "### Top Security Issues\n\n"
            top_rules = self._get_top_rules(valid_findings, limit=5)
            for rule_id, count in top_rules:
                summary += f"- `{rule_id}`: {count} occurrence(s)\n"
            summary += "\n"
        
        # Recommendation
        if len(valid_findings) == 0:
            summary += "### ✅ Result\n\n"
            summary += "No valid security findings detected. Great job!\n"
        else:
            summary += "### ⚠️ Action Required\n\n"
            summary += f"Please review and address the {len(valid_findings)} security finding(s) above.\n"
        
        logger.info("Generated summary report")
        return summary
    
    def _count_by_severity(self, findings: list[Finding]) -> dict[str, int]:
        """Count findings by severity level."""
        counts: dict[str, int] = {}
        for finding in findings:
            level = finding.level
            counts[level] = counts.get(level, 0) + 1
        return counts
    
    def _count_by_tool(self, findings: list[Finding]) -> dict[str, int]:
        """Count findings by tool."""
        counts: dict[str, int] = {}
        for finding in findings:
            tool = finding.tool or "unknown"
            counts[tool] = counts.get(tool, 0) + 1
        return counts
    
    def _get_top_rules(
        self,
        findings: list[Finding],
        limit: int = 5
    ) -> list[tuple[str, int]]:
        """Get top N most common rule IDs."""
        counts: dict[str, int] = {}
        for finding in findings:
            rule_id = finding.rule_id
            counts[rule_id] = counts.get(rule_id, 0) + 1
        
        # Sort by count descending
        sorted_rules = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_rules[:limit]
    
    def _get_emoji_for_level(self, level: str) -> str:
        """Get emoji for severity level."""
        emojis = {
            "error": "🔴",
            "warning": "🟡",
            "note": "🔵",
        }
        return emojis.get(level, "⚪")
    
    def write_annotations_file(
        self,
        annotations: list[Annotation],
        output_path: Path
    ) -> None:
        """
        Write annotations to file for CI/CD integration.
        
        Args:
            annotations: List of annotations
            output_path: Path to write annotations
        """
        import json
        
        data = [
            {
                "file": ann.file_path,
                "line": ann.line,
                "level": ann.level,
                "message": ann.message,
                "title": ann.title,
            }
            for ann in annotations
        ]
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info("Wrote annotations to: %s", output_path)
    
    def write_summary_file(
        self,
        summary: str,
        output_path: Path
    ) -> None:
        """
        Write summary report to file.
        
        Args:
            summary: Summary text
            output_path: Path to write summary
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(summary)
        
        logger.info("Wrote summary to: %s", output_path)


# #AFTERMATH_METRIC - PR annotator with structured feedback generation
# #AFTERMATH_PATTERN_IDENTIFIED - Actionable security feedback in PR reviews
