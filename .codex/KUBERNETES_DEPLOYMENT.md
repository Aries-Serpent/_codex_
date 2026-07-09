# Kubernetes Deployment Guide — Aries-Serpent v0.1.0-final

Complete guide for deploying Aries-Serpent to Kubernetes clusters with production-grade configuration.

## Deployment Architecture

```
┌─────────────────────────────────────────────┐
│        Load Balancer (External)             │
│        Service: aries-serpent-api           │
└───────────────┬─────────────────────────────┘
                │
        ┌───────┴─────────┬──────────────┐
        │                 │              │
    ┌───▼───┐         ┌──▼──┐        ┌──▼──┐
    │ Pod 1 │         │Pod 2│        │Pod 3│
    │ API   │         │ API │        │ API │
    └───┬───┘         └──┬──┘        └──┬──┘
        │                │              │
        └────┬───────────┴──────────────┘
             │
    ┌────────▼────────────┐
    │ HPA (1-10 replicas) │
    │ 70% CPU target      │
    └─────────────────────┘
         │
         ├─ ConfigMap (aries-serpent-config)
         ├─ Secrets (aries-serpent-secrets)
         └─ ServiceAccount (aries-serpent)
```

## File Structure

```
.codex/kubernetes/
├── api-deployment.yaml      # Deployment definition (3 replicas)
├── api-service.yaml         # LoadBalancer service
├── config-map.yaml          # Non-sensitive configuration
├── secret-template.yaml     # Secrets template (DO NOT commit values)
├── hpa.yaml                 # Horizontal Pod Autoscaler (1-10 replicas)
├── rbac.yaml                # ServiceAccount, Role, RoleBinding
└── KUBERNETES_DEPLOYMENT.md # This file
```

## Prerequisites

### Kubernetes Cluster
- Kubernetes 1.24+ (for SecurityPolicy and HPA v2)
- Persistent Volume support (optional)
- Metrics Server for HPA (usually pre-installed)

### Tools
```bash
# Required
kubectl 1.24+                # Kubernetes CLI
kubeval                      # YAML validation

# Optional but recommended
helm 3.10+                   # Package manager
kustomize                    # Template overlays
kind                         # Local K8s testing
```

### Verify Prerequisites

```bash
# Check kubectl version
kubectl version --client

# Verify metrics-server (for HPA)
kubectl get deployment metrics-server -n kube-system

# Check API version support
kubectl api-versions | grep autoscaling
```

---

## Deployment Steps

### Step 1: Create Namespace (Optional)

```bash
# Create dedicated namespace
kubectl create namespace aries-serpent

# Set default namespace
kubectl config set-context --current --namespace=aries-serpent
```

### Step 2: Create RBAC Resources

```bash
# Apply RBAC (ServiceAccount, Role, RoleBinding)
kubectl apply -f .codex/kubernetes/rbac.yaml

# Verify
kubectl get serviceaccount aries-serpent
kubectl get role aries-serpent-role
kubectl get rolebinding aries-serpent-binding
```

### Step 3: Create ConfigMap

```bash
# Apply ConfigMap
kubectl apply -f .codex/kubernetes/config-map.yaml

# Verify
kubectl get configmap aries-serpent-config
kubectl get configmap aries-serpent-config -o yaml
```

### Step 4: Create Secrets

```bash
# Option A: From template (edit with real values first)
cp .codex/kubernetes/secret-template.yaml /tmp/secrets.yaml
# Edit /tmp/secrets.yaml with actual secrets
kubectl apply -f /tmp/secrets.yaml
rm /tmp/secrets.yaml  # DO NOT commit edited template

# Option B: From environment variables
kubectl create secret generic aries-serpent-secrets \
  --from-literal=api_key=$API_KEY \
  --from-literal=database_url=$DATABASE_URL \
  --from-literal=jwt_secret=$JWT_SECRET

# Option C: From file
cat > /tmp/secrets.env << 'EOF'
api_key=your-secret-value
database_url=******host:5432/db
jwt_secret=your-jwt-secret
EOF
kubectl create secret generic aries-serpent-secrets --from-env-file=/tmp/secrets.env
rm /tmp/secrets.env

# Verify (do NOT show values)
kubectl get secret aries-serpent-secrets
kubectl get secret aries-serpent-secrets -o yaml  # Shows encoded values
```

### Step 5: Deploy API Server

```bash
# Apply Deployment
kubectl apply -f .codex/kubernetes/api-deployment.yaml

# Watch rollout
kubectl rollout status deployment/aries-serpent-api --timeout=5m

# Verify
kubectl get deployment aries-serpent-api
kubectl get pods -l app=aries-serpent,component=api
```

