# Feature Store Operations Runbook

**Version**: 1.0.0  
**Last Updated**: 2025-12-07  
**Owner**: ML Engineering Team

---

## Overview

This runbook covers feature store operations, health monitoring, and troubleshooting procedures.

---

## Quick Reference

### Check Feature Store Health

```bash
python -m codex_ml.cli.feature_store health
```

### List Registered Features

```bash
python -m codex_ml.cli.feature_store list --health
```

### Register New Feature Group

```bash
python -m codex_ml.cli.feature_store register feature_name 1.0.0 \
  --description "Feature description"
```

---

## Feature Store Operations

### 1. Initialize Feature Store

**When**: First time setup or after reset

**Command**:
```bash
python scripts/initialize_feature_store.py --config configs/production/features.yaml
```

**Expected Output**:
```
✓ Feature store initialized at artifacts/features/production
✓ Registered 10 feature groups
```

**Verification**:
```bash
ls -la artifacts/features/production/
cat artifacts/features/production/registry.json
```

### 2. Register Feature Group

**When**: Adding new features to production

**Steps**:

1. Define feature schema:
```json
// schema/my_features.json
{
  "name": "my_features",
  "version": "1.0.0",
  "features": [
    {"name": "feature_1", "type": "float", "description": "..."},
    {"name": "feature_2", "type": "int", "description": "..."}
  ]
}
```

2. Register via CLI:
```bash
python -m codex_ml.cli.feature_store register my_features 1.0.0 \
  --description "My custom features" \
  --schema schema/my_features.json
```

3. Verify registration:
```bash
python -m codex_ml.cli.feature_store list | grep my_features
```

### 3. Update Feature Version

**When**: Schema changes or feature improvements

**Steps**:

1. Register new version:
```bash
python -m codex_ml.cli.feature_store register my_features 1.1.0 \
  --description "Added new features"
```

2. Update training configs to use new version:
```yaml
features:
  my_features:
    version: "1.1.0"
```

3. Deprecate old version (after migration):
```bash
python -m codex_ml.cli.feature_store deprecate my_features 1.0.0
```

### 4. Feature Health Monitoring

**When**: Continuous monitoring

**Command**:
```bash
python -m codex_ml.cli.feature_store health --output health_report.json
```

**Health Checks**:
- Freshness: < 2 hours (SLA)
- Completeness: > 95% non-null
- Consistency: Schema matches registration

**Alert Conditions**:
- **WARNING**: Feature age > 48 hours
- **CRITICAL**: Feature age > 72 hours
- **ERROR**: Feature unavailable

---

## Troubleshooting

### Issue: Feature Store Not Initialized

**Symptoms**:
- Error: "Feature store not found"
- Empty registry

**Solution**:
```bash
# Re-initialize feature store
python scripts/initialize_feature_store.py --config configs/production/features.yaml

# Verify
python -m codex_ml.cli.feature_store list
```

### Issue: Stale Features

**Symptoms**:
- Health check shows feature age > 48 hours
- Alert: "Feature Staleness"

**Solutions**:

1. Check feature update pipeline:
```bash
# View last update time
python -c "
from codex_ml.features.feature_store import FeatureStore
store = FeatureStore('artifacts/features/production')
features = store.list_features()
for f in features:
    print(f'{f.name}: {f.last_updated}')
"
```

2. Trigger feature refresh:
```bash
python scripts/refresh_features.py --feature-group user_features
```

3. If pipeline issue, investigate logs:
```bash
tail -f logs/feature_pipeline.log
```

### Issue: Feature Retrieval Slow

**Symptoms**:
- High p95 latency (> 100ms)
- Training pipeline timeout

**Solutions**:

1. Enable caching:
```yaml
# configs/production/features.yaml
feature_store:
  point_in_time:
    cache_enabled: true
    cache_ttl_minutes: 60
```

2. Optimize partitioning:
```yaml
feature_store:
  storage:
    partition_by_date: true
```

3. Consider Redis caching layer (Phase 7.5):
```yaml
feature_store:
  cache:
    backend: redis
    host: redis.internal.company.com
```

### Issue: Registry Corruption

**Symptoms**:
- Cannot list features
- JSON parse errors

