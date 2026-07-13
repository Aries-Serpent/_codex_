# Local Development Environment Setup (Phase 6.2+)

**Version**: v0.2.1
**Last Updated:** 2026-07-11

> **Version**: 2.0.0 (Phase 6.2 Update)  
> **Last Updated**: 2026-07-06  
> **Status**: Phase 7 Ready (Groundwork Prepared)  
> **Timeline**: Phase 6.2 → Phase 7 (2026-07-08)  

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Phase 6.2 Environment Variables (NEW)](#phase-62-environment-variables-new)
3. [Setup Instructions](#setup-instructions)
4. [Validate Environment](#validate-environment)
5. [Environment-Specific Configurations](#environment-specific-configurations)
6. [Troubleshooting](#troubleshooting)
7. [Phase 7 Integration Testing](#phase-7-integration-testing)

---

## Quickstart

For experienced developers working with Phase 6.2 infrastructure:

```bash
# Clone the repository
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install in editable mode
pip install -e ".[dev]"

# Copy environment template
cp .env.example .env

# (Optional) Customize for your environment
# nano .env

# Validate environment variables
bash .codex/validate_local_env.sh

# Run tests
pytest tests/ -v --tb=short
```

---

## Phase 6.2 Environment Variables (NEW)

**Phase 6.2** introduces 8 new environment variables that replace hardcoded localhost references. These variables enable:

-  Flexible infrastructure configuration (local, Docker, Kubernetes)
-  Environment-specific settings (dev, staging, production)
-  Security policy enforcement (trusted hosts, feature gates)
-  Distributed training coordination (master node settings)

### Variable Summary

| Variable | Purpose | Default | Deployed |
|----------|---------|---------|----------|
| `CODEX_REDIS_HOST` | Redis cache hostname | `localhost` |  2026-07-06 |
| `CODEX_OLLAMA_HOST` | Ollama LLM service | `http://localhost:11434` |  2026-07-06 |
| `CODEX_MASTER_ADDR` | DDP training master | `localhost` |  2026-07-06 |
| `CODEX_MASTER_PORT` | DDP training port | `29500` |  2026-07-06 |
| `CODEX_INFERENCE_SERVICE_HOST` | Inference API bind | `127.0.0.1` |  2026-07-06 |
| `CODEX_INFERENCE_SERVICE_PORT` | Inference API port | `8000` |  2026-07-06 |
| `CODEX_TRUSTED_HOSTS` | Host header allowlist | `localhost,127.0.0.1,testserver` |  2026-07-06 |
| `CODEX_LOCAL_LOOPBACK` | Dev feature gate | `true` |  2026-07-06 |

**All variables are deployed to GitHub Settings and available during Phase 6.2.**

---

## Setup Instructions

### 1. Clone and Install

```bash
git clone https://github.com/Aries-Serpent/_codex_.git
cd _codex_
pip install -e ".[dev]"
```

### 2. Configure Environment Variables

Most developers can skip this step — **all variables have sensible localhost defaults**.

**Option A: Use Defaults (Recommended for Local Dev)**

```bash
# Skip environment setup; defaults work fine for localhost
pytest tests/ -v
```

**Option B: Customize for Your Environment**

```bash
# Copy template
cp .env.example .env

# Edit with your values
nano .env

# Load into current shell
source .env

# Verify configuration
bash .codex/validate_local_env.sh
```

### 3. Start Local Services (If Needed)

If you're running services locally and using non-default hosts:

```bash
# Redis (for distributed caching)
redis-server

# Ollama (for LLM embeddings)
ollama serve

# Application (in another terminal)
python -m codex_ml.cli serve --port 8000
```

### 4. Validate Environment

```bash
# Run validation script
bash .codex/validate_local_env.sh

# Expected output:
#  Variable defaults check completed
#  Fallback behavior verification passed
#  Override behavior verification passed
#  Security feature gate verification passed
#  CODEX_TRUSTED_HOSTS verification passed
#  Port validation passed
#  URL validation passed
#  Configuration integration test passed
#
#  All validation tests PASSED!
```

### 5. Run Tests

```bash
# Run all tests (uses default localhost configuration)
pytest tests/ -v

# Run specific test suites
pytest tests/test_phase_6_2_b_env_vars.py -v
pytest tests/config/test_env_vars_comprehensive.py -v

# Run with custom environment
CODEX_REDIS_HOST=custom-redis pytest tests/ -v
```

---

## Environment-Specific Configurations

### Local Development (Default)

```bash
# Default .env for local machine development
cp .env.example .env

# All services on localhost, minimal security checks
# Perfect for running everything on your machine
```

**Services to start:**

```bash
# Terminal 1: Redis
redis-server --port 6379

# Terminal 2: Ollama
ollama serve

# Terminal 3: Application
python -m codex_ml.cli serve
```

### Docker Compose Environment

```bash
# Use container hostnames
export CODEX_REDIS_HOST=redis
export CODEX_OLLAMA_HOST=http://ollama:11434
export CODEX_MASTER_ADDR=training-master
export CODEX_INFERENCE_SERVICE_HOST=0.0.0.0
export CODEX_TRUSTED_HOSTS=localhost,127.0.0.1,testserver,inference-api
export CODEX_LOCAL_LOOPBACK=true

# Start services
docker-compose up -d
```

**docker-compose.yml example:**

```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  ollama:
    image: ollama/ollama:latest
    ports:
      - "11434:11434"

  inference-api:
    build: .
    environment:
      - CODEX_REDIS_HOST=redis
      - CODEX_OLLAMA_HOST=http://ollama:11434
      - CODEX_INFERENCE_SERVICE_HOST=0.0.0.0
      - CODEX_LOCAL_LOOPBACK=true
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - ollama
```

### Kubernetes Staging

```bash
# Use Kubernetes DNS names
export CODEX_REDIS_HOST=redis-staging.codex.svc.cluster.local
export CODEX_OLLAMA_HOST=http://ollama-staging.codex.svc.cluster.local:11434
export CODEX_MASTER_ADDR=training-master-0.training.codex.svc.cluster.local
export CODEX_INFERENCE_SERVICE_HOST=0.0.0.0
export CODEX_TRUSTED_HOSTS=*.staging.codex.svc.cluster.local
export CODEX_LOCAL_LOOPBACK=false

# Deploy
kubectl apply -f k8s/staging/
```

### Kubernetes Production

```bash
# Hardened production configuration
export CODEX_REDIS_HOST=redis-primary.codex.svc.cluster.local
export CODEX_OLLAMA_HOST=http://ollama.codex.svc.cluster.local:11434
export CODEX_MASTER_ADDR=training-master-0.training.codex.svc.cluster.local
export CODEX_INFERENCE_SERVICE_HOST=0.0.0.0
export CODEX_TRUSTED_HOSTS=*.codex.svc.cluster.local,codex.prod
export CODEX_LOCAL_LOOPBACK=false

# Deploy
kubectl apply -f k8s/production/
```

---

## Troubleshooting

### "Connection refused" for Redis/Ollama

**Problem**: Services won't connect  
**Solution**:

1. Check if services are running:
   ```bash
   redis-cli ping        # Should return PONG
   curl http://localhost:11434  # Should return response
   ```

2. Update environment variables to correct host:
   ```bash
   export CODEX_REDIS_HOST=your-redis-host
   export CODEX_OLLAMA_HOST=http://your-ollama-host:11434
   bash .codex/validate_local_env.sh
   ```

3. Or start services locally:
   ```bash
   redis-server &
   ollama serve &
   ```

### Tests fail with "localhost: not resolvable"

**Problem**: Hostname resolution issues  
**Solution**:

1. Ensure `CODEX_LOCAL_LOOPBACK=true` (default):
   ```bash
   export CODEX_LOCAL_LOOPBACK=true
   pytest tests/ -v
   ```

2. Check `/etc/hosts` includes localhost:
   ```bash
   grep localhost /etc/hosts
   # Should show: 127.0.0.1 localhost
   ```

### "Host header not in CODEX_TRUSTED_HOSTS"

**Problem**: Request rejected by host validation  
**Solution**:

1. Add your hostname to trusted hosts:
   ```bash
   export CODEX_TRUSTED_HOSTS=localhost,127.0.0.1,testserver,my-hostname
   ```

2. Or disable feature gate for local dev:
   ```bash
   export CODEX_LOCAL_LOOPBACK=true
   ```

### "Production mode issues in dev"

**Problem**: Security checks too strict for development  
**Solution**:

```bash
# Enable localhost feature gate (development mode)
export CODEX_LOCAL_LOOPBACK=true

# For localhost development, this bypasses some security checks
# NEVER set to 'false' in actual development!
```

---

## Phase 7 Integration Testing

**Phase 7** (2 days post-merge, ~2026-07-08T10:00Z) includes validation of all 8 variables with live GitHub Settings deployment.

### Pre-Phase 7 Preparation (Do This Now)

1. **Copy environment template:**
   ```bash
   cp .env.example .env
   ```

2. **Run validation script:**
   ```bash
   bash .codex/validate_local_env.sh
   ```

3. **Review Phase 7 test plan:**
   ```bash
   # See: tests/test_phase_6_2_b_env_vars.py
   # See: tests/config/test_env_vars_comprehensive.py
   ```

### Phase 7 Execution (Automated)

When Phase 7 activates:

1. **All 8 variables live in GitHub Settings**
2. **Validation script runs automatically:**
   ```bash
   bash .codex/validate_local_env.sh
   ```

3. **Integration tests execute:**
   ```bash
   pytest tests/test_phase_6_2_b_env_vars.py -v
   pytest tests/config/test_env_vars_comprehensive.py -v
   ```

4. **Phase 7 completion report generated:**
   -  All variables deployed and accessible
   -  Local development validation passed
   -  Integration tests successful
   -  Ready for Phase 8 (CI/CD integration)

### Phase 7 Checklist

- [ ] `.env.example` copied to `.env`
- [ ] `bash .codex/validate_local_env.sh` passes all 8 tests
- [ ] `pytest tests/test_phase_6_2_b_env_vars.py` passes
- [ ] `pytest tests/config/test_env_vars_comprehensive.py` passes
- [ ] Environment-specific configurations validated
- [ ] Docker Compose setup works (if using)
- [ ] Kubernetes manifests use correct variable names (if using)

---

## More Information

- **Full Specification**: See `.codex/ENV_VARS_IMPLEMENTATION_SPECIFICATION.md`
- **Variable Inventory**: See `.codex/ENVIRONMENT_VARIABLES_ANALYSIS_TABLE.md`
- **Test Coverage**: See `tests/test_phase_6_2_b_env_vars.py`
- **GitHub Settings**: https://github.com/Aries-Serpent/_codex_/settings/variables

---

## Phase Timeline

| Phase | Date | Task |
|-------|------|------|
| **6.2** | 2026-07-06 | Deploy 8 variables to GitHub Settings  |
| **7.0** | 2026-07-08 | Validate in local development (2 days post-merge) |
| **7.1** | 2026-07-09 | Run integration tests with live variables |
| **7.2** | 2026-07-10 | Generate Phase 7 completion report |
| **8.0** | 2026-07-11 | CI/CD pipeline integration |

---

**Last Updated**: 2026-07-06  
**Status**: Phase 7 Groundwork Complete (Ready for 2026-07-08 Execution)
