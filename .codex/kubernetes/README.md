# Aries-Serpent Kubernetes Manifests

Production-grade Kubernetes deployment manifests for Aries-Serpent v0.1.0-final.

## Files

| File | Purpose | Type |
|------|---------|------|
| `api-deployment.yaml` | API Server deployment (3 replicas, health checks, resource limits) | Deployment |
| `api-service.yaml` | LoadBalancer service exposing HTTP:8000 | Service |
| `config-map.yaml` | Non-sensitive configuration (log level, timeouts, etc.) | ConfigMap |
| `secret-template.yaml` | Template for secrets (API keys, credentials) - DO NOT commit values | Secret |
| `hpa.yaml` | Horizontal Pod Autoscaler (1-10 replicas, 70% CPU target) | HPA |
| `rbac.yaml` | RBAC resources (ServiceAccount, Role, RoleBinding) | RBAC |
| `README.md` | This file | Documentation |

## Quick Start

### 1. Validate manifests

```bash
# Validate with kubectl
kubectl apply -f . --dry-run=client --validate=true

# Validate with kubeval (if installed)
kubeval *.yaml
```

### 2. Create secrets

```bash
# Create secret with actual values (replace XXXXX with real values)
kubectl create secret generic aries-serpent-secrets \
  --from-literal=api_key=XXXXX \
  --from-literal=database_url=XXXXX \
  --from-literal=jwt_secret=XXXXX
```

### 3. Deploy all resources

```bash
# Apply all manifests in order
kubectl apply -f rbac.yaml
kubectl apply -f config-map.yaml
kubectl apply -f api-deployment.yaml
kubectl apply -f api-service.yaml
kubectl apply -f hpa.yaml

# Or apply all at once
kubectl apply -f .
```

### 4. Verify deployment

```bash
# Check all resources
kubectl get all -l app=aries-serpent

# Watch rollout
kubectl rollout status deployment/aries-serpent-api

# Get service IP
kubectl get service aries-serpent-api
```

## Resource Summary

```yaml
Deployment:
  replicas: 3
  containers: 1 (api)
  image: aries-serpent:0.1.0-final-api
  requests:
    cpu: 200m
    memory: 512Mi
  limits:
    cpu: 500m
    memory: 1Gi

Service:
  type: LoadBalancer
  port: 8000
  sessionAffinity: ClientIP

HPA:
  min: 1 replica
  max: 10 replicas
  target: 70% CPU utilization
  scale-up: 30s window
  scale-down: 300s window

RBAC:
  serviceAccount: aries-serpent
  permissions: Read ConfigMap, Read Secret, Read Pods
```

## Security Features

- ✅ Non-root user (UID 1001)
- ✅ Read-only root filesystem support
- ✅ Resource limits enforced
- ✅ RBAC with least privilege
- ✅ Secrets encrypted (not in ConfigMap)
- ✅ Health checks (liveness + readiness)
- ✅ Pod anti-affinity for HA
- ✅ Zero-downtime rolling updates

## Documentation

See detailed guides in `.codex/`:
- `DOCKER_BUILD.md` — Docker image build instructions
- `KUBERNETES_DEPLOYMENT.md` — Complete K8s deployment guide
- `CONTAINER_SECURITY.md` — Security hardening and scanning

---

**Version:** 0.1.0-final  
**Status:** ✅ Production Ready  
**Last Updated:** 2026-07-09
