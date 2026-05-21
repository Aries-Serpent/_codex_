# Workflow Portfolio 7-Day Table

Source: `docs/reporting/workflow_portfolio_7d_table.csv`

> Exhaustive inventory lives in the CSV. This markdown view highlights the fields most useful
> for Copilot session triage: active state, recent usage, recommendation bucket, smoke posture,
> and branch-drift conflict risk.

| workflow_name | file_path | state | active_last_7_days | runs_7d | last_run_at_utc | recommended_portfolio_action | copilot_smoke_posture | branch_update_conflict_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Workflow Compliance Audit (actionlint) | .github/workflows/actionlint-audit.yml | active | False | 0 |  | keep-enabled-historical-use | unobserved-7d | low |
| Admin Action Notifier (Reusable) | .github/workflows/admin-action-notifier.yml | active | False | 0 |  | keep-enabled-orchestration | unobserved-7d | low |
| Admin Action — T-03 security_events Scope Gate | .github/workflows/admin-action-t03.yml | active | True | 47 | 2026-05-15T18:21:52Z | keep-enabled-active | approval-gated-or-mixed | low |
| Admin Setup Verification | .github/workflows/admin_setup_verification.yml | active | False | 0 |  | keep-enabled-historical-use | unobserved-7d | low |
| Agent Token Delegation | .github/workflows/agent-auth-delegation.yml | active | True | 5 | 2026-05-15T04:44:07Z | keep-enabled-wec-critical | observed-failures | medium |
| Agent Handoff Gate | .github/workflows/agent-handoff-gate.yml | active | True | 5 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-green | low |
| Agent Orchestration (Unified) | .github/workflows/agent-orchestration-unified.yml | active | False | 0 |  | keep-enabled-orchestration | unobserved-7d | medium |
| Agent Registry Validation | .github/workflows/agent-registry-validation.yml | active | False | 0 |  | keep-enabled-historical-use | unobserved-7d | low |
| Agent Variable Writer (Provenance-Chain) | .github/workflows/agent-var-writer.yml | active | True | 5 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-green | high |
| Agent Infrastructure Manager | .github/workflows/agent_infrastructure_manager.yml | active | True | 5 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-green | medium |
| API Documentation | .github/workflows/api-documentation.yml | active | False | 0 |  | keep-enabled-historical-use | unobserved-7d | low |
| App Package Download | .github/workflows/app-package-download.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Archival Compliance | .github/workflows/archival_compliance.yml | disabled_manually | False | 0 |  | already-disabled | disabled | unknown |
| Artifact Monitoring | .github/workflows/artifact-monitoring.yml | active | True | 6 | 2026-05-15T15:47:31Z | keep-enabled-active | observed-green | low |
| AST Analysis | .github/workflows/ast-analysis.yml | disabled_manually | False | 0 |  | already-disabled | disabled | unknown |
| Audit & QA Suite (Unified) | .github/workflows/audit-qa-suite.yml | active | True | 6 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-green | medium |
| Authentication Tests | .github/workflows/auth-tests.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| ⚡ Auto-Approve Pending Workflow Runs | .github/workflows/auto-approve-workflows.yml | active | True | 48 | 2026-05-15T18:21:38Z | keep-enabled-active | approval-gated-or-mixed | low |
| Auto-Fix Common CI Issues | .github/workflows/auto-fix-common-issues.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | high |
| PR Auto-Fix Check | .github/workflows/auto-fix-pr-check.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | high |
| Autonomous Codebase Management | .github/workflows/autonomous-agent.yml | active | True | 4 | 2026-05-15T18:33:56Z | keep-enabled-active | observed-green | low |
| Autonomy Phase CI Matrix | .github/workflows/autonomy-phase-ci-matrix.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Batch CI Failure Triage | .github/workflows/batch-ci-triage.yml | active | True | 18 | 2026-05-15T18:30:38Z | keep-enabled-active | observed-green | low |
| Performance Benchmarks | .github/workflows/benchmarks.yml | disabled_stub | False | 0 |  | already-disabled | disabled | unknown |
| 🌿 Branch Cleanup | .github/workflows/branch-cleanup.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| 🔀 Branch Divergence Monitor — 0D_base_ ↔ main | .github/workflows/branch-divergence-monitor.yml | active | True | 3 | 2026-05-15T12:43:13Z | keep-enabled-active | observed-green | low |
| 🔀 Branch Rebase Gate | .github/workflows/branch-rebase-gate.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | high |
| Build Agent Environment Cache | .github/workflows/build-agent-env-cache.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| Build & Push Preview Image | .github/workflows/build-preview-image.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Cache Health Monitor | .github/workflows/cache-health-monitor.yml | disabled_stub | False | 0 |  | already-disabled | disabled | unknown |
| Cache Pruning | .github/workflows/cache-pruning.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| Cache Validation | .github/workflows/cache-validation.yml | disabled_stub | False | 0 |  | already-disabled | disabled | unknown |
| Chat-Ops — @copilot Webhook Trigger | .github/workflows/chatops_copilot_trigger.yml | active | True | 5 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-green | medium |
| CI Checkpoint Validation | .github/workflows/ci-checkpoint-validation.yml | active | True | 2 | 2026-05-15T07:08:39Z | keep-enabled-active | observed-green | low |
| 🚨 CI Failure Issue Creator | .github/workflows/ci-failure-issue-creator.yml | active | True | 4 | 2026-05-15T12:50:54Z | keep-enabled-active | observed-failures | medium |
| CI Health Monitor | .github/workflows/ci-health-monitor.yml | active | True | 3 | 2026-05-15T12:48:43Z | keep-enabled-active | observed-green | medium |
| CI Rescue — Auto-Fix & @copilot RCA | .github/workflows/ci-rescue.yml | disabled_manually | True | 55 | 2026-05-15T02:16:56Z | already-disabled | disabled | medium |
| Cleanup Stale Self-Heal Branches | .github/workflows/cleanup-stale-branches.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| 🧹 Cleanup Stale PR Comments | .github/workflows/cleanup-stale-pr-comments.yml | active | True | 12 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-failures | medium |
| Code Quality & Coverage Suite | .github/workflows/code-quality-coverage-suite.yml | active | True | 2 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| 🧹 Codebase Health Sweep | .github/workflows/codebase-health-sweep.yml | active | True | 7 | 2026-05-15T07:27:38Z | keep-enabled-active | observed-green | medium |
| 🔍 CodeQL Alert Fetcher | .github/workflows/codeql-alert-fetcher.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| CodeQL | .github/workflows/codeql-analysis.yml | active | True | 5 | 2026-05-15T16:55:44Z | keep-enabled-wec-critical | approval-gated-or-mixed | low |
| CodeQL Advanced | .github/workflows/codeql.yml | active | True | 2 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| CODEX Manifest Auto-Refresh | .github/workflows/codex-manifest-refresh.yml | active | True | 4 | 2026-05-15T18:33:50Z | keep-enabled-active | observed-green | medium |
| Cognitive Action & Decision (Unified) | .github/workflows/cognitive-action-decision.yml | active | True | 3 | 2026-05-15T12:56:01Z | keep-enabled-active | observed-green | medium |
| Cognitive Analysis & Learning (Unified) | .github/workflows/cognitive-analysis-feed.yml | active | True | 4 | 2026-05-15T12:57:22Z | keep-enabled-active | observed-green | medium |
| Cognitive Perception Layer | .github/workflows/cognitive-perception.yml | active | True | 4 | 2026-05-15T18:35:59Z | keep-enabled-active | observed-green | low |
| Cognitive Brain CI Feedback | .github/workflows/cognitive_brain_ci_feedback.yml | disabled_manually | False | 0 |  | already-disabled | disabled | medium |
| 📈 OTel Coherence Snapshot | .github/workflows/coherence-snapshot.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| PR Comment Review Gate | .github/workflows/comment-review-gate.yml | active | True | 6 | 2026-05-15T16:03:08Z | keep-enabled-wec-critical | observed-failures | low |
| Consolidated PR Status | .github/workflows/consolidated-pr-status.yml | active | False | 0 |  | keep-enabled-orchestration | unobserved-7d | low |
| 🤖 Agent Check-In — Q&A Bridge (Discussion #3756) | .github/workflows/copilot-agent-checkin.yml | active | True | 5 | 2026-05-15T16:03:08Z | keep-enabled-wec-critical | observed-green | medium |
| 🔄 Auto-Post @copilot review After Agent Session | .github/workflows/copilot-agent-session-done.yml | active | True | 10 | 2026-05-15T07:27:34Z | keep-enabled-active | approval-gated-or-mixed | high |
| Agent Vars Bootstrap | .github/workflows/copilot-agent-vars-bootstrap.yml | active | True | 5 | 2026-05-15T16:55:44Z | keep-enabled-active | approval-gated-or-mixed | medium |
| Copilot Automation Suite | .github/workflows/copilot-automation.yml | disabled_stub | False | 0 |  | already-disabled | disabled | unknown |
| Copilot Evolution & Review (Unified) | .github/workflows/copilot-evolution-suite.yml | active | True | 10 | 2026-05-15T16:41:46Z | keep-enabled-active | observed-green | high |
| Copilot Issue Triage | .github/workflows/copilot-issue-triage.yml | active | True | 1 | 2026-05-15T03:30:38Z | keep-enabled-active | observed-failures | low |
| Copilot Iterative Self-Healing Auto-Poster | .github/workflows/copilot-iterative-self-healing.yml | disabled_manually | True | 55 | 2026-05-15T02:16:56Z | already-disabled | disabled | medium |
| Copilot PR Session Injector | .github/workflows/copilot-pr-session-injector.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | medium |
| 🤖 Copilot Review Responder | .github/workflows/copilot-review-responder.yml | active | True | 5 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-green | medium |
| 🔗 Copilot Session Chain | .github/workflows/copilot-session-chain.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | high |
| Copilot Agent Environment Setup | .github/workflows/copilot-setup-steps.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | medium |
| 💰 Cost Gate | .github/workflows/cost-gate.yml | active | False | 0 |  | keep-enabled-wec-critical | unobserved-7d | low |
| Coverage with Timeout Guards | .github/workflows/coverage-with-timeout.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| 🔀 Create Sub-PR: Session Branch → 0D_base_ | .github/workflows/create-sub-pr-to-0D_base_.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| D_CAPABLE Agent Promotion Gate | .github/workflows/d-capable-promotion-gate.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | medium |
| Data Quality & Determinism Suite | .github/workflows/data-quality-suite.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| 🚨 Deferral Language Gate | .github/workflows/deferral-language-gate.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-wec-critical | observed-green | low |
| 📦 Dependabot Auto-Absorb | .github/workflows/dependabot-auto-absorb.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | medium |
| DependaBot Sheriff (Automated Consolidation) | .github/workflows/dependabot-sheriff.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Dependency Scan (template) | .github/workflows/dependency-scan.yml | active | True | 1 | 2026-05-15T04:22:49Z | keep-enabled-active | observed-green | low |
| Resilient Dependency Submission | .github/workflows/dependency-submission.yml | active | True | 5 | 2026-05-15T16:55:44Z | keep-enabled-active | approval-gated-or-mixed | low |
| Duplicate Detection on PR | .github/workflows/detect-duplicates.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| 🧹 Discussion Cleanup — Deduplicate Comments | .github/workflows/discussion-cleanup.yml | active | True | 1 | 2026-05-15T07:21:17Z | keep-enabled-active | observed-green | low |
| 🌉 Discussion → PR Response Bridge (RC-3) | .github/workflows/discussion-response-bridge.yml | active | True | 4 | 2026-05-15T04:49:39Z | keep-enabled-active | observed-green | low |
| 📚 Documentation Freshness Check | .github/workflows/doc-freshness-check.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| 🔄 Doc Refresh Gate (AAIS) | .github/workflows/doc-refresh-gate.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| CI - Build, Smoke Test, and Push Docker (GHCR) — OWNER APPROVED (NO-MARKETPLACE) | .github/workflows/docker-build-push.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Docs Health (Post-Merge) | .github/workflows/docs-health.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | medium |
| Documentation Link Checker | .github/workflows/documentation-link-checker.yml | active | True | 4 | 2026-05-15T16:55:44Z | keep-enabled-active | approval-gated-or-mixed | low |
| Documentation Quality Check | .github/workflows/documentation-quality-check.yml | disabled_stub | False | 0 |  | already-disabled | disabled | unknown |
| E→D Transition Readiness Gate | .github/workflows/e-to-d-transition-gate.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | medium |
| Embedding Index Rebuild | .github/workflows/embedding-index-rebuild.yml | active | True | 5 | 2026-05-15T18:33:07Z | keep-enabled-active | observed-green | low |
| ⚡ Fast-Forward Safe Files to Main | .github/workflows/fast-forward-safe-files.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| 🚿 Flush Queued Workflow Runs | .github/workflows/flush-queued-runs.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Forward-Sync Auto-Generated Files → staging chain (Safety Net) | .github/workflows/forward-sync-autogen.yml | active | True | 1 | 2026-05-15T03:07:13Z | keep-enabled-active | observed-green | high |
| GitHub Guru Agent | .github/workflows/github-guru.yml | active | True | 6 | 2026-05-15T07:19:58Z | keep-enabled-active | observed-green | low |
| HAR Cache Capture | .github/workflows/har-capture.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | medium |
| HTML Visual (Screenshots) | .github/workflows/html_visual_regression.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| IMDS Pre-Flight Check | .github/workflows/imds_preflight.yml | disabled_manually | False | 0 |  | already-disabled | disabled | unknown |
| 🔍 Issue Resolution Gate | .github/workflows/issue-resolution-gate.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| Iterative Self-Healing CI | .github/workflows/iterative-self-healing-ci.yml | active | True | 413 | 2026-05-15T18:36:26Z | keep-enabled-active | approval-gated-or-mixed | high |
| PR Labeler | .github/workflows/labeler.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Maturity Check | .github/workflows/maturity-check.yml | disabled_stub | False | 0 |  | already-disabled | disabled | unknown |
| MCP Health & Metrics Gate | .github/workflows/mcp-health.yml | active | True | 1 | 2026-05-15T05:22:19Z | keep-enabled-active | observed-green | low |
| Model Drift Detection & Auto-Retrain | .github/workflows/model-drift-retrain.yml | active | True | 1 | 2026-05-15T03:12:04Z | keep-enabled-active | observed-green | low |
| mypy Baseline (Type-Check Anti-Regression) | .github/workflows/mypy-baseline.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Nightly CodeQL Alert Triage | .github/workflows/nightly-codeql-alert-triage.yml | active | True | 1 | 2026-05-15T03:20:12Z | keep-enabled-active | observed-green | low |
| Nox Quality Gates | .github/workflows/nox_gates.yml | disabled_manually | False | 0 |  | keep-enabled-wec-critical | disabled | low |
| 🧹 One-Shot: Cleanup Stale Self-Heal Branches | .github/workflows/one-shot-cleanup.yml | disabled_manually | False | 0 |  | already-disabled | disabled | unknown |
| OpenVINO Phase C — Intel Arc iGPU Smoke Tests | .github/workflows/openvino-phase-c.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| CI — Optimized with Caching | .github/workflows/optimized-ci.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| 🩺 Pages Health Guard (Self-Healing) | .github/workflows/pages-health-guard.yml | active | True | 36 | 2026-05-15T18:34:47Z | keep-enabled-active | observed-green | low |
| Deploy Pages (MkDocs) | .github/workflows/pages-mkdocs.yml | active | True | 15 | 2026-05-15T18:36:22Z | keep-enabled-active | observed-failures | low |
| Pages Pre-Merge Validation | .github/workflows/pages-pre-merge-validation.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | medium |
| Pages Scheduled Validation | .github/workflows/pages-scheduled-validation.yml | active | True | 1 | 2026-05-15T00:34:53Z | keep-enabled-active | observed-green | low |
| 📋 Post Accountability Report to Discussion | .github/workflows/post-accountability-to-discussion.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| 🧠 Post CI Status to Discussions | .github/workflows/post-ci-status-to-discussion.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Post-Merge Validation (Optimized) | .github/workflows/post-merge-validation-optimized.yml | disabled_manually | False | 0 |  | already-disabled | disabled | medium |
| PR Checks (Isolated Cache) | .github/workflows/pr-checks.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| 💰 PR Cost Check | .github/workflows/pr-cost-check.yml | active | True | 6 | 2026-05-15T04:44:06Z | keep-enabled-active | observed-green | low |
| Generate PR Follow-Up Prompt | .github/workflows/pr-followup-generator.yml | active | True | 6 | 2026-05-15T04:44:06Z | keep-enabled-active | observed-green | medium |
| PR Size Analyzer | .github/workflows/pr-size-analyzer.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| Pre-Flight CI Validation | .github/workflows/pre-flight-validation.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Pre-Merge Validation | .github/workflows/pre-merge-validation.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-wec-critical | observed-green | medium |
| 🔍 Proactive CI Monitor | .github/workflows/proactive-ci-monitor.yml | active | True | 19 | 2026-05-15T17:59:39Z | keep-enabled-active | observed-failures | low |
| Process Variable Intents | .github/workflows/process-variable-intents.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | medium |
| Progressive Validation Suite | .github/workflows/progressive-validation.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| 🚀 Promote Integration Branch (0D_base_ → main) | .github/workflows/promote-integration-branch.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Publish Status Dashboard Release | .github/workflows/publish_dashboard_release.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Publish Python Package to PyPI | .github/workflows/pypi-publish.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| QA Walkthrough Agent | .github/workflows/qa-walkthrough.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| RAG Freshness Scheduler | .github/workflows/rag-freshness-scheduler.yml | active | True | 4 | 2026-05-15T18:32:53Z | keep-enabled-active | observed-green | low |
| Rate-Limit History Prune | .github/workflows/ratelimit_history_prune.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| 🔗 Reference Integrity + Agent Size Gate | .github/workflows/reference-integrity.yml | active | True | 2 | 2026-05-15T04:04:54Z | keep-enabled-wec-critical | observed-green | medium |
| Repository Organization & Cleanup | .github/workflows/repo-organization.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Repo Var Sync (Scheduled) | .github/workflows/repo-var-sync-schedule.yml | active | True | 1 | 2026-05-15T07:21:07Z | keep-enabled-active | observed-green | low |
| Repository Health Monitoring | .github/workflows/repository-health-monitoring.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| 🔖 Required Actions Version Enforcer | .github/workflows/required-actions-enforcer.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | medium |
| Resilient Validation Suite | .github/workflows/resilient_validation.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-wec-critical | observed-green | low |
| restore-pipeline CI | .github/workflows/restore-pipeline-ci.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Root Organization Validation | .github/workflows/root-org-validation.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Runner diagnostics — self-hosted readiness | .github/workflows/runner-diagnostics.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| rust-error-validator Observation (D_CAPABLE) | .github/workflows/rust-error-validator-observation.yml | active | False | 0 |  | keep-enabled-scheduled | unobserved-7d | low |
| Rust-Python Hybrid Swarm CI/CD | .github/workflows/rust_swarm_ci.yml | active | True | 1 | 2026-05-15T03:07:13Z | keep-enabled-active | observed-green | low |
| Generate SBOM | .github/workflows/sbom.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Scan and Report GitHub Secrets and Variables | .github/workflows/scan-secrets-variables.yml | active | True | 2 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| Scheduled Archival | .github/workflows/scheduled-archival.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Scheduled Dependency Audit & SBOM | .github/workflows/scheduled-dependency-audit.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| 🔐 Secrets Baseline Enforcer | .github/workflows/secrets-baseline-enforcer.yml | active | True | 5 | 2026-05-15T16:55:44Z | keep-enabled-active | approval-gated-or-mixed | medium |
| Security Alert Notification | .github/workflows/security-alert-notification.yml | active | True | 1 | 2026-05-15T09:53:39Z | keep-enabled-active | observed-green | low |
| Security Scanning Suite | .github/workflows/security-scanning-suite.yml | active | True | 6 | 2026-05-15T16:55:44Z | keep-enabled-wec-critical | approval-gated-or-mixed | low |
| Security Scanning | .github/workflows/security-scanning.yml | disabled_manually | False | 0 |  | already-disabled | disabled | unknown |
| Bootstrap Security Tools from Variables | .github/workflows/security-tools-bootstrap.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| ⚡ Self-Approve Pending Workflow Runs | .github/workflows/self-approve-pending-runs.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Self-Healing CI | .github/workflow-archive/disabled/self-healing.yml | archived | False | 0 |  | already-disabled | disabled | low |
| Semgrep SAST (SARIF Upload) | .github/workflows/semgrep_sarif.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Session Incremental Summary Reminder | .github/workflows/session-incremental-summary-reminder.yml | active | True | 22 | 2026-05-15T17:58:18Z | keep-enabled-active | observed-green | low |
| Session Watchdog — Timebox & Continuity Enforcement | .github/workflows/session-watchdog.yml | active | True | 5 | 2026-05-15T16:03:08Z | keep-enabled-active | observed-green | medium |
| ShellCheck (IMDS Tooling) | .github/workflows/shellcheck.yml | disabled_manually | False | 0 |  | already-disabled | disabled | unknown |
| Status Gate (.statusrc) | .github/workflows/status_gate.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Sync Environment Variables | .github/workflows/sync-env-vars.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | medium |
| CI Telemetry Collection | .github/workflows/telemetry-collection.yml | active | True | 1 | 2026-05-15T02:58:48Z | keep-enabled-active | observed-green | low |
| Template Lint (HTML includes) | .github/workflows/template_lint.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Analytics Failure Simulator | .github/workflow-archive/disabled/test-analytics-failure-sim.yml | archived | False | 0 |  | already-disabled | disabled | low |
| RAG Module Tests | .github/workflows/test-rag.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Test Variables API | .github/workflows/test-variables-api.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Token Expiry Monitor | .github/workflows/token-expiry-monitor.yml | active | True | 1 | 2026-05-15T09:57:01Z | keep-enabled-active | observed-green | low |
| Token Probe — CODEX_MASTER_KEY & CODEX_BACKUP_KEY Validation | .github/workflows/token-probe.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Trigger validations on approval | .github/workflows/trigger-on-approval.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Unified Deployment Suite | .github/workflows/unified-deployment.yml | active | False | 0 |  | review-manually-high-impact | unobserved-7d | medium |
| Validation Pipeline | .github/workflows/validate.yml | active | True | 2 | 2026-05-15T04:24:04Z | keep-enabled-wec-critical | observed-failures | low |
| Auto-Sync Variables Master Guide | .github/workflows/vars-guide-sync.yml | active | True | 1 | 2026-05-15T06:58:13Z | keep-enabled-active | observed-green | high |
| Workflow Analytics & Health (Unified) | .github/workflows/workflow-analytics-unified.yml | disabled_manually | False | 0 |  | already-disabled | disabled | low |
| Workflow Execution Gate | .github/workflows/workflow-execution-gate.yml | active | True | 5 | 2026-05-15T04:44:06Z | keep-enabled-wec-critical | observed-green | medium |
| Workflow Expiry Enforcer — Auto-disable on expiry | .github/workflows/workflow-expiry-enforcer.yml | disabled_manually | False | 0 |  | already-disabled | disabled | medium |
| Workflow Documentation Link Validation | .github/workflows/workflow-link-validation.yml | active | True | 1 | 2026-05-15T04:04:54Z | keep-enabled-active | observed-green | low |
| Workflow Restore Tool | .github/workflows/workflow-restore.yml | active | False | 0 |  | archive-review-candidate | unobserved-7d | low |
| Claude | dynamic/agents/anthropic-code-agent | active | False | 0 |  | archive-review-candidate | unobserved-7d | unknown |
| OpenAI Codex | dynamic/agents/openai-code-agent | active | False | 0 |  | archive-review-candidate | unobserved-7d | unknown |
| Claude | dynamic/anthropic-code-agent/claude | active | False | 0 |  | archive-review-candidate | unobserved-7d | unknown |
| Codespaces Prebuilds | dynamic/codespaces/create_codespaces_prebuilds | active | False | 0 |  | archive-review-candidate | unobserved-7d | unknown |
| Copilot code review | dynamic/copilot-pull-request-reviewer/copilot-pull-request-reviewer | active | False | 0 |  | archive-review-candidate | unobserved-7d | unknown |
| Copilot cloud agent | dynamic/copilot-swe-agent/copilot | active | True | 6 | 2026-05-15T18:13:45Z | keep-enabled-active | observed-failures | unknown |
| Dependabot Updates | dynamic/dependabot/dependabot-updates | active | False | 0 |  | archive-review-candidate | unobserved-7d | unknown |
| Dependency Graph | dynamic/dependabot/update-graph | active | False | 0 |  | archive-review-candidate | unobserved-7d | unknown |
| Automatic Dependency Submission | dynamic/dependency-graph/auto-submission | active | True | 14 | 2026-05-15T18:34:09Z | keep-enabled-active | observed-green | unknown |
| CodeQL | dynamic/github-code-scanning/codeql | active | True | 14 | 2026-05-15T18:34:09Z | keep-enabled-active | observed-green | unknown |
| pages-build-deployment | dynamic/pages/pages-build-deployment | active | True | 8 | 2026-05-15T18:34:09Z | keep-enabled-active | observed-green | unknown |
