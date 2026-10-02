# Module Tier Progression Strategy
## Coverage Roadmap from Baseline (34.63%) to Phase 1 (40%) and Beyond

**Created:** 2026-07-02T02:22:00Z  
**Baseline:** 34.63% (Locked)  
**Phase 1 Target:** 40.0% (±0.5%)  

---

## Overview

The codebase is organized into 4 coverage tiers with distinct progression strategies:
- **Tier 1 (Security & Auth Core):** MAINTAIN ≥90% throughout all phases
- **Tier 2 (Auth Systems):** MAINTAIN ≥85% throughout all phases
- **Tier 3 (Infrastructure & CLI):** RAISE incrementally: 76% → 77% → 80% → 85% → 90%
- **Tier 4 (Extended Coverage):** AGGRESSIVE growth: 61% → 70% → 80% → 90% → 95%

---

## Tier 1: Security & Authentication Core
### Status: COMPREHENSIVE (92.6% avg coverage)
### Modules
- `security_core` - Core security infrastructure
- `token_rotation` - Token rotation mechanisms
- `scope_validator` - OAuth scope validation
- `decorators` - Authentication decorators
- `cve_monitor` - CVE monitoring system

### Progression Strategy: MAINTAIN
- **Baseline:** 92.6%
- **Phase 1-9 Requirement:** ≥90.0% (NO REGRESSION)
- **Tolerance:** No loss allowed
- **Justification:** Security-critical modules must never lose coverage
- **Escalation:** Any drop >1% triggers immediate review
- **Agent Responsibility:** unified-coverage-agent + @mbaetiong for approval

### Test Distribution by Phase
| Phase | Coverage | Tests Added | Description |
|-------|----------|-------------|-------------|
| Baseline | 92.6% | 0 | Current state |
| Phase 1-2 | ≥92.0% | Edge case tests | Mutation-resistant |
| Phase 3+ | ≥92.0% | Integration tests | End-to-end security flows |

---

## Tier 2: Authentication Systems
### Status: COMPREHENSIVE (86.1% avg coverage)
### Modules
- `user_store` - User storage & retrieval
- `mfa_provider` - Multi-factor authentication
- `token_manager` - Token lifecycle management
- `authenticator` - Core auth logic
- `middleware` - Auth middleware
- `oauth_manager` - OAuth provider integration
- `github_app` - GitHub App authentication
- `repositories` - Repository access control

### Progression Strategy: MAINTAIN
- **Baseline:** 86.1%
- **Phase 1-9 Requirement:** ≥85.0% (NO REGRESSION)
- **Tolerance:** Max 1% loss (maintain ≥84%)
- **Justification:** Authentication is critical infrastructure
- **Escalation:** Drop >1% blocks PR merge
- **Agent Responsibility:** unified-coverage-agent with human review

### Test Distribution by Phase
| Phase | Coverage | Tests Added | Description |
|-------|----------|-------------|-------------|
| Baseline | 86.1% | 0 | Current state |
| Phase 1-2 | ≥86.0% | OAuth edge cases | Token expiry, refresh |
| Phase 3+ | ≥85.0% | MFA tests | TOTP, backup codes |

---

## Tier 3: Infrastructure & CLI
### Status: EXTENDED (76.0% avg coverage)
### Modules
- `cli_core` - CLI core functionality
- `codex_ml_cli` - Machine learning CLI
- `cli_rag` - RAG system CLI
- `tokenization_cli` - Tokenization CLI
- `archive_cli` - Archive management CLI
- `quantum_orchestrator_cli` - Quantum orchestrator CLI

### Progression Strategy: INCREMENTAL RAISE
- **Baseline:** 76.0%
- **Phase 1 Target:** 77.0% (+1.0%)
- **Phase 2 Target:** 80.0% (+3.0% cumulative)
- **Phase 3 Target:** 85.0% (+5.0% cumulative)
- **Phase 4+ Target:** 90.0% (+10.0% cumulative)

