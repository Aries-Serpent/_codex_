# Security Scripts

This directory contains scripts for managing security vulnerabilities and code scanning alerts in the repository.

## 📋 Available Scripts

### 1. Alert Management

#### `fetch_codeql_alerts.py`
Fetch all CodeQL code scanning alerts from GitHub API.

**Usage:**
```bash
# Fetch all open alerts
python scripts/security/fetch_codeql_alerts.py

# Fetch only high severity alerts
python scripts/security/fetch_codeql_alerts.py --severity high

# Fetch first 10 pages (for testing)
python scripts/security/fetch_codeql_alerts.py --max-pages 10

# Custom output directory
python scripts/security/fetch_codeql_alerts.py --output-dir /tmp/alerts
```

**Requirements:**
- `requests` library: `pip install requests`
- GitHub token with `security_events` scope (for read operations, via `GITHUB_TOKEN` env var)
  - Note: In GitHub Actions workflows, this is configured as `security-events: read` permission
  - For personal access tokens (PATs), use the `security_events` scope (no `:read`/`:write` suffix)

**Outputs:**
- `.codex/security/alert_inventory.json` - Complete alert data
- `.codex/security/alert_inventory.csv` - Spreadsheet format
- `.codex/security/alert_summary.md` - Human-readable summary

#### `close_codeql_alert.py`
Close resolved code scanning alerts via GitHub API.

**Usage:**
```bash
# Close a single alert as fixed
python scripts/security/close_codeql_alert.py \
  --alert 123 \
  --reason fixed \
  --comment "Fixed SQL injection vulnerability" \
  --pr 456

# Close multiple alerts
python scripts/security/close_codeql_alert.py \
  --alerts 123,124,125 \
  --reason fixed \
  --comment "Fixed in batch security update"

# Mark as false positive
python scripts/security/close_codeql_alert.py \
  --alert 789 \
  --reason false_positive \
  --comment "Test code demonstrating vulnerability detection"

# Dry run (don't actually close)
python scripts/security/close_codeql_alert.py \
  --alert 123 \
  --reason fixed \
  --comment "Testing closure process" \
  --dry-run
```

**Requirements:**
- `requests` library: `pip install requests`
- GitHub token with `security_events` scope (for write operations, via `GITHUB_TOKEN` env var)
  - Note: In GitHub Actions workflows, this is configured as `security-events: write` permission
  - For personal access tokens (PATs), use the `security_events` scope (no `:read`/`:write` suffix)

**Dismissal Reasons:**
- `fixed` - A fix has been deployed
- `false_positive` - This alert is a false positive
- `wont_fix` - This vulnerability will not be fixed
- `used_in_tests` - This is test code, not a real vulnerability

### 2. Security Analysis

#### `validate_security.py`
Run comprehensive security validation checks.

#### `validate_auth_security.py`
Validate authentication and authorization security.

## 🚀 Quick Start Guide

### Step 1: Set up GitHub Token

Create a GitHub personal access token with these permissions:
- `repo` (full control)
- `security_events` (read and write)

Export it as an environment variable:
```bash
export GITHUB_TOKEN="ghp_your_token_here"
```

### Step 2: Fetch All Alerts

```bash
# Fetch all open alerts
python scripts/security/fetch_codeql_alerts.py

# View the summary
cat .codex/security/alert_summary.md

# Analyze the JSON data
jq '.alerts | group_by(.severity) | map({severity: .[0].severity, count: length})' .codex/security/alert_inventory.json
```

### Step 3: Prioritize and Fix

1. Review the alert summary to identify critical/high severity issues
2. Fix vulnerabilities in your code
3. Create a PR with your fixes
4. After PR is merged, close the alerts

### Step 4: Close Resolved Alerts

```bash
# After fixing vulnerability in PR #456
python scripts/security/close_codeql_alert.py \
  --alert 123 \
  --reason fixed \
  --comment "Fixed SQL injection by using parameterized queries" \
  --pr 456
```

### Step 5: Track Progress

View closure log:
```bash
cat .codex/security/alert_closures.jsonl | jq -s '.'
```

## 📊 Workflow Integration

### GitHub Actions Integration

You can integrate these scripts into GitHub Actions workflows:

```yaml
- name: Fetch CodeQL Alerts
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    python scripts/security/fetch_codeql_alerts.py
    
- name: Upload Alert Report
  uses: actions/upload-artifact@v4
  with:
    name: codeql-alert-report
    path: .codex/security/
```

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:
```yaml
  - repo: local
    hooks:
      - id: security-check
        name: Security Check
        entry: python scripts/security/validate_security.py
        language: system
        pass_filenames: false
```

## 🔒 Security Best Practices

### Token Security
- **Never** commit GitHub tokens to the repository
- Use environment variables or secrets management
- Rotate tokens regularly (recommended: every 90 days)
- Use fine-grained tokens with minimal permissions

### Alert Handling
- **Critical/High**: Fix within 24-72 hours
- **Medium**: Fix within 1-2 weeks
- **Low**: Schedule for next sprint
- **False Positives**: Document thoroughly before dismissing

### Documentation
- Always provide detailed comments when closing alerts
- Link to PRs or commits that fixed the issue
- Document false positives with justification
- Track all closures in the log file

## 📚 Related Documentation

- [CodeQL Alert Resolution Planset](../../.codex/plans/CODEQL_ALERT_RESOLUTION_PLANSET.md)
- [Security Guidelines](../../docs/security/SECURITY_GUIDELINES.md) (to be created)
- [GitHub Code Scanning API](https://docs.github.com/en/rest/code-scanning)
- [CodeQL Documentation](https://codeql.github.com/docs/)

## 🐛 Troubleshooting

### "403 Resource not accessible by integration"
- Your GitHub token doesn't have sufficient permissions
- Ensure `security_events:read` permission is enabled
- For closing alerts, you need `security_events:write`

### "404 Repository not found"
- Check repository owner and name are correct
- Verify your token has access to the repository
- Ensure code scanning is enabled for the repository

### "Rate limit exceeded"
- GitHub API has rate limits (5000 requests/hour for authenticated)
- The scripts include automatic rate limit handling
- For large repositories, use `--max-pages` to process in batches

### No alerts found
- Verify code scanning is enabled in repository settings
- Check that CodeQL workflows have run successfully
- Try different state filters: `--state open`, `--state closed`

## 💡 Tips

### Performance Optimization
- Use `--max-pages` for testing with large repositories
- Process alerts in batches to avoid API rate limits
- Cache alert data locally to reduce API calls

### Alert Categorization
- Use the JSON output for custom analysis with `jq` or Python
- Group alerts by file/module for batch fixes
- Prioritize by severity and exploitability

### Automation
- Create shell scripts for common workflows
- Use GitHub Actions for scheduled alert checks
- Integrate with your CI/CD pipeline

## 🤝 Contributing

When adding new security scripts:
1. Follow the existing code structure
2. Add comprehensive docstrings
3. Include usage examples
4. Update this README
5. Add tests if applicable

## 📝 License

These scripts are part of the _codex_ repository and inherit its license.

---

**Questions?** Open an issue or contact @mbaetiong
