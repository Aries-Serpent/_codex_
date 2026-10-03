# 📋 NEXT SESSION ACTION PLAN
## Phase 6.2 Completion & Post-Merge Execution
## PR Preparation & Main Branch Merge Guidance

**Created:** 2026-07-06T02:58:22Z  
**Target Execution:** Immediately following this session  
**Authority:** @mbaetiong (D-tier autonomous)  
**Scope:** Pre-merge validation → PR preparation → Main branch merge strategy

---

## 🎯 EXECUTIVE SUMMARY

This session has completed all planning for Phase 6 (Localhost Hardcode Migration). 
The next session must execute:

1. **Pre-Merge Execution** (60-80 min): Complete Phase 6.2 code replacements
2. **PR Preparation** (20-30 min): Code review, validation, final checks
3. **Merge Strategy** (guidance): Criteria and checklist for main branch merge

**Expected Outcome:** Merge-ready PR with all 8 environment variables implemented and tested

---

## 📍 PRE-MERGE EXECUTION PLAN (Next Session)

### PHASE 6.2.A: Variable Definition Files (10 min)

**Objective:** Create `.codex/pending_ops/*.json` files for GitHub API to deploy variables

**Action Steps:**

```bash
# Step 1: Create pending_ops directory (if not exists)
mkdir -p .codex/pending_ops

# Step 2: Create 8 variable definition files
# Each file follows this format:
cat > .codex/pending_ops/variable_CODEX_REDIS_HOST.json << 'EOF'
{
  "name": "CODEX_REDIS_HOST",
  "value": "localhost",
  "scope": "repository",
  "description": "Redis server hostname for distributed caching in RAG and ML training pipelines",
  "integration_point": "src/codex/rag/cache/distributed_cache.py",
  "version_introduced": "0.1.0",
  "security_impact": "low"
}
EOF

cat > .codex/pending_ops/variable_CODEX_OLLAMA_HOST.json << 'EOF'
{
  "name": "CODEX_OLLAMA_HOST",
  "value": "http://localhost",
  "scope": "repository",
  "description": "Ollama LLM server base URL for RAG inference",
  "integration_point": "src/codex/rag/providers/ollama_provider.py",
  "version_introduced": "0.1.0",
  "security_impact": "low"
}
EOF

cat > .codex/pending_ops/variable_CODEX_MASTER_ADDR.json << 'EOF'
{
  "name": "CODEX_MASTER_ADDR",
  "value": "localhost",
  "scope": "repository",
  "description": "Master node address for distributed PyTorch DDP initialization",
  "integration_point": "src/codex_ml/training/distributed.py",
  "version_introduced": "0.1.0",
  "security_impact": "low"
}
EOF

cat > .codex/pending_ops/variable_CODEX_MASTER_PORT.json << 'EOF'
{
  "name": "CODEX_MASTER_PORT",
  "value": "29500",
  "scope": "repository",
  "description": "Master node port for distributed PyTorch DDP communication",
  "integration_point": "src/codex_ml/training/distributed.py",
  "version_introduced": "0.1.0",
  "security_impact": "low"
}
EOF

cat > .codex/pending_ops/variable_CODEX_INFERENCE_SERVICE_HOST.json << 'EOF'
{
  "name": "CODEX_INFERENCE_SERVICE_HOST",
  "value": "127.0.0.1",
  "scope": "repository",
  "description": "Bind address for ML inference server HTTP listener",
  "integration_point": "src/codex_ml/serving/inference_server.py",
  "version_introduced": "0.1.0",
  "security_impact": "medium"
}
EOF

cat > .codex/pending_ops/variable_CODEX_INFERENCE_SERVICE_PORT.json << 'EOF'
{
  "name": "CODEX_INFERENCE_SERVICE_PORT",
  "value": "8000",
  "scope": "repository",
  "description": "Port for ML inference server HTTP listener",
  "integration_point": "src/codex_ml/serving/inference_server.py",
  "version_introduced": "0.1.0",
  "security_impact": "low"
}
EOF

cat > .codex/pending_ops/variable_CODEX_TRUSTED_HOSTS.json << 'EOF'
{
  "name": "CODEX_TRUSTED_HOSTS",
  "value": "localhost,127.0.0.1,testserver",
  "scope": "repository",
  "description": "Allowlist of trusted hostnames for inference server requests",
  "integration_point": "src/codex_ml/serving/inference_server.py",
  "version_introduced": "0.1.0",
  "security_impact": "high"
}
EOF

cat > .codex/pending_ops/variable_CODEX_LOCAL_LOOPBACK.json << 'EOF'
{
  "name": "CODEX_LOCAL_LOOPBACK",
  "value": "true",
  "scope": "repository",
  "description": "Feature gate for localhost/127.0.0.1/::1 allowlist in security policies",
  "integration_point": "src/safety/network_policy.py",
  "version_introduced": "0.1.0",
  "security_impact": "critical"
}
EOF
```

