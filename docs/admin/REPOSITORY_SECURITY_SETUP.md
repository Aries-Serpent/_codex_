# Repository Administration Guide
## Complete Setup & Configuration for _codex_ Security Infrastructure

**Document Version**: 2.0
**Last Updated**: 2026-06-22
**Maintainer**: Security Team

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Repository Settings](#repository-settings)
3. [Environment Variables](#environment-variables)
4. [GitHub Actions Secrets](#github-actions-secrets)
5. [Branch Protection Rules](#branch-protection-rules)
6. [Security Scanning Configuration](#security-scanning-configuration)
7. [Dependency Management](#dependency-management)
8. [Pre-commit Hooks Setup](#pre-commit-hooks-setup)
9. [CI/CD Workflows](#cicd-workflows)
10. <!-- BROKEN ANCHOR: [Monitoring & Alerting](#monitoring-alerting) -->
11. [Team Permissions](#team-permissions)
12. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides complete instructions for repository administrators to configure and maintain the security infrastructure for the `_codex_` repository.

### What's Included

✅ **Security Utilities Module** (`src/codex/security/`)
✅ **Encrypted Storage** with multiple algorithms
✅ **Performance Benchmarks** for all security functions
✅ **Integration Tests** (18 test cases)
✅ **Comprehensive Documentation**
✅ **Pre-commit Hooks** for secret detection
✅ **CI/CD Security Workflows**

---

## Repository Settings

### 1. General Settings

Navigate to: **Settings** → **General**

#### Required Configurations:

```yaml
Repository visibility: Private (recommended) or Public
Features:
  - ✅ Issues
  - ✅ Pull Requests
  - ✅ Discussions (optional)
  - ✅ Projects (optional)

Pull Requests:
  - ✅ Allow squash merging
  - ✅ Allow rebase merging
  - ✅ Always suggest updating pull request branches
  - ✅ Automatically delete head branches

Security:
  - ✅ Enable Dependabot alerts
  - ✅ Enable Dependabot security updates
  - ✅ Enable CodeQL code scanning
```

### 2. Security & Analysis

Navigate to: **Settings** → **Security & analysis**

#### Enable All Security Features:

```yaml
Dependency graph: ✅ Enabled
Dependabot alerts: ✅ Enabled
Dependabot security updates: ✅ Enabled

Code scanning:
  - ✅ CodeQL analysis (setup via workflow)
  - ✅ Secret scanning
  - ✅ Secret scanning push protection

Private vulnerability reporting: ✅ Enabled
```

---

## Environment Variables

### Required for Local Development

Create `.env` file (DO NOT COMMIT):

```bash
# Security - Encryption Key for SecureStorage
ENCRYPTION_KEY="<generate-with-python-below>"

# Optional: Logging Configuration
LOG_SANITIZE_MAX_LENGTH=1000
MASK_TOKEN_SHOW_CHARS=6

# Optional: Performance Settings
SECURITY_CACHE_SIZE=10000
```

### Generate Encryption Key

```python
python3 << 'EOF'
from cryptography.fernet import Fernet
print(f"ENCRYPTION_KEY={Fernet.generate_key().decode()}")
EOF
```

**IMPORTANT**: Store the key securely:
- Use password manager
- Add to team secrets vault
- Never commit to git
- Rotate every 90 iterations

---

## GitHub Actions Secrets

Navigate to: **Settings** → **Secrets and variables** → **Actions**

### Required Secrets

| Secret Name | Description | How to Generate |
|-------------|-------------|-----------------|
| `ENCRYPTION_KEY` | Fernet encryption key for CI/CD | See above |
| `CODECOV_TOKEN` | Code coverage reporting (optional) | From codecov.io |
| `SLACK_WEBHOOK_URL` | Security alert notifications (optional) | From Slack workspace |

### Add Secret via CLI:

```bash
gh secret set ENCRYPTION_KEY --body "$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
```

### Add Secret via Web UI:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Name: `ENCRYPTION_KEY`
4. Value: Paste generated key
5. Click **Add secret**

---

## Branch Protection Rules

Navigate to: **Settings** → **Branches** → **Add branch protection rule**

### Protect `main` Branch

```yaml
Branch name pattern: main

Rules:
  - ✅ Require a pull request before merging
    - ✅ Require approvals: 1
    - ✅ Dismiss stale pull request approvals when new commits are pushed
    - ✅ Require review from Code Owners

  - ✅ Require status checks to pass before merging
    - ✅ Require branches to be up to date before merging
    - Required checks:
      - test (Python 3.12)
      - security-scan
      - codeql
      - pre-commit

  - ✅ Require conversation resolution before merging
  - ✅ Require signed commits (optional but recommended)
  - ✅ Require linear history
  - ✅ Do not allow bypassing the above settings

  - Rules applied to administrators: ✅ Yes
```

### Protect `0D_base_` Branch (Development)

```yaml
Branch name pattern: 0D_base_

Rules:
  - ✅ Require a pull request before merging
    - Require approvals: 0 (for rapid iteration)

  - ✅ Require status checks to pass before merging
    - Required checks:
      - test
      - security-scan

  - ✅ Require conversation resolution before merging
  - Allow force pushes: ❌ No
```

---

## Security Scanning Configuration

### 1. CodeQL Configuration

File: `.github/workflows/codeql-analysis.yml` (already exists)

Verify configuration:

```yaml
name: CodeQL

on:
  push:
    branches: [main, 0D_base_]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * 1'  # Weekly Monday 6am

jobs:
  analyze:
    runs-on: ubuntu-latest
    permissions:
      security-events: write
      contents: read

    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
          queries: security-and-quality
      - uses: github/codeql-action/analyze@v3
```

### 2. Secret Scanning

Already enabled in repository settings. Configure alerts:

Navigate to: **Settings** → **Code security** → **Secret scanning**

```yaml
Push protection: ✅ Enabled
Alert notifications:
  - ✅ Email notifications to admins
  - ✅ Web notifications

Custom patterns: (Add if needed)
  - Pattern name: Internal API Token
  - Pattern: internal_[a-zA-Z0-9]{32}
```

### 3. Dependabot Configuration

File: `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "per-phase"
      day: "monday"
    open-pull-requests-limit: 10
    reviewers:
      - "security-team"
    labels:
      - "dependencies"
      - "security"

  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "per-phase"
    labels:
      - "github-actions"
```

---

## Dependency Management

### Per-Iteration Maintenance Tasks

```bash
# 1. Check for vulnerabilities
pip-audit --desc

# 2. Review Dependabot PRs
gh pr list --label dependencies

# 3. Update requirements if needed
pip-compile requirements.in -o requirements/lock.txt --upgrade

# 4. Run security tests
pytest tests/security/ -v

# 5. Regenerate SBOMs
syft packages dir:. -o spdx-json > sbom.json
```

### Vulnerability Response SLA

| Severity | Response Time | Fix Time |
|----------|---------------|----------|
| Critical | 24 Commits | 7 iterations |
| High | 48 Commits | 14 iterations |
| Moderate | 1 phase | 30 iterations |
| Low | 2 phases | 90 iterations |

---

## Pre-commit Hooks Setup

### For All Developers

Add to team onboarding documentation:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
cd /path/to/_codex_
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Update hooks
pre-commit autoupdate
```

### Verify Hooks Configuration

File: `.pre-commit-config.yaml`

Ensure these hooks are present:

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    hooks:
      - id: detect-secrets

  - repo: https://github.com/gitleaks/gitleaks
    hooks:
      - id: gitleaks

  - repo: https://github.com/PyCQA/bandit
    hooks:
      - id: bandit

  - repo: https://github.com/pypa/pip-audit
    hooks:
      - id: pip-audit
```

---

## CI/CD Workflows

### Security Workflows to Monitor

1. **Security Scan** (`.github/workflows/security-scan.yml`)
   - Runs pip-audit
   - Scans for secrets with gitleaks
   - Runs Semgrep security rules

2. **CodeQL Analysis** (`.github/workflows/codeql-analysis.yml`)
   - Runs on push to main/0D_base_
   - per-phase scheduled scan
   - Blocks merge on Critical/High findings

3. **Dependency Audit** (`.github/workflows/scheduled-dependency-audit.yml`)
   - Weekly Monday 6am UTC
   - Checks for new vulnerabilities
   - Auto-creates issues for updates

### Workflow Permissions

Ensure workflows have minimum required permissions:

```yaml
permissions:
  contents: read
  security-events: write  # For CodeQL/SARIF uploads
  issues: write  # For creating security issues
  pull-requests: write  # For Dependabot PRs
```

---

## Monitoring & Alerting

### 1. GitHub Security Tab

Navigate to: **Security** tab

Monitor:
- ✅ Dependabot alerts
- ✅ CodeQL scanning alerts
- ✅ Secret scanning alerts
- ✅ Security advisories

### 2. Email Notifications

Configure in: **Settings** → **Notifications**

```yaml
Security alerts:
  - ✅ Email notifications
  - ✅ Web + Mobile notifications

Recipients:
  - Repository admins
  - Security team members
```

### 3. Slack Integration (Optional)

Add webhook to `.github/workflows/security-scan.yml`:

```yaml
- name: Notify Slack on Failure
  if: failure()
  run: |
    curl -X POST ${{ secrets.SLACK_WEBHOOK_URL }} \
      -H 'Content-Type: application/json' \
      -d '{
        "text": "🚨 Security scan failed in _codex_",
        "blocks": [{
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*Security Alert*\nWorkflow: ${{ github.workflow }}\nBranch: ${{ github.ref }}\n<${{ github.server_url }}/${{ github.repository }}/actions/runs/${{ github.run_id }}|View Run>"
          }
        }]
      }'
```

---

## Team Permissions

### Recommended Team Structure

Navigate to: **Settings** → **Collaborators and teams**

| Team | Role | Access Level | Responsibilities |
|------|------|--------------|------------------|
| Admins | Admin | Write + Admin | Repository settings, secret management |
| Security Team | Maintain | Write | Security reviews, vulnerability response |
| Developers | Write | Write | Code contributions, PR reviews |
| Bots | Write | Write | Copilot, Dependabot, automated PRs |

### CODEOWNERS File

Create `.github/CODEOWNERS`:

```
# Security-sensitive files require security team review
/src/codex/security/ @org/security-team
/docs/security/ @org/security-team
/.github/workflows/security-*.yml @org/security-team
/requirements*.txt @org/security-team

# All files require at least one review
* @org/developers
```

---

## Troubleshooting

### Issue: Encryption Key Not Found

**Error**: `ValueError: Encryption key required`

**Solution**:
```bash
# Set environment variable
export ENCRYPTION_KEY="$(python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

# Or add to GitHub Secrets
gh secret set ENCRYPTION_KEY --body "your-key-here"
```

### Issue: Pre-commit Hooks Failing

**Error**: `detect-secrets` or `gitleaks` fails

**Solution**:
```bash
# Update hooks
pre-commit autoupdate

# Clear cache
pre-commit clean

# Reinstall
pre-commit uninstall
pre-commit install

# Skip hook temporarily (emergency only)
git commit --no-verify
```

### Issue: CodeQL Analysis Timeout

**Error**: CodeQL analysis takes >6 hours

**Solution**:
```yaml
# In .github/workflows/codeql-analysis.yml
- uses: github/codeql-action/init@v3
  with:
    languages: python
    queries: security-only  # Changed from security-and-quality
```

### Issue: Dependabot PRs Not Auto-Merging

**Solution**:
1. Verify branch protection allows Dependabot PRs
2. Check workflow permissions
3. Enable auto-merge in Dependabot settings:

```yaml
# .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "per-phase"
    auto-merge: true  # Add this
    auto-merge-patch: true
```

---

## Verification Checklist

After completing setup, verify:

### Security Features
- [ ] Dependabot alerts enabled and working
- [ ] CodeQL scanning runs successfully
- [ ] Secret scanning detects test secrets
- [ ] Pre-commit hooks block commits with secrets

### Encryption
- [ ] `ENCRYPTION_KEY` set in GitHub Secrets
- [ ] SecureStorage works in CI/CD
- [ ] All algorithms (Fernet, AES-GCM, ChaCha20) functional

### Testing
- [ ] Security integration tests pass (`pytest tests/security/`)
- [ ] Benchmarks run successfully (`python benchmarks/security_benchmarks.py`)
- [ ] All CI workflows complete without errors

### Documentation
- [ ] README.md updated with security section
- [ ] SECURITY_GUIDELINES.md accessible to team
- [ ] This admin guide shared with all admins

### Team Access
- [ ] CODEOWNERS file configured
- [ ] Security team has appropriate permissions
- [ ] All developers have pre-commit hooks installed

---

## Quick Reference Commands

```bash
# Check security status
gh api repos/:owner/:repo/vulnerability-alerts

# List Dependabot alerts
gh api repos/:owner/:repo/dependabot/alerts

# Run security scan locally
pre-commit run --all-files

# Generate encryption key
python3 -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'

# Test security utilities
python3 -c 'import sys; sys.path.insert(0, "src"); from codex.security import mask_token; print(mask_token("test_key_12345"))'

# Run benchmarks
python benchmarks/security_benchmarks.py

# Run security tests
pytest tests/security/ -v

# Check for vulnerabilities
pip-audit --desc

# Update dependencies
pip-compile requirements.in -o requirements/lock.txt --upgrade
```

---

## Additional Resources

- **Internal Wiki**: Security Best Practices
- **Slack Channel**: #security-alerts
- **Email**: security@localhost
- **Incident Response**: [Runbook](../security/INCIDENT_RESPONSE.md)

---

## Maintenance Schedule

### per-iteration
- Monitor Dependabot alerts
- Review CodeQL findings

### Per Iteration Cycle
- Review security scan results
- Triage new vulnerabilities
- Update dependencies (automated)

### Per Iteration Phase
- Security team retrospective
- Update documentation
- Review access permissions

### Per Iteration Milestone
- Full security audit
- Penetration testing
- Update security policies
- Rotate encryption keys

---

**Document Owner**: Security Team
**Review Cycle**: Iteration-based (every 3 major releases)
**Next Review**: 2026-03-23T00:00:00Z
**Version**: 2.0

For questions or updates, contact: security@localhost

---

## 🎯 Mission Overview

**Objective**: Establish comprehensive security infrastructure for repository including encryption, scanning, monitoring, and compliance enforcement.

**Energy Level**: ⚡⚡⚡⚡⚡ (5/5 - Security Critical)

**Status**: 🟢 Active

---

## ⚖️ Verification Checklist

### Security Features Configuration
- [ ] Dependabot alerts enabled and monitored
- [ ] CodeQL scanning runs on push and per-phase schedule
- [ ] Secret scanning with push protection active
- [ ] Pre-commit hooks installed for all developers
- [ ] Branch protection rules enforced on main/0D_base_

### Encryption & Secrets
- [ ] `ENCRYPTION_KEY` generated and stored in GitHub Secrets
- [ ] Fernet encryption key stored in team password manager
- [ ] SecureStorage module functional in CI/CD workflows
- [ ] All three algorithms (Fernet, AES-GCM, ChaCha20) tested
- [ ] Key rotation schedule documented (90 iteration cycle)

### Monitoring & Alerting
- [ ] GitHub Security tab reviewed per-phase
- [ ] Email notifications configured for admins
- [ ] Slack webhook integrated for critical alerts (optional)
- [ ] Dependabot PRs reviewed within SLA timeframes
- [ ] Vulnerability response SLA documented and shared

### Team & Access Control
- [ ] CODEOWNERS file configured for sensitive paths
- [ ] Team permissions assigned (Admins, Security, Developers, Bots)
- [ ] Security team has maintain/write access
- [ ] All developers completed pre-commit setup
- [ ] Repository admin access limited to authorized personnel

---

## 📈 Success Metrics

| Metric | Current | Target | Status |
|--------|---------|--------|--------|
| Security Scan Coverage | 100% | 100% | 🟢 |
| Critical Vulnerability SLA | <24h response | <24h | 🟢 |
| High Vulnerability SLA | <48h response | <48h | 🟢 |
| Pre-commit Hook Adoption | Team-wide | 100% | 🟢 |
| Secret Detection Rate | 100% | 100% | 🟢 |
| Encryption Algorithm Support | 3 algorithms | ≥3 | 🟢 |
| Branch Protection Compliance | main + 0D_base_ | 100% critical branches | 🟢 |
| Quarterly Security Audit | Scheduled | 4/year | 🟢 |

---

## ⚛️ Physics Alignment

| Principle | Application | Implementation |
|-----------|-------------|----------------|
| Path 🛤️ | Systematic security hardening progression | 10-phase setup: Settings → Secrets → Branch Protection → Scanning → Monitoring |
| Fields 🔄 | Repository state transformation to secure baseline | Unsecured → Monitoring enabled → Secrets protected → Compliance enforced |
| Patterns 👁️ | Continuous security posture observation | Iteration-cycle scans, continuous alert monitoring, milestone audits |
| Redundancy 🔀 | Multi-layer security defense | Pre-commit hooks + CI scans + CodeQL + Dependabot + Secret scanning |
| Balance ⚖️ | Security rigor vs developer velocity | Automated security checks with clear bypass procedures for emergencies |

---

## ⚡ Energy Distribution

| Phase | Energy | Rationale |
|-------|--------|-----------|
| Initial Repository Configuration | ⚡⚡⚡⚡⚡ | Foundation - incorrect settings undermine all other security |
| Encryption Key Generation | ⚡⚡⚡⚡⚡ | Critical - protects all encrypted data at rest |
| Branch Protection Setup | ⚡⚡⚡⚡⚡ | Essential - prevents unauthorized/unreviewed changes to production |
| Security Scanning Configuration | ⚡⚡⚡⚡ | High priority - automated detection of vulnerabilities |
| Pre-commit Hook Deployment | ⚡⚡⚡⚡ | Important - prevents secrets from entering repository |
| Monitoring & Alerting | ⚡⚡⚡⚡ | Critical for incident response |
| Team Permissions & CODEOWNERS | ⚡⚡⚡⚡ | Ensures human oversight of sensitive changes |
| Dependency Management | ⚡⚡⚡ | Ongoing maintenance task |

**Total Energy Investment**: 31/40 units

---

## 🧠 Redundancy Patterns

**Rollback Strategy**: All configuration changes made via Infrastructure-as-Code (YAML files). Rollback by reverting commits to `.github/` directory.

**Parallel Paths**:
- If CodeQL analysis times out → Switch to `security-only` queries instead of `security-and-quality`
- If Dependabot PRs not merging → Enable manual merge workflow with security team approval
- If pre-commit hooks block valid commits → Temporary bypass with `--no-verify` (logged and reviewed)
- If encryption library unavailable → Use environment variable encryption key (with warning)
- If GitHub Actions secrets unavailable → Support local `.env` file for development (not committed)

**Recovery Procedures**:
1. **Encryption Key Lost**: Generate new key, re-encrypt all secrets, update `ENCRYPTION_KEY` in GitHub, rotate immediately
2. **CodeQL False Positives**: Add suppression comment with justification, track in security issue for review
3. **Dependabot Alert Storm**: Triage by severity (Critical/High first), batch-update compatible versions
4. **Secret Scanning False Positive**: Add to `.gitignore` patterns or configure custom secret pattern exclusions
5. **Branch Protection Blocking Emergency Fix**: Admin override with mandatory post-incident review and documentation
6. **Pre-commit Hook Preventing Deployment**: Emergency bypass with `--no-verify`, immediate security review ticket created
7. **Vulnerability SLA Breach**: Escalate to security team lead, implement temporary mitigation (network isolation, feature flag), document in incident log
