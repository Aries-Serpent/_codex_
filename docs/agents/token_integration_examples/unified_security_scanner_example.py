"""
Unified Security Scanner Agent - Token Integration Example

Comprehensive multi-operation example combining multiple scopes and tools.

Key Concepts:
- Level 2 (CODEX_BACKUP_TOKEN) token
- Scopes: repo, security_events, contents:read
- Orchestrates multiple security scanning operations
- Aggregates results from different security tools
- Comprehensive error handling
"""

import logging
import requests
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SecurityAlert:
    tool: str
    severity: AlertSeverity
    title: str
    description: str
    location: Optional[str]
    cve: Optional[str]


@dataclass
class ScanResult:
    repo: str
    total_alerts: int
    by_severity: Dict[str, int]
    by_tool: Dict[str, int]
    alerts: List[SecurityAlert]
    scan_timestamp: str


class UnifiedSecurityScanner:
    """Unified security scanning across multiple tools."""
    
    # Supported security tools
    TOOLS = ['codeql', 'secret_scanning', 'dependabot', 'sast']
    
    def __init__(self):
        from scripts.ci._token_resolver import get_token, validate_scope
        
        self.token = get_token(required_elevated=True)
        if not self.token:
            self.token = get_token(required_elevated=False)
        
        validate_scope(self.token, ['repo', 'security_events', 'contents:read'])
        self.session = requests.Session()
        self.session.headers.update(
            {"Authorization": f"token {self.token}"}
        )
    
    def run_unified_security_scan(self, repo: str) -> ScanResult:
        """Run all security scanners and aggregate results."""
        
        all_alerts = []
        by_tool = {}
        
        logger.info(f"Starting unified security scan for {repo}")
        
        # Run CodeQL
        codeql_alerts = self._run_codeql_scan(repo)
        all_alerts.extend(codeql_alerts)
        by_tool['codeql'] = len(codeql_alerts)
        
        # Run Secret Scanning
        secret_alerts = self._run_secret_scan(repo)
        all_alerts.extend(secret_alerts)
        by_tool['secret_scanning'] = len(secret_alerts)
        
        # Run Dependabot Check
        dependabot_alerts = self._run_dependabot_check(repo)
        all_alerts.extend(dependabot_alerts)
        by_tool['dependabot'] = len(dependabot_alerts)
        
        # Aggregate by severity
        by_severity = {}
        for severity in AlertSeverity:
            count = sum(1 for a in all_alerts if a.severity == severity)
            if count > 0:
                by_severity[severity.value] = count
        
        result = ScanResult(
            repo=repo,
            total_alerts=len(all_alerts),
            by_severity=by_severity,
            by_tool=by_tool,
            alerts=all_alerts,
            scan_timestamp=self._get_timestamp()
        )
        
        logger.info(
            "scan_complete",
            extra={
                "repo": repo,
                "total": result.total_alerts,
                "tools": by_tool
            }
        )
        
        return result
    
    def _run_codeql_scan(self, repo: str) -> List[SecurityAlert]:
        """Run CodeQL scanning."""
        url = f"https://api.github.com/repos/{repo}/code-scanning/alerts"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            alerts = []
            for item in response.json():
                alerts.append(SecurityAlert(
                    tool='codeql',
                    severity=AlertSeverity(item.get('severity', 'medium')),
                    title=item['rule']['name'],
                    description=item['rule']['description'],
                    location=item.get('location', {}).get('path'),
                    cve=None
                ))
            
            logger.info(f"CodeQL: Found {len(alerts)} alerts")
            return alerts
        
        except requests.HTTPError as e:
            logger.warning(f"CodeQL scan failed: {e}")
            return []
    
    def _run_secret_scan(self, repo: str) -> List[SecurityAlert]:
        """Run secret scanning."""
        url = f"https://api.github.com/repos/{repo}/secret-scanning/alerts"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            alerts = []
            for item in response.json():
                alerts.append(SecurityAlert(
                    tool='secret_scanning',
                    severity=AlertSeverity.CRITICAL,
                    title=f"Exposed {item['secret_type']}",
                    description=item.get('resolution_reason', 'Exposed secret'),
                    location=None,
                    cve=None
                ))
            
            logger.info(f"Secret Scanning: Found {len(alerts)} alerts")
            return alerts
        
        except requests.HTTPError as e:
            logger.warning(f"Secret scan failed: {e}")
            return []
    
    def _run_dependabot_check(self, repo: str) -> List[SecurityAlert]:
        """Run Dependabot vulnerability check."""
        url = f"https://api.github.com/repos/{repo}/dependabot/alerts"
        
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            alerts = []
            for item in response.json():
                severity = item.get('security_advisory', {}).get('severity', 'medium')
                alerts.append(SecurityAlert(
                    tool='dependabot',
                    severity=AlertSeverity(severity),
                    title=item['security_advisory']['summary'],
                    description=item['security_advisory']['description'],
                    location=item.get('dependency', {}).get('manifest_path'),
                    cve=item['security_advisory'].get('cve_id')
                ))
            
            logger.info(f"Dependabot: Found {len(alerts)} alerts")
            return alerts
        
        except requests.HTTPError as e:
            logger.warning(f"Dependabot check failed: {e}")
            return []
    
    def generate_report(self, scan_result: ScanResult) -> str:
        """Generate human-readable security report."""
        
        report = f"""# Security Scan Report

**Repository**: {scan_result.repo}
**Timestamp**: {scan_result.scan_timestamp}
**Total Alerts**: {scan_result.total_alerts}

## By Severity

"""
        for severity, count in scan_result.by_severity.items():
            report += f"- **{severity.upper()}**: {count}\n"
        
        report += "\n## By Tool\n\n"
        for tool, count in scan_result.by_tool.items():
            report += f"- **{tool}**: {count}\n"
        
        report += "\n## Top Issues\n\n"
        
        # Sort by severity
        severity_order = {s.value: i for i, s in enumerate(AlertSeverity)}
        sorted_alerts = sorted(
            scan_result.alerts,
            key=lambda a: severity_order.get(a.severity.value, 999)
        )
        
        for alert in sorted_alerts[:10]:
            report += f"- **{alert.severity.value.upper()}** {alert.tool}: {alert.title}\n"
            if alert.cve:
                report += f"  CVE: {alert.cve}\n"
        
        return report
    
    @staticmethod
    def _get_timestamp() -> str:
        from datetime import datetime
        return datetime.utcnow().isoformat()


if __name__ == "__main__":
    scanner = UnifiedSecurityScanner()
    result = scanner.run_unified_security_scan("owner/repo")
    
    print(f"Scan Results:")
    print(f"  Total: {result.total_alerts}")
    print(f"  By Tool: {result.by_tool}")
    print(f"  By Severity: {result.by_severity}")
    
    report = scanner.generate_report(result)
    print("\n" + report)
