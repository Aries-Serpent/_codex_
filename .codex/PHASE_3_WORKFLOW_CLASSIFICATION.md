# PHASE 3.1 - Workflow Classification Report
## CODEX_MASTER_KEY Campaign - Token Requirements Analysis

**Generated:** 2026-06-29T03:55:12.956830+00:00  
**Status:** ✅ COMPLETE  
**Total Workflows Classified:** 209

---

## Executive Summary

This report classifies all 209 GitHub Actions workflows into 3 categories based on their token requirements and security impact. The classification determines which workflows need the `CODEX_MASTER_KEY` token for elevated operations.

### Classification Overview

| Category | Count | Target | Status | Token Requirements |
|----------|-------|--------|--------|-------------------|
| **A: Elevated Ops** | 61 | 40-50 | ⚠️ Above | CODEX_MASTER_KEY required |
| **B: Mixed Ops** | 86 | 80-100 | ✅ In Range | Conditional CODEX_MASTER_KEY |
| **C: Standard Ops** | 62 | 60-70 | ✅ In Range | Standard github.token |
| **TOTAL** | **209** | **209** | ✅ Complete | - |

### Priority Distribution

- **CRITICAL:** 61 workflows (require immediate remediation)
- **HIGH:** 86 workflows (require Phase 3.2 implementation)
- **MEDIUM:** 62 workflows (Phase 3.3 optimization)

### Effort Estimate

- **Total Effort:** 374.0 hours
  - Category A: 183.0 hours (3h per workflow)
  - Category B: 172.0 hours (2h per workflow)
  - Category C: 19.0 hours (0.5h per workflow)

---

## Category Definitions

### Category A: Elevated Operations (CODEX_MASTER_KEY Required)
**61 workflows**

**Description:** Elevated Ops - Workflows requiring CODEX_MASTER_KEY for PR edits, variable writes, workflow dispatch, security events

**Characteristics:**
- Modify pull requests (edits, comments, approvals)
- Write to repository contents
- Write repository variables
- Trigger workflow dispatches
- Manage security events
- Force push or delete branches

**Risk Level:** HIGH - Requires authentication upgrade
**Phase 3.2 Action:** Implement CODEX_MASTER_KEY token management

