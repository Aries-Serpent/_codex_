# Technical Reference Guide - Codex ML

**Document Version:** 1.0.0  
**Last Updated:** 2026-07-08  
**Authority:** Phase 12 WS3 Documentation Lane 8  
**Audience:** Developers, DevOps Engineers, API Consumers  
**Status:** Production Reference

---

## Table of Contents

1. [API Reference](#api-reference)
2. [CLI Reference](#cli-reference)
3. [Configuration Reference](#configuration-reference)
4. [Database Schema](#database-schema)
5. [Event & Message Formats](#event--message-formats)
6. [Environment Variables](#environment-variables)

---

## API Reference

### Overview

**Base URL**: `https://api.codex.local` (or cloud provider endpoint)  
**API Version**: v1  
**Authentication**: ****** (JWT) or API key  
**Rate Limits**: 1000 req/s per API key  
**Response Format**: JSON  
**Timeout**: 30s for sync, 60s for async

### Authentication

#### JWT ******

```bash
curl -H "Authorization: ******" \
     https://api.codex.local/v1/models
```

**JWT Structure:**
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user-123",
    "iat": 1609459200,
    "exp": 1609545600,
    "scopes": ["models:read", "models:write"]
  }
}
```

#### API Key Authentication

```bash
curl -H "X-API-Key: sk_live_..." \
     https://api.codex.local/v1/models
```

### Core Endpoints

#### 1. Models API

##### List Models
```
GET /v1/models
```

**Query Parameters:**
- `limit` (int, default=20): Max results
- `offset` (int, default=0): Pagination offset
- `status` (string): Filter by status (active, deprecated, archived)
- `tag` (string): Filter by tags

**Response:**
```json
{
  "data": [
    {
      "id": "model-gpt-3-5",
      "name": "GPT-3.5 Turbo",
      "version": "2024-03",
      "status": "active",
      "created_at": "2024-03-15T10:30:00Z",
      "updated_at": "2024-06-15T14:20:00Z",
      "framework": "transformers",
      "parameters": 7000000000,
      "quantization": "fp16",
      "tags": ["language-model", "fine-tuned"]
    }
  ],
  "pagination": {
    "total": 42,
    "limit": 20,
    "offset": 0
  }
}
```

**Status Codes:**
- `200 OK`: Success
- `401 Unauthorized`: Invalid credentials
- `429 Too Many Requests`: Rate limit exceeded

##### Get Model Details
```
GET /v1/models/{model_id}
```

**Response:**
```json
{
  "id": "model-gpt-3-5",
  "name": "GPT-3.5 Turbo",
  "version": "2024-03",
  "status": "active",
  "description": "Fine-tuned GPT-3.5 model",
  "framework": "transformers",
  "parameters": 7000000000,
  "quantization": "fp16",
  "batch_size_limit": 32,
  "memory_required": "16GB",
  "latency_p50": "120ms",
  "latency_p99": "450ms",
  "throughput": "100 req/s",
  "created_at": "2024-03-15T10:30:00Z",
  "updated_at": "2024-06-15T14:20:00Z",
  "metadata": {
    "training_date": "2024-03-01",
    "training_data_size": "500GB",
    "validation_accuracy": 0.952
  }
}
```

##### Create Model
```
POST /v1/models
Content-Type: application/json
```

**Request Body:**
```json
{
  "name": "Custom Model",
  "version": "1.0.0",
  "framework": "transformers",
  "model_url": "s3://bucket/model.tar.gz",
  "description": "Custom fine-tuned model",
  "metadata": {
    "training_date": "2024-07-08",
    "validation_accuracy": 0.95
  }
}
```

**Response:** `201 Created`

#### 2. Inference API

##### Single Inference
```
POST /v1/inference
Content-Type: application/json
```

**Request:**
```json
{
  "model_id": "model-gpt-3-5",
  "input": {
    "prompt": "What is machine learning?",
    "max_tokens": 100,
    "temperature": 0.7
  },
  "options": {
    "timeout": "10s",
    "return_logits": false
  }
}
```

**Response:** `200 OK`
```json
{
  "request_id": "req-abc123",
  "model_id": "model-gpt-3-5",
  "output": {
    "text": "Machine learning is...",
    "tokens": 45,
    "finish_reason": "stop"
  },
  "metrics": {
    "latency_ms": 245,
    "tokens_per_second": 180
  }
}
```

##### Batch Inference
```
POST /v1/inference/batch
Content-Type: application/json
```

**Request:**
```json
{
  "model_id": "model-gpt-3-5",
  "inputs": [
    { "prompt": "What is AI?" },
    { "prompt": "What is ML?" },
    { "prompt": "What is DL?" }
  ],
  "batch_size": 32
}
```

**Response:**
```json
{
  "batch_id": "batch-xyz789",
  "status": "completed",
  "results": [
    {
      "request_id": "req-0",
      "output": { "text": "..." }
    },
    {
      "request_id": "req-1",
      "output": { "text": "..." }
    }
  ],
  "metrics": {
    "total_latency_ms": 850,
    "throughput_inferences_per_second": 3.5
  }
}
```

#### 3. Training API

##### List Training Jobs
```
GET /v1/training/jobs
```

**Response:**
```json
{
  "data": [
    {
      "job_id": "job-train-001",
      "name": "Fine-tune GPT-3.5",
      "status": "running",
      "progress": 65,
      "created_at": "2024-07-08T10:00:00Z",
      "estimated_completion": "2024-07-10T14:30:00Z",
      "metrics": {
        "loss": 0.234,
        "accuracy": 0.942,
        "learning_rate": 0.0001
      }
    }
  ]
}
```

##### Create Training Job
```
POST /v1/training/jobs
```

**Request:**
```json
{
  "name": "Fine-tune Model",
  "model_id": "model-base",
  "dataset_url": "s3://bucket/training_data.tar.gz",
  "config": {
    "epochs": 3,
    "batch_size": 32,
    "learning_rate": 0.0001,
    "optimizer": "adamw",
    "scheduler": "cosine"
  },
  "compute": {
    "gpus": 4,
    "gpu_type": "a100",
    "memory": "128Gi"
  }
}
```

**Response:** `201 Created`

---

## CLI Reference

### Installation

```bash
pip install codex-ml-cli
# or
pip install codex-ml[cli]
```

### Configuration

```bash
# Initialize CLI
codex-ml config init

# Set API endpoint
codex-ml config set endpoint https://api.codex.local

# Set authentication
codex-ml config set api_key sk_live_...
# or
codex-ml config set jwt_token $TOKEN
```

### Commands

#### Models Commands

```bash
# List all models
codex-ml models list [--limit=20] [--status=active]

# Get model details
codex-ml models get <model_id>

# Create model
codex-ml models create \
  --name "Custom Model" \
  --version 1.0.0 \
  --url s3://bucket/model.tar.gz

# Update model
codex-ml models update <model_id> \
  --status deprecated

# Delete model
codex-ml models delete <model_id>
```

#### Inference Commands

```bash
# Single inference
codex-ml infer <model_id> \
  --input '{"prompt": "What is AI?"}' \
  --output-file result.json

# Batch inference
codex-ml infer batch <model_id> \
  --input-file inputs.jsonl \
  --batch-size 32 \
  --output-file results.jsonl

# Stream inference (for text generation)
codex-ml infer stream <model_id> \
  --input '{"prompt": "Once upon a time"}' \
  --stream
```

#### Training Commands

```bash
# List training jobs
codex-ml training list [--status=running]

# Get job details
codex-ml training get <job_id>

# Create training job
codex-ml training create \
  --name "Fine-tune Model" \
  --model <model_id> \
  --dataset s3://bucket/data.tar.gz \
  --epochs 3 \
  --batch-size 32 \
  --gpus 4

# Monitor training
codex-ml training monitor <job_id> \
  --refresh 5s

# Cancel training job
codex-ml training cancel <job_id>

# Get training logs
codex-ml training logs <job_id> [--tail=100] [--follow]
```

#### Configuration Commands

```bash
# Show current config
codex-ml config show

# Set configuration
codex-ml config set key value

# Reset to defaults
codex-ml config reset
```

#### System Commands

```bash
# Health check
codex-ml health

# System info
codex-ml system info

# Version
codex-ml --version
```

---

## Configuration Reference

### Hydra Configuration Structure

```yaml
codex:
  # Model serving configuration
  model_serving:
    engine: ray  # Options: ray, kubernetes, local
    num_replicas: 3
    max_concurrent_queries: 100
    timeout_seconds: 30
    
    # GPU allocation
    gpu_per_replica: 1
    gpu_type: a100  # Options: a100, h100, v100, l4
    
    # Model caching
    cache_enabled: true
    cache_size_gb: 100
    
  # Training configuration
  training:
    engine: ray
    num_workers: 4
    gpus_per_worker: 2
    
    # Checkpointing
    checkpoint_freq_epochs: 1
    checkpoint_dir: /mnt/checkpoints
    
    # Distributed training
    distributed: true
    sync_batch_norm: true
    
  # Data configuration
  data:
    batch_size: 32
    num_workers: 4
    prefetch_factor: 2
    persistent_workers: true
    
    # Data splitting
    train_ratio: 0.8
    val_ratio: 0.1
    test_ratio: 0.1
    
  # Optimization
  optimizer:
    name: adamw
    lr: 0.0001
    beta1: 0.9
    beta2: 0.999
    eps: 1.0e-8
    weight_decay: 0.01
    
  # Scheduler
  scheduler:
    name: cosine
    warmup_steps: 1000
    num_cycles: 1
    
  # Logging
  logging:
    level: INFO
    format: json
    include_timestamp: true
    
    # Metrics tracking
    track_metrics: true
    log_frequency: 100
    
  # Storage
  storage:
    type: s3  # Options: s3, gcs, azure, local
    bucket: codex-ml-artifacts
    prefix: models/
    
    # Backup
    enable_backup: true
    backup_frequency: hourly
    retention_days: 30
```

### Environment Variables

```bash
# API Configuration
CODEX_API_ENDPOINT=https://api.codex.local
CODEX_API_KEY=sk_live_...
CODEX_JWT_TOKEN=$TOKEN

# Model Serving
CODEX_MODEL_SERVING_ENGINE=ray
CODEX_MODEL_REPLICAS=3
CODEX_GPU_TYPE=a100

# Training
CODEX_TRAINING_ENGINE=ray
CODEX_TRAINING_WORKERS=4
CODEX_GPUS_PER_WORKER=2

# Storage
CODEX_STORAGE_TYPE=s3
CODEX_STORAGE_BUCKET=codex-ml-artifacts
CODEX_STORAGE_CREDENTIALS_FILE=/secrets/aws-credentials

# Logging
CODEX_LOG_LEVEL=INFO
CODEX_LOG_FORMAT=json

# Monitoring
CODEX_PROMETHEUS_PORT=8001
CODEX_METRICS_ENABLED=true

# Debug
CODEX_DEBUG=false
CODEX_TRACE_ENABLED=true
```

### Configuration Files

```
~/.codex/
├── config.yaml          # Main configuration
├── credentials.yaml     # Authentication credentials
├── models/
│   ├── model1/
│   │   └── config.yaml
│   └── model2/
│       └── config.yaml
└── training/
    └── job1/
        └── config.yaml
```

---

## Database Schema

### PostgreSQL Schema

#### Models Table

```sql
CREATE TABLE models (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR(255) NOT NULL,
  version VARCHAR(50) NOT NULL,
  status VARCHAR(20) DEFAULT 'active',  -- active, deprecated, archived
  framework VARCHAR(100),  -- transformers, pytorch, tensorflow
  parameters BIGINT,
  quantization VARCHAR(20),  -- fp32, fp16, int8, int4
  
  -- Deployment info
  model_url VARCHAR(2048),  -- S3/GCS path
  checkpoint_id UUID,
  
  -- Metadata
  description TEXT,
  tags JSONB DEFAULT '[]',
  metadata JSONB DEFAULT '{}',
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID REFERENCES users(id),
  
  CONSTRAINT unique_name_version UNIQUE(name, version),
  INDEX (status),
  INDEX (created_at DESC)
);
```

#### Inference Requests Table

```sql
CREATE TABLE inference_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  model_id UUID NOT NULL REFERENCES models(id),
  
  -- Request info
  input JSONB NOT NULL,
  output JSONB,
  
  -- Status
  status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
  error_message TEXT,
  
  -- Performance metrics
  latency_ms INT,
  tokens_generated INT,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  completed_at TIMESTAMP,
  
  -- User tracking
  user_id UUID REFERENCES users(id),
  api_key_id UUID,
  
  INDEX (model_id),
  INDEX (status),
  INDEX (created_at DESC)
);
```

#### Training Jobs Table

```sql
CREATE TABLE training_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  name VARCHAR(255) NOT NULL,
  model_id UUID REFERENCES models(id),
  base_model_id UUID REFERENCES models(id),
  
  -- Configuration
  config JSONB NOT NULL,
  
  -- Status tracking
  status VARCHAR(20) DEFAULT 'pending',  -- pending, running, completed, failed, cancelled
  progress_percent INT DEFAULT 0,
  
  -- Compute allocation
  gpu_count INT,
  gpu_type VARCHAR(50),
  memory_gb INT,
  
  -- Metrics
  metrics JSONB DEFAULT '{}',  -- loss, accuracy, etc.
  
  -- Artifacts
  checkpoint_paths TEXT[] DEFAULT '{}',
  output_model_id UUID REFERENCES models(id),
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  started_at TIMESTAMP,
  completed_at TIMESTAMP,
  estimated_completion TIMESTAMP,
  
  -- User tracking
  user_id UUID NOT NULL REFERENCES users(id),
  
  INDEX (status),
  INDEX (created_at DESC)
);
```

#### API Keys Table

```sql
CREATE TABLE api_keys (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  
  user_id UUID NOT NULL REFERENCES users(id),
  
  -- Key management
  key_hash VARCHAR(255) NOT NULL UNIQUE,
  name VARCHAR(255),
  
  -- Permissions
  scopes TEXT[] DEFAULT '{models:read, models:write}',
  
  -- Rate limiting
  rate_limit_rps INT DEFAULT 100,
  
  -- Status
  active BOOLEAN DEFAULT true,
  
  -- Timestamps
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_used_at TIMESTAMP,
  expires_at TIMESTAMP,
  
  INDEX (user_id),
  INDEX (key_hash)
);
```

#### Metrics Table

```sql
CREATE TABLE metrics (
  id BIGSERIAL PRIMARY KEY,
  
  -- Metric identification
  metric_name VARCHAR(255) NOT NULL,
  labels JSONB,  -- Tags: {env: prod, service: api}
  
  -- Value
  value FLOAT NOT NULL,
  
  -- Timestamp (for time-series)
  recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  
  -- Indexing
  CONSTRAINT metrics_unique UNIQUE(metric_name, labels, recorded_at),
  INDEX (metric_name, recorded_at DESC),
  INDEX (recorded_at DESC PARTITION BY RANGE (recorded_at))  -- Partitioning for large tables
);
```

### MongoDB Collections (for semi-structured data)

```javascript
// Training checkpoints
db.checkpoints.insertOne({
  _id: ObjectId(),
  job_id: UUID,
  epoch: 5,
  model_weights: Binary,  // Large binary data
  optimizer_state: Binary,
  metrics: {
    loss: 0.234,
    accuracy: 0.942
  },
  created_at: ISODate(),
  storage_path: "s3://bucket/checkpoint-5.pt"
});

// Model metadata
db.model_metadata.insertOne({
  _id: "model-gpt-3-5",
  training_config: { /* full config */ },
  dataset_info: {
    name: "Training Data v2",
    samples: 1000000,
    split_ratios: { train: 0.8, val: 0.1, test: 0.1 }
  },
  validation_results: {
    accuracy: 0.952,
    f1_score: 0.947,
    confusion_matrix: [ /* data */ ]
  }
});
```

---

## Event & Message Formats

### Pub/Sub Events

All events follow CloudEvents format.

#### Model Training Events

```json
{
  "specversion": "1.0",
  "type": "com.codex.training.job.created",
  "source": "/training/job-123",
  "id": "evt-abc123",
  "time": "2024-07-08T10:30:00Z",
  "datacontenttype": "application/json",
  "subject": "model-gpt-3-5/v2",
  "data": {
    "job_id": "job-123",
    "model_id": "model-gpt-3-5",
    "version": "v2",
    "status": "started",
    "config": {
      "epochs": 3,
      "batch_size": 32
    }
  }
}
```

#### Model Deployment Events

```json
{
  "type": "com.codex.model.deployed",
  "source": "/models/model-gpt-3-5",
  "id": "evt-def456",
  "time": "2024-07-08T14:00:00Z",
  "data": {
    "model_id": "model-gpt-3-5",
    "version": "2024-07",
    "environment": "production",
    "replicas": 3,
    "regions": ["us-east-1", "eu-west-1"]
  }
}
```

#### Inference Events

```json
{
  "type": "com.codex.inference.completed",
  "source": "/inference/req-xyz",
  "id": "evt-ghi789",
  "time": "2024-07-08T15:30:00Z",
  "data": {
    "request_id": "req-xyz",
    "model_id": "model-gpt-3-5",
    "latency_ms": 245,
    "tokens": 45,
    "status": "success"
  }
}
```

### Message Queue Formats (RabbitMQ/Kafka)

#### Training Checkpoint Message

```json
{
  "type": "training.checkpoint",
  "timestamp": "2024-07-08T10:30:00Z",
  "payload": {
    "job_id": "job-123",
    "epoch": 5,
    "metrics": {
      "loss": 0.234,
      "accuracy": 0.942,
      "learning_rate": 0.0001
    },
    "checkpoint_url": "s3://bucket/checkpoints/job-123/epoch-5.pt",
    "size_bytes": 5368709120
  }
}
```

---

## Environment Variables

### Critical Configuration

```bash
# Required
CODEX_API_ENDPOINT=https://api.codex.local
CODEX_STORAGE_BUCKET=codex-ml-artifacts

# Authentication (one required)
CODEX_API_KEY=sk_live_...
CODEX_JWT_TOKEN=$JWT

# Cloud provider credentials
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
# or GCP
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
# or Azure
AZURE_STORAGE_ACCOUNT_NAME=...
AZURE_STORAGE_ACCOUNT_KEY=...
```

### Operational Configuration

```bash
# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
OTEL_ENABLED=true
JAEGER_AGENT_HOST=localhost
JAEGER_AGENT_PORT=6831

# Monitoring
PROMETHEUS_ENABLED=true
PROMETHEUS_PORT=8001
METRICS_EXPORT_INTERVAL=30s

# Resource limits
MEMORY_LIMIT=8Gi
CPU_LIMIT=4
GPU_MEMORY_LIMIT=24Gi

# Performance tuning
BATCH_SIZE=32
NUM_WORKERS=4
PREFETCH_FACTOR=2

# Model serving
RAY_SERVE_ENABLE=true
NUM_REPLICAS=3
INFERENCE_TIMEOUT=30s
```

### Optional Advanced Configuration

```bash
# Development/Debug
DEBUG_MODE=false
TRACE_ENABLED=false
PROFILE_ENABLED=false

# Cache configuration
CACHE_BACKEND=redis
REDIS_URL=redis://localhost:6379/0
CACHE_TTL=3600

# Advanced optimization
USE_MIXED_PRECISION=true
GRADIENT_ACCUMULATION_STEPS=4
USE_DISTRIBUTED_TRAINING=true

# Model registry
MODEL_REGISTRY_URL=http://mlflow:5000
MODEL_REGISTRY_TYPE=mlflow
```

---

## Best Practices

### API Usage

1. **Batch Inference**: Use for throughput-sensitive workloads
2. **Error Handling**: Implement exponential backoff for retries
3. **Rate Limiting**: Monitor headers, respect rate limits
4. **Caching**: Cache model lists, rarely-changing configs

### Configuration Management

1. **Secrets**: Use HashiCorp Vault, never hardcode
2. **Profiles**: Create environment-specific configs
3. **Version Control**: Track configuration changes in Git
4. **Testing**: Validate config before deployment

### Database

1. **Connection Pooling**: Use connection pools, max 20 per app instance
2. **Indexes**: Maintain indexes on frequently queried fields
3. **Partitioning**: Partition metrics table by date
4. **Backups**: Automated hourly snapshots with 30-day retention

---

## See Also

- [Infrastructure Architecture](INFRASTRUCTURE_ARCHITECTURE.md)
- [Operations Manual](OPERATIONS.md)
- [API Changelog](../../docs/API_REFERENCE.md)
- [Deployment Guides](../deployment/)

---

**Revision History:**

| Date | Author | Changes |
|------|--------|---------|
| 2026-07-08 | Phase 12 WS3 Lane 8 | Initial creation |

