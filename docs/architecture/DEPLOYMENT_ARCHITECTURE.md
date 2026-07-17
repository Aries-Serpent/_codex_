# Deployment Architecture
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated**: 2026-01-20
**Version**: v0.2.1
**Supported Platforms**: Local, Docker, Kubernetes, Cloud

---

## Deployment Architecture Overview

```mermaid
%%{init: {'accessibility': {'title': 'Deployment Architecture<br/>Local Docker Kubernetes Cloud'}, 'theme': 'base'}}%%

graph TB
 subgraph "Local Development"
 LocalDev[" Developer Laptop<br/>• Python venv<br/>• Local SQLite DB<br/>• Local Redis cache"]
 LocalTools[" Local Tools<br/>• pip/conda<br/>• pytest<br/>• tensorboard"]
 end

 subgraph "Docker Containerized"
 BuildStage[" Build Stage<br/>• Dockerfile multi-stage<br/>• Install dependencies<br/>• Compile wheels"]
 RuntimeStage[" Runtime Stage<br/>• Minimal base image<br/>• Python slim<br/>• Security scanning"]
 Registry[" Container Registry<br/>• GitHub Container Reg<br/>• Version tags<br/>• Signature validation"]
 end

 subgraph "Kubernetes Orchestration"
 K8sCluster[" K8s Cluster<br/>• Pod scheduling<br/>• Resource management<br/>• Auto-scaling"]
 K8sServices[" K8s Services<br/>• ClusterIP services<br/>• LoadBalancer<br/>• Ingress controller"]
 K8sStorage[" K8s Storage<br/>• PersistentVolumes<br/>• StatefulSets<br/>• Database pods"]
 K8sNet[" K8s Network<br/>• NetworkPolicies<br/>• Pod-to-Pod<br/>• Egress rules"]
 end

 subgraph "Cloud Deployment"
 CloudCompute[" Cloud Compute<br/>• AWS EC2/Lambda<br/>• GCP Compute Engine<br/>• Azure Container Inst."]
 CloudStorage[" Cloud Storage<br/>• S3/GCS/Azure Blob<br/>• Model versioning<br/>• Data persistence"]
 CloudDB[" Managed Database<br/>• AWS RDS<br/>• GCP Cloud SQL<br/>• Azure Database"]
 CloudMonitor[" Cloud Monitoring<br/>• CloudWatch/Stackdriver<br/>• Log aggregation<br/>• Metrics/Traces"]
 end

 subgraph "CI/CD Pipeline"
 Git[" Git Repository<br/>• Source code<br/>• Commit triggers<br/>• Branch protection"]
 GHActions[" GitHub Actions<br/>• Build jobs<br/>• Test jobs<br/>• Deploy jobs"]
 Tests[" Automated Tests<br/>• Unit tests<br/>• Integration tests<br/>• E2E tests"]
 Publish[" Publish<br/>• Push to registry<br/>• Create release<br/>• Tag version"]
 end

 %% Deployment flow
 LocalDev --> LocalTools

 LocalTools -->|"git push"| Git
 
 Git --> GHActions

 GHActions -->|"Run tests"| Tests

 Tests -->|"Build image"| BuildStage

 BuildStage --> RuntimeStage

 RuntimeStage -->|"Push image"| Registry
 
 Registry -->|"Pull image"| K8sCluster

 Registry -->|"Pull image"| CloudCompute
 
 K8sCluster --> K8sServices

 K8sCluster --> K8sStorage

 K8sCluster --> K8sNet
 
 K8sStorage -.connects.-> CloudDB
 K8sServices -.mounts.-> CloudStorage
 
 CloudCompute --> CloudStorage

 CloudCompute --> CloudDB

 CloudCompute --> CloudMonitor
 
 Publish -->|"Release tag"| Registry
 
 %% Monitoring
 K8sCluster -.metrics.-> CloudMonitor
 LocalDev -.logs.-> CloudMonitor
 
 %% Styling
 style LocalDev fill:#e0f2fe,stroke:#0284c7,stroke-width:2px
 style LocalTools fill:#e0f2fe,stroke:#0284c7,stroke-width:2px,color:#000
 
 style BuildStage fill:#fef3c7,stroke:#d97706,stroke-width:2px
 style RuntimeStage fill:#fef3c7,stroke:#d97706,stroke-width:2px
 style Registry fill:#fef3c7,stroke:#d97706,stroke-width:2px
 
 style K8sCluster fill:#dcfce7,stroke:#16a34a,stroke-width:2px
 style K8sServices fill:#dcfce7,stroke:#16a34a,stroke-width:2px
 style K8sStorage fill:#dcfce7,stroke:#16a34a,stroke-width:2px
 style K8sNet fill:#dcfce7,stroke:#16a34a,stroke-width:2px
 
 style CloudCompute fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px
 style CloudStorage fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px
 style CloudDB fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px
 style CloudMonitor fill:#f3e8ff,stroke:#7c3aed,stroke-width:2px
 
 style Git fill:#fce7f3,stroke:#db2777,stroke-width:2px
 style GHActions fill:#fce7f3,stroke:#db2777,stroke-width:2px
 style Tests fill:#fce7f3,stroke:#db2777,stroke-width:2px
 style Publish fill:#fce7f3,stroke:#db2777,stroke-width:2px
```

---

## Deployment Targets

### Local Development
**Use Case**: Development, debugging, rapid iteration

**Setup**:
```bash
git clone <repo>
cd _codex_
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
```

