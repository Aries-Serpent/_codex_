# 🤖 Multi-Agent Campaign Implementation Plan
## Phases 6→7→8→9: Non-Blocking Code Quality Improvements & Future Roadmap

**Document Version:** 1.0.0  
**Date Created:** 2026-07-06T02:29Z  
**Authority:** @mbaetiong (D-tier autonomous, DO NOT DEFER)  
**Status:** PLANNING PHASE — Ready for Sequential Phase Execution  
**Campaign Scope:** Phases 6 (Current, Non-Blocking Code Quality) + Phases 7-9 (Future Planning Post-Merge)

---

## 📋 EXECUTIVE SUMMARY

This comprehensive campaign plan outlines:

1. **Phase 6: Non-Blocking Code Quality Improvements** (Current, ~80 minutes total)
   - TASK 6.1: Move 12 test files from `src/` to `tests/` (~20 min)
   - TASK 6.2: Replace 24 localhost hardcodes with environment variables (~60 min)
   - Environment variable implementation requirements and documentation

2. **Phase 7-9: Future Campaign Roadmap** (Post-Merge Planning)
   - Phase 7: Local development environment validation
   - Phase 8: Offline-first consumption patterns validation  
   - Phase 9: External user onboarding success metrics

**Campaign Characteristics:**
- ✅ **Non-blocking**: Can be deferred without blocking current critical work
- ✅ **High-value**: Improves code quality, configurability, and maintainability
- ✅ **Parallelizable**: Both tasks can be executed in parallel by specialized agents
- ✅ **Well-scoped**: Clear acceptance criteria and agent assignment
- ✅ **Production-ready**: No breaking changes to public APIs

---

## PHASE 6: NON-BLOCKING CODE QUALITY IMPROVEMENTS

### Task 6.1: Move Test Files from src/ to tests/

**Status:** ✅ READY FOR EXECUTION  
**Est. Effort:** 20 minutes  
**Lead Agent:** `test-alignment-fixer` or `autonomous-test-healer-agent`  
**Dependencies:** None (can run in parallel with Task 6.2)

#### Scope & Files

**12 test files currently in src/ that MUST move to tests/:**

```
src/restore_pipeline/tests/test_restore_pipeline.py         → tests/restore_pipeline/
src/restore_pipeline/tests/conftest.py                       → tests/restore_pipeline/
src/quantum/testing.py                                       → tests/quantum/ (or src/quantum/tests/)
src/codex/consolidation/test_fixtures.py                     → tests/consolidation/
src/codex_ml/ast/tests/test_config.py                        → tests/codex_ml/ast/
src/codex_ml/ast/tests/test_analyzers.py                     → tests/codex_ml/ast/
src/codex_ml/ast/tests/test_node.py                          → tests/codex_ml/ast/
src/codex_ml/ast/tests/test_storage.py                       → tests/codex_ml/ast/
src/codex_ml/ast/tests/test_graph.py                         → tests/codex_ml/ast/
src/codex_ml/training/ab_testing.py                          → tests/codex_ml/training/ (or keep if not purely test)
src/codex_ml/experiments/ab_testing.py                       → tests/codex_ml/experiments/ (or keep if not purely test)
src/cognitive_brain/quantum/ab_testing.py                    → tests/cognitive_brain/quantum/ (or keep if not purely test)
src/tests/test_session_embeddings_phase4.py                  → tests/session_embeddings/
src/tests/test_concurrency_protection.py                     → tests/concurrency/
```

#### Key Actions

1. **Audit & Classify** (5 min)
   - Verify each file is purely a test (test_* prefix or testing module)
   - Identify imports from src/ that will need path adjustments
   - Check for conftest.py files (need special handling to preserve fixture discovery)
   - Identify ab_testing modules that may be production code (preserve in src/)

2. **Create Target Directory Structure** (3 min)
   - Create `tests/restore_pipeline/`
   - Create `tests/codex_ml/ast/`
   - Update `tests/` __init__.py files as needed
   - Preserve conftest.py at proper hierarchy level

