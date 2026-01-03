"""
AST Analysis Agent - Report Generator.

Generates structured reports from code analysis findings
with support for multiple output formats.
"""
import json
import csv
import io
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ReportConfig:
    """Configuration for report generation.
    
    Attributes:
        title: Report title
        include_summary: Include summary section
        include_details: Include detailed findings
        format: Output format (json, csv, markdown, html)
        severity_filter: Only include these severities
        category_filter: Only include these categories
    """
    title: str = "AST Analysis Report"
    include_summary: bool = True
    include_details: bool = True
    format: str = "markdown"
    severity_filter: Optional[List[str]] = None
    category_filter: Optional[List[str]] = None


class ReportGenerator:
    """Generates analysis reports.
    
    Supports multiple output formats:
    - Markdown: Human-readable format
    - JSON: Machine-readable format
    - CSV: Spreadsheet-compatible format
    - HTML: Web display format
    
    Attributes:
        config: Report configuration
    """
    
    def __init__(self, config: Optional[ReportConfig] = None):
        """Initialize report generator.
        
        Args:
            config: Report configuration (uses defaults if None)
        """
        self.config = config or ReportConfig()
    
    def generate(
        self,
        findings: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate report from findings.
        
        Args:
            findings: List of finding dictionaries
            metadata: Optional report metadata
            
        Returns:
            Formatted report string
        """
        # Filter findings
        filtered = self._filter_findings(findings)
        
        # Generate based on format
        if self.config.format == "json":
            return self._generate_json(filtered, metadata)
        elif self.config.format == "csv":
            return self._generate_csv(filtered)
        elif self.config.format == "html":
            return self._generate_html(filtered, metadata)
        else:
            return self._generate_markdown(filtered, metadata)
    
    def _filter_findings(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter findings based on config."""
        filtered = findings
        
        if self.config.severity_filter:
            filtered = [
                f for f in filtered 
                if f.get('severity') in self.config.severity_filter
            ]
        
        if self.config.category_filter:
            filtered = [
                f for f in filtered 
                if f.get('category') in self.config.category_filter
            ]
        
        return filtered
    
    def _generate_summary(self, findings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics."""
        by_severity = {}
        by_category = {}
        by_file = {}
        
        for finding in findings:
            # Count by severity
            sev = finding.get('severity', 'unknown')
            by_severity[sev] = by_severity.get(sev, 0) + 1
            
            # Count by category
            cat = finding.get('category', 'unknown')
            by_category[cat] = by_category.get(cat, 0) + 1
            
            # Count by file
            file_path = finding.get('file_path', 'unknown')
            by_file[file_path] = by_file.get(file_path, 0) + 1
        
        return {
            'total_findings': len(findings),
            'by_severity': by_severity,
            'by_category': by_category,
            'files_affected': len(by_file),
            'by_file': by_file,
        }
    
    def _generate_markdown(
        self,
        findings: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> str:
        """Generate Markdown report."""
        lines = []
        
        # Header
        lines.append(f"# {self.config.title}")
        lines.append("")
        lines.append(f"**Generated:** {datetime.now().isoformat()}")
        
        if metadata:
            lines.append(f"**Files Analyzed:** {metadata.get('total_files', 'N/A')}")
        
        lines.append("")
        
        # Summary
        if self.config.include_summary:
            summary = self._generate_summary(findings)
            lines.append("## Summary")
            lines.append("")
            lines.append(f"- **Total Findings:** {summary['total_findings']}")
            lines.append(f"- **Files Affected:** {summary['files_affected']}")
            lines.append("")
            
            lines.append("### By Severity")
            lines.append("")
            for sev, count in sorted(summary['by_severity'].items()):
                lines.append(f"- {sev}: {count}")
            lines.append("")
            
            lines.append("### By Category")
            lines.append("")
            for cat, count in sorted(summary['by_category'].items()):
                lines.append(f"- {cat}: {count}")
            lines.append("")
        
        # Details
        if self.config.include_details and findings:
            lines.append("## Findings")
            lines.append("")
            
            for i, finding in enumerate(findings, 1):
                sev = finding.get('severity', 'unknown')
                icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(sev, "⚪")
                
                lines.append(f"### {i}. {icon} {finding.get('category', 'unknown')}")
                lines.append("")
                lines.append(f"**File:** `{finding.get('file_path', 'unknown')}`:{finding.get('line', 0)}")
                lines.append(f"**Severity:** {sev}")
                lines.append("")
                lines.append(f"> {finding.get('message', 'No message')}")
                
                if finding.get('suggestion'):
                    lines.append("")
                    lines.append(f"**Suggestion:** {finding['suggestion']}")
                
                lines.append("")
        
        return "\n".join(lines)
    
    def _generate_json(
        self,
        findings: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> str:
        """Generate JSON report."""
        report = {
            'title': self.config.title,
            'generated': datetime.now().isoformat(),
            'metadata': metadata or {},
            'summary': self._generate_summary(findings),
            'findings': findings,
        }
        return json.dumps(report, indent=2)
    
    def _generate_csv(self, findings: List[Dict[str, Any]]) -> str:
        """Generate CSV report."""
        output = io.StringIO()
        
        if not findings:
            return ""
        
        # Get all possible fields
        fieldnames = ['file_path', 'line', 'column', 'severity', 'category', 'message', 'suggestion', 'confidence']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        
        for finding in findings:
            writer.writerow(finding)
        
        return output.getvalue()
    
    def _generate_html(
        self,
        findings: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]],
    ) -> str:
        """Generate HTML report."""
        summary = self._generate_summary(findings)
        
        html_parts = [
            "<!DOCTYPE html>",
            "<html><head>",
            f"<title>{self.config.title}</title>",
            "<style>",
            "body { font-family: -apple-system, sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; }",
            "table { border-collapse: collapse; width: 100%; }",
            "th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }",
            "th { background-color: #f4f4f4; }",
            ".error { color: #d73a49; }",
            ".warning { color: #e36209; }",
            ".info { color: #0366d6; }",
            "</style>",
            "</head><body>",
            f"<h1>{self.config.title}</h1>",
            f"<p><strong>Generated:</strong> {datetime.now().isoformat()}</p>",
        ]
        
        # Summary
        if self.config.include_summary:
            html_parts.append("<h2>Summary</h2>")
            html_parts.append("<ul>")
            html_parts.append(f"<li><strong>Total Findings:</strong> {summary['total_findings']}</li>")
            html_parts.append(f"<li><strong>Files Affected:</strong> {summary['files_affected']}</li>")
            html_parts.append("</ul>")
        
        # Findings table
        if self.config.include_details and findings:
            html_parts.append("<h2>Findings</h2>")
            html_parts.append("<table>")
            html_parts.append("<tr><th>Severity</th><th>Category</th><th>File</th><th>Line</th><th>Message</th></tr>")
            
            for finding in findings:
                sev = finding.get('severity', 'unknown')
                html_parts.append(
                    f"<tr class='{sev}'>"
                    f"<td>{sev}</td>"
                    f"<td>{finding.get('category', '')}</td>"
                    f"<td>{finding.get('file_path', '')}</td>"
                    f"<td>{finding.get('line', '')}</td>"
                    f"<td>{finding.get('message', '')}</td>"
                    "</tr>"
                )
            
            html_parts.append("</table>")
        
        html_parts.append("</body></html>")
        
        return "\n".join(html_parts)