**Environment**:
- Python virtual environment
- Local SQLite database
- Optional: Redis for caching
- Test runner: pytest
- Monitoring: TensorBoard

**Command**:
```bash
codex train --config configs/dev.yaml
```

---

### Docker Containerized
**Use Case**: Consistent environments, CI/CD, Kubernetes

**Build Process**:
```dockerfile
# Stage 1: Build
FROM python:3.11-slim as builder
WORKDIR /build
COPY requirements*.txt .
RUN pip install --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
COPY --from=builder /root/.local /root/.local
COPY . /app
WORKDIR /app
ENV PATH=/root/.local/bin:$PATH
CMD ["codex", "serve"]
```

**Registry**:
- GitHub Container Registry (ghcr.io)
- Version tags: `v0.2.1`, `latest`, `main`
- Signature validation: Cosign

**Commands**:
```bash
docker build -t codex:latest .
docker run -p 8000:8000 codex:latest
docker push ghcr.io/aries-serpent/codex:latest
```

---

### Kubernetes Orchestration
**Use Case**: Production scaling, high availability

**Manifest Structure**:
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
 name: codex-api
spec:
 replicas: 3
 selector:
 matchLabels:
 app: codex-api
 template:
 metadata:
 labels:
 app: codex-api
 spec:
 containers:
 - name: codex
 image: ghcr.io/aries-serpent/codex:v0.2.1
 ports:
 - containerPort: 8000
 env:
 - name: CONFIG_FILE
 value: /etc/config/config.yaml
 resources:
 requests:
 cpu: 2
 memory: 8Gi
 limits:
 cpu: 4
 memory: 16Gi
 livenessProbe:
 httpGet:
 path: /health
 port: 8000
 initialDelaySeconds: 30
 periodSeconds: 10
---
# service.yaml
apiVersion: v1
kind: Service
metadata:
 name: codex-api
spec:
 type: LoadBalancer
 selector:
 app: codex-api
 ports:
 - protocol: TCP
 port: 80
 targetPort: 8000
---
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
 name: codex-ingress
spec:
 ingressClassName: nginx
 rules:
 - host: api.codex.example.com
 http:
 paths:
 - path: /
 pathType: Prefix
 backend:
 service:
 name: codex-api
 port:
 number: 80
```

**Operations**:
```bash
kubectl apply -f k8s/
kubectl get pods
kubectl logs -f deployment/codex-api
kubectl scale deployment codex-api --replicas=5
```

---

### Cloud Deployment
**Use Case**: Fully managed, auto-scaling, enterprise

**AWS Deployment**:
```bash
# ECS on Fargate
aws ecs create-service \
 --cluster production \
 --service-name codex \
 --task-definition codex:1 \
 --desired-count 3 \
 --launch-type FARGATE

# Or Lambda for serverless
aws lambda create-function \
 --function-name codex-predict \
 --runtime python3.11 \
 --handler app.handler \
 --code S3Bucket=codex-builds,S3Key=lambda.zip
```

**GCP Deployment**:
```bash
gcloud run deploy codex \
 --image gcr.io/project/codex:latest \
 --platform managed \
 --region us-central1 \
 --memory 8Gi \
 --cpu 4
```

**Azure Deployment**:
```bash
az containerapp create \
 --resource-group rg-codex \
 --name codex \
 --image mcr.microsoft.com/codex:latest \
 --cpu 4 \
 --memory 8Gi
```

---

## Storage Configuration

### Local Development
```yaml
database:
 type: sqlite
 path: ./data/codex.db
 
cache:
 type: local
 path: ./cache/
 
storage:
 type: local
 path: ./models/
```

### Docker/K8s
```yaml
database:
 type: postgresql
 host: postgres-service
 port: 5432
 
cache:
 type: redis
 host: redis-service
 port: 6379
 
storage:
 type: s3
 bucket: codex-models
 prefix: v0.2.1/
```

### Cloud
```yaml
database:
 type: postgresql
 host: cloudsql-instance
 ssl: true
 
cache:
 type: redis
 endpoint: elasticache.amazonaws.com
 
storage:
 type: s3
 bucket: prod-models
 prefix: v0.2.1/
 encryption: AES256
```

---

## CI/CD Deployment Pipeline

```
1. Commit to git
 
2. GitHub Actions trigger
 Build (docker build)
 Test (pytest)
 Scan (security checks)
 Push image
 
3. Create release
 Version tag (v0.2.1)
 Release notes
 GitHub release
 
4. Deploy to environments
 Dev cluster (auto)
 Staging cluster (auto)
 Production cluster (manual approval)
 
5. Post-deployment
 Health checks
 Smoke tests
 Metrics validation
 Alert team if issues
```

---

## Environment Comparison

| Aspect | Local | Docker | K8s | Cloud |
|--------|-------|--------|-----|-------|
| **Setup Time** | 5 min | 10 min | 30 min | 15 min |
| **Data Isolation** | None | Volumes | PVCs | Managed |
| **Scaling** | Manual | Manual | Auto | Auto |
| **Monitoring** | Local | Logs | Prometheus | CloudWatch |
| **Cost** | Free | Free | $100-500/mo | $500-2000/mo |
| **HA** | | | | |
| **Security** | Basic | Good | Excellent | Excellent |

---

## Next Steps

- Review the Docker multi-stage build configuration in the repository
- Explore Kubernetes deployment configurations in the `k8s/` directory
- Consider cloud-specific deployment options based on your infrastructure

---

**Note**: This document covers the deployment architecture overview. For detailed deployment guides, refer to the infrastructure documentation in the repository.
