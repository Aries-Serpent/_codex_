# Deployment Guide - Aries-Serpent v0.1.0

**Version**: v0.2.1
**Last Updated:** 2026-07-11

**Document Type:** Operations & Deployment Guide
**Audience:** DevOps Engineers, System Administrators, Cloud Architects
**Last Updated: 2026-07-09

## Deployment Methods Overview

```

 Aries-Serpent Deployment Options 

 Local/Dev Docker Compose Kubernetes 
 (Single Node) (Multi-Node) (Production) 

```

## 1. Docker Compose Deployment

### 1.1 Quick Start with Docker Compose

```bash
# Clone and setup
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create .env file
cat > .env << 'EOF'
POSTGRES_USER=aries
POSTGRES_PASSWORD=secret-change-this
POSTGRES_DB=aries_db
REDIS_PASSWORD=redis-secret
API_PORT=8000
EOF

# Start services
docker-compose -f docker/docker-compose.yml up -d

# Verify
docker-compose -f docker/docker-compose.yml ps
curl http://localhost:8000/api/v1/health
```

### 1.2 Docker Compose Configuration

```yaml
# docker/docker-compose.yml
version: '3.9'

services:
 api:
 image: aries-serpent:0.1.0-api
 ports:
 - "${API_PORT}:8000"
 environment:
 DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
 REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
 depends_on:
 - postgres
 - redis
 healthcheck:
 test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
 interval: 30s
 timeout: 10s
 retries: 3

 inference:
 image: aries-serpent:0.1.0-inference
 environment:
 DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
 REDIS_URL: redis://:${REDIS_PASSWORD}@redis:6379
 depends_on:
 - postgres
 - redis
 deploy:
 resources:
 limits:
 cpus: '2'
 memory: 4G

 postgres:
 image: postgres:15-alpine
 environment:
 POSTGRES_USER: ${POSTGRES_USER}
 POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
 POSTGRES_DB: ${POSTGRES_DB}
 volumes:
 - postgres_data:/var/lib/postgresql/data
 healthcheck:
 test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
 interval: 10s

 redis:
 image: redis:7-alpine
 command: redis-server --requirepass ${REDIS_PASSWORD}
 volumes:
 - redis_data:/data
 healthcheck:
 test: ["CMD", "redis-cli", "ping"]
 interval: 10s

volumes:
 postgres_data:
 redis_data:

networks:
 default:
 name: aries-network
```

### 1.3 Scaling with Docker Compose

```bash
# Scale specific service
docker-compose -f docker/docker-compose.yml up -d --scale inference=3

# View replicas
docker-compose -f docker/docker-compose.yml ps

# Monitor resource usage
docker stats

# Stop all services
docker-compose -f docker/docker-compose.yml down
```

## 2. Kubernetes Deployment

### 2.1 Local Kubernetes Setup (minikube)

```bash
# Install minikube (if not installed)
brew install minikube # macOS
# or curl https://minikube.sigs.k8s.io/docs/start/ for other platforms

# Start minikube cluster
minikube start --cpus=4 --memory=8192 --disk-size=20g

# Enable addons for monitoring
minikube addons enable prometheus
minikube addons enable dashboard

# Deploy Aries-Serpent
kubectl apply -f manifests/k8s/base/
kubectl apply -f manifests/k8s/overlays/development/

# Verify deployment
kubectl get all

# Access application
kubectl port-forward svc/api 8000:8000
curl http://localhost:8000/api/v1/health

# Dashboard
minikube dashboard
```

### 2.2 Production Kubernetes Setup

#### Prerequisites

- Managed K8s cluster (EKS, GKE, AKS, or on-premises)
- kubectl configured to access cluster
- Helm 3+ (optional but recommended)
- Persistent storage provisioner

#### Namespace Setup

```bash
# Create namespace
kubectl create namespace aries-prod

# Set as default
kubectl config set-context --current --namespace=aries-prod

# Create secrets
kubectl create secret generic db-credentials \
 --from-literal=username=aries \
 --from-literal=password='secure-password' \
 -n aries-prod

kubectl create secret generic api-secrets \
 --from-literal=jwt-secret='jwt-secret-key' \
 -n aries-prod
```

#### Deployment

```bash
# Apply production manifests
kubectl apply -f manifests/k8s/base/ -n aries-prod
kubectl apply -f manifests/k8s/overlays/production/ -n aries-prod

# Verify all pods are running
kubectl get pods -n aries-prod
kubectl get svc -n aries-prod

# Check logs
kubectl logs -l app=api -n aries-prod -f

# Monitor metrics
kubectl top pods -n aries-prod
kubectl top nodes
```

### 2.3 Kubernetes Configuration

