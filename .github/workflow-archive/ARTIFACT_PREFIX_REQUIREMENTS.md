# Artifact Prefix Requirements

**Purpose**: Document workflows requiring `Art_` prefix for downloadable artifact discoverability  
**Date**: 2026-02-06  
**Status**: Ready for implementation  
**Total Workflows**: 42

---

## 📋 Executive Summary

**Requirement**: All workflows that produce downloadable artifacts via `actions/upload-artifact` **MUST** have their display name prefixed with `Art_` for easy identification.

**Current Status**: 0 of 42 workflows (0%) have the `Art_` prefix  
**Target Status**: 42 of 42 workflows (100%) with `Art_` prefix  
**Implementation**: Update `name:` field in each workflow YAML

---

## 🎯 Implementation Guide

### Quick Fix Pattern

```yaml
# BEFORE (no prefix)
name: Testing Suite

# AFTER (with prefix)
name: Art_Testing Suite
```

### Bulk Implementation Script

```bash
#!/bin/bash
# Script to add Art_ prefix to artifact-producing workflows

WORKFLOWS=(
  "agent-chain-orchestrator.yml"
  "audit-improvement-pipeline.yml"
  # ... (add all 42 workflows from list below)
)

for workflow in "${WORKFLOWS[@]}"; do
  # Backup original
  cp .github/workflows/$workflow .github/workflows/$workflow.bak
  
  # Add Art_ prefix to name field
  sed -i 's/^name: \(.*\)/name: Art_\1/' .github/workflows/$workflow
  
  echo "✅ Updated: $workflow"
done

echo "🎉 All artifact workflows updated!"
```

---

## 📦 Complete Workflow List (42 Workflows)

### Category: Agent Workflows (1)

1. **agent-chain-orchestrator.yml**
   - Current: `Agent Chain Orchestrator (Quantum-Inspired)`
   - Required: `Art_Agent Chain Orchestrator (Quantum-Inspired)`
   - Artifacts: 1 (agent-chain-plan)
   - Priority: High

### Category: Authentication (1)

2. **auth-compliance-report.yml**
   - Current: `Auth Compliance Report Generator`
   - Required: `Art_Auth Compliance Report Generator`
   - Artifacts: 1 (compliance-report)
   - Priority: Medium

### Category: CI/CD (5)

3. **audit-improvement-pipeline.yml**
   - Current: `Audit & Improvement Pipeline`
   - Required: `Art_Audit & Improvement Pipeline`
   - Artifacts: 2 (audit-results, audit-run-manifest)
   - Priority: High

4. **batch-ci-triage.yml**
   - Current: `Batch CI Failure Triage`
   - Required: `Art_Batch CI Failure Triage`
   - Artifacts: 2 (triage-report, failed-workflow-logs)
   - Priority: High

5. **ci-health-suite.yml**
   - Current: `CI Health Suite`
   - Required: `Art_CI Health Suite`
   - Artifacts: 1 (ci-health-report)
   - Priority: High

6. **post-merge-validation-optimized.yml**
   - Current: `Post-Merge Validation (Optimized)`
   - Required: `Art_Post-Merge Validation (Optimized)`
   - Artifacts: 1 (modernization-report)
   - Priority: High

7. **rust_swarm_ci.yml**
   - Current: `Rust-Python Hybrid Swarm CI/CD`
   - Required: `Art_Rust-Python Hybrid Swarm CI/CD`
   - Artifacts: 6 (build, test, coverage, benchmarks, integration logs)
   - Priority: Critical (most artifacts)

### Category: Cognitive (4)

8. **cognitive-action.yml**
   - Current: `Cognitive Action System`
   - Required: `Art_Cognitive Action System`
   - Artifacts: 1 (cognitive-action-result)
   - Priority: Medium

9. **cognitive-aftermath.yml**
   - Current: `Cognitive Aftermath Analysis`
   - Required: `Art_Cognitive Aftermath Analysis`
   - Artifacts: 1 (cognitive-aftermath-report)
   - Priority: Medium

10. **cognitive-brain-feed.yml**
    - Current: `Cognitive Brain Feed`
    - Required: `Art_Cognitive Brain Feed`
    - Artifacts: 1 (cognitive-brain-feed)
    - Priority: Medium

11. **cognitive-decision.yml**
    - Current: `Cognitive Decision Engine`
    - Required: `Art_Cognitive Decision Engine`
    - Artifacts: 1 (cognitive-decision-result)
    - Priority: Medium

### Category: Documentation (2)

12. **documentation-link-checker.yml**
    - Current: `Documentation Link Checker`
    - Required: `Art_Documentation Link Checker`
    - Artifacts: 1 (link-check-report)
    - Priority: Medium

13. **documentation-suite.yml**
    - Current: `Documentation Suite`
    - Required: `Art_Documentation Suite`
    - Artifacts: 1 (documentation-artifacts)
    - Priority: Medium