**Deliverable:** 8 JSON files in `.codex/pending_ops/`

**Verification:**
```bash
ls -la .codex/pending_ops/variable_*.json | wc -l
# Expected output: 8
```

---

### PHASE 6.2.B: Code Replacements (60 min)

**Objective:** Replace localhost hardcodes with os.environ.get() patterns

**Execution Strategy:** 5 sequential batches + 1 validation phase

#### Batch 1: Redis, Ollama, Master Addr/Port (10 min)

**Files to Update:**
- `src/codex/rag/cache/distributed_cache.py` — Add CODEX_REDIS_HOST support
- `src/cache/redis_cache.py` — Add CODEX_REDIS_HOST support
- `src/codex/rag/providers/ollama_provider.py` — Add CODEX_OLLAMA_HOST support
- `src/codex_ml/training/distributed.py` — Add CODEX_MASTER_ADDR + CODEX_MASTER_PORT
- `src/codex_ml/training/multi_node_orchestration.py` — Verify existing env var support

**Pattern to Apply:**
```python
import os

# For REDIS_HOST (string)
redis_host = redis_host or os.environ.get("CODEX_REDIS_HOST", "localhost")

# For OLLAMA_HOST (string)
host = host or os.environ.get("CODEX_OLLAMA_HOST", "http://localhost")

# For MASTER_ADDR (string, in dataclass)
@dataclass
class DistributedConfig:
    master_addr: str = field(default_factory=lambda: os.environ.get("CODEX_MASTER_ADDR", "localhost"))
    master_port: int = field(default_factory=lambda: int(os.environ.get("CODEX_MASTER_PORT", "29500")))
```

**Commit Message:**
```
fix(env): add CODEX_REDIS_HOST, CODEX_OLLAMA_HOST, CODEX_MASTER_ADDR/PORT env vars

- Replace hardcoded localhost with os.environ.get() patterns
- Maintain backward compatibility with fallback defaults
- Files: distributed_cache, redis_cache, ollama_provider, distributed config
- All variables scoped to repository-level configuration
```

---

#### Batch 2: Inference Service Host/Port (10 min)

**Files to Update:**
- `src/codex_ml/serving/inference_server.py` — Add CODEX_INFERENCE_SERVICE_HOST + PORT

**Pattern to Apply:**
```python
import os

# In app initialization
inference_host = os.environ.get("CODEX_INFERENCE_SERVICE_HOST", "127.0.0.1")
inference_port = int(os.environ.get("CODEX_INFERENCE_SERVICE_PORT", "8000"))
app.run(host=inference_host, port=inference_port)
```

**Commit Message:**
```
fix(env): add CODEX_INFERENCE_SERVICE_HOST and CODEX_INFERENCE_SERVICE_PORT env vars

- Replace hardcoded 127.0.0.1:8000 with environment variables
- Support different bind addresses across dev/staging/prod
- Maintain backward compatibility with secure defaults
- File: inference_server.py
```

---

#### Batch 3: Trusted Hosts (10 min)

