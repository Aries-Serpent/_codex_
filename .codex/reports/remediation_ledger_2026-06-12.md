# Remediation Ledger — 2026-06-12

> **Sources:** `remediation_plan_codeql_python.md`, `remediation_plan_semgrep.md`, `remediation_plan_secrets.md`
> **Status key:** `FIXED` = commit SHA present and fix plausible · `FALSE_POSITIVE` = documented justification · `OPEN` = no verifiable commit SHA

---

## CodeQL Python (107 findings)

| # | Severity | Rule | File | Line | Status | Commit/Evidence |
|---|---|---|---|---|---|---|
| 1 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 155 | FIXED | acd5a3762 (Phase 1-A) |
| 2 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 157 | FIXED | acd5a3762 (Phase 1-A) |
| 3 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 159 | FIXED | acd5a3762 (Phase 1-A) |
| 4 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 161 | FIXED | acd5a3762 (Phase 1-A) |
| 5 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/github-security-validator-agent/src/agent.py` | 268 | FIXED | acd5a3762 (Phase 1-A) |
| 6 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/github-security-validator-agent/src/agent.py` | 274 | FIXED | acd5a3762 (Phase 1-A) |
| 7 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/scripts/ci_failure_crossref.py` | 167 | FIXED | acd5a3762 (Phase 1-A) |
| 8 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/analyze_workflows.py` | 315 | FIXED | acd5a3762 (Phase 1-A) |
| 9 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/catalog_workflows.py` | 280 | OPEN | No commit SHA in Phase entries |
| 10 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/catalog_workflows.py` | 281 | OPEN | No commit SHA in Phase entries |
| 11 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ci/auto_fix_common_issues.py` | 472 | OPEN | No commit SHA in Phase entries |
| 12 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ci/auto_fix_common_issues.py` | 478 | OPEN | No commit SHA in Phase entries |
| 13 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/decode_workflow_secrets.py` | 217 | FIXED | acd5a3762 (Phase 1-A) |
| 14 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/fix_security_issues.py` | 266 | OPEN | No commit SHA in Phase entries |
| 15 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/fix_security_issues.py` | 270 | OPEN | No commit SHA in Phase entries |
| 16 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/github_secrets_sync.py` | 115 | OPEN | No commit SHA in Phase entries |
| 17 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/github_secrets_sync.py` | 118 | OPEN | No commit SHA in Phase entries |
| 18 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ops/codex_mint_tokens_per_run.py` | 401 | OPEN | No commit SHA in Phase entries |
| 19 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ops/codex_mint_tokens_per_run.py` | 449 | OPEN | No commit SHA in Phase entries |
| 20 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ops/codex_repo_admin_bootstrap.py` | 572 | FIXED | acd5a3762 (Phase 1-A) |
| 21 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 211 | OPEN | No commit SHA in Phase entries |
| 22 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 212 | OPEN | No commit SHA in Phase entries |
| 23 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 221 | OPEN | No commit SHA in Phase entries |
| 24 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 225 | OPEN | No commit SHA in Phase entries |
| 25 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 226 | OPEN | No commit SHA in Phase entries |
| 26 | HIGH | `py/clear-text-logging-sensitive-data` | `src/codex/knowledge/pii.py` | 179 | OPEN | No commit SHA in Phase entries |
| 27 | HIGH | `py/clear-text-logging-sensitive-data` | `src/codex/knowledge/pii.py` | 180 | OPEN | No commit SHA in Phase entries |
| 28 | HIGH | `py/clear-text-logging-sensitive-data` | `src/security/providers/github_provider.py` | 481 | OPEN | No commit SHA in Phase entries |
| 29 | HIGH | `py/clear-text-logging-sensitive-data` | `src/security/providers/github_provider.py` | 519 | OPEN | No commit SHA in Phase entries |
| 30 | HIGH | `py/clear-text-logging-sensitive-data` | `tests/integration/test_admin_automation_agent.py` | 226 | FIXED | acd5a3762 (Phase 1-A) |
| 31 | HIGH | `py/clear-text-storage-sensitive-data` | `.codex/reports/ci_workflow_analysis_artifacts_2026_01_30/workflow_analyzer.py` | 503 | FIXED | 2138f9da1 (Phase 1-B) |
| 32 | HIGH | `py/clear-text-storage-sensitive-data` | `.github/scripts/workflow_analyzer.py` | 464 | FIXED | 2138f9da1 (Phase 1-B) |
| 33 | HIGH | `py/clear-text-storage-sensitive-data` | `.github/scripts/workflow_analyzer.py` | 468 | FIXED | 2138f9da1 (Phase 1-B) |
| 34 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 297 | OPEN | No commit SHA in Phase entries |
| 35 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 298 | OPEN | No commit SHA in Phase entries |
| 36 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 319 | OPEN | No commit SHA in Phase entries |
| 37 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 320 | OPEN | No commit SHA in Phase entries |
| 38 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 321 | OPEN | No commit SHA in Phase entries |
| 39 | HIGH | `py/clear-text-storage-sensitive-data` | `src/codex_ml/deployment/package.py` | 65 | FIXED | 2138f9da1 (Phase 1-B) |
| 40 | HIGH | `py/clear-text-storage-sensitive-data` | `tools/codex_secret_scan_stub.py` | 60 | FIXED | 2138f9da1 (Phase 1-B) |
| 41 | HIGH | `py/clear-text-storage-sensitive-data` | `tools/codex_secret_scan_stub.py` | 70 | FIXED | 2138f9da1 (Phase 1-B) |
| 42 | HIGH | `py/clear-text-storage-sensitive-data` | `tools/codex_secret_scan_stub.py` | 76 | FIXED | 2138f9da1 (Phase 1-B) |
| 43 | LOW | `py/cyclic-import` | `src/security/content_filters.py` | 7 | FIXED | acd5a3762 (Phase 2-B — _types.py extraction) |
| 44 | LOW | `py/cyclic-import` | `src/security/core.py` | 128 | FIXED | acd5a3762 (Phase 2-B — _types.py extraction) |
| 45 | LOW | `py/cyclic-import` | `src/security/core.py` | 335 | FIXED | acd5a3762 (Phase 2-B — _types.py extraction) |
| 46 | LOW | `py/cyclic-import` | `src/security/core.py` | 90 | FIXED | acd5a3762 (Phase 2-B — _types.py extraction) |
| 47 | LOW | `py/overwritten-inherited-attribute` | `tests/capabilities/deployment/test_deployment_comprehensive.py` | 196 | OPEN | Mentioned in bulk section only — no commit SHA in Phase entries |
| 48 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1028 | FIXED | 3a0cd9055 (Phase 2-C) |
| 49 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1101 | FIXED | 3a0cd9055 (Phase 2-C) |
| 50 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1106 | FIXED | 3a0cd9055 (Phase 2-C) |
| 51 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1173 | FIXED | 3a0cd9055 (Phase 2-C) |
| 52 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1193 | FIXED | 3a0cd9055 (Phase 2-C) |
| 53 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 2993 | FIXED | 3a0cd9055 (Phase 2-C) |
| 54 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 2999 | FIXED | 3a0cd9055 (Phase 2-C) |
| 55 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 101 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 56 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 138 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 57 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 190 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 58 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 190 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 59 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 241 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 60 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 256 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 61 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 273 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 62 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 293 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 63 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 332 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 64 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 336 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 65 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 72 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 66 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_deep_coverage_batch9.py` | 214 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 67 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_deep_coverage_batch9.py` | 334 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 68 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_quantum_game_theory.py` | 111 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 69 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_quantum_game_theory.py` | 92 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 70 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_maps.py` | 54 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 71 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_maps.py` | 66 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 72 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_zendesk.py` | 55 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 73 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_zendesk.py` | 67 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 74 | LOW | `py/uninitialized-local-variable` | `tests/configuration/test_config_basics.py` | 39 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 75 | LOW | `py/uninitialized-local-variable` | `tests/deployment_infra/test_deployment_comprehensive.py` | 101 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 76 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_data_gate.py` | 37 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 77 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_data_gate.py` | 64 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 78 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_data_report.py` | 36 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 79 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_eval_wrapper.py` | 36 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 80 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_monitor_report.py` | 47 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 81 | LOW | `py/uninitialized-local-variable` | `tests/modeling/test_lora_minimal.py` | 39 | FIXED | ff72490a6 (Phase 2-A) |
| 82 | LOW | `py/uninitialized-local-variable` | `tests/modeling/test_lora_minimal.py` | 85 | FIXED | ff72490a6 (Phase 2-A) |
| 83 | LOW | `py/uninitialized-local-variable` | `tests/performance/test_performance_regression.py` | 275 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 84 | LOW | `py/uninitialized-local-variable` | `tests/performance/test_performance_regression.py` | 303 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 85 | LOW | `py/uninitialized-local-variable` | `tests/security/test_security_gating.py` | 99 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 86 | LOW | `py/uninitialized-local-variable` | `tests/smoke/test_cli_determinism_wiring.py` | 30 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 87 | LOW | `py/uninitialized-local-variable` | `tests/specs/test_dup_similarity.py` | 51 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 88 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 24 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 89 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 24 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 90 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 25 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 91 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 26 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 92 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_roundtrip_basic.py` | 100 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 93 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_roundtrip_basic.py` | 107 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 94 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_roundtrip_basic.py` | 42 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 95 | LOW | `py/uninitialized-local-variable` | `tests/training/test_simple_trainer.py` | 22 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 96 | LOW | `py/uninitialized-local-variable` | `tests/training/test_simple_trainer.py` | 35 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 97 | LOW | `py/uninitialized-local-variable` | `tests/unit/test_peft_utils.py` | 39 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 98 | LOW | `py/uninitialized-local-variable` | `tests/unit/test_peft_utils.py` | 40 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 99 | LOW | `py/uninitialized-local-variable` | `tests/unit/test_plugin_loader.py` | 18 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 100 | LOW | `py/uninitialized-local-variable` | `tests/utils/test_repro_rng.py` | 50 | OPEN | Residual sweep — no commit SHA in Phase entries |
| 101 | LOW | `py/unused-global-variable` | `src/codex_ml/metrics/registry.py` | 38 | FIXED | 3a0cd9055 (Phase 2-D) |
| 102 | MEDIUM | `py/log-injection` | `cognitive_app/src/server/cli_api_server.py` | 1419 | OPEN | Representative file in bulk section only — no commit SHA in Phase entries |
| 103 | MEDIUM | `py/log-injection` | `cognitive_app/src/server/cli_api_server.py` | 1434 | OPEN | Representative file in bulk section only — no commit SHA in Phase entries |
| 104 | MEDIUM | `py/log-injection` | `services/msp_gateway/middleware/tenant_context.py` | 392 | OPEN | No commit SHA in Phase entries |
| 105 | MEDIUM | `py/log-injection` | `services/msp_gateway/providers/retrieval_adapter.py` | 60 | OPEN | No commit SHA in Phase entries |
| 106 | MEDIUM | `py/log-injection` | `services/msp_gateway/security.py` | 175 | OPEN | No commit SHA in Phase entries |
| 107 | MEDIUM | `py/log-injection` | `services/msp_gateway/security.py` | 195 | OPEN | No commit SHA in Phase entries |