### Step 6: Create Service

```bash
# Apply Service
kubectl apply -f .codex/kubernetes/api-service.yaml

# Verify
kubectl get service aries-serpent-api
kubectl get endpoints aries-serpent-api

# Get LoadBalancer IP (may take 1-2 minutes)
kubectl get service aries-serpent-api --watch
```

### Step 7: Deploy HPA

```bash
# Apply HorizontalPodAutoscaler
kubectl apply -f .codex/kubernetes/hpa.yaml

# Verify
kubectl get hpa aries-serpent-api-hpa
kubectl describe hpa aries-serpent-api-hpa
```

### Step 8: Verify Full Stack

```bash
# Check all resources
kubectl get all -l app=aries-serpent

# Check health of pods
kubectl get pods -l app=aries-serpent -o wide

# Get service details
kubectl get service aries-serpent-api -o wide

# Test health endpoint
EXTERNAL_IP=$(kubectl get service aries-serpent-api -o jsonpath='{.status.loadBalancer.ingress[0].ip}')
curl http://$EXTERNAL_IP:8000/health
```

---

## Complete Deployment Script

```bash
#!/bin/bash
# deploy-aries.sh - Complete Kubernetes deployment

set -e

NAMESPACE=${1:-default}
CONFIG_DIR=".codex/kubernetes"

echo "🚀 Deploying Aries-Serpent to namespace: $NAMESPACE"

# Step 1: Create namespace if needed
echo "1️⃣  Creating namespace..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Step 2: RBAC
echo "2️⃣  Applying RBAC..."
kubectl apply -n $NAMESPACE -f $CONFIG_DIR/rbac.yaml

# Step 3: ConfigMap
echo "3️⃣  Applying ConfigMap..."
kubectl apply -n $NAMESPACE -f $CONFIG_DIR/config-map.yaml

# Step 4: Secrets (must exist before deployment)
echo "4️⃣  Checking Secrets..."
if ! kubectl get secret aries-serpent-secrets -n $NAMESPACE &>/dev/null; then
  echo "⚠️  Secret not found. Create with:"
  echo "   kubectl create secret generic aries-serpent-secrets \\"
  echo "     --from-literal=api_key=<value> \\"
  echo "     --from-literal=database_url=<value> \\"
  echo "     -n $NAMESPACE"
  exit 1
fi

# Step 5: Deployment
echo "5️⃣  Deploying API Server..."
kubectl apply -n $NAMESPACE -f $CONFIG_DIR/api-deployment.yaml
kubectl rollout status deployment/aries-serpent-api -n $NAMESPACE --timeout=5m

# Step 6: Service
echo "6️⃣  Exposing Service..."
kubectl apply -n $NAMESPACE -f $CONFIG_DIR/api-service.yaml

# Step 7: HPA
echo "7️⃣  Applying Autoscaler..."
kubectl apply -n $NAMESPACE -f $CONFIG_DIR/hpa.yaml

# Verify
echo "✅ Deployment Complete!"
echo ""
echo "📊 Status:"
kubectl get all -n $NAMESPACE -l app=aries-serpent
echo ""
echo "🔗 Service Details:"
kubectl get service aries-serpent-api -n $NAMESPACE -o wide
```

---

## Validation

### Validate YAML

```bash
# Validate all manifests
kubeval .codex/kubernetes/api-deployment.yaml
kubeval .codex/kubernetes/api-service.yaml
kubeval .codex/kubernetes/config-map.yaml
kubeval .codex/kubernetes/hpa.yaml
kubeval .codex/kubernetes/rbac.yaml

# Validate with dry-run
kubectl apply -f .codex/kubernetes/ --dry-run=client --validate=true
```

### Health Checks

```bash
# Check pod status
kubectl get pods -l app=aries-serpent -o wide

# Check pod logs
kubectl logs deployment/aries-serpent-api --tail=100

# Check health endpoint
kubectl exec -it <pod-name> -- curl http://localhost:8000/health

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Performance Metrics

```bash
# View current resource usage
kubectl top pods -l app=aries-serpent

# View node resource usage
kubectl top nodes

# View HPA metrics
kubectl get hpa aries-serpent-api-hpa --watch
```

---

## Scaling

### Manual Scaling

```bash
# Scale to 5 replicas
kubectl scale deployment aries-serpent-api --replicas=5