**Files to Update:**
- `src/codex_ml/serving/inference_server.py` — Add CODEX_TRUSTED_HOSTS support

**Pattern to Apply:**
```python
import os

# Parse comma-separated trusted hosts
trusted_hosts_str = os.environ.get("CODEX_TRUSTED_HOSTS", "localhost,127.0.0.1,testserver")
DEFAULT_TRUSTED_HOSTS = [h.strip() for h in trusted_hosts_str.split(",")]
```

**Commit Message:**
```
fix(env): add CODEX_TRUSTED_HOSTS env var for Host header validation

- Replace hardcoded trusted hosts list with environment variable
- Support environment-specific Host header allowlists
- Security control for production Host header injection prevention
- File: inference_server.py
```

---

#### Batch 4: Local Loopback (10 min)

**Files to Update:**
- `src/safety/network_policy.py` — Add CODEX_LOCAL_LOOPBACK feature gate
- `src/codex/auth/github_app.py` — Add CODEX_LOCAL_LOOPBACK feature gate
- `src/codex_ml/tracking/mlflow_guard.py` — Add CODEX_LOCAL_LOOPBACK feature gate
- `src/codex_ml/tracking/guards.py` — Add CODEX_LOCAL_LOOPBACK feature gate

**Pattern to Apply:**
```python
import os

# Feature gate for localhost allowlist
_ENABLE_LOOPBACK = os.environ.get("CODEX_LOCAL_LOOPBACK", "true").lower() == "true"
_DEFAULT_LOCALHOSTS = ("localhost", "127.0.0.1", "::1") if _ENABLE_LOOPBACK else ()

# In validation logic:
if _ENABLE_LOOPBACK and _host in _DEFAULT_LOCALHOSTS:
    # Allow localhost in development
    pass
```

**Commit Message:**
```
fix(env): add CODEX_LOCAL_LOOPBACK feature gate for development bypass

- Control localhost allowlist across 4 security modules
- Enable fast iteration in development (true) vs strict production (false)
- Critical security control: prevents production-mode bypasses
- Files: network_policy.py, github_app.py, mlflow_guard.py, guards.py
```

---

#### Batch 5: Test Updates + Validation (20 min)

**Test Files to Update:**
- `tests/rag/cache/test_distributed_cache.py` — Add tests for CODEX_REDIS_HOST
- `tests/rag/providers/test_ollama_provider.py` — Add tests for CODEX_OLLAMA_HOST
- `tests/training/test_distributed_coverage.py` — Add tests for CODEX_MASTER_ADDR/PORT
- `tests/codex_ml/serving/` — Add tests for inference service env vars
- `tests/safety/test_network_policy.py` — Add tests for CODEX_LOCAL_LOOPBACK feature gate

**Test Pattern to Add:**
```python
import os
import pytest

def test_redis_host_env_var(monkeypatch):
    """Verify CODEX_REDIS_HOST overrides default."""
    monkeypatch.setenv("CODEX_REDIS_HOST", "custom-redis")
    cache = DistributedCache()
    assert cache.redis_host == "custom-redis"

def test_redis_host_fallback():
    """Verify fallback to localhost when env var unset."""
    cache = DistributedCache()
    assert cache.redis_host == "localhost"

def test_local_loopback_disabled(monkeypatch):
    """Verify localhost allowlist disabled in production mode."""
    monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "false")
    # Force reimport or reload to apply feature gate
    from src.safety import network_policy
    assert network_policy._DEFAULT_LOCALHOSTS == ()

def test_local_loopback_enabled(monkeypatch):
    """Verify localhost allowlist enabled in development mode."""
    monkeypatch.setenv("CODEX_LOCAL_LOOPBACK", "true")
    # Force reimport or reload to apply feature gate
    from src.safety import network_policy
    assert network_policy._DEFAULT_LOCALHOSTS == ("localhost", "127.0.0.1", "::1")
```

