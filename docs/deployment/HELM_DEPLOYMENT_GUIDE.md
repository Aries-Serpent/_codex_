# Helm Chart Deployment Guide

**Version**: v0.2.1
**Last Updated:** 2026-07-11

**Last Updated**: 2026-07-08  
**Version**: 1.0  
**Audience**: Kubernetes operators, DevOps engineers, Helm users  
**Environment**: Kubernetes with Helm  
**Tier**: Production-Ready

---

## Overview

This guide covers deploying Codex ML using Helm charts for simplified, templated Kubernetes deployments with environment management.

### Advantages of Helm Deployment

- **Package Management**: Versioned releases with dependencies
- **Templating**: Environment-specific configurations
- **Rollback**: Easy version downgrades
- **Reusability**: Share charts across teams
- **Community**: Large ecosystem of pre-built charts

---

## Prerequisites

### Install Helm

```bash
# Install Helm 3.x
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Verify installation
helm version

# Add common Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Verify repositories
helm repo list
```

### Kubernetes Cluster

```bash
# Verify cluster access
kubectl cluster-info
kubectl get nodes

# Create namespaces
kubectl create namespace codex-ml
kubectl create namespace monitoring
```

---

## Step-by-Step Deployment

### 1. Create Helm Chart Structure

```bash
# Generate new chart
helm create codex-ml

# Or use existing chart from repository
helm pull codex-ml/codex-ml --untar

# Chart structure
codex-ml/
├── Chart.yaml                 # Chart metadata
├── values.yaml               # Default values
├── values-dev.yaml           # Dev environment overrides
├── values-staging.yaml       # Staging environment overrides
├── values-prod.yaml          # Production environment overrides
├── charts/                    # Dependency charts
├── templates/
│   ├── deployment.yaml       # Application deployment
│   ├── service.yaml          # Service definition
│   ├── ingress.yaml          # Ingress configuration
│   ├── configmap.yaml        # Configuration
│   ├── secret.yaml           # Secrets
│   ├── hpa.yaml              # Horizontal Pod Autoscaler
│   ├── pdb.yaml              # Pod Disruption Budget
│   ├── networkpolicy.yaml    # Network policies
│   └── _helpers.tpl          # Template helpers
└── values.schema.json        # Schema validation
```

### 2. Create Chart.yaml

```yaml
# Chart.yaml
apiVersion: v2
name: codex-ml
description: A Helm chart for Codex ML application
type: application
version: 1.0.0
appVersion: 1.0.0
keywords:
  - codex-ml
  - machine-learning
  - api
home: https://github.com/Aries-Serpent/codex
icon: https://example.com/logo.png
sources:
  - https://github.com/Aries-Serpent/codex
maintainers:
  - name: DevOps Team
    email: devops@example.com
dependencies:
  - name: postgresql
    version: "11.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: postgresql.enabled
  - name: redis
    version: "17.x.x"
    repository: https://charts.bitnami.com/bitnami
    condition: redis.enabled
```

### 3. Create Base Values