**Workflows (sorted by name):**

  1. 🔴 **adaptive-agent-delegation.yml**
     - Path: `.github/workflows/adaptive-agent-delegation.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
  2. 🔴 **admin-action-t03.yml**
     - Path: `.github/workflows/admin-action-t03.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
  3. 🔴 **admin_setup_verification.yml**
     - Path: `.github/workflows/admin_setup_verification.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
  4. 🔴 **agent-auth-delegation.yml**
     - Path: `.github/workflows/agent-auth-delegation.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
  5. 🔴 **agent-var-writer.yml**
     - Path: `.github/workflows/agent-var-writer.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
  6. 🔴 **artifact-monitoring.yml**
     - Path: `.github/workflows/artifact-monitoring.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
  7. 🔴 **auto-approve-workflows.yml**
     - Path: `.github/workflows/auto-approve-workflows.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
  8. 🔴 **automated-rollback-generation.yml**
     - Path: `.github/workflows/automated-rollback-generation.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
  9. 🔴 **autonomy-phase-ci-matrix.yml**
     - Path: `.github/workflows/autonomy-phase-ci-matrix.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 10. 🔴 **batch-ci-triage.yml**
     - Path: `.github/workflows/batch-ci-triage.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 11. 🔴 **branch-divergence-monitor.yml**
     - Path: `.github/workflows/branch-divergence-monitor.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 12. 🔴 **cache-pruning.yml**
     - Path: `.github/workflows/cache-pruning.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 13. 🔴 **chatops_copilot_trigger.yml**
     - Path: `.github/workflows/chatops_copilot_trigger.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 14. 🔴 **ci-checkpoint-validation.yml**
     - Path: `.github/workflows/ci-checkpoint-validation.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 15. 🔴 **ci-failure-issue-creator.yml**
     - Path: `.github/workflows/ci-failure-issue-creator.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 16. 🔴 **ci-health-monitor.yml**
     - Path: `.github/workflows/ci-health-monitor.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: non_compliant
 17. 🔴 **cleanup-stale-pr-comments.yml**
     - Path: `.github/workflows/cleanup-stale-pr-comments.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: non_compliant
 18. 🔴 **codebase-health-sweep.yml**
     - Path: `.github/workflows/codebase-health-sweep.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 19. 🔴 **codeql-alert-fetcher.yml**
     - Path: `.github/workflows/codeql-alert-fetcher.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 20. 🔴 **codeql-analysis.yml**
     - Path: `.github/workflows/codeql-analysis.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 21. 🔴 **codeql.yml**
     - Path: `.github/workflows/codeql.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 22. 🔴 **codex-manifest-refresh.yml**
     - Path: `.github/workflows/codex-manifest-refresh.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 23. 🔴 **cognitive_brain_ci_feedback.yml**
     - Path: `.github/workflows/cognitive_brain_ci_feedback.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 24. 🔴 **comment-review-gate.yml**
     - Path: `.github/workflows/comment-review-gate.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 25. 🔴 **copilot-agent-checkin.yml**
     - Path: `.github/workflows/copilot-agent-checkin.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 26. 🔴 **copilot-agent-session-done.yml**
     - Path: `.github/workflows/copilot-agent-session-done.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 27. 🔴 **copilot-agent-vars-bootstrap.yml**
     - Path: `.github/workflows/copilot-agent-vars-bootstrap.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 28. 🔴 **copilot-issue-triage.yml**
     - Path: `.github/workflows/copilot-issue-triage.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 29. 🔴 **copilot-iterative-self-healing.yml**
     - Path: `.github/workflows/copilot-iterative-self-healing.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 30. 🔴 **copilot-pr-session-injector.yml**
     - Path: `.github/workflows/copilot-pr-session-injector.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 31. 🔴 **copilot-session-chain.yml**
     - Path: `.github/workflows/copilot-session-chain.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 32. 🔴 **copilot-setup-steps.yml**
     - Path: `.github/workflows/copilot-setup-steps.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: review_needed
 33. 🔴 **cost-gate.yml**
     - Path: `.github/workflows/cost-gate.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: review_needed
 34. 🔴 **create-sub-pr-to-0D_base_.yml**
     - Path: `.github/workflows/create-sub-pr-to-0D_base_.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 35. 🔴 **deferral-language-gate.yml**
     - Path: `.github/workflows/deferral-language-gate.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 36. 🔴 **dependabot-auto-absorb.yml**
     - Path: `.github/workflows/dependabot-auto-absorb.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 37. 🔴 **discussion-response-bridge.yml**
     - Path: `.github/workflows/discussion-response-bridge.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 38. 🔴 **docker-build-push.yml**
     - Path: `.github/workflows/docker-build-push.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 39. 🔴 **documentation-link-checker.yml**
     - Path: `.github/workflows/documentation-link-checker.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 40. 🔴 **github-guru.yml**
     - Path: `.github/workflows/github-guru.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 41. 🔴 **issue-resolution-gate.yml**
     - Path: `.github/workflows/issue-resolution-gate.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 42. 🔴 **iterative-self-healing-ci.yml**
     - Path: `.github/workflows/iterative-self-healing-ci.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 43. 🔴 **post-accountability-to-discussion.yml**
     - Path: `.github/workflows/post-accountability-to-discussion.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: review_needed
 44. 🔴 **post-ci-status-to-discussion.yml**
     - Path: `.github/workflows/post-ci-status-to-discussion.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: review_needed
 45. 🔴 **pr-followup-generator.yml**
     - Path: `.github/workflows/pr-followup-generator.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 46. 🔴 **pre-merge-validation.yml**
     - Path: `.github/workflows/pre-merge-validation.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 47. 🔴 **promote-integration-branch.yml**
     - Path: `.github/workflows/promote-integration-branch.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 48. 🔴 **ratelimit_history_prune.yml**
     - Path: `.github/workflows/ratelimit_history_prune.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 49. 🔴 **repo-var-sync-schedule.yml**
     - Path: `.github/workflows/repo-var-sync-schedule.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 50. 🔴 **resilient_validation.yml**
     - Path: `.github/workflows/resilient_validation.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 51. 🔴 **rust_swarm_ci.yml**
     - Path: `.github/workflows/rust_swarm_ci.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 52. 🔴 **session-context-capture.yml**
     - Path: `.github/workflows/session-context-capture.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: review_needed
 53. 🔴 **session-incremental-summary-reminder.yml**
     - Path: `.github/workflows/session-incremental-summary-reminder.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 54. 🔴 **session-recovery-continuous-monitoring.yml**
     - Path: `.github/workflows/session-recovery-continuous-monitoring.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 55. 🔴 **session-recovery-handler.yml**
     - Path: `.github/workflows/session-recovery-handler.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: non_compliant
 56. 🔴 **session-watchdog.yml**
     - Path: `.github/workflows/session-watchdog.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 57. 🔴 **test-rag.yml**
     - Path: `.github/workflows/test-rag.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: review_needed
 58. 🔴 **test-variables-api.yml**
     - Path: `.github/workflows/test-variables-api.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: review_needed
 59. 🔴 **token-probe.yml**
     - Path: `.github/workflows/token-probe.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: no_token
 60. 🔴 **trigger-on-approval.yml**
     - Path: `.github/workflows/trigger-on-approval.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: compliant
 61. 🔴 **workflow-execution-gate.yml**
     - Path: `.github/workflows/workflow-execution-gate.yml`
     - Priority: CRITICAL | Effort: 3.0h
     - Compliance: non_compliant

