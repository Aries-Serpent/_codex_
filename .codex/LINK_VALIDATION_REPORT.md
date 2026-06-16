# 📋 Documentation Link Validation Audit Report

**Audit Date:** 2026-06-16T13:28:39Z
**Repository:** Aries-Serpent/_codex_
**Scope:** docs/ directory (all .md files)

---

## 📊 Executive Summary

| Metric | Count | Status |
|--------|-------|--------|
| **Files Scanned** | 1646 | ✅ |
| **Valid Internal Links** | 2718 | ✅ |
| **Broken Internal Links** | 64 | ⚠️ |
| **Broken Anchor References** | 108 | ⚠️ |
| **External Links Found** | 2699 | ℹ️ Manual Review |
| **Total Issues** | 172 | |

---

## ✅ Valid Internal Links Summary

**Total Valid Links:** 2718

Distribution by type:
- Anchor references (#section): 621
- Internal file links: 2097

---

## ⚠️ Broken Internal Links (Critical)

**Total Broken Links:** 64

### Detailed Broken Link List

| File | Link | Issue | Line |
|------|------|-------|------|
| `docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md` | `[^"\']+` | File not found: docs/[^"\']+ | 540 |
| `docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md` | `[^"\']+` | File not found: docs/[^"\']+ | 541 |
| `docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md` | `[^"\']+` | File not found: docs/[^"\']+ | 542 |
| `docs/GITHUB_PAGES_MANAGER_IMPLEMENTATION.md` | `../guides/user-guide.md` | File not found: guides/user-guide.md | 233 |
| `docs/GITHUB_SPARK_INTEGRATION_GUIDE.md` | `mailto:support@example.com` | File not found: docs/mailto:support@example.com | 1687 |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | `1` | File not found: docs/accountability/1 | 1453 |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | `?:\.[\d]+` | File not found: docs/accountability/?:\.[\d]+ | 15432 |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | `URL` | File not found: docs/accountability/URL | 29460 |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | `URL` | File not found: docs/accountability/URL | 29467 |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | `URL` | File not found: docs/accountability/URL | 30147 |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | `URL` | File not found: docs/accountability/URL | 30319 |
| `docs/admin/PYTHON_3.11_TO_3.12_MIGRATION_AUDIT.md` | `items: list[T]` | File not found: docs/admin/items: list[T] | 486 |
| `docs/ai-facing/Design_Specification_Quantum_Compression_Neural_Pathway_Integration.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/ai-facing/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 188 |
| `docs/ai-facing/Design_Specification_Quantum_Compression_Neural_Pathway_Integration.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/ai-facing/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 188 |
| `docs/ai-facing/Design_Specification_Quantum_Compression_Neural_Pathway_Integration.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/ai-facing/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 188 |
| `docs/analysis/LINK_VALIDATION_FIX_SUMMARY.md` | `[^"\']+` | File not found: docs/analysis/[^"\']+ | 78 |
| `docs/analysis/LINK_VALIDATION_FIX_SUMMARY.md` | `state["inputs"]` | File not found: docs/analysis/state["inputs"] | 83 |
| `docs/analysis/LINK_VALIDATION_FIX_SUMMARY.md` | `blob:https://chatgpt.com/...` | File not found: docs/analysis/blob:https:/chatgpt.com/... | 88 |
| `docs/analysis/LINK_VALIDATION_FIX_SUMMARY.md` | `items: list[T]` | File not found: docs/analysis/items: list[T] | 98 |
| `docs/analysis/WORKFLOW_LINK_VALIDATION_FINAL_REPORT.md` | `[^"\']+` | File not found: docs/analysis/[^"\']+ | 174 |
| `docs/analysis/WORKFLOW_LINK_VALIDATION_FINAL_REPORT.md` | `state["inputs"]` | File not found: docs/analysis/state["inputs"] | 178 |
| `docs/analysis/WORKFLOW_LINK_VALIDATION_FINAL_REPORT.md` | `items: list[T]` | File not found: docs/analysis/items: list[T] | 190 |
| `docs/capabilities/functional_training.md` | `state["inputs"]` | File not found: docs/capabilities/state["inputs"] | 283 |
| `docs/capabilities/functional_training.md` | `outputs, state["targets"]` | File not found: docs/capabilities/outputs, state["targets"] | 284 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `[^"\']+` | File not found: docs/maintenance/[^"\']+ | 28 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `[^"\']+` | File not found: docs/maintenance/[^"\']+ | 53 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/maintenance/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 76 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/maintenance/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 77 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/maintenance/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 78 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `state["inputs"]` | File not found: docs/maintenance/state["inputs"] | 82 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `outputs, state["targets"]` | File not found: docs/maintenance/outputs, state["targets"] | 83 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `.+?` | File not found: docs/plans/.+? | 2379 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2462 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2463 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2464 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2465 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2466 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2467 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2468 |
| `docs/plans/copilot-directives-to-implementation-plan.md` | `[^"\']+` | File not found: docs/plans/[^"\']+ | 2469 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 41 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/quality/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 96 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/quality/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 98 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/quality/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 100 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `state["inputs"]` | File not found: docs/quality/state["inputs"] | 105 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `outputs, state["targets"]` | File not found: docs/quality/outputs, state["targets"] | 107 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 129 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/quality/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 149 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/quality/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 151 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1` | File not found: docs/quality/blob:https:/chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1 | 153 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `state["inputs"]` | File not found: docs/quality/state["inputs"] | 155 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `outputs, state["targets"]` | File not found: docs/quality/outputs, state["targets"] | 157 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 243 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 245 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 247 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 249 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 251 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 253 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 255 |
| `docs/quality/BROKEN_LINKS_REPORT.md` | `[^"\']+` | File not found: docs/quality/[^"\']+ | 257 |
| `docs/workflows/DELEGATED_COMMENT_WORKFLOWS.md` | `URL` | File not found: docs/workflows/URL | 5 |
| `docs/workflows/DELEGATED_COMMENT_WORKFLOWS.md` | `URL` | File not found: docs/workflows/URL | 510 |
| `docs/workflows/DELEGATED_COMMENT_WORKFLOWS.md` | `URL` | File not found: docs/workflows/URL | 511 |
| `docs/workflows/DELEGATED_COMMENT_WORKFLOWS.md` | `URL` | File not found: docs/workflows/URL | 513 |

---

## 🔗 Broken Anchor References

**Total Broken Anchors:** 108

### Anchor Issues by Type

#### Same-File Anchor References (95)

| File | Anchor | Line |
|------|--------|------|
| `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` | `#5-manifest--discovery` | 24 |
| `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` | `#10-security--injection-hardening` | 29 |
| `docs/AGENTIC_REPO_SYSTEM_GUIDE.md` | `#11-accountability--audit-trail` | 30 |
| `docs/CODEBASE_MERMAID_MAPS.md` | `#9-pda-loop--aftermath` | 21 |
| `docs/CODEBASE_MERMAID_MAPS.md` | `#11-security--token-delegation` | 23 |
| `docs/CODEBASE_MERMAID_MAPS.md` | `#16-phase-9--cognitive-brain-autonomous-ops` | 28 |
| `docs/CODEBASE_MERMAID_MAPS.md` | `#17-phase-10--post-coverage-maintenance` | 29 |
| `docs/CODEBASE_MERMAID_MAPS.md` | `#18-phase-10-progress--coverage-expansion` | 30 |
| `docs/Copy_of_Repository Secrets and Variables Inventory.md` | `#1-repository-variables-settingsvariablesactions` | 93 |
| `docs/Copy_of_Repository Secrets and Variables Inventory.md` | `#3-environment-variables--secrets-aries_serpent_codex_` | 95 |
| `docs/Copy_of_Repository Secrets and Variables Inventory.md` | `#8-immediate-post-setup-validation-ui` | 100 |
| `docs/Copy_of_Repository Secrets and Variables Inventory.md` | `#-complete-inventory-tables` | 101 |
| `docs/Copy_of_Repository Secrets and Variables Inventory.md` | `#-summary-statistics` | 102 |
| `docs/Copy_of_Repository Secrets and Variables Inventory.md` | `#-maintainer-execution-checklist` | 103 |
| `docs/Copy_of_Repository Secrets and Variables Inventory.md` | `#-complete-inventory-tables` | 344 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#2-how-to-set-variables--quick-links` | 18 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#5-environment-secrets-aries_serpent_codex_` | 21 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6a--cognitive-brain` | 23 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6b--copilot-agent-runtime` | 24 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6c--cicd-health` | 25 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6d--identity--static-config` | 26 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6e--runtime--build-config` | 27 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6f--ml--huggingface--weights--biases` | 28 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6g-webhook--infra` | 29 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6h--autonomous-agent-config` | 30 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#7-environment-variables-aries_serpent_codex_` | 31 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#10-known-issues--inconsistencies` | 34 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#13--previously-missing--all-resolved-2026-03-07` | 37 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#7-environment-variables-aries_serpent_codex_` | 170 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6h--autonomous-agent-config` | 671 |
| `docs/admin/GITHUB_VARIABLES_MASTER_GUIDE.md` | `#6h--autonomous-agent-config` | 685 |
| `docs/admin/HUMAN_ADMIN_REPO_VARIABLES_SETUP.md` | `#1--batch-cli-method-recommended---5-minutes` | 544 |
| `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` | `#3-new-variables--cognitive-brain` | 15 |
| `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` | `#4-new-variables--copilot-cli` | 16 |
| `docs/admin/REPO_VARIABLES_IMPLEMENTATION_GUIDE.md` | `#5-new-variables--cicd-health` | 17 |
| `docs/admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md` | `#mcp-architecture-in-_codex_` | 13 |
| `docs/admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md` | `#current-_codex_-mcp-implementation` | 15 |
| `docs/admin/integration/GITHUB_MCP_INTEGRATION_GUIDE.md` | `#_codex_-specific-integration-examples` | 21 |
| `docs/authentication/USER_GUIDE.md` | `#enabling-multi-factor-authentication` | 12 |
| `docs/authentication/USER_GUIDE.md` | `#working-with-tokens` | 13 |
| `docs/authentication/USER_GUIDE.md` | `#session-management` | 14 |
| `docs/authentication/USER_GUIDE.md` | `#security-best-practices` | 15 |
| `docs/authentication/USER_GUIDE.md` | `#troubleshooting` | 16 |
| `docs/ci/CI_RESCUE_PIPELINE.md` | `#5-sequence-diagram--golden-path-2026-03-30` | 16 |
| `docs/ci/PR_LIFECYCLE.md` | `#7-rescue--self-healing-chain` | 23 |
| `docs/ci/PR_LIFECYCLE.md` | `#15-rag-module-tests--chronic-failure-pattern` | 31 |
| `docs/ci/PR_LIFECYCLE.md` | `#16-copilot-comment-budget--rate-limit-controls` | 32 |
| `docs/ci/PR_LIFECYCLE.md` | `#17-pda-loop--aftermath--failure-pattern-logging` | 33 |
| `docs/ci/PR_LIFECYCLE.md` | `#18-wec-workflow-catalog--complete-reference` | 34 |
| `docs/ci/PR_LIFECYCLE.md` | `#23-wec-trigger--cancel-model` | 39 |
| `docs/ci/PR_LIFECYCLE.md` | `#24-auto-approve-overhaul--schedule-labels--owner-protection-s302` | 40 |
| `docs/ci/PR_LIFECYCLE.md` | `#appendix-known-recurring-ci-failure-patterns` | 42 |
| `docs/ci/PR_LIFECYCLE.md` | `#18-wec-workflow-catalog--complete-reference` | 81 |
| `docs/ci/PR_LIFECYCLE.md` | `#` | 382 |
| `docs/ci/PR_LIFECYCLE.md` | `#18-wec-workflow-catalog--complete-reference` | 733 |
| `docs/ci/PR_LIFECYCLE.md` | `#18-wec-workflow-catalog--complete-reference` | 2176 |
| `docs/contributing/CODE_QUALITY_IMPORT_GUIDELINES.md` | `#type_checking-pattern` | 18 |
| `docs/maintenance/LINK_VALIDATION_REPORT.md` | `#tooling-testing` | 177 |
| `docs/operations/ALERT_RUNBOOKS.md` | `#critical-database-connection-failed` | 43 |
| `docs/operations/INCIDENT_RESPONSE_PLAYBOOKS.md` | `#communication--escalation` | 21 |
| `docs/operations/PRODUCTION_OPERATIONS_RUNBOOK.md` | `#scaling--performance` | 13 |
| `docs/operations/PRODUCTION_OPERATIONS_RUNBOOK.md` | `#backup--recovery` | 14 |
| `docs/operations/PRODUCTION_OPERATIONS_RUNBOOK.md` | `#secrets--access-management` | 16 |
| `docs/operations/PRODUCTION_OPERATIONS_RUNBOOK.md` | `#monitoring--alerts` | 17 |
| `docs/ops/CACHE_SHARED_DATASETS.md` | `#7-gaps--recommendations` | 17 |
| `docs/ops/SAR_METHODOLOGY.md` | `#4-phase-1--search-drift--anomaly-detection` | 24 |
| `docs/ops/SAR_METHODOLOGY.md` | `#5-phase-2--triage-severity-classification` | 25 |
| `docs/ops/SAR_METHODOLOGY.md` | `#6-phase-3--rescue-remediation-playbooks` | 26 |
| `docs/ops/SAR_METHODOLOGY.md` | `#7-phase-4--reintegrate-validation-gate` | 27 |
| `docs/ops/SAR_METHODOLOGY.md` | `#8-phase-5--prevent-continuous-watchdog` | 28 |
| `docs/ops/SAR_METHODOLOGY.md` | `#10-gap-registry--roadmap` | 30 |
| `docs/ops/SAR_METHODOLOGY.md` | `#12-executable-planset--copilot-agent-steps` | 32 |
| `docs/ops/SAR_METHODOLOGY.md` | `#13-tools--cli-quick-reference` | 33 |
| `docs/ops/SAR_METHODOLOGY.md` | `#14-references--standards` | 34 |
| `docs/plans/AUTONOMOUS_PRIVILEGE_ARCHITECTURE.md` | `#1-the-five-surfaces--overview` | 13 |
| `docs/plans/AUTONOMOUS_PRIVILEGE_ARCHITECTURE.md` | `#9-full-autonomy-loop--end-to-end-sequence` | 21 |
| `docs/plans/AUTONOMOUS_PRIVILEGE_ARCHITECTURE.md` | `#11-failure-modes--fallback-chains` | 23 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#executive-summary` | 11 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#current-architecture-analysis` | 12 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#merge-chain--workflow-architecture` | 13 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#session-concurrency-control-design` | 14 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#pr-template-enhancement` | 15 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#autonomous-self-healing-pipeline` | 16 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#expected-errors--known-limitations` | 17 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#edge-cases--blockers` | 18 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#implementation-roadmap` | 19 |
| `docs/plans/AUTONOMOUS_SELF_HEALING_PROPOSAL_S182.md` | `#verification--testing-strategy` | 20 |
| `docs/plans/COPILOT_SESSION_HANDOFF_DESIGN.md` | `#7-known-gaps--improvement-plan` | 17 |
| `docs/plans/larger-runners-upgrade.md` | `#8-recent-changes-context-w-119--w-122` | 39 |
| `docs/production/RBAC_SPECIFICATION.md` | `#audit--compliance` | 19 |
| `docs/production/SECRET_ROTATION_POLICY.md` | `#monitoring--compliance` | 18 |
| `docs/production/SECRET_ROTATION_POLICY.md` | `#faq--troubleshooting` | 19 |
| `docs/reference/ELEVATED_PRIVILEGES_TOKEN_REVIEW.md` | `#6-identified-gaps--aais-improvement-tasks` | 15 |
| `docs/workflows/DELEGATED_COMMENT_WORKFLOWS.md` | `#2-workflow-catalogue--reference-table` | 12 |
| `docs/workflows/PR_COMMENT_LIFECYCLE.md` | `#process-overlap--consolidation-opportunities` | 17 |

#### Cross-File Anchor References (13)

| Source File | Link | Target File | Anchor | Line |
|-------------|------|-------------|--------|------|
| `docs/PR_TEMPLATE_COMPREHENSIVE.md` | `./CONTRIBUTING.md#testing-requirements` | `docs/CONTRIBUTING.md` | `testing-requirements` | 710 |
| `docs/ROADMAP.md` | `ops/SAR_METHODOLOGY.md#10-gap-registry--roadmap` | `docs/ops/SAR_METHODOLOGY.md` | `10-gap-registry--roadmap` | 53 |
| `docs/cognitive_brain/INDEX.md` | `../evolution/EVOLUTION_TIMELINE.md#phase-9` | `docs/evolution/EVOLUTION_TIMELINE.md` | `phase-9` | 41 |
| `docs/cognitive_brain/INDEX.md` | `../evolution/PLANSET_REGISTRY.md#phase-9` | `docs/evolution/PLANSET_REGISTRY.md` | `phase-9` | 42 |
| `docs/index.md` | `../CONTRIBUTING.md#using-operational-templates` | `CONTRIBUTING.md` | `using-operational-templates` | 99 |
| `docs/reporting/copilot_agent_session_standard_operation.md` | `workflow_portfolio_7d_analysis.md#-branch-update-conflict-dashboard` | `docs/reporting/workflow_portfolio_7d_analysis.md` | `-branch-update-conflict-dashboard` | 120 |
| `docs/status_updates/survey-0D_base_-and-1926-2025-10-30.md` | `./guides/reasoning_overview.md#evaluation-readiness` | `docs/status_updates/guides/reasoning_overview.md` | `evaluation-readiness` | 2212 |
| `docs/system/CODEBASE_DASHBOARD.md` | `../SECRETS_AND_ENVIRONMENT_VARIABLES.md#🗺️-workflow--agent-variable-usage-map` | `docs/SECRETS_AND_ENVIRONMENT_VARIABLES.md` | `🗺️-workflow--agent-variable-usage-map` | 47 |
| `docs/tech_debt/research_queue/questions_for_research.md` | `../../../src/codex_init.py#L15` | `src/codex_init.py` | `L15` | 679 |
| `docs/tech_debt/research_queue/questions_for_research.md` | `../../../tools/validate.py#L25` | `tools/validate.py` | `L25` | 716 |
| `docs/tech_debt/research_queue/questions_for_research.md` | `../../../src/codex_ml/training/unified_training.py#L42` | `src/codex_ml/training/unified_training.py` | `L42` | 763 |
| `docs/tech_debt/research_queue/questions_for_research.md` | `../../../src/codex_ml/training/unified_training.py#L43` | `src/codex_ml/training/unified_training.py` | `L43` | 784 |
| `docs/validation/Windows_Filename_Remediation.md` | `../../AGENTS.md#-cross-platform-filename-requirements` | `AGENTS.md` | `-cross-platform-filename-requirements` | 158 |


---

## 🌐 External Links (Manual Review Required)

**Total External Links:** 2699

### Sample External URLs (First 50)

1. `http://${API_ENDPOINT}`
2. `http://${API_ENDPOINT}/...`
3. `http://${API_ENDPOINT}/api/v1/health`
4. `http://${API_ENDPOINT}/api/v1/resources`
5. `http://${API_ENDPOINT}/api/v1/status`
6. `http://${API_ENDPOINT}/api/v1/test`
7. `http://${API_ENDPOINT}/api/v1/validation/production-health`
8. `http://${API_ENDPOINT}/auth/login`
9. `http://${API_ENDPOINT}/health`
10. `http://127.0.0.1:3000",`
11. `http://127.0.0.1:5000"`
12. `http://127.0.0.1:5000")`
13. `http://127.0.0.1:7777/copilot/run`
14. `http://127.0.0.1:7777/health`
15. `http://127.0.0.1:8000/`
16. `http://127.0.0.1:8000/health`
17. `http://127.0.0.1:8080"`
18. `http://<server-ip>:8000/health`
19. `http://LOAD_BALANCER_IP/health`
20. `http://``
21. `http://alertmanager:9093/api/v1/alerts`
22. `http://codex_auth;`
23. `http://evil.com')\">Click`
24. `http://evil.com'\">"`
25. `http://example.com",`
26. `http://external.com`
27. `http://jaeger:14268/api/traces"`
28. `http://jaeger:4317`).`
29. `http://json-schema.org/draft-07/schema#",`
30. `http://localhost:18765/api/health`
31. `http://localhost:3000`
32. `http://localhost:4317``
33. `http://localhost:5173',`
34. `http://localhost:5601`
35. `http://localhost:6060/debug/pprof/heap`
36. `http://localhost:6060/debug/pprof/profile?seconds=30`
37. `http://localhost:8000/health`
38. `http://localhost:8000/infer`
39. `http://localhost:8000``
40. `http://localhost:8080/admin/cache/clear`
41. `http://localhost:8080/health/detailed`
42. `http://localhost:8080/health/live`
43. `http://localhost:8080/health/ready`
44. `http://localhost:8765`
45. `http://localhost:8765"`
46. `http://localhost:8765")`
47. `http://localhost:8765"]`
48. `http://localhost:8765';``
49. `http://localhost:8765/api/cli/history`
50. `http://localhost:8765/api/cli/history?limit=1`

... and 2649 more external links


**Note:** External links should be validated manually as needed. Consider using:
- GitHub's link-validator workflow
- `curl -I <url>` for spot checks
- Automated link checkers for production documentation

---

## 📋 Files Scanned

**Total:** 1646 markdown files

Sample of files audited:
- `docs/ADMIN_DECISIONS_README.md`
- `docs/ADMIN_FAQ.md`
- `docs/ADMIN_IMPLEMENTATION_GUIDE.md`
- `docs/ADMIN_QUICKSTART.md`
- `docs/ADVANCED_PHYSICS_GUIDE.md`
- `docs/AGENTIC_REPO_SYSTEM_GUIDE.md`
- `docs/AI_AGENT_INTUITIVENESS_SCORE_V2.md`
- `docs/AI_ASSISTANT_TERMINOLOGY_AUDIT.md`
- `docs/AI_TURN_ANALYSIS_PR2462.md`
- `docs/API_REFERENCE.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_BLUEPRINT.md`
- `docs/AUTONOMOUS_CONTINUATION_PROMPT_PHASE_1_2.md`
- `docs/Architecture.md`
- `docs/BUNDLE_BUILDER_INTEGRATION_PLAN.md`
- `docs/CHANGELOG.md`
- `docs/CHANGELOG/INDEX.md`
- `docs/CHANGELOG/change_log.md`
- `docs/CHANGELOG/changelog_codex.md`
- `docs/CHANGELOG/changelog_session_logging.md`
- `docs/CHATGPT_ASSISTANT_GUIDE.md`
- `docs/CHECKPOINTS.md`
- `docs/CI.md`
- `docs/CI_FAILURE_RESOLUTION_PR_2858.md`
- `docs/CLI.md`
- `docs/CODEBASE_MERMAID_MAPS.md`
- `docs/CODEOWNER-NOTES.md`
- `docs/CODEX_STRUCTURE_CONSOLIDATION_PROMPT.md`
- `docs/CODE_REVIEW_STANDARDS.md`
- `docs/COGNITIVE_BRAIN_GITHUB_LOGS_UPDATE.md`

... and 1616 more files


---

## 🎯 Remediation Priority

### Critical (Requires Immediate Action)
- **64 Broken internal file references** - These links point to non-existent files
- **13 Broken cross-file anchors** - These links reference sections that don't exist in target files

**Action:** Review and fix the broken links listed above. These prevent proper navigation in documentation.

### Non-Critical (Consider Fixing)
- **95 Broken same-file anchors** - These links reference sections within the same file that don't exist

**Action:** Fix anchor names to match section headings, or update section headings to match anchor references.


### Informational

- **2699 External links** - These should be periodically validated but don't block documentation functionality
  - Consider adding link validation to CI/CD pipeline
  - Document external dependencies and update frequency

---

## 🔧 How to Fix Broken Links

### Broken Internal File References
1. Check if the referenced file exists in the docs/ directory
2. If file is missing, either:
   - Restore the file if it was accidentally deleted
   - Update the link to point to the correct file
3. Verify the relative path is correct from the source file's perspective

### Broken Anchors
1. Check the target file for the referenced section
2. If the section exists, update the anchor to match the heading text
3. If the section doesn't exist, either:
   - Add the missing section
   - Remove or update the link to point to an existing section
4. Remember: GitHub converts headings to anchors by lowercasing and replacing spaces with hyphens

### Example Anchor Conversion
```
Heading: "## Configuration Management"
Anchor:  "#configuration-management"
```

---

## 📈 Trends & Recommendations

### Current Status
- ✅ 2718 valid links are functioning correctly
- ⚠️ 172 total broken links need remediation
- Success rate: 94.0%

### Recommendations
1. **Immediate:** Fix all broken file references (blocking)
2. **Soon:** Fix broken anchor references (improves navigation)
3. **Ongoing:** Add link validation to CI/CD pipeline to catch new broken links
4. **Documentation:** Consider using a link checker tool in your release process

### Tools to Consider
- `markdown-link-checker` - Node.js based
- Python's `linkchecker` library
- GitHub Actions: `gaurav-nelson/github-action-markdown-link-check`

---

## 📝 Audit Methodology

This audit:
1. **Indexed** all markdown files in the docs/ directory
2. **Extracted** anchor definitions from headings and HTML anchors
3. **Scanned** all markdown links ([text](url)) and direct URLs
4. **Validated** internal file references and cross-file anchors
5. **Cataloged** external URLs for manual review

### Scanning Rules
- Internal links: Must reference existing files or anchors
- Anchors: Extracted from markdown headings (converted to GitHub format)
- External links: Extracted but not validated (requires network access)
- Relative paths: Resolved from the source file's directory

---

**Report Generated:** 2026-06-16T13:28:39Z
**Detailed Data:** See `.codex/link_audit_detailed.json`
