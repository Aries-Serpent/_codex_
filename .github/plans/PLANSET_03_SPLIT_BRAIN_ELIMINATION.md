# Planset 03: Split Brain Elimination (Zendesk Orchestration)

**Planset ID:** PS-03  
**Priority:** P0 - Critical  
**Phase:** Pre-commit Cycle 1-3  
**Status:** 📋 Planned  
**Dependencies:** PS-02 (Secure Bridge)  
**Cognitive Brain Objective:** Establish single source of truth for Zendesk operations

---

## Context

**Problem:** Duplicate orchestration logic in two locations:
- `agents/zendesk_quantum_orchestrator.py` (legacy, 500+ lines)
- `src/codex/zendesk/quantum/orchestrator.py` (modern, incomplete)

**Impact:** Inconsistent behavior, maintenance burden, unclear authority

**Solution:** Port unique business rules to modern orchestrator, delete legacy file

---

## Implementation Plan

### Pre-commit Cycle 1: Business Rule Analysis

**Goal:** Identify all unique logic in legacy orchestrator

**Tasks:**
- [ ] Analyze `agents/zendesk_quantum_orchestrator.py` line-by-line
- [ ] Document Priority Mapping rules
- [ ] Document Organization Routing logic
- [ ] Identify dependencies on Zenpy SDK
- [ ] Create migration checklist
- [ ] Map to modern orchestrator methods

**Deliverables:**
- Migration analysis document
- Business rule inventory
- Test case specifications

**Success Criteria:**
- [ ] All unique rules documented
- [ ] Zero business logic overlooked
- [ ] Migration path clear

### Pre-commit Cycle 2: Logic Porting

**Goal:** Implement business rules in modern orchestrator

**Tasks:**
- [ ] Port Priority Mapping to `src/codex/zendesk/quantum/orchestrator.py`
- [ ] Port Organization Routing logic
- [ ] Implement using Zenpy SDK patterns
- [ ] Add Pydantic validation for all inputs
- [ ] Create comprehensive unit tests (90%+ coverage)
- [ ] Integration tests with Zendesk sandbox

**Files to Modify:**
- `src/codex/zendesk/quantum/orchestrator.py` (+300 lines)
- Create `src/codex/zendesk/model/routing.py` (Pydantic models)

**Files to Create:**
- `tests/test_zendesk_orchestrator.py` (400+ lines)
- `tests/integration/test_zendesk_routing.py` (200+ lines)

**Success Criteria:**
- [ ] All business rules ported
- [ ] Tests passing (100%)
- [ ] Type safety enforced
- [ ] Schema validation working

### Pre-commit Cycle 3: Legacy Deprecation

**Goal:** Remove legacy orchestrator, validate system

**Tasks:**
- [ ] Update all imports to use modern orchestrator
- [ ] Run full test suite
- [ ] Delete `agents/zendesk_quantum_orchestrator.py`
- [ ] Update documentation
- [ ] Create migration guide for future reference
- [ ] Monitor for any missed edge cases

**Files to Delete:**
- `agents/zendesk_quantum_orchestrator.py`

**Files to Update:**
- All files importing legacy orchestrator (~10 files)
- Documentation referencing old approach

**Success Criteria:**
- [ ] Legacy file deleted
- [ ] All tests passing
- [ ] Zero import errors
- [ ] Documentation updated
- [ ] Single source of truth established

---

## Business Rules to Port

### Priority Mapping
```python
# Legacy rule (hardcoded dict)
priority_map = {"urgent": 1, "high": 2, "normal": 3, "low": 4}

# Modern approach (Pydantic enum)
class TicketPriority(str, Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    
    def to_zendesk_priority(self) -> int:
        return {
            self.URGENT: 1,
            self.HIGH: 2,
            self.NORMAL: 3,
            self.LOW: 4
        }[self]
```

### Organization Routing
```python
# Port organization-based routing logic
# Validate with Pydantic, use Zenpy SDK for API calls
```

---

## Success Metrics

- **Code Reduction:** -500 lines (legacy file deleted)
- **Single Source of Truth:** 1 orchestrator (was 2)
- **Test Coverage:** 90%+ on all business logic
- **Type Safety:** 100% (Pydantic validation)

---

## Cognitive Brain Integration

**Patterns Learned:**
1. Legacy code analysis and migration strategies
2. Pydantic schema design for business rules
3. Zenpy SDK integration patterns
4. Comprehensive testing for critical path code

**Reusable Utilities:**
1. Business rule migration checklist
2. Pydantic model templates for SaaS integrations
3. Integration test patterns for external APIs

---

**Created:** 2026-01-08  
**Agent:** GitHub Copilot (PR #2750)
