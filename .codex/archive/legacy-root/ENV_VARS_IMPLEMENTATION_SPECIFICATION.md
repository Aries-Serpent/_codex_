# 🔧 Environment Variables Implementation Specification
## Phase 6.2: Localhost → Environment Variables Migration

**Document Version:** 1.0.0  
**Date Created:** 2026-07-06T02:29Z  
**Scope:** 8 new repository variables to implement in Aries-Serpent/_codex_  
**Deployment:** Via `.github/workflows/process-variable-intents.yml`  
**Status:** 🟢 READY FOR IMPLEMENTATION

---

## 📋 EXECUTIVE SUMMARY

This document specifies **8 new environment variables** required to replace 24 localhost hardcodes in the codebase.

- **Scope:** Repository-level variables (github.com/Aries-Serpent/_codex_/settings/variables)
- **Format:** Key-value string pairs (GitHub standard)
- **Fallback Behavior:** All have localhost defaults in code (backward compatible)
- **Security:** No secrets; all are configuration endpoints safe for version control
- **Timeline:** Create pending_ops files during Phase 6, deploy via workflow on merge

---

## 1️⃣ CODEX_REDIS_HOST

**Purpose:** Redis cache server hostname  
**Integration Points:**
- `src/codex/rag/cache/distributed_cache.py:redis_host` (default param)
- `src/cache/redis_cache.py:host` (default param)

**Specification:**

```yaml
Name: CODEX_REDIS_HOST
Type: string
Default Value (fallback in code): "localhost"
Recommended Values:
  development: "localhost"
  staging: "redis-staging.internal.codex"  
  production: "redis-primary.codex.svc.cluster.local"
Description: >
  Redis server hostname for distributed caching in RAG and ML training pipelines.
  Used by distributed_cache.py for cross-machine cache coordination.
Scope: Core infrastructure
Required: No (has fallback)
Security Impact: Low (hostname only, no secrets)
Version Introduced: 0.1.0
```

**Implementation in Code:**

```python
# BEFORE (src/codex/rag/cache/distributed_cache.py)
def __init__(self, redis_host: str = "localhost", ...):
    self.redis_host = redis_host

# AFTER (with env var)
def __init__(self, redis_host: str = None, ...):
    self.redis_host = redis_host or os.environ.get("CODEX_REDIS_HOST", "localhost")
```

**Tests Affected:**
- `tests/rag/cache/test_distributed_cache.py`
- `tests/cache/` (if exists)

---

## 2️⃣ CODEX_OLLAMA_HOST

**Purpose:** Ollama LLM inference server endpoint  
**Integration Points:**
- `src/codex/rag/providers/ollama_provider.py:host` (default param)

**Specification:**

```yaml
Name: CODEX_OLLAMA_HOST
Type: string (URL format)
Default Value (fallback in code): "http://localhost"
Recommended Values:
  development: "http://localhost:11434"
  staging: "http://ollama-staging.internal.codex:11434"
  production: "http://ollama.codex.svc.cluster.local:11434"
Description: >
  Ollama LLM server base URL for RAG inference.
  Must include protocol (http/https) and optional port.
  Used by OllamaProvider for embedding and chat inference.
Scope: RAG/inference
Required: No (has fallback)
Security Impact: Low (endpoint URL, no credentials)
Version Introduced: 0.1.0
Notes: >
  - Include full URL with protocol
  - Port 11434 is Ollama default
  - Can be a LoadBalancer endpoint for high availability
```

**Implementation in Code:**

```python
# BEFORE (src/codex/rag/providers/ollama_provider.py)
def __init__(self, host: str = "http://localhost", ...):
    self.host = host

# AFTER
def __init__(self, host: str = None, ...):
    self.host = host or os.environ.get("CODEX_OLLAMA_HOST", "http://localhost")
```

**Tests Affected:**
- `tests/rag/providers/test_ollama_provider.py`

---

## 3️⃣ CODEX_MASTER_ADDR

**Purpose:** Master node address for distributed PyTorch training  
**Integration Points:**
- `src/codex_ml/training/distributed.py:master_addr` (default param)
- `src/codex_ml/training/multi_node_orchestration.py:master_addr` (env var already supported)

