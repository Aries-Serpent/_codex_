# 🔄 WEC Pruning Audit Report — Lane 1 · 2026-07-18

**Audit Date**: 2026-07-18T17:21:13.419280
**PR Number**: #5336
**Repository**: Aries-Serpent/_codex_
**Branch**: copilot/custom-image-setup

---

## 📊 Executive Summary

| Metric | Count |
|--------|-------|
| Initial workflow count | 219 |
| Archived workflows | 0 |
| Active workflows | 219 |
| WEC Approved (keep) | 7 |
| WEC Unapproved (prune) | 32 |
| Uncategorized | 180 |
| Reduction ratio | 82.1% |

---

## 🔍 WEC Checkbox Mapping

### ✅ Checked Items (8 Workflows - Must Keep)

| Category | Workflow | Status |
|----------|----------|--------|
| Always Required | pre-merge-validation.yml | ✅ Keep |
| Always Required | comment-review-gate.yml | ✅ Keep |
| Always Required | deferral-language-gate.yml | ✅ Keep |
| Always Required | agent-auth-delegation.yml | ✅ Keep |
| Always Required | workflow-execution-gate.yml | ✅ Keep |
| Always Active | copilot-agent-checkin.yml | ✅ Keep |
| Always Active | cost-gate.yml | ✅ Keep |
| Auto-Approve | auto-approve-workflows.yml | ✅ Keep |

---

## 📋 Workflow Status Breakdown

### ✅ Kept Workflows (7)

- ✅ agent-auth-delegation.yml
- ✅ auto-approve-workflows.yml
- ✅ comment-review-gate.yml
- ✅ cost-gate.yml
- ✅ deferral-language-gate.yml
- ✅ pre-merge-validation.yml
- ✅ workflow-execution-gate.yml

### ❌ Unapproved Workflows to Prune (32)

 1. ❌ actionlint-audit.yml
 2. ❌ agent-registry-validation.yml
 3. ❌ audit-qa-suite.yml
 4. ❌ auth-tests.yml
 5. ❌ auto-fix-common-issues.yml
 6. ❌ auto-fix-pr-check.yml
 7. ❌ ci-checkpoint-validation.yml
 8. ❌ code-quality-coverage-suite.yml
 9. ❌ coverage-with-timeout.yml
10. ❌ d-capable-promotion-gate.yml
11. ❌ data-quality-suite.yml
12. ❌ dependency-submission.yml
13. ❌ docker-build-push.yml
14. ❌ e-to-d-transition-gate.yml
15. ❌ html_visual_regression.yml
16. ❌ mcp-health.yml
17. ❌ mypy-baseline.yml
18. ❌ nox_gates.yml
19. ❌ pages-pre-merge-validation.yml
20. ❌ pr-checks.yml
21. ❌ pre-flight-validation.yml
22. ❌ progressive-validation.yml
23. ❌ qa-walkthrough.yml
24. ❌ reference-integrity.yml
25. ❌ resilient_validation.yml
26. ❌ root-org-validation.yml
27. ❌ rust_swarm_ci.yml
28. ❌ security-scanning-suite.yml
29. ❌ semgrep_sarif.yml
30. ❌ template_lint.yml
31. ❌ test-rag.yml
32. ❌ validate.yml

### ❓ Uncategorized Workflows (180)

These workflows are not explicitly listed in the WEC checklist.
They should be reviewed and either added to WEC or archived.

