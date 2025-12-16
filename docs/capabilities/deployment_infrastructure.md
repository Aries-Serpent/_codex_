# Deployment Infrastructure

## Overview

The deployment infrastructure capability provides comprehensive container orchestration, Kubernetes manifests, Docker configurations, and infrastructure-as-code templates for deploying Codex ML services in production environments.

**Keywords**: deployment, infrastructure, kubernetes, docker, container, orchestration, rollback, helm, k8s, manifests, devops, ci-cd

## Purpose

Provides deployment infrastructure through:
- **Container Orchestration**: Kubernetes manifests and Helm charts
- **Docker Configuration**: Optimized Dockerfiles for production
- **Infrastructure-as-Code**: Reproducible infrastructure templates
- **Rollback Mechanisms**: Safe deployment with automatic rollback
- **Health Checks**: Liveness and readiness probes
- **Resource Management**: CPU/memory limits and autoscaling

## Architecture

### Deployment Layers

```
┌─────────────────────────────────────┐
│   CI/CD Pipeline                    │
│   (Build, Test, Deploy triggers)    │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Container Registry                │
│   (Docker images, versioning)       │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Kubernetes Cluster                │
│   (Pods, Services, Ingress)         │
└─────────────┬───────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│   Monitoring & Observability        │
│   (Metrics, Logs, Alerts)           │
└─────────────────────────────────────┘
```

## Configuration

### Docker Configuration

```dockerfile
# Production Dockerfile pattern
FROM python:3.11-slim AS builder

# Security: Non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Layer caching optimization
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN pip install --no-cache-dir .

USER appuser

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s \
  CMD curl -f http://localhost:8080/healthz || exit 1

CMD ["python", "-m", "codex.serve"]
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml-service
  labels:
    app: codex-ml
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codex-ml
  template:
    metadata:
      labels:
        app: codex-ml
    spec:
      containers:
      - name: codex-ml
        image: codex-ml:latest
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "2"
            memory: "4Gi"
          requests:
            cpu: "500m"
            memory: "1Gi"
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Helm Chart Values

```yaml
# values.yaml
replicaCount: 3

image:
  repository: codex-ml
  tag: latest
  pullPolicy: IfNotPresent

service:
  type: ClusterIP
  port: 8080

resources:
  limits:
    cpu: 2
    memory: 4Gi
  requests:
    cpu: 500m
    memory: 1Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

rollback:
  enabled: true
  maxRevisions: 5
```

## Usage Examples

### Example 1: Local Docker Build and Run

```bash
# Build production image
docker build -f Dockerfile -t codex-ml:latest .

# Run with health checks
docker run -d \
  --name codex-ml \
  -p 8080:8080 \
  --health-cmd="curl -f http://localhost:8080/healthz || exit 1" \
  --health-interval=30s \
  codex-ml:latest

# Verify container health
docker inspect --format='{{.State.Health.Status}}' codex-ml
```

### Example 2: Kubernetes Deployment

```bash
# Apply manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Check deployment status
kubectl rollout status deployment/codex-ml-service

# Verify pods are running
kubectl get pods -l app=codex-ml
```

### Example 3: Helm Chart Installation

```bash
# Install with custom values
helm install codex-ml ./charts/codex-ml \
  --namespace codex \
  --create-namespace \
  --set replicaCount=3 \
  --set image.tag=v1.2.0

# Upgrade with rollback capability
helm upgrade codex-ml ./charts/codex-ml \
  --set image.tag=v1.3.0 \
  --wait --timeout=5m

# Rollback if needed
helm rollback codex-ml 1
```

### Example 4: Blue-Green Deployment

```bash
# Deploy green version
kubectl apply -f k8s/deployment-green.yaml

# Verify green is healthy
kubectl rollout status deployment/codex-ml-green

# Switch traffic to green
kubectl patch service codex-ml \
  -p '{"spec":{"selector":{"version":"green"}}}'