3. **Move Files & Update Imports** (10 min)
   - Move files to proper tests/ location
   - Update import statements in moved files (from `src.*` → relative imports)
   - Update import statements in remaining src/ files that referenced test modules
   - Verify no `src.*` imports in test files (use relative/absolute test paths)

4. **Verify & Validate** (2 min)
   - Run pytest discovery to confirm all tests found
   - Run test suite to ensure no path issues
   - Verify coverage metrics unchanged

#### Success Criteria

- ✅ All 12 test files moved to `tests/` (or proper subdirectories)
- ✅ No import errors in test execution
- ✅ Test discovery works: `pytest --collect-only` finds all tests
- ✅ All tests pass with same coverage metrics
- ✅ conftest.py files positioned for proper fixture discovery
- ✅ No changes to test logic or assertions

#### Special Considerations

**ab_testing.py modules:** Need to verify these are NOT production code that's being imported:
- `src/codex_ml/training/ab_testing.py`
- `src/codex_ml/experiments/ab_testing.py`  
- `src/cognitive_brain/quantum/ab_testing.py`

If these are imported by production code, **do not move**. If purely test utilities, move to tests/.

---

### Task 6.2: Replace 24 Localhost Hardcodes with Environment Variables

**Status:** ✅ READY FOR EXECUTION  
**Est. Effort:** 60 minutes  
**Lead Agent:** Custom agent (see assignment below)  
**Dependencies:** Environment variable implementation (see Section III)

#### Scope & Hardcode Audit

**Found: 246 total localhost occurrences across 94 files**

**Primary hardcodes to REPLACE (24 critical):**

The 24 critical localhost hardcodes are those with hardcoded defaults in function signatures or constant definitions:

```python
# CRITICAL (must replace with env vars):
1. src/codex/rag/providers/ollama_provider.py
   - host: str = "http://localhost" (line ~XX)
   
2. src/codex/rag/cache/distributed_cache.py
   - redis_host: str = "localhost" (line ~XX)
   - redis_host="localhost" in function calls
   
3. src/codex/utils/dict_operations.py
   - default='localhost' in nested_get() examples
   
4. src/codex/auth/github_app.py
   - if _host in ("", "localhost", "127.0.0.1", "::1"): (security check)
   
5. src/codex/archive/dal.py
   - config.setdefault("host", "localhost")
   
6. src/codex_ml/serving/inference_server.py
   - DEFAULT_TRUSTED_HOSTS = ["localhost", "127.0.0.1", "testserver"]
   
7. src/codex_ml/training/multi_node_orchestration.py
   - master_addr = os.environ.get("MASTER_ADDR", "localhost")
   - master_port defaults
   
8. src/codex_ml/training/distributed.py
   - master_addr: str = "localhost"
   
9. src/cache/redis_cache.py
   - host: str = "localhost"
   
10. src/safety/network_policy.py
    - _DEFAULT_LOCALHOSTS: tuple[str, ...] = ("localhost", "127.0.0.1", "::1")

11. src/codex_ml/tracking/writers.py
    - localhost detection logic
    
12. src/codex_ml/tracking/mlflow_guard.py
    - localhost validation and defaults
    
13. src/codex_ml/tracking/guards.py
    - localhost in allowlist checks
    
14. scripts/deployment/health_check_runner.py
    - default="localhost" in argparse
    
15. scripts/launch_distributed.py
    - default="localhost"

[CONTINUES with 9 more critical files...]
```

**Secondary occurrences (non-critical, mostly in docstrings/examples):**
- 180+ occurrences in comments, docstrings, examples
- These are OK to leave as-is (documentation examples)
- Only replace those that are ACTIVE DEFAULT VALUES in code paths

#### New Environment Variables Required

**Repository-Level Variables (MUST BE IMPLEMENTED):**