### Progression Breakdown
| Phase | Target | Delta | Tests Added | Strategy |
|-------|--------|-------|-------------|----------|
| Baseline | 76.0% | 0% | 0 | Current state |
| Phase 1 | 77.0% | +1.0% | ~100 | CLI argument parsing |
| Phase 2 | 80.0% | +3.0% | ~300 | Command execution flows |
| Phase 3 | 85.0% | +5.0% | ~350 | Error handling paths |
| Phase 4+ | 90.0% | +10.0% | ~200 | Integration scenarios |

### Test Strategy
- **Phase 1:** Focus on CLI help, argument validation, default values
- **Phase 2:** Command execution with various configurations
- **Phase 3:** Error paths, invalid arguments, edge cases
- **Phase 4:** Multi-command workflows, integration with other tiers

### Agent Responsibility: unified-coverage-agent (gap-fill)

---

## Tier 4: Extended Coverage & Capabilities
### Status: EXTENDED (61.0% avg coverage)
### Modules
- `rag_embeddings` - Retrieval-augmented generation
- `safety_moderation` - Content moderation
- `training_systems` - Training infrastructure
- `data_handling` - Data pipeline
- `agents_orchestration` - Agent coordination
- `capabilities` - Feature capabilities
- `bridge_integration` - System bridges
- `other_modules` - Supporting modules

### Progression Strategy: AGGRESSIVE GROWTH
- **Baseline:** 61.0%
- **Phase 1 Target:** 70.0% (+9.0%)
- **Phase 2 Target:** 80.0% (+10.0% cumulative)
- **Phase 3 Target:** 85.0% (+5.0% cumulative)
- **Phase 4+ Target:** 95.0% (+10.0% cumulative)

### Progression Breakdown
| Phase | Target | Delta | Tests Added | Strategy |
|-------|--------|-------|-------------|----------|
| Baseline | 61.0% | 0% | 0 | Current state |
| Phase 1 | 70.0% | +9.0% | ~1,000 | Happy path + edge cases |
| Phase 2 | 80.0% | +10.0% | ~1,200 | Error paths + integration |
| Phase 3 | 85.0% | +5.0% | ~800 | Property-based testing |
| Phase 4+ | 95.0% | +10.0% | ~500 | Mutation-resistant tests |

### Test Strategy (Per Sub-Module)
**RAG Embeddings (current 35%):**
- Phase 1: Add 250 tests for embedding generation, similarity scoring
- Phase 2: Add 300 tests for chunk handling, index operations
- Phase 3: Property-based tests for invariants
- Goal: 85% by Phase 3

**Safety Moderation (current 45%):**
- Phase 1: Add 200 tests for rule matching, score thresholds
- Phase 2: Add 250 tests for bypass detection, false positives
- Phase 3: Add 100 tests for edge cases
- Goal: 90% by Phase 3

**Training Systems (current 52%):**
- Phase 1: Add 300 tests for trainer init, forward pass, backprop
- Phase 2: Add 350 tests for epoch handling, checkpoint save/load
- Phase 3: Add 150 tests for distributed training
- Goal: 85% by Phase 3

**Data Handling (current 48%):**
- Phase 1: Add 250 tests for load, transform, validate
- Phase 2: Add 300 tests for split strategies, edge cases
- Phase 3: Add 150 tests for streaming pipelines
- Goal: 80% by Phase 3

**Agents Orchestration (current 40%):**
- Phase 1: Add 400 tests for agent initialization, delegation
- Phase 2: Add 350 tests for message routing, async handling
- Phase 3: Add 200 tests for failure recovery
- Goal: 85% by Phase 3

### Agent Responsibility
- **Gap-Fill:** unified-coverage-agent (aggressive targeting)
- **Edge Cases:** autonomous-test-healer-agent (flaky test fixes)
- **Error Paths:** ci-testing-agent (error handling validation)

---

## Combined Progression Summary

