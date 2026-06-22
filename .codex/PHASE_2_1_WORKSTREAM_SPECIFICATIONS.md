# Phase 2.1 Implementation Specification
> **Workstream:** Token Broker & Secret Infrastructure  
> **Status:** 🟡 EXECUTING  
> **Agents Delegated:** 3 parallel agents (see below)  
> **Expected Completion:** 24-48 hours

---

## Parallel Execution Workstreams

### Workstream A: Token Broker Enhancement (Agent ID: phase-2-1-token-broker-enhance)
**Status:** 🟡 IN PROGRESS

**Deliverables:**
1. Enhanced `src/codex/autonomy/token_broker.py`
   - ✅ TokenHealthStatus enum
   - ✅ TokenHealthChecker class
   - ✅ TokenCircuitBreaker class (exponential backoff)
   - ✅ TokenRotationScheduler class
   - ✅ Structured logging integration

2. Test Suite: `tests/unit/test_token_broker_enhancements.py`
   - Minimum 15 test cases covering all new components
   - Circuit breaker state transitions
   - Health check failure scenarios
   - Token rotation scheduling

3. Documentation: `.codex/PHASE_2_1_TOKEN_BROKER_DESIGN.md`
   - Technical design patterns
   - API reference for all new classes
   - Observability/metrics guide
   - Example usage

**Key Requirements:**
- Zero API breaking changes to TokenBroker.resolve()
- All new functions must be type-hinted
- Health checks detect: expired tokens, revoked tokens, scope mismatch
- Circuit breaker prevents cascade failures
- Rotation warnings at 80-day mark

---

### Workstream B: Secret Injection Workflow (Agent ID: phase-2-1-secret-injection-wor)
**Status:** 🟡 IN PROGRESS

**Deliverables:**
1. Design Document: `.codex/PHASE_2_1_SECRET_INJECTION_DESIGN.md`
   - Step-by-step procedures for @mbaetiong
   - GitHub environment setup (CODEX_MASTER_KEY, CODEX_BACKUP_KEY)
   - OAuth app scope requirements
   - Validation checks & emergency revocation

2. Validation Script: `scripts/ci/validate_token_setup.py`
   - Tests both primary and backup tokens
   - Validates JWT structure, scopes, expiration
   - Performs API operation tests (create PR, update variables, manage workflows)
   - Returns JSON result with detailed diagnostics

3. CI Workflow: `.github/workflows/validate-token-health.yml`
   - Runs token validation on schedule (daily)
   - Posts results to GitHub
   - Alerts @mbaetiong on token health degradation

**Key Requirements:**
- Instructions must be actionable by non-technical users
- Token rotation never breaks CI/CD pipelines
- All token events tracked in audit logs
- Clear rollback procedure documented

---

### Workstream C: Compliance Framework (Agent ID: phase-2-3-compliance-framework)
**Status:** 🟡 IN PROGRESS

**Deliverables:**
1. Compliance Validators (6 validators, one per requirement):
   - `req1_eligibility_validator.py` - PR eligibility checks
   - `req2_compliance_validator.py` - Docs/tests/security compliance
   - `req3_merge_validator.py` - Authorization rules
   - `req4_accountability_validator.py` - AGENT_ACCOUNTABILITY_REPORT.md
   - `req5_changelog_validator.py` - CHANGELOG.md
   - `req6_postmerge_validator.py` - Post-merge health checks

2. Master Orchestrator: `scripts/ci/unified_compliance_check.py`
   - Orchestrates all 6 validators
   - Produces compliance score (0-100)
   - JSON output for CI integration

3. CI Workflow: `.github/workflows/unified-governance-check.yml`
   - Runs pre-merge compliance check
   - Blocks merge if any requirement fails
   - Supports force-override audit trail

4. Compliance Dashboard: `scripts/ci/compliance_dashboard.py`
   - Tracks compliance trends
   - Identifies violation hotspots
   - Generates daily/monthly reports

**Key Requirements:**
- All validators complete in <60 seconds
- <1% false positive rate
- Explainable decisions (show reasoning)
- Support strict mode (block) and warning mode

---

## Integration Points

### Token Broker → Secret Injection
- Token broker health checks will consume CODEX_MASTER_KEY
- Secret injection validates using token broker circuits
- Rotation scheduler integrates with backup key failover

### Secret Injection → Compliance Framework
- Token health affects compliance score (req-6 post-merge)
- Governance gate verifies CODEX_MASTER_KEY presence
- Failed token validation blocks PR merge

### All → Session Accountability
- All components log to .codex/compliance/ audit trail
- AGENT_ACCOUNTABILITY_REPORT.md tracks all phase 2.1 changes
- Session wrapup verifies compliance at PR merge

---

## Success Metrics for Phase 2.1

| Metric | Target | Status |
|--------|--------|--------|
| Token broker enhancements deployed | ✅ Deployed | 🟡 In Progress |
| Health checks detect all failure modes | ✅ 100% coverage | 🟡 In Progress |
| Circuit breaker prevents cascades | ✅ Yes | 🟡 In Progress |
| Secret injection workflow documented | ✅ Complete | 🟡 In Progress |
| Validation script passes all tests | ✅ 100% pass | 🟡 In Progress |
| Compliance validators enforcing REQ-1-6 | ✅ All 6 working | 🟡 In Progress |
| Pre-merge blocker integrated | ✅ Yes | 🟡 In Progress |
| Zero emergency rollbacks (48h) | ✅ Zero | 🟡 In Progress |

---

## Commit & Audit Trail

- **Master Tracker:** .codex/IMPLEMENTATION_PHASE2_PHASE3_MASTER.md
- **Phase 2.1 Progress:** This document
- **Token Broker Progress:** .codex/PHASE_2_1_TOKEN_BROKER_PROGRESS.md (auto-updated)
- **Secret Injection Progress:** .codex/PHASE_2_1_SECRET_INJECTION_PROGRESS.md (auto-updated)
- **Compliance Progress:** .codex/PHASE_2_3_COMPLIANCE_PROGRESS.md (auto-updated)
- **Agent Registry:** .github/agents/AGENT_REGISTRY.yaml (unchanged)
- **Auth Status:** .codex/agent_context.json (tracked)

---

**Last Updated:** 2026-06-21T23:32:53Z  
**Next Review:** When first agent completes (ETA: 2026-06-22T01:00:00Z)
