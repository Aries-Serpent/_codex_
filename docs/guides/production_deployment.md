# Production Deployment Guide

> **Version**: 1.0 (Phase 7D)  
> **Status**: ✅ Complete and production-ready  
> **Last Updated**: 2026-06-22T09:30:00Z  
> **Authority**: @mbaetiong

---

## Overview

This guide provides comprehensive procedures for deploying the _codex_ system to production environments. It covers infrastructure setup, containerization, orchestration, monitoring, and disaster recovery.

**Key Capabilities**:
- ✅ Multi-cloud deployment (AWS, Azure, GCP)
- ✅ Kubernetes orchestration with Helm charts
- ✅ Zero-downtime deployments (blue-green, canary)
- ✅ Automatic health checks and monitoring
- ✅ Disaster recovery and rollback procedures
- ✅ Security compliance and secrets management

---

## Table of Contents

1. [Infrastructure Requirements](#infrastructure-requirements)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Deployment Strategies](#deployment-strategies)
4. [Container Deployment](#container-deployment)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Configuration Management](#configuration-management)
7. [Monitoring and Observability](#monitoring-and-observability)
8. [Scaling Guidelines](#scaling-guidelines)
9. [Disaster Recovery](#disaster-recovery)
10. [Troubleshooting](#troubleshooting)

---

## Infrastructure Requirements

### Minimum Hardware Requirements

| Component | CPU | Memory | Storage | Network |
|-----------|-----|--------|---------|---------|
| **Single Node** | 4 cores | 16 GB | 100 GB | 100 Mbps |
| **HA Cluster (3 nodes)** | 12+ cores | 48+ GB | 300+ GB | 1 Gbps |
| **Production (5+ nodes)** | 20+ cores | 64+ GB | 500+ GB | 10 Gbps |

### Software Prerequisites

```bash
# Python 3.9+
python --version

# Docker 20.10+
docker --version

# Kubernetes 1.24+ (for K8s deployments)
kubectl version

# Helm 3.10+ (for Helm deployments)
helm version

# PostgreSQL 13+ or MySQL 8.0+ (if needed)
psql --version
```

## Network Configuration

- **Inbound**: HTTP (80), HTTPS (443), Admin (8000-9000)
- **Outbound**: API access to GitHub, AWS/Azure/GCP APIs, PyPI
- **DNS**: Internal service discovery, external API endpoints
- **Firewall**: Security group rules, network policies

---

## Pre-Deployment Checklist

Before deploying to production, verify:

- [ ] **Code Review**: All changes reviewed and approved
- [ ] **Tests Passing**: Full test suite runs green
- [ ] **Security Scan**: CodeQL, SAST, dependency scans passed
- [ ] **Documentation**: Updated and accurate
- [ ] **Secrets**: No secrets in codebase (verified via scanning)
- [ ] **Configuration**: Environment variables validated
- [ ] **Backups**: Verified backup strategy in place
- [ ] **Monitoring**: Alerting rules configured
- [ ] **Rollback Plan**: Documented and tested
- [ ] **Stakeholder Sign-off**: Approval from owners

---

## Deployment Strategies

### 1. Blue-Green Deployment (Recommended)

Zero-downtime deployment using parallel environments:

```bash
# Current production (Blue environment)
kubectl get deployment codex-blue

# New deployment (Green environment)
kubectl apply -f k8s/green-deployment.yaml

# Run smoke tests
./scripts/smoke_test.sh https://codex-green.internal

# Switch traffic (via load balancer)
kubectl patch service codex -p \
  '{"spec":{"selector":{"app":"codex-green"}}}'

# Keep Blue for quick rollback
kubectl delete deployment codex-blue  # Only after 24h validation
```

**Advantages**: Zero downtime, quick rollback, safe testing  
**Duration**: ~5-10 minutes  
**Risk**: LOW

## 2. Canary Deployment

Gradual rollout with monitoring:

```bash
# Deploy 10% of traffic to new version
kubectl set image deployment/codex \
  codex=codex:v2.0.0 \
  --record \
  --max-surge=1 \
  --max-unavailable=0

# Monitor metrics (error rate, latency, CPU)
watch kubectl top pod -l app=codex

# Gradually increase (if metrics look good)
kubectl rollout resume deployment/codex

# Rollback if issues detected
kubectl rollout undo deployment/codex
```

**Advantages**: Safety, gradual validation, quick rollback  
**Duration**: 30-120 minutes  
**Risk**: MEDIUM

## 3. Rolling Update

Progressive replacement ensuring service availability:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 1 extra pod during update
      maxUnavailable: 1  # 1 pod can be unavailable
  selector:
    matchLabels:
      app: codex
  template:
    metadata:
      labels:
        app: codex
    spec:
      containers:
      - name: codex
        image: codex:v2.0.0
```

**Advantages**: Gradual, automatic, built-in  
**Duration**: 10-30 minutes (5 replicas)  
**Risk**: MEDIUM-HIGH

---

## Container Deployment

### Building Container Images

#### Docker Build (CPU-Only)

```bash
# Build image
docker build -f docker/Dockerfile.cpu -t codex-cpu:latest .

# Run smoke test
docker run --rm \
  -v "$PWD":/app \
  -w /app \
  codex-cpu:latest \
  pytest -q -k "determinism or ast_cli_schema"

# Tag for registry
docker tag codex-cpu:latest gcr.io/my-project/codex:v2.0.0

# Push to registry
docker push gcr.io/my-project/codex:v2.0.0
```

## Docker Best Practices

```dockerfile
# Use minimal base image
FROM python:3.11-slim

# Non-root user
RUN useradd -m -u 1000 codex
USER codex

# Multi-stage build for size optimization
FROM python:3.11-slim as builder
RUN pip install --user --no-cache-dir -r requirements.txt

FROM python:3.11-slim
COPY --from=builder /root/.local /home/codex/.local
```

## Running Containers

```bash
# Basic run
docker run -d \
  --name codex-prod \
  -p 8000:8000 \
  -e ENVIRONMENT=production \
  -e LOG_LEVEL=INFO \
  gcr.io/my-project/codex:v2.0.0

# With resource limits
docker run -d \
  --name codex-prod \
  --memory=4g \
  --cpus=2 \
  --log-driver json-file \
  --log-opt max-size=10m \
  --log-opt max-file=3 \
  -e ENVIRONMENT=production \
  gcr.io/my-project/codex:v2.0.0

# Health check
docker run -d \
  --health-cmd='curl --fail http://localhost:8000/health || exit 1' \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  gcr.io/my-project/codex:v2.0.0
```

---

## Kubernetes Deployment

### Prerequisites

```bash
# Install Kubernetes cluster (minikube, EKS, AKS, GKE)
# Minimum version: 1.24+

# Verify cluster
kubectl cluster-info
kubectl get nodes

# Install Helm 3+
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Helm Chart Deployment

```bash
# Add chart repository
helm repo add codex-charts https://charts.example.com
helm repo update

# Install release
helm install codex codex-charts/codex \
  --namespace production \
  --create-namespace \
  --values values-production.yaml \
  --version 2.0.0

# Verify deployment
kubectl get pods -n production
kubectl get service codex -n production

# Check status
helm status codex -n production

# Upgrade to new version
helm upgrade codex codex-charts/codex \
  --namespace production \
  --values values-production.yaml \
  --version 2.1.0 \
  --wait

# Rollback if needed
helm rollback codex 1 -n production
```

## Manual Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex
  namespace: production
  labels:
    app: codex
    version: v2.0.0
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codex
  template:
    metadata:
      labels:
        app: codex
        version: v2.0.0
    spec:
      containers:
      - name: codex
        image: gcr.io/my-project/codex:v2.0.0
        ports:
        - containerPort: 8000
          name: http
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
        env:
        - name: ENVIRONMENT
          value: "production"
        - name: LOG_LEVEL
          value: "INFO"
        - name: CODEX_SESSION_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
---
apiVersion: v1
kind: Service
metadata:
  name: codex
  namespace: production
spec:
  selector:
    app: codex
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
    protocol: TCP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: codex-hpa
  namespace: production
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codex
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

---

## Configuration Management

### Environment Variables (Production)

```bash
# Deployment configuration
export ENVIRONMENT=production
export LOG_LEVEL=INFO
export DEBUG=false

# API configuration
export API_HOST=0.0.0.0
export API_PORT=8000
export API_WORKERS=4

# Session and database
export CODEX_SESSION_DIR=/data/sessions
export CODEX_LOG_DB_PATH=/data/logs.db

# Performance tuning
export CODEX_BATCH_SIZE=32
export CODEX_MAX_MEMORY_MB=4096
export CODEX_FORCE_CPU=0

# Security
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export GITHUB_TOKEN=<from-secrets-manager>
```

### Authentication & Credentials (Production - REQUIRED)

This section provides step-by-step instructions for setting up authentication environment variables in your deployment environment.

#### 1. Authentication Secret Key Setup

The application requires a secret key for JWT token signing and session encryption. Choose **ONE** of these options:

**Option A: Using AUTH_SECRET_KEY (Recommended)**

```bash
# Generate a cryptographically secure random key
export AUTH_SECRET_KEY=$(openssl rand -hex 32)

# Verify it was set
echo "✅ AUTH_SECRET_KEY is set: ${#AUTH_SECRET_KEY} characters"

# In your deployment environment (Docker, Kubernetes, etc.):
# Add to .env file, secrets manager, or environment variables
AUTH_SECRET_KEY="<your-hex-generated-key>"
```

**Option B: Using CODEX_AUTH_SECRET_KEY (Alternative)**

```bash
# If you prefer the CODEX-prefixed naming convention:
export CODEX_AUTH_SECRET_KEY=$(openssl rand -hex 32)

# The application accepts either AUTH_SECRET_KEY or CODEX_AUTH_SECRET_KEY
# Precedence: AUTH_SECRET_KEY is checked first, then falls back to CODEX_AUTH_SECRET_KEY
```

**Deployment Methods:**

| Method | Command | Example |
|--------|---------|---------|
| **Docker** | `docker run -e AUTH_SECRET_KEY=...` | `docker run -e AUTH_SECRET_KEY=$(openssl rand -hex 32) codex:latest` |
| **Docker Compose** | Add to `.env` or `docker-compose.yml` | `AUTH_SECRET_KEY: "${AUTH_SECRET_KEY}"` |
| **Kubernetes** | Create Secret resource | `kubectl create secret generic codex-auth --from-literal=AUTH_SECRET_KEY=...` |
| **Kubernetes Helm** | values.yaml | `authSecretKey: "<your-key>"` |
| **Environment File** | `.env` or `/etc/codex/.env` | `AUTH_SECRET_KEY=<your-key>` |
| **Shell Export** | `export AUTH_SECRET_KEY=...` | `source .env && export AUTH_SECRET_KEY` |

#### 2. GitHub App OAuth Client Secret

If using GitHub App OAuth for authentication:

```bash
# Step 1: Obtain from GitHub App Settings
# Navigate to: GitHub Settings → Developer settings → OAuth Apps → Your App
# Copy the "Client Secret" value

export GITHUB_APP_CLIENT_SECRET="<your-github-app-client-secret>"

# Step 2: Verify in deployment (DO NOT log the actual value)
if [ -z "$GITHUB_APP_CLIENT_SECRET" ]; then
    echo "❌ ERROR: GITHUB_APP_CLIENT_SECRET not set!"
    exit 1
else
    echo "✅ GITHUB_APP_CLIENT_SECRET is set (length: ${#GITHUB_APP_CLIENT_SECRET})"
fi

# Step 3: Configure in deployment environment
# Add to secrets manager, environment file, or orchestration system
```

**Deployment Steps for GitHub App OAuth:**

1. **Generate GitHub App Client Secret:**
   - Go to https://github.com/settings/developers
   - Click on your OAuth App
   - In "Client Secret" section, click "Generate a new client secret"
   - Copy the newly generated secret immediately (it only displays once)

2. **Set in Deployment Environment:**
   ```bash
   # For Docker containers
   docker run -e GITHUB_APP_CLIENT_SECRET="<secret>" codex:latest
   
   # For Kubernetes with Secrets
   kubectl create secret generic github-oauth \
     --from-literal=GITHUB_APP_CLIENT_SECRET="<secret>"
   kubectl set env deployment/codex \
     --from=secret/github-oauth
   
   # For systemd service
   # Add to /etc/systemd/system/codex.service:
   # Environment="GITHUB_APP_CLIENT_SECRET=<secret>"
   ```

3. **Verify Configuration:**
   ```bash
   # Test authentication endpoint
   curl -X POST http://localhost:8000/auth/github/callback \
     -H "Content-Type: application/json" \
     -d '{"code": "test", "state": "test"}'
   
   # Should return 400 Bad Request (invalid code), NOT 500 Server Error
   # A 500 error indicates GITHUB_APP_CLIENT_SECRET is not set properly
   ```

#### 3. Additional Service Credentials

For services requiring authentication:

| Service | Environment Variable | How to Obtain |
|---------|----------------------|---------------|
| **Slack Webhooks** | `SLACK_WEBHOOK_URL` | Create in Slack App settings → Incoming Webhooks |
| **AWS Credentials** | `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` | AWS IAM → Create Access Keys → Download CSV |
| **Azure Credentials** | `AZURE_SUBSCRIPTION_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` | Azure Portal → App Registrations → Certificates & Secrets |
| **GCP Credentials** | `GOOGLE_APPLICATION_CREDENTIALS` | GCP Console → Service Accounts → Create Key (JSON) |
| **API Keys** | Service-specific | Provider's developer console |

**Example Multi-Service Setup:**

```bash
# Docker Compose (.env file)
AUTH_SECRET_KEY=<generated-hex-key>
GITHUB_APP_CLIENT_SECRET=<github-secret>
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
AWS_ACCESS_KEY_ID=<aws-key-id>
AWS_SECRET_ACCESS_KEY=<aws-secret>
AZURE_SUBSCRIPTION_ID=<subscription-id>
```

#### 4. Secrets Management Best Practices

| Practice | Method | Command |
|----------|--------|---------|
| **Generate Secure Secrets** | OpenSSL | `openssl rand -hex 32` (32 bytes = 256 bits) |
| **Store in Vault** | HashiCorp Vault | `vault kv put secret/codex AUTH_SECRET_KEY=...` |
| **Store in Cloud** | AWS Secrets Manager | `aws secretsmanager create-secret --name codex/auth ...` |
| **Store in K8s** | Kubernetes Secrets | `kubectl create secret generic codex-auth ...` |
| **Encrypt at Rest** | etcd (K8s) | Enable encryption: `--encryption-provider-config` |
| **Rotate Periodically** | Scheduled | Every 90 days minimum |
| **Audit Access** | Enable logging | CloudTrail, Vault audit logs, K8s audit logs |
| **Never Log** | Code review | Grep for `AUTH_SECRET_KEY` in logs to verify |

#### 5. Deployment Verification Checklist

Before deploying to production, verify:

- [ ] **AUTH_SECRET_KEY is set:**
  ```bash
  if [ -z "$AUTH_SECRET_KEY" ]; then echo "❌ NOT SET"; else echo "✅ SET"; fi
  ```

- [ ] **GITHUB_APP_CLIENT_SECRET is set** (if using GitHub OAuth):
  ```bash
  if [ -z "$GITHUB_APP_CLIENT_SECRET" ]; then echo "❌ NOT SET"; else echo "✅ SET"; fi
  ```

- [ ] **All service credentials are set:**
  ```bash
  # Check all required environment variables
  for var in AUTH_SECRET_KEY GITHUB_APP_CLIENT_SECRET SLACK_WEBHOOK_URL; do
    if [ -z "$(eval echo \$$var)" ]; then
      echo "❌ $var is NOT SET"
    else
      echo "✅ $var is set (length: ${#var})"
    fi
  done
  ```

- [ ] **Secrets are NOT committed to git:**
  ```bash
  git log -p | grep -i "AUTH_SECRET_KEY\|GITHUB_APP_CLIENT_SECRET" || echo "✅ No secrets in git history"
  ```

- [ ] **Environment variables are isolated per environment:**
  - Production secrets ≠ Development secrets
  - Each environment has separate credential sets

- [ ] **Secrets are rotated on deployment:**
  ```bash
  # Example: Auto-generate new key on deploy
  export AUTH_SECRET_KEY=$(openssl rand -hex 32)
  ```



## Configuration Files

```yaml
# config/production.yaml
environment: production
logging:
  level: INFO
  format: json
  output: file
  path: /var/log/codex/app.log

database:
  backend: postgresql
  host: codex-db.default.svc.cluster.local
  port: 5432
  name: codex_prod
  pool_size: 20
  max_overflow: 40

cache:
  backend: redis
  host: codex-redis.default.svc.cluster.local
  port: 6379
  ttl: 3600

monitoring:
  metrics_enabled: true
  metrics_port: 9090
  trace_sampling: 0.1
```

---

## Monitoring and Observability

### Prometheus Metrics

```yaml
# prometheus/codex-rules.yaml
groups:
- name: codex
  interval: 30s
  rules:
  - alert: HighErrorRate
    expr: rate(codex_errors_total[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"

  - alert: HighLatency
    expr: histogram_quantile(0.95, rate(codex_request_duration_seconds_bucket[5m])) > 1
    for: 5m
    annotations:
      summary: "P95 latency > 1s"
```

## Health Checks

```python
# Application health endpoints
GET /health           # Liveness probe (is app running?)
GET /ready            # Readiness probe (can accept traffic?)
GET /metrics          # Prometheus metrics
GET /version          # Version information
```

## Observability Best Practices

1. **Structured Logging**: JSON format for log aggregation
2. **Distributed Tracing**: OpenTelemetry for request flows
3. **Metrics**: Prometheus for time-series monitoring
4. **Alerting**: PagerDuty/Opsgenie integration
5. **Log Aggregation**: ELK/Loki stack

---

## Scaling Guidelines

### Horizontal Scaling

```bash
# Manual scaling
kubectl scale deployment codex --replicas=10 -n production

# Automatic scaling
kubectl autoscale deployment codex --min=3 --max=20 --cpu-percent=70 -n production

# Check scaling status
kubectl get hpa codex -n production -w
```

## Vertical Scaling

Adjust resource requests/limits in deployment manifest:

```yaml
resources:
  requests:
    memory: "4Gi"
    cpu: "2000m"
  limits:
    memory: "8Gi"
    cpu: "4000m"
```

### Capacity Planning

- **Baseline**: 3-5 pods minimum for HA
- **Peak**: 2-3x baseline capacity
- **Reserved**: 20-30% extra for surge traffic
- **Storage**: Plan for 1 year of logs/data retention

---

## Disaster Recovery

### Backup Procedures

```bash
# Database backup
kubectl exec -n production codex-db-0 -- \
  pg_dump -U codex -W codex_prod > backup-$(date +%Y%m%d).sql

# Volume backup (Kubernetes persistent volumes)
kubectl get pvc -n production
# Configure with cloud provider snapshots

# Configuration backup
kubectl get all -n production -o yaml > backup-manifests.yaml
```

## Rollback Procedures

```bash
# Kubernetes rollback
kubectl rollout undo deployment/codex -n production

# Helm rollback
helm rollback codex -n production

# Database rollback
psql -U codex -d codex_prod < backup-20260622.sql
```

## Recovery Time Objectives (RTO)

| Scenario | RTO | Procedure |
|----------|-----|-----------|
| **Pod Crash** | < 1 min | Auto-restart via K8s controller |
| **Node Failure** | 2-5 min | Pod rescheduled to another node |
| **Data Corruption** | 30 min | Restore from backup |
| **Region Outage** | 2-4 hours | Failover to secondary region |

---

## Troubleshooting

### Common Issues

#### Pod Won't Start

```bash
# Check pod status
kubectl describe pod codex-xxxx -n production

# Check logs
kubectl logs codex-xxxx -n production
kubectl logs codex-xxxx -n production --previous  # Previous crash

# Common causes:
# - Image not found: Check registry, image tag
# - OOMKilled: Increase memory limit
# - CrashLoopBackOff: Check application logs for errors
```

## High Memory Usage

```bash
# Check top processes
kubectl top pod -n production --sort-by=memory

# Check resource requests
kubectl describe node | grep "Allocated resources"

# Solution: Increase pod limits or scale horizontally
```

## Service Unavailable

```bash
# Check service endpoints
kubectl get endpoints codex -n production

# Check network policy
kubectl get networkpolicy -n production

# Check load balancer
kubectl get svc codex -n production -o wide
```

## Database Connection Errors

```bash
# Check database pod
kubectl get pod -n production -l app=postgres

# Check connection string
kubectl exec codex-xxxx -n production -- env | grep DATABASE

# Test connectivity
kubectl exec codex-xxxx -n production -- \
  psql -h codex-db -U codex -c "SELECT 1"
```

---

## Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Helm Charts](https://helm.sh/docs/)
- [API Reference](../api/)
- [Architecture Blueprint](../architecture/INDEX.md)

---

## Support & Escalation

- **Issues**: File GitHub issue with `[deployment]` tag
- **Security**: Email security@example.com
- **Urgent (Down)**: Page on-call engineer via PagerDuty
- **Documentation**: Update this guide and sync with team

---

*Last Updated: 2026-06-22T09:30:00Z*  
*Authority: @mbaetiong*  
*Status: ✅ Phase 7D Complete*
