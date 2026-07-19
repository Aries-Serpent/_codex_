#!/usr/bin/env python3
"""
Extract security vulnerability metrics.

Aggregates pip-audit and bandit findings:
- Count of vulnerabilities by severity
- Dependency health score
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def extract_security(
    pip_audit_json: str,
    bandit_json: str,
    vulns_output: str,
    health_output: str
) -> None:
    """Extract security metrics."""
    
    # Load pip-audit findings
    pip_vulns = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    
    try:
        with open(pip_audit_json) as f:
            pip_data = json.load(f)
            
        # Count vulnerabilities by severity
        for vuln in pip_data.get('vulnerabilities', []):
            severity = vuln.get('advisory', {}).get('severity', '').lower()
            if severity in pip_vulns:
                pip_vulns[severity] += 1
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Load bandit findings
    bandit_vulns = {'high': 0, 'medium': 0, 'low': 0}
    
    try:
        with open(bandit_json) as f:
            bandit_data = json.load(f)
        
        # Count findings by severity
        for finding in bandit_data.get('results', []):
            severity = finding.get('severity', '').lower()
            if severity in bandit_vulns:
                bandit_vulns[severity] += 1
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    
    # Create vulnerability output
    total_vulns = sum(pip_vulns.values()) + sum(bandit_vulns.values())
    
    vulns_output_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "security_vulnerabilities",
        "total_vulnerabilities": total_vulns,
        "by_severity": {
            "critical": pip_vulns['critical'],
            "high": pip_vulns['high'] + bandit_vulns['high'],
            "medium": pip_vulns['medium'] + bandit_vulns['medium'],
            "low": pip_vulns['low'] + bandit_vulns['low'],
        },
        "sources": {
            "pip_audit": sum(pip_vulns.values()),
            "bandit": sum(bandit_vulns.values()),
        },
        "targets": {
            "critical": 0,
            "high": 0,
            "medium_max": 5,
        },
        "source": "pip-audit + bandit",
    }
    
    # Calculate health score
    # Formula: 100 - (critical*10 + high*5 + medium*1 + low*0.1)
    health_score = 100 - (
        pip_vulns['critical'] * 10 +
        pip_vulns['high'] * 5 +
        pip_vulns['medium'] * 1 +
        bandit_vulns['high'] * 5 +
        bandit_vulns['medium'] * 1
    )
    health_score = max(0, min(100, health_score))  # Clamp to 0-100
    
    health_output_data = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "metric_id": "dependency_health",
        "health_score": round(health_score, 1),
        "target_score": 90.0,
        "status": "healthy" if health_score >= 90 else "at_risk" if health_score >= 70 else "critical",
        "details": {
            "critical_vulnerabilities": pip_vulns['critical'],
            "high_vulnerabilities": pip_vulns['high'] + bandit_vulns['high'],
            "medium_vulnerabilities": pip_vulns['medium'] + bandit_vulns['medium'],
        },
    }
    
    # Write vulnerability output
    vulns_file = Path(vulns_output)
    vulns_file.parent.mkdir(parents=True, exist_ok=True)
    with open(vulns_file, 'w') as f:
        json.dump(vulns_output_data, f, indent=2)
    
    # Write health output
    health_file = Path(health_output)
    health_file.parent.mkdir(parents=True, exist_ok=True)
    with open(health_file, 'w') as f:
        json.dump(health_output_data, f, indent=2)
    
    print(f"✅ Security metrics written to {vulns_output} and {health_output}")
    print(f"   Total vulnerabilities: {total_vulns}")
    print(f"   Critical: {pip_vulns['critical']}")
    print(f"   High: {pip_vulns['high'] + bandit_vulns['high']}")
    print(f"   Health score: {health_score:.1f}/100")


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: extract_security.py <pip_audit.json> <bandit.json> <vulns_output.json> <health_output.json>")
        sys.exit(1)
    
    extract_security(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