- ❓ action-version-check.yml
- ❓ adaptive-agent-delegation.yml
- ❓ admin-action-notifier.yml
- ❓ admin-action-t03.yml
- ❓ admin_setup_verification.yml
- ❓ agent-handoff-gate.yml
- ❓ agent-health-check.yml
- ❓ agent-orchestration-unified.yml
- ❓ agent-task-janitor.yml
- ❓ agent-var-writer.yml
- ❓ agent_infrastructure_manager.yml
- ❓ agentic-diff-guard.yml
- ❓ api-documentation.yml
- ❓ app-package-download.yml
- ❓ artifact-monitoring.yml
- ❓ automated-compliance-check.yml
- ❓ automated-monitoring-setup.yml
- ❓ automated-post-deployment-verification.yml
- ❓ automated-release-creation.yml
- ❓ automated-rollback-generation.yml
- ❓ autonomous-agent.yml
- ❓ autonomy-phase-ci-matrix.yml
- ❓ batch-ci-triage.yml
- ❓ benchmarks.yml
- ❓ branch-cleanup.yml
- ❓ branch-divergence-monitor.yml
- ❓ branch-rebase-gate.yml
- ❓ build-agent-env-cache.yml
- ❓ build-preview-image.yml
- ❓ cache-health-monitor.yml
- ❓ cache-pruning.yml
- ❓ cache-validation.yml
- ❓ capacity-planner-monitor.yml
- ❓ chatops_copilot_trigger.yml
- ❓ ci-failure-issue-creator.yml
- ❓ ci-pass-rate-gate.yml
- ❓ ci-pattern-healer.yml
- ❓ ci-pattern-prevention-gate.yml
- ❓ ci-rescue.yml
- ❓ cleanup-stale-branches.yml
- ❓ cleanup-stale-pr-comments.yml
- ❓ codebase-health-sweep.yml
- ❓ codex-manifest-refresh.yml
- ❓ codex-master-key-validation.yml
- ❓ cognitive-action-decision.yml
- ❓ cognitive-analysis-feed.yml
- ❓ cognitive-k8s-provisioning.yml
- ❓ cognitive-perception.yml
- ❓ cognitive-registry-validation.yml
- ❓ cognitive_brain_ci_feedback.yml
- ❓ coherence-snapshot.yml
- ❓ consistency-checks.yml
- ❓ consolidated-pr-status.yml
- ❓ container-scan.yml
- ❓ copilot-agent-vars-bootstrap.yml
- ❓ copilot-evolution-suite.yml
- ❓ copilot-setup-steps.yml
- ❓ copilot-setup-validation.yml
- ❓ correlation-engine-monitor.yml
- ❓ coverage-ratchet.yml
- ❓ create-sub-pr-to-0D_base_.yml
- ❓ cve-scanning.yml
- ❓ dependabot-auto-absorb.yml
- ❓ dependabot-preflight.yml
- ❓ dependabot-sheriff.yml
- ❓ dependency-scan.yml
- ❓ detect-duplicates.yml
- ❓ discussion-cleanup.yml
- ❓ discussion-response-bridge.yml
- ❓ embedding-index-rebuild.yml
- ❓ ensemble-predictor-monitor.yml
- ❓ enterprise-compliance.yml
- ❓ fast-forward-safe-files.yml
- ❓ flush-queued-runs.yml
- ❓ forward-sync-autogen.yml
- ❓ ghost-object-actioner.yml
- ❓ github-guru.yml
- ❓ har-capture.yml
- ❓ import-linter.yml
- ❓ issue-resolution-gate.yml
- ❓ iterative-self-healing-ci.yml
- ❓ labeler.yml
- ❓ machine-readable-governance.yml
- ❓ machine-readable-maintenance-pr.yml
- ❓ manifest-drift-guard.yml
- ❓ maturity-check.yml
- ❓ ml-lifecycle-gate.yml
- ❓ ml-tests.yml
- ❓ model-drift-retrain.yml
- ❓ mutation-testing.yml
- ❓ nightly-codeql-alert-triage.yml
- ❓ observable-release.yml
- ❓ openvino-phase-c.yml
- ❓ optimized-ci.yml
- ❓ optimized-test-execution.yml
- ❓ pages-health-guard.yml
- ❓ pages-mkdocs.yml
- ❓ pages-scheduled-validation.yml
- ❓ parallel-quality-checks.yml
- ❓ performance-gate.yml
- ❓ performance-monitoring.yml
- ❓ phase-12-2-compliance-check.yml
- ❓ phase-12-hourly-monitoring.yml
- ❓ pr-cost-check.yml
- ❓ pr-followup-generator.yml
- ❓ pr-size-analyzer.yml
- ❓ pre-release-validation.yml
- ❓ premerge-triage-gate.yml
- ❓ proactive-ci-monitor.yml
- ❓ process-variable-intents.yml
- ❓ profile-validation.yml
- ❓ promote-integration-branch.yml
- ❓ promotion-readiness-gate.yml
- ❓ publish_dashboard_release.yml
- ❓ pypi-publish.yml
- ❓ rag-freshness-scheduler.yml
- ❓ rag-quality-nightly.yml
- ❓ ratelimit_history_prune.yml
- ❓ reasoning-engine-monitor.yml
- ❓ release-to-pypi.yml
- ❓ release.yml
- ❓ repo-organization.yml
- ❓ repo-var-sync-schedule.yml
- ❓ required-actions-enforcer.yml
- ❓ restore-pipeline-ci.yml
- ❓ runner-diagnostics.yml
- ❓ rust-error-validator-observation.yml
- ❓ rust-ffi.yml
- ❓ sbom.yml
- ❓ scaling-framework-monitor.yml
- ❓ scan-secrets-variables.yml
- ❓ scheduled-archival.yml
- ❓ scheduled-dependency-audit.yml
- ❓ secrets-baseline-enforcer.yml
- ❓ secrets-detection.yml
- ❓ secrets-false-positive-healer.yml
- ❓ security-alert-notification.yml
- ❓ security-copilot-commands.yml
- ❓ security-findings-api.yml
- ❓ security-findings-copilot-handoff.yml
- ❓ security-pr-enhancement.yml
- ❓ security-scan-phase-16.yml
- ❓ security-tools-bootstrap.yml
- ❓ self-approve-pending-runs.yml
- ❓ self-healing.yml
- ❓ sigstore-verify.yml
- ❓ sla-optimizer-monitor.yml
- ❓ slo-canary-check.yml
- ❓ smoke-tests-deployment.yml
- ❓ status_gate.yml
- ❓ sync-env-vars.yml
- ❓ telemetry-collection.yml
- ❓ test-pyramid-report.yml
- ❓ test-variables-api.yml
- ❓ tiered-approval-gate.yml
- ❓ token-expiry-monitor.yml
- ❓ token-probe.yml
- ❓ trigger-on-approval.yml
- ❓ unified-cognitive-brain-suite.yml
- ❓ unified-copilot-management.yml
- ❓ unified-deployment.yml
- ❓ unified-documentation.yml
- ❓ unified-governance-check.yml
- ❓ unified-health-monitoring.yml
- ❓ unified-monitoring-suite.yml
- ❓ unified-phase-gates.yml
- ❓ unified-post-merge-management.yml
- ❓ unified-security-ops-suite.yml
- ❓ unified-security-scanning.yml
- ❓ unified-session-management.yml
- ❓ validate-api-null-handling.yml
- ❓ validate-code-examples.yml
- ❓ validate-token-health.yml
- ❓ vars-guide-sync.yml
- ❓ wec-enforcement-gate.yml
- ❓ workflow-analytics-unified.yml
- ❓ workflow-compliance-gate.yml
- ❓ workflow-expiry-enforcer.yml
- ❓ workflow-link-validation.yml
- ❓ workflow-restore.yml