### All Tiers Target by Phase
| Phase | Tier 1 | Tier 2 | Tier 3 | Tier 4 | Overall | Tests |
|-------|--------|--------|--------|--------|---------|-------|
| Baseline | 92.6% | 86.1% | 76.0% | 61.0% | 34.63% | 2,467 |
| Phase 1 | ≥92.0% | ≥85.0% | 77.0% | 70.0% | 40.0% | 2,800 |
| Phase 2 | ≥92.0% | ≥85.0% | 80.0% | 80.0% | 50.0% | 3,500 |
| Phase 3 | ≥92.0% | ≥85.0% | 85.0% | 85.0% | 60.0% | 4,200 |
| Phase 4 | ≥90.0% | ≥85.0% | 90.0% | 90.0% | 70.0% | 5,000 |
| Phase 5 | ≥90.0% | ≥85.0% | 90.0% | 95.0% | 75.0% | 5,500 |
| Phase 6+ | ≥90.0% | ≥85.0% | 90.0% | 95.0% | ≥80% | 6,000+ |

---

## Per-Tier Agent Assignments

### Tier 1 & 2 (Security & Auth)
- **Agent:** unified-coverage-agent (monitor)
- **Escalation:** @mbaetiong (any >1% drop)
- **Approach:** Defensive maintenance, no aggressive growth
- **Review Cadence:** Weekly regression check

### Tier 3 (Infrastructure)
- **Agent:** unified-coverage-agent (incremental gap-fill)
- **Approach:** Steady +1-3% per phase
- **Focus Areas:** CLI argument handling, error cases
- **Test Patterns:** Parametrized tests for input validation

### Tier 4 (Extended)
- **Agent:** unified-coverage-agent (aggressive gap-fill)
- **Secondaries:** autonomous-test-healer-agent, ci-testing-agent
- **Approach:** Targeted module growth, 9-10% per phase
- **Focus Areas:** Happy paths → error paths → edge cases → properties
- **Test Patterns:** Bulk test generation by category

---

## Phase Gate Requirements

### Phase 1 Gate (40% target)
- [ ] Tier 1 maintains ≥92.0%
- [ ] Tier 2 maintains ≥85.0%
- [ ] Tier 3 reaches 77.0%
- [ ] Tier 4 reaches 70.0%
- [ ] Overall reaches 40.0% ±0.5%
- [ ] Test count ≥2,800
- [ ] All quality metrics pass
- [ ] Module regression: None >5%
- [ ] Unified-coverage-agent approved phase completion

### Phase 2 Gate (50% target)
- [ ] Tier 1 maintains ≥92.0%
- [ ] Tier 2 maintains ≥85.0%
- [ ] Tier 3 reaches 80.0%
- [ ] Tier 4 reaches 80.0%
- [ ] Overall reaches 50.0% ±0.5%
- [ ] Test count ≥3,500
- [ ] Zero cross-module dependencies broken
- [ ] Human approval required

---

## Escalation Rules

### Coverage Loss Triggers
| Tier | Loss | Action | Agent |
|------|------|--------|-------|
| Tier 1 | >0.5% | Block PR | @mbaetiong |
| Tier 2 | >1.0% | Block PR | unified-coverage-agent |
| Tier 3 | >2.0% | Block PR | unified-coverage-agent |
| Tier 4 | >3.0% | Warn + recommend | unified-coverage-agent |

### Coverage Gain Opportunities
- **Tier 1/2:** Any >1% gain → celebrate, no action needed
- **Tier 3:** >2% gain ahead of schedule → accelerate to next phase
- **Tier 4:** >5% gain → offer to fund additional test generation

---

## References

- **Baseline Snapshot:** `.codex/COVERAGE_BASELINE_34_63.json`
- **Validation Criteria:** `.codex/COVERAGE_VALIDATION_CRITERIA.md`
- **Phase Gates:** `.codex/PHASE_VALIDATION_GATES.yaml` (Phase 1+)
- **Zero-Coverage Remediation:** `.codex/ZERO_COVERAGE_REMEDIATION.md`