```yaml
# manifests/k8s/base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
 name: api
spec:
 replicas: 3
 selector:
 matchLabels:
 app: api
 template:
 metadata:
 labels:
 app: api
 spec:
 containers:
 - name: api
 image: aries-serpent:0.1.0-api
 ports:
 - containerPort: 8000
 env:
 - name: DATABASE_URL
 valueFrom:
 secretKeyRef:
 name: db-credentials
 key: url
 resources:
 requests:
 cpu: "500m"
 memory: "1Gi"
 limits:
 cpu: "2"
 memory: "4Gi"
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
 initialDelaySeconds: 5
 periodSeconds: 5
```

### 2.4 Auto-scaling

```yaml
# manifests/k8s/base/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
 name: api-hpa
spec:
 scaleTargetRef:
 apiVersion: apps/v1
 kind: Deployment
 name: api
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

## 3. Backup & Recovery

### 3.1 Database Backup

```bash
# Backup PostgreSQL
kubectl exec -it postgres-0 -n aries-prod -- \
 pg_dump -U aries aries_db > backup-$(date +%Y%m%d).sql

# Backup to S3
kubectl exec -it postgres-0 -n aries-prod -- \
 pg_dump -U aries aries_db | gzip | \
 aws s3 cp - s3://backups/aries-db-$(date +%Y%m%d).sql.gz

# Restore from backup
kubectl exec -i postgres-0 -n aries-prod -- \
 psql -U aries aries_db < backup-20260709.sql
```

### 3.2 Configuration Backup

```bash
# Backup ConfigMaps
kubectl get configmaps -n aries-prod -o yaml > configmaps-backup.yaml

# Backup Secrets (WARNING: contains sensitive data)
kubectl get secrets -n aries-prod -o yaml > secrets-backup.yaml

# Restore
kubectl apply -f configmaps-backup.yaml
kubectl apply -f secrets-backup.yaml
```

## 4. Monitoring & Health Checks

### 4.1 Health Check Endpoints

```bash
# Application health
curl http://localhost:8000/health
# Response: {"status": "healthy", "version": "0.1.0"}

# Readiness check
curl http://localhost:8000/ready
# Response: {"ready": true, "dependencies": {...}}

# Kubernetes health probes
kubectl describe pod api-0 | grep -A 10 "Liveness"
```

### 4.2 Prometheus Metrics

```bash
# View metrics endpoint
curl http://localhost:8000/metrics

# Port-forward Prometheus
kubectl port-forward svc/prometheus 9090:9090

# Access Prometheus UI
open http://localhost:9090
```

## 5. Scaling Strategies

### 5.1 Horizontal Scaling (More Pods)

```bash
# Scale API deployment
kubectl scale deployment api --replicas=5 -n aries-prod

# Verify
kubectl get pods -l app=api -n aries-prod
```

### 5.2 Vertical Scaling (More Resources)

```yaml
# Update resource limits in deployment
kubectl set resources deployment api \
 --limits=cpu=4,memory=8Gi \
 --requests=cpu=2,memory=4Gi \
 -n aries-prod
```

### 5.3 Multi-Region Deployment

```bash
# Deploy to multiple regions
for region in us-east-1 eu-west-1 ap-southeast-1; do
 KUBECONFIG=~/.kube/${region}-config \
 kubectl apply -f manifests/k8s/overlays/production/
done
```

## 6. Troubleshooting

### 6.1 Common Issues

**Pod stuck in ImagePullBackOff:**
```bash
kubectl describe pod <pod-name>
# Check image registry credentials
kubectl create secret docker-registry regcred \
 --docker-server=ghcr.io \
 --docker-username=user \
 --docker-******
```

**Node disk pressure:**
```bash
# Clean up old images
docker image prune -a --force

# Increase node disk size
kubectl drain node <node> --ignore-daemonsets
# Then resize in cloud provider
kubectl uncordon node <node>
```

**Database connection timeout:**
```bash
# Check database pod
kubectl logs postgres-0

# Test connection from pod
kubectl exec -it api-0 -- \
 psql -h postgres -U aries -d aries_db
```

### 6.2 Debug Commands

```bash
# View all resources
kubectl get all -n aries-prod

# Detailed pod info
kubectl describe pod <pod-name> -n aries-prod

# Container logs
kubectl logs <pod-name> -n aries-prod

# Port forward for debugging
kubectl port-forward <pod-name> 8000:8000

# Execute command in pod
kubectl exec -it <pod-name> -- /bin/bash

# View events
kubectl get events -n aries-prod --sort-by='.lastTimestamp'
```

## 7. Production Checklist

Before deploying to production:

- [ ] All images pushed to registry
- [ ] Secrets configured in cluster
- [ ] Database backups configured
- [ ] Monitoring and alerting enabled
- [ ] Resource requests/limits set
- [ ] Health checks configured
- [ ] Log aggregation setup
- [ ] Network policies applied
- [ ] TLS certificates configured
- [ ] Disaster recovery plan documented

---

**Status:** COMPLETE
**Last Updated: 2026-07-09