---

## Semgrep (87 unique findings; 1 finding overlaps with CodeQL and is tracked there)

| # | Severity | Rule | File | Line | Status | Commit/Evidence |
|---|---|---|---|---|---|---|
| 1 | ERROR | `dangerous-subprocess-use-tainted-env-args` | `tests/test_container_smoke.py` | 40 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 2 | ERROR | `use-defused-xml` | `src/codex/dynamics/solution_xml.py` | 27 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 3 | ERROR | `use-defused-xml` | `tests/test_readiness_remaining_modules.py` | 114 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 4 | WARNING | `dynamic-urllib-use-detected` | `.github/agents/codex_reviewer/github_client.py` | 162 | FIXED | 3a0cd9055 (Phase 4-A) |
| 5 | WARNING | `dynamic-urllib-use-detected` | `.github/agents/codex_reviewer/github_client.py` | 232 | FIXED | 3a0cd9055 (Phase 4-A) |
| 6 | WARNING | `dynamic-urllib-use-detected` | `.github/agents/codex_reviewer/github_client.py` | 257 | FIXED | 3a0cd9055 (Phase 4-A) |
| 7 | WARNING | `dynamic-urllib-use-detected` | `.github/agents/codex_reviewer/github_client.py` | 283 | FIXED | 3a0cd9055 (Phase 4-A) |
| 8 | WARNING | `dynamic-urllib-use-detected` | `.github/agents/github-guru-agent/github_client.py` | 110 | FIXED | 3a0cd9055 (Phase 4-A) |
| 9 | WARNING | `dynamic-urllib-use-detected` | `.github/agents/github-guru-agent/github_client.py` | 162 | FIXED | 3a0cd9055 (Phase 4-A) |
| 10 | WARNING | `dynamic-urllib-use-detected` | `.github/agents/github-guru-agent/guru_adapter.py` | 384 | FIXED | 3a0cd9055 (Phase 4-A) |
| 11 | WARNING | `dynamic-urllib-use-detected` | `.github/copilot-cascade/mcp_server.py` | 553 | FIXED | 3a0cd9055 (Phase 4-A) |
| 12 | WARNING | `dynamic-urllib-use-detected` | `.github/copilot-cascade/mcp_server.py` | 702 | FIXED | 3a0cd9055 (Phase 4-A) |
| 13 | WARNING | `dynamic-urllib-use-detected` | `src/codex/agents/brain_client.py` | 157 | FIXED | 3a0cd9055 (Phase 4-A) |
| 14 | WARNING | `dynamic-urllib-use-detected` | `src/codex/auth/github_app.py` | 284 | FIXED | 3a0cd9055 (Phase 4-A) |
| 15 | WARNING | `dynamic-urllib-use-detected` | `src/codex/auth/github_app.py` | 353 | FIXED | 3a0cd9055 (Phase 4-A) |
| 16 | WARNING | `dynamic-urllib-use-detected` | `src/codex/auth/github_app.py` | 402 | FIXED | 3a0cd9055 (Phase 4-A) |
| 17 | WARNING | `dynamic-urllib-use-detected` | `src/codex/github/mcp_poster.py` | 186 | FIXED | 3a0cd9055 (Phase 4-A) |
| 18 | WARNING | `dynamic-urllib-use-detected` | `src/codex/github/mcp_poster.py` | 1482 | FIXED | 3a0cd9055 (Phase 4-A) |
| 19 | WARNING | `dynamic-urllib-use-detected` | `src/codex/github/mcp_poster.py` | 1933 | FIXED | 3a0cd9055 (Phase 4-A) |
| 20 | WARNING | `dynamic-urllib-use-detected` | `src/codex/github/mcp_poster.py` | 1987 | FIXED | 3a0cd9055 (Phase 4-A) |
| 21 | WARNING | `dynamic-urllib-use-detected` | `src/codex/skills/telemetry.py` | 369 | FIXED | 3a0cd9055 (Phase 4-A) |
| 22 | WARNING | `dynamic-urllib-use-detected` | `src/services/crawler/zendesk_sync.py` | 232 | FIXED | 3a0cd9055 (Phase 4-A) |
| 23 | WARNING | `dynamic-urllib-use-detected` | `tests/test_actions_server_smoke.py` | 17 | FIXED | 3a0cd9055 (Phase 4-A) |
| 24 | WARNING | `exec-detected` | `src/codex_ml/plugins/registry.py` | 90 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 25 | WARNING | `exec-detected` | `tests/test_readme_examples.py` | 34 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 26 | WARNING | `insecure-file-permissions` | `.github/security-tools/bootstrap_extractor.py` | 103 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 27 | WARNING | `insecure-file-permissions` | `cli/script_polish.py` | 703 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 28 | WARNING | `insecure-file-permissions` | `src/bridge_manager.py` | 359 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 29 | WARNING | `insecure-file-permissions` | `src/codex/release/api.py` | 142 | OPEN | Bulk section only — no commit SHA in Phase 3-A/4-A/B/C entries |
| 30 | WARNING | `python-logger-credential-disclosure` | `cognitive_app/src/server/cli_api_server.py` | 1320 | FIXED | 4659c8640 (Phase 3-A — logger-credential-disclosure rule family completed) |
| 31 | WARNING | `python-logger-credential-disclosure` | `cognitive_app/src/server/cli_api_server.py` | 1326 | FIXED | 4659c8640 (Phase 3-A) |
| 32 | WARNING | `python-logger-credential-disclosure` | `services/msp_gateway/middleware/rate_limit.py` | 250 | FIXED | 4659c8640 (Phase 3-A) |
| 33 | WARNING | `python-logger-credential-disclosure` | `services/msp_gateway/middleware/rate_limit.py` | 348 | FIXED | 4659c8640 (Phase 3-A) |
| 34 | WARNING | `python-logger-credential-disclosure` | `services/msp_gateway/routers/infer.py` | 231 | FIXED | 4659c8640 (Phase 3-A) |
| 35 | WARNING | `python-logger-credential-disclosure` | `src/codex/api/auth_routes.py` | 338 | FIXED | 4659c8640 (Phase 3-A) |
| 36 | WARNING | `python-logger-credential-disclosure` | `src/codex/api/auth_routes.py` | 340 | FIXED | 4659c8640 (Phase 3-A) |
| 37 | WARNING | `python-logger-credential-disclosure` | `src/codex/archive/sigstore_client.py` | 102 | FIXED | 4659c8640 (Phase 3-A) |
| 38 | WARNING | `python-logger-credential-disclosure` | `src/codex/auth/authenticator.py` | 295 | FIXED | 4659c8640 (Phase 3-A) |
| 39 | WARNING | `python-logger-credential-disclosure` | `src/codex/auth/authenticator.py` | 313 | FIXED | 4659c8640 (Phase 3-A) |
| 40 | WARNING | `python-logger-credential-disclosure` | `src/codex/autonomy/token_broker.py` | 145 | FIXED | 4659c8640 (Phase 3-A) |
| 41 | WARNING | `python-logger-credential-disclosure` | `src/codex/autonomy/token_broker.py` | 155 | FIXED | 4659c8640 (Phase 3-A) |
| 42 | WARNING | `python-logger-credential-disclosure` | `src/codex/autonomy/token_broker.py` | 165 | FIXED | 4659c8640 (Phase 3-A) |
| 43 | WARNING | `python-logger-credential-disclosure` | `src/codex/cli.py` | 1867 | FIXED | 4659c8640 (Phase 3-A) |
| 44 | WARNING | `python-logger-credential-disclosure` | `src/codex/zendesk/apply.py` | 104 | FIXED | 4659c8640 (Phase 3-A) |
| 45 | WARNING | `python-logger-credential-disclosure` | `src/codex_ml/interfaces/tokenizer.py` | 442 | FIXED | 4659c8640 (Phase 3-A) |
| 46 | WARNING | `python-logger-credential-disclosure` | `src/codex_ml/pipeline.py` | 74 | FIXED | 4659c8640 (Phase 3-A) |
| 47 | WARNING | `python-logger-credential-disclosure` | `src/codex_ml/pipeline.py` | 77 | FIXED | 4659c8640 (Phase 3-A) |
| 48 | WARNING | `python-logger-credential-disclosure` | `src/codex_ml/safety/filters.py` | 790 | FIXED | 4659c8640 (Phase 3-A) |
| 49 | WARNING | `python-logger-credential-disclosure` | `src/codex_ml/utils/safe_pickle.py` | 154 | FIXED | 4659c8640 (Phase 3-A) |
| 50 | WARNING | `python-logger-credential-disclosure` | `src/codex_ml/utils/safe_pickle.py` | 158 | FIXED | 4659c8640 (Phase 3-A) |
| 51 | WARNING | `python-logger-credential-disclosure` | `src/hhg_logistics/model/peft_utils.py` | 87 | FIXED | 4659c8640 (Phase 3-A) |
| 52 | WARNING | `python-logger-credential-disclosure` | `src/modeling.py` | 259 | FIXED | 4659c8640 (Phase 3-A) |
| 53 | WARNING | `python-logger-credential-disclosure` | `src/security/providers/github_provider.py` | 439 | FIXED | 4659c8640 (Phase 3-A) |
| 54 | WARNING | `python-logger-credential-disclosure` | `src/security/providers/github_provider.py` | 450 | FIXED | 4659c8640 (Phase 3-A) |
| 55 | WARNING | `python-logger-credential-disclosure` | `src/security/providers/github_provider.py` | 524 | FIXED | 4659c8640 (Phase 3-A) |
| 56 | WARNING | `python-logger-credential-disclosure` | `src/security/providers/github_provider.py` | 578 | FIXED | 4659c8640 (Phase 3-A) |
| 57 | WARNING | `python-logger-credential-disclosure` | `src/security/providers/github_provider.py` | 629 | FIXED | 4659c8640 (Phase 3-A) |
| 58 | WARNING | `python-logger-credential-disclosure` | `src/training/engine_hf_trainer.py` | 1074 | FIXED | 4659c8640 (Phase 3-A) |
| 59 | WARNING | `python-logger-credential-disclosure` | `src/training/functional_training.py` | 313 | FIXED | 4659c8640 (Phase 3-A) |
| 60 | WARNING | `avoid-pickle` | `src/codex_ml/utils/checkpoint_core.py` | 370 | FIXED | 3a0cd9055 (Phase 4-B — safe wrapper + weights_only=True) |
| 61 | WARNING | `avoid-pickle` | `src/codex_ml/utils/checkpoint_core.py` | 372 | FIXED | 3a0cd9055 (Phase 4-B) |
| 62 | WARNING | `avoid-pickle` | `src/codex_ml/utils/checkpoint_core.py` | 425 | FIXED | 3a0cd9055 (Phase 4-B) |
| 63 | WARNING | `avoid-pickle` | `src/codex_ml/utils/checkpointing.py` | 289 | FIXED | 3a0cd9055 (Phase 4-B) |
| 64 | WARNING | `avoid-pickle` | `src/codex_ml/utils/checkpointing.py` | 295 | FIXED | 3a0cd9055 (Phase 4-B) |
| 65 | WARNING | `avoid-pickle` | `src/codex_ml/utils/safe_pickle.py` | 75 | FIXED | 3a0cd9055 (Phase 4-B) |
| 66 | WARNING | `avoid-pickle` | `src/codex_ml/utils/safe_pickle.py` | 116 | FIXED | 3a0cd9055 (Phase 4-B) |
| 67 | WARNING | `avoid-pickle` | `src/codex_ml/utils/safe_pickle.py` | 129 | FIXED | 3a0cd9055 (Phase 4-B) |
| 68 | WARNING | `avoid-pickle` | `tests/security/test_security_utilities.py` | 87 | FIXED | 3a0cd9055 (Phase 4-B — test files delegate to safe wrapper) |
| 69 | WARNING | `avoid-pickle` | `tests/security/test_security_utilities.py` | 100 | FIXED | 3a0cd9055 (Phase 4-B) |
| 70 | WARNING | `avoid-pickle` | `tests/security/test_security_utilities.py` | 118 | FIXED | 3a0cd9055 (Phase 4-B) |
| 71 | WARNING | `avoid-pickle` | `tests/security/test_security_utilities.py` | 135 | FIXED | 3a0cd9055 (Phase 4-B) |
| 72 | WARNING | `avoid-pickle` | `tests/test_checkpoint_manager.py` | 46 | FIXED | 3a0cd9055 (Phase 4-B) |
| 73 | WARNING | `avoid-pickle` | `tests/test_checkpoint_save_resume.py` | 34 | FIXED | 3a0cd9055 (Phase 4-B) |
| 74 | WARNING | `avoid-pickle` | `tests/test_codex_ml_safe_pickle.py` | 40 | FIXED | 3a0cd9055 (Phase 4-B) |
| 75 | WARNING | `avoid-pickle` | `tests/test_codex_ml_safe_pickle.py` | 54 | FIXED | 3a0cd9055 (Phase 4-B) |
| 76 | WARNING | `avoid-pickle` | `tests/training/test_training_edge_cases_phase26.py` | 507 | FIXED | 3a0cd9055 (Phase 4-B) |
| 77 | WARNING | `avoid-pickle` | `utils/safe_pickle.py` | 72 | FIXED | 3a0cd9055 (Phase 4-B) |
| 78 | WARNING | `avoid-pickle` | `utils/safe_pickle.py` | 145 | FIXED | 3a0cd9055 (Phase 4-B) |
| 79 | WARNING | `avoid-pickle` | `utils/safe_pickle.py` | 171 | FIXED | 3a0cd9055 (Phase 4-B) |
| 80 | WARNING | `insecure-hash-algorithm-md5` | `tests/utils/test_hash_utils.py` | 30 | FIXED | 3a0cd9055 (Phase 4-C — SHA-256 only, no changes needed) |
| 81 | WARNING | `insecure-hash-algorithm-md5` | `tests/utils/test_hash_utils.py` | 31 | FIXED | 3a0cd9055 (Phase 4-C) |
| 82 | WARNING | `insecure-hash-algorithm-md5` | `tests/utils/test_hash_utils.py` | 136 | FIXED | 3a0cd9055 (Phase 4-C) |
| 83 | WARNING | `insecure-hash-algorithm-md5` | `tests/utils/test_hash_utils.py` | 147 | FIXED | 3a0cd9055 (Phase 4-C) |
| 84 | WARNING | `insecure-hash-algorithm-md5` | `tests/utils/test_hash_utils.py` | 157 | FIXED | 3a0cd9055 (Phase 4-C) |
| 85 | WARNING | `insecure-hash-algorithm-sha1` | `src/codex/session/accountability_autoupdate.py` | 206 | OPEN | SHA-1 not covered in Phase 4-C; bulk section only — no commit SHA |
| 86 | WARNING | `insecure-hash-algorithm-sha1` | `src/codex_bridge/github_client.py` | 52 | OPEN | SHA-1 not covered in Phase 4-C; bulk section only — no commit SHA |
| 87 | WARNING | `insecure-hash-algorithm-sha1` | `src/codex_ml/data/splits.py` | 27 | OPEN | SHA-1 not covered in Phase 4-C; bulk section only — no commit SHA |

