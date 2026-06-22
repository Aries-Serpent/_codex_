# Kubernetes Deployment Guide

> **Version**: 1.0.0  
> **Last Updated**: 2026-06-22  
> **Status**: Production-Ready  
> **Audience**: DevOps Engineers, Platform Teams, Kubernetes Operators  

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Kubernetes Manifests](#kubernetes-manifests)
4. [Helm Chart Configuration](#helm-chart-configuration)
5. [StatefulSet Deployment](#statefulset-deployment)
6. [Ingress Configuration](#ingress-configuration)
7. [Resource Limits & Requests](#resource-limits--requests)
8. [Horizontal Pod Autoscaler](#horizontal-pod-autoscaler)
9. [Monitoring & Observability](#monitoring--observability)
10. [Security Policies](#security-policies)
11. [Troubleshooting](#troubleshooting)
12. [Production Checklist](#production-checklist)

---

## Overview

This guide provides comprehensive instructions for deploying the Codex ML platform on Kubernetes with production-grade security, monitoring, and scalability.

### Key Deployment Patterns

1. **Deployment**: Stateless API and worker services
2. **StatefulSet**: Persistent model serving and training
3. **ConfigMap**: Configuration management
4. **Secret**: Sensitive data management
5. **Service**: Internal and external networking
6. **Ingress**: External traffic routing

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│  Kubernetes Cluster (kubeadm, EKS, GKE, AKS)           │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  Ingress Controller (nginx)                      │   │
│  │  - Route /api → API Service                      │   │
│  │  - Route /metrics → Prometheus                   │   │
│  └──────────────────────────────────────────────────┘   │
│                 │                                        │
│  ┌──────────────┴──────────────────────────────────┐   │
│  │  Services                                        │   │
│  │  - codex-api (ClusterIP:8000)                   │   │
│  │  - codex-inference (LoadBalancer:9000)         │   │
│  │  - codex-prometheus (ClusterIP:9090)           │   │
│  └──────────────┬──────────────────────────────────┘   │
│                 │                                        │
│  ┌──────────────┴──────────────────────────────────┐   │
│  │  Deployments & StatefulSets                     │   │
│  │  ┌─────────────────┐  ┌─────────────────┐      │   │
│  │  │ codex-api       │  │ codex-training  │      │   │
│  │  │ Replicas: 3     │  │ Replicas: 1     │      │   │
│  │  └─────────────────┘  └─────────────────┘      │   │
│  │  ┌─────────────────┐                           │   │
│  │  │ codex-worker    │                           │   │
│  │  │ Replicas: 2     │                           │   │
│  │  └─────────────────┘                           │   │
│  └──────────────────────────────────────────────────┘   │
│                                                         │
│  ┌──────────────────────────────────────────────────┐   │
│  │  PersistentVolumes                               │   │
│  │  - codex-checkpoints (50Gi)                     │   │
│  │  - codex-logs (20Gi)                           │   │
│  │  - codex-artifacts (100Gi)                     │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Cluster Setup

```bash
# Kubernetes version 1.24+
kubectl version --client

# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Verify RBAC is enabled
kubectl api-versions | grep rbac
```

### Required Tools

```bash
# kubectl: Kubernetes CLI
kubectl version

# helm: Package manager (v3.0+)
helm version

# docker: Container runtime
docker version

# kustomize: Template management (optional)
kustomize version
```

### Cluster Resources

```bash
# Check available resources
kubectl top nodes
kubectl describe nodes

# Verify storage classes
kubectl get storageclasses

# Check available compute
kubectl get nodes -o json | jq '.items[].status.capacity'
```

---

## Kubernetes Manifests

### Namespace Setup

```yaml
# codex-namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: codex-ml
  labels:
    app: codex
    environment: production
```

**Create namespace**:
```bash
kubectl apply -f codex-namespace.yaml
```

### ConfigMap: Application Configuration

```yaml
# codex-configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: codex-config
  namespace: codex-ml
data:
  CODEX_ENV: "production"
  API_HOST: "0.0.0.0"
  API_PORT: "8000"
  API_WORKERS: "4"
  LOG_LEVEL: "INFO"
  ENABLE_METRICS: "true"
  BATCH_SIZE: "32"
  MODEL_DEVICE: "cuda"
  
  # Hydra configuration template
  hydra_config.yaml: |
    defaults:
      - _self_
    
    model:
      name: gpt2
      device: cuda
    
    training:
      batch_size: 32
      learning_rate: 1.0e-4
      num_epochs: 3
    
    data:
      path: /data/train
      preprocessing:
        max_length: 512
```

### Secret: Sensitive Data

```yaml
# codex-secret.yaml (encrypted in production)
apiVersion: v1
kind: Secret
metadata:
  name: codex-secrets
  namespace: codex-ml
type: Opaque
stringData:
  API_KEY: "your-api-key-here"
  DATABASE_PASSWORD: "secure-password"
  WANDB_API_KEY: "wandb-api-key"
  MLFLOW_TRACKING_URI: "******postgres:5432/mlflow"
```

**Create secret safely**:
```bash
# Using kubectl create secret
kubectl create secret generic codex-secrets \
  --from-literal=API_KEY="$(openssl rand -base64 32)" \
  --from-literal=DATABASE_PASSWORD="$(openssl rand -base64 32)" \
  -n codex-ml

# Or from file (pre-encrypted)
kubectl create secret generic codex-secrets \
  --from-file=.env.production \
  -n codex-ml
```

### Deployment: API Service

```yaml
# codex-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-api
  namespace: codex-ml
  labels:
    app: codex-api
    version: v1
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  
  selector:
    matchLabels:
      app: codex-api
  
  template:
    metadata:
      labels:
        app: codex-api
        version: v1
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8000"
        prometheus.io/path: "/metrics"
    
    spec:
      serviceAccountName: codex-sa
      
      # Security context for pod
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 1000
      
      # Init container for setup
      initContainers:
      - name: init-setup
        image: ghcr.io/aries-serpent/codex-ml:latest
        command: ['python', '-m', 'src.codex_ml.cli', 'init']
        envFrom:
        - configMapRef:
            name: codex-config
      
      containers:
      - name: codex-api
        image: ghcr.io/aries-serpent/codex-ml:latest
        imagePullPolicy: IfNotPresent
        
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        
        # Environment configuration
        envFrom:
        - configMapRef:
            name: codex-config
        - secretRef:
            name: codex-secrets
        
        # Environment variables
        env:
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: POD_NAMESPACE
          valueFrom:
            fieldRef:
              fieldPath: metadata.namespace
        - name: POD_IP
          valueFrom:
            fieldRef:
              fieldPath: status.podIP
        
        # Resource limits
        resources:
          requests:
            cpu: "2"
            memory: "4Gi"
          limits:
            cpu: "4"
            memory: "8Gi"
        
        # Liveness probe: restart if unhealthy
        livenessProbe:
          httpGet:
            path: /health
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Readiness probe: remove from service if not ready
        readinessProbe:
          httpGet:
            path: /ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        
        # Startup probe: allow time for initialization
        startupProbe:
          httpGet:
            path: /health
            port: http
          failureThreshold: 30
          periodSeconds: 10
        
        # Volume mounts
        volumeMounts:
        - name: config
          mountPath: /app/config
          readOnly: true
        - name: logs
          mountPath: /app/logs
        - name: tmp
          mountPath: /tmp
      
      # Volumes
      volumes:
      - name: config
        configMap:
          name: codex-config
      - name: logs
        emptyDir: {}
      - name: tmp
        emptyDir: {}
      
      # Pod affinity
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
          - weight: 100
            podAffinityTerm:
              labelSelector:
                matchExpressions:
                - key: app
                  operator: In
                  values:
                  - codex-api
              topologyKey: kubernetes.io/hostname
      
      # Tolerations for node taints
      tolerations:
      - key: "workload"
        operator: "Equal"
        value: "ml"
        effect: "NoSchedule"
```

### Service: Internal Networking

```yaml
# codex-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: codex-api
  namespace: codex-ml
  labels:
    app: codex-api
spec:
  type: ClusterIP
  ports:
  - port: 8000
    targetPort: http
    protocol: TCP
    name: http
  selector:
    app: codex-api
  sessionAffinity: ClientIP
  sessionAffinityConfig:
    clientIP:
      timeoutSeconds: 10800
```

---

## Helm Chart Configuration

### Helm Chart Structure

```
codex-ml-chart/
├── Chart.yaml
├── values.yaml
├── values-dev.yaml
├── values-prod.yaml
├── templates/
│   ├── namespace.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── pvc.yaml
│   ├── networkpolicy.yaml
│   ├── serviceaccount.yaml
│   └── NOTES.txt
└── README.md
```

### Chart.yaml

```yaml
apiVersion: v2
name: codex-ml
description: Codex ML ML framework for production
type: application
version: 1.0.0
appVersion: "0.1.0"
home: https://github.com/Aries-Serpent/_codex_
sources:
  - https://github.com/Aries-Serpent/_codex_
maintainers:
  - name: Aries-Serpent
    email: team@example.com
```

### values.yaml (Default)

```yaml
replicaCount: 3

image:
  repository: ghcr.io/aries-serpent/codex-ml
  pullPolicy: IfNotPresent
  tag: "latest"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000

securityContext:
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true
  runAsNonRoot: true

service:
  type: ClusterIP
  port: 8000
  targetPort: 8000

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
  hosts:
    - host: "codex-ml.example.com"
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: codex-ml-tls
      hosts:
        - codex-ml.example.com

resources:
  limits:
    cpu: 4
    memory: 8Gi
  requests:
    cpu: 2
    memory: 4Gi

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

persistence:
  enabled: true
  storageClass: "fast-ssd"
  accessMode: ReadWriteOnce
  size: 50Gi

monitoring:
  enabled: true
  serviceMonitor:
    enabled: true
    interval: 30s
```

### values-prod.yaml (Production Overrides)

```yaml
replicaCount: 5

image:
  tag: "v0.1.0"  # Pin to specific version in production

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  tls:
    - secretName: codex-ml-prod-tls
      hosts:
        - codex-ml.prod.example.com

resources:
  limits:
    cpu: 8
    memory: 16Gi
  requests:
    cpu: 4
    memory: 8Gi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 75

persistence:
  size: 200Gi
  storageClass: "premium-rwo"
```

### Helm Installation

```bash
# Add Helm repository
helm repo add codex https://charts.example.com
helm repo update

# Install chart (development)
helm install codex-ml codex/codex-ml \
  --namespace codex-ml \
  --create-namespace \
  --values values.yaml \
  --values values-dev.yaml

# Install chart (production)
helm install codex-ml codex/codex-ml \
  --namespace codex-ml-prod \
  --create-namespace \
  --values values.yaml \
  --values values-prod.yaml

# Upgrade chart
helm upgrade codex-ml codex/codex-ml \
  --values values.yaml

# Rollback to previous version
helm rollback codex-ml 1
```

---

## StatefulSet Deployment

### Training StatefulSet

```yaml
# codex-training-statefulset.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: codex-training
  namespace: codex-ml
spec:
  serviceName: codex-training
  replicas: 1
  
  selector:
    matchLabels:
      app: codex-training
  
  template:
    metadata:
      labels:
        app: codex-training
    
    spec:
      serviceAccountName: codex-sa
      
      containers:
      - name: training
        image: ghcr.io/aries-serpent/codex-ml:latest
        
        # GPU support
        resources:
          requests:
            nvidia.com/gpu: 1
          limits:
            nvidia.com/gpu: 1
            cpu: "8"
            memory: "16Gi"
        
        # Volume mounts for persistent storage
        volumeMounts:
        - name: checkpoints
          mountPath: /app/checkpoints
        - name: data
          mountPath: /app/data
        - name: logs
          mountPath: /app/logs
  
  # PersistentVolumeClaim templates
  volumeClaimTemplates:
  - metadata:
      name: checkpoints
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "fast-ssd"
      resources:
        requests:
          storage: 50Gi
  
  - metadata:
      name: data
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "standard"
      resources:
        requests:
          storage: 100Gi
  
  - metadata:
      name: logs
    spec:
      accessModes: [ "ReadWriteOnce" ]
      storageClassName: "standard"
      resources:
        requests:
          storage: 20Gi
```

---

## Ingress Configuration

### Nginx Ingress

```yaml
# codex-ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: codex-ingress
  namespace: codex-ml
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - codex-ml.example.com
    - api.codex-ml.example.com
    secretName: codex-tls
  
  rules:
  - host: codex-ml.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: codex-api
            port:
              number: 8000
  
  - host: api.codex-ml.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: codex-api
            port:
              number: 8000
```

---

## Resource Limits & Requests

### Node Resource Planning

| Component | CPU Request | Memory Request | CPU Limit | Memory Limit |
|-----------|------------|----------------|-----------|--------------|
| API Pod | 2 | 4Gi | 4 | 8Gi |
| Training Pod | 4 | 8Gi | 8 | 16Gi |
| Worker Pod | 1 | 2Gi | 2 | 4Gi |

### Resource Quota per Namespace

```yaml
# codex-resourcequota.yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: codex-quota
  namespace: codex-ml
spec:
  hard:
    requests.cpu: "50"
    requests.memory: "100Gi"
    limits.cpu: "100"
    limits.memory: "200Gi"
    pods: "100"
    persistentvolumeclaims: "10"
```

---

## Horizontal Pod Autoscaler

### CPU-Based Autoscaling

```yaml
# codex-hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: codex-api-hpa
  namespace: codex-ml
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codex-api
  
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
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 15
      selectPolicy: Max
    
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

---

## Monitoring & Observability

### ServiceMonitor for Prometheus

```yaml
# codex-servicemonitor.yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: codex-monitor
  namespace: codex-ml
spec:
  selector:
    matchLabels:
      app: codex-api
  
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
```

### PrometheusRule for Alerts

```yaml
# codex-prometheusrule.yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: codex-alerts
  namespace: codex-ml
spec:
  groups:
  - name: codex.rules
    interval: 30s
    rules:
    - alert: CodexHighErrorRate
      expr: rate(codex_requests_total{status="500"}[5m]) > 0.05
      for: 5m
      annotations:
        summary: "Codex high error rate"
    
    - alert: CodexPodCrashing
      expr: rate(kube_pod_container_status_restarts_total{pod=~"codex-.*"}[1h]) > 0
      for: 5m
      annotations:
        summary: "Codex pod restarting"
```

---

## Security Policies

### NetworkPolicy: Ingress & Egress

```yaml
# codex-networkpolicy.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: codex-netpolicy
  namespace: codex-ml
spec:
  podSelector:
    matchLabels:
      app: codex-api
  
  policyTypes:
  - Ingress
  - Egress
  
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
    ports:
    - protocol: TCP
      port: 8000
  
  egress:
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53      # DNS
    - protocol: UDP
      port: 53      # DNS
    - protocol: TCP
      port: 443     # HTTPS
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### PodSecurityPolicy

```yaml
# codex-podsecpolicy.yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: codex-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
  - ALL
  volumes:
  - 'configMap'
  - 'emptyDir'
  - 'projected'
  - 'secret'
  - 'downwardAPI'
  - 'persistentVolumeClaim'
  hostNetwork: false
  hostIPC: false
  hostPID: false
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'MustRunAs'
    seLinuxOptions:
      level: "s0:c123,c456"
  readOnlyRootFilesystem: false
```

---

## Troubleshooting

### Pod Not Starting

```bash
# Check pod status
kubectl describe pod <pod-name> -n codex-ml

# Check pod logs
kubectl logs <pod-name> -n codex-ml

# Check previous logs (if crashed)
kubectl logs <pod-name> --previous -n codex-ml

# Debug with shell
kubectl exec -it <pod-name> -- /bin/bash -n codex-ml
```

### Service Unreachable

```bash
# Check service endpoints
kubectl get endpoints codex-api -n codex-ml

# Check service DNS
kubectl run -it --rm debug --image=busybox -- sh
nslookup codex-api.codex-ml.svc.cluster.local

# Test connectivity between pods
kubectl run -it --rm debug --image=nicolaka/netshoot -- bash
curl codex-api:8000/health
```

### Resource Constraints

```bash
# Check node resources
kubectl top nodes
kubectl describe node <node-name>

# Check pod resource usage
kubectl top pod -n codex-ml
kubectl describe pod <pod-name> -n codex-ml

# Check resource quotas
kubectl describe resourcequota codex-quota -n codex-ml
```

---

## Production Checklist

- [ ] Kubernetes cluster version 1.24+
- [ ] All images scanned for vulnerabilities
- [ ] Secret management configured (Sealed Secrets or HashiCorp Vault)
- [ ] RBAC policies applied
- [ ] NetworkPolicies enforced
- [ ] PodSecurityPolicies applied
- [ ] Resource requests and limits set
- [ ] HPA configured and tested
- [ ] Monitoring and alerting enabled
- [ ] Persistent storage configured and tested
- [ ] Ingress TLS certificates configured
- [ ] Backup and disaster recovery plan documented
- [ ] Load testing completed
- [ ] Failover procedures tested

---

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)
- [OWASP Kubernetes Security](https://cheatsheetseries.owasp.org/cheatsheets/Kubernetes_Security_Cheat_Sheet.html)
