# Infrastructure Components Reference - Codex ML
**Last Updated:** 2026-07-11

**Document Version:** 1.0.0  
**Last Updated: 2026-07-08
**Authority:** Phase 12 WS3 Documentation Lane 8  
**Audience:** Infrastructure Engineers, DevOps, Platform Architects  
**Status:** Technical Specification

---

## Table of Contents

1. [Compute Components](#compute-components)
2. [Storage Components](#storage-components)
3. [Networking Components](#networking-components)
4. [Monitoring Components](#monitoring-components)
5. [Data Services](#data-services)
6. [ML Framework Components](#ml-framework-components)

---

## Compute Components

### Kubernetes Control Plane

**Version:** 1.28.x+ (managed service: EKS, GKE, AKS)

#### Components

| Component | Version | Replicas | Storage | Purpose |
|-----------|---------|----------|---------|---------|
| API Server | 1.28.x | 3 | etcd | REST API for cluster management |
| etcd | 3.5.x | 3 | SSD 50GB | Distributed key-value store |
| Scheduler | 1.28.x | 3 | - | Pod scheduling decisions |
| Controller Manager | 1.28.x | 3 | - | Reconciliation loops |
| CoreDNS | 1.10.x | 2 | - | In-cluster DNS |

**Specifications:**

```yaml
API Server:
  CPU: 4 cores per replica
  Memory: 4Gi per replica
  Max requests/sec: 500
  Audit logging: Enabled
  
etcd:
  CPU: 2 cores per replica
  Memory: 2Gi per replica
  Storage: SSD 50GB per replica
  Backup: Hourly to S3
  
Scheduler:
  CPU: 1 core per replica
  Memory: 1Gi per replica
  Predicates: 10 default
  Extenders: Custom GPU scheduler
```

**Monitoring:**

```
Metrics:
  - apiserver_request_duration_seconds
  - etcd_server_has_leader
  - scheduler_pending_pods
  - controller_manager_queue_depth
  
Alerts:
  - APIServer latency >500ms
  - etcd leader election
  - Pod scheduling stuck
```

### Worker Nodes - GPU

**Instance Type:** AWS p4d.24xlarge / GCP a100-80gb-pcie

#### Specifications

```yaml
Node Profile:
  CPU: 96 vCPU
  Memory: 1152 GB
  GPU: 8x A100 80GB
  GPU Memory: 640GB total
  Network: 400 Gbps
  Storage: 3x 1TB NVMe SSD
  
Cost: ~$200/hour (AWS)

Node Feature Labels:
  gpu: "a100"
  memory: "high"
  training: "enabled"
  compute: "gpu"
```

#### Pod Limits

```yaml
Per Pod:
  GPU: 0-4 (fractional via time-slicing)
  Memory: 64-256Gi
  CPU: 8-48 cores
  
Per Node:
  Total GPU: 8
  Total Memory: 1024Gi (reserve 128Gi)
  Total CPU: 80 (reserve 16)
  Total Pods: 110
```

#### GPU Isolation & Sharing

```
Sharing Options:
  1. Time-slicing (default)
     - Multiple pods share GPU
     - Context switching overhead ~5%
     - Best for interactive/dev workloads
  
  2. GPU sharing via MIG (A100)
     - 7-way GPU partition
     - Guaranteed isolation
     - Best for production serving
  
  3. Full GPU isolation
     - Exclusive GPU per pod
     - Zero sharing overhead
     - Required for high-performance training
```

### Worker Nodes - CPU

**Instance Type:** AWS c6i.4xlarge / GCP c2-standard-16

#### Specifications

```yaml
Node Profile:
  CPU: 16 vCPU
  Memory: 32GB
  Network: 10 Gbps
  Storage: 1x 100GB NVMe
  
Cost: ~$0.68/hour (AWS)
Typical Count: 6-12 nodes

Use Cases:
  - API servers (2 dedicated)
  - Metadata services (2 dedicated)
  - Monitoring stack (2 shared)
  - Batch jobs (flexible)
  - System pods (required)
```

#### Pod Placement

```yaml
Affinity Rules:
  API Servers:
    - Anti-affinity: spread across nodes
    - Require: CPU nodes only
    - Topology: one per node preferred
  
  System Pods:
    - Prefer: CPU nodes (not GPU)
    - Tolerate: GPU nodes
  
  Batch Jobs:
    - Prefer: CPU nodes
    - Can use: spare GPU node capacity
```

### Memory-Optimized Nodes (Optional)

**Instance Type:** AWS r6i.4xlarge / GCP m2-ultramem

```yaml
Use Case: High-memory workloads
  - Redis cluster (if on-premise)
  - Data pre-processing
  - Large batch aggregations

Specifications:
  CPU: 16 vCPU
  Memory: 128GB
  Count: 2-4 nodes
  Cost: ~$2/hour (AWS)
```

---

## Storage Components

### Persistent Volumes

#### EBS-backed Volumes (AWS)

```yaml
Volume Types:
  gp3 (General Purpose):
    - 3 IOPS/GB, 125 MB/s per GB
    - Use: Database, logs
    - Size: 500GB-2TB per volume
    
  io2 (High IOPS):
    - 64 IOPS/GB, 1 GB/s per volume
    - Use: PostgreSQL (critical)
    - Size: 100-500GB
    
  st1 (Throughput):
    - 125 MB/s max, < $0.05/GB
    - Use: Archives, backups
    - Size: > 1TB

Configuration:
  gp3:
    Provisioned IOPS: 3000-16000
    Throughput: 125-1000 MB/s
    Encryption: AES-256 (enabled)
    Replication: Multi-AZ (RDS)
    Snapshots: Hourly, 30-day retention
```

#### Network Attached Storage (NAS)

```yaml
EFS (Elastic File System):
  Type: NFS v4.1
  Performance Mode: General purpose
  Throughput Mode: Bursting
  Use Case: Shared training data cache
  
Storage Details:
  Throughput Burst: 500 MB/s
  Throughput Sustained: 50 MB/s
  Latency: 5-20ms
  Cost: Pay-per-GB (storage + requests)
```

### Object Storage

#### S3 Configuration

```yaml
Buckets:
  codex-ml-artifacts:
    Purpose: Models, checkpoints, outputs
    Versioning: Enabled
    Lifecycle: 
      - Current: No limit
      - Old: Transition to IA after 90 days
      - Archived: Transition to Glacier after 1 year
      - Delete: After 7 years
    
  codex-training-data:
    Purpose: Input datasets
    Versioning: Disabled (immutable after upload)
    Replication: Cross-region to backup region
    Access: Private, no public access
    
  codex-backups:
    Purpose: Database backups, snapshots
    Versioning: Enabled
    MFA Delete: Enabled (safety)
    Retention: Indefinite (compliance)

Performance:
  Request Rate: 3500 PUT, 5500 GET per second per prefix
  Latency: 100-200ms
  Durability: 99.999999999% (11 nines)
```

### Distributed Cache

#### Redis Cluster Configuration

```yaml
Redis Cluster:
  Version: 7.0+
  Mode: Cluster (not standalone)
  Nodes: 6 (3 primary + 3 replica)
  Replication: Synchronous
  
  Per Node:
    Memory: 16GB
    CPU: 2 cores
    Instance: cache.r6g.xlarge
  
  Configuration:
    # Memory management
    maxmemory: 14GB per node
    maxmemory-policy: allkeys-lru
    
    # Persistence
    save: "900 1 300 10 60 10000"
    appendonly: yes
    appendfsync: everysec
    
    # Cluster settings
    cluster-enabled: yes
    cluster-node-timeout: 15000
    
  Monitoring:
    - Connected clients per node
    - Memory eviction rate
    - Replication offset
    - Key space fragmentation
```

#### Use Cases

```
Session/Request Cache:
  - TTL: 1 hour
  - Key pattern: session:*
  - Size limit: 100GB
  
Model Inference Cache:
  - TTL: 24 hours
  - Key pattern: inference:*
  - Size limit: 150GB (LRU eviction)
  
Rate Limiting:
  - TTL: 1 minute (rolling window)
  - Key pattern: ratelimit:*
  - Size limit: 10GB
```

---

## Networking Components

### Ingress Controller

#### NGINX Ingress

```yaml
Configuration:
  Version: 1.7.0+
  Replicas: 3 (one per node)
  
  Service Type: LoadBalancer (cloud LB)
  Annotations:
    - SSL/TLS: Enabled
    - HTTP/2: Enabled
    - Compression: gzip
    - Rate limiting: Per IP
    
  ResourceLimits:
    CPU: 500m per replica
    Memory: 512Mi per replica

TLS Configuration:
  Protocol: TLS 1.2 / 1.3
  Certificates: cert-manager automated renewal
  Cipher Suite:
    - TLS_AES_256_GCM_SHA384
    - TLS_AES_128_GCM_SHA256
    - TLS_CHACHA20_POLY1305_SHA256
```

### Service Mesh (Istio)

```yaml
Istio Components:
  istiod:
    - Control plane
    - Configuration distribution
    - Resource count: 1-3 replicas
  
  Ingress Gateway:
    - Entrypoint for external traffic
    - TLS termination
    - Replicas: 3
  
  Egress Gateway:
    - Outbound traffic control
    - Replicas: 2
  
  Sidecars:
    - Per pod (automatic injection)
    - mTLS enforcement
    - Traffic management

Features Enabled:
  - mTLS: Strict (all pod-to-pod)
  - Rate Limiting: Per service/endpoint
  - Circuit Breaking: Default 100 connections
  - Retry Policy: 3 retries, 1s timeout
```

### Network Policies

```yaml
Default Policy: Deny All (zero-trust)

Allow Rules:
  API Service:
    - Ingress: From IngressGateway (80, 443)
    - Ingress: From Prometheus (9090)
    - Egress: To PostgreSQL (5432)
    - Egress: To Redis (6379)
    - Egress: To S3 (443)
  
  Model Server:
    - Ingress: From API Service (8000)
    - Ingress: From Prometheus (9090)
    - Egress: To S3 (443)
  
  PostgreSQL:
    - Ingress: From API Service (5432)
    - Ingress: From backups (5432)
    - Egress: To backup S3 (443)
  
  Redis:
    - Ingress: From API Service (6379)
    - Ingress: From training (6379)
    - Egress: None

Monitoring:
  - Connection denied count
  - Policy violations
  - Anomalous traffic patterns
```

---

## Monitoring Components

### Prometheus

#### Configuration

```yaml
Prometheus:
  Version: 2.50.x
  Replicas: 2
  Storage: EBS gp3 100GB per replica
  Retention: 15 days (local), 1 year (remote)
  
  Scrape Configuration:
    Interval: 15 seconds
    Timeout: 10 seconds
    
  Remote Write:
    Destination: Cortex/Thanos
    Batching: 1000 samples per request
    Parallelism: 10 concurrent requests

Resource Limits:
  CPU: 2 cores
  Memory: 4Gi
  
Ingestion Rate:
  - 1M+ metrics per minute
  - 500GB+ per month at 15s resolution
```

#### Scrape Targets

```yaml
kubernetes:
  - API server
  - etcd
  - Kubelet
  - Kube-proxy
  - Node exporter (disk, network, system)

Applications:
  - API server (port 9090)
  - Model server (port 8001)
  - Training (port 8002)
  - Databases (port 9187)

Services:
  - NGINX (port 10254)
  - Istio (port 15000)
  - Redis (port 9121)
```

### Grafana

#### Dashboards

```yaml
Key Dashboards:
  1. Cluster Health
     - Node status, resource usage
     - Pod distribution
     - Network throughput
  
  2. Application Metrics
     - API latency, throughput, errors
     - Model inference metrics
     - Training job progress
  
  3. Database Performance
     - Query latency
     - Connection pool usage
     - Replication lag
  
  4. Infrastructure Costs
     - Cloud provider spend
     - Resource utilization
     - Cost per service

Configuration:
  Datasources: Prometheus, Loki, Elasticsearch
  Default Refresh: 30 seconds
  Time Range: 1h (dashboard), customizable
  Alerting: Integrated with AlertManager
```

### AlertManager

```yaml
Routes:
  Critical:
    Receiver: pagerduty + slack + email
    Group Wait: 10 seconds
    Repeat: 15 minutes
  
  Warning:
    Receiver: slack + email
    Group Wait: 30 seconds
    Repeat: 1 hour
  
  Info:
    Receiver: slack channel
    Group Wait: 5 minutes
    Repeat: 6 hours

Notifications:
  PagerDuty:
    Severity: Critical
    Escalation: 5 min auto-escalate
  
  Slack:
    Channel: #incidents
    Mentions: @platform-on-call (critical)
    Rich formatting: Included
  
  Email:
    Recipient: ops-team@company.com
    Digest: 5pm UTC daily summary
```

---

## Data Services

### PostgreSQL

#### High Availability Configuration

```yaml
Setup: Primary + 2 Synchronous Replicas (RDS Multi-AZ)

Primary:
  Instance Type: db.r6i.2xlarge (8 vCPU, 64GB RAM)
  Storage: EBS gp3 500GB, encrypted
  Backup: Automated daily + continuous WAL archiving
  
Replicas:
  Count: 2 (different AZs)
  Sync Mode: Synchronous (guarantee durability)
  Replication Lag: <100ms
  Failover: Automatic on primary failure

Configuration:
  max_connections: 400
  shared_buffers: 16GB
  effective_cache_size: 48GB
  work_mem: 40MB
  
  # Replication
  max_wal_senders: 5
  wal_level: replica
  hot_standby: on
  
  # Performance
  random_page_cost: 1.1  # For SSD
  effective_io_concurrency: 200

Monitoring:
  - Connection count
  - Query latency (p50, p95, p99)
  - Active transactions
  - Replication lag
  - Cache hit ratio
```

#### Backup Strategy

```yaml
Automated Backups:
  - Frequency: Every 6 hours
  - Retention: 30 days
  - Location: S3 + cross-region copy
  - Size: ~50-100GB per backup
  
WAL Archiving:
  - Frequency: Every 5 minutes
  - Retention: 7 days
  - Location: S3 with versioning
  - Use: Point-in-time recovery
  
Backup Verification:
  - Weekly restore test to test environment
  - Monthly full recovery test
  - Monthly archive integrity check
```

### Redis

#### Cluster Configuration

```yaml
Redis Cluster:
  Version: 7.0+
  Nodes: 6 (3 primary + 3 replica)
  
  Node Specs:
    Instance: AWS ElastiCache cache.r6g.xlarge
    Memory: 16GB per node
    CPU: 2 vCPU per node
    Network: EBS-optimized, 10Gbps
  
  Replication:
    Mode: Async (1-2ms lag acceptable)
    Failover: Automatic via cluster manager
    
  Persistence:
    RDB: Disabled (acceptable data loss)
    AOF: Enabled, fsync every second
    Backup: Snapshot to S3 daily

Tuning:
  appendonly: yes
  appendfsync: everysec
  maxmemory-policy: allkeys-lru
  timeout: 300
  
Monitoring:
  - Memory eviction rate
  - Connected clients
  - Commands per second
  - Hit rate (%)
  - Replication offset
```

---

## ML Framework Components

### Ray Cluster

#### Head Node

```yaml
Head Node (Standalone or K8s Pod):
  CPU: 8 cores
  Memory: 32GB
  Storage: 100GB (for temp/checkpoint staging)
  
  Services:
    - Ray Head: Main process
    - Dashboard: Web UI (8265)
    - Object Store: Shared memory backend
    - GCS: Global control store (Redis)
  
  Configuration:
    object_store_memory: 25GB
    redis_password: enabled
    enable_object_store_memory_monitor: true
    plasma_timeout_millis: 5000
```

#### Worker Nodes

```yaml
GPU Worker Nodes:
  Instance Type: p4d.24xlarge (8x A100 GPU)
  CPU: 96 cores
  Memory: 1152GB
  GPU: 8x A100 80GB
  
  Ray Configuration:
    num_gpus: 8
    num_cpus: 96
    object_store_memory: 100GB per node
    resources:
      a100_gpu: 8
      training_gpu: 8

CPU Worker Nodes:
  Instance Type: c6i.4xlarge
  CPU: 16 cores
  Memory: 32GB
  
  Ray Configuration:
    num_gpus: 0
    num_cpus: 16
    object_store_memory: 20GB
    resources:
      cpu: 16
```

### Model Registry

#### MLflow Configuration

```yaml
MLflow Server:
  Backend Store: PostgreSQL (models metadata)
  Artifact Store: S3 (model files)
  Version: 2.10.x
  
  Database:
    Engine: PostgreSQL
    Connection Pool: 10-50
    
  Artifact Storage:
    S3 Bucket: codex-mlflow-artifacts
    Prefix: mlflow/
    Versioning: Enabled
    
  Features:
    - Experiment tracking
    - Model versioning (stages: None, Staging, Production)
    - Model registry (enable in 2.1+)
    - Artifact storage
    - REST API (port 5000)

Configuration File:
  command: mlflow server --backend-store-uri postgresql://... \
    --default-artifact-root s3://codex-mlflow-artifacts \
    --host 0.0.0.0 --port 5000
```

---

## Component Dependencies

### Startup Order

```
1. etcd (required for all K8s components)
2. API Server, Scheduler, Controller Manager
3. CoreDNS
4. CNI Plugin (Calico)
5. Storage Classes & Persistent Volumes
6. PostgreSQL (standalone) or RDS provisioning
7. Redis Cluster
8. NGINX/Istio Ingress
9. Prometheus & Grafana
10. AlertManager
11. Application Deployments
12. Ray Head Node
13. Ray Worker Nodes
14. Training/Serving Workloads
```

### Critical Dependencies

```
API Service:
  - PostgreSQL (required)
  - Redis (optional, degrades without cache)
  - Model Registry (optional)
  - S3 (required for long-term storage)

Model Server:
  - Ray (required)
  - S3 (for model artifacts)
  - Redis (for cache, optional)

Training:
  - Ray (required)
  - PostgreSQL (for metadata)
  - S3 (for checkpoints, required)
  - Data storage (dataset location)
```

---

## See Also

- [Infrastructure Architecture](INFRASTRUCTURE_ARCHITECTURE.md)
- [Technical Reference](TECHNICAL_REFERENCE.md)
- [Operations Manual](OPERATIONS_MANUAL.md)
- [Performance & Reliability](PERFORMANCE_RELIABILITY.md)

---

**Document Maintenance:**
- Review quarterly for version updates
- Update after component upgrades
- Validate specifications with production data