```yaml
# CODEX Repository Variables (github.com/Aries-Serpent/_codex_/settings/variables)

### Service Connectivity
CODEX_REDIS_HOST:
  default: "localhost"
  production: "redis.internal.codex"
  description: "Redis cache host for distributed_cache.py"
  scope: "Core services"

CODEX_OLLAMA_HOST:
  default: "http://localhost"
  production: "http://ollama.internal.codex"
  description: "Ollama LLM inference server host"
  scope: "RAG providers"

CODEX_MASTER_ADDR:
  default: "localhost"
  production: "primary-node.training.codex"
  description: "Master node address for distributed PyTorch training"
  scope: "ML training"

CODEX_MASTER_PORT:
  default: "29500"
  production: "29500"
  description: "Master node port for distributed training (stable across envs)"
  scope: "ML training"

### HTTP Services  
CODEX_INFERENCE_SERVICE_HOST:
  default: "127.0.0.1"
  production: "inference.codex.svc.cluster.local"
  description: "ML inference server bind address"
  scope: "Serving"

CODEX_INFERENCE_SERVICE_PORT:
  default: "8000"
  production: "8000"
  description: "ML inference server port"
  scope: "Serving"

CODEX_API_SERVER_HOST:
  default: "127.0.0.1"
  production: "api.codex.svc.cluster.local"
  description: "API server bind address"
  scope: "API services"

CODEX_API_SERVER_PORT:
  default: "8765"
  production: "8765"
  description: "Copilot CLI API server port"
  scope: "API services"

### Development & Validation
CODEX_TRUSTED_HOSTS:
  default: "localhost,127.0.0.1,testserver"
  production: "codex.internal.io,*.svc.cluster.local"
  format: "comma-separated list"
  description: "Allowlist for inference server HTTP requests"
  scope: "Security, serving"

CODEX_LOCAL_LOOPBACK:
  default: "true"
  production: "false"
  description: "Enable localhost/127.0.0.1/::1 allowlist checks (dev/test only)"
  scope: "Security policy"

CODEX_DAL_DB_HOST:
  default: "localhost"
  production: "postgres.internal.codex"
  description: "Archive DAL database host"
  scope: "Data layer"
```

**Organization-Level Variables (Optional, for future monorepo/multi-service):**

```yaml
# GitHub Organization Variables (github.com/orgs/Aries-Serpent/settings/variables)

ORG_REDIS_CLUSTER_ENDPOINT:
  scope: "organization-wide"
  default: ""
  description: "Optional: org-wide Redis cluster endpoint (overrides repo CODEX_REDIS_HOST)"

ORG_INFERENCE_GATEWAY:
  scope: "organization-wide"
  default: ""
  description: "Optional: org-wide inference gateway (overrides repo CODEX_OLLAMA_HOST)"
```

#### Implementation Plan (60 minutes)

**Phase 6.2.A: Environment Variable Setup (10 min)**
1. Document all 8 new repo variables above
2. Pre-create variables in `.codex/pending_ops/` for variable-sync workflow
3. Verify `.codex/agent_context.json` will be updated with new variables

**Phase 6.2.B: Core Replacements (35 min)**

**Batch 1 (10 min): High-Priority Service Defaults**
- `src/codex/rag/cache/distributed_cache.py` - CODEX_REDIS_HOST
- `src/codex/rag/providers/ollama_provider.py` - CODEX_OLLAMA_HOST
- `src/codex_ml/training/multi_node_orchestration.py` - CODEX_MASTER_ADDR, CODEX_MASTER_PORT
- `src/codex_ml/training/distributed.py` - CODEX_MASTER_ADDR
- `src/cache/redis_cache.py` - CODEX_REDIS_HOST

**Batch 2 (10 min): API & Serving Defaults**
- `src/codex_ml/serving/inference_server.py` - CODEX_INFERENCE_SERVICE_HOST, PORT, CODEX_TRUSTED_HOSTS
- `src/mcp/server/http.py` - CODEX_API_SERVER_HOST/PORT (if hardcoded)
- `src/mcp/server/run.py` - CODEX_API_SERVER_HOST/PORT
- `cognitive_app/src/server/cli_api_server.py` - CODEX_API_SERVER_HOST/PORT