```yaml
# values.yaml
replicaCount: 3

image:
  repository: registry.example.com/codex-ml
  pullPolicy: IfNotPresent
  tag: "1.0.0"

imagePullSecrets: []
nameOverride: ""
fullnameOverride: "codex-ml"

serviceAccount:
  create: true
  annotations:
    iam.gke.io/gcp-service-account: codex-ml@project.iam.gserviceaccount.com
  name: ""

podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"

podSecurityContext:
  fsGroup: 1000
  runAsNonRoot: true
  runAsUser: 1000
  seccompProfile:
    type: RuntimeDefault

securityContext:
  allowPrivilegeEscalation: false
  capabilities:
    drop:
    - ALL
  readOnlyRootFilesystem: true

service:
  type: ClusterIP
  port: 80
  targetPort: 8000
  annotations: {}

ingress:
  enabled: true
  className: "nginx"
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/rate-limit: "100"
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.example.com

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1000m
    memory: 2Gi

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70
  targetMemoryUtilizationPercentage: 80

nodeSelector: {}

tolerations: []

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
            - codex-ml
        topologyKey: kubernetes.io/hostname

livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2

env:
  - name: ENVIRONMENT
    value: "production"
  - name: LOG_LEVEL
    value: "INFO"
  - name: NUM_WORKERS
    value: "4"

envFrom:
  - configMapRef:
      name: codex-config
  - secretRef:
      name: codex-secrets

volumeMounts:
  - name: tmp
    mountPath: /tmp
  - name: cache
    mountPath: /var/cache

volumes:
  - name: tmp
    emptyDir:
      sizeLimit: 1Gi
  - name: cache
    emptyDir:
      sizeLimit: 2Gi

postgresql:
  enabled: true
  auth:
    username: codex_admin
    password: "changeme"
    database: codex
  primary:
    persistence:
      enabled: true
      size: 100Gi
    resources:
      requests:
        cpu: 1000m
        memory: 2Gi

redis:
  enabled: true
  auth:
    enabled: true
    password: "changeme"
  master:
    persistence:
      enabled: true
      size: 20Gi
  replica:
    replicaCount: 1
    persistence:
      enabled: true
```

### 4. Create Environment-Specific Values

```yaml
# values-prod.yaml
replicaCount: 5

image:
  tag: "1.0.0"

resources:
  limits:
    cpu: 2000m
    memory: 4Gi
  requests:
    cpu: 1500m
    memory: 3Gi

autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
  targetCPUUtilizationPercentage: 60

env:
  - name: ENVIRONMENT
    value: "production"
  - name: LOG_LEVEL
    value: "WARN"
  - name: NUM_WORKERS
    value: "8"

postgresql:
  primary:
    persistence:
      size: 500Gi
  replica:
    replicaCount: 2

redis:
  master:
    persistence:
      size: 100Gi
  replica:
    replicaCount: 2

ingress:
  enabled: true
  hosts:
    - host: api.example.com
```

### 5. Create Deployment Template

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "codex-ml.fullname" . }}
  labels:
    {{- include "codex-ml.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "codex-ml.selectorLabels" . | nindent 6 }}
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
        {{- with .Values.podAnnotations }}
        {{- toYaml . | nindent 8 }}
        {{- end }}
      labels:
        {{- include "codex-ml.selectorLabels" . | nindent 8 }}
    spec:
      {{- with .Values.imagePullSecrets }}
      imagePullSecrets:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      serviceAccountName: {{ include "codex-ml.serviceAccountName" . }}
      securityContext:
        {{- toYaml .Values.podSecurityContext | nindent 8 }}
      containers:
      - name: {{ .Chart.Name }}
        securityContext:
          {{- toYaml .Values.securityContext | nindent 12 }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 8000
          protocol: TCP
        {{- if .Values.livenessProbe }}
        livenessProbe:
          {{- toYaml .Values.livenessProbe | nindent 12 }}
        {{- end }}
        {{- if .Values.readinessProbe }}
        readinessProbe:
          {{- toYaml .Values.readinessProbe | nindent 12 }}
        {{- end }}
        resources:
          {{- toYaml .Values.resources | nindent 12 }}
        {{- with .Values.env }}
        env:
          {{- toYaml . | nindent 12 }}
        {{- end }}
        {{- with .Values.envFrom }}
        envFrom:
          {{- toYaml . | nindent 12 }}
        {{- end }}
        {{- with .Values.volumeMounts }}
        volumeMounts:
          {{- toYaml . | nindent 12 }}
        {{- end }}
      {{- with .Values.volumes }}
      volumes:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.nodeSelector }}
      nodeSelector:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.affinity }}
      affinity:
        {{- toYaml . | nindent 8 }}
      {{- end }}
      {{- with .Values.tolerations }}
      tolerations:
        {{- toYaml . | nindent 8 }}
      {{- end }}
```

### 6. Install with Helm

```bash
# Add chart repository
helm repo add codex https://charts.example.com
helm repo update

# Install in dev environment
helm install codex-ml codex/codex-ml \
  --namespace codex-ml \
  --values values-dev.yaml

