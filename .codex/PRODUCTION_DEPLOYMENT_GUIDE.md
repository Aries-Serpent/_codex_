# Production Deployment Guide

**Version:** 1.0  
**Last Updated:** 2026-01-10  
**Audience:** DevOps Engineers, SREs, Platform Teams  
**Status:** Draft - Requires Implementation Completion

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Security Configuration](#security-configuration)
4. [Database Setup](#database-setup)
5. [Service Configuration](#service-configuration)
6. [Deployment Steps](#deployment-steps)
7. [Monitoring & Observability](#monitoring--observability)
8. [Rollback Procedures](#rollback-procedures)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide covers deployment of the Codex ML platform to production environments with focus on:

- **Security-First Deployment**: JWT/OAuth token validation, TLS encryption, secret management
- **Scalability**: Horizontal scaling with sharding, load balancing
- **Reliability**: Health checks, graceful shutdowns, circuit breakers
- **Observability**: Logging, metrics, tracing integration

### System Architecture

```
┌─────────────────┐
│   Load Balancer │ (HTTPS/TLS 1.3)
└────────┬────────┘
         │
    ┌────┴────┐
    │  API    │ (FastAPI, Uvicorn workers)
    │ Gateway │ (Auth: JWT/OAuth)
    └────┬────┘
         │
    ┌────┴─────────────────────┐
    │                          │
┌───▼────┐              ┌─────▼──────┐
│  RAG   │              │  Training  │
│ Service│              │  Service   │
└───┬────┘              └─────┬──────┘
    │                         │
┌───▼──────────┐      ┌──────▼───────┐
│ Vector Store │      │  ML Backend  │
│ (PGVector/   │      │  (Ray Serve) │
│  Sharded)    │      │              │
└──────────────┘      └──────────────┘
```

---

## Prerequisites

### Infrastructure Requirements

**Minimum Requirements (Development/Staging):**
- **Compute**: 4 CPU cores, 16GB RAM per node
- **Storage**: 100GB SSD (OS + application)
- **Database**: PostgreSQL 14+ with pgvector extension
- **Python**: 3.11+
- **Container Runtime**: Docker 24.0+ or Kubernetes 1.28+

**Production Requirements:**
- **Compute**: 3+ nodes with 8+ CPU cores, 32GB+ RAM each
- **Storage**: 500GB+ SSD per node, NAS/S3 for shared storage
- **Database**: PostgreSQL 15+ (managed service recommended)
  - With pgvector extension installed
  - Multi-AZ replication for HA
- **Load Balancer**: Layer 7 LB with TLS termination
- **Secrets Management**: HashiCorp Vault, AWS Secrets Manager, or Azure Key Vault

### Network Requirements

- **Inbound**: HTTPS (443), Health check endpoint (8080)
- **Outbound**: Database (5432), Redis (6379), S3/Object Storage
- **Internal**: Service mesh or VPC private networking

---

## Security Configuration

### 1. JWT Token Validation

**⚠️ CRITICAL: Must be implemented before production deployment**

Currently, `src/security/decorators.py::get_token_scopes()` raises `NotImplementedError`.  
Implement one of the following:

#### Option A: JWT with Symmetric Keys (HS256)

```python
# config/security.py
from pydantic_settings import BaseSettings

class SecuritySettings(BaseSettings):
    JWT_SECRET_KEY: str  # Load from secrets manager
    JWT_ALGORITHM: str = "HS256"
    JWT_AUDIENCE: str = "codex-api"
    JWT_ISSUER: str = "codex-auth"
    JWT_EXPIRATION_HOURS: int = 24

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

```python
# src/security/decorators.py (replace stub)
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from .config import SecuritySettings

settings = SecuritySettings()

async def get_token_scopes(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> List[str]:
    try:
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
            issuer=settings.JWT_ISSUER,
        )
        return payload.get("scopes", [])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
```

**Deployment:**
1. Generate strong secret key: `openssl rand -hex 32`
2. Store in secrets manager (never commit to Git)
3. Inject via environment variable: `JWT_SECRET_KEY=<secret>`

#### Option B: JWT with Asymmetric Keys (RS256)

For distributed systems with separate auth/resource servers:

```python
class SecuritySettings(BaseSettings):
    JWT_PUBLIC_KEY: str  # RSA public key (PEM format)
    JWT_ALGORITHM: str = "RS256"
    JWT_AUDIENCE: str = "codex-api"
    JWT_ISSUER: str = "auth-service"
```

```python
async def get_token_scopes(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> List[str]:
    try:
        # Load public key once at startup (cache)
        public_key = open(settings.JWT_PUBLIC_KEY_PATH).read()
        payload = jwt.decode(
            credentials.credentials,
            public_key,
            algorithms=[settings.JWT_ALGORITHM],
            audience=settings.JWT_AUDIENCE,
        )
        return payload.get("scopes", [])
    except jwt.ExpiredSignatureError:
        raise HTTPException(401, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

### 2. TLS/SSL Configuration

**Load Balancer TLS Termination (Recommended):**

```yaml
# Example: AWS ALB with ACM certificate
apiVersion: v1
kind: Service
metadata:
  name: codex-api
  annotations:
    service.beta.kubernetes.io/aws-load-balancer-ssl-cert: arn:aws:acm:...
    service.beta.kubernetes.io/aws-load-balancer-backend-protocol: http
    service.beta.kubernetes.io/aws-load-balancer-ssl-ports: "443"
spec:
  type: LoadBalancer
  ports:
    - port: 443
      targetPort: 8000
```

**Application-Level TLS (Advanced):**

```python
# uvicorn_config.py
import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8443,
        ssl_keyfile="/etc/ssl/private/server.key",
        ssl_certfile="/etc/ssl/certs/server.crt",
        ssl_ca_certs="/etc/ssl/certs/ca-bundle.crt",
        ssl_version=ssl.PROTOCOL_TLS_SERVER,
        ssl_ciphers="ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM",
    )
```

### 3. Secret Management

**Environment Variables (Development Only):**

```bash
export JWT_SECRET_KEY="dev-secret-do-not-use-in-prod"
export DATABASE_URL="postgresql://user:pass@localhost/codex"
export OPENAI_API_KEY="sk-..."
```

**Production: Secrets Manager Integration**

```python
# config/secrets.py
import boto3
from botocore.exceptions import ClientError

def get_secret(secret_name: str) -> dict:
    """Retrieve secret from AWS Secrets Manager"""
    client = boto3.client("secretsmanager", region_name="us-east-1")
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return json.loads(response["SecretString"])
    except ClientError as e:
        raise RuntimeError(f"Failed to retrieve secret: {e}")

# Usage
secrets = get_secret("codex/production/api-keys")
JWT_SECRET_KEY = secrets["jwt_secret"]
DATABASE_PASSWORD = secrets["db_password"]
```

---

## Database Setup

### PostgreSQL with pgvector Extension

**Installation:**

```sql
-- PostgreSQL 15+ with pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- Create dedicated user
CREATE USER codex_app WITH PASSWORD '<strong-password>';
GRANT CONNECT ON DATABASE codex_production TO codex_app;
```

**Schema Migrations:**

```sql
-- Create tables with 128-bit integer support for UUID ticket IDs
CREATE TABLE zendesk_tickets (
    ticket_id NUMERIC(39,0) PRIMARY KEY,  -- 128-bit UUID as integer
    subject TEXT NOT NULL,
    priority TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_ticket_created (created_at DESC)
);

-- Vector store tables for RAG
CREATE TABLE document_embeddings (
    id SERIAL PRIMARY KEY,
    tenant_id VARCHAR(255) NOT NULL,
    document_id VARCHAR(255) NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding vector(384),  -- Sentence-BERT dimension
    content TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    INDEX idx_tenant (tenant_id),
    INDEX idx_embedding USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)
);
```

**Connection Pool Configuration:**

```python
# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,  # Base connections
    max_overflow=20,  # Additional connections under load
    pool_timeout=30,  # Wait for connection (seconds)
    pool_recycle=3600,  # Recycle connections hourly
    pool_pre_ping=True,  # Verify connections before use
    echo=False,  # Disable SQL logging in production
)
```

---

## Service Configuration

### FastAPI Application

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZIPMiddleware
import uvicorn

app = FastAPI(
    title="Codex ML API",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url=None,  # Disable in production
)

# CORS (configure allowed origins)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Compression
app.add_middleware(GZIPMiddleware, minimum_size=1000)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # CPU cores
        log_level="info",
        access_log=True,
    )
```

### Docker Container

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Non-root user
RUN useradd -m -u 1000 codex && chown -R codex:codex /app
USER codex

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Start application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### Kubernetes Deployment

```yaml
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
      - name: api
        image: codex-ml:1.0.0
        ports:
        - containerPort: 8000
        env:
        - name: JWT_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: codex-secrets
              key: jwt-secret
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: codex-secrets
              key: database-url
        resources:
          requests:
            memory: "4Gi"
            cpu: "2"
          limits:
            memory: "8Gi"
            cpu: "4"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

## Deployment Steps

### 1. Pre-Deployment Checklist

- [ ] **Security**: JWT implementation complete, secrets configured
- [ ] **Database**: Migrations applied, connection pool tested
- [ ] **Tests**: All tests passing (unit, integration, security)
- [ ] **Code Quality**: CodeQL scan clean (no high/critical issues)
- [ ] **Documentation**: API docs updated, runbooks prepared
- [ ] **Monitoring**: Metrics endpoints configured, alerts set up
- [ ] **Backups**: Database backup verified, rollback plan documented

### 2. Deployment Procedure (Blue-Green)

```bash
# 1. Deploy new version (green)
kubectl apply -f k8s/deployment-green.yaml

# 2. Wait for health checks
kubectl wait --for=condition=ready pod -l version=green --timeout=300s

# 3. Run smoke tests
pytest tests/smoke/ --env=green

# 4. Switch traffic (update service selector)
kubectl patch service codex-api -p '{"spec":{"selector":{"version":"green"}}}'

# 5. Monitor metrics for 10 minutes
# Check error rates, latency, CPU/memory

# 6. If stable, scale down blue
kubectl scale deployment codex-api-blue --replicas=0

# 7. If issues, rollback
kubectl patch service codex-api -p '{"spec":{"selector":{"version":"blue"}}}'
```

### 3. Database Migrations

```bash
# Using Alembic (example)
alembic upgrade head

# Verify migration
psql $DATABASE_URL -c "SELECT version_num FROM alembic_version;"
```

---

## Monitoring & Observability

### Metrics (Prometheus)

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('http_requests_total', 'Total requests', ['method', 'endpoint'])
request_duration = Histogram('http_request_duration_seconds', 'Request duration')
active_connections = Gauge('db_connections_active', 'Active database connections')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    with request_duration.time():
        response = await call_next(request)
        request_count.labels(method=request.method, endpoint=request.url.path).inc()
        return response
```

### Logging (Structured JSON)

```python
import logging
import json

class JSONFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps({
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "service": "codex-api",
        })

logging.basicConfig(level=logging.INFO, handlers=[
    logging.StreamHandler()
])
logging.root.handlers[0].setFormatter(JSONFormatter())
```

### Alerts (Prometheus AlertManager)

```yaml
groups:
- name: codex-api
  rules:
  - alert: HighErrorRate
    expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
    annotations:
      summary: "High error rate detected"
  - alert: HighLatency
    expr: histogram_quantile(0.95, http_request_duration_seconds) > 1.0
    annotations:
      summary: "95th percentile latency > 1s"
```

---

## Rollback Procedures

### Immediate Rollback (Traffic Switch)

```bash
# Revert to previous version
kubectl set image deployment/codex-api api=codex-ml:1.0.0-previous
kubectl rollout status deployment/codex-api
```

### Database Rollback

```bash
# Downgrade one version
alembic downgrade -1

# Restore from backup (last resort)
pg_restore -d codex_production backup_20260110.dump
```

---

## Troubleshooting

### Common Issues

**Issue: JWT validation fails**
- Check `JWT_SECRET_KEY` is loaded correctly
- Verify token expiration/issuer/audience claims match
- Test with: `pyjwt decode <token> --secret <key>`

**Issue: Database connection pool exhausted**
- Increase `pool_size` and `max_overflow`
- Check for connection leaks (unclosed sessions)
- Monitor with: `SELECT count(*) FROM pg_stat_activity;`

**Issue: High memory usage**
- Check for large model loading without cleanup
- Reduce batch sizes for inference
- Enable swap if needed (temporary)

---

## Status: BLOCKED

**This deployment guide cannot be executed until:**

1. ✅ JWT token validation implemented (Phase 3)
2. ✅ Security integration tests written
3. ✅ Database migrations finalized
4. ⚠️ CodeQL scan passes with no critical issues
5. ⚠️ Load testing completed

**Next Steps:** See `.codex/AI_AGENT_NEXT_PHASE_PR2765.md` for implementation tasks.
