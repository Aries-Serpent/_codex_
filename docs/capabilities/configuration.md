# Configuration Guide

**Generated**: 2025-12-28 | **Author**: mbaetiong

## Overview

CODEX uses a hierarchical configuration system supporting multiple environments (development, staging, production) with secure secret management.

---

## Configuration Files

### Primary Config: `config/config.yaml`

```yaml
# Environment-specific settings
environment: ${ENV:-development}

# Model configuration
model:
  registry_uri: ${MLFLOW_TRACKING_URI}
  artifact_location: ${ARTIFACT_STORE}
  default_model: "codex-classifier-v2"

# Feature engineering
features:
  enable_cache: true
  cache_ttl_seconds: 3600

# Inference
inference:
  batch_size: 32
  timeout_seconds: 30
  max_retries: 3

# Monitoring
monitoring:
  enable_prometheus: true
  metrics_port: 9090
  log_level: ${LOG_LEVEL:-INFO}
```

### Environment Variables (`.env`)

```bash
# Core settings
ENV=production
LOG_LEVEL=INFO

# MLflow
MLFLOW_TRACKING_URI=https://mlflow.codex.ai
MLFLOW_EXPERIMENT_NAME=codex-experiments

# AWS credentials (use Secrets Manager in production)
AWS_ACCESS_KEY_ID=<from-secrets-manager>
AWS_SECRET_ACCESS_KEY=<from-secrets-manager>

# Database
DATABASE_URL=postgresql://user:pass@host:5432/codex
```

---

## Configuration Priority (Highest to Lowest)

1. **Environment Variables**: `export KEY=value`
2. **`.env` file**: Local development overrides
3. **`config/config.yaml`**: Default settings
4. **Secrets Manager**: Production secrets (AWS Secrets Manager, GitHub Secrets)

---

## Secrets Management

### Development
- Use `.env` file (never commit to Git, add to `.gitignore`)

### Production
- **GitHub Actions**: Use `${{ secrets.SECRET_NAME }}`
- **AWS**: Use Secrets Manager with IAM role-based access
- **Kubernetes**: Use Sealed Secrets or External Secrets Operator

**Example (GitHub Actions)**:
```yaml
- name: Deploy model
  env:
    MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_URI }}
    AWS_ACCESS_KEY_ID: ${{ secrets.AWS_KEY }}
  run: python deploy.py
```

---

## Loading Configuration in Code

```python
from codex_ml.config import load_config

# Load configuration (auto-detects environment)
config = load_config()

# Access settings
model_name = config.model.default_model
batch_size = config.inference.batch_size

# Override specific settings
config.override("inference.timeout_seconds", 60)
```

---

## See Also

- [Environment Setup](../setup/environment.md)
- [Secrets Management](../security/secrets.md)
- [Deployment Guide](../deployment/deploy_pipeline.md)
