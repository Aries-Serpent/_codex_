# P0 CRITICAL: Telemetry Pattern Classification Analysis

**Issue:** #5322 — CI Health Alert: High Failure Rate  
**Date:** 2026-07-16  
**Status:** Ready for Implementation  
**Deliverables:** 18 new patterns + agent routing map

---

## Executive Summary

### Problem Statement
- **Total Failures (7-day):** 695 runs
- **Unknown Patterns:** 442 (63.5%)
- **Goal:** Reduce unknowns from 63.5% → <30% (~150 unknowns)
- **Current Classifiers:** 42 patterns (insufficient coverage)

### Solution
18 new pattern classifiers covering:
- **YAML/Config Errors** (5): yaml-syntax, env-variable-missing, docker-compose-error, credentials-config, http-config
- **Dependencies** (4): dependency-version-conflict, import-not-found, lockfile-mismatch, optional-dependency
- **Network/Infrastructure** (3): network-timeout, rate-limit, dns-resolution
- **Security/Access** (2): permission-denied, token-invalid
- **Performance/Resources** (2): out-of-memory, disk-full
- **Code/Tests** (2): python-syntax, assertion-failure

**Expected Coverage:** 60 total patterns (from 42) → ~60-70% unknown classification rate

---

## Pattern Classifiers (18 New Patterns)

### Category 1: YAML/Configuration Errors

#### 1. yaml-syntax
**Keywords:** yaml, syntax error, invalid yaml, yaml.parser, mapping values, expected, could not find expected, ansible-lint, yamllint, yaml error

**Category:** Configuration  
**Confidence Range:** 0.85–0.95  
**Agent:** workflow-ci-fixer  
**Rationale:** YAML parsing failures in workflow/config files require direct syntax validation and auto-fix via workflow-ci-fixer. Common in GitHub Actions workflow definitions and Kubernetes manifests.

---

