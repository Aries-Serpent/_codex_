# Environment Variables Reference

> **Version**: 2.0.0  
> **Last Updated**: 2026-06-20  
> **Scope**: Complete environment variables documentation

---

## Quick Setup

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env

# Verify setup
python -c "from dotenv import load_dotenv; load_dotenv(); print('✅ Env loaded')"
```

---

## Core Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENVIRONMENT` | String | `development` | Environment: development, staging, production |
| `DEBUG` | Boolean | `False` | Enable debug mode (production: always False) |
| `LOG_LEVEL` | String | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `SECRET_KEY` | String | **REQUIRED** | Django secret key (production: strong random) |
| `ALLOWED_HOSTS` | String | `localhost` | Comma-separated allowed hosts |
| `WORKERS` | Integer | `4` | Number of worker processes |

**Example:**
```bash
ENVIRONMENT=production
DEBUG=False
LOG_LEVEL=INFO
SECRET_KEY=your-super-secret-key-here
ALLOWED_HOSTS=example.com,api.example.com
WORKERS=8
```

---

## Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | String | `sqlite:///codex.db` | Database connection URL |
| `DB_HOST` | String | `localhost` | Database host |
| `DB_PORT` | Integer | `5432` | Database port (PostgreSQL) |
| `DB_NAME` | String | `codex` | Database name |
| `DB_USER` | String | **REQUIRED** | Database username |
| `DB_PASSWORD` | String | **REQUIRED** | Database password |
| `DB_POOL_SIZE` | Integer | `10` | Database connection pool size |
| `DB_ECHO` | Boolean | `False` | Log all SQL queries |

**Example (PostgreSQL):**
```bash
DATABASE_URL=******localhost:5432/codex
# Or individual variables:
DB_HOST=db.example.com
DB_PORT=5432
DB_NAME=codex_production
DB_USER=codex_user
DB_PASSWORD=secure_password
DB_POOL_SIZE=20
```

---

## MCP Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MCP_BACKEND` | String | `mock` | Backend type: mock, pinecone, redis, custom |
| `MCP_WORKERS` | Integer | `4` | Number of MCP worker processes |
| `MCP_BATCH_SIZE` | Integer | `32` | Batch size for processing |
| `MCP_TIMEOUT` | Integer | `30` | Request timeout in seconds |

**For Pinecone Backend:**
```bash
MCP_BACKEND=pinecone
PINECONE_API_KEY=your-api-key
PINECONE_ENVIRONMENT=us-west4-gcp
PINECONE_INDEX=codex-prod
PINECONE_DIMENSION=1536
```

**For Redis Backend:**
```bash
MCP_BACKEND=redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
```

---

## Ray Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `RAY_ADDRESS` | String | `None` | Ray cluster address (localhost for local) |
| `RAY_NUM_CPUS` | Integer | `auto` | Number of CPUs for Ray |
| `RAY_NUM_GPUS` | Integer | `0` | Number of GPUs for Ray |
| `RAY_MEMORY` | Integer | `auto` | Memory allocation in bytes |

**Example:**
```bash
# Local Ray
RAY_ADDRESS=local

# Remote Ray cluster
RAY_ADDRESS=ray://cluster.example.com:10001
RAY_NUM_CPUS=16
RAY_NUM_GPUS=2
RAY_MEMORY=67108864000  # 62.5 GB
```

---

## API Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `API_HOST` | String | `0.0.0.0` | API server host |
| `API_PORT` | Integer | `8000` | API server port |
| `API_WORKERS` | Integer | `4` | Number of API workers |
| `CORS_ORIGINS` | String | `*` | CORS allowed origins (comma-separated) |
| `API_RATE_LIMIT` | Integer | `100` | Requests per minute per IP |

**Example:**
```bash
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=8
CORS_ORIGINS=https://example.com,https://admin.example.com
API_RATE_LIMIT=1000
```

---