**Batch 3 (10 min): Data Layer & Security**
- `src/codex/archive/dal.py` - CODEX_DAL_DB_HOST
- `src/safety/network_policy.py` - CODEX_LOCAL_LOOPBACK
- `src/codex/auth/github_app.py` - localhost check (make conditional on CODEX_LOCAL_LOOPBACK)
- `src/codex_ml/tracking/mlflow_guard.py` - CODEX_LOCAL_LOOPBACK
- `src/codex_ml/tracking/guards.py` - CODEX_LOCAL_LOOPBACK

**Batch 4 (5 min): Scripts & Utilities**
- `scripts/deployment/health_check_runner.py` - environment variables
- `scripts/launch_distributed.py` - CODEX_MASTER_ADDR defaults

**Phase 6.2.C: Refactoring & Documentation (10 min)**

1. Create utility helper in `src/codex/utils/env_defaults.py`:
   ```python
   # New module for centralized localhost-to-env-var management
   def get_redis_host() -> str:
       return os.environ.get("CODEX_REDIS_HOST", "localhost")
   
   def get_ollama_host() -> str:
       return os.environ.get("CODEX_OLLAMA_HOST", "http://localhost")
   
   def get_master_addr() -> str:
       return os.environ.get("CODEX_MASTER_ADDR", "localhost")
   
   # ... etc
   ```

2. Update `src/codex/utils/env_vars.py` docs with new patterns

3. Create `.codex/LOCALHOST_REPLACEMENT_AUDIT.md` documenting:
   - 24 critical replacements made
   - 180+ documentation examples left unchanged
   - New environment variables created
   - Fallback behavior preserved

**Phase 6.2.D: Testing & Validation (5 min)**

1. Run affected test suites:
   ```bash
   pytest tests/rag/cache/ -v
   pytest tests/codex_ml/training/ -v
   pytest tests/safety/ -v
   pytest tests/codex_ml/serving/ -v
   ```

2. Verify environment variable fallbacks:
   ```bash
   # Test with env var set
   CODEX_REDIS_HOST=custom-redis pytest tests/rag/cache/
   
   # Test without (should fall back to localhost)
   pytest tests/rag/cache/
   ```

3. Integration test (health check runner):
   ```bash
   CODEX_INFERENCE_SERVICE_HOST=127.0.0.1 \
   CODEX_INFERENCE_SERVICE_PORT=8000 \
   python scripts/deployment/health_check_runner.py
   ```

#### Success Criteria

- ✅ 24 critical localhost hardcodes replaced with os.environ.get() calls
- ✅ All replacements have sensible defaults (backward compatible)
- ✅ 8 new environment variables documented and ready for repo configuration
- ✅ New helper utility `src/codex/utils/env_defaults.py` created
- ✅ All affected tests pass with both env-var-set and default-fallback paths
- ✅ Documentation updated in `.codex/LOCALHOST_REPLACEMENT_AUDIT.md`
- ✅ `.codex/agent_context.json` updated with new variable definitions

---

## PHASE 7-9: FUTURE CAMPAIGN ROADMAP (Post-Merge Planning)

### Phase 7: Local Development Environment Validation

**Objective:** Ensure reproducible local development setups with validated environment configurations.

**Scope:**
- Develop local environment template (`.codex/dev-environment-template.md`)
- Create environment validation script (`scripts/validate_local_env.py`)
- Document required tools, versions, and configuration
- Create quickstart guide for new contributors

**Lead Agent:** `configuration-management-agent` or `config-validator`

**Estimated Effort:** 4-6 hours (separate session)

**Key Deliverables:**
1. `.codex/LOCAL_DEVELOPMENT_SETUP.md`
2. `scripts/validate_local_env.py` (validates all dependencies + env vars)
3. `scripts/setup_local_dev.sh` (automated environment provisioning)
4. `.env.example` file with all required variables
5. Docker Compose files for containerized local development

**Success Metrics:**
- New contributors can set up full dev environment in <30 minutes
- `validate_local_env.py` detects 100% of common misconfigurations
- All CI/CD tests pass locally before commit

---