---

### Category B: Mixed Operations (Conditional CODEX_MASTER_KEY)
**86 workflows**

**Description:** Mixed Ops - Workflows with both standard and elevated operations

**Characteristics:**
- Mix of read and write operations
- Some elevated permissions needed
- Standard operations sufficient for some tasks
- Conditional token upgrade strategy possible

**Risk Level:** MEDIUM - Requires careful token management
**Phase 3.2 Action:** Implement selective CODEX_MASTER_KEY usage

**Top 20 Workflows by Priority (sorted by name):**

  1. 🟠 **actionlint-audit.yml**
     - Path: `.github/workflows/actionlint-audit.yml`
     - Priority: HIGH | Effort: 2.0h
  2. 🟠 **admin-action-notifier.yml**
     - Path: `.github/workflows/admin-action-notifier.yml`
     - Priority: HIGH | Effort: 2.0h
  3. 🟠 **agent-handoff-gate.yml**
     - Path: `.github/workflows/agent-handoff-gate.yml`
     - Priority: HIGH | Effort: 2.0h
  4. 🟠 **agent-orchestration-unified.yml**
     - Path: `.github/workflows/agent-orchestration-unified.yml`
     - Priority: HIGH | Effort: 2.0h
  5. 🟠 **agent-registry-validation.yml**
     - Path: `.github/workflows/agent-registry-validation.yml`
     - Priority: HIGH | Effort: 2.0h
  6. 🟠 **agent-task-janitor.yml**
     - Path: `.github/workflows/agent-task-janitor.yml`
     - Priority: HIGH | Effort: 2.0h
  7. 🟠 **agent_infrastructure_manager.yml**
     - Path: `.github/workflows/agent_infrastructure_manager.yml`
     - Priority: HIGH | Effort: 2.0h
  8. 🟠 **audit-qa-suite.yml**
     - Path: `.github/workflows/audit-qa-suite.yml`
     - Priority: HIGH | Effort: 2.0h
  9. 🟠 **auth-tests.yml**
     - Path: `.github/workflows/auth-tests.yml`
     - Priority: HIGH | Effort: 2.0h
 10. 🟠 **auto-fix-common-issues.yml**
     - Path: `.github/workflows/auto-fix-common-issues.yml`
     - Priority: HIGH | Effort: 2.0h
 11. 🟠 **auto-fix-pr-check.yml**
     - Path: `.github/workflows/auto-fix-pr-check.yml`
     - Priority: HIGH | Effort: 2.0h
 12. 🟠 **automated-release-creation.yml**
     - Path: `.github/workflows/automated-release-creation.yml`
     - Priority: HIGH | Effort: 2.0h
 13. 🟠 **autonomous-agent.yml**
     - Path: `.github/workflows/autonomous-agent.yml`
     - Priority: HIGH | Effort: 2.0h
 14. 🟠 **branch-cleanup.yml**
     - Path: `.github/workflows/branch-cleanup.yml`
     - Priority: HIGH | Effort: 2.0h
 15. 🟠 **branch-rebase-gate.yml**
     - Path: `.github/workflows/branch-rebase-gate.yml`
     - Priority: HIGH | Effort: 2.0h
 16. 🟠 **build-agent-env-cache.yml**
     - Path: `.github/workflows/build-agent-env-cache.yml`
     - Priority: HIGH | Effort: 2.0h
 17. 🟠 **build-preview-image.yml**
     - Path: `.github/workflows/build-preview-image.yml`
     - Priority: HIGH | Effort: 2.0h
 18. 🟠 **ci-pass-rate-gate.yml**
     - Path: `.github/workflows/ci-pass-rate-gate.yml`
     - Priority: HIGH | Effort: 2.0h
 19. 🟠 **ci-rescue.yml**
     - Path: `.github/workflows/ci-rescue.yml`
     - Priority: HIGH | Effort: 2.0h
 20. 🟠 **cleanup-stale-branches.yml**
     - Path: `.github/workflows/cleanup-stale-branches.yml`
     - Priority: HIGH | Effort: 2.0h