# Install in production with overrides
helm install codex-ml codex/codex-ml \
  --namespace codex-ml \
  --values values-prod.yaml \
  --set postgresql.auth.****** rand -base64 32) \
  --set redis.auth.****** rand -base64 32)

# Verify installation
helm status codex-ml -n codex-ml
helm get values codex-ml -n codex-ml
```

### 7. Upgrade Deployment

```bash
# Upgrade to new version
helm upgrade codex-ml codex/codex-ml \
  --namespace codex-ml \
  --values values-prod.yaml \
  --set image.tag="1.0.1"

# Watch upgrade progress
kubectl rollout status deployment/codex-ml -n codex-ml

# Check revision history
helm history codex-ml -n codex-ml

# Rollback to previous version
helm rollback codex-ml 1 -n codex-ml
```

### 8. Manage Dependencies

```bash
# Update dependency charts
helm dependency update

# Install/update dependencies
helm dependency install

# Verify dependencies
helm dependency list

# Example: Override dependency values
helm install codex-ml ./codex-ml \
  --values values-prod.yaml \
  --set postgresql.auth.****** \
  --set postgresql.primary.resources.requests.cpu=2000m
```

---

## Helm Chart Testing

```bash
# Lint chart for errors
helm lint ./codex-ml

# Validate templates
helm template codex-ml ./codex-ml \
  --values values-prod.yaml \
  --debug

# Dry-run before installation
helm install codex-ml ./codex-ml \
  --namespace codex-ml \
  --values values-prod.yaml \
  --dry-run \
  --debug

# Install in test environment
helm install codex-ml ./codex-ml \
  --namespace test \
  --values values-test.yaml

# Run chart tests
helm test codex-ml -n codex-ml
```

---

## Helm Chart Repositories

```bash
# Push chart to repository
helm package ./codex-ml
helm repo index --url https://charts.example.com .

# Or use ChartMuseum
curl --data-binary "@codex-ml-1.0.0.tgz" \
  http://chartmuseum.example.com/api/charts

# Publish to Artifact Hub
# See https://artifacthub.io/docs/

# Search for charts
helm search repo codex-ml
helm search hub codex-ml
```

---

## Best Practices

### Chart Development

```yaml
# Use semantic versioning
version: 1.0.0  # Major.Minor.Patch

# Validate schema
values.schema.json

# Document values
# Add comments explaining each value

# Use helpers for consistency
_helpers.tpl templates
```

### Production Deployment

```bash
# Version control your values files
git commit values-prod.yaml

# Use separate namespaces per environment
kubectl create namespace codex-ml-prod

# Implement resource quotas per namespace
kubectl apply -f resource-quota.yaml -n codex-ml-prod

# Monitor Helm releases
helm list -A
helm status <release> -n <namespace>

# Document deployment decisions
# Keep runbooks for Helm operations
```

### Security

```bash
# Use secrets for sensitive data
kubectl create secret generic codex-secrets \
  --from-literal=db-****** \
  -n codex-ml

# Restrict access to values files
git-crypt lock values-prod.yaml

# Sign Helm charts
helm package --sign ./codex-ml
helm verify ./codex-ml-1.0.0.tgz

# Use networkpolicies
# Include in chart templates
```

---

## Production Readiness Checklist

- [ ] Chart passes linting (`helm lint`)
- [ ] Templates render correctly (`helm template`)
- [ ] Dry-run successful (`helm install --dry-run`)
- [ ] Dependencies updated and tested
- [ ] Values files documented and version controlled
- [ ] Security scanning passed
- [ ] Load testing completed
- [ ] Rollback tested
- [ ] Monitoring dashboards created
- [ ] Alert rules configured
- [ ] Runbooks documented
- [ ] Team trained on Helm operations
- [ ] Chart repository configured
- [ ] Release notes prepared

---

**Next Steps**:
1. Package and push chart to repository
2. Document Helm operations in runbooks
3. Set up automated testing in CI/CD
4. Train team on Helm deployment procedures
5. Monitor releases and collect feedback