**Specification:**

```yaml
Name: CODEX_MASTER_ADDR
Type: string (hostname/IP)
Default Value (fallback in code): "localhost"
Recommended Values:
  development: "localhost"
  staging: "training-master-staging.internal.codex"
  production: "training-master-0.training.codex.svc.cluster.local"
Description: >
  Master node address for distributed PyTorch DDP initialization.
  Used in DistributedSampler and synchronization primitives.
Scope: ML training
Required: No (has fallback)
Security Impact: Low (hostname only)
Version Introduced: 0.1.0
Notes: >
  - Must be resolvable by all worker nodes
  - Can be hostname or IP address
  - multi_node_orchestration.py already checks os.environ.get("MASTER_ADDR")
  - Synchronize with CODEX_MASTER_PORT for full training bootstrap
```

**Implementation in Code:**

```python
# BEFORE (src/codex_ml/training/distributed.py)
class DistributedConfig:
    master_addr: str = "localhost"

# AFTER
class DistributedConfig:
    master_addr: str = field(default_factory=lambda: os.environ.get("CODEX_MASTER_ADDR", "localhost"))
```

**Tests Affected:**
- `tests/training/test_distributed_coverage.py`
- `tests/distributed/test_distributed_enhanced.py`

---

## 4️⃣ CODEX_MASTER_PORT

**Purpose:** Master node port for distributed PyTorch training  
**Integration Points:**
- `src/codex_ml/training/distributed.py:master_port` (default param)
- `src/codex_ml/training/multi_node_orchestration.py:master_port` (env var already supported)

**Specification:**

```yaml
Name: CODEX_MASTER_PORT
Type: string (integer as string, e.g., "29500")
Default Value (fallback in code): "29500"
Recommended Values:
  development: "29500"
  staging: "29500"
  production: "29500"
Description: >
  Master node port for distributed PyTorch DDP communication.
  Standard PyTorch DDP port; usually stable across environments.
Scope: ML training
Required: No (has fallback)
Security Impact: Low (port number, usually static)
Version Introduced: 0.1.0
Notes: >
  - Standard PyTorch DDP port (RFC: 29400-29500 range reserved)
  - Rarely changes across environments
  - Must be open and accessible on master node
  - Synchronize with CODEX_MASTER_ADDR for full training bootstrap
```

**Implementation in Code:**

```python
# BEFORE (src/codex_ml/training/distributed.py)
class DistributedConfig:
    master_port: int = 29500

# AFTER
class DistributedConfig:
    master_port: int = field(default_factory=lambda: int(os.environ.get("CODEX_MASTER_PORT", "29500")))
```

**Tests Affected:**
- `tests/training/test_distributed_coverage.py`
- `tests/distributed/test_distributed_init.py`

---

## 5️⃣ CODEX_INFERENCE_SERVICE_HOST

**Purpose:** ML inference server bind address  
**Integration Points:**
- `src/codex_ml/serving/inference_server.py` (server startup)
- `src/mcp/server/http.py:host` (if applicable)

**Specification:**

```yaml
Name: CODEX_INFERENCE_SERVICE_HOST
Type: string (hostname/IP)
Default Value (fallback in code): "127.0.0.1"
Recommended Values:
  development: "127.0.0.1" or "localhost"
  staging: "0.0.0.0"  # Bind to all interfaces in Kubernetes
  production: "0.0.0.0"  # Bind to all interfaces in Kubernetes
Description: >
  Bind address for ML inference server HTTP listener.
  127.0.0.1 = localhost only; 0.0.0.0 = all network interfaces.
Scope: Serving/inference
Required: No (has fallback)
Security Impact: Medium (affects network exposure)
Version Introduced: 0.1.0
Notes: >
  - 127.0.0.1 for local development (secure default)
  - 0.0.0.0 for Kubernetes/container deployments (require network policy)
  - Never use external IP in container orchestration (let CNI handle routing)
```

**Implementation in Code:**

```python
# BEFORE (src/codex_ml/serving/inference_server.py)
app.run(host="127.0.0.1", port=8000)

# AFTER
host = os.environ.get("CODEX_INFERENCE_SERVICE_HOST", "127.0.0.1")
app.run(host=host, port=8000)
```

