# Documentation Link Validation Report

> **⚠️ DEPRECATED**: This is a legacy report from a previous validation run.
>
> **Current Status**: As of 2026-02-10, enhanced validation system deployed with:
> - Smart false positive filtering (reduces noise by 93%)
> - Code block detection to skip examples
> - Pattern-based exclusions for code syntax
>
> **Latest Results**: Only 5 errors (all acceptable/documented)
>
> Run current validation:
> ```bash
> python scripts/validate_docs_links.py
> ```
>
> See: `.codex/validation_categorization_report.md` for current analysis

---

## Historical Report (Archived)

**Report Date**: ~2025-2026 (Pre-Enhancement)  
**Total Files**: 1292  
**Broken Links**: 321 (includes many false positives)

**Note**: This report contains numerous false positives including:
- Regex patterns (e.g., `["\']([^"\']+)`)
- Code examples (e.g., `ClassName(config)`)
- Python syntax (e.g., `state["inputs"]`)
- Blob URLs from external sources

---

## Missing Extension (33)

### .codex/archive/README_UPDATED.md

- `Dockerfile` → No suggestion

### .codex/change_log.md

- `Dockerfile` → No suggestion

### .codex/update_pr_template_for_continuation.md

- ``{output_file}`` → No suggestion
- `full prompt` → No suggestion

### docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md

- `"\'` → No suggestion
- `["\']([^"\']+)` → No suggestion
- `"\'` → No suggestion

### docs/NEWCOMER_GUIDE.md

- `docs/templates/` → No suggestion

### docs/agents/CODE_TEMPLATES.md

- ``ClassName(config)`` → No suggestion
- ``ClassName(config)`` → No suggestion
- ``ClassName(config)`` → No suggestion
- ``ServiceName(config)`` → No suggestion

### docs/agents/PROMPT_TEMPLATES.md

- _(Code snippet - not a link)_
- ``method("valid_input")`` → No suggestion
- ``method("")`` → No suggestion
- ``method(None)`` → No suggestion

### docs/ai-facing/Design_Specification_Quantum_Compression_Neural_Pathway_Integration.md

- `[!\[GitHub\](blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1)` → No suggestion
- `[!\[GitHub\](blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1)` → No suggestion
- `[!\[GitHub\](blob:https://chatgpt.com/605ab1eb-dbcf-4f51-8968-026373f955d1)` → No suggestion

### docs/capabilities/functional_training.md

- `["model"](state["inputs"])` → No suggestion
- `["criterion"](outputs, state["targets"])` → No suggestion

### docs/mcp/MCP_DEVELOPER_GUIDE.md

- `Test Examples` → No suggestion

_... and 4 more files_

## Missing File (206)

### .codex/FOLLOWUP_FOR_PHASE3.md

