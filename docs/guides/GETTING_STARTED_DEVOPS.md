# Getting Started Guide for DevOps Engineers

**Last Updated:** 2026-07-08  
**Target Audience:** DevOps, SRE, infrastructure engineers, platform teams  
**Estimated Time:** 25-30 minutes to production infrastructure

## 🎯 Your Goal

Set up, manage, and scale Codex ML infrastructure with enterprise-grade reliability, automation, and disaster recovery. This guide covers infrastructure-as-code, container orchestration, and operational excellence.

---

## Phase 1: Infrastructure Planning (5 minutes)

### Architecture Decision Matrix

**Choose Your Setup:**

| Scenario | Recommended | Effort | Cost |
|----------|------------|--------|------|
| **Local Development** | Docker Compose | Low | Free |
| **Team Development** | Kubernetes (Kind) | Medium | Free |
| **Staging Environment** | EKS/GKE/AKS | High | $200-500/mo |
| **Production** | Multi-AZ Kubernetes | Very High | $1000+/mo |

### System Requirements

**Minimum:**
- 8 vCPU, 16 GB RAM, 100 GB SSD
- Linux (Ubuntu 20.04+, RHEL 8+) or macOS
- Docker 20.10+, Kubernetes 1.24+

**Recommended:**
- 32+ vCPU, 64 GB RAM, 500 GB SSD
- Multiple availability zones
- GPU nodes for inference (A100/H100)
- Dedicated database (managed PostgreSQL)
- Distributed storage (EBS, Persistent Volumes)

---

## Phase 2: Local Development Setup (5 minutes)

### Docker Compose (All-in-One)

Create `docker-compose.yml`:

```yaml
version: '3.9'

services:
  # Codex ML API Server
  api:
    image: codex-ml:v0.1.0
    container_name: codex-ml-api
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./config:/app/config
      - ./data:/app/data
    environment:
      - LOG_LEVEL=INFO
      - CUDA_VISIBLE_DEVICES=0
      - MODEL_CACHE_DIR=/app/models
    depends_on:
      - postgres
      - redis
    networks:
      - codex-network

  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: codex-postgres
    environment:
      POSTGRES_DB: codex_ml
      POSTGRES_USER: codex
      POSTGRES_PASSWORD: ${DB_PASSWORD:-changeme}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - codex-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U codex"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: codex-redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - codex-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # MLflow Tracking Server (optional)
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    container_name: codex-mlflow
    ports:
      - "5000:5000"
    volumes:
      - mlflow_data:/mlflow
    command: mlflow server --host 0.0.0.0 --backend-store-uri sqlite:////mlflow/mlflow.db
    networks:
      - codex-network

  # Prometheus Monitoring
  prometheus:
    image: prom/prometheus:latest
    container_name: codex-prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - codex-network

  # Grafana Dashboards
  grafana:
    image: grafana/grafana:latest
    container_name: codex-grafana
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/dashboards:/etc/grafana/provisioning/dashboards
    depends_on:
      - prometheus
    networks:
      - codex-network

volumes:
  postgres_data:
  redis_data:
  mlflow_data:
  prometheus_data:
  grafana_data:

networks:
  codex-network:
    driver: bridge
```

**Launch:**

```bash
# Create .env file
cat > .env << EOF
DB_PASSWORD=secure_password_here
GRAFANA_PASSWORD=your_grafana_password
EOF

# Start all services
docker-compose up -d

# Verify
docker-compose ps
docker-compose logs -f api

# Access services
# API: http://localhost:8000
# MLflow: http://localhost:5000
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/password)
```

---

## Phase 3: Kubernetes Deployment (10 minutes)

### Local Kubernetes Cluster (Kind)

```bash
# Install Kind
curl -Lo ./kind https://kind.sigs.k8s.io/dl/latest/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind

# Create cluster
kind create cluster \
  --name codex-ml-dev \
  --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: codex-ml-dev
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
EOF

# Verify
kubectl cluster-info
kubectl get nodes
```