## Monitoring & Observability

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SENTRY_DSN` | String | `None` | Sentry error tracking URL |
| `PROMETHEUS_PORT` | Integer | `8001` | Prometheus metrics port |
| `JAEGER_ENABLED` | Boolean | `False` | Enable distributed tracing |
| `JAEGER_AGENT_HOST` | String | `localhost` | Jaeger agent host |
| `JAEGER_AGENT_PORT` | Integer | `6831` | Jaeger agent port |

**Example:**
```bash
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
PROMETHEUS_PORT=9090
JAEGER_ENABLED=True
JAEGER_AGENT_HOST=jaeger.monitoring.svc
JAEGER_AGENT_PORT=6831
```

---

## Security Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `JWT_SECRET` | String | **REQUIRED** | JWT signing secret |
| `JWT_EXPIRY` | Integer | `3600` | JWT token expiry in seconds |
| `SSL_CERT_PATH` | String | `None` | Path to SSL certificate |
| `SSL_KEY_PATH` | String | `None` | Path to SSL private key |
| `SESSION_TIMEOUT` | Integer | `1800` | Session timeout in seconds |

**Example:**
```bash
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRY=7200  # 2 hours
SSL_CERT_PATH=/etc/ssl/certs/server.crt
SSL_KEY_PATH=/etc/ssl/private/server.key
SESSION_TIMEOUT=3600  # 1 hour
```

---

## External Services

### OpenAI / LLM Configuration

```bash
OPENAI_API_KEY=sk-xxx...
OPENAI_MODEL=gpt-4
OPENAI_MAX_TOKENS=2000
OPENAI_TEMPERATURE=0.7
```

### Model Registry

```bash
MODEL_REGISTRY_URL=http://registry.example.com
MODEL_DOWNLOAD_PATH=/models
HUGGINGFACE_TOKEN=hf_xxx...
```

---

## Development Configuration

```bash
# Development
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///dev.db
MCP_BACKEND=mock

# Testing
ENVIRONMENT=testing
DEBUG=False
LOG_LEVEL=WARNING
DATABASE_URL=sqlite:///:memory:
MCP_BACKEND=mock
```

---

## Production Configuration

```bash
# Production requirements
ENVIRONMENT=production
DEBUG=False  # ⚠️ NEVER set to True in production
LOG_LEVEL=WARNING
DATABASE_URL=******db.production.svc/codex
MCP_BACKEND=pinecone
SSL_CERT_PATH=/etc/ssl/certs/server.crt
SSL_KEY_PATH=/etc/ssl/private/server.key
JWT_SECRET=generated-random-secret-key
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
```

---

## Loading Environment Variables

### Python (dotenv)

```python
from dotenv import load_dotenv
import os

# Load from .env file
load_dotenv()

# Access variables
database_url = os.getenv("DATABASE_URL")
debug = os.getenv("DEBUG", "False").lower() == "true"
workers = int(os.getenv("WORKERS", "4"))
```

### Docker

```dockerfile
# Use .env file
ENV_FILE=.env.production
RUN --mount=type=secret,id=env \
    source /run/secrets/env && \
    echo "Database: ${DATABASE_URL}"
```

### Docker Compose

```yaml
services:
  api:
    env_file: .env.production
    environment:
      - ENVIRONMENT=production
      - DEBUG=False
```

---

## Validation

```bash
# Check all required variables are set
python -c "
import os
from dotenv import load_dotenv

load_dotenv()

required = ['ENVIRONMENT', 'DATABASE_URL', 'SECRET_KEY']
missing = [var for var in required if not os.getenv(var)]

if missing:
    print(f'❌ Missing variables: {missing}')
else:
    print('✅ All required variables set')
"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Variables not loading | Check .env file exists, verify path |
| Wrong values | Check .env syntax, no quotes needed unless spaces |
| Database connection fails | Verify DATABASE_URL format and credentials |
| MCP not connecting | Check MCP_BACKEND and credentials |

---

**Last Updated:** 2026-06-20