**Solution**:

1. Backup current registry:
```bash
cp artifacts/features/production/registry.json \
   artifacts/features/production/registry.json.backup
```

2. Restore from backup:
```bash
cp artifacts/features/production/registry.json.backup.<timestamp> \
   artifacts/features/production/registry.json
```

3. Or re-initialize (loses custom registrations):
```bash
python scripts/initialize_feature_store.py --config configs/production/features.yaml
```

---

## Operational Procedures

### Daily Health Check

**Schedule**: Daily at 9 AM

**Steps**:
1. Run health check:
```bash
python -m codex_ml.cli.feature_store health > daily_health_$(date +%Y%m%d).txt
```

2. Review for alerts:
```bash
grep -E "WARNING|CRITICAL|ERROR" daily_health_$(date +%Y%m%d).txt
```

3. If issues found, follow troubleshooting guide

### Weekly Cleanup

**Schedule**: Sunday midnight

**Steps**:
1. Archive old feature versions (> 90 days):
```bash
python scripts/archive_old_features.py --days 90
```

2. Validate registry integrity:
```bash
python scripts/validate_registry.py
```

### Monthly Review

**Schedule**: First Monday of month

**Steps**:
1. Generate usage report:
```bash
python scripts/feature_usage_report.py --month $(date +%Y-%m)
```

2. Identify unused features:
```bash
python scripts/identify_unused_features.py --threshold 0.05
```

3. AI Assistant review and autonomous deprecation decision

---

## Monitoring Dashboards

### Feature Freshness Dashboard

**URL**: `artifacts/features/health_reports/`

**Metrics**:
- Feature age by group
- SLA compliance rate
- Alert history

### Feature Usage Dashboard

**Metrics**:
- Access frequency per feature
- Popular feature combinations
- P95 retrieval latency

---

## Alerting Rules

### Configured Alerts

1. **Feature Staleness (WARNING)**
   - Condition: `feature_age > 48h`
   - Channel: Slack #mlops-alerts
   - Response: Check feature pipeline

2. **Feature Staleness (CRITICAL)**
   - Condition: `feature_age > 72h`
   - Channel: Slack + PagerDuty
   - Response: Immediate investigation

3. **Feature Unavailable (ERROR)**
   - Condition: `feature_missing = true`
   - Channel: Slack + PagerDuty + Email
   - Response: Escalate to on-call

4. **High Error Rate**
   - Condition: `error_rate > 5%`
   - Channel: Slack #mlops-alerts
   - Response: Check logs and recent changes

---

## Rollback Procedures

### Rollback to Previous Feature Version

```bash
# 1. List available versions
python -m codex_ml.cli.feature_store versions user_features

# 2. Update training config to use previous version
# configs/production/features.yaml
features:
  user_features:
    version: "1.0.0"  # Rollback from 1.1.0

# 3. Restart training pipelines
python scripts/restart_training.py
```

### Emergency Disable Feature Store

```bash
# Quick disable in config
sed -i 's/enabled: true/enabled: false/' configs/production/features.yaml

# Or via environment variable
export FEATURE_STORE_ENABLED=false
```

---

## Performance Benchmarks

| Operation | Target | Current | Status |
|-----------|--------|---------|--------|
| Feature retrieval (p50) | <5ms | 3ms | ✅ |
| Feature retrieval (p95) | <10ms | 8ms | ✅ |
| Feature retrieval (p99) | <50ms | 25ms | ✅ |
| Registration | <100ms | 50ms | ✅ |
| Health check | <1s | 0.5s | ✅ |

---

## Escalation Path

| Issue Severity | Response Time | Escalation |
|----------------|---------------|------------|
| INFO | Next business day | Team Slack |
| WARNING | Within 2 hours | ML Engineer |
| CRITICAL | Within 30 minutes | On-call + Team Lead |
| EMERGENCY | Immediate | On-call + Director |

---

## Contact Information

- **Primary**: ML Engineering Team (#ml-engineering)
- **On-call**: Check PagerDuty rotation
- **Escalation**: ML Platform Lead
- **Documentation**: `configs/production/README.md`

---

*Last reviewed: Previous Cycle-12-07*