*... and 66 more Category B workflows*

---

### Category C: Standard Operations (Read-Only)
**62 workflows**

**Description:** Standard Ops - Workflows with read-only operations or no token usage

**Characteristics:**
- Read-only operations only
- No token modifications needed
- Lowest security risk
- Standard github.token sufficient

**Risk Level:** LOW - No action required
**Phase 3.2 Action:** Monitor for scope creep

**Workflows (sorted by name):**

  1. **agent-health-check.yml**
     - Path: `.github/workflows/agent-health-check.yml`
     - Priority: MEDIUM | Effort: 0.25h
  2. **api-documentation.yml**
     - Path: `.github/workflows/api-documentation.yml`
     - Priority: MEDIUM | Effort: 0.25h
  3. **app-package-download.yml**
     - Path: `.github/workflows/app-package-download.yml`
     - Priority: MEDIUM | Effort: 0.5h
  4. **automated-monitoring-setup.yml**
     - Path: `.github/workflows/automated-monitoring-setup.yml`
     - Priority: MEDIUM | Effort: 0.25h
  5. **automated-post-deployment-verification.yml**
     - Path: `.github/workflows/automated-post-deployment-verification.yml`
     - Priority: MEDIUM | Effort: 0.25h
  6. **behavior-compare.yaml**
     - Path: `.github/workflows/ci-templates/behavior-compare.yaml`
     - Priority: MEDIUM | Effort: 0.25h
  7. **benchmarks.yml**
     - Path: `.github/workflows/benchmarks.yml`
     - Priority: MEDIUM | Effort: 0.25h
  8. **cache-health-monitor.yml**
     - Path: `.github/workflows/cache-health-monitor.yml`
     - Priority: MEDIUM | Effort: 0.25h
  9. **cache-validation.yml**
     - Path: `.github/workflows/cache-validation.yml`
     - Priority: MEDIUM | Effort: 0.25h
 10. **ci-pattern-healer.yml**
     - Path: `.github/workflows/ci-pattern-healer.yml`
     - Priority: MEDIUM | Effort: 0.25h
 11. **ci-pattern-prevention-gate.yml**
     - Path: `.github/workflows/ci-pattern-prevention-gate.yml`
     - Priority: MEDIUM | Effort: 0.25h
 12. **cognitive-k8s-provisioning.yml**
     - Path: `.github/workflows/cognitive-k8s-provisioning.yml`
     - Priority: MEDIUM | Effort: 0.25h
 13. **cognitive-perception.yml**
     - Path: `.github/workflows/cognitive-perception.yml`
     - Priority: MEDIUM | Effort: 0.5h
 14. **consistency-checks.yml**
     - Path: `.github/workflows/consistency-checks.yml`
     - Priority: MEDIUM | Effort: 0.25h
 15. **consolidated-pr-status.yml**
     - Path: `.github/workflows/consolidated-pr-status.yml`
     - Priority: MEDIUM | Effort: 0.25h
 16. **container-scan.yml**
     - Path: `.github/workflows/container-scan.yml`
     - Priority: MEDIUM | Effort: 0.25h
 17. **copilot-automation.yml**
     - Path: `.github/workflows/copilot-automation.yml`
     - Priority: MEDIUM | Effort: 0.25h
 18. **copilot-setup-validation.yml**
     - Path: `.github/workflows/copilot-setup-validation.yml`
     - Priority: MEDIUM | Effort: 0.25h
 19. **dependabot-preflight.yml**
     - Path: `.github/workflows/dependabot-preflight.yml`
     - Priority: MEDIUM | Effort: 0.25h
 20. **dependency-scan.yml**
     - Path: `.github/workflows/dependency-scan.yml`
     - Priority: MEDIUM | Effort: 0.5h
 21. **doc-freshness-check.yml**
     - Path: `.github/workflows/doc-freshness-check.yml`
     - Priority: MEDIUM | Effort: 0.5h
 22. **doc-refresh-gate.yml**
     - Path: `.github/workflows/doc-refresh-gate.yml`
     - Priority: MEDIUM | Effort: 0.25h
 23. **docs-code-alignment.yml**
     - Path: `.github/workflows/docs-code-alignment.yml`
     - Priority: MEDIUM | Effort: 0.25h
 24. **docs-health.yml**
     - Path: `.github/workflows/docs-health.yml`
     - Priority: MEDIUM | Effort: 0.5h
 25. **documentation-quality-check.yml**
     - Path: `.github/workflows/documentation-quality-check.yml`
     - Priority: MEDIUM | Effort: 0.25h
 26. **flush-queued-runs.yml**
     - Path: `.github/workflows/flush-queued-runs.yml`
     - Priority: MEDIUM | Effort: 0.5h
 27. **import-linter.yml**
     - Path: `.github/workflows/import-linter.yml`
     - Priority: MEDIUM | Effort: 0.25h
 28. **maturity-check.yml**
     - Path: `.github/workflows/maturity-check.yml`
     - Priority: MEDIUM | Effort: 0.25h
 29. **mcp-cache-warm.yml**
     - Path: `.github/workflows/examples/mcp-cache-warm.yml`
     - Priority: MEDIUM | Effort: 0.25h
 30. **ml-lifecycle-gate.yml**
     - Path: `.github/workflows/ml-lifecycle-gate.yml`
     - Priority: MEDIUM | Effort: 0.25h
 31. **mutation-testing.yml**
     - Path: `.github/workflows/mutation-testing.yml`
     - Priority: MEDIUM | Effort: 0.25h
 32. **optimized-ci.yml**
     - Path: `.github/workflows/optimized-ci.yml`
     - Priority: MEDIUM | Effort: 0.5h
 33. **performance-gate.yml**
     - Path: `.github/workflows/performance-gate.yml`
     - Priority: MEDIUM | Effort: 0.5h
 34. **phase-8-2-issue-triage.yml**
     - Path: `.github/workflows/phase-8-2-issue-triage.yml`
     - Priority: MEDIUM | Effort: 0.5h
 35. **post-merge-validation-optimized.yml**
     - Path: `.github/workflows/post-merge-validation-optimized.yml`
     - Priority: MEDIUM | Effort: 0.5h
 36. **post-phase-update-to-discussion.yml**
     - Path: `.github/workflows/post-phase-update-to-discussion.yml`
     - Priority: MEDIUM | Effort: 0.25h
 37. **promotion-readiness-gate.yml**
     - Path: `.github/workflows/promotion-readiness-gate.yml`
     - Priority: MEDIUM | Effort: 0.25h
 38. **publish_dashboard_release.yml**
     - Path: `.github/workflows/publish_dashboard_release.yml`
     - Priority: MEDIUM | Effort: 0.5h
 39. **pypi-publish.yml**
     - Path: `.github/workflows/pypi-publish.yml`
     - Priority: MEDIUM | Effort: 0.25h
 40. **rag-freshness-scheduler.yml**
     - Path: `.github/workflows/rag-freshness-scheduler.yml`
     - Priority: MEDIUM | Effort: 0.25h
 41. **rag-quality-nightly.yml**
     - Path: `.github/workflows/rag-quality-nightly.yml`
     - Priority: MEDIUM | Effort: 0.25h
 42. **release.yml**
     - Path: `.github/workflows/release.yml`
     - Priority: MEDIUM | Effort: 0.25h
 43. **repo-organization.yml**
     - Path: `.github/workflows/repo-organization.yml`
     - Priority: MEDIUM | Effort: 0.25h
 44. **repository-health-monitoring.yml**
     - Path: `.github/workflows/repository-health-monitoring.yml`
     - Priority: MEDIUM | Effort: 0.25h
 45. **required-actions-enforcer.yml**
     - Path: `.github/workflows/required-actions-enforcer.yml`
     - Priority: MEDIUM | Effort: 0.25h
 46. **restore-pipeline-ci.yml**
     - Path: `.github/workflows/restore-pipeline-ci.yml`
     - Priority: MEDIUM | Effort: 0.5h
 47. **runner-diagnostics.yml**
     - Path: `.github/workflows/runner-diagnostics.yml`
     - Priority: MEDIUM | Effort: 0.5h
 48. **rust-error-validator-observation.yml**
     - Path: `.github/workflows/rust-error-validator-observation.yml`
     - Priority: MEDIUM | Effort: 0.25h
 49. **scheduled-archival.yml**
     - Path: `.github/workflows/scheduled-archival.yml`
     - Priority: MEDIUM | Effort: 0.25h
 50. **scheduled-dependency-audit.yml**
     - Path: `.github/workflows/scheduled-dependency-audit.yml`
     - Priority: MEDIUM | Effort: 0.25h
 51. **secrets-baseline-enforcer.yml**
     - Path: `.github/workflows/secrets-baseline-enforcer.yml`
     - Priority: MEDIUM | Effort: 0.25h
 52. **security-alert-notification.yml**
     - Path: `.github/workflows/security-alert-notification.yml`
     - Priority: MEDIUM | Effort: 0.25h
 53. **security-tools-bootstrap.yml**
     - Path: `.github/workflows/security-tools-bootstrap.yml`
     - Priority: MEDIUM | Effort: 0.25h
 54. **self-healing.yml**
     - Path: `.github/workflows/self-healing.yml`
     - Priority: MEDIUM | Effort: 0.25h
 55. **semgrep_sarif.yml**
     - Path: `.github/workflows/semgrep_sarif.yml`
     - Priority: MEDIUM | Effort: 0.25h
 56. **sigstore-verify.yml**
     - Path: `.github/workflows/sigstore-verify.yml`
     - Priority: MEDIUM | Effort: 0.5h
 57. **sync-env-vars.yml**
     - Path: `.github/workflows/sync-env-vars.yml`
     - Priority: MEDIUM | Effort: 0.25h
 58. **test-pyramid-report.yml**
     - Path: `.github/workflows/test-pyramid-report.yml`
     - Priority: MEDIUM | Effort: 0.25h
 59. **validate-api-null-handling.yml**
     - Path: `.github/workflows/validate-api-null-handling.yml`
     - Priority: MEDIUM | Effort: 0.25h
 60. **validate-code-examples.yml**
     - Path: `.github/workflows/validate-code-examples.yml`
     - Priority: MEDIUM | Effort: 0.25h
 61. **vars-guide-sync.yml**
     - Path: `.github/workflows/vars-guide-sync.yml`
     - Priority: MEDIUM | Effort: 0.25h
 62. **workflow-restore.yml**
     - Path: `.github/workflows/workflow-restore.yml`
     - Priority: MEDIUM | Effort: 0.25h