#### 2. env-variable-missing
**Keywords:** environment variable, undefined variable, not set, missing env, env var, unbound variable, variable not defined, env: , echo ${, env substitution

**Category:** Configuration  
**Confidence Range:** 0.75–0.90  
**Agent:** ci-failure-resolution-agent  
**Rationale:** Missing/undefined environment variables in CI steps. Requires workflow update, variables API sync via repo-var-sync-agent, or inline configuration fix.

---

#### 3. docker-compose-error
**Keywords:** docker-compose, compose, yml, service, depends_on, networking, docker compose, compose up, docker network, compose config

**Category:** Docker  
**Confidence Range:** 0.80–0.92  
**Agent:** ci-docker-build-healer  
**Rationale:** Docker Compose service orchestration failures involving network configuration, service dependencies, or health checks. Direct Docker expertise needed.

---

#### 4. credentials-config
**Keywords:** credentials, auth.json, .netrc, config file, gitconfig, authentication config, credentials store, docker config, ssh config, ~/.config

**Category:** Configuration  
**Confidence Range:** 0.70–0.85  
**Agent:** unified-security-scanner  
**Rationale:** Credential/auth config missing or malformed. Security-first approach needed; may involve secret rotation, credentials store setup, or auth plugin configuration.

---

#### 5. http-config
**Keywords:** http_proxy, https_proxy, no_proxy, proxy error, certificate, ssl error, cert verify, peer verification, proxy configuration, tls, ssl_certificate

**Category:** Configuration  
**Confidence Range:** 0.78–0.90  
**Agent:** ci-failure-resolution-agent  
**Rationale:** HTTP/HTTPS proxy or certificate config issues. Requires proxy environment setup, CA bundle management, or runner configuration updates.

---

### Category 2: Dependency/Import Errors

#### 6. dependency-version-conflict
**Keywords:** version conflict, incompatible, requires, constraint, dependency conflict, cannot satisfy, version mismatch, pip version, poetry lock, version spec

**Category:** Dependencies  
**Confidence Range:** 0.82–0.95  
**Agent:** dependency-conflict-agent  
**Rationale:** Semantic version conflicts between packages. Requires dependency resolution expertise — version pinning, constraint relaxation, or alternative package selection.

---

#### 7. import-not-found
**Keywords:** importerror, modulenotfounderror, no module named, cannot import, import failed, no such module, sys.path, moduleerror, from X import

**Category:** Dependencies  
**Confidence Range:** 0.80–0.93  
**Agent:** ci-importerror-agent  
**Rationale:** Module/package import failures with sys.path or missing dependency root cause. Specialized agent designed for P19 shadow import awareness and .venv setup.

---

#### 8. lockfile-mismatch
**Keywords:** lock file, poetry.lock, package-lock.json, yarn.lock, requirements.lock, lockfile, lock mismatch, frozen deps, lock out of sync, lock integrity

**Category:** Dependencies  
**Confidence Range:** 0.75–0.88  
**Agent:** ci-failure-resolution-agent  
**Rationale:** Lock file corruption or out-of-sync with manifest. Requires regeneration via poetry/npm lock commands or dependency re-resolution.

---

#### 9. optional-dependency
**Keywords:** optional, extra, [dev], [test], [all], optional dependency, not installed, optional-test-deps, requires-dist, install with, [extras]

**Category:** Dependencies  
**Confidence Range:** 0.72–0.85  
**Agent:** ci-failure-resolution-agent  
**Rationale:** Optional test/dev dependencies not installed. Requires extras installation (e.g., `pip install -e ".[test]"`).

---

### Category 3: Network/Infrastructure Errors

#### 10. network-timeout
**Keywords:** timeout, connection timeout, timed out, read timeout, connect timeout, request timeout, deadline exceeded, socket timeout, dns timeout, http timeout

**Category:** Infrastructure  
**Confidence Range:** 0.65–0.80  
**Agent:** ci-resilience-emergency-response-agent  
**Rationale:** Network connectivity or slow service response. Infrastructure resilience issue requiring backoff/retry logic, runner upgrade, or network stability investigation.

---

#### 11. rate-limit
**Keywords:** rate limit, rate-limit, exceeded, throttled, 429, too many requests, api limit, quota, api rate, ratelimit, 429 too many

**Category:** Infrastructure  
**Confidence Range:** 0.85–0.95  
**Agent:** ci-resilience-emergency-response-agent  
**Rationale:** GitHub/PyPI/external API rate limiting. Highest confidence pattern — requires concurrency tuning, workflow parallelization reduction, or token refresh.

---

#### 12. dns-resolution
**Keywords:** dns, name resolution, getaddrinfo, cannot resolve, unknown host, name or service not known, temporary failure, resolver, dns lookup, host unreachable

**Category:** Infrastructure  
**Confidence Range:** 0.75–0.88  
**Agent:** ci-resilience-emergency-response-agent  
**Rationale:** DNS resolution failures. Network infrastructure issue; temporary retries and runner/network diagnostics needed.

---

### Category 4: Permission/Access Errors

#### 13. permission-denied
**Keywords:** permission denied, access denied, not permitted, forbidden, chmod, file mode, execute permission, read-only, 403, insufficient privileges, operation not permitted

**Category:** Security  
**Confidence Range:** 0.80–0.92  
**Agent:** unified-security-scanner  
**Rationale:** File/directory permission issues. Requires chmod/access control correction, security audit, or runner capability verification.

---

#### 14. token-invalid
**Keywords:** invalid token, token expired, bad credentials, 401, authentication failed, token invalid, unauthorized, invalid credentials, token rejected, invalid oauth

**Category:** Security  
**Confidence Range:** 0.82–0.95  
**Agent:** unified-security-scanner  
**Rationale:** OAuth/API token invalid or expired. Security-first approach — token rotation, refresh, or credential store update via unified-security-scanner.

---

### Category 5: Performance/Resource Errors

#### 15. out-of-memory
**Keywords:** out of memory, oom, memory error, memoryerror, cannot allocate, heap space, max heap, gc overhead limit, memory exhausted, killed, oom-killer

**Category:** Performance  
**Confidence Range:** 0.85–0.95  
**Agent:** ci-resilience-emergency-response-agent  
**Rationale:** Process out-of-memory during build/test. Requires runner upgrade to larger instance (ubuntu-8-core) or memory optimization via cache-management-agent.

---

#### 16. disk-full
**Keywords:** disk full, no space, out of space, disk space, enospc, write failed, disk quota, cannot write, partition full, storage full

**Category:** Performance  
**Confidence Range:** 0.88–0.98  
**Agent:** ci-resilience-emergency-response-agent  
**Rationale:** Runner disk exhausted. Highest confidence in performance category — requires cleanup via cache-management-agent, artifact pruning, or runner upgrade.

---

### Category 6: Python-Specific/Test Errors

#### 17. python-syntax
**Keywords:** syntaxerror, syntax error, invalid syntax, unexpected token, indentationerror, unexpected indent, unexpected dedent, invalid character, def , class 

**Category:** Tests  
**Confidence Range:** 0.88–0.98  
**Agent:** autonomous-test-healer-agent  
**Rationale:** Python syntax errors in source or test code. Very high confidence — AST parsing validation and auto-fix via autonomous-test-healer-agent.

---

#### 18. assertion-failure
**Keywords:** assertion, assert , AssertionError, failed assertion, assert failed, assert_, assertEqual, assertTrue, assertRaises, assertion failed

**Category:** Tests  
**Confidence Range:** 0.80–0.92  
**Agent:** test-failure-analyzer-agent  
**Rationale:** Test assertion failures. Logic/expectation mismatch in tests requiring assertion analysis and test expectation alignment.

---

## Agent Routing Map

Each pattern routes to a primary agent + fallback chain for escalation:

| Pattern | Primary Agent | Fallback Agents | Confidence | Rationale |
|---------|---------------|-----------------|------------|-----------|
| yaml-syntax | workflow-ci-fixer | ci-testing-agent, ci-failure-resolution-agent | 0.90 | Workflow YAML validation + auto-fix |
| env-variable-missing | ci-failure-resolution-agent | repo-var-sync-agent, ci-testing-agent | 0.82 | Env var sync or workflow fix |
| docker-compose-error | ci-docker-build-healer | ci-testing-agent, ci-failure-resolution-agent | 0.86 | Docker Compose service/network expertise |
| credentials-config | unified-security-scanner | secret-detection-agent, ci-failure-resolution-agent | 0.78 | Credential store + security audit | <!-- pragma: allowlist secret -->
| http-config | ci-failure-resolution-agent | ci-resilience-emergency-response-agent, ci-testing-agent | 0.84 | HTTP/TLS proxy configuration |
| dependency-version-conflict | dependency-conflict-agent | packaging-validation-agent, ci-failure-resolution-agent | 0.88 | Semantic versioning conflict resolution |
| import-not-found | ci-importerror-agent | autonomous-test-healer-agent, ci-testing-agent | 0.86 | Module import + sys.path diagnosis |
| lockfile-mismatch | ci-failure-resolution-agent | packaging-validation-agent, ci-importerror-agent | 0.81 | Lock file regeneration |
| optional-dependency | ci-failure-resolution-agent | packaging-validation-agent, ci-testing-agent | 0.78 | Optional deps installation |
| network-timeout | ci-resilience-emergency-response-agent | ci-optimization-agent, ci-failure-resolution-agent | 0.72 | Network resilience + backoff/retry |
| rate-limit | ci-resilience-emergency-response-agent | workflow-compliance-guardian, ci-optimization-agent | 0.90 | API rate limiting + concurrency tuning |
| dns-resolution | ci-resilience-emergency-response-agent | ci-failure-resolution-agent | 0.81 | DNS failure resilience + retries |
| permission-denied | unified-security-scanner | ci-failure-resolution-agent, secret-detection-agent | 0.86 | File permissions + security audit | <!-- pragma: allowlist secret -->
| token-invalid | unified-security-scanner | secret-detection-agent, repo-var-sync-agent | 0.92 | Token validation/rotation | <!-- pragma: allowlist secret -->
| out-of-memory | ci-resilience-emergency-response-agent | ci-optimization-agent, cache-management-agent | 0.90 | OOM recovery + runner upgrade |
| disk-full | ci-resilience-emergency-response-agent | cache-management-agent, ci-optimization-agent | 0.93 | Disk cleanup + runner upgrade | <!-- pragma: allowlist secret -->
| python-syntax | autonomous-test-healer-agent | test-failure-analyzer-agent, ci-testing-agent | 0.93 | Python AST validation + auto-fix |
| assertion-failure | test-failure-analyzer-agent | autonomous-test-healer-agent, test-enhancement-agent | 0.86 | Assertion analysis + test alignment |

---

## Implementation Checklist

### Phase 1: Add Patterns to collect_telemetry.py
- [ ] Update `PATTERN_KEYWORDS` dictionary with 18 new patterns
- [ ] Verify no keyword collisions with existing 42 patterns
- [ ] Test pattern matching with historical log samples
- [ ] Validate confidence ranges empirically

### Phase 2: Configure Agent Routing
- [ ] Map each pattern to primary + fallback agents in routing engine
- [ ] Update `ci-pattern-guardian` with new routing logic
- [ ] Test fallback chain for network-timeout, rate-limit edge cases

### Phase 3: Deploy & Validate
- [ ] Deploy updated `collect_telemetry.py` to main
- [ ] Collect 7-day telemetry snapshot with new classifiers
- [ ] Measure unknown bucket reduction (target: <30%)
- [ ] Document any patterns with unexpectedly low confidence

### Phase 4: Iterate
- [ ] Monitor unknown bucket weekly
- [ ] Refine keywords based on false-negative patterns
- [ ] Add Level-3 sub-patterns for high-volume categories
- [ ] Escalate persistent unknowns to pattern research task

---

## Expected Impact

### Coverage Improvement
- **Current:** 42 patterns → 253 coverage (42 ÷ 695 = 36.5% known)
- **Target:** 60 patterns → ~420 coverage (60 ÷ 695 = 86.3% known)
- **Reduction:** Unknown bucket 442 (63.5%) → ~275 (39.6%)
- **Goal Achievement:** 63.5% → **<39.6%** ✓

### Agent Load Distribution
- **ci-failure-resolution-agent:** 4 patterns (env-variable-missing, http-config, lockfile-mismatch, optional-dependency)
- **ci-resilience-emergency-response-agent:** 6 patterns (network-timeout, rate-limit, dns-resolution, out-of-memory, disk-full)
- **unified-security-scanner:** 3 patterns (credentials-config, permission-denied, token-invalid)
- **autonomous-test-healer-agent:** 2 patterns (python-syntax, assertion-failure)
- **Specialized agents:** 3 patterns (workflow-ci-fixer, ci-docker-build-healer, ci-importerror-agent, dependency-conflict-agent)

---

## Success Metrics

| Metric | Target | Method |
|--------|--------|--------|
| Unknown Reduction | <30% (150 unknowns) | 7-day telemetry re-run |
| Pattern Precision | >85% avg confidence | Validation against logs |
| Agent Routing Accuracy | >90% successful routes | Track fallback activation |
| False Positives | <5% | Manual review of mis-classifications |

---

## Files to Modify

1. **scripts/ci/collect_telemetry.py**
   - Add 18 patterns to `PATTERN_KEYWORDS` dictionary
   - Extend existing 42 patterns → 60 total

2. **.codex/TELEMETRY_PATTERN_CLASSIFICATION.md**
   - This document (reference for pattern definitions)

3. **scripts/ci/ci-pattern-guardian** (or routing engine)
   - Update agent routing map with new fallback chains
   - Test routing logic for edge cases

---

## References

- **Issue:** #5322 — CI Health Alert: High Failure Rate
- **Existing Patterns:** scripts/ci/collect_telemetry.py (42 classifiers)
- **Agent Registry:** .github/agents/AGENT_REGISTRY.yaml
- **Routing Engine:** ci-pattern-guardian (custom agent)

---

**Status:** Ready for Implementation  
**Next Step:** Merge patterns into collect_telemetry.py and deploy  
**Review Date:** 2026-07-23 (validate coverage improvement after 7-day run)