### 📦 Archived Workflows (0)

*None*

---

## 📊 Pruning Statistics

**Initial state:**
- Total workflows: 219
- Archived: 0
- Active: 219

**After WEC pruning:**
- Workflows to keep: 7
- Workflows to disable: 32
- Final active count: 7
- **Reduction: 32 workflows (82.1%)**

---

## ✅ Approval Queue Status

### PR #5336 Required Checks (WEC-Approved)

All 5 required status checks are WEC-approved:
1. ✅ pre-merge-validation.yml
2. ✅ comment-review-gate.yml
3. ✅ deferral-language-gate.yml
4. ✅ agent-auth-delegation.yml
5. ✅ workflow-execution-gate.yml

### Auto-Fire Workflows (WEC-Approved)

- ✅ copilot-agent-checkin.yml (fires on push)
- ✅ cost-gate.yml (called by agent-auth-delegation)
- ✅ auto-approve-workflows (auto-approves pending runs)

### Pending Workflows Awaiting Approval

**Count**: 32 workflows unapproved

These workflows are currently queued/pending in the GitHub Actions tab
and require explicit WEC approval to run:

 1. actionlint-audit.yml
 2. agent-registry-validation.yml
 3. audit-qa-suite.yml
 4. auth-tests.yml
 5. auto-fix-common-issues.yml
 6. auto-fix-pr-check.yml
 7. ci-checkpoint-validation.yml
 8. code-quality-coverage-suite.yml
 9. coverage-with-timeout.yml