---

## Validation Results

### Classification Completeness
✅ **All 209 workflows classified** (100% coverage)

### Distribution Verification

⚠️ Category A: 61 workflows (target range 40-50)
✅ Category B: 86 workflows (within range 80-100)
✅ Category C: 62 workflows (within range 60-70)

### Phase 1 Audit Alignment
✅ All classifications validated against PHASE_1_WORKFLOWS_AUDIT.json  
✅ Compliance status incorporated in classification logic  
✅ Operation types (critical/elevated/standard) mapped correctly  

---

## Phase 3.2 Implementation Roadmap

### Sprint 1: Category A - Critical Path (Week 1)
**Objective:** Implement CODEX_MASTER_KEY for Category A workflows

**Actions:**
1. **PR Edit Workflows** (15 workflows)
   - Update workflows with PR modify operations
   - Implement CODEX_MASTER_KEY fallback pattern
   - Test PR comment, approve, and edit operations

2. **Variable Write Workflows** (12 workflows)
   - Implement repository variable write capability
   - Add environment variable substitution
   - Validate variable persistence

3. **Security Event Workflows** (34 workflows)
   - Implement critical operation handling
   - Add security alert processing
   - Deploy session management

**Estimated Effort:** 152.5 hours

### Sprint 2: Category B - Mixed Operations (Week 2-3)
**Objective:** Implement conditional token upgrade strategy