### Deploy Codex ML on Kubernetes

Create `k8s/codex-ml-deployment.yaml`:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: codex-ml

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: codex-ml-config
  namespace: codex-ml
data:
  app.yaml: |
    experiment_name: kubernetes-deployment
    log_level: INFO
    
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codex-ml-api
  namespace: codex-ml
spec:
  replicas: 3
  selector:
    matchLabels:
      app: codex-ml-api
  template:
    metadata:
      labels:
        app: codex-ml-api
        version: v0.1.0
    spec:
      containers:
      - name: api
        image: codex-ml:v0.1.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 8000
          name: http
        
        # Resource requests/limits
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        
        # Liveness and readiness probes
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
        
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
        
        # Environment variables
        env:
        - name: LOG_LEVEL
          value: "INFO"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: codex-ml-secrets
              key: database_url
        
        # Volume mounts
        volumeMounts:
        - name: models
          mountPath: /app/models
          readOnly: true
        - name: config
          mountPath: /app/config
          readOnly: true
      
      # Volumes
      volumes:
      - name: models
        emptyDir: {}  # Use PersistentVolume in production
      - name: config
        configMap:
          name: codex-ml-config

---
apiVersion: v1
kind: Service
metadata:
  name: codex-ml-api
  namespace: codex-ml
spec:
  type: LoadBalancer  # Use ClusterIP in production with Ingress
  selector:
    app: codex-ml-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: codex-ml-api-hpa
  namespace: codex-ml
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: codex-ml-api
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

---
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: codex-ml-api-pdb
  namespace: codex-ml
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: codex-ml-api
```

**Deploy:**

```bash
# Create secrets
kubectl create secret generic codex-ml-secrets \
  --from-literal=database_url=******postgres:5432/codex_ml \
  -n codex-ml

# Apply manifests
kubectl apply -f k8s/codex-ml-deployment.yaml

# Verify
kubectl get pods -n codex-ml
kubectl get svc -n codex-ml

# Port-forward for local access
kubectl port-forward -n codex-ml svc/codex-ml-api 8000:80
```

---

## Phase 4: Production Infrastructure (Advanced)

### Multi-Environment Setup

Create `terraform/main.tf`:

```hcl
# AWS Elastic Kubernetes Service
resource "aws_eks_cluster" "codex_ml" {
  name            = "codex-ml-prod"
  role_arn        = aws_iam_role.eks_cluster_role.arn
  version         = "1.27"
  
  vpc_config {
    subnet_ids = concat(
      aws_subnet.private[*].id,
      aws_subnet.public[*].id
    )
  }
}

# Node group for API servers
resource "aws_eks_node_group" "api_servers" {
  cluster_name    = aws_eks_cluster.codex_ml.name
  node_group_name = "api-servers"
  node_role_arn   = aws_iam_role.node_role.arn
  
  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 2
  }
  
  instance_types = ["m5.2xlarge"]  # Production instances
  
  tags = {
    Name = "codex-ml-api"
  }
}

# Node group for GPU inference
resource "aws_eks_node_group" "gpu_inference" {
  cluster_name    = aws_eks_cluster.codex_ml.name
  node_group_name = "gpu-inference"
  node_role_arn   = aws_iam_role.node_role.arn
  
  scaling_config {
    desired_size = 2
    max_size     = 8
    min_size     = 1
  }
  
  instance_types = ["g4dn.2xlarge"]  # GPU instances
  
  tags = {
    Name = "codex-ml-gpu"
  }
}

# RDS PostgreSQL Database
resource "aws_db_instance" "codex_ml" {
  identifier     = "codex-ml-db"
  engine         = "postgres"
  engine_version = "15.2"
  instance_class = "db.r5.2xlarge"
  
  allocated_storage    = 100
  storage_encrypted    = true
  multi_az             = true
  
  db_name  = "codex_ml"
  username = "codex"
  password = random_password.db_password.result
  
  backup_retention_period = 30
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  publicly_accessible = false
  vpc_security_group_ids = [aws_security_group.db.id]
  db_subnet_group_name   = aws_db_subnet_group.default.name
}

