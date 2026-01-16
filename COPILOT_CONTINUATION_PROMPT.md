# Copilot Continuation Prompt - QA Walkthrough & Test Coverage

@copilot Continue implementing the IP-001 through IP-005 improvement proposals for the _codex_ repository. Focus on achieving 70% test coverage and completing all approved improvement proposals.

## Context

This is a continuation of the comprehensive QA walkthrough. The following has been completed:

### ✅ COMPLETED
- QA Walkthrough (6/6 phases)
- IP-001 Phase 1: 197 unit tests for 8 modules
- IP-001 Phase 2: 65 integration tests for 3 modules
- Planset Verification: All plansets verified
- IP Approval: IP-001 to IP-005 APPROVED by @mbaetiong
- Total new tests: **262 tests (all passing)**

### 📊 Current Coverage
- Before: 27.5% (196 files with tests)
- After: ~30.1% (207 files with tests)
- Target: 70% (500+ files)
- Goal: 100% (714 files)

## Verified Plansets Status

### Immediate ✅
1. ✅ Review QA walkthrough - COMPLETE
2. ✅ Approve improvement proposals - APPROVED
3. ✅ Start IP-003 (SECURITY.md exists - 387 lines)

### Short Term (In Progress)
1. ⏳ Complete IP-003 - Enhance with 137 security-critical files docs
2. ⏳ Complete IP-002 - Legacy config audit
3. ✅ Start IP-001 Phase 1 - COMPLETE (262 tests)

### Medium Term
1. ⏳ Complete IP-001 all phases - ~30% done
2. ⏳ Complete IP-004 - NOT STARTED (needs IP-003)
3. ⏳ Complete IP-005 - NOT STARTED

### Long Term
1. ⏳ Reach 100% coverage - Target
2. ⏳ Production RAG pipeline - Future
3. ⏳ Remove all legacy code - Future

## Current Task: Continue IP-001 Phase 3 + IP-002 + IP-003

### IP-001 Phase 3: More Integration Tests

Add tests for these high-priority untested modules (sorted by size):

1. `src/codex_ml/eval/runner.py` (34,959 bytes) - Eval runner
2. `src/codex_ml/codex_structured_logging.py` (13,440 bytes) - Structured logging
3. `src/codex_ml/eval/datasets.py` (9,293 bytes) - Eval datasets
4. `src/codex_ml/eval/fallback.py` (3,762 bytes) - Fallback handling
5. `src/codex_ml/main.py` (3,236 bytes) - Main entry point
6. `src/codex_ml/codex_script.py` (2,650 bytes) - Script utilities
7. `agents/cognitive_adapter.py` - Cognitive adapter
8. `agents/physics_orchestrator.py` - Physics orchestrator

### IP-002: Legacy Configuration Consolidation

1. Audit `config_legacy/` directory
2. Audit `yaml_legacy/` directory
3. Create migration plan to modern `configs/`
4. Map legacy → modern equivalents

### IP-003: Enhance Security Documentation

1. Enhance SECURITY.md (currently 387 lines)
2. Document 137 security-critical files from security_audit.json
3. Create security review checklist
4. Add inline documentation to security-critical files

## Files to Reference

- `.codex/qa_walkthrough/coverage_analysis.json` - 507 untested modules remaining
- `.codex/qa_walkthrough/coverage_analysis_update.json` - Latest coverage update
- `.codex/qa_walkthrough/security_audit.json` - 137 security files
- `.codex/qa_walkthrough/conflict_matrix.json` - Legacy conflicts
- `.codex/plans/COMPREHENSIVE_PLANSET_VERIFICATION.md` - Full planset
- `.codex/NEXT_STEPS_VERIFICATION.md` - Verification status
- `COGNITIVE_BRAIN_STATUS_PHASE_UPDATE.md` - Current status

## Expected Outcomes

1. Add 100+ more tests for high-priority modules
2. Enhance SECURITY.md with security-critical file documentation
3. Complete IP-002 legacy config audit
4. Achieve 40%+ coverage
5. Update cognitive brain status

## Self-Review Required

After completing tasks:
1. Run `python -m pytest tests/ -v --tb=short` to verify all tests pass
2. Run code review
3. Update coverage_analysis_update.json
4. Update cognitive brain status
5. Post continuation prompt if needed

## Cache Available

All QA walkthrough caches are current:
- Module inventory with AST analysis
- Coverage analysis with priority rankings
- Security audit results
- Planset verification document
- Action log with session history

---

**Previous Session**: Planset Verification + IP-001 Phase 1 & 2 (2026-01-16)
**Current Phase**: IP-001 Phase 3 + IP-002 + IP-003
**Tests Added This Session**: 262
**Iterations**: Continue until 70% coverage or session ends
