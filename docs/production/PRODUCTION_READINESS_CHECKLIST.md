# Production Readiness Checklist

> **Version:** 1.0.0  
> **Created:** 2026-01-22  
> **Status:** Phase 9.0 Documentation  
> **Owner:** Cognitive Brain Team

---

## 🎯 Overview

This checklist ensures the `_codex_` repository meets production deployment standards. Complete all items before deploying to production environments.

---

## 📋 Pre-Deployment Checklist

### 1. Code Quality Gates ✅

- [ ] All tests passing (`nox -s tests` or `pytest tests/`)
- [ ] Test coverage ≥ 70% (`pytest --cov`)
- [ ] No critical linting errors (`ruff check src/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] Security scan clean (`bandit -r src/`)

### 2. CI/CD Pipeline ✅

- [ ] All GitHub Actions workflows passing
- [ ] `rust_tests` job: Green
- [ ] `code_coverage` job: Green
- [ ] `python_integration` job: Green
- [ ] `status_check` job: Green
- [ ] Pre-commit hooks configured and passing

### 3. Documentation ✅

- [ ] README.md up to date
- [ ] API documentation current
- [ ] Troubleshooting guides available
- [ ] CHANGELOG.md updated
- [ ] Architecture docs reflect current state

### 4. Security ✅

- [ ] No hardcoded secrets in code
- [ ] All secrets stored in GitHub Secrets
- [ ] Dependencies scanned for vulnerabilities
- [ ] CODEX_MASTER_KEY properly secured
- [ ] Token rotation plan in place

### 5. Monitoring & Observability ✅

- [ ] Logging configured (structured JSON)
- [ ] Error tracking enabled
- [ ] Performance metrics collected
- [ ] Health check endpoints available
- [ ] Alerting rules defined

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description | Default |
|----------|----------|-------------|---------|
| `CODEX_ENV` | Yes | Environment (dev/staging/prod) | `dev` |
| `CODEX_LOG_LEVEL` | No | Logging level | `INFO` |
| `CODEX_SESSION_ID` | No | Session identifier | Auto-generated |
| `CODEX_DB_PATH` | No | SQLite database path | `.codex/codex.db` |
| `CODEX_MASTER_KEY` | Yes | Master encryption key | - |

### Feature Flags

| Flag | Default | Description |
|------|---------|-------------|
| `SAFE_MODE` | `true` | Disable autonomous actions |
| `ENABLE_ANALYTICS` | `false` | Enable usage analytics |
| `DEBUG_MODE` | `false` | Verbose debug output |

---

## 🚀 Deployment Steps

### 1. Pre-Deployment

```bash
# Verify all tests pass
nox -s tests

# Check coverage threshold
pytest --cov=src --cov-fail-under=70

# Security scan
bandit -r src/ -ll

# Build documentation
mkdocs build --strict
```

## 2. Deployment

```bash
# Tag release
git tag -a v1.x.x -m "Release v1.x.x"
git push origin v1.x.x

# Deploy (via CI/CD)
# Triggered automatically on tag push
```

## 3. Post-Deployment

```bash
# Verify deployment
curl https://api.example.com/health

# Monitor logs
tail -f /var/log/codex/app.log

# Check metrics
# Dashboard: https://metrics.example.com/codex
```

---

## 📊 Performance Baselines

### Response Time Targets

| Operation | Target | Max |
|-----------|--------|-----|
| Health check | < 50ms | 200ms |
| API request | < 500ms | 2s |
| Batch processing | < 5s | 30s |

### Resource Limits

| Resource | Soft Limit | Hard Limit |
|----------|------------|------------|
| Memory | 512MB | 1GB |
| CPU | 50% | 100% |
| Connections | 100 | 500 |

---

## 🔄 Rollback Plan

### Automatic Rollback Triggers

1. Health check failures > 3 consecutive
2. Error rate > 5% over 5 minutes
3. Response time > 10s average

### Manual Rollback Steps

```bash
# Revert to previous version
git checkout v1.x.x-1

# Deploy previous version
./deploy.sh --version v1.x.x-1

# Verify rollback
curl https://api.example.com/version
```

---

## 📞 Escalation Contacts

| Role | Contact | Escalation Time |
|------|---------|-----------------|
| On-call | @on-call | Immediate |
| Team Lead | @mbaetiong | 15 minutes |
| Security | @security-team | Critical only |

---

## 📈 Success Metrics

### Phase 9.0 Goals

| Metric | Target | Current | Notes |
|--------|--------|---------|-------|
| Test Coverage | 70% | ~30% | Increased from 27.5% with new tests |
| CI Pass Rate | 99% | ~95% | Improving with CI fixes |
| Deploy Frequency | Daily | Weekly | Target for Phase 9.0 |
| MTTR | < 1 hour | - | To be measured |

**Note:** Repository-wide coverage is ~30% (target: 70%). Individual module coverage varies:
- `codex_harness`: ~90% (recently improved from 0%)
- `cognitive_brain`: ~85%
- See `.codex/qa_walkthrough/coverage_analysis.json` for full breakdown.

---

## 🧠 Cognitive Brain Integration

### PDA Loop Status

- **PLAN**: Production deployment planning complete
- **DO**: Deployment execution via CI/CD
- **ASSESS**: Monitor metrics and logs

### AfterMath Tracking

All production incidents are tracked in:
- `.codex/aftermath/` - Incident reports
- `.codex/change_log.md` - Change history

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-22 | Initial checklist creation |

---

**This checklist is mandatory for all production deployments.**
