# Deployment Runbook
**Last Updated:** 2026-07-11
**Version:** v0.2.0

**Version:** 1.0.0  
**Created:** 2026-01-18  
**Phase:** 18.3 - Deployment Automation  
**Status:**  Production Ready

---

## Overview

This runbook documents the deployment process for the Codex platform, including pre-deployment checks, deployment steps, and rollback procedures.

---

## Pre-Deployment Checklist

### 1. Code Quality Gates

- [ ] All tests pass (40500+ tests)
- [ ] Coverage threshold met (75%)
- [ ] CodeQL security scan passes
- [ ] Ruff linting passes
- [ ] Type checking passes (mypy)

### 2. Documentation Check

- [ ] README.md updated
- [ ] CHANGELOG.md updated
- [ ] API documentation current
- [ ] Architecture diagrams updated

### 3. Dependency Check

- [ ] pip-audit passes (no critical vulnerabilities)
- [ ] Dependencies pinned in requirements.txt
- [ ] Lockfile up to date

### 4. Environment Verification

- [ ] Staging environment functional
- [ ] Secrets properly configured
- [ ] Environment variables documented

---

## Deployment Steps

### Step 1: Version Bump

```bash
# Update version in pyproject.toml
sed -i 's/version = ".*"/version = "X.Y.Z"/' pyproject.toml

# Commit version bump
git commit -am "chore: bump version to X.Y.Z"
```

## Step 2: Create Release Tag

```bash
# Create annotated tag
git tag -a vX.Y.Z -m "Release vX.Y.Z: Phase 14-18 Test Coverage Complete"

# Push tag
git push origin vX.Y.Z
```

## Step 3: Build Release Artifacts

```bash
# Clean build
rm -rf dist/ build/

# Build wheel and source distribution
python -m build

# Verify build
ls -la dist/
```

## Step 4: Upload to Package Registry

```bash
# Upload to PyPI (production)
python -m twine upload dist/*

# Or upload to private registry
python -m twine upload --repository-url https://your-registry/simple/ dist/*
```

## Step 5: Deploy to Production

```bash
# Pull latest changes
git pull origin main

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if applicable)
python -m codex.cli migrate

# Restart services
systemctl restart codex-api
systemctl restart codex-worker
```

---

## Rollback Procedures

### Quick Rollback

```bash
# Revert to previous version
pip install codex==PREVIOUS_VERSION

# Or from git
git checkout vPREVIOUS_TAG
pip install -e .
```

## Database Rollback

```bash
# Rollback migrations
python -m codex.cli migrate --rollback 1
```

## Service Recovery

```bash
# Check service status
systemctl status codex-api codex-worker

# Restart services
systemctl restart codex-api
systemctl restart codex-worker

# Check logs
journalctl -u codex-api -f
```

---

## Health Checks

### API Health Check

```bash
```

Expected response:
```json
{
  "status": "healthy",
  "version": "X.Y.Z",
  "database": "connected",
  "cache": "connected"
}
```

### Worker Health Check

```bash
celery -A codex.tasks inspect ping
```

### Metrics Check

```bash
```

---

## Monitoring & Alerts

### Key Metrics

| Metric | Threshold | Action |
|--------|-----------|--------|
| API Response Time | >1s p99 | Scale up |
| Error Rate | >1% | Investigate |
| CPU Usage | >80% | Scale out |
| Memory Usage | >90% | Optimize |
| Disk Space | >85% | Clean up |

### Alert Channels

- PagerDuty: Critical alerts
- Slack #alerts: Warning alerts
- Email: Daily digest

---

## Blue-Green Deployment

### Setup

1. Maintain two identical environments (blue/green)
2. Route traffic to active environment
3. Deploy to inactive environment
4. Switch traffic after validation

### Switching Traffic

```bash
# Update load balancer
./scripts/switch-traffic.sh blue|green

# Verify traffic routing
curl -H "Host: api.codex.io" http://LOAD_BALANCER_IP/health
```

---

## Emergency Contacts

| Role | Contact | Availability |
|------|---------|--------------|
| On-Call Engineer | @oncall | 24/7 |
| Tech Lead | @techlead | Business hours |
| Security Team | @security | 24/7 for critical |

---

## Post-Deployment Tasks

1. [ ] Verify all health checks pass
2. [ ] Run smoke tests
3. [ ] Check error logs for new issues
4. [ ] Update status page
5. [ ] Notify stakeholders

---

**Owner:** Platform Engineering  
**Review Cadence:** Quarterly  
**Last Updated: 2026-07-11
