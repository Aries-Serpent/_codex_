# Non-workflow snapshot recovery manifest

Source tip: `5980258483d8f03b6385562fc0940c52e183fb87`.

Base: `71613ee000808ab758cc2f8ddb07a05c5101f731`.

Snapshot commit: `053409ad98ff3dc40243d1e132a1139e83ffaef7`.

The snapshot restores exactly 332 non-workflow paths from the source tip in one commit. The four workflow changes are deliberately absent. A subsequent non-rewriting merge preserves the assigned publication branch's prior history, whose net change is `.codex/session_startup_packet.json` timestamp metadata. This manifest and its validation evidence are separate recovery documentation, not part of the original 332-path snapshot.

The copied checkpoints and historical accountability/changelog/audit reports describe the original source snapshot, which included workflow changes. They must not be read as fresh validation of this workflow-excluded branch. In particular setup-runtime/workflow contract tests may require held-back workflow behavior. This partial recovery is not release-ready.

## Held-back workflows

| Path | Exists on base | Disposition |
|---|---|---|
| `.github/workflows/copilot-setup-steps.yml` | Yes | Base version retained; source changes held back by explicit scope and workflow-write permission boundary. |
| `.github/workflows/deferral-language-gate.yml` | Yes | Base version retained; source changes held back by explicit scope and workflow-write permission boundary. |
| `.github/workflows/pypi-publish.yml` | Yes | Base version retained; source changes held back by explicit scope and workflow-write permission boundary. |
| `.github/workflows/strict-no-deferral-security.yml` | Yes | Base version retained; source changes held back by explicit scope and workflow-write permission boundary. |

## Snapshot references to held-back workflows

117 file/line/workflow references across 18 files. Detection uses each full path or workflow basename; base existence is independently verified above. Historical prose is listed alongside executable/config references rather than being treated as proof of functional coupling.