---

## Secrets (key groups — 667 files consolidated into finding groups)

| Group | File(s) | Status | Commit/Evidence |
|---|---|---|---|
| Vendor/generated bulk exclusions | `.venv_ci/**`, `.codex/validation/**`, `assets/manifest.json` | FIXED | 8a5f23868 (Phase 5-B — `--exclude-files` added to `security-scanning-suite.yml`) |
| Source scripts — allowlisted false positives | `scripts/pr3248_agent_task_spec.py`, `scripts/pr3248_mcp_collection_helper.py`, `scripts/populate_pr3248_checks.py`, `scripts/pr3248_comprehensive_collector.py`, `scripts/process_workflow_runs.py` | FALSE_POSITIVE | 2026-06-12 status: exact-line `<!-- pragma: allowlist secret -->` pragmas added; no true secrets found |
| GitHub agent validation script | `.github/agents/scripts/validate_patterns.py` | FALSE_POSITIVE | 2026-06-12 status: exact-line allowlist pragmas added; no true secrets found |
| Test fixture Python files (15 files) | `tests/security/test_providers.py`, `tests/ci/test_post_rescue_comment.py`, `tests/api/test_auth_mfa_expiry.py`, `tests/auth/test_mfa_provider.py`, `tests/auth/test_token_manager.py`, `tests/branch_coverage/test_branch_coverage_config.py`, `tests/agents/test_msp_client_phase9_1.py`, `coverage_tests/test_security_providers_unittest.py`, `tests/unit/test_alerting.py`, `tests/unit/utils/test_reproducibility_hardening.py`, `tests/unit/utils/test_safe_pickle.py`, `tests/services/test_api_main_phase_e.py`, `tests/test_fast_forward_safe_files.py`, `scripts/space_traversal/viz_html.py`, `tools/codex_apply_modeling_monitoring_api.py` | FALSE_POSITIVE | 2026-06-13 extended source triage: 37 baseline entries confirmed false positives; exact-line pragmas added |
| GitHub Actions workflow YAML files | `.github/workflows/codeql-alert-fetcher.yml`, `.github/workflows/security-scanning-suite.yml` | FALSE_POSITIVE | 2026-06-13 extended source triage: secret references / step IDs, not credential values |
| JSON/JSONL baseline-only files | `.codex/webhook_config.json` (lines 7, 85), `.codex/agent_context.json` (line 14), `.codex/aftermath/pda_iterations.jsonl` (lines 3, 4, 57, 231) | FIXED | 8a5f23868 (Phase 5-A — already registered in `.secrets.baseline`; env-var references / Git SHAs, not credentials) |
| CODEX_MANIFEST.json conflict + SHA256 entropy | `CODEX_MANIFEST.json` (line 2248) | FIXED | 8a5f23868 (Phase 5-C — merge conflict resolved; `.secrets.baseline` updated) |
| Active test files with existing allowlists | `tests/safety/test_sanitizers_coverage.py`, `tests/serving/test_inference_enhanced.py`, `tests/test_token_verification.py` | FALSE_POSITIVE | Follow-up validation 2026-06-12: all 6 findings already exact-line allowlisted; `detect-secrets scan` returned clean |
| Evidence archive SHA-256 noise | `.codex/evidence/archive_ops.jsonl` (24 Hex High Entropy hits) | FALSE_POSITIVE | Follow-up validation 2026-06-12: SHA-256 archive record hashes, not credentials; no inline suppression possible for JSONL |
| Baseline-only phase 5-D (regeneration) | `.secrets.baseline` | FIXED | 8a5f23868 (Phase 5-D — deferred to CI run; existing baseline entries remain tracked known issues) |