**Validation Commands:**
```bash
# Test all replacements with env vars unset (fallback mode)
pytest tests/ -v --tb=short

# Test with all env vars set to custom values
export CODEX_REDIS_HOST="test-redis"
export CODEX_OLLAMA_HOST="http://test-ollama:11434"
export CODEX_MASTER_ADDR="test-master"
export CODEX_MASTER_PORT="29501"
export CODEX_INFERENCE_SERVICE_HOST="0.0.0.0"
export CODEX_INFERENCE_SERVICE_PORT="8001"
export CODEX_TRUSTED_HOSTS="test.example.com"
export CODEX_LOCAL_LOOPBACK="false"
pytest tests/ -v --tb=short

# Test security validation (prod mode)
export CODEX_LOCAL_LOOPBACK="false"
pytest tests/safety/test_network_policy.py -v --tb=short
```

**Commit Message:**
```
test(env): add comprehensive tests for all 8 environment variables

- Test fallback behavior when env vars unset
- Test override behavior when env vars set
- Test security feature gates (CODEX_LOCAL_LOOPBACK)
- Coverage: Redis, Ollama, Master Addr/Port, Inference Service, Trusted Hosts, Loopback
- All tests pass in both env-var-set and fallback modes
```

---

### VALIDATION CHECKLIST (Before Commit)

- [ ] All 8 `.codex/pending_ops/*.json` files created and valid JSON
- [ ] All 4 code modules updated with `os.environ.get()` patterns
- [ ] All 3 test files updated with comprehensive test coverage
- [ ] Full test suite passes: `pytest tests/ -v`
- [ ] No secrets or credentials accidentally committed
- [ ] Linting passes: `ruff check --fix src/ tests/`
- [ ] Type checking passes: `mypy src/` (if applicable)
- [ ] No hardcoded localhost values remain in critical paths
- [ ] Documentation comments explain env var purpose in code

**Run Pre-Commit Validation:**
```bash
python scripts/ci/pre-commit-hooks.py
python scripts/ci/enforce_actions_versions.py
python scripts/ci/session_wrapup_autofix.py --check --pr-number <PR>
```

---

## 🔀 PR PREPARATION (Next Session)

### PR Title
```
feat(env): replace 24 localhost hardcodes with 8 repository environment variables

- Phase 6.2: Localhost hardcode migration
- 8 new repository variables (CODEX_REDIS_HOST, CODEX_OLLAMA_HOST, etc.)
- Backward compatible with localhost fallbacks
- Production-safe with CODEX_LOCAL_LOOPBACK feature gate
- Fixes: #<issue_number> (if applicable)
```

### PR Description Template

```markdown
## 🎯 Overview

This PR implements Phase 6.2 of the Multi-Agent Campaign: migration of 24 critical 
localhost hardcodes to 8 repository environment variables, enabling dev/staging/prod 
environment control.

## 📊 Changes Summary

| Category | Count | Details |
|----------|-------|---------|
| Environment Variables | 8 | CODEX_REDIS_HOST, CODEX_OLLAMA_HOST, CODEX_MASTER_ADDR/PORT, CODEX_INFERENCE_SERVICE_HOST/PORT, CODEX_TRUSTED_HOSTS, CODEX_LOCAL_LOOPBACK |
| Files Modified | ~12 | src/codex/rag/, src/codex_ml/training/, src/codex_ml/serving/, src/safety/ |
| Tests Updated | 5 | Distributed cache, Ollama provider, Training config, Inference server, Security policy |
| Hardcodes Replaced | 24 critical + 220 non-critical | All with os.environ.get() patterns |

## ✨ Key Features

### 1. Environment Variable Support
- ✅ CODEX_REDIS_HOST — Redis caching for distributed systems
- ✅ CODEX_OLLAMA_HOST — RAG inference endpoint
- ✅ CODEX_MASTER_ADDR / CODEX_MASTER_PORT — Distributed training bootstrap
- ✅ CODEX_INFERENCE_SERVICE_HOST / PORT — ML inference server bind
- ✅ CODEX_TRUSTED_HOSTS — Host header security validation
- ✅ CODEX_LOCAL_LOOPBACK — Development-only security bypass feature gate

### 2. Backward Compatibility
- All variables have localhost defaults in code
- Zero breaking changes to existing deployments
- Fallback behavior preserves current localhost-based development workflow

### 3. Security-First Design
- CODEX_LOCAL_LOOPBACK prevents production-mode security bypasses
- CODEX_TRUSTED_HOSTS controls Host header injection attacks
- All variables are configuration (no secrets or credentials)
- Safe for version control and public repositories

### 4. Comprehensive Testing
- Unit tests: Each variable fallback + override paths
- Integration tests: Full training/serving pipelines with custom values
- Security tests: CODEX_LOCAL_LOOPBACK production mode validation
- All tests pass in both env-var-set and fallback modes

## 🔍 Testing

### Pre-Merge Validation
```bash
# Fallback mode (env vars unset)
pytest tests/ -v --tb=short