| Snapshot file | Line | Held-back path | Exists on base |
|---|---:|---|---|
| `.codex/aftermath/pda_iterations.jsonl` | 19 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 74 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 95 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 236 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 237 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 294 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 6 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 7 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 12 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `.codex/aftermath/pda_iterations.jsonl` | 410 | `.github/workflows/pypi-publish.yml` | Yes |
| `.codex/checkpoints/pypi-code-complete.json` | 14 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/checkpoints/pypi-phase2-triage.json` | 42 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/reports/agent-restrictions-evidence-2026-10-22.json` | 602 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/reports/agent-restrictions-evidence-2026-10-22.json` | 644 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `.codex/reports/agent-restrictions-evidence-2026-10-22.json` | 603 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `.codex/reports/agent-restrictions-evidence-2026-10-22.json` | 645 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `.codex/reports/agent-restrictions-evidence-2026-10-22.json` | 604 | `.github/workflows/strict-no-deferral-security.yml` | Yes |
| `.codex/reports/agent-restrictions-evidence-2026-10-22.json` | 646 | `.github/workflows/strict-no-deferral-security.yml` | Yes |
| `.github/agents/cognitive-brain-session-injector.md` | 144 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `CHANGELOG.md` | 409 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `CHANGELOG.md` | 284 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `CHANGELOG.md` | 169 | `.github/workflows/pypi-publish.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 130 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 136 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 183 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 330 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 1472 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 8542 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 12049 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 12096 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 12117 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 12120 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 12191 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 12199 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 21698 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 21707 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 23937 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 13575 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 14025 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 14034 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 14044 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 14055 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 14161 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 14887 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 15337 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 15346 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 15356 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 15367 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 15473 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 15877 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 16398 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 16468 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 16788 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 16941 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 17255 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 17459 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 17518 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 17531 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 17598 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 18002 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 18379 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 18946 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19118 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19263 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19273 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19414 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19422 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19430 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19438 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19864 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19874 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19884 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19892 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19900 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19908 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19916 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 19926 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 20568 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 20624 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 20632 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 20726 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 20790 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 21282 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 21292 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 21566 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 696 | `.github/workflows/pypi-publish.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 6374 | `.github/workflows/pypi-publish.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 23283 | `.github/workflows/pypi-publish.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 23290 | `.github/workflows/pypi-publish.yml` | Yes |
| `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md` | 23349 | `.github/workflows/pypi-publish.yml` | Yes |
| `docs/agent/COPILOT_SETUP_STEPS_GUARD.md` | 5 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/agent/COPILOT_SETUP_STEPS_GUARD.md` | 56 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/agent/COPILOT_SETUP_STEPS_GUARD.md` | 58 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | 163 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md` | 636 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `docs/ops/SAR_METHODOLOGY.md` | 680 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `docs/ops/SAR_METHODOLOGY.md` | 708 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/session_wrapup_autofix.py` | 107 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `scripts/ci/session_wrapup_autofix.py` | 152 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `scripts/ci/session_wrapup_autofix.py` | 522 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `scripts/ci/session_wrapup_autofix.py` | 1787 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `scripts/ci/validate_copilot_dependencies.py` | 3 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/validate_copilot_dependencies.py` | 37 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/validate_copilot_dependencies.py` | 302 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/validate_copilot_dependencies.py` | 304 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/validate_copilot_dependencies.py` | 328 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `scripts/ci/validate_copilot_setup_steps.py` | 3 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/validate_copilot_setup_steps.py` | 50 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/validate_copilot_setup_steps.py` | 726 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `scripts/ci/validate_copilot_setup_steps.py` | 63 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `scripts/ci/validate_setup_steps_yaml.sh` | 4 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `src/aries_serpent_core/agents/brain_client.py` | 65 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `src/aries_serpent_core/agents/brain_client.py` | 201 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `tests/ci/test_agent_bootstrap_runtime.py` | 16 | `.github/workflows/copilot-setup-steps.yml` | Yes |
| `tests/ci/test_agent_instruction_contract.py` | 92 | `.github/workflows/deferral-language-gate.yml` | Yes |
| `tests/ci/test_agent_instruction_contract.py` | 93 | `.github/workflows/strict-no-deferral-security.yml` | Yes |
| `tests/release/test_pypi_publish_workflow.py` | 9 | `.github/workflows/pypi-publish.yml` | Yes |

## Held-back workflow references to snapshot checkpoints/configuration

Examined all 11 changed checkpoint/manifest/configuration candidates against all four source workflow files using full paths and basenames. Each match below is a source dependency, not a claim that the unchanged base workflow consumes the new file or schema correctly.

| Snapshot file | Held-back workflow | Workflow line | Reference |
|---|---|---:|---|
| None found | - | - | Literal full-path/basename search returned no matches. |

## Validation comparison

Both trees use the same existing `/tmp/pypi-venv/bin/python` environment in separate detached worktrees. Commands are unmodified: no exclusions, maxfail overrides, timeout wrappers, failure ignores or baseline resets. Full test commands run sequentially to avoid two memory-heavy suites competing. An active or queued command is not a passing result.

| Command | Base | Snapshot |
|---|---|---|
| `python -m ruff check .` | Exit 1 | Exit 0 |
| `python -m black --check src/` | Exit 1 | Exit 0 |
| `python -m mypy src/` | Exit 2 | Exit 1 |
| `python -m pytest tests/ --cov=src` | running | queued |

Ruff improves from two F405 errors to zero. Black improves from 84 files requiring formatting to zero (1,969 source files unchanged). Base mypy exits before analysis because `self-healing contains __init__.py but is not a valid Python package name`; snapshot mypy completes with 1,055 errors in 323 files across 1,972 checked files. These distinct failure modes do not support claiming a quantified type-error reduction against this base run. Snapshot typing remains blocked.

Full raw static-command output is retained in `recovery/bfe2456b/validation/`. Full-suite output, process state and exit status are recorded during execution under `/tmp/codex-nonworkflow-validation-f17775fa/`; if not yet terminal, full-suite and repository-wide coverage acceptance remain unverified. No passing full-suite result is inferred from earlier selected tests.

## Exact snapshot paths

- `.codex/AGENTIC_REPO_STATE.md`
- `.codex/CODEBASE_AGENCY_POLICY.md`
- `.codex/SELF_HEALING_POLICY_TIERS.md`
- `.codex/aftermath/pda_iterations.jsonl`
- `.codex/checkpoints/pypi-code-complete.json`
- `.codex/checkpoints/pypi-phase2-triage.json`
- `.codex/docs/AGENT_INSTRUCTION_INVENTORY.md`
- `.codex/docs/COPILOT_AGENT_PROMPT_GUIDE.md`
- `.codex/docs/COPILOT_MCP_TOOL_REFERENCE.md`
- `.codex/docs/GITHUB_API_AND_MCP_REFERENCE.md`
- `.codex/patterns/PATTERN_INDEX.md`
- `.codex/reports/AGENT_RESTRICTIONS_AUDIT_2026_10_22.md`
- `.codex/reports/agent-restrictions-evidence-2026-10-22.json`
- `.github/AGENTS.md`
- `.github/WORKFLOW_GOVERNANCE.md`
- `.github/agents/COPILOT_HARDENED_PLANNING_PROTOCOL.md`
- `.github/agents/autonomous-test-healer-agent.md`
- `.github/agents/ci-importerror-agent.md`
- `.github/agents/ci-log-retrieval-agent.md`
- `.github/agents/ci-testing-agent.md`
- `.github/agents/cognitive-brain-session-injector.md`
- `.github/agents/docs/AGENTS.md`
- `.github/agents/policy-coach-agent.md`
- `.github/agents/pr-check-remediation-agent.md`
- `.github/agents/pr-test-infrastructure-fixer.md`
- `.github/agents/qa-walkthrough-agent.md`
- `.github/agents/self-healing-orchestrator-agent.md`
- `.github/agents/session-wrapup-autofix-agent.md`
- `.github/agents/skills-master-agent.md`
- `.github/agents/unified-governance-gate.md`
- `.github/agents/workflow-compliance-guardian.agent.md`
- `.github/copilot-instructions.md`
- `.github/copilot-prompts/active/SESSION-DIAGNOSTIC-PROTOCOL.md`
- `.github/scripts/session_preload.py`
- `.pre-commit-config.yaml`
- `.secrets.baseline`
- `CHANGELOG.md`
- `README.md`
- `docs/accountability/AGENT_ACCOUNTABILITY_REPORT.md`
- `docs/agent/COPILOT_SETUP_STEPS_GUARD.md`
- `docs/ci/GITHUB_API_COPILOT_AGENT_REFERENCE.md`
- `docs/deployment/DEPLOYMENT_RUNBOOK.md`
- `docs/evolution/COGNITIVE_CODEBASE_MAP.md`
- `docs/evolution/INDEX.md`
- `docs/guides/AGENTS.md`
- `docs/guides/lfs_policy.md`
- `docs/ops/SAR_METHODOLOGY.md`
- `docs/reference/GITHUB_VARIABLES_SECRETS_REFERENCE.md`
- `mypy.ini`
- `prompts/AGENTS.md`
- `pyproject.toml`
- `requirements-dev.txt`
- `requirements-test.txt`
- `scripts/AGENTS.md`
- `scripts/ci/agent_resource_profile.py`
- `scripts/ci/agent_setup_readiness.py`
- `scripts/ci/check_deferral_language.py`
- `scripts/ci/check_no_deferral_security.py`
- `scripts/ci/environment_preflight.py`
- `scripts/ci/fetch_lfs_assets.py`
- `scripts/ci/mypy_baseline.py`
- `scripts/ci/phase_10_3_context_scorer.py`
- `scripts/ci/phase_9_1_confidence_scorer.py`
- `scripts/ci/prepare_agent_context.py`
- `scripts/ci/promotion_readiness_gate.py`
- `scripts/ci/session_wrapup_autofix.py`
- `scripts/ci/validate_copilot_bootstrap.py`
- `scripts/ci/validate_copilot_dependencies.py`
- `scripts/ci/validate_copilot_setup_steps.py`
- `scripts/ci/validate_repo_variables.py`
- `scripts/ci/validate_setup_steps_yaml.sh`
- `scripts/tools/doc_metrics_sync.py`
- `src/agent/adapters/openai_compatible_adapter.py`
- `src/agents/__init__.py`
- `src/agents/advanced_physics_calculators.py`
- `src/agents/agent_memory.py`
- `src/agents/developer_orchestrator.py`
- `src/agents/mental_mapping.py`
- `src/agents/mlp_scoring.py`
- `src/agents/msp_client.py`
- `src/agents/physics_integration.py`
- `src/agents/physics_orchestrator.py`
- `src/agents/quantum_game_theory.py`
- `src/aries_serpent_core/agent/core.py`
- `src/aries_serpent_core/agents/brain_client.py`
- `src/aries_serpent_core/api/auth_routes.py`
- `src/aries_serpent_core/ast_adapters/python_adapter.py`
- `src/aries_serpent_core/auth/exceptions.py`
- `src/aries_serpent_core/auth/oauth_manager.py`
- `src/aries_serpent_core/auth/user_store.py`
- `src/aries_serpent_core/cli_rag.py`
- `src/aries_serpent_core/cli_secure.py`
- `src/aries_serpent_core/cli_zendesk.py`
- `src/aries_serpent_core/clients/github_client.py`
- `src/aries_serpent_core/cognitive/brain_interface.py`
- `src/aries_serpent_core/cognitive/ml/validation.py`
- `src/aries_serpent_core/docs_agent/schema_validator.py`
- `src/aries_serpent_core/docs_agent/validation.py`
- `src/aries_serpent_core/github/api_client.py`
- `src/aries_serpent_core/github/http_client.py`
- `src/aries_serpent_core/github/mcp_poster.py`
- `src/aries_serpent_core/governance/approval_service.py`
- `src/aries_serpent_core/ingest/adapter.py`
- `src/aries_serpent_core/logging/chronicle_analytics.py`
- `src/aries_serpent_core/logging/chronicle_cost.py`
- `src/aries_serpent_core/logging/db_utils.py`
- `src/aries_serpent_core/logging/export.py`
- `src/aries_serpent_core/logging/import_ndjson.py`
- `src/aries_serpent_core/logging/query_logs.py`
- `src/aries_serpent_core/logging/session_logger.py`
- `src/aries_serpent_core/logging/session_query.py`
- `src/aries_serpent_core/logging/thread_safe_session_db.py`
- `src/aries_serpent_core/logging/viewer.py`
- `src/aries_serpent_core/rag/indexer.py`
- `src/aries_serpent_core/resilience/__init__.py`
- `src/aries_serpent_core/resilience/circuit_breaker.py`
- `src/aries_serpent_core/resilience/degradation.py`
- `src/aries_serpent_core/resilience/retry.py`
- `src/aries_serpent_core/security/__init__.py`
- `src/aries_serpent_core/security_utils.py`
- `src/aries_serpent_core/skills/cli.py`
- `src/aries_serpent_core/skills/compression.py`
- `src/aries_serpent_core/training.py`
- `src/aries_serpent_core/utils/config_loader.py`
- `src/aries_serpent_core/zendesk/apply.py`
- `src/codex/cli/__init__.py`
- `src/codex/cognitive_brain/__init__.py`
- `src/codex/cognitive_brain/authority.py`
- `src/codex/cognitive_brain/evidence_store.py`
- `src/codex/cognitive_brain/improvement_loop_runner.py`
- `src/codex/cognitive_brain/improvement_pipeline.py`
- `src/codex/cognitive_brain/isolated_execution.py`
- `src/codex/cognitive_brain/kernel.py`
- `src/codex/cognitive_brain/reasoning_engine.py`
- `src/codex/correlation/planset_011.py`
- `src/codex/ensemble/fastapi_server.py`
- `src/codex/ensemble/integration_adapters.py`
- `src/codex/logging/session_logger.py`
- `src/codex/rag/__init__.py`
- `src/codex/scaling/cost_allocator.py`
- `src/codex/scaling/infrastructure/rbac_engine.py`
- `src/codex_bridge/github_client.py`
- `src/codex_init.py`
- `src/codex_ml/__init__.py`
- `src/codex_ml/_train_init_helpers.py`
- `src/codex_ml/checkpointing/checkpoint_core.py`
- `src/codex_ml/cli/__init__.py`
- `src/codex_ml/cli/entrypoints.py`
- `src/codex_ml/cli/main.py`
- `src/codex_ml/cli/utils.py`
- `src/codex_ml/codex_structured_logging.py`
- `src/codex_ml/config/__init__.py`
- `src/codex_ml/data/hf_datasets.py`
- `src/codex_ml/data/split_utils.py`
- `src/codex_ml/deployment/package.py`
- `src/codex_ml/eval/eval_runner.py`
- `src/codex_ml/features/feast_compat.py`
- `src/codex_ml/hf_loader.py`
- `src/codex_ml/integrations/har_integration.py`
- `src/codex_ml/interfaces/tokenizer.py`
- `src/codex_ml/logging/unified_logger.py`
- `src/codex_ml/metrics/classification.py`
- `src/codex_ml/metrics/metric_implementations.py`
- `src/codex_ml/metrics/sinks.py`
- `src/codex_ml/models/decoder_only.py`
- `src/codex_ml/monitoring/codex_logging.py`
- `src/codex_ml/monitoring/prometheus.py`
- `src/codex_ml/monitoring/prometheus_metrics.py`
- `src/codex_ml/pipeline.py`
- `src/codex_ml/safety/filters.py`
- `src/codex_ml/safety/sanitizers.py`
- `src/codex_ml/serving/ab_testing_harness.py`
- `src/codex_ml/serving/inference_server.py`
- `src/codex_ml/serving/monitoring.py`
- `src/codex_ml/tokenization/adapter.py`
- `src/codex_ml/tracking/writers.py`
- `src/codex_ml/train_loop.py`
- `src/codex_ml/training/fsdp_wrapper.py`
- `src/codex_ml/training/strategies.py`
- `src/codex_ml/utils/__init__.py`
- `src/codex_ml/utils/checkpoint_manager.py`
- `src/codex_ml/utils/checkpointing.py`
- `src/codex_ml/utils/config_loader.py`
- `src/codex_ml/utils/retention.py`
- `src/codex_ml/utils/safe_pickle.py`
- `src/codex_ml/workflow/track_c_workflow.py`
- `src/cognitive_brain/agents/cognitive_interface.py`
- `src/ingestion/utils.py`
- `src/mcp/AGENTS.md`
- `src/orchestration/governance/drift_detection.py`
- `src/orchestration/governance/replay_verification.py`
- `src/orchestration/healing/action_executor.py`
- `src/orchestration/healing/validation_loop.py`
- `src/orchestration/simulation.py`
- `src/quantum/orchestrator.py`
- `src/restore_pipeline/config.py`
- `src/security/logging.py`
- `src/security/security_hardening.py`
- `src/services/api/main.py`
- `src/services/ita/app/git_ops.py`
- `src/services/ita/app/security.py`
- `src/services/msp_gateway/middleware/rate_limit.py`
- `src/services/msp_gateway/middleware/tenant_context.py`
- `src/services/msp_gateway/providers/retrieval_adapter.py`
- `src/services/msp_gateway/routers/admin.py`
- `src/services/msp_gateway/routers/infer.py`
- `src/services/msp_gateway/routers/kb.py`
- `src/services/msp_gateway/security.py`
- `src/services/workflow/inventory.py`
- `src/tools/apply_container_api.py`
- `src/tools/apply_hydra_scaffold.py`
- `src/tools/apply_interfaces.py`
- `src/tools/apply_mlflow_tracking.py`
- `src/tools/apply_stack_polish.py`
- `src/tools/codex_agents_workflow.py`
- `src/tools/codex_apply_modeling_monitoring_api.py`
- `src/tools/codex_coverage_booster.py`
- `src/tools/codex_data_audit.py`
- `src/tools/codex_dataset_index.py`
- `src/tools/codex_dep_pin_check.py`
- `src/tools/codex_exec.py`
- `src/tools/codex_experiment_index.py`
- `src/tools/codex_local_gate_runner.py`
- `src/tools/codex_logging_workflow.py`
- `src/tools/codex_make_smoke_tests.py`
- `src/tools/codex_patch_exec.py`
- `src/tools/codex_precommit_bootstrap.py`
- `src/tools/codex_secret_scan.py`
- `src/tools/codex_secret_scan_stub.py`
- `src/tools/codex_session_logging_workflow.py`
- `src/tools/codex_task_runner.py`
- `src/tools/docs_agent/agent_execution_standard.py`
- `src/tools/docs_agent/inventory.py`
- `src/tools/dupinv/ast_detector.py`
- `src/tools/dupinv/ast_parsers/python_parser.py`
- `src/tools/dupinv/core.py`
- `src/tools/dupinv/exact_detector.py`
- `src/tools/dupinv/git_metadata.py`
- `src/tools/dupinv/normalize.py`
- `src/tools/dupinv/output.py`
- `src/tools/dupinv/semantic_detector.py`
- `src/tools/dupinv/shim_integration.py`
- `src/tools/ml_predictor.py`
- `src/tools/modernization_scanner_v2.py`
- `src/tools/patch_apply.py`
- `src/tools/run_supplied_task.py`
- `src/tools/selection_report.py`
- `src/tools/status/generate_status_update.py`
- `tests/agents/test_autonomous_runner.py`
- `tests/agents/test_brain_client.py`
- `tests/agents/test_edge_cases_exception_paths.py`
- `tests/agents/test_harness.py`
- `tests/agents/test_import_migration_orchestrator.py`
- `tests/agents/test_load_and_concurrent.py`
- `tests/agents/test_memory_connection_lifetime.py`
- `tests/agents/test_phase2_deep_coverage_batch4.py`
- `tests/agents/test_phase2_deep_coverage_batch5.py`
- `tests/agents/test_quality.py`
- `tests/agents/test_quantum_game_core_flows.py`
- `tests/agents/test_round3_agent_type_contracts.py`
- `tests/agents/test_variable_management.py`
- `tests/api/test_auth_email_validation.py`
- `tests/api/test_auth_exception_identity.py`
- `tests/api/test_http_status_codes_phase7a.py`
- `tests/api/test_request_validation_phase7a.py`
- `tests/ast_adapters/test_python_adapter.py`
- `tests/branch_coverage/test_branch_coverage_utils.py`
- `tests/ci/test_agent_bootstrap_runtime.py`
- `tests/ci/test_agent_instruction_contract.py`
- `tests/ci/test_fetch_lfs_assets.py`
- `tests/ci/test_mypy_baseline_gate.py`
- `tests/ci/test_session_wrapup_autofix.py`
- `tests/codex/test_ingest_phase9_1.py`
- `tests/codex_ml/ast/core/test_config.py`
- `tests/codex_ml/test_data_comprehensive.py`
- `tests/codex_ml/test_metrics_comprehensive.py`
- `tests/codex_ml/test_optional_backend_contracts.py`
- `tests/codex_ml/test_train_loop_comprehensive.py`
- `tests/codex_ml/test_training_helper_import_contracts.py`
- `tests/codex_ml/test_training_initialization_contracts.py`
- `tests/conftest.py`
- `tests/docs_agent/test_schemas.py`
- `tests/github/test_mcp_poster.py`
- `tests/integration/test_phase9_2_cognitive_brain.py`
- `tests/patterns/test_phase_19_expansion.py`
- `tests/release/test_pypi_publish_workflow.py`
- `tests/safety/test_sanitizers_comprehensive.py`
- `tests/scaling/test_rbac_1000.py`
- `tests/scaling/test_rbac_custom_grants.py`
- `tests/scripts/test_ci_top5.py`
- `tests/scripts/test_session_preload.py`
- `tests/security/test_decorators_comprehensive.py`
- `tests/security/test_gap_coverage_phase_16.py`
- `tests/security/test_security_core_comprehensive.py`
- `tests/security/test_storage_comprehensive.py`
- `tests/security/test_token_rotation_comprehensive.py`
- `tests/services/msp_gateway/test_rate_limit_middleware_extra.py`
- `tests/services/workflow/test_parser_comprehensive.py`
- `tests/smoke/test_install.py`
- `tests/space_traversal/test_peft_comprehensive/test_functional_training_main.py`
- `tests/src/test_core_pipeline_complete.py`
- `tests/templates/test_cli_template.py`
- `tests/test_advanced_indexing.py`
- `tests/test_chronicle_analytics.py`
- `tests/test_chronicle_cost.py`
- `tests/test_cli_lazy_imports.py`
- `tests/test_code_quality_fixes.py`
- `tests/test_config_loader.py`
- `tests/test_core_cli_typing_regressions.py`
- `tests/test_dependency_shadow_guard.py`
- `tests/test_edge_cases_comprehensive.py`
- `tests/test_edge_cases_day2_batch1.py`
- `tests/test_edge_cases_ml_modules.py`
- `tests/test_edge_cases_validation_serialization.py`
- `tests/test_governance_approval_service.py`
- `tests/test_normalize.py`
- `tests/test_package_dependency_contract.py`
- `tests/test_phase7b_gap_fill_batch2.py`
- `tests/test_phase7b_gap_fill_batch3.py`
- `tests/test_source_package_layout.py`
- `tests/test_text.py`
- `tests/test_train_loop.py`
- `tests/tools/test_codex_local_gate_and_experiment_index.py`
- `tests/tools/test_doc_metrics_sync.py`
- `tests/tools/test_round3_status_types.py`
- `tests/tools/test_tool_typing_contracts.py`
- `tests/unit/test_comparator_phase1a.py`
- `tests/unit/test_ingest_adapter_phase1a.py`
- `tests/unit/test_phase_9_1_decisions.py`
- `tools/github/app_token.py`
- `tools/github/gh_api.py`
- `uv.lock`