### Category: Monitoring (6)

14. **biweekly-research-digest.yml**
    - Current: `Biweekly Research Digest`
    - Required: `Art_Biweekly Research Digest`
    - Artifacts: 1 (research-digest)
    - Priority: Low

15. **publish_dashboard_release.yml**
    - Current: `Publish Dashboard Release`
    - Required: `Art_Publish Dashboard Release`
    - Artifacts: 1 (dashboard-release)
    - Priority: High

16. **repository-health-monitoring.yml**
    - Current: `Repository Health Monitoring`
    - Required: `Art_Repository Health Monitoring`
    - Artifacts: 1 (health-monitoring-report)
    - Priority: High

17. **workflow-analytics-manual.yml**
    - Current: `Manual Workflow Analytics`
    - Required: `Art_Manual Workflow Analytics`
    - Artifacts: 1 (workflow-analytics-report)
    - Priority: Medium

18. **workflow-analytics-scheduled.yml**
    - Current: `Scheduled Workflow Analytics`
    - Required: `Art_Scheduled Workflow Analytics`
    - Artifacts: 1 (workflow-trends)
    - Priority: Medium

19. **workflow-health-check.yml**
    - Current: `Workflow Health Check (Quantum-Inspired)`
    - Required: `Art_Workflow Health Check (Quantum-Inspired)`
    - Artifacts: 1 (workflow-health-report)
    - Priority: Medium

### Category: Other (15)

20. **code-quality.yml**
    - Current: `Code Quality Analysis`
    - Required: `Art_Code Quality Analysis`
    - Artifacts: 1 (code-quality-report)
    - Priority: High

21. **codebase-qa-walkthrough.yml**
    - Current: `Codebase QA Walkthrough`
    - Required: `Art_Codebase QA Walkthrough`
    - Artifacts: 1 (qa-walkthrough-report)
    - Priority: High

22. **coverage_report.yml**
    - Current: `Coverage Report Generator`
    - Required: `Art_Coverage Report Generator`
    - Artifacts: 1 (coverage-artifacts)
    - Priority: High

23. **data_validation.yml**
    - Current: `Data Validation Pipeline`
    - Required: `Art_Data Validation Pipeline`
    - Artifacts: 1 (validation-report)
    - Priority: Medium

24. **decode-validate-artifact.yml**
    - Current: `Decode & Validate Artifact`
    - Required: `Art_Decode & Validate Artifact`
    - Artifacts: 1 (validation-result)
    - Priority: Medium

25. **detect-duplicates.yml**
    - Current: `Duplicate Detection`
    - Required: `Art_Duplicate Detection`
    - Artifacts: 1 (duplicate-detection-report)
    - Priority: High

26. **determinism.yml**
    - Current: `Determinism Audit`
    - Required: `Art_Determinism Audit`
    - Artifacts: 1 (determinism-audit)
    - Priority: High

27. **flatten-repo-download.yml**
    - Current: `Flatten Repository Download`
    - Required: `Art_Flatten Repository Download`
    - Artifacts: 1 (flattened-repo)
    - Priority: Low

28. **generate-repository-structure.yml**
    - Current: `Generate Repository Structure`
    - Required: `Art_Generate Repository Structure`
    - Artifacts: 1 (repository-structure)
    - Priority: Medium

29. **html_visual_baseline.yml**
    - Current: `HTML Visual Baseline Generator`
    - Required: `Art_HTML Visual Baseline Generator`
    - Artifacts: 1 (status-html-visual)
    - Priority: Medium

30. **html_visual_regression.yml**
    - Current: `HTML Visual Regression Testing`
    - Required: `Art_HTML Visual Regression Testing`
    - Artifacts: 1 (status-html-screenshots)
    - Priority: Medium

31. **integration-gated.yml**
    - Current: `Integration Tests (Gated)`
    - Required: `Art_Integration Tests (Gated)`
    - Artifacts: 1 (integration-test-results)
    - Priority: High

32. **monthly-model-retraining.yml**
    - Current: `Monthly Model Retraining`
    - Required: `Art_Monthly Model Retraining`
    - Artifacts: 1 (model-training-artifacts)
    - Priority: Medium

33. **notebooklm-sync.yml**
    - Current: `NotebookLM Sync`
    - Required: `Art_NotebookLM Sync`
    - Artifacts: 1 (notebooklm-sync-report)
    - Priority: Low

34. **pr-followup-generator.yml**
    - Current: `PR Follow-up Generator`
    - Required: `Art_PR Follow-up Generator`
    - Artifacts: 1 (pr-followup)
    - Priority: Medium

35. **root-org-validation.yml**
    - Current: `Root Organization Validation`
    - Required: `Art_Root Organization Validation`
    - Artifacts: 3 (before, after, validation-report)
    - Priority: High