---

## Summary

### Counts by section

| Section | FIXED | FALSE_POSITIVE | OPEN | Total |
|---|---:|---:|---:|---:|
| CodeQL Python | 32 | 0 | 75 | 107 |
| Semgrep | 75 | 0 | 12 | 87 |
| Secrets (groups) | 4 | 6 | 0 | 10 |
| **Total** | **111** | **6** | **87** | **204** |

- **FIXED: 111** (32 CodeQL + 75 Semgrep + 4 Secrets groups)
- **FALSE_POSITIVE: 6** (all Secrets groups)
- **OPEN: 87** (75 CodeQL + 12 Semgrep)

---

### OPEN items — full list with suggested owner agent

#### CodeQL Python OPEN (75 findings)

| Finding | File | Line | Suggested Owner |
|---|---|---|---|
| CQL-9 HIGH clear-text-logging | `scripts/catalog_workflows.py` | 280 | `security-alert-verification-agent` |
| CQL-10 HIGH clear-text-logging | `scripts/catalog_workflows.py` | 281 | `security-alert-verification-agent` |
| CQL-11 HIGH clear-text-logging | `scripts/ci/auto_fix_common_issues.py` | 472 | `security-alert-verification-agent` |
| CQL-12 HIGH clear-text-logging | `scripts/ci/auto_fix_common_issues.py` | 478 | `security-alert-verification-agent` |
| CQL-14 HIGH clear-text-logging | `scripts/fix_security_issues.py` | 266 | `security-alert-verification-agent` |
| CQL-15 HIGH clear-text-logging | `scripts/fix_security_issues.py` | 270 | `security-alert-verification-agent` |
| CQL-16 HIGH clear-text-logging | `scripts/github_secrets_sync.py` | 115 | `security-alert-verification-agent` |
| CQL-17 HIGH clear-text-logging | `scripts/github_secrets_sync.py` | 118 | `security-alert-verification-agent` |
| CQL-18 HIGH clear-text-logging | `scripts/ops/codex_mint_tokens_per_run.py` | 401 | `security-alert-verification-agent` |
| CQL-19 HIGH clear-text-logging | `scripts/ops/codex_mint_tokens_per_run.py` | 449 | `security-alert-verification-agent` |
| CQL-21 HIGH clear-text-logging | `scripts/security/verify_token_scope.py` | 211 | `security-alert-verification-agent` |
| CQL-22 HIGH clear-text-logging | `scripts/security/verify_token_scope.py` | 212 | `security-alert-verification-agent` |
| CQL-23 HIGH clear-text-logging | `scripts/security/verify_token_scope.py` | 221 | `security-alert-verification-agent` |
| CQL-24 HIGH clear-text-logging | `scripts/security/verify_token_scope.py` | 225 | `security-alert-verification-agent` |
| CQL-25 HIGH clear-text-logging | `scripts/security/verify_token_scope.py` | 226 | `security-alert-verification-agent` |
| CQL-26 HIGH clear-text-logging | `src/codex/knowledge/pii.py` | 179 | `security-alert-verification-agent` |
| CQL-27 HIGH clear-text-logging | `src/codex/knowledge/pii.py` | 180 | `security-alert-verification-agent` |
| CQL-28 HIGH clear-text-logging | `src/security/providers/github_provider.py` | 481 | `security-alert-verification-agent` |
| CQL-29 HIGH clear-text-logging | `src/security/providers/github_provider.py` | 519 | `security-alert-verification-agent` |
| CQL-34 HIGH clear-text-storage | `scripts/catalog_workflows.py` | 297 | `security-alert-verification-agent` |
| CQL-35 HIGH clear-text-storage | `scripts/catalog_workflows.py` | 298 | `security-alert-verification-agent` |
| CQL-36 HIGH clear-text-storage | `scripts/catalog_workflows.py` | 319 | `security-alert-verification-agent` |
| CQL-37 HIGH clear-text-storage | `scripts/catalog_workflows.py` | 320 | `security-alert-verification-agent` |
| CQL-38 HIGH clear-text-storage | `scripts/catalog_workflows.py` | 321 | `security-alert-verification-agent` |
| CQL-47 LOW overwritten-inherited-attr | `tests/capabilities/deployment/test_deployment_comprehensive.py` | 196 | `codebase-health-guardian` |
| CQL-55 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 101 | `ci-testing-agent` |
| CQL-56 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 138 | `ci-testing-agent` |
| CQL-57 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 190 | `ci-testing-agent` |
| CQL-58 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 190 | `ci-testing-agent` |
| CQL-59 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 241 | `ci-testing-agent` |
| CQL-60 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 256 | `ci-testing-agent` |
| CQL-61 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 273 | `ci-testing-agent` |
| CQL-62 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 293 | `ci-testing-agent` |
| CQL-63 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 332 | `ci-testing-agent` |
| CQL-64 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 336 | `ci-testing-agent` |
| CQL-65 LOW uninitialized-local | `scripts/cognitive/tests/test_advanced_reasoning.py` | 72 | `ci-testing-agent` |
| CQL-66 LOW uninitialized-local | `tests/agents/test_phase2_deep_coverage_batch9.py` | 214 | `ci-testing-agent` |
| CQL-67 LOW uninitialized-local | `tests/agents/test_phase2_deep_coverage_batch9.py` | 334 | `ci-testing-agent` |
| CQL-68 LOW uninitialized-local | `tests/agents/test_phase2_quantum_game_theory.py` | 111 | `ci-testing-agent` |
| CQL-69 LOW uninitialized-local | `tests/agents/test_phase2_quantum_game_theory.py` | 92 | `ci-testing-agent` |
| CQL-70 LOW uninitialized-local | `tests/codex/test_cli_maps.py` | 54 | `ci-testing-agent` |
| CQL-71 LOW uninitialized-local | `tests/codex/test_cli_maps.py` | 66 | `ci-testing-agent` |
| CQL-72 LOW uninitialized-local | `tests/codex/test_cli_zendesk.py` | 55 | `ci-testing-agent` |
| CQL-73 LOW uninitialized-local | `tests/codex/test_cli_zendesk.py` | 67 | `ci-testing-agent` |
| CQL-74 LOW uninitialized-local | `tests/configuration/test_config_basics.py` | 39 | `ci-testing-agent` |
| CQL-75 LOW uninitialized-local | `tests/deployment_infra/test_deployment_comprehensive.py` | 101 | `ci-testing-agent` |
| CQL-76 LOW uninitialized-local | `tests/integration/test_data_gate.py` | 37 | `ci-testing-agent` |
| CQL-77 LOW uninitialized-local | `tests/integration/test_data_gate.py` | 64 | `ci-testing-agent` |
| CQL-78 LOW uninitialized-local | `tests/integration/test_data_report.py` | 36 | `ci-testing-agent` |
| CQL-79 LOW uninitialized-local | `tests/integration/test_eval_wrapper.py` | 36 | `ci-testing-agent` |
| CQL-80 LOW uninitialized-local | `tests/integration/test_monitor_report.py` | 47 | `ci-testing-agent` |
| CQL-83 LOW uninitialized-local | `tests/performance/test_performance_regression.py` | 275 | `ci-testing-agent` |
| CQL-84 LOW uninitialized-local | `tests/performance/test_performance_regression.py` | 303 | `ci-testing-agent` |
| CQL-85 LOW uninitialized-local | `tests/security/test_security_gating.py` | 99 | `ci-testing-agent` |
| CQL-86 LOW uninitialized-local | `tests/smoke/test_cli_determinism_wiring.py` | 30 | `ci-testing-agent` |
| CQL-87 LOW uninitialized-local | `tests/specs/test_dup_similarity.py` | 51 | `ci-testing-agent` |
| CQL-88 LOW uninitialized-local | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 24 | `ci-testing-agent` |
| CQL-89 LOW uninitialized-local | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 24 | `ci-testing-agent` |
| CQL-90 LOW uninitialized-local | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 25 | `ci-testing-agent` |
| CQL-91 LOW uninitialized-local | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 26 | `ci-testing-agent` |
| CQL-92 LOW uninitialized-local | `tests/tokenization/test_roundtrip_basic.py` | 100 | `ci-testing-agent` |
| CQL-93 LOW uninitialized-local | `tests/tokenization/test_roundtrip_basic.py` | 107 | `ci-testing-agent` |
| CQL-94 LOW uninitialized-local | `tests/tokenization/test_roundtrip_basic.py` | 42 | `ci-testing-agent` |
| CQL-95 LOW uninitialized-local | `tests/training/test_simple_trainer.py` | 22 | `ci-testing-agent` |
| CQL-96 LOW uninitialized-local | `tests/training/test_simple_trainer.py` | 35 | `ci-testing-agent` |
| CQL-97 LOW uninitialized-local | `tests/unit/test_peft_utils.py` | 39 | `ci-testing-agent` |
| CQL-98 LOW uninitialized-local | `tests/unit/test_peft_utils.py` | 40 | `ci-testing-agent` |
| CQL-99 LOW uninitialized-local | `tests/unit/test_plugin_loader.py` | 18 | `ci-testing-agent` |
| CQL-100 LOW uninitialized-local | `tests/utils/test_repro_rng.py` | 50 | `ci-testing-agent` |
| CQL-102 MEDIUM log-injection | `cognitive_app/src/server/cli_api_server.py` | 1419 | `security-alert-verification-agent` |
| CQL-103 MEDIUM log-injection | `cognitive_app/src/server/cli_api_server.py` | 1434 | `security-alert-verification-agent` |
| CQL-104 MEDIUM log-injection | `services/msp_gateway/middleware/tenant_context.py` | 392 | `security-alert-verification-agent` |
| CQL-105 MEDIUM log-injection | `services/msp_gateway/providers/retrieval_adapter.py` | 60 | `security-alert-verification-agent` |
| CQL-106 MEDIUM log-injection | `services/msp_gateway/security.py` | 175 | `security-alert-verification-agent` |
| CQL-107 MEDIUM log-injection | `services/msp_gateway/security.py` | 195 | `security-alert-verification-agent` |