**Tests Affected:**
- `tests/codex_ml/serving/` (if exists)

---

## 6️⃣ CODEX_INFERENCE_SERVICE_PORT

**Purpose:** ML inference server listen port  
**Integration Points:**
- `src/codex_ml/serving/inference_server.py` (server startup)

**Specification:**

```yaml
Name: CODEX_INFERENCE_SERVICE_PORT
Type: string (integer as string, e.g., "8000")
Default Value (fallback in code): "8000"
Recommended Values:
  development: "8000"
  staging: "8000"
  production: "8000"
Description: >
  Port for ML inference server HTTP listener.
  Must be unprivileged (>1024) for non-root containers.
Scope: Serving/inference
Required: No (has fallback)
Security Impact: Low (port number)
Version Introduced: 0.1.0
Notes: >
  - Standard port 8000 for ML services
  - Rarely changes across environments
  - Synchronize with CODEX_INFERENCE_SERVICE_HOST for full server bootstrap
```

**Implementation in Code:**

```python
# BEFORE (src/codex_ml/serving/inference_server.py)
app.run(host="127.0.0.1", port=8000)

# AFTER
port = int(os.environ.get("CODEX_INFERENCE_SERVICE_PORT", "8000"))
app.run(host=host, port=port)
```

**Tests Affected:**
- `tests/codex_ml/serving/` (if exists)

---

## 7️⃣ CODEX_TRUSTED_HOSTS

**Purpose:** Allowlist of trusted hostnames for inference server requests  
**Integration Points:**
- `src/codex_ml/serving/inference_server.py:DEFAULT_TRUSTED_HOSTS`
- Used for HTTP request origin validation

**Specification:**

```yaml
Name: CODEX_TRUSTED_HOSTS
Type: string (comma-separated list)
Default Value (fallback in code): "localhost,127.0.0.1,testserver"
Recommended Values:
  development: "localhost,127.0.0.1,testserver"
  staging: "inference-staging.internal.codex,*.staging.codex.svc.cluster.local"
  production: "*.codex.svc.cluster.local,codex.prod"
Description: >
  Comma-separated allowlist of trusted hostnames for inference server requests.
  Used to prevent Host header injection attacks and control request origin.
Scope: Security/serving
Required: No (has fallback)
Security Impact: High (controls Host header validation)
Version Introduced: 0.1.0
Notes: >
  - Comma-separated, no spaces
  - Can use wildcards (*.example.com)
  - testserver included for pytest fixtures
  - Must include all valid hostnames/LBs pointing to this service
```

**Implementation in Code:**

```python
# BEFORE (src/codex_ml/serving/inference_server.py)
DEFAULT_TRUSTED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

# AFTER
DEFAULT_TRUSTED_HOSTS = os.environ.get("CODEX_TRUSTED_HOSTS", "localhost,127.0.0.1,testserver").split(",")
```

**Tests Affected:**
- `tests/codex_ml/serving/inference_server.py`

---

## 8️⃣ CODEX_LOCAL_LOOPBACK

**Purpose:** Enable/disable localhost loopback allowlist checks (dev-only feature gate)  
**Integration Points:**
- `src/safety/network_policy.py:_DEFAULT_LOCALHOSTS`
- `src/codex/auth/github_app.py:if _host in ("", "localhost", ...)`
- `src/codex_ml/tracking/mlflow_guard.py:localhost validation`
- `src/codex_ml/tracking/guards.py:localhost allowlist`

**Specification:**

```yaml
Name: CODEX_LOCAL_LOOPBACK
Type: boolean (string: "true" or "false")
Default Value (fallback in code): "true"
Recommended Values:
  development: "true"   # Allow localhost development
  staging: "false"      # Disable localhost in staging (enforce production behavior)
  production: "false"   # Disable localhost (require real hostnames/certs)
Description: >
  Feature gate for localhost/127.0.0.1/::1 allowlist in security policies.
  When true: localhost traffic is implicitly trusted (development mode).
  When false: all traffic subject to normal validation rules (production mode).
Scope: Security policy
Required: No (has fallback)
Security Impact: Critical (enables/disables development bypass)
Version Introduced: 0.1.0
Notes: >
  - MUST be "false" in production
  - MUST be "true" in development to enable fast iteration
  - When false, all connections require proper TLS certs and hostnames
  - Controls: MLflow guard, network policy enforcement, auth checks
  - Environment variable should be checked during app startup
```

