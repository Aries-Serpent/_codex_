"""
Security Alert Verification Agent - Token Integration Example

Demonstrates alert triage flow with Level 2 token and safe fallback pattern.

Key Concepts:
- Level 2 (CODEX_BACKUP_TOKEN) token with fallback
- Scopes: repo, security_events, actions:read_self
- Safe fallback to GITHUB_TOKEN if Level 2 unavailable
- Security scanning operations
"""

import logging
import requests
from typing import Dict, List
from dataclasses import dataclass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Alert:
    id: int
    tool: str
    state: str
    severity: str
    url: str


class SecurityAlertVerificationAgent:
    """Verify and triage security alerts."""
    
    def __init__(self):
        from scripts.ci._token_resolver import get_token, validate_scope
        
        # Try Level 2 first, fallback to Level 1
        self.token = get_token(required_elevated=True)
        
        if not self.token:
            logger.warning("Level 2 unavailable, using standard token")
            self.token = get_token(required_elevated=False)
            if not self.token:
                raise RuntimeError("No token available")
        
        # Validate available scopes
        try:
            validate_scope(self.token, ['repo', 'security_events'])
        except Exception:
            logger.warning("Full scopes not available, limited functionality")
    
    def verify_security_alerts(self, repo: str) -> List[Alert]:
        """Retrieve and verify security alerts."""
        url = f"https://api.github.com/repos/{repo}/security-advisories"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            alerts = []
            for item in response.json():
                alerts.append(Alert(
                    id=item['id'],
                    tool=item.get('tool', 'unknown'),
                    state=item.get('state', 'open'),
                    severity=item.get('severity', 'unknown'),
                    url=item.get('html_url', '')
                ))
            
            logger.info(
                "alerts_retrieved",
                extra={"repo": repo, "count": len(alerts)}
            )
            return alerts
        
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                logger.error("Insufficient scope for security alerts")
            raise
    
    def create_alert_issue(
        self,
        repo: str,
        alert: Alert,
        title: str = None
    ) -> Dict:
        """Create GitHub issue for alert."""
        title = title or f"Security Alert: {alert.tool} - {alert.severity}"
        
        url = f"https://api.github.com/repos/{repo}/issues"
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        body = f"""## Security Alert

**Tool**: {alert.tool}
**State**: {alert.state}
**Severity**: {alert.severity}

[View Alert]({alert.url})
"""
        
        try:
            response = requests.post(
                url,
                json={"title": title, "body": body},
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            issue = response.json()
            logger.info(
                "alert_issue_created",
                extra={"repo": repo, "issue": issue['number']}
            )
            return issue
        
        except requests.HTTPError as e:
            logger.error(f"Failed to create issue: {e}")
            raise


if __name__ == "__main__":
    agent = SecurityAlertVerificationAgent()
    alerts = agent.verify_security_alerts("owner/repo")
    print(f"Found {len(alerts)} alerts")