### Phase 8: Offline-First Consumption Patterns Validation

**Objective:** Validate that the "core" package (8-15 MB, stdlib-only) works in air-gapped environments.

**Scope:**
- Create offline wheelhouse (all transitive dependencies with checksums)
- Test installation in isolated network environment
- Validate all 10 stable public APIs work offline
- Document air-gapped deployment procedures

**Lead Agent:** `unified-security-scanner` + `packaging-validation-agent`

**Estimated Effort:** 6-8 hours (separate session)

**Key Deliverables:**
1. Offline wheelhouse generation script
2. Air-gapped installation test suite
3. `.codex/OFFLINE_CONSUMPTION_VALIDATION_REPORT.md`
4. Updated `ISOLATED_DEPLOYMENT.md` with procedures
5. Dependency graph documentation for offline scenarios

**Success Metrics:**
- Wheelhouse contains 100% of transitive deps
- Installation succeeds without network access
- All public APIs functional offline (zero network fallback triggers)
- Documentation rated "sufficient for external users"

**Related Memories:**
- ✅ Lockfile-based reproducible distribution (uv.lock + cyclonedx SBOM)
- ✅ Offline-first design principle (stdlib-only core, deny-by-default network)

---

### Phase 9: External User Onboarding Success Metrics

**Objective:** Measure and improve external user adoption, satisfaction, and time-to-first-value.

**Scope:**
- Create external onboarding metrics dashboard
- Implement usage telemetry (opt-in, privacy-first)
- Document common integration patterns
- Create runnable examples for key use cases
- Measure time-to-first-value by role (data scientist, engineer, MLOps)

**Lead Agent:** `documentation-quality-agent` + `post-merge-doc-alignment-agent`

**Estimated Effort:** 8-10 hours (separate session, multi-track possible)

**Key Deliverables:**
1. `.codex/EXTERNAL_ADOPTION_METRICS.md` (instrumentation plan)
2. `docs/external/GETTING_STARTED_BY_ROLE.md`
3. 5+ runnable example scripts in `examples/`
4. Integration guide for popular ML platforms (Hugging Face, MLflow, etc.)
5. FAQ document addressing "why would I use this?" for external users
6. Quarterly adoption metrics dashboard (GitHub Pages)

**Success Metrics:**
- >90% of external users complete first integration within 2 hours
- Net Promoter Score (NPS) >40 from beta users
- <15 minute time-to-first-API-call for standard use cases
- Documentation rated A+ by external technical reviewers

---

## IV. AGENT ASSIGNMENT & SEQUENCING

### Phase 6: Current Session (Parallel Execution)

**Task 6.1: Test File Migration**
- **Lead Agent:** `autonomous-test-healer-agent`
- **Supporting Agents:** `test-alignment-fixer`, `code-analysis-agent`
- **Execution:** Parallel with Task 6.2
- **Duration:** ~20 minutes
- **Artifacts:** Migration report, before/after test discovery output

**Task 6.2: Localhost → Environment Variables**
- **Lead Agent:** Custom multi-batch agent (parallel batch execution)
  - Option A: `code-analysis-agent` + `config-validator` + `dependency-conflict-agent`
  - Option B: Single agent with batch orchestration
- **Supporting Agents:** `packaging-validation-agent` (verify no breaking changes)
- **Execution:** Parallel with Task 6.1
- **Duration:** ~60 minutes total (5 parallel batches × 12 min max)
- **Artifacts:** 
  - `.codex/LOCALHOST_REPLACEMENT_AUDIT.md`
  - `.codex/ENV_VARS_IMPLEMENTATION_SPEC.md`
  - New variable definitions for variable-sync workflow

### Phase 7: Scheduled Post-Merge Session

**Tentative Date:** 2026-07-08T10:00Z (2 days post-merge)  
**Lead Agent:** `config-validator`  
**Supporting Agents:** `documentation-quality-agent`, `policy-coach-agent`  
**Parallel Tracks:** Single track (4-6 hours continuous)

### Phase 8: Scheduled Post-Merge Session