# Override mode (env vars set)
export CODEX_REDIS_HOST="test-redis"
export CODEX_LOCAL_LOOPBACK="false"
pytest tests/ -v --tb=short

# Linting & type checks
ruff check --fix src/ tests/
mypy src/
pre-commit run --all-files
```

### Post-Merge Validation (Phase 7)
```bash
# Monitor .github/workflows/process-variable-intents.yml execution
# Verify all 8 variables created in GitHub Settings → Variables
# Run Phase 7 validation tests (2 days post-merge)
```

## 📋 Deployment Runbook

### Development (No Action)
- Defaults use localhost
- No environment variable setup required

### Staging (Post-Merge)
```bash
# GitHub Settings → Variables → Add/Update:
CODEX_REDIS_HOST = "redis-staging.internal.codex"
CODEX_OLLAMA_HOST = "http://ollama-staging.internal.codex:11434"
CODEX_MASTER_ADDR = "training-master-staging.internal.codex"
CODEX_INFERENCE_SERVICE_HOST = "0.0.0.0"
CODEX_TRUSTED_HOSTS = "*.staging.codex.svc.cluster.local"
CODEX_LOCAL_LOOPBACK = "false"
```

### Production (Post-Merge)
```bash
# GitHub Settings → Variables → Add/Update:
CODEX_REDIS_HOST = "redis-primary.codex.svc.cluster.local"
CODEX_OLLAMA_HOST = "http://ollama.codex.svc.cluster.local:11434"
CODEX_MASTER_ADDR = "training-master-0.training.codex.svc.cluster.local"
CODEX_INFERENCE_SERVICE_HOST = "0.0.0.0"
CODEX_TRUSTED_HOSTS = "*.codex.svc.cluster.local,codex.prod"
CODEX_LOCAL_LOOPBACK = "false"
```

## 🔗 Related Issues

- Closes: #<issue_number> (Localhost hardcode migration)
- Relates to: Phase 6 Multi-Agent Campaign
- Depends on: Phase 6.1 (test file migration — separate PR)

## ✅ Checklist

- [x] All 8 environment variables specified
- [x] Code replacements follow os.environ.get() pattern
- [x] All hardcodes replaced with fallback defaults
- [x] Comprehensive test coverage added
- [x] CODEX_LOCAL_LOOPBACK feature gate implemented
- [x] No secrets committed
- [x] All tests passing (fallback + override modes)
- [x] Documentation updated
- [x] Backward compatibility verified
- [x] .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md updated
- [x] CHANGELOG.md updated
- [x] Pre-commit hooks passing

## 📖 Documentation

- **Specification:** `.codex/ENV_VARS_IMPLEMENTATION_SPECIFICATION.md`
- **Analysis:** `.codex/ENVIRONMENT_VARIABLES_ANALYSIS_TABLE.md`
- **Campaign Plan:** `.codex/MULTI_AGENT_CAMPAIGN_PLAN_PHASES_6_7_8_9.md`
- **Pending Ops:** `.codex/pending_ops/variable_*.json` (8 files)

## 🔐 Security Review

✅ No secrets introduced
✅ All variables are configuration endpoints
✅ Backward compatible (fallback to localhost)
✅ CODEX_LOCAL_LOOPBACK enforces production-mode strictness
✅ Zero breaking changes to public APIs
✅ Safe for version control and distribution

## 🚀 Post-Merge (Phase 7+)

### Immediate (Day 0-1)
- Monitor workflow deployment of 8 variables to GitHub repository settings
- Verify `.codex/agent_context.json` updated with new variables
- Run validation tests with live variables

### Short-term (Day 2-3)
- Phase 7: Local Development Environment Validation
- Phase 8: Offline-First Consumption Patterns

### Medium-term (Day 4-5)
- Phase 9: External User Onboarding Metrics

## 📞 Questions?

See [ENVIRONMENT_VARIABLES_ANALYSIS_TABLE.md](.codex/ENVIRONMENT_VARIABLES_ANALYSIS_TABLE.md) 
for detailed specifications of all 8 variables.
```