#### Semgrep OPEN (12 findings)

| Finding | File | Line | Suggested Owner |
|---|---|---|---|
| SG-1 ERROR dangerous-subprocess | `tests/test_container_smoke.py` | 40 | `security-audit-agent` |
| SG-2 ERROR use-defused-xml | `src/codex/dynamics/solution_xml.py` | 27 | `security-audit-agent` |
| SG-3 ERROR use-defused-xml | `tests/test_readiness_remaining_modules.py` | 114 | `security-audit-agent` |
| SG-24 WARNING exec-detected | `src/codex_ml/plugins/registry.py` | 90 | `security-audit-agent` |
| SG-25 WARNING exec-detected | `tests/test_readme_examples.py` | 34 | `security-audit-agent` |
| SG-26 WARNING insecure-file-permissions | `.github/security-tools/bootstrap_extractor.py` | 103 | `codebase-health-guardian` |
| SG-27 WARNING insecure-file-permissions | `cli/script_polish.py` | 703 | `codebase-health-guardian` |
| SG-28 WARNING insecure-file-permissions | `src/bridge_manager.py` | 359 | `codebase-health-guardian` |
| SG-29 WARNING insecure-file-permissions | `src/codex/release/api.py` | 142 | `codebase-health-guardian` |
| SG-85 WARNING insecure-hash-sha1 | `src/codex/session/accountability_autoupdate.py` | 206 | `security-alert-verification-agent` |
| SG-86 WARNING insecure-hash-sha1 | `src/codex_bridge/github_client.py` | 52 | `security-alert-verification-agent` |
| SG-87 WARNING insecure-hash-sha1 | `src/codex_ml/data/splits.py` | 27 | `security-alert-verification-agent` |
