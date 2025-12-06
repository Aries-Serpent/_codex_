# Gap 1: Kubernetes Orchestration Enhancement

**Priority:** Medium  
**Category:** Data & Experiments (Compute Management)  
**Azure MLOps Capabilities:** Rows 14-16  
**Current State:** 🟡 Partial (80% complete)

---

## Gap Description

### Current Implementation
- ✅ Docker containers exist (`Dockerfile`, `Dockerfile.gpu`, `Dockerfile.local`)
- ✅ Health probes implemented (`/health`, `/ready`, `/healthz`, `/readyz`)
- ✅ Graceful shutdown mechanisms
- ❌ No Kubernetes manifests
- ❌ No auto-scaling configuration
- ❌ No cloud-managed compute integration

### Azure MLOps Requirement (Level 4)
> **Row 16:** "Compute is managed (for ML workloads)"  
> Expectation: Kubernetes orchestration with auto-scaling, resource management, and production deployment patterns.

---

## Objective

Implement Kubernetes manifests and orchestration tooling to enable:
1. Production-grade deployment on Kubernetes clusters
2. Auto-scaling based on load and resource utilization
3. Resource quotas and limits management
4. Multi-pod deployment with load balancing
5. Health-based pod lifecycle management

---

## Implementation Tasks

### Task 1: Create Kubernetes Base Manifests
**File:** `manifests/k8s/base/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml-server
  labels:
    app: codex-ml
    component: inference
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codex-ml
  template:
    metadata:
      labels:
        app: codex-ml
        version: v1
    spec:
      containers:
      - name: codex-ml
        image: codex-ml:latest
        ports:
        - containerPort: 8000
          name: http
        - containerPort: 9090
          name: metrics
        env:
        - name: CODEX_FORCE_CPU
          value: "1"
        - name: WANDB_MODE
          value: "offline"
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
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 15
          periodSeconds: 5
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 15"]
```

### Task 2: Service Configuration
**File:** `manifests/k8s/base/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: codex-ml-service
  labels:
    app: codex-ml
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: http
    protocol: TCP
    name: http
  - port: 9090
    targetPort: metrics
    protocol: TCP
    name: metrics
  selector:
    app: codex-ml
```

### Task 3: Horizontal Pod Autoscaler
**File:** `manifests/k8s/base/hpa.yaml`

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: codex-ml-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codex-ml-server
  minReplicas: 2
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
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 30
      - type: Pods
        value: 2
        periodSeconds: 30
      selectPolicy: Max
```

### Task 4: ConfigMap for Application Settings
**File:** `manifests/k8s/base/configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: codex-ml-config
data:
  # Offline-first settings
  WANDB_MODE: "offline"
  HF_DATASETS_OFFLINE: "1"
  TRANSFORMERS_OFFLINE: "1"
  
  # Telemetry disabled
  DO_NOT_TRACK: "1"
  DISABLE_TELEMETRY: "1"
  
  # Deterministic mode
  PYTHONHASHSEED: "0"
  CUBLAS_WORKSPACE_CONFIG: ":4096:8"
  
  # Application settings
  WORKERS: "4"
  MAX_REQUESTS: "1000"
  TIMEOUT: "60"
```

### Task 5: Secret Management
**File:** `manifests/k8s/base/secret.yaml.template`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: codex-ml-secrets
type: Opaque
stringData:
  # Model registry credentials (if needed)
  MODEL_REGISTRY_TOKEN: ""
  
  # MLflow tracking (if using remote)
  MLFLOW_TRACKING_URI: ""
  MLFLOW_TRACKING_TOKEN: ""
  
  # API keys (if needed for external services)
  API_KEY: ""
```

### Task 6: Resource Quotas
**File:** `manifests/k8s/base/resourcequota.yaml`

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: codex-ml-quota
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    persistentvolumeclaims: "10"
```

### Task 7: GPU Node Deployment (Optional)
**File:** `manifests/k8s/overlays/gpu/deployment-patch.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml-server
spec:
  template:
    spec:
      nodeSelector:
        gpu: "true"
      containers:
      - name: codex-ml
        image: codex-ml:gpu
        env:
        - name: CODEX_FORCE_CPU
          value: "0"
        resources:
          requests:
            nvidia.com/gpu: 1
          limits:
            nvidia.com/gpu: 1
```

### Task 8: Kustomization Structure
**File:** `manifests/k8s/base/kustomization.yaml`

```yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
- deployment.yaml
- service.yaml
- hpa.yaml
- configmap.yaml
- resourcequota.yaml