---

## ✅ MAIN BRANCH MERGE CRITERIA

### Pre-Merge Checklist (✅ All Required)

- [ ] **Code Quality**
  - [ ] All tests passing: `pytest tests/ -v`
  - [ ] Linting passes: `ruff check src/ tests/`
  - [ ] Type checking passes (if applicable)
  - [ ] No hardcoded localhost values in critical paths
  - [ ] All imports organized per codebase conventions

- [ ] **Compliance**
  - [ ] .codex/archive/reports/AGENT_ACCOUNTABILITY_REPORT.md updated (REQ-4)
  - [ ] CHANGELOG.md updated (REQ-5)
  - [ ] Both files in same commit as final code changes
  - [ ] `session_wrapup_autofix.py --check --pr-number <PR>` passing
  - [ ] No deferral language in commit messages or PR description

- [ ] **Security**
  - [ ] No secrets or credentials committed
  - [ ] `detect-secrets` scan passing
  - [ ] `github-mcp-server get_code_scanning_alert` — 0 critical/high alerts
  - [ ] CODEX_LOCAL_LOOPBACK feature gate properly implemented
  - [ ] All 8 variables marked as non-secret configuration

- [ ] **Documentation**
  - [ ] PR description complete with deployment runbook
  - [ ] `.codex/pending_ops/*.json` files created and valid JSON
  - [ ] All 8 variables documented in code comments
  - [ ] Integration points referenced in code
  - [ ] Test coverage documented

- [ ] **Approval & Review**
  - [ ] At least 1 approval from maintainer or code review agent
  - [ ] All blocking review comments resolved
  - [ ] WEC (Workflow Execution Checklist) section present in PR body
  - [ ] All required workflows passing in WEC

---

## 📊 MERGE TO MAIN STRATEGY

### Merge Type
**Squash Merge** (recommended) or **Create a Merge Commit**

**Reasoning:**
- Single logical change (Phase 6.2 completion)
- Clean commit history with comprehensive message
- Easier to revert if needed (single commit)

### Pre-Merge Final Checks

```bash
# 1. Ensure branch is up-to-date with main
git fetch origin main
git rebase origin/main

# 2. Run full test suite one final time
pytest tests/ -v --tb=short

# 3. Verify all compliance requirements
python scripts/ci/session_wrapup_autofix.py --check --pr-number <PR>

# 4. Scan for secrets one final time
python scripts/ci/detect_secrets.py --baseline .secrets.baseline

# 5. Check for deferral language
python scripts/ci/check_deferral_language.py

# 6. Verify WEC section in PR body
cat <(gh pr view <PR> --json body) | grep "## 🔄 Workflow Execution Checklist"
```

### Merge Command (When Ready)