- `.*\` → No suggestion

### .codex/PR_FOLLOWUP_COMMENT.md

- `.*\` → No suggestion

### .codex/change_log.md

- `docs/guides/AGENTS.md` → Possible: ../../_codex_/_codex_/AGENTS.md
- ``.github/workflows/ci.yml`` → No suggestion
- `docs/guides/AGENTS.md` → Possible: ../../_codex_/_codex_/AGENTS.md
- ``.github/workflows/ci.yml`` → No suggestion
- `docs/guides/AGENTS.md` → Possible: ../../_codex_/_codex_/AGENTS.md
  _... and 4 more_

### .codex/docs/AGENTS.md.original.cf4e8c9.md

- `.codex/guardrails.md` → Possible: ../../_codex_/.codex/guardrails.md
- `docs/agent/OPERATIONAL_GUIDELINES.md` → Possible: ../../_codex_/docs/agent/OPERATIONAL_GUIDELINES.md
- `.codex/guardrails.md` → Possible: ../../_codex_/.codex/guardrails.md
- `docs/agent/OPERATIONAL_GUIDELINES.md` → Possible: ../../_codex_/docs/agent/OPERATIONAL_GUIDELINES.md
- `docs/admin/GENESIS_SETUP_GUIDE.md` → Possible: ../../_codex_/docs/admin/GENESIS_SETUP_GUIDE.md
  _... and 8 more_

### .codex/status/_codex_status_update-2025-08-31.md

- ``.codex/deferred_items.md`` → Possible: ../../_codex_/docs/deferred_items.md

### .codex/status/_codex_status_update-2025-09-07.md

- `docs/guides/AGENTS.md` → Possible: ../../_codex_/_codex_/AGENTS.md

### .codex/update_pr_template_for_continuation.md

- `Updated Follow-Up Prompt` → No suggestion
- ``.github/copilot-prompts/active/PR-{pr_number}-followup.md`` → No suggestion
- `complete follow-up prompt` → No suggestion
- `View` → No suggestion

### agents/prompts/audit/check-regressions.md

- `show-trend.md` → No suggestion
- `store-trend.md` → No suggestion

### agents/prompts/audit/run-full-audit.md

- `generate-dashboard.md` → No suggestion
- `show-trend.md` → No suggestion

### agents/prompts/deployment/pre-release-deployment.md

- `validate-release.md` → No suggestion

_... and 41 more files_

## Relative Up (81)

### .codex/COMPREHENSIVE_WORKFLOW_CONSOLIDATION_PLAN.md

- `[Environment Setup](../setup/environment.md)` → Possible: ../../_codex_/docs/ops/environment.md
- `[Secrets Management](../security/secrets.md)` → No suggestion
- `Deployment Guide` → Possible: ../../_codex_/docs/zendesk/README.md

### .codex/update_pr_template_for_continuation.md

- `PR #2649 Phase 3` → Possible: ../../_codex_/misc/repo-owner-review/auto-generated-prompts/PR-2649-followup.md
- `PR #2651 Phase 1` → Possible: ../../_codex_/misc/repo-owner-review/auto-generated-prompts/PR-2651-followup.md

### agents/prompts/debugging/performance-optimization.md

- `[Codex performance utilities](https://github.com/Aries-Serpent/_codex_/blob/main/scripts/space_traversal/performance.py)` → No suggestion

### agents/prompts/debugging/resolve-merge-conflicts.md

- `[Codex contribution guidelines](.././CONTRIBUTING.md)` → Possible: ../../_codex_/docs/dev/CONTRIBUTING.md

### agents/prompts/debugging/security-remediation.md

- `[Codex Security Policy](.././SECURITY.md)` → Possible: ../../_codex_/SECURITY.md

### agents/prompts/debugging/test-failure-debugging.md

- `[Codex testing conventions](#tooling-testing)` → No suggestion

### configs/CONFIGURATION_STRUCTURE.md

- `Configuration Best Practices` → Possible: ../../_codex_/docs/capabilities/configuration.md
- `Training Configuration Guide` → Possible: ../../_codex_/docs/capabilities/configuration.md
- `Deployment Configuration` → Possible: ../../_codex_/docs/capabilities/configuration.md

### docs/DOCUMENTATION_INDEX.md

- `COMPREHENSIVE_GAP_ANALYSIS.md` → Possible: archive/COMPREHENSIVE_GAP_ANALYSIS.md
- `PR_FINAL_SUMMARY.md` → Possible: archive/pr_reports/PR_FINAL_SUMMARY.md
- `archive/historical_docs_20251210/INDEX.md` → Possible: ../../_codex_/workbench/INDEX.md
- `training/config.py` → No suggestion
- `MCP_DEVELOPER_GUIDE.md` → Possible: mcp/MCP_DEVELOPER_GUIDE.md
  _... and 12 more_

### docs/DUPLICATION_METRICS_GUIDE.md

- `Acceptance Criteria Verification` → No suggestion

### docs/GITHUB_AGENT_PR_REVIEWER_IMPLEMENTATION.md

- `[Security Best Practices](.././SECURITY.md)` → Possible: ../../_codex_/SECURITY.md
- `[Contributing Guidelines](.././CONTRIBUTING.md)` → Possible: dev/CONTRIBUTING.md
- `[Agents Architecture](.././agents.md)` → Possible: ../../_codex_/_codex_/AGENTS.md
- `[Security Guidelines](.././SECURITY.md)` → Possible: ../../_codex_/SECURITY.md
- `[Contributing Guidelines](.././CONTRIBUTING.md)` → Possible: dev/CONTRIBUTING.md
  _... and 1 more_

_... and 27 more files_

## Tmp Violations (1)

### docs/admin/CONTINUATION_ROADMAP.md

- `Phase 1 Implementation Summary` → No suggestion