**Tentative Date:** 2026-07-09T10:00Z (3 days post-merge)  
**Lead Agent:** `unified-security-scanner`  
**Supporting Agents:** `packaging-validation-agent`, `ci-testing-agent`  
**Parallel Tracks:** 2 tracks (build wheelhouse + test isolation in parallel)

### Phase 9: Scheduled Post-Merge Session

**Tentative Date:** 2026-07-10T10:00Z (4 days post-merge)  
**Lead Agent:** `documentation-quality-agent`  
**Supporting Agents:** `post-merge-doc-alignment-agent`, `claim-verification-agent`  
**Parallel Tracks:** 3 tracks (examples + docs + metrics in parallel)

---

## V. ENVIRONMENT VARIABLE IMPLEMENTATION SPECIFICATION

### Variable Creation & Deployment

**Workflow:** `.github/workflows/process-variable-intents.yml`

**Steps:**
1. Write variable definitions to `.codex/pending_ops/variable_CODEX_REDIS_HOST.json`
2. Run `engine-tools-report_progress` (triggers workflow via commit)
3. Workflow detects pending_ops files → creates GitHub repository variables
4. `.codex/agent_context.json` auto-syncs with new variables
5. Next session has access to live variables in agent context

**Variable Template Format:**

```json
{
  "name": "CODEX_REDIS_HOST",
  "value": "localhost",
  "scope": "repository",
  "description": "Redis cache host for distributed_cache.py",
  "integration_point": "src/codex/rag/cache/distributed_cache.py:redis_host param",
  "fallback_behavior": "Uses value if set, else defaults to 'localhost' in code",
  "environments": {
    "development": "localhost",
    "staging": "redis-staging.internal.codex",
    "production": "redis.internal.codex"
  }
}
```

**All 8 Variables with Specifications:**

See "New Environment Variables Required" section above for full definitions.

### Deployment Timeline

**Phase 6 Session (This Session):**
- Create variable definition files in `.codex/pending_ops/`
- Document in `.codex/ENV_VARS_IMPLEMENTATION_SPEC.md`
- No actual variable creation (deferred to report_progress workflow)

**Phase 6 Merge:**
- Variables created by `process-variable-intents.yml` workflow
- `.codex/agent_context.json` refreshes with new variables
- Code replacements now have live environment variables available

**Phase 6 + Post-Merge:**
- Operators configure variables in GitHub UI for different environments
- Development: defaults (localhost)
- Staging/Production: actual hostnames/endpoints

---

## VI. RISK ASSESSMENT & MITIGATION

### Task 6.1 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Import path errors after move | Medium | High | Pre-move audit, test discovery verification, import rewrite script |
| Conftest.py hierarchy breaks fixture discovery | Low | High | Test conftest placement during move, run `pytest --fixtures` |
| ab_testing.py confusion (test vs. production) | Low | Medium | Pre-move audit to classify, move only verified test files |
| Coverage metrics regression | Low | Low | Compare coverage before/after, should be identical |

**Mitigation Strategy:** Run full pre-move audit, move only verified test files, validate with pytest discovery.

### Task 6.2 Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Backward compatibility break | Low | High | All changes use os.environ.get() with localhost defaults |
| Hardcoded localhost in unreachable code left behind | Medium | Low | Comprehensive grep audit, final validation sweep |
| Security issue: localhost allowlist too broad | Low | High | CODEX_LOCAL_LOOPBACK flag to disable dev-only features in production |
| Documentation examples become misleading | Medium | Low | Audit and update docstrings/examples in same task |
| Variable naming conflicts with other projects | Low | Medium | Use CODEX_ prefix consistently, check against GitHub docs |

**Mitigation Strategy:** Conservative defaults, backward compatibility guaranteed, security-first approach to localhost allowlists.

### Phase 7-9 Risks

| Phase | Risk | Mitigation |
|-------|------|-----------|
| 7 | Contributors ignore validation script | Auto-run in pre-commit hooks, clear error messages |
| 8 | Offline scenario untested in CI | Add nightly CI job that tests air-gapped installation |
| 9 | External users don't use metrics | Make telemetry opt-in, privacy-first, with clear consent |