36. **zendesk-knowledge-sync.yml**
    - Current: `Zendesk Knowledge Sync`
    - Required: `Art_Zendesk Knowledge Sync`
    - Artifacts: 1 (zendesk-sync-report)
    - Priority: Low

### Category: Security (7)

37. **codeql-chunked.yml**
    - Current: `CodeQL Chunked Analysis`
    - Required: `Art_CodeQL Chunked Analysis`
    - Artifacts: 3 (chunk-1, chunk-2, chunk-3)
    - Priority: Critical (security)

38. **dependency-scan.yml**
    - Current: `Dependency Security Scan`
    - Required: `Art_Dependency Security Scan`
    - Artifacts: 1 (dependency-scan-report)
    - Priority: High

39. **scheduled-dependency-audit.yml**
    - Current: `Scheduled Dependency Audit & SBOM`
    - Required: `Art_Scheduled Dependency Audit & SBOM`
    - Artifacts: 2 (audit-report, sbom-artifacts)
    - Priority: High

40. **security-scan.yml**
    - Current: `Security Scan`
    - Required: `Art_Security Scan`
    - Artifacts: 1 (security-scan-report)
    - Priority: High

41. **security-scanning-suite.yml**
    - Current: `Security Scanning Suite`
    - Required: `Art_Security Scanning Suite`
    - Artifacts: 3 (scan-results, vulnerability-report, sarif-results)
    - Priority: Critical (security)

42. **security-suite.yml**
    - Current: `Unified Security Suite`
    - Required: `Art_Unified Security Suite`
    - Artifacts: 1 (security-suite-results)
    - Priority: High

43. **self-healing.yml**
    - Current: `Self-Healing CI/CD`
    - Required: `Art_Self-Healing CI/CD`
    - Artifacts: 1 (self-healing-report)
    - Priority: High

44. **semgrep_sarif.yml**
    - Current: `Semgrep SAST (SARIF Upload)`
    - Required: `Art_Semgrep SAST (SARIF Upload)`
    - Artifacts: 1 (semgrep-sarif-results)
    - Priority: High

### Category: Testing (4)

45. **copilot-self-evolution.yml**
    - Current: `Copilot Self-Evolution`
    - Required: `Art_Copilot Self-Evolution`
    - Artifacts: 1 (evolution-state)
    - Priority: High

46. **test-comprehensive.yml**
    - Current: `Comprehensive Tests with Caching`
    - Required: `Art_Comprehensive Tests with Caching`
    - Artifacts: 4 (test-results, coverage, performance, logs)
    - Priority: High

47. **test-rag.yml**
    - Current: `RAG Module Tests`
    - Required: `Art_RAG Module Tests`
    - Artifacts: 2 (test-results, coverage-report)
    - Priority: High

48. **test-suite.yml**
    - Current: `Testing Suite`
    - Required: `Art_Testing Suite`
    - Artifacts: 5 (pytest, coverage-html, coverage-xml, logs, benchmarks)
    - Priority: Critical (most test artifacts)

### Category: Validation (1)

49. **workflow-link-validation.yml**
    - Current: `Workflow Documentation Link Validation`
    - Required: `Art_Workflow Documentation Link Validation`
    - Artifacts: 1 (link-validation-report)
    - Priority: Medium

---

## 📊 Priority Breakdown

| Priority | Count | % of Total | Recommendation |
|----------|-------|-----------|----------------|
| **Critical** | 4 | 8% | Implement immediately (Week 1) |
| **High** | 24 | 50% | Implement in Week 1-2 |
| **Medium** | 16 | 33% | Implement in Week 2-3 |
| **Low** | 4 | 8% | Implement in Week 3-4 |

### Critical Priority (4 workflows)
These produce the most artifacts or are security-critical:
1. rust_swarm_ci.yml (6 artifacts)
2. codeql-chunked.yml (3 artifacts, security)
3. security-scanning-suite.yml (3 artifacts, security)
4. test-suite.yml (5 artifacts)

### High Priority (24 workflows)
Key operational workflows with frequent artifact access:
- All testing workflows (test-comprehensive, test-rag, integration-gated)
- All security workflows (dependency-scan, security-scan, semgrep, self-healing)
- Critical CI/CD workflows (audit-improvement, batch-ci-triage, post-merge-validation)
- Quality workflows (code-quality, codebase-qa, coverage_report, detect-duplicates, determinism)

---

## 🔍 Verification Script

