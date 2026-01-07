# Production Readiness Checklist — _codex_ Repository

**Last Updated**: 2025-12-05 (PR #2390)  
**Status**: 🟡 IN PROGRESS (40% Complete)

---

## Core Infrastructure ✅ COMPLETE

### Audit Pipeline
- [x] S1-S7 stages implemented
- [x] Deterministic output normalization (patches 0006)
- [x] Context index sorting
- [x] Capability scoring with weighted components
- [x] Template rendering (Jinja2)
- [x] JSON artifacts with sort_keys=True

### CI/CD Workflows
- [x] space-audit.yml (fast + full jobs)
- [x] produce-trend.yml (scheduled daily)
- [x] Quality gates with PR comments
- [x] Artifact upload/download
- [x] Baseline management

### Baseline System
- [x] establish_baseline.sh with metadata
- [x] SHA256 verification
- [x] metadata.json generation
- [x] Age-based rotation logic

---

## Code Quality 🟡 IN PROGRESS

### Import Hygiene
- [x] Hydra shadowing resolved (hydra/ → config_legacy/)
- [x] YAML shadowing prevention (site-packages verification)
- [x] AST-based refactor tooling (refactor_imports.py)
- [ ] **Legacy imports reduced ≥50%** (0/99 → target ≤50)
  - Current: 99 occurrences
  - Target: ≤50 occurrences
  - Priority files identified: ~10-15 in scripts/ and cli/

### Testing
- [x] Validation test suite (tests/validation/)
- [x] Determinism tests
- [x] Shadowing tests
- [x] Template hash validation
- [ ] **Full test suite passing** (pending execution)
- [ ] Integration tests for refactored imports

### Security
- [x] CodeQL scanning enabled
- [x] No high/critical vulnerabilities (0 alerts)
- [x] Conflict verification (verify_conflicts.py)
- [x] Safe import resolution

---

## Documentation 🟡 IN PROGRESS

### User Guides
- [x] Usage_Guide.md (audit commands)
- [x] Traversal_Workflow.md
- [x] Convergence_Runbook.md foundation
- [ ] **Reviewer Sign-off Checklist** (in runbook)
- [ ] Baseline lifecycle documentation
- [ ] Trend monitoring guide

### Developer Guides
- [x] AST refactor tool documentation
- [x] Mapping strategy (mappings/README.md)
- [x] Batch PR templates
- [ ] Contributing guidelines for refactors
- [ ] Rollback procedures (tested)

### Status Reports
- [x] v1.2.7 Status Report
- [x] Wave summaries (partial)
- [ ] **Final production readiness report**
- [ ] Metrics dashboard or visualization

---

## Monitoring & Observability 🟡 IN PROGRESS

### Trend Capture
- [x] capability_trends.jsonl format defined
- [x] Scheduled workflow (daily 03:00 UTC)
- [x] Manual trigger (workflow_dispatch)
- [ ] **Trend data populated** (requires execution)
- [ ] Visualization script (plot_trends.py)

### Metrics
- [x] Top 10 capabilities tracking
- [x] Low maturity count
- [x] Baseline SHA tracking
- [ ] Historical trend analysis
- [ ] Regression alert thresholds

---

## Validation & Determinism ⏸️ PENDING EXECUTION

### Determinism
- [x] verify_determinism.py script
- [x] Normalization logic (remove timestamps, sort, round)
- [x] Two-run comparison
- [ ] **Proven deterministic** (2 runs → identical output)
- [ ] SHA equality documented

### Shadowing
- [x] verify_conflicts.py --expect-site-packages
- [x] yaml → site-packages ✅
- [ ] **hydra → site-packages** (requires pip install hydra-core)
- [ ] Split-brain resolution (training, tokenization)

### Regression Testing
- [x] Baseline diff script
- [x] regression_diff.txt capture
- [x] fail_on_score_regression flag
- [ ] **Baseline comparison executed**
- [ ] No unexpected regressions

---

## Acceptance Criteria Summary

### Critical (Must Pass)
| Criterion | Status | Blocker |
|-----------|--------|---------|
| Determinism (2-run equality) | ⏸️ Pending | Requires full audit execution |
| Shadowing (yaml/hydra) | ⚠️ Partial | hydra-core not installed |
| Legacy imports (≥50% reduction) | ❌ 0% | Refactoring not started |
| Tests PASS | ⏸️ Pending | pytest not available in env |
| Security (0 critical) | ✅ PASS | - |

### Important (Should Pass)
| Criterion | Status | Note |
|-----------|--------|------|
| CI artifacts uploaded | ✅ Ready | Workflow configured |
| Baseline metadata | ✅ Ready | System implemented |
| Documentation complete | 🟡 80% | Final polish needed |
| Monitoring active | 🟡 Ready | Needs execution |
| Rollback tested | 📋 Documented | Not executed |

---

## Remaining Work (Priority Order)

### Phase 1: Immediate (v1.2.8)
1. **Targeted Import Refactoring** (~10-15 files)
   - scripts/train.py
   - cli/task_sequence.py
   - cli/script_polish.py
   - Other high-impact files
   - Validate after each batch (3-5 files)

2. **Full Validation Execution**
   - Run with proper dependencies
   - Document all results
   - Capture artifacts

3. **Determinism Proof**
   - Two consecutive full runs
   - SHA comparison
   - Evidence attachment

### Phase 2: Documentation (v1.2.9)
1. Update Convergence_Runbook.md with reviewer checklist
2. Finalize Usage_Guide.md with all workflows
3. Create production deployment guide
4. Document monitoring and alerts

### Phase 3: Polish (v1.3.0)
1. Trend visualization script
2. Automated reporting
3. Dashboard (optional)
4. Performance optimization

---

## Risk Register

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Tests fail post-refactor | HIGH | MEDIUM | Batch validation, .bak files |
| Determinism breaks | HIGH | LOW | Patches applied, tested logic |
| Baseline corruption | MEDIUM | LOW | Git-tracked, SHA-verified |
| CI workflow failures | MEDIUM | LOW | Manual trigger available |
| Documentation drift | LOW | MEDIUM | Automated checks, reviews |

---

## Sign-off Requirements

### Technical Lead
- [ ] Code review complete
- [ ] Architecture approved
- [ ] Security scan passed ✅
- [ ] Performance acceptable

### QA/Validation
- [ ] All tests passing
- [ ] Determinism proven
- [ ] Regression tests passed
- [ ] Edge cases covered

### Product/Documentation
- [ ] User guides complete
- [ ] API documentation current
- [ ] Examples tested
- [ ] Release notes prepared

### Maintainer (mbaetiong)
- [x] Autonomous execution approved ✅
- [ ] Final review and merge authorization
- [ ] Production deployment approval

---

## Current Status: 40% Complete

**Completed**: Infrastructure, tooling, documentation framework, security  
**In Progress**: Import refactoring, validation execution  
**Pending**: Final polish, monitoring activation

**Target Completion**: v1.3.0 (estimated 3-5 iterations)

---

**Last Validated**: 2025-12-05 (commit e902006)  
**Next Review**: After v1.2.8 completion  
**Reviewer**: @mbaetiong
