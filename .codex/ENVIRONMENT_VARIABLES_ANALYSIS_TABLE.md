# 📊 Environment Variables Analysis Table
## Phase 6.2: Repository Variables for Localhost Migration

**Generated:** 2026-07-06T02:58:22Z  
**Scope:** All 8 environment variables from `.codex/ENV_VARS_IMPLEMENTATION_SPECIFICATION.md`  
**Status:** 🟢 READY FOR ACTION

---

## 📋 ENVIRONMENT VARIABLES INVENTORY

### QUICK REFERENCE TABLE

| # | Variable Name | Scope Type | Variable Type | Default Value | Dev Value | Staging Value | Production Value | Security Impact |
|---|---|---|---|---|---|---|---|---|
| 1 | `CODEX_REDIS_HOST` | **Repo** | Environment Action | `localhost` | `localhost` | `redis-staging.internal.codex` | `redis-primary.codex.svc.cluster.local` | 🟢 Low |
| 2 | `CODEX_OLLAMA_HOST` | **Repo** | Environment Action | `http://localhost` | `http://localhost:11434` | `http://ollama-staging.internal.codex:11434` | `http://ollama.codex.svc.cluster.local:11434` | 🟢 Low |
| 3 | `CODEX_MASTER_ADDR` | **Repo** | Environment Action | `localhost` | `localhost` | `training-master-staging.internal.codex` | `training-master-0.training.codex.svc.cluster.local` | 🟢 Low |
| 4 | `CODEX_MASTER_PORT` | **Repo** | Environment Action | `29500` | `29500` | `29500` | `29500` | 🟢 Low |
| 5 | `CODEX_INFERENCE_SERVICE_HOST` | **Repo** | Environment Action | `127.0.0.1` | `127.0.0.1` | `0.0.0.0` | `0.0.0.0` | 🟡 Medium |
| 6 | `CODEX_INFERENCE_SERVICE_PORT` | **Repo** | Environment Action | `8000` | `8000` | `8000` | `8000` | 🟢 Low |
| 7 | `CODEX_TRUSTED_HOSTS` | **Repo** | Environment Action | `localhost,127.0.0.1,testserver` | `localhost,127.0.0.1,testserver` | `*.staging.codex.svc.cluster.local` | `*.codex.svc.cluster.local,codex.prod` | 🔴 High |
| 8 | `CODEX_LOCAL_LOOPBACK` | **Repo** | Environment Action | `true` | `true` | `false` | `false` | 🔴 Critical |

---

## DETAILED SPECIFICATIONS BY VARIABLE