```bash
#!/bin/bash
# Verify Art_ prefix implementation

echo "🔍 Checking Art_ prefix implementation..."

# Expected workflows
expected=(
  "agent-chain-orchestrator.yml"
  "audit-improvement-pipeline.yml"
  # ... (all 42 workflows)
)

missing=0
for workflow in "${expected[@]}"; do
  if ! grep -q "^name: Art_" .github/workflows/$workflow; then
    echo "❌ Missing Art_ prefix: $workflow"
    ((missing++))
  else
    echo "✅ Has Art_ prefix: $workflow"
  fi
done

echo ""
if [ $missing -eq 0 ]; then
  echo "🎉 All 42 workflows have Art_ prefix!"
else
  echo "⚠️  $missing workflows missing Art_ prefix"
  exit 1
fi
```

---

## 📝 Implementation Checklist

### Pre-Implementation
- [ ] Backup all 42 workflow files
- [ ] Create rollback script
- [ ] Test prefix addition on 1 workflow
- [ ] Verify workflow still triggers correctly

### Implementation (Batch 1 - Critical)
- [ ] rust_swarm_ci.yml
- [ ] codeql-chunked.yml
- [ ] security-scanning-suite.yml
- [ ] test-suite.yml

### Implementation (Batch 2 - High Priority)
- [ ] audit-improvement-pipeline.yml
- [ ] batch-ci-triage.yml
- [ ] ci-health-suite.yml
- [ ] post-merge-validation-optimized.yml
- [ ] code-quality.yml
- [ ] codebase-qa-walkthrough.yml
- [ ] coverage_report.yml
- [ ] detect-duplicates.yml
- [ ] determinism.yml
- [ ] integration-gated.yml
- [ ] root-org-validation.yml
- [ ] dependency-scan.yml
- [ ] scheduled-dependency-audit.yml
- [ ] security-scan.yml
- [ ] security-suite.yml
- [ ] self-healing.yml
- [ ] semgrep_sarif.yml
- [ ] copilot-self-evolution.yml
- [ ] test-comprehensive.yml
- [ ] test-rag.yml
- [ ] publish_dashboard_release.yml
- [ ] repository-health-monitoring.yml
- [ ] agent-chain-orchestrator.yml

### Implementation (Batch 3 - Medium Priority)
- [ ] auth-compliance-report.yml
- [ ] cognitive-action.yml
- [ ] cognitive-aftermath.yml
- [ ] cognitive-brain-feed.yml
- [ ] cognitive-decision.yml
- [ ] documentation-link-checker.yml
- [ ] documentation-suite.yml
- [ ] workflow-analytics-manual.yml
- [ ] workflow-analytics-scheduled.yml
- [ ] workflow-health-check.yml
- [ ] data_validation.yml
- [ ] decode-validate-artifact.yml
- [ ] generate-repository-structure.yml
- [ ] html_visual_baseline.yml
- [ ] html_visual_regression.yml
- [ ] pr-followup-generator.yml
- [ ] workflow-link-validation.yml
- [ ] monthly-model-retraining.yml

### Implementation (Batch 4 - Low Priority)
- [ ] biweekly-research-digest.yml
- [ ] flatten-repo-download.yml
- [ ] notebooklm-sync.yml
- [ ] zendesk-knowledge-sync.yml

### Post-Implementation
- [ ] Run verification script
- [ ] Update ARTIFACT_CATALOG.md with new names
- [ ] Update documentation referencing workflow names
- [ ] Test artifact retrieval with new prefixed names
- [ ] Commit changes with descriptive message
- [ ] Create PR for review

---

## 🎯 Expected Outcomes

### Discoverability
**Before**: Users must search through 108 workflows to find artifact producers  
**After**: Users can filter by `Art_` prefix to see only 42 artifact-producing workflows

### GitHub UI Enhancement
**Actions Tab**: Workflows with artifacts clearly identified by `Art_` prefix

### Artifact Retrieval
**Command**: `gh workflow list | grep "Art_"` shows only artifact-producing workflows

### Documentation
**Clarity**: Artifact catalog can reference workflows by their prefixed names

---

## 📚 Related Documentation

- **Workflow Analysis**: `.github/workflow-archive/WORKFLOW_ANALYSIS_COMPLETE.md`
- **Artifact Catalog**: `.github/workflow-archive/ARTIFACT_CATALOG.md`
- **Consolidation Planset**: `.github/workflow-archive/WORKFLOW_CONSOLIDATION_PLANSET_V2.md` (pending)

---

## 🔄 Rollback Procedure

If prefix causes issues:

```bash
#!/bin/bash
# Rollback Art_ prefix changes

for backup in .github/workflows/*.bak; do
  original="${backup%.bak}"
  cp "$backup" "$original"
  echo "✅ Restored: $original"
done

echo "🔄 Rollback complete!"
```

---

**Document Status**: ✅ Ready for Implementation  
**Review Required**: Yes  
**Estimated Time**: 2-4 hours (batched implementation)  
**Risk Level**: Low (cosmetic change to `name:` field)

---

*Generated by GitHub Copilot Agent*  
*Date: 2026-02-06*  
*Version: 1.0*