```bash
# Option 1: Squash merge (recommended)
gh pr merge <PR> --squash --auto

# Option 2: Create merge commit
gh pr merge <PR> --create-merge-commit --auto

# Option 3: Manual merge (if auto not available)
git checkout main
git pull origin main
git merge --squash <branch-name>
git commit -m "feat(env): Phase 6.2 localhost hardcodes → 8 repository env vars"
git push origin main
```

### Post-Merge Verification

```bash
# 1. Verify commit on main
git log main -1 --oneline | grep "Phase 6.2\|env vars"

# 2. Verify workflows triggered
gh run list --status pending

# 3. Wait for process-variable-intents.yml to complete
# (Creates 8 variables in GitHub Settings → Variables)

# 4. Verify variables in .codex/agent_context.json
cat .codex/agent_context.json | jq '.variables | keys | map(select(startswith("CODEX_")))'

# 5. Confirm all Phase 6.2 tasks complete
gh issue comment <ISSUE> --body "Phase 6.2 complete: 8 env vars deployed, 24 hardcodes replaced"
```

---

## 📌 NEXT SESSION EXECUTION ORDER

### Session Start (5 min)
1. ✅ Load mandatory pre-load files (AGENTIC_REPO_STATE.md, etc.)
2. ✅ Read `.codex/NEXT_SESSION_ACTION_PLAN.md` (this document)
3. ✅ Confirm D-mode authorization from @mbaetiong
4. ✅ Report current state

### Execution Phase 1: Pre-Merge (60-80 min)
1. **6.2.A (10 min):** Create 8 `.codex/pending_ops/*.json` files
2. **6.2.B (60 min):** Execute 5 batches of code replacements + tests
3. **Validation (10 min):** Run full test suite + compliance checks

### Execution Phase 2: PR Preparation (20-30 min)
1. **Code Review (5 min):** Verify no deferral language, no secrets
2. **Final Testing (10 min):** `pytest tests/` + `ruff check` + `mypy`
3. **PR Body (10 min):** Fill in description from template above
4. **WEC Section (5 min):** Add Workflow Execution Checklist

### Execution Phase 3: Merge Preparation (5-10 min)
1. **Create PR:** If not already created
2. **Set Auto-Approve (optional):** Use `wec:auto-approve` label if authorized
3. **Monitor Workflows:** Wait for CI to pass
4. **Execute Merge:** Use `gh pr merge` or GitHub UI

### Post-Merge (Day 1-2)
1. **Verify Variable Deployment:** Confirm all 8 in GitHub Settings
2. **Run Phase 7 Tests:** Local environment validation
3. **Document Audit Trail:** Create `.codex/LOCALHOST_REPLACEMENT_AUDIT.md`

---

## 🎯 SUCCESS CRITERIA

✅ **Phase 6.2 Complete When:**
- [ ] All 8 environment variables implemented in code
- [ ] All 24 critical hardcodes replaced with os.environ.get()
- [ ] All tests passing (fallback + override modes)
- [ ] PR merged to main branch
- [ ] Workflows deployed 8 variables to GitHub Settings
- [ ] `.codex/agent_context.json` reflects new variables
- [ ] No breaking changes introduced
- [ ] Zero security vulnerabilities
- [ ] Documentation complete

✅ **Ready for Phases 7-9 When:**
- [ ] All Phase 6 success criteria met
- [ ] 2-day post-merge stabilization period complete
- [ ] Phase 7 validation tests passing
- [ ] Lead agents assigned for Phases 7-9

---

## 📞 ESCALATION CONTACTS

- **Session Authority:** @mbaetiong (D-tier autonomous)
- **Code Review:** Use `code-review` agent
- **CI Failures:** Use `ci-failure-resolution-agent`
- **Test Failures:** Use `autonomous-test-healer-agent`
- **Blocking Issues:** Post issue with `[ESCALATION]` tag

---

**Document Status:** ✅ **READY FOR NEXT SESSION EXECUTION**  
**Authority:** @mbaetiong (all plans approved)  
**Created:** 2026-07-06T02:58:22Z  
**Next Review:** After Phase 6.2.B.5 validation completion