# ElastiCache Redis Cluster
resource "aws_elasticache_cluster" "codex_ml" {
  cluster_id           = "codex-ml-redis"
  engine               = "redis"
  node_type           = "cache.r6g.xlarge"
  num_cache_nodes     = 3
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                = 6379
  
  security_group_ids      = [aws_security_group.redis.id]
  subnet_group_name       = aws_elasticache_subnet_group.default.name
  automatic_failover_enabled = true
}

# S3 Bucket for Model Storage
resource "aws_s3_bucket" "models" {
  bucket = "codex-ml-models-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "models" {
  bucket = aws_s3_bucket.models.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
```

**Deploy infrastructure:**

```bash
# Initialize Terraform
terraform init

# Plan changes
terraform plan -out=tfplan

# Apply
terraform apply tfplan

# Get outputs
terraform output kubeconfig > kubeconfig.yaml
export KUBECONFIG=kubeconfig.yaml
kubectl get nodes
```

---

## Phase 5: Monitoring & Observability

### Prometheus Scrape Config

Create `monitoring/prometheus.yml`:

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

alerting:
  alertmanagers:
  - static_configs:
    - targets:
      - localhost:9093

rule_files:
  - 'alert_rules.yml'

scrape_configs:
  # Kubernetes API server
  - job_name: 'kubernetes-apiservers'
    static_configs:
    - targets: ['kubernetes.default.svc']
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

  # Kubelet
  - job_name: 'kubernetes-nodes'
    static_configs:
    - targets: ['localhost:10250']
    scheme: https
    tls_config:
      ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
    bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token

  # Codex ML API
  - job_name: 'codex-ml-api'
    kubernetes_sd_configs:
    - role: pod
      namespaces:
        names:
        - codex-ml
    relabel_configs:
    - source_labels: [__meta_kubernetes_pod_label_app]
      action: keep
      regex: codex-ml-api
```

### Alert Rules

Create `monitoring/alert_rules.yml`:

```yaml
groups:
- name: codex-ml.rules
  interval: 30s
  rules:
  
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    for: 5m
    annotations:
      summary: "High error rate detected"
      description: "Error rate above 5% for {{ $labels.instance }}"
  
  - alert: HighLatency
    expr: histogram_quantile(0.99, http_request_duration_seconds) > 1
    for: 5m
    annotations:
      summary: "High latency detected"
      description: "P99 latency above 1s for {{ $labels.instance }}"
  
  - alert: PodCrashLooping
    expr: rate(kube_pod_container_status_restarts_total[15m]) > 0.1
    for: 5m
    annotations:
      summary: "Pod crash looping"
      description: "{{ $labels.pod }} in {{ $labels.namespace }} is crash looping"
  
  - alert: ModelDrift
    expr: kl_divergence_production_vs_baseline > 0.3
    for: 1h
    annotations:
      summary: "Model drift detected"
      description: "Production predictions diverging from baseline"
```

---

## 📚 Next Steps

- **Helm Charts**: [Helm Deployment](./HELM_DEPLOYMENT.md)
- **GitOps**: [ArgoCD Setup](./GITOPS_SETUP.md)
- **Disaster Recovery**: [DR Planning](../admin/DISASTER_RECOVERY.md)
- **Cost Optimization**: [FinOps Guide](./FINOPS_GUIDE.md)

## 🆘 Getting Help

- **Infrastructure Questions**: [GitHub Discussions](https://github.com/Aries-Serpent/_codex_/discussions?discussions_q=infrastructure)
- **Report Issues**: [Create an Issue](https://github.com/Aries-Serpent/_codex_/issues/new?labels=devops)
- **Join Community**: [Slack #devops Channel](https://slack.codex-ml.com)

---

**Let's build reliable infrastructure! 🛠️**
