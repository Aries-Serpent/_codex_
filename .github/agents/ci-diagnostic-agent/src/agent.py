#!/usr/bin/env python3
"""
CI Diagnostic Agent - Automated CI failure analysis and remediation
Part of Phase 8: Advanced Monitoring implementation
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import yaml


@dataclass
class Finding:
    """A single diagnostic finding"""
    pattern_name: str
    severity: str
    line_number: Optional[int]
    matched_text: str
    context: str


@dataclass
class DiagnosticReport:
    """Complete diagnostic report"""
    run_id: str
    timestamp: str
    status: str
    root_cause: Optional[str]
    findings: List[Finding]
    remediation: List[str]
    auto_fixable: bool
    confidence: float


class CIDiagnosticAgent:
    """Automated CI failure analysis and remediation"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize agent with configuration"""
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "agent.yml"
        
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """Compile regex patterns from config"""
        patterns = {}
        for name, config in self.config['failure_patterns'].items():
            patterns[name] = re.compile(config['pattern'])
        return patterns
    
    def analyze_logs(self, logs: str) -> List[Finding]:
        """Analyze logs for known failure patterns"""
        findings = []
        
        for line_num, line in enumerate(logs.split('\n'), 1):
            for pattern_name, regex in self.patterns.items():
                match = regex.search(line)
                if match:
                    pattern_config = self.config['failure_patterns'][pattern_name]
                    
                    # Get context (2 lines before and after)
                    lines = logs.split('\n')
                    start = max(0, line_num - 3)
                    end = min(len(lines), line_num + 2)
                    context = '\n'.join(lines[start:end])
                    
                    finding = Finding(
                        pattern_name=pattern_name,
                        severity=pattern_config['severity'],
                        line_number=line_num,
                        matched_text=match.group(0),
                        context=context
                    )
                    findings.append(finding)
        
        return findings
    
    def determine_root_cause(self, findings: List[Finding]) -> Tuple[Optional[str], float]:
        """Determine most likely root cause with confidence score"""
        if not findings:
            return None, 0.0
        
        # Count findings by severity
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        pattern_counts = {}
        
        for finding in findings:
            severity_counts[finding.severity] += 1
            pattern_counts[finding.pattern_name] = pattern_counts.get(finding.pattern_name, 0) + 1
        
        # Prioritize by severity and frequency
        if severity_counts['critical'] > 0:
            # Most frequent critical issue
            critical_findings = [f for f in findings if f.severity == 'critical']
            most_common = max(set(f.pattern_name for f in critical_findings),
                            key=lambda x: pattern_counts[x])
            confidence = min(pattern_counts[most_common] / len(findings), 1.0)
            return most_common, confidence * 0.95  # 95% max confidence for critical
        
        # Otherwise, most frequent high severity
        high_findings = [f for f in findings if f.severity == 'high']
        if high_findings:
            most_common = max(set(f.pattern_name for f in high_findings),
                            key=lambda x: pattern_counts[x])
            confidence = min(pattern_counts[most_common] / len(findings), 1.0)
            return most_common, confidence * 0.85
        
        # Fall back to most common pattern
        most_common = max(pattern_counts, key=pattern_counts.get)
        confidence = min(pattern_counts[most_common] / len(findings), 1.0)
        return most_common, confidence * 0.70
    
    def suggest_fixes(self, root_cause: Optional[str]) -> List[str]:
        """Suggest remediation steps"""
        if not root_cause:
            return ["No specific root cause identified. Review logs manually."]
        
        pattern_config = self.config['failure_patterns'].get(root_cause, {})
        remediation = [pattern_config.get('remediation', 'No remediation available')]
        
        # Add specific fixes based on pattern
        if root_cause == 'disk_full':
            remediation.extend([
                "Add disk cleanup step: sudo rm -rf /usr/share/dotnet /opt/ghc",
                "Remove Docker images: docker rmi $(docker images -q)",
                "Clear apt caches: sudo apt-get clean"
            ])
        elif root_cause == 'import_error':
            remediation.extend([
                "Verify __all__ exports in __init__.py",
                "Check for circular imports",
                "Ensure package is installed: pip install -e ."
            ])
        elif root_cause == 'timeout':
            remediation.extend([
                "Add @pytest.mark.timeout(300) decorator",
                "Mock expensive operations",
                "Use parallel execution where safe"
            ])
        elif root_cause == 'cache_miss':
            remediation.extend([
                "Clear caches: find . -type d -name __pycache__ -exec rm -rf {} +",
                "Remove .pytest_cache",
                "Retry workflow after cleanup"
            ])
        
        return remediation
    
    def can_auto_fix(self, root_cause: Optional[str]) -> bool:
        """Determine if issue can be automatically fixed"""
        if not root_cause:
            return False
        
        pattern_config = self.config['failure_patterns'].get(root_cause, {})
        return pattern_config.get('auto_fixable', False)
    
    def analyze_failure(self, run_id: str, logs: str) -> DiagnosticReport:
        """Complete failure analysis"""
        findings = self.analyze_logs(logs)
        root_cause, confidence = self.determine_root_cause(findings)
        remediation = self.suggest_fixes(root_cause)
        auto_fixable = self.can_auto_fix(root_cause)
        
        if not findings:
            status = "no_issues_detected"
        elif confidence > 0.8:
            status = "high_confidence"
        elif confidence > 0.5:
            status = "medium_confidence"
        else:
            status = "low_confidence"
        
        return DiagnosticReport(
            run_id=run_id,
            timestamp=datetime.now().isoformat(),
            status=status,
            root_cause=root_cause,
            findings=findings,
            remediation=remediation,
            auto_fixable=auto_fixable,
            confidence=confidence
        )
    
    def generate_markdown_report(self, report: DiagnosticReport) -> str:
        """Generate markdown report"""
        md = f"""## 🔍 CI Diagnostic Report

**Run ID**: {report.run_id}  
**Timestamp**: {report.timestamp}  
**Status**: {report.status}  
**Confidence**: {report.confidence:.1%}

### Root Cause Analysis

"""
        
        if report.root_cause:
            md += f"**Identified Issue**: `{report.root_cause}`  \n"
            md += f"**Auto-fixable**: {'✅ Yes' if report.auto_fixable else '❌ No'}  \n\n"
        else:
            md += "**No specific root cause identified**  \n\n"
        
        if report.findings:
            md += f"### Findings ({len(report.findings)} total)\n\n"
            
            # Group by severity
            by_severity = {}
            for finding in report.findings:
                by_severity.setdefault(finding.severity, []).append(finding)
            
            for severity in ['critical', 'high', 'medium', 'low']:
                if severity in by_severity:
                    md += f"\n#### {severity.upper()} ({len(by_severity[severity])})\n\n"
                    for finding in by_severity[severity][:5]:  # Limit to 5 per severity
                        md += f"- **{finding.pattern_name}** (line {finding.line_number})\n"
                        md += f"  ```\n  {finding.matched_text}\n  ```\n"
        
        md += "\n### Recommended Actions\n\n"
        for i, action in enumerate(report.remediation, 1):
            md += f"{i}. {action}\n"
        
        md += "\n### Next Steps\n\n"
        if report.auto_fixable and report.confidence > 0.7:
            md += "✅ **This issue can be automatically remediated.**  \n"
            md += "Reply with `@copilot auto-fix` to attempt automatic remediation.  \n\n"
        else:
            md += "⚠️ **Manual intervention required.**  \n"
            md += "Review the findings above and apply the recommended actions.  \n\n"
        
        md += "---\n"
        md += "*Generated by CI Diagnostic Agent v1.0.0*"
        
        return md
    
    def save_report(self, report: DiagnosticReport, output_path: str):
        """Save report to file"""
        # Save JSON
        json_path = Path(output_path).with_suffix('.json')
        with open(json_path, 'w') as f:
            # Convert findings to dicts
            report_dict = asdict(report)
            json.dump(report_dict, f, indent=2)
        
        # Save Markdown
        md_path = Path(output_path).with_suffix('.md')
        with open(md_path, 'w') as f:
            f.write(self.generate_markdown_report(report))
        
        print(f"✅ Report saved to {json_path} and {md_path}")


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description="CI Diagnostic Agent")
    parser.add_argument('--run-id', required=True, help='CI run ID to analyze')
    parser.add_argument('--logs', help='Path to log file (or reads stdin)')
    parser.add_argument('--output', default='diagnostic_report', help='Output file path (no extension)')
    parser.add_argument('--config', help='Path to agent config')
    parser.add_argument('--test', action='store_true', help='Run in test mode')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = CIDiagnosticAgent(config_path=args.config)
    
    # Test mode
    if args.test:
        print("✅ CI Diagnostic Agent initialized successfully")
        print(f"📋 Loaded {len(agent.patterns)} failure patterns")
        print("🔍 Pattern names:", list(agent.patterns.keys()))
        return 0
    
    # Read logs
    if args.logs:
        with open(args.logs) as f:
            logs = f.read()
    else:
        logs = sys.stdin.read()
    
    # Analyze
    print(f"🔍 Analyzing logs for run {args.run_id}...")
    report = agent.analyze_failure(args.run_id, logs)
    
    # Save report
    agent.save_report(report, args.output)
    
    # Print summary
    print(f"\n📊 Analysis Summary:")
    print(f"   Root cause: {report.root_cause or 'Unknown'}")
    print(f"   Confidence: {report.confidence:.1%}")
    print(f"   Findings: {len(report.findings)}")
    print(f"   Auto-fixable: {'Yes' if report.auto_fixable else 'No'}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
