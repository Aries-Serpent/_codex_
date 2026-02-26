# Phase 2 Workflow Consolidation - Preparation Guide

**Phase 1 Status**: ✅ COMPLETE  
**Current Workflows**: 73  
**Phase 2 Target**: 48  
**Remaining Consolidation**: 25 workflows

---

## 📊 Phase 1 Achievement Summary

Phase 1 successfully reduced workflows from **108 to 73** (32% reduction), **exceeding the target of 78 by 5 workflows**.

**Phase 1 Consolidations:**
- Group 3 (Cache): 5 workflows → Distributed pattern
- Group 2 (Test): 2 workflows → optimized-ci.yml
- Group 7 (Analytics): 3 workflows → workflow-analytics-unified.yml
- Group 6 (CodeQL): 1 workflow → codeql-analysis.yml
- Group 4 (CI Health): 2 workflows → ci-health-monitor.yml
- Group 10 (Misc): 4 workflows → .github/misc/
- Group 1 (Security): 2 workflows → security-scanning-suite.yml
- Group 8 (Self-Healing): 2 workflows → self-healing.yml
- Group 5 (Auth): 7 workflows → Manual/on-demand
- Final Groups: 11 workflows → Various consolidations

**Total**: 35 workflows disabled/moved, 4 new groups moved to misc/, 1 new unified workflow created

---

## 🎯 Phase 2 Consolidation Candidates

To reach target of 48 workflows, we need to consolidate **25 more workflows**.

### High-Priority Candidates (10 workflows)

**1. Cognitive Workflows** (4 workflows)
- cognitive-action.yml
- cognitive-decision.yml
- cognitive-aftermath.yml
- cognitive-brain-feed.yml

**Consolidation Strategy:**
- Merge action + decision → cognitive-action-decision.yml
- Merge aftermath + feed → cognitive-analysis-feed.yml
- **Reduction**: 4 → 2 (save 2 workflows)

**2. Agent Workflows** (2 workflows)
- agent-chain-orchestrator.yml
- agent_handoff.yml

**Consolidation Strategy:**
- Merge into unified agent-orchestration.yml
- **Reduction**: 2 → 1 (save 1 workflow)

**3. Copilot Workflows** (2 workflows)
- copilot-cascade-review.yml
- copilot-self-evolution.yml

**Consolidation Strategy:**
- Merge into copilot-evolution-suite.yml
- **Reduction**: 2 → 1 (save 1 workflow)

**4. Audit Workflows** (2 workflows)
- audit-improvement-pipeline.yml
- codebase-qa-walkthrough.yml

**Consolidation Strategy:**
- Merge into unified audit-qa-suite.yml
- **Reduction**: 2 → 1 (save 1 workflow)

### Medium-Priority Candidates (8 workflows)

**5. Deployment Workflows** (2 workflows)
- deploy-cognitive-app.yml
- pre-release-deployment.yml

**6. Coverage/Quality** (2 workflows)
- coverage_report.yml
- code-quality.yml

**7. Data/Validation** (2 workflows)
- data_validation.yml
- determinism.yml

**8. HTML/Visual** (2 workflows)
- html_visual_regression.yml (keep)
- Any remaining visual workflows

### Lower-Priority Candidates (7 workflows)

**9. Specialized Testing** (3 workflows)
- integration-gated.yml (if not already disabled)
- test-rag.yml
- batch-ci-triage.yml

**10. Specialized Workflows** (4 workflows)
- genesis-bootstrap.yml (could move to misc)
- artifact-monitoring.yml
- autonomous-agent.yml
- dependency-scan.yml

---

## 📋 Phase 2 Execution Plan

### Week 1: High-Priority (10 workflows → 4 workflows)
**Target**: Save 6 workflows

1. **Day 1-2**: Cognitive workflows consolidation
   - Create cognitive-action-decision.yml
   - Create cognitive-analysis-feed.yml
   - Disable 4 old workflows

2. **Day 3-4**: Agent & Copilot consolidation
   - Create agent-orchestration.yml
   - Create copilot-evolution-suite.yml
   - Disable 4 old workflows

3. **Day 5**: Audit workflows consolidation
   - Create audit-qa-suite.yml
   - Disable 2 old workflows

**Week 1 Result**: 73 → 67 workflows

---

### Week 2: Medium-Priority (8 workflows → 4 workflows)
**Target**: Save 4 workflows

1. **Day 1-2**: Deployment consolidation
   - Create unified-deployment.yml
   - Disable 2 old workflows

2. **Day 3-4**: Coverage/Quality consolidation
   - Create code-quality-coverage-suite.yml
   - Disable 2 old workflows

3. **Day 5**: Data/Validation consolidation
   - Create data-quality-suite.yml
   - Disable 2 old workflows

**Week 2 Result**: 67 → 63 workflows

---

### Week 3: Lower-Priority (7 workflows → 2 workflows)
**Target**: Save 5 workflows

1. **Day 1-3**: Specialized testing consolidation
   - Evaluate test-rag.yml (keep or merge)
   - Consolidate batch CI triage
   - Disable 3 workflows

2. **Day 4-5**: Specialized workflows review
   - Move genesis-bootstrap to misc (rarely used)
   - Evaluate autonomous-agent.yml
   - Consolidate artifact monitoring
   - Disable/move 4 workflows

**Week 3 Result**: 63 → 58 workflows

---

### Week 4: Final Optimization (10 workflows → 0 workflows)
**Target**: Save 10 workflows to reach 48

1. **Day 1-2**: Documentation consolidation
   - Merge documentation workflows if any remaining

2. **Day 3-4**: Final review and optimization
   - Identify any remaining low-usage workflows
   - Consider moving experimental workflows to misc/

3. **Day 5**: Validation and documentation
   - Update all documentation
   - Create Phase 2 completion report
   - Validate target achievement

**Week 4 Result**: 58 → 48 workflows ✅

---

## 🛡️ Phase 2 Safety Guidelines

### Before Each Consolidation
1. Review workflow usage patterns
2. Check for dependencies
3. Create consolidated workflow
4. Test on feature branch
5. Run in parallel for validation period

### During Consolidation
1. Create .meta files for all disabled workflows
2. Document consolidation rationale
3. Maintain backup references
4. Update artifact catalog

### After Each Consolidation
1. Monitor for 24-48 hours
2. Check for CI/CD failures
3. Validate artifact production
4. Update documentation

---

## 📝 Phase 2 Success Criteria

- [ ] Reduce from 73 to 48 workflows (25 workflows)
- [ ] All disabled workflows have .meta files
- [ ] Zero critical functionality lost
- [ ] Documentation comprehensive
- [ ] Backup/restore procedures verified
- [ ] CI/CD health maintained
- [ ] Phase 2 completion report created

---

## 🔗 Related Documentation

- Phase 1 Completion Report: `.github/workflow-archive/phase1-consolidation/PHASE1_COMPLETION_REPORT.md`
- Phase 1 Execution Plan: `.github/workflow-archive/phase1-consolidation/PHASE1_EXECUTION_PLAN.md`
- Parity Checklist: `.github/workflow-archive/PARITY_CHECKLIST.md`
- Consolidation Planset V2: `.github/workflow-archive/WORKFLOW_CONSOLIDATION_PLANSET_V2.md`

---

## 📞 Approval Required

Phase 2 consolidation requires explicit human admin approval before proceeding.

**To Approve Phase 2:**
Comment on PR: `"Approved: Phase 2 Consolidation"`

---

**Generated**: 2026-02-07  
**Status**: ⏳ AWAITING APPROVAL  
**Next Action**: Human admin review and approval