**Actions:**
1. **Analyze Each Workflow** (86 workflows)
   - Determine which operations truly require elevation
   - Create selective token upgrade decision tree
   - Document operation-to-token mapping

2. **Implement Conditional Logic**
   - Create helper scripts for token detection
   - Implement `if: elevated_op_needed()` conditions
   - Add token switching mechanism

3. **Test Mixed Scenarios**
   - Test standard operations with standard token
   - Test elevated operations with CODEX_MASTER_KEY
   - Validate fallback behavior

**Estimated Effort:** 172.0 hours

### Sprint 3: Category C - Maintenance (Week 4)
**Objective:** Ensure Category C workflows remain secure and efficient

**Actions:**
1. **Monitor Scope Creep** (62 workflows)
   - Track any new elevated operations
   - Alert on token requirement changes
   - Maintain lowest-privilege principle

2. **Performance Optimization**
   - Remove unnecessary token contexts
   - Optimize read-only operation patterns
   - Reduce token generation overhead

**Estimated Effort:** 31.0 hours

### Post-Implementation: Phase 3.3 Optimization
**Objective:** Continuous improvement and monitoring

**Actions:**
- Implement workflow monitoring for token usage
- Create automated alerts for permission violations
- Build remediation automation
- Establish quarterly audit cadence