# Remove blue after verification
kubectl delete deployment codex-ml-blue
```

### Example 5: Canary Deployment

```yaml
# canary-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml-canary
spec:
  replicas: 1  # 10% of traffic
  template:
    metadata:
      labels:
        app: codex-ml
        track: canary
```

## Safeguards

### Deployment Safeguards

- **Validation**: Manifest validation before apply with kubeval
- **Resource Limits**: Enforced CPU/memory constraints
- **Rollback**: Automatic rollback on failed health checks
- **Progressive**: Gradual rollout with pause on errors
- **Audit**: All deployments logged with timestamps

### Security Safeguards

- **Non-root**: Containers run as non-root user
- **Read-only**: File system read-only where possible
- **Secrets**: Kubernetes secrets for sensitive data
- **Network Policies**: Restrict pod-to-pod communication
- **RBAC**: Role-based access control for kubectl

### Health Check Safeguards

```python
# Health check implementation
from fastapi import FastAPI
from typing import Dict

app = FastAPI()

@app.get("/healthz")
async def health_check() -> Dict[str, str]:
    """
    Liveness probe endpoint.
    
    Safeguard: Returns 200 only if service is alive.
    Validation: Checks core dependencies.
    """
    return {"status": "healthy"}

@app.get("/ready")
async def readiness_check() -> Dict[str, str]:
    """
    Readiness probe endpoint.
    
    Safeguard: Returns 200 only when ready for traffic.
    Validation: Checks model loaded and DB connected.
    """
    # Validate model is loaded
    if not model_manager.is_loaded():
        raise HTTPException(503, "Model not loaded")
    
    return {"status": "ready"}
```

## Best Practices

1. **Immutable Infrastructure**: Never modify running containers
2. **Version Tags**: Always use specific image tags, not :latest
3. **Resource Requests**: Set both requests and limits
4. **Health Checks**: Implement both liveness and readiness probes
5. **Rolling Updates**: Use rolling strategy with maxUnavailable
6. **Secrets Management**: Use external secrets operators
7. **GitOps**: Store all manifests in version control
8. **Monitoring**: Deploy Prometheus/Grafana alongside

## Troubleshooting

### Pod Not Starting

```bash
# Check pod events
kubectl describe pod <pod-name>

# Check container logs
kubectl logs <pod-name> -c <container-name>

# Check resource availability
kubectl describe nodes | grep -A5 "Allocated resources"
```

### Deployment Stuck

```bash
# Check rollout status
kubectl rollout status deployment/<name> --timeout=5m

# Check for failed replicas
kubectl get deployment <name> -o jsonpath='{.status}'

# Force rollback
kubectl rollout undo deployment/<name>
```

### Health Check Failures

```bash
# Test health endpoint manually
kubectl exec <pod-name> -- curl -s localhost:8080/healthz

# Check probe configuration
kubectl get deployment <name> -o yaml | grep -A10 "livenessProbe"
```

## Integration

### CI/CD Integration

```yaml
# .github/workflows/deploy.yml
deploy:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v4
    
    - name: Build and push image
      run: |
        docker build -t $IMAGE:$TAG .
        docker push $IMAGE:$TAG
    
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/codex-ml \
          codex-ml=$IMAGE:$TAG
        kubectl rollout status deployment/codex-ml
```

### Monitoring Integration

```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: codex-ml-metrics
spec:
  selector:
    matchLabels:
      app: codex-ml
  endpoints:
  - port: metrics
    interval: 15s
```

## Related Capabilities

- [CI/CD Pipeline](ci_cd_pipeline.md) - Build and deployment automation
- [Status Reporting](status_reporting.md) - Deployment status monitoring
- [Archival Bundling](archival_bundling.md) - Artifact packaging

## References

- Kubernetes Documentation: https://kubernetes.io/docs/
- Docker Best Practices: https://docs.docker.com/develop/develop-images/dockerfile_best-practices/
- Helm Charts Guide: https://helm.sh/docs/topics/charts/
