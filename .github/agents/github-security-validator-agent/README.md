# GitHub Security Validator Agent

A specialized GitHub Copilot Agent for validating security configurations, audit logging, and CodeQL suppressions across the repository. Automates security compliance checks and ensures security best practices are maintained.

## Purpose

Automates security validation activities including organization audit logging setup (HA-OPT-002) and CodeQL suppressions review with 90-day rotation cycle (HA-OPT-003) from the Human Admin Consolidated Action Tracker.

## Features

### 1. Organization Audit Logging (HA-OPT-002)
- Validates audit log configuration
- Checks retention policies
- Verifies log shipping to SIEM
- Monitors audit log access
- Reports compliance status

### 2. CodeQL Suppressions Review (HA-OPT-003)
- Reviews suppression comments in code
- Validates 90-day rotation cycle
- Identifies expired suppressions
- Generates renewal recommendations
- Tracks suppression patterns

### 3. Security Configuration Validation
- Validates branch protection rules
- Checks required status checks
- Verifies secret scanning configuration
- Validates dependency scanning
- Reports security posture

## Installation

No installation required. This agent is automatically available in GitHub Copilot Agent environment.

## Usage

### Via GitHub Copilot Agent

```markdown
@github-security-validator-agent Run security validation checks
```

### Via Command Line

```bash
cd .github/agents/github-security-validator-agent
python src/agent.py --task all --report json
```

## Validation Tasks

### Task 1: Audit Logging Validation
```bash
python src/agent.py --task audit-logging --verbose
```

**Checks**:
- Organization audit log enabled
- Retention period configured (minimum 90 days)
- Log streaming to external SIEM
- Audit log API access permissions
- Compliance with security policies

### Task 2: CodeQL Suppressions Review
```bash
python src/agent.py --task codeql-suppressions --verbose
```

**Checks**:
- Find all `// lgtm[rule-id]` comments
- Find all `// codeql[rule-id]` comments
- Calculate age of each suppression
- Identify suppressions > 90 days old
- Generate renewal recommendations

### Task 3: Branch Protection Validation
```bash
python src/agent.py --task branch-protection --verbose
```

### Task 4: Secret Scanning Configuration
```bash
python src/agent.py --task secret-scanning --verbose
```

## Configuration

Configuration is loaded from `config/agent.yml`:

```yaml
agent:
  name: github-security-validator-agent
  version: 1.0.0
  responsibilities:
    - HA-OPT-002  # Organization audit logging
    - HA-OPT-003  # CodeQL suppressions review

validation:
  audit_logging:
    enabled: true
    min_retention_days: 90
    require_siem_streaming: true
    
  codeql_suppressions:
    enabled: true
    max_age_days: 90
    require_justification: true
    patterns:
      - "lgtm\\[.*\\]"
      - "codeql\\[.*\\]"
      
  branch_protection:
    enabled: true
    protected_branches:
      - main
      - develop
      - production
    required_checks:
      - require_reviews: true
      - min_approvals: 1
      - dismiss_stale_reviews: true
      - require_code_owner_reviews: true
      
  secret_scanning:
    enabled: true
    check_push_protection: true
    check_validity: true

reporting:
  format: json
  output_dir: .reports/security-validator
  include_recommendations: true
```

## Output Examples

### JSON Report

```json
{
  "agent": "github-security-validator-agent",
  "version": "1.0.0",
  "timestamp": "2026-01-13T20:45:00Z",
  "overall_status": "passed",
  "validations": {
    "audit_logging": {
      "status": "passed",
      "enabled": true,
      "retention_days": 180,
      "siem_streaming": true,
      "compliance": "SOC2"
    },
    "codeql_suppressions": {
      "status": "warning",
      "total_suppressions": 12,
      "expired_suppressions": 3,
      "suppressions_to_review": [
        {
          "file": "src/monitoring/metrics.py",
          "line": 145,
          "rule": "py/sql-injection",
          "age_days": 127,
          "justification": "Parameterized query verified",
          "action": "renew_or_remove"
        }
      ]
    },
    "branch_protection": {
      "status": "passed",
      "protected_branches": 3,
      "all_checks_enabled": true
    },
    "secret_scanning": {
      "status": "passed",
      "enabled": true,
      "push_protection": true
    }
  },
  "recommendations": [
    "Review 3 expired CodeQL suppressions",
    "Update justification for suppressions older than 90 days"
  ]
}
```

## Integration with GitHub Actions

```yaml
name: Security Validation

on:
  schedule:
    - cron: '0 0 * * 1'  # Weekly on Monday
  workflow_dispatch:

jobs:
  validate-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Run Security Validator
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python .github/agents/github-security-validator-agent/src/agent.py \
            --task all \
            --report json \
            --output-dir ${{ github.workspace }}/.reports
            
      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: security-validation-results
          path: .reports/security-validator/
          
      - name: Create issue for failures
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const report = JSON.parse(
              fs.readFileSync('.reports/security-validator/summary.json', 'utf8')
            );
            
            github.rest.issues.create({
              title: '🔐 Security Validation Failures Detected',
              body: `Security validation checks have failed.\n\n**Details**: ${JSON.stringify(report, null, 2)}`,
              labels: ['security', 'automated']
            });
```

## Suppression Age Tracking

The agent maintains a database of suppression ages:

```json
{
  "suppressions": [
    {
      "id": "sup_001",
      "file": "src/api/handler.py",
      "line": 234,
      "rule": "py/sql-injection",
      "first_seen": "2025-10-15T00:00:00Z",
      "age_days": 90,
      "justification": "Input sanitized upstream",
      "reviewer": "security-team",
      "next_review": "2026-01-13T00:00:00Z",
      "status": "due_for_review"
    }
  ]
}
```

## Recommendations Engine

The agent provides actionable recommendations:

1. **Expired Suppressions**: "Remove suppression at `file:line` or update justification"
2. **Missing Justifications**: "Add justification comment for suppression at `file:line`"
3. **Audit Log Issues**: "Enable audit log retention for minimum 90 days"
4. **Branch Protection**: "Enable required reviewers for branch `main`"

## Development

### Running Locally

```bash
pip install pyyaml requests

python src/agent.py --task all --verbose
```

### Testing

```bash
python -m pytest tests/test_agent.py -v
```

## Troubleshooting

### Insufficient permissions
```
Error: Token does not have audit log read permissions
Solution: Grant 'read:audit_log' scope to GitHub token
```

### CodeQL suppressions not found
```
Warning: No CodeQL suppressions found in repository
Solution: This is expected if CodeQL is not used or no suppressions exist
```

## License

See repository root LICENSE file.