# Verify
kubectl get deployment aries-serpent-api
kubectl get pods -l app=aries-serpent
```

### Autoscaling Behavior

HPA monitors CPU/memory utilization:

- **Scale Up:** When CPU > 70% or Memory > 80%
  - Adds 100% of current pods or 2 pods (whichever is greater)
  - Decision window: 30 seconds
  
- **Scale Down:** When CPU < 50% and Memory < 70%
  - Removes 50% of pods or 1 pod (whichever is greater)
  - Decision window: 300 seconds (5 minutes, prevents thrashing)

---

## Updating Deployment

### Rolling Update

```bash
# Update container image
kubectl set image deployment/aries-serpent-api \
  api=aries-serpent:0.1.1-api \
  --record

# Watch rollout
kubectl rollout status deployment/aries-serpent-api

# View rollout history
kubectl rollout history deployment/aries-serpent-api

# Rollback to previous version
kubectl rollout undo deployment/aries-serpent-api

# Rollback to specific revision
kubectl rollout undo deployment/aries-serpent-api --to-revision=2
```

### Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap aries-serpent-config

# Restart pods to pick up changes
kubectl rollout restart deployment/aries-serpent-api
```

### Update Secrets

```bash
# For sensitive data, recreate secret
kubectl delete secret aries-serpent-secrets
kubectl create secret generic aries-serpent-secrets \
  --from-literal=api_key=$NEW_API_KEY

# Restart pods
kubectl rollout restart deployment/aries-serpent-api
```

---

## Troubleshooting

### Pod Won't Start

```bash
# Check pod status
kubectl describe pod <pod-name>

# Check logs
kubectl logs <pod-name>
kubectl logs <pod-name> --previous  # Previous crash

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

### Service Not Accessible

```bash
# Verify service endpoints
kubectl get endpoints aries-serpent-api

# Check service selector
kubectl get service aries-serpent-api -o yaml | grep -A 10 selector

# Test connectivity from pod
kubectl exec <pod-name> -- curl http://aries-serpent-api:8000/health
```

### HPA Not Scaling

```bash
# Check HPA status
kubectl describe hpa aries-serpent-api-hpa

# Check metrics available
kubectl get --raw /apis/metrics.k8s.io/v1beta1/nodes

# Check metrics-server logs
kubectl logs deployment/metrics-server -n kube-system
```

### Resource Exhaustion

```bash
# Check node resource usage
kubectl top nodes

# Check pod resource usage
kubectl top pods -l app=aries-serpent

# Increase limits in deployment
kubectl set resources deployment/aries-serpent-api \
  --limits=cpu=1000m,memory=2Gi \
  --requests=cpu=500m,memory=1Gi
```

---

## Helm Alternative

For advanced deployments, use Helm charts:

```bash
# Create Helm chart structure
helm create aries-serpent-chart

# Install from chart
helm install aries-serpent ./aries-serpent-chart

# Upgrade
helm upgrade aries-serpent ./aries-serpent-chart

# Check release status
helm status aries-serpent

# Rollback
helm rollback aries-serpent
```

---

## Monitoring & Observability

### Prometheus Integration

```yaml
# ServiceMonitor for Prometheus (if using Prometheus Operator)
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: aries-serpent
spec:
  selector:
    matchLabels:
      app: aries-serpent
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
```

### Logging

```bash
# Collect logs from all pods
kubectl logs -f deployment/aries-serpent-api --all-containers=true

# Export logs
kubectl logs deployment/aries-serpent-api > deployment-logs.txt

# Centralized logging (if ELK/Loki deployed)
# Logs automatically shipped to central system
```

---

## Security Best Practices

✅ **Implemented in Manifests:**
- Non-root user (UID 1001)
- Read-only root filesystem support
- Resource limits enforced
- RBAC with least privilege
- Secrets not in ConfigMap
- Health checks for pod status
- Pod Anti-Affinity for HA

**Additional Recommendations:**
- Network Policies to restrict traffic
- Pod Security Standards enforcement
- Image scanning before deployment
- Regular secret rotation
- Audit logging enabled
- TLS ingress configuration

---

## High Availability Checklist

- ✅ Replicas: 3 (minimum for HA)
- ✅ Pod Anti-Affinity: Distributed across nodes
- ✅ Health Checks: Liveness + Readiness
- ✅ Resource Limits: Preventing node starvation
- ✅ Graceful Shutdown: 30s termination period
- ✅ HPA: Automatic scaling (1-10 replicas)
- ✅ RollingUpdate: Zero-downtime deployments

---

## References

- Kubernetes Documentation: https://kubernetes.io/docs/
- Deployment Best Practices: https://kubernetes.io/docs/concepts/configuration/overview/
- Security: https://kubernetes.io/docs/concepts/security/
- RBAC: https://kubernetes.io/docs/reference/access-authn-authz/rbac/
- HPA: https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/

---

**Last Updated:** 2026-07-09  
**Status:** ✅ Production Ready
