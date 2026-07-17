# Upgrade Guide
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Version:** 0.1.0
**Last Updated: 2026-07-09
**Audience:** DevOps, Platform Engineers, Developers

---

## Migration Paths

### From beta1 0.1.0 (Final)

#### Breaking Changes

```python
# OLD API (beta1)
from codex.ml.v1 import inference
results = inference(texts)

# NEW API (0.1.0)
from codex.ml import InferencePipeline
pipeline = InferencePipeline("bert-base")
results = pipeline(texts, batch_size=32)
```

#### Configuration Changes

```python
# OLD: Dict-based config
cfg = {
    "model": "bert-base",
    "batch_size": 32,
    "device": "cuda"
}
pipeline = Pipeline(cfg)

# NEW: Hydra YAML config
from codex.core import Hydra
cfg = Hydra.load_config("inference.yaml")
pipeline = Pipeline(cfg)
```

#### Migration Steps

1. Update imports in all files
2. Convert configuration files to YAML
3. Test with new API
4. Update documentation
5. Deploy gradually (canary rollout)

---

### From beta2 0.1.0 (Final)

#### Configuration Format

```yaml
# OLD: inference.yaml (beta2)
model: bert-base
batch_size: 16
# Missing: cache configuration

# NEW: inference.yaml (0.1.0)
model: bert-base
batch_size: 32
cache:
  enabled: true
  ttl_seconds: 3600
  layers: [http, model, data, compute]
```

#### New Features

- Multi-layer caching (HTTP, model, data, compute)
- Automatic batch sizing
- Graceful degradation
- Enhanced monitoring

#### Steps

1. Update configuration files
2. Test caching layer
3. Performance baseline
4. Gradual rollout

---

### From beta3 0.1.0 (Final)

#### Minor API Changes

```python
# OLD: beta3
from codex.ml import inference_v2
results = inference_v2(texts)

# NEW: 0.1.0 (compatible with minimal changes)
from codex.ml import InferencePipeline
pipeline = InferencePipeline("bert-base")
results = pipeline(texts)
```

#### Dependency Updates

- PyTorch: >=2.0.0
- Transformers: >=4.35.0
- Hydra: >=1.3.2

#### Upgrade Procedure

1. Backup current deployment
2. Update dependencies
3. Run tests
4. Deploy to staging
5. Verify functionality
6. Deploy to production

---

## Upgrade Strategies

### 1. In-Place Upgrade

**Best for:** Single-machine deployments, small installations

```bash
# Backup
cp -r /app/codex /app/codex.backup

# Stop service
systemctl stop codex-api

# Upgrade package
pip install --upgrade codex-ml==0.1.0

# Run migrations
python -m codex.cli migrate --from-version=beta3

# Start service
systemctl start codex-api

# Verify
curl http://localhost:8000/health
```

### 2. Blue-Green Deployment

**Best for:** Zero-downtime requirements, Kubernetes

```bash
# Deploy new version (green)
kubectl apply -f k8s/deployment-0.1.0.yaml -n codex

# Verify green environment
kubectl get pods -n codex
kubectl exec <green-pod> -- curl http://localhost:8000/health

# Switch traffic (blue → green)
kubectl patch service codex-api -n codex -p \
  '{"spec":{"selector":{"version":"0.1.0"}}}'

# Verify traffic
curl http://codex-api/health

# Delete old version (blue)
kubectl delete deployment codex-api-beta3 -n codex
```

### 3. Canary Rollout

**Best for:** Large deployments, critical services

```bash
# Deploy 10% traffic to new version
kubectl patch deployment codex-api -n codex --type merge \
  -p '{"spec":{"selector":{"version":"canary"}}}'

# Monitor metrics for 30 minutes
kubectl get pods -n codex

# Increase to 50% if stable
kubectl patch deployment codex-api -n codex --type merge \
  -p '{"spec":{"selector":{"version":"canary-50"}}}'

# Full rollout if metrics good
kubectl patch deployment codex-api -n codex --type merge \
  -p '{"spec":{"selector":{"version":"0.1.0"}}}'
```

---

## Testing Before Upgrade

### Pre-Upgrade Checklist

```bash
# 1. Run full test suite
pytest tests/ -v --cov=src/codex

# 2. Check API compatibility
python scripts/check_api_compatibility.py

# 3. Test database migrations (if applicable)
python -m codex.cli migrate --dry-run

# 4. Verify performance
python scripts/benchmark.py --baseline

# 5. Smoke tests
python tests/smoke_tests.py

# 6. Integration tests
python tests/integration_tests.py
```

### Staging Environment

```bash
# Deploy to staging first
docker-compose -f docker/docker-compose-staging.yml up -d

# Run full test suite
pytest tests/integration/ -v

# Load test
apache2-utils: ab -c 100 -n 10000 http://localhost:9000/health

# Verify logs
docker-compose logs api | grep -i error
```

---

## Rollback Procedure

If issues occur during upgrade:

### Immediate Rollback

```bash
# Kubernetes
kubectl rollout undo deployment/codex-api -n codex

# Docker Compose
docker-compose -f docker/docker-compose.yml down
docker-compose -f docker/docker-compose-backup.yml up -d

# Direct deployment
pip install codex-ml==0.1.0-beta3
systemctl restart codex-api
```

### Verification After Rollback

```bash
# Check version
python -c "import codex; print(codex.__version__)"

# Verify health
curl http://localhost:8000/health

# Check logs for errors
journalctl -u codex-api -n 50
```

---

## Migration Guide by Component

### Database (If Applicable)

```bash
# Backup
pg_dump codex_db > backup_$(date +%s).sql

# Run migrations
python -m codex.cli migrate --from-version=beta3 --to-version=0.1.0

# Verify
psql codex_db -c "\d"  # Check schema
```

### Configuration Files

```bash
# Convert old format to new
python scripts/convert_config.py \
  --input configs/old/inference.yaml \
  --output configs/new/inference.yaml

# Validate new config
python -m codex.cli validate-config configs/new/inference.yaml
```

### Docker Images

```bash
# Build new images
docker build -f docker/Dockerfile \
  -t aries-serpent-api:0.1.0 .

# Push to registry
docker push aries-serpent-api:0.1.0

# Update K8s manifests
kubectl set image deployment/codex-api \
  api=aries-serpent-api:0.1.0 -n codex
```

---

## Troubleshooting Upgrade Issues

### Issue: Incompatible Configuration

```bash
# Validate config against schema
python -m codex.cli validate-config --version 0.1.0

# Show differences
diff -u old_config.yaml new_config.yaml

# Auto-convert (if available)
python scripts/auto_migrate_config.py old_config.yaml
```

### Issue: Database Migration Fails

```bash
# Check migration status
python -m codex.cli migrate --status

# Rollback migration
python -m codex.cli migrate --rollback

# Check logs
cat logs/migration.log
```

### Issue: API Incompatibility

```bash
# Check API changes
python scripts/check_api_breaking_changes.py

# Run compatibility tests
pytest tests/compatibility/ -v

# Update code
# ...manual updates required...
```

---

## Success Criteria

Upgrade is successful when:

- All tests passing
- Zero downtime (for rolling upgrades)
- Performance baseline met
- No error spikes
- All features working
- Health checks passing
- Monitoring stable

---

**Last Updated: 2026-07-09
**Support:** [GitHub Issues](https://github.com/Aries-Serpent/_codex_/issues)