10. d-capable-promotion-gate.yml
11. data-quality-suite.yml
12. dependency-submission.yml
13. docker-build-push.yml
14. e-to-d-transition-gate.yml
15. html_visual_regression.yml
16. mcp-health.yml
17. mypy-baseline.yml
18. nox_gates.yml
19. pages-pre-merge-validation.yml
20. pr-checks.yml
21. pre-flight-validation.yml
22. progressive-validation.yml
23. qa-walkthrough.yml
24. reference-integrity.yml
25. resilient_validation.yml
26. root-org-validation.yml
27. rust_swarm_ci.yml
28. security-scanning-suite.yml
29. semgrep_sarif.yml
30. template_lint.yml
31. test-rag.yml
32. validate.yml

---

## 🚀 Pruning Action Plan

**Status**: 🟢 Ready to Execute

### Step 1: Disable Unapproved Workflows

Disable all unapproved workflows in GitHub Actions:

- [ ] Disable: actionlint-audit.yml
- [ ] Disable: agent-registry-validation.yml
- [ ] Disable: audit-qa-suite.yml
- [ ] Disable: auth-tests.yml
- [ ] Disable: auto-fix-common-issues.yml
- [ ] Disable: auto-fix-pr-check.yml
- [ ] Disable: ci-checkpoint-validation.yml
- [ ] Disable: code-quality-coverage-suite.yml
- [ ] Disable: coverage-with-timeout.yml
- [ ] Disable: d-capable-promotion-gate.yml
- [ ] Disable: data-quality-suite.yml
- [ ] Disable: dependency-submission.yml
- [ ] Disable: docker-build-push.yml
- [ ] Disable: e-to-d-transition-gate.yml
- [ ] Disable: html_visual_regression.yml
- [ ] Disable: mcp-health.yml
- [ ] Disable: mypy-baseline.yml
- [ ] Disable: nox_gates.yml
- [ ] Disable: pages-pre-merge-validation.yml
- [ ] Disable: pr-checks.yml
- [ ] Disable: pre-flight-validation.yml
- [ ] Disable: progressive-validation.yml
- [ ] Disable: qa-walkthrough.yml
- [ ] Disable: reference-integrity.yml
- [ ] Disable: resilient_validation.yml
- [ ] Disable: root-org-validation.yml
- [ ] Disable: rust_swarm_ci.yml
- [ ] Disable: security-scanning-suite.yml
- [ ] Disable: semgrep_sarif.yml
- [ ] Disable: template_lint.yml
- [ ] Disable: test-rag.yml
- [ ] Disable: validate.yml

### Step 2: Archive if Needed

- [ ] Review 180 uncategorized workflows
- [ ] Archive obsolete workflows

### Step 3: Verify PR Gates

- [x] All 5 required checks are WEC-approved
- [x] workflow-execution-gate.yml is active
- [x] WEC enforcement is enabled

---

**Report Generated**: 2026-07-18T17:21:13.419371
**Agent**: workflow-compliance-guardian v2.0.0