### 1️⃣ CODEX_REDIS_HOST

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_REDIS_HOST` |
| **Type** | String (hostname) |
| **Default (Fallback)** | `localhost` |
| **Dev Value** | `localhost` |
| **Staging Value** | `redis-staging.internal.codex` |
| **Production Value** | `redis-primary.codex.svc.cluster.local` |
| **Integration Points** | `src/codex/rag/cache/distributed_cache.py` (line: redis_host param)<br/>`src/cache/redis_cache.py` (line: host param) |
| **Security Impact** | 🟢 **Low** — hostname only, no secrets |
| **Required** | ❌ No (has localhost fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Redis server hostname for distributed caching in RAG and ML training pipelines |
| **Test Files Affected** | `tests/rag/cache/test_distributed_cache.py`<br/>`tests/cache/` |

**Implementation Pattern:**
```python
# Code should use:
redis_host = os.environ.get("CODEX_REDIS_HOST", "localhost")
```

---

### 2️⃣ CODEX_OLLAMA_HOST

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_OLLAMA_HOST` |
| **Type** | String (URL with protocol) |
| **Default (Fallback)** | `http://localhost` |
| **Dev Value** | `http://localhost:11434` |
| **Staging Value** | `http://ollama-staging.internal.codex:11434` |
| **Production Value** | `http://ollama.codex.svc.cluster.local:11434` |
| **Integration Points** | `src/codex/rag/providers/ollama_provider.py` (line: host param) |
| **Security Impact** | 🟢 **Low** — endpoint URL, no credentials |
| **Required** | ❌ No (has http://localhost fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Ollama LLM server base URL for RAG inference; must include protocol and optional port |
| **Test Files Affected** | `tests/rag/providers/test_ollama_provider.py` |

**Implementation Pattern:**
```python
# Code should use:
ollama_host = os.environ.get("CODEX_OLLAMA_HOST", "http://localhost")
```

---

### 3️⃣ CODEX_MASTER_ADDR

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_MASTER_ADDR` |
| **Type** | String (hostname/IP) |
| **Default (Fallback)** | `localhost` |
| **Dev Value** | `localhost` |
| **Staging Value** | `training-master-staging.internal.codex` |
| **Production Value** | `training-master-0.training.codex.svc.cluster.local` |
| **Integration Points** | `src/codex_ml/training/distributed.py` (line: master_addr param)<br/>`src/codex_ml/training/multi_node_orchestration.py` (already supports env var) |
| **Security Impact** | 🟢 **Low** — hostname only |
| **Required** | ❌ No (has localhost fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Master node address for distributed PyTorch DDP initialization |
| **Notes** | Must be resolvable by all worker nodes; sync with CODEX_MASTER_PORT |
| **Test Files Affected** | `tests/training/test_distributed_coverage.py`<br/>`tests/distributed/test_distributed_enhanced.py` |

**Implementation Pattern:**
```python
# Code should use:
master_addr = os.environ.get("CODEX_MASTER_ADDR", "localhost")
```

---

### 4️⃣ CODEX_MASTER_PORT

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_MASTER_PORT` |
| **Type** | String (integer as string) |
| **Default (Fallback)** | `29500` |
| **Dev Value** | `29500` |
| **Staging Value** | `29500` |
| **Production Value** | `29500` |
| **Integration Points** | `src/codex_ml/training/distributed.py` (line: master_port param)<br/>`src/codex_ml/training/multi_node_orchestration.py` (already supports env var) |
| **Security Impact** | 🟢 **Low** — port number, usually static |
| **Required** | ❌ No (has 29500 fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Master node port for distributed PyTorch DDP communication |
| **Notes** | Standard PyTorch DDP port (RFC: 29400-29500 reserved); rarely changes across environments |
| **Test Files Affected** | `tests/training/test_distributed_coverage.py`<br/>`tests/distributed/test_distributed_init.py` |

**Implementation Pattern:**
```python
# Code should use:
master_port = int(os.environ.get("CODEX_MASTER_PORT", "29500"))
```

---

### 5️⃣ CODEX_INFERENCE_SERVICE_HOST

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_INFERENCE_SERVICE_HOST` |
| **Type** | String (hostname/IP) |
| **Default (Fallback)** | `127.0.0.1` |
| **Dev Value** | `127.0.0.1` or `localhost` |
| **Staging Value** | `0.0.0.0` (bind all interfaces in Kubernetes) |
| **Production Value** | `0.0.0.0` (bind all interfaces in Kubernetes) |
| **Integration Points** | `src/codex_ml/serving/inference_server.py` (server startup)<br/>`src/mcp/server/http.py` (if applicable) |
| **Security Impact** | 🟡 **Medium** — affects network exposure |
| **Required** | ❌ No (has 127.0.0.1 fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Bind address for ML inference server HTTP listener |
| **Notes** | 127.0.0.1 = localhost only; 0.0.0.0 = all network interfaces; use 0.0.0.0 in container orchestration only |
| **Test Files Affected** | `tests/codex_ml/serving/` |

**Implementation Pattern:**
```python
# Code should use:
inference_host = os.environ.get("CODEX_INFERENCE_SERVICE_HOST", "127.0.0.1")
app.run(host=inference_host, port=8000)
```

---

### 6️⃣ CODEX_INFERENCE_SERVICE_PORT

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_INFERENCE_SERVICE_PORT` |
| **Type** | String (integer as string) |
| **Default (Fallback)** | `8000` |
| **Dev Value** | `8000` |
| **Staging Value** | `8000` |
| **Production Value** | `8000` |
| **Integration Points** | `src/codex_ml/serving/inference_server.py` (server startup) |
| **Security Impact** | 🟢 **Low** — port number |
| **Required** | ❌ No (has 8000 fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Port for ML inference server HTTP listener |
| **Notes** | Must be unprivileged (>1024) for non-root containers; sync with CODEX_INFERENCE_SERVICE_HOST |
| **Test Files Affected** | `tests/codex_ml/serving/` |

**Implementation Pattern:**
```python
# Code should use:
inference_port = int(os.environ.get("CODEX_INFERENCE_SERVICE_PORT", "8000"))
app.run(host=inference_host, port=inference_port)
```

---

### 7️⃣ CODEX_TRUSTED_HOSTS

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_TRUSTED_HOSTS` |
| **Type** | String (comma-separated list, no spaces) |
| **Default (Fallback)** | `localhost,127.0.0.1,testserver` |
| **Dev Value** | `localhost,127.0.0.1,testserver` |
| **Staging Value** | `*.staging.codex.svc.cluster.local` |
| **Production Value** | `*.codex.svc.cluster.local,codex.prod` |
| **Integration Points** | `src/codex_ml/serving/inference_server.py` (line: DEFAULT_TRUSTED_HOSTS) |
| **Security Impact** | 🔴 **High** — controls Host header validation |
| **Required** | ❌ No (has fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Allowlist of trusted hostnames for inference server requests; prevents Host header injection |
| **Notes** | Comma-separated, no spaces; can use wildcards; must include all valid hostnames/LBs; testserver for pytest |
| **Test Files Affected** | `tests/codex_ml/serving/inference_server.py` |

**Implementation Pattern:**
```python
# Code should use:
trusted_hosts_str = os.environ.get("CODEX_TRUSTED_HOSTS", "localhost,127.0.0.1,testserver")
DEFAULT_TRUSTED_HOSTS = [h.strip() for h in trusted_hosts_str.split(",")]
```

---

### 8️⃣ CODEX_LOCAL_LOOPBACK

| Attribute | Value |
|-----------|-------|
| **Scope** | 🏢 **Repository** |
| **Variable Type** | 📍 Environment Action Variable |
| **Name** | `CODEX_LOCAL_LOOPBACK` |
| **Type** | String (boolean: "true" or "false") |
| **Default (Fallback)** | `true` |
| **Dev Value** | `true` (allow localhost development) |
| **Staging Value** | `false` (enforce production behavior) |
| **Production Value** | `false` (require real hostnames/certs) |
| **Integration Points** | `src/safety/network_policy.py` (line: _DEFAULT_LOCALHOSTS)<br/>`src/codex/auth/github_app.py` (localhost validation)<br/>`src/codex_ml/tracking/mlflow_guard.py` (localhost validation)<br/>`src/codex_ml/tracking/guards.py` (localhost allowlist) |
| **Security Impact** | 🔴 **Critical** — enables/disables development bypass |
| **Required** | ❌ No (has "true" fallback) |
| **Version Introduced** | `0.1.0` |
| **Description** | Feature gate for localhost/127.0.0.1/::1 allowlist in security policies |
| **Notes** | MUST be "false" in production; MUST be "true" in dev; when false, all connections require TLS certs & hostnames |
| **Test Files Affected** | `tests/safety/test_network_policy.py`<br/>`tests/auth/test_oauth_flow.py`<br/>`tests/codex_ml/tracking/` |

**Implementation Pattern:**
```python
# Code should use:
_ENABLE_LOOPBACK = os.environ.get("CODEX_LOCAL_LOOPBACK", "true").lower() == "true"
_DEFAULT_LOCALHOSTS = ("localhost", "127.0.0.1", "::1") if _ENABLE_LOOPBACK else ()
```

---

## SUMMARY MATRIX

### By Scope Classification

| Scope | Count | Variables |
|-------|-------|-----------|
| 🏢 **Repository-Level** | **8** | All variables are repository-scoped |
| 🏛️ **Organization-Level** | **0** | None at org level for Phase 6.2 |

### By Variable Type Classification

| Type | Count | Variables |
|------|-------|-----------|
| 📍 **Environment Action Variables** | **8** | All are environment action variables (need deployment in GitHub Settings → Variables) |
| 👤 **Agent Variables** | **0** | None are agent-specific variables |
| **Both** | **0** | No variables serve dual purposes |

### By Security Impact

| Level | Count | Variables |
|-------|-------|-----------|
| 🟢 **Low** | **5** | CODEX_REDIS_HOST, CODEX_OLLAMA_HOST, CODEX_MASTER_ADDR, CODEX_MASTER_PORT, CODEX_INFERENCE_SERVICE_PORT |
| 🟡 **Medium** | **1** | CODEX_INFERENCE_SERVICE_HOST |
| 🔴 **High** | **1** | CODEX_TRUSTED_HOSTS |
| 🔴 **Critical** | **1** | CODEX_LOCAL_LOOPBACK |

### By Environment Value Variability

| Category | Variables |
|----------|-----------|
| **Static (same across all envs)** | CODEX_MASTER_PORT, CODEX_INFERENCE_SERVICE_PORT |
| **Environment-Dependent** | CODEX_REDIS_HOST, CODEX_OLLAMA_HOST, CODEX_MASTER_ADDR, CODEX_INFERENCE_SERVICE_HOST, CODEX_TRUSTED_HOSTS, CODEX_LOCAL_LOOPBACK |

---

## PHASE 6.2 ACTION CHECKLIST

### Pre-Merge Actions (This Session)

- [ ] **6.2.A: Variable Definition Files** (10 min)
  - [ ] Create `.codex/pending_ops/variable_CODEX_REDIS_HOST.json`
  - [ ] Create `.codex/pending_ops/variable_CODEX_OLLAMA_HOST.json`
  - [ ] Create `.codex/pending_ops/variable_CODEX_MASTER_ADDR.json`
  - [ ] Create `.codex/pending_ops/variable_CODEX_MASTER_PORT.json`
  - [ ] Create `.codex/pending_ops/variable_CODEX_INFERENCE_SERVICE_HOST.json`
  - [ ] Create `.codex/pending_ops/variable_CODEX_INFERENCE_SERVICE_PORT.json`
  - [ ] Create `.codex/pending_ops/variable_CODEX_TRUSTED_HOSTS.json`
  - [ ] Create `.codex/pending_ops/variable_CODEX_LOCAL_LOOPBACK.json`

- [ ] **6.2.B: Code Replacements** (60 min) — 5 execution batches
  - [ ] **Batch 1 (10 min):** Redis, Ollama, Master Addr/Port
  - [ ] **Batch 2 (10 min):** Inference Service Host/Port
  - [ ] **Batch 3 (10 min):** Trusted Hosts
  - [ ] **Batch 4 (10 min):** Local Loopback (4 files)
  - [ ] **Batch 5 (20 min):** Test updates + validation

### Post-Merge Actions (Next Session Planning)

- [ ] **7.A: Variable Deployment** (via GitHub API, auto-triggered by workflow)
  - [ ] Monitor `.github/workflows/process-variable-intents.yml` execution
  - [ ] Verify all 8 variables created in GitHub Settings → Variables
  - [ ] Confirm `.codex/agent_context.json` refreshes with new variables

- [ ] **7.B: Code Validation** (1-2 hours post-merge)
  - [ ] Run full test suite with env vars unset (fallback mode)
  - [ ] Run full test suite with env vars set (custom values)
  - [ ] Run security validation (CODEX_LOCAL_LOOPBACK=false)

- [ ] **7.C: Documentation Update**
  - [ ] Create `.codex/LOCALHOST_REPLACEMENT_AUDIT.md` (audit trail)
  - [ ] Update `README.md` with environment variable configuration guide
  - [ ] Update deployment runbooks for Dev/Staging/Prod

---

## NEXT SESSION PLAN REFERENCE

**See:** `.codex/NEXT_SESSION_ACTION_PLAN.md` (to be created before merge)

**Key Guidance:**
1. ✅ Deploy `.codex/pending_ops/*.json` files via workflow (automated)
2. ✅ Run parallel validation tests (Phase 6.2.B.5)
3. ✅ Document replacement audit trail
4. ✅ Prepare PR merge guidance (main branch merge criteria)

---

**Document Status:** ✅ **READY FOR ACTION**  
**Authority:** @mbaetiong (D-tier autonomous)  
**Generated:** 2026-07-06T02:58:22Z