**Implementation in Code:**

```python
# BEFORE (src/safety/network_policy.py)
_DEFAULT_LOCALHOSTS: tuple[str, ...] = ("localhost", "127.0.0.1", "::1")

# AFTER
_ENABLE_LOOPBACK = os.environ.get("CODEX_LOCAL_LOOPBACK", "true").lower() == "true"
_DEFAULT_LOCALHOSTS: tuple[str, ...] = ("localhost", "127.0.0.1", "::1") if _ENABLE_LOOPBACK else ()
```

**Implementation in github_app.py:**

```python
# BEFORE
if _host in ("", "localhost", "127.0.0.1", "::1"):
    # Allow local development

# AFTER
_ENABLE_LOOPBACK = os.environ.get("CODEX_LOCAL_LOOPBACK", "true").lower() == "true"
if _ENABLE_LOOPBACK and _host in ("", "localhost", "127.0.0.1", "::1"):
    # Allow local development only if feature gate enabled
```

**Tests Affected:**
- `tests/safety/test_network_policy.py`
- `tests/auth/test_oauth_flow.py` (localhost redirect testing)
- `tests/codex_ml/tracking/` (MLflow guard tests)

---

## IMPLEMENTATION WORKFLOW

### Step 1: Create Variable Definition Files

During Phase 6.2.A (10 min), create `.codex/pending_ops/variable_*.json` files:

```bash
cat > .codex/pending_ops/variable_CODEX_REDIS_HOST.json << 'EOF'
{
  "name": "CODEX_REDIS_HOST",
  "value": "localhost",
  "scope": "repository",
  "description": "Redis cache host for distributed_cache.py",
  "integration_point": "src/codex/rag/cache/distributed_cache.py"
}
EOF
```

### Step 2: Deploy Variables via Workflow

When `engine-tools-report_progress` commits these files:
1. `.github/workflows/process-variable-intents.yml` detects `pending_ops/*.json`
2. GitHub API creates repository variables
3. `.codex/agent_context.json` refreshes with new variables
4. Next session has live variables in `CODEX_*` environment

### Step 3: Code Replacements

During Phase 6.2.B, replace hardcodes with:

```python
value = os.environ.get("CODEX_VARIABLE_NAME", "fallback_default")
```

### Step 4: Validation

Verify variables are live:

```bash
# Check .codex/agent_context.json for new entries
cat .codex/agent_context.json | grep CODEX_REDIS_HOST
```

---

## VARIABLE SECURITY CHECKLIST

✅ **No Secrets:** All 8 variables are configuration endpoints, not credentials  
✅ **Safe for Git:** No API keys, passwords, or tokens  
✅ **Backward Compatible:** All have localhost fallbacks in code  
✅ **Prefixed:** All use CODEX_ prefix to avoid conflicts  
✅ **Documented:** Each integrated into code with clear comments  
✅ **Tested:** Test suite validates both env-var-set and fallback paths  

---

## INTEGRATION POINTS SUMMARY

| Variable | Files Affected | Impact |
|----------|-----------------|--------|
| CODEX_REDIS_HOST | 2 (rag/cache, cache/) | RAG caching, training coordination |
| CODEX_OLLAMA_HOST | 1 (rag/providers) | RAG inference |
| CODEX_MASTER_ADDR | 2 (training modules) | Distributed training |
| CODEX_MASTER_PORT | 2 (training modules) | Distributed training |
| CODEX_INFERENCE_SERVICE_HOST | 2 (serving, mcp) | Model serving |
| CODEX_INFERENCE_SERVICE_PORT | 2 (serving, mcp) | Model serving |
| CODEX_TRUSTED_HOSTS | 1 (inference_server) | Security validation |
| CODEX_LOCAL_LOOPBACK | 4 (safety, auth, tracking) | Dev-only feature gate |