---

## Risk Assessment

### Category A Risk Analysis

**High Risk Workflows:**
- **admin-auth-delegation.yml** - Session management with critical operations
- **adaptive-agent-delegation.yml** - Complex approval workflow
- **agent-auth-delegation.yml** - Multiple elevated operations

**Mitigation Strategies:**
1. Implement rate limiting on elevated operations
2. Add audit logging for all CODEX_MASTER_KEY usage
3. Create approval gates for critical workflows
4. Enable GitHub Advanced Security for PR modification operations

### Category B Risk Analysis

**Mixed Risk Workflows:**
- Require careful token management
- Need conditional logic validation
- Risk of accidental scope creep

**Mitigation Strategies:**
1. Implement selective token upgrade with clear conditions
2. Add warnings when switching to elevated tokens
3. Create dashboards to track token usage patterns
4. Enforce regular token rotation

### Category C Safety Assurance

**Lowest Risk Operations:**
- Read-only workflows are inherently safe
- No token upgrade needed
- Compliance with least-privilege principle maintained

**Verification:**
- Quarterly audits to ensure no scope creep
- Automated testing for token-less operations
- Documentation of intended read-only design

---

## Metrics and KPIs

### Classification Quality Metrics
- **Coverage:** 209/209 workflows (100%)
- **Classification Consistency:** Validated against Phase 1 audit
- **Target Range Hit Rate:** 2/3 categories in range

### Phase 3.2 Success Metrics
- All Category A workflows successfully implement CODEX_MASTER_KEY
- Category B workflows reduce CODEX_MASTER_KEY usage by 40%
- Category C workflows maintain 0% token requirement

### Security Metrics
- Token rotation frequency: Every 90 days
- Audit log completeness: 100% of elevated operations
- Incident response time: <1 hour for token compromise

---

## References

- **Phase 1 Source:** `.codex/PHASE_1_WORKFLOWS_AUDIT.json`
- **Classification JSON:** `.codex/PHASE_3_WORKFLOW_CLASSIFICATION.json`
- **GitHub Actions Documentation:** https://docs.github.com/actions
- **Token Management Guide:** `.github/docs/TOKEN_MANAGEMENT.md`

---

## Appendix: Technical Implementation Details

### Classification Algorithm

The workflows were classified using a multi-factor analysis:

1. **Primary Factor:** Operation Type
   - `critical` → Category A (highest burden)
   - `elevated` → Category B or A (depends on secondary factors)
   - `standard` → Category C (lowest burden)

2. **Secondary Factors:**
   - Compliance status
   - Operations detected (elevated, standard, critical)
   - Token environment variables
   - Risk level assessment

3. **Effort Calculation:**
   - Category A: 3.0 hours/workflow (complex implementation)
   - Category B: 2.0 hours/workflow (mixed logic)
   - Category C: 0.5 hours/workflow (monitoring only)

### Validation Criteria

✅ All 209 workflows from Phase 1 audit included  
✅ No duplicates detected  
✅ All classifications have priority assigned  
✅ All workflows have effort estimate  
✅ Compliance status validated  

---

**Document Status:** FINAL  
**Last Updated:** {datetime.now(timezone.utc).isoformat()}  
**Review Status:** PENDING  
**Approval Status:** NOT YET APPROVED  