---

## VII. SUCCESS CRITERIA & ACCEPTANCE

### Phase 6 Acceptance (This Session)

**All-or-Nothing Gate:** Must achieve ALL of the following:

✅ **Task 6.1:** 
- All 12 test files moved to `tests/` (verified with `pytest --collect-only`)
- All tests pass
- No import errors

✅ **Task 6.2:**
- 24 critical localhost hardcodes replaced
- 8 new environment variables documented
- `src/codex/utils/env_defaults.py` created with helper functions
- `.codex/LOCALHOST_REPLACEMENT_AUDIT.md` created
- All affected tests pass (with and without env vars)
- `.codex/ENV_VARS_IMPLEMENTATION_SPEC.md` ready for variable-sync workflow

✅ **Overall:**
- No breaking changes to public APIs
- No secrets committed
- Code Review: zero critical findings
- CodeQL: zero new security alerts
- Coverage: maintained or improved

---

## VIII. APPENDIX: FULL LOCALHOST HARDCODE INVENTORY

### Critical Replacements (24 files)

```
1. src/codex/rag/cache/distributed_cache.py (2 occurrences)
2. src/codex/rag/providers/ollama_provider.py (1)
3. src/codex/utils/dict_operations.py (4, mostly examples)
4. src/codex/auth/github_app.py (1, security check)
5. src/codex/archive/dal.py (1)
6. src/codex_ml/serving/inference_server.py (3)
7. src/codex_ml/training/multi_node_orchestration.py (2)
8. src/codex_ml/training/distributed.py (1)
9. src/cache/redis_cache.py (1)
10. src/safety/network_policy.py (1)
11. src/codex_ml/tracking/writers.py (1)
12. src/codex_ml/tracking/mlflow_guard.py (2)
13. src/codex_ml/tracking/guards.py (1)
14. scripts/deployment/health_check_runner.py (2)
15. scripts/launch_distributed.py (1)
16. src/mcp/config.py (1)
17. src/mcp/server/run.py (1)
18. src/mcp/server/http.py (2)
19. cognitive_app/src/server/cli_api_server.py (1)
20. services/msp_gateway/app.py (1)
21. services/msp_gateway/config.py (1)
22. services/ita/app/main.py (1)
23. src/codex_ml/telemetry/server.py (1)
24. monitoring/dashboard_api.py (1)
```

**Total critical files:** 24  
**Total critical occurrences:** ~40 (some files have multiple)  
**Total localhost occurrences in codebase:** 246  
**Ratio of hardcoded defaults to comments/examples:** ~40:206 (16% critical)

### Secondary Occurrences (Non-Critical, Leave As-Is)

- Examples in docstrings: ~80
- Comments explaining localhost behavior: ~60
- Test mocks and fixtures: ~66

These are safe to leave unchanged (documentation/examples).

---

## IX. NEXT STEPS

### Immediate Actions (This Session)

1. ✅ Finalize this campaign plan document
2. ⏳ Create Phase 6.1 agent brief for `autonomous-test-healer-agent`
3. ⏳ Create Phase 6.2 agent briefs for localhost replacement agents
4. ⏳ Initialize variable definition files in `.codex/pending_ops/`
5. ⏳ Kick off parallel Phase 6 execution

### Post-Session Actions

1. Merge Phase 6 changes to main
2. Schedule Phase 7 session (2 days post-merge)
3. Schedule Phase 8 session (3 days post-merge)
4. Schedule Phase 9 session (4 days post-merge)
5. Document final metrics in `.codex/AGENT_ACCOUNTABILITY_REPORT.md`

---

## X. DOCUMENT HISTORY

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | 2026-07-06T02:29Z | @copilot | Initial comprehensive campaign plan |

---

**Document Ready for Execution:** 2026-07-06T02:29:31Z  
**Authority:** @mbaetiong (D-tier autonomous, all plans and decisions approved)  
**Status:** 🟢 **READY FOR SEQUENTIAL EXECUTION**