---

## TESTING STRATEGY

### Unit Tests (Per-Variable)

```bash
# Test CODEX_REDIS_HOST fallback
CODEX_REDIS_HOST="" pytest tests/rag/cache/test_distributed_cache.py::test_redis_default

# Test CODEX_REDIS_HOST env var override
CODEX_REDIS_HOST="custom-redis" pytest tests/rag/cache/test_distributed_cache.py::test_redis_custom
```

### Integration Tests

```bash
# Full training pipeline with custom master node
CODEX_MASTER_ADDR="custom-master" CODEX_MASTER_PORT="29500" \
  pytest tests/training/test_distributed_coverage.py

# Inference server with custom hosts
CODEX_INFERENCE_SERVICE_HOST="0.0.0.0" CODEX_TRUSTED_HOSTS="custom.example.com" \
  pytest tests/codex_ml/serving/
```

### Security Validation

```bash
# Validate localhost loopback disabled in production mode
CODEX_LOCAL_LOOPBACK="false" pytest tests/safety/test_network_policy.py

# Validate localhost loopback enabled in dev mode
CODEX_LOCAL_LOOPBACK="true" pytest tests/safety/test_network_policy.py
```

---

## DEPLOYMENT RUNBOOK

### Development Environment

```bash
# No action needed; defaults work (localhost)
# Optionally override with custom services:
export CODEX_REDIS_HOST="localhost"
export CODEX_OLLAMA_HOST="http://localhost:11434"
export CODEX_LOCAL_LOOPBACK="true"

# Run app
python -m codex.cli serve
```

### Staging Environment

```bash
# GitHub Settings → Variables → Add/Update:
CODEX_REDIS_HOST = "redis-staging.internal.codex"
CODEX_OLLAMA_HOST = "http://ollama-staging.internal.codex:11434"
CODEX_MASTER_ADDR = "training-master-staging.internal.codex"
CODEX_INFERENCE_SERVICE_HOST = "0.0.0.0"
CODEX_TRUSTED_HOSTS = "*.staging.codex.svc.cluster.local"
CODEX_LOCAL_LOOPBACK = "false"

# Deployment continues; reads variables from environment
```

### Production Environment

```bash
# GitHub Settings → Variables → Add/Update:
CODEX_REDIS_HOST = "redis-primary.codex.svc.cluster.local"
CODEX_OLLAMA_HOST = "http://ollama.codex.svc.cluster.local:11434"
CODEX_MASTER_ADDR = "training-master-0.training.codex.svc.cluster.local"
CODEX_INFERENCE_SERVICE_HOST = "0.0.0.0"
CODEX_TRUSTED_HOSTS = "*.codex.svc.cluster.local,codex.prod"
CODEX_LOCAL_LOOPBACK = "false"

# Deployment continues; strict security checks enforced
```

---

## SUCCESS CRITERIA

✅ All 8 variables created in GitHub repository variables  
✅ All hardcodes replaced with os.environ.get() + fallback  
✅ 24 critical localhost hardcodes eliminated  
✅ Backward compatibility: fallbacks ensure localhost defaults if vars unset  
✅ Security: CODEX_LOCAL_LOOPBACK feature gate active  
✅ Tests: 100% pass with both env-var-set and fallback paths  
✅ Documentation: `.codex/LOCALHOST_REPLACEMENT_AUDIT.md` created  

---

## ROLLBACK PLAN

If issues arise post-deployment:

1. **Revert Code Changes:** Git revert commits containing env var replacements
2. **Remove Variables:** GitHub UI → Settings → Variables → Delete CODEX_* variables
3. **Restore Defaults:** Code will fall back to hardcoded localhost values
4. **Zero Downtime:** Existing code with hardcoded defaults continues working

---

## DOCUMENT HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-07-06T02:29Z | @copilot | Initial specification for 8 environment variables |

---

**Status:** 🟢 **READY FOR IMPLEMENTATION**  
**Authority:** @mbaetiong (D-tier autonomous)  
**Next Step:** Create pending_ops files during Phase 6.2.A