configMapGenerator:
- name: codex-ml-config
  envs:
  - config.env

labels:
- pairs:
    app: codex-ml
    managed-by: kustomize
```

### Task 9: Deployment Script
**File:** `scripts/k8s_deploy.sh`

```bash
#!/usr/bin/env bash
set -euo pipefail

# Kubernetes deployment script for Codex ML

NAMESPACE="${CODEX_K8S_NAMESPACE:-default}"
ENVIRONMENT="${CODEX_ENV:-production}"
IMAGE_TAG="${CODEX_IMAGE_TAG:-latest}"

echo "Deploying Codex ML to Kubernetes"
echo "Namespace: $NAMESPACE"
echo "Environment: $ENVIRONMENT"
echo "Image Tag: $IMAGE_TAG"

# Create namespace if it doesn't exist
kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -

# Apply base manifests
kubectl apply -k "manifests/k8s/base" -n "$NAMESPACE"

# Apply environment-specific overlays
if [ -d "manifests/k8s/overlays/$ENVIRONMENT" ]; then
  echo "Applying $ENVIRONMENT overlay..."
  kubectl apply -k "manifests/k8s/overlays/$ENVIRONMENT" -n "$NAMESPACE"
fi

# Wait for deployment to be ready
echo "Waiting for deployment to be ready..."
kubectl rollout status deployment/codex-ml-server -n "$NAMESPACE" --timeout=5m

# Verify health
echo "Verifying health endpoints..."
POD=$(kubectl get pod -l app=codex-ml -n "$NAMESPACE" -o jsonpath='{.items[0].metadata.name}')
kubectl exec "$POD" -n "$NAMESPACE" -- curl -s http://localhost:8000/health

echo "✅ Deployment complete!"
```

### Task 10: Monitoring Integration
**File:** `manifests/k8s/base/servicemonitor.yaml`

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: codex-ml-metrics
  labels:
    app: codex-ml
spec:
  selector:
    matchLabels:
      app: codex-ml
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
```

---

## Testing & Validation

### Local Testing (Minikube/Kind)
```bash
# Start local cluster
minikube start --cpus=4 --memory=8192

# Build and load image
docker build -t codex-ml:latest .
minikube image load codex-ml:latest

# Deploy
kubectl apply -k manifests/k8s/base

# Test endpoints
kubectl port-forward svc/codex-ml-service 8000:8000
curl http://localhost:8000/health

# Check auto-scaling
kubectl get hpa -w

# Cleanup
kubectl delete -k manifests/k8s/base
```

### Production Deployment Checklist
- [ ] Image pushed to container registry
- [ ] Secrets configured in cluster
- [ ] Resource quotas appropriate for cluster
- [ ] HPA metrics server enabled
- [ ] Prometheus ServiceMonitor configured (if using)
- [ ] Ingress/LoadBalancer configured for external access
- [ ] TLS certificates configured
- [ ] RBAC permissions verified
- [ ] Network policies applied
- [ ] Backup/disaster recovery plan in place

---

## Documentation Updates

### New Files to Create
1. `docs/deployment/kubernetes_guide.md` - Comprehensive K8s deployment guide
2. `docs/deployment/scaling_guide.md` - Auto-scaling configuration and tuning
3. `docs/operations/kubernetes_troubleshooting.md` - Common issues and solutions

### Updates Required
1. `README.md` - Add Kubernetes deployment section
2. `docs/deployment/README.md` - Link to Kubernetes guide
3. `AGENTS.md` - Add K8s orchestration to prohibited actions (since external)

---

## Success Criteria

✅ **Complete when:**
1. All K8s manifests created and validated with `kubectl apply --dry-run`
2. Deployment script tested in local Minikube/Kind cluster
3. Auto-scaling verified with load testing
4. Health probes trigger proper pod lifecycle events
5. Documentation complete and reviewed
6. Azure MLOps capability rows 14-16 marked as ✅ Met

**Expected Capability Improvement:**
- Data & Experiments: 80% → 100% (+20%)
- Overall Azure MLOps Score: 94% → 96% (+2%)

---

## References

- Current Docker implementation: `Dockerfile`, `docker-compose.yml`
- Health probes: `src/codex_ml/serving/health.py`
- Prometheus metrics: `src/codex_ml/monitoring/metrics.py`
- Azure MLOps maturity model documentation
