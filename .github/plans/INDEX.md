# Planset Index - 0D_base Branch Architectural Remediation

**Branch:** `0D_base_`  
**Created:** 2026-01-08  
**Status:** 📋 Active Planning Phase  
**Total Plansets:** 10  
**Priority Distribution:** 6 P0 (Critical), 3 P1 (High), 1 P2 (Medium)

---

## Overview

This index tracks all plansets for the comprehensive architectural remediation of the `0D_base_` branch. Each planset addresses specific "Split Brain" issues, security vulnerabilities, and technical debt identified in the audit.

---

## Planset Status

| ID | Name | Priority | Phase | Status | Dependencies |
|----|------|----------|-------|--------|--------------|
| PS-01 | Configuration Consolidation | P0 | Cycle 1-3 | 📋 Planned | None |
| PS-02 | IPC Bridge Hardening | P0 | Cycle 1-2 | 📋 Planned | None |
| PS-03 | Split Brain Elimination | P0 | Cycle 1-3 | 📋 Planned | PS-02 |
| PS-04 | Privacy-First Memory | P0 | Cycle 1-2 | 📋 Planned | PS-06 |
| PS-05 | Token Security Neutralization | P0 | Cycle 1 | 📋 Planned | None |
| PS-06 | Knowledge Crawler Service | P0 | Cycle 1-4 | 📋 Planned | PS-01 |
| PS-07 | Business Logic Elevation | P1 | Cycle 1-2 | 📋 Planned | PS-01 |
| PS-08 | Microservice Root Cleanup | P1 | Cycle 1-2 | 📋 Planned | None |
| PS-09 | Training Entry Point Unification | P1 | Cycle 1-2 | 📋 Planned | PS-01 |
| PS-10 | Owner Guard CI/CD Enforcement | P2 | Cycle 1 | 📋 Planned | PS-02 |

---

## Implementation Phases

### Phase 1: Foundation (Pre-commit Cycles 1-5)
**Plansets:** PS-01, PS-02, PS-05  
**Goal:** Establish secure foundations and eliminate critical vulnerabilities  
**Duration:** 5 pre-commit cycles

**Key Deliverables:**
- Hydra configuration consolidation complete
- Named pipes replacing TCP sockets
- Token security neutralized
- All tests passing

### Phase 2: Core Remediation (Pre-commit Cycles 6-12)
**Plansets:** PS-03, PS-04, PS-06, PS-07  
**Goal:** Eliminate Split Brain, implement privacy controls, operationalize knowledge sync  
**Duration:** 7 pre-commit cycles

**Key Deliverables:**
- Single source of truth for Zendesk logic
- PII scrubbing operational
- Knowledge crawler service deployed
- Business logic in validated code

### Phase 3: Integration & Cleanup (Pre-commit Cycles 13-17)
**Plansets:** PS-08, PS-09, PS-10  
**Goal:** Clean up repository structure, unify entry points, enforce CI/CD controls  
**Duration:** 5 pre-commit cycles

**Key Deliverables:**
- Repository root cleaned
- Training workflows unified
- Owner guard enforced
- Documentation complete

---

## Cognitive Brain Objectives

Each planset contributes to the following cognitive brain objectives:

### 1. Data Sovereignty
- **PS-06:** Knowledge Crawler Service establishes authoritative knowledge sync
- **PS-04:** Privacy-First Memory ensures PII compliance
- **Objective:** Single source of truth for all external knowledge

### 2. Schema Authority
- **PS-03:** Split Brain Elimination enforces single orchestrator
- **PS-07:** Business Logic Elevation validates all business rules
- **Objective:** Type-safe, validated schemas prevent hallucination

### 3. Configuration Consolidation
- **PS-01:** Hydra consolidation eliminates config sprawl
- **Objective:** Centralized, validated configuration management

### 4. Security Normalization
- **PS-02:** IPC Bridge Hardening secures inter-process communication
- **PS-05:** Token Security prevents credential leaks
- **PS-10:** Owner Guard prevents unauthorized deployments
- **Objective:** Defense-in-depth security model

### 5. Architectural Cleanliness
- **PS-08:** Microservice cleanup enforces monolith structure
- **PS-09:** Training unification establishes clear entry points
- **Objective:** Clean, maintainable codebase structure

---

## Success Metrics

### Code Quality
- **Lines Reduced:** Target -2,000 lines (duplicate elimination)
- **Test Coverage:** Maintain 85%+ across all changes
- **Linting:** Zero new violations
- **Type Safety:** 95%+ type hint coverage

### Security
- **Vulnerabilities Fixed:** 10 critical issues
- **Security Score:** 10/10 on all new code
- **Audit Compliance:** 100%

### Performance
- **Config Loading:** <100ms
- **IPC Latency:** <10ms
- **Knowledge Sync:** <1 hour drift
- **Build Time:** No degradation

### Maintainability
- **Documentation:** 100% of new utilities documented
- **Single Source of Truth:** Achieved across all domains
- **Technical Debt:** -40% reduction

---

## Risk Management

### High-Risk Changes
1. **IPC Bridge Replacement (PS-02):** Affects all workflow executions
   - **Mitigation:** Parallel run for 1 cycle, rollback plan ready
   
2. **Split Brain Elimination (PS-03):** Large refactor of critical path
   - **Mitigation:** Comprehensive test coverage, incremental migration

3. **Configuration Migration (PS-01):** Touches many files
   - **Mitigation:** Backward compatibility layer, gradual rollout

### Medium-Risk Changes
4. **Knowledge Crawler (PS-06):** New service with external dependencies
   - **Mitigation:** Extensive testing, graceful degradation

5. **Training Unification (PS-09):** Impacts ML workflows
   - **Mitigation:** Parallel validation, user acceptance testing

---

## Dependencies

### External
- Hydra (configuration management)
- Pydantic (schema validation)
- Linux OS (named pipes)
- GitHub Actions (CI/CD)

### Internal
- Cognitive brain patterns
- Utility registry
- Test infrastructure
- Documentation standards

---

## Progression Tracking

### Completed: 0/10
- None yet

### In Progress: 0/10
- None yet

### Blocked: 0/10
- None yet

### Ready for Implementation: 10/10
- All plansets documented and ready

---

## Next Actions

1. **Immediate:** Begin PS-01 (Configuration Consolidation)
2. **Parallel:** Start PS-02 (IPC Bridge Hardening)
3. **Queue:** Prepare PS-05 (Token Security)
4. **Review:** Validate all plansets with stakeholders

---

## Related Documentation

- `.codex/CODEBASE_AGENCY_POLICY.md` - Agent operational policies
- `.codex/AI_AGENT_UTILITIES_REGISTRY.md` - Reusable utilities
- `docs/architecture/TOP_5_QUICK_WINS_PLAN.md` - High-level strategy
- `.codex/cognitive_brain/` - Pattern learning and objectives

---

**Maintained By:** GitHub Copilot Agents  
**Review Frequency:** After each pre-commit cycle  
**Last Updated:** 2026-01-08  
**Next Review:** After PS-01 completion
