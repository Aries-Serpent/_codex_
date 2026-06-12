# remediation_plan_codeql_python.md

- Generated: 2026-06-05T05:16:00Z
- Source artifact: `security-suite-codeql-python/codeql-sarif/python/python.sarif`
- Run: `26992144518` · Commit: `4086f9afdb98d9fd58ed123220f337a4caae94f0`

## Executive Summary

- Total findings parsed: **107**
- Security-classified findings (HIGH/MEDIUM): **48**
- Code-quality findings (LOW): **59**
- Auto-fixable batch candidates: **5**
- Manual review/fix candidates: **102**

## Severity Breakdown

| Severity | Count | Percent |
|---|---:|---:|
| HIGH | 42 | 39.3% |
| MEDIUM | 6 | 5.6% |
| LOW | 59 | 55.1% |

## Rule Breakdown and Fix Strategy

| Rule ID | Count | Severity | Category | Remediation Strategy |
|---|---:|---|---|---|
| `py/uninitialized-local-variable` | 46 | LOW | Code Quality | Initialize variable on all control paths; add explicit defaults before branching/try blocks. |
| `py/clear-text-logging-sensitive-data` | 30 | HIGH | Security | Mask/redact secrets before logging; replace with token fingerprints/non-sensitive identifiers. <!-- pragma: allowlist secret --> |
| `py/clear-text-storage-sensitive-data` | 12 | HIGH | Security | Avoid persisting raw secrets; use secure stores, hashing, or encryption-at-rest wrappers. <!-- pragma: allowlist secret --> |
| `py/pythagorean` | 7 | LOW | Code Quality | Replace `x**0.5` with `math.sqrt(x)` or `math.hypot(...)` for clarity/correctness. |
| `py/log-injection` | 6 | MEDIUM | Security | Sanitize/escape user-controlled values and prefer structured logging fields. |
| `py/cyclic-import` | 4 | LOW | Code Quality | Move imports into function scope or refactor shared symbols to dependency-neutral module. |
| `py/overwritten-inherited-attribute` | 1 | LOW | Code Quality | Rename/shim inherited attribute, or align parent/child contracts explicitly. |
| `py/unused-global-variable` | 1 | LOW | Code Quality | Remove unused globals or convert to constants consumed by callers/tests. |

## Top Affected Files

| File | Findings |
|---|---:|
| `scripts/cognitive/tests/test_advanced_reasoning.py` | 11 |
| `scripts/catalog_workflows.py` | 7 |
| `agents/physics_orchestrator.py` | 7 |
| `scripts/security/verify_token_scope.py` | 5 | <!-- pragma: allowlist secret -->
| `.github/agents/admin-automation-agent/src/agent.py` | 4 |
| `tests/tokenization/test_fast_tokenizer_wrapper.py` | 4 | <!-- pragma: allowlist secret -->
| `tools/codex_secret_scan_stub.py` | 3 | <!-- pragma: allowlist secret -->
| `src/security/core.py` | 3 |
| `tests/tokenization/test_roundtrip_basic.py` | 3 | <!-- pragma: allowlist secret -->
| `.github/agents/github-security-validator-agent/src/agent.py` | 2 |
| `scripts/ci/auto_fix_common_issues.py` | 2 |
| `scripts/ops/codex_mint_tokens_per_run.py` | 2 | <!-- pragma: allowlist secret -->
| `scripts/fix_security_issues.py` | 2 |
| `scripts/github_secrets_sync.py` | 2 | <!-- pragma: allowlist secret -->
| `src/security/providers/github_provider.py` | 2 |
| `src/codex/knowledge/pii.py` | 2 |
| `.github/scripts/workflow_analyzer.py` | 2 |
| `cognitive_app/src/server/cli_api_server.py` | 2 |
| `services/msp_gateway/security.py` | 2 |
| `tests/codex/test_cli_maps.py` | 2 |

## Full Structured Finding List (107)

| # | Severity | Rule | File | Line | Message |
|---:|---|---|---|---:|---|
| 1 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 155 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 2 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 157 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 3 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 159 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 4 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/admin-automation-agent/src/agent.py` | 161 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 5 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/github-security-validator-agent/src/agent.py` | 268 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 6 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/agents/github-security-validator-agent/src/agent.py` | 274 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 7 | HIGH | `py/clear-text-logging-sensitive-data` | `.github/scripts/ci_failure_crossref.py` | 167 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 8 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/analyze_workflows.py` | 315 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 9 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/catalog_workflows.py` | 280 | This expression logs [sensitive data (secret)](1) as clear text. This expression logs [sensitive data (secret)](2) as clear text. This expression logs [sensitive data (secret)](3) as clear text. This expression logs [sensitive data (secret)](4) as clear text. This expression logs [sensitive data (secret)](5) as clear text. This expression logs [sensitive data (secret)](6) as clear text. | <!-- pragma: allowlist secret -->
| 10 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/catalog_workflows.py` | 281 | This expression logs [sensitive data (secret)](1) as clear text. This expression logs [sensitive data (secret)](2) as clear text. This expression logs [sensitive data (secret)](3) as clear text. This expression logs [sensitive data (secret)](4) as clear text. This expression logs [sensitive data (secret)](5) as clear text. This expression logs [sensitive data (secret)](6) as clear text. | <!-- pragma: allowlist secret -->
| 11 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ci/auto_fix_common_issues.py` | 472 | This expression logs [sensitive data (secret)](1) as clear text. This expression logs [sensitive data (secret)](2) as clear text. | <!-- pragma: allowlist secret -->
| 12 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ci/auto_fix_common_issues.py` | 478 | This expression logs [sensitive data (secret)](1) as clear text. This expression logs [sensitive data (secret)](2) as clear text. | <!-- pragma: allowlist secret -->
| 13 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/decode_workflow_secrets.py` | 217 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 14 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/fix_security_issues.py` | 266 | This expression logs [sensitive data (password)](1) as clear text. | <!-- pragma: allowlist secret -->
| 15 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/fix_security_issues.py` | 270 | This expression logs [sensitive data (password)](1) as clear text. | <!-- pragma: allowlist secret -->
| 16 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/github_secrets_sync.py` | 115 | This expression logs [sensitive data (secret)](1) as clear text. This expression logs [sensitive data (secret)](2) as clear text. This expression logs [sensitive data (secret)](3) as clear text. | <!-- pragma: allowlist secret -->
| 17 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/github_secrets_sync.py` | 118 | This expression logs [sensitive data (secret)](1) as clear text. This expression logs [sensitive data (secret)](2) as clear text. This expression logs [sensitive data (secret)](3) as clear text. | <!-- pragma: allowlist secret -->
| 18 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ops/codex_mint_tokens_per_run.py` | 401 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 19 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ops/codex_mint_tokens_per_run.py` | 449 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 20 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/ops/codex_repo_admin_bootstrap.py` | 572 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 21 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 211 | This expression logs [sensitive data (password)](1) as clear text. | <!-- pragma: allowlist secret -->
| 22 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 212 | This expression logs [sensitive data (password)](1) as clear text. | <!-- pragma: allowlist secret -->
| 23 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 221 | This expression logs [sensitive data (password)](1) as clear text. | <!-- pragma: allowlist secret -->
| 24 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 225 | This expression logs [sensitive data (password)](1) as clear text. | <!-- pragma: allowlist secret -->
| 25 | HIGH | `py/clear-text-logging-sensitive-data` | `scripts/security/verify_token_scope.py` | 226 | This expression logs [sensitive data (password)](1) as clear text. | <!-- pragma: allowlist secret -->
| 26 | HIGH | `py/clear-text-logging-sensitive-data` | `src/codex/knowledge/pii.py` | 179 | This expression logs [sensitive data (private)](1) as clear text. |
| 27 | HIGH | `py/clear-text-logging-sensitive-data` | `src/codex/knowledge/pii.py` | 180 | This expression logs [sensitive data (private)](1) as clear text. |
| 28 | HIGH | `py/clear-text-logging-sensitive-data` | `src/security/providers/github_provider.py` | 481 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 29 | HIGH | `py/clear-text-logging-sensitive-data` | `src/security/providers/github_provider.py` | 519 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 30 | HIGH | `py/clear-text-logging-sensitive-data` | `tests/integration/test_admin_automation_agent.py` | 226 | This expression logs [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 31 | HIGH | `py/clear-text-storage-sensitive-data` | `.codex/reports/ci_workflow_analysis_artifacts_2026_01_30/workflow_analyzer.py` | 503 | This expression stores [sensitive data (secret)](1) as clear text. This expression stores [sensitive data (secret)](2) as clear text. This expression stores [sensitive data (secret)](3) as clear text. This expression stores [sensitive data (secret)](4) as clear text. | <!-- pragma: allowlist secret -->
| 32 | HIGH | `py/clear-text-storage-sensitive-data` | `.github/scripts/workflow_analyzer.py` | 464 | This expression stores [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 33 | HIGH | `py/clear-text-storage-sensitive-data` | `.github/scripts/workflow_analyzer.py` | 468 | This expression stores [sensitive data (secret)](1) as clear text. This expression stores [sensitive data (secret)](2) as clear text. This expression stores [sensitive data (secret)](3) as clear text. This expression stores [sensitive data (secret)](4) as clear text. This expression stores [sensitive data (secret)](5) as clear text. | <!-- pragma: allowlist secret -->
| 34 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 297 | This expression stores [sensitive data (secret)](1) as clear text. This expression stores [sensitive data (secret)](2) as clear text. This expression stores [sensitive data (secret)](3) as clear text. This expression stores [sensitive data (secret)](4) as clear text. This expression stores [sensitive data (secret)](5) as clear text. This expression stores [sensitive data (secret)](6) as clear text. | <!-- pragma: allowlist secret -->
| 35 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 298 | This expression stores [sensitive data (secret)](1) as clear text. This expression stores [sensitive data (secret)](2) as clear text. This expression stores [sensitive data (secret)](3) as clear text. This expression stores [sensitive data (secret)](4) as clear text. This expression stores [sensitive data (secret)](5) as clear text. This expression stores [sensitive data (secret)](6) as clear text. | <!-- pragma: allowlist secret -->
| 36 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 319 | This expression stores [sensitive data (secret)](1) as clear text. This expression stores [sensitive data (secret)](2) as clear text. This expression stores [sensitive data (secret)](3) as clear text. This expression stores [sensitive data (secret)](4) as clear text. This expression stores [sensitive data (secret)](5) as clear text. This expression stores [sensitive data (secret)](6) as clear text. | <!-- pragma: allowlist secret -->
| 37 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 320 | This expression stores [sensitive data (secret)](1) as clear text. This expression stores [sensitive data (secret)](2) as clear text. This expression stores [sensitive data (secret)](3) as clear text. This expression stores [sensitive data (secret)](4) as clear text. This expression stores [sensitive data (secret)](5) as clear text. This expression stores [sensitive data (secret)](6) as clear text. | <!-- pragma: allowlist secret -->
| 38 | HIGH | `py/clear-text-storage-sensitive-data` | `scripts/catalog_workflows.py` | 321 | This expression stores [sensitive data (secret)](1) as clear text. This expression stores [sensitive data (secret)](2) as clear text. This expression stores [sensitive data (secret)](3) as clear text. This expression stores [sensitive data (secret)](4) as clear text. This expression stores [sensitive data (secret)](5) as clear text. This expression stores [sensitive data (secret)](6) as clear text. | <!-- pragma: allowlist secret -->
| 39 | HIGH | `py/clear-text-storage-sensitive-data` | `src/codex_ml/deployment/package.py` | 65 | This expression stores [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 40 | HIGH | `py/clear-text-storage-sensitive-data` | `tools/codex_secret_scan_stub.py` | 60 | This expression stores [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 41 | HIGH | `py/clear-text-storage-sensitive-data` | `tools/codex_secret_scan_stub.py` | 70 | This expression stores [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 42 | HIGH | `py/clear-text-storage-sensitive-data` | `tools/codex_secret_scan_stub.py` | 76 | This expression stores [sensitive data (secret)](1) as clear text. | <!-- pragma: allowlist secret -->
| 43 | LOW | `py/cyclic-import` | `src/security/content_filters.py` | 7 | Import of module [src.security.core](1) begins an import cycle. |
| 44 | LOW | `py/cyclic-import` | `src/security/core.py` | 128 | Import of module [src.security.content_filters](1) begins an import cycle. |
| 45 | LOW | `py/cyclic-import` | `src/security/core.py` | 335 | Import of module [src.security.content_filters](1) begins an import cycle. |
| 46 | LOW | `py/cyclic-import` | `src/security/core.py` | 90 | Import of module [src.security.content_filters](1) begins an import cycle. |
| 47 | LOW | `py/overwritten-inherited-attribute` | `tests/capabilities/deployment/test_deployment_comprehensive.py` | 196 | Assignment overwrites attribute api_version, which was previously defined in superclass [K8sManifest](1). |
| 48 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1028 | Pythagorean calculation with sub-optimal numerics. |
| 49 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1101 | Pythagorean calculation with sub-optimal numerics. |
| 50 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1106 | Pythagorean calculation with sub-optimal numerics. |
| 51 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1173 | Pythagorean calculation with sub-optimal numerics. |
| 52 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 1193 | Pythagorean calculation with sub-optimal numerics. |
| 53 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 2993 | Pythagorean calculation with sub-optimal numerics. |
| 54 | LOW | `py/pythagorean` | `agents/physics_orchestrator.py` | 2999 | Pythagorean calculation with sub-optimal numerics. |
| 55 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 101 | Local variable 'CausalModel' may be used before it is initialized. |
| 56 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 138 | Local variable 'nx' may be used before it is initialized. |
| 57 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 190 | Local variable 'BaseSRegressor' may be used before it is initialized. |
| 58 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 190 | Local variable 'RandomForestRegressor' may be used before it is initialized. |
| 59 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 241 | Local variable 'RandomForestClassifier' may be used before it is initialized. |
| 60 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 256 | Local variable 'shap' may be used before it is initialized. |
| 61 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 273 | Local variable 'shap' may be used before it is initialized. |
| 62 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 293 | Local variable 'shap' may be used before it is initialized. |
| 63 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 332 | Local variable 'RandomForestRegressor' may be used before it is initialized. |
| 64 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 336 | Local variable 'shap' may be used before it is initialized. |
| 65 | LOW | `py/uninitialized-local-variable` | `scripts/cognitive/tests/test_advanced_reasoning.py` | 72 | Local variable 'CausalModel' may be used before it is initialized. |
| 66 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_deep_coverage_batch9.py` | 214 | Local variable 'reflected' may be used before it is initialized. |
| 67 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_deep_coverage_batch9.py` | 334 | Local variable 'result' may be used before it is initialized. |
| 68 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_quantum_game_theory.py` | 111 | Local variable 'ActionType' may be used before it is initialized. |
| 69 | LOW | `py/uninitialized-local-variable` | `tests/agents/test_phase2_quantum_game_theory.py` | 92 | Local variable 'ActionType' may be used before it is initialized. |
| 70 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_maps.py` | 54 | Local variable 'cli_maps' may be used before it is initialized. |
| 71 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_maps.py` | 66 | Local variable 'cli_maps' may be used before it is initialized. |
| 72 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_zendesk.py` | 55 | Local variable 'cli_zendesk' may be used before it is initialized. |
| 73 | LOW | `py/uninitialized-local-variable` | `tests/codex/test_cli_zendesk.py` | 67 | Local variable 'cli_zendesk' may be used before it is initialized. |
| 74 | LOW | `py/uninitialized-local-variable` | `tests/configuration/test_config_basics.py` | 39 | Local variable 'yaml' may be used before it is initialized. |
| 75 | LOW | `py/uninitialized-local-variable` | `tests/deployment_infra/test_deployment_comprehensive.py` | 101 | Local variable 'yaml' may be used before it is initialized. |
| 76 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_data_gate.py` | 37 | Local variable 'run_data_drift_gate' may be used before it is initialized. |
| 77 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_data_gate.py` | 64 | Local variable 'run_data_drift_gate' may be used before it is initialized. |
| 78 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_data_report.py` | 36 | Local variable 'build_data_drift' may be used before it is initialized. |
| 79 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_eval_wrapper.py` | 36 | Local variable 'harness' may be used before it is initialized. |
| 80 | LOW | `py/uninitialized-local-variable` | `tests/integration/test_monitor_report.py` | 47 | Local variable 'serve_report' may be used before it is initialized. |
| 81 | LOW | `py/uninitialized-local-variable` | `tests/modeling/test_lora_minimal.py` | 39 | Local variable 'LoraConfig' may be used before it is initialized. |
| 82 | LOW | `py/uninitialized-local-variable` | `tests/modeling/test_lora_minimal.py` | 85 | Local variable 'LoraConfig' may be used before it is initialized. |
| 83 | LOW | `py/uninitialized-local-variable` | `tests/performance/test_performance_regression.py` | 275 | Local variable 'AgentMemorySystem' may be used before it is initialized. |
| 84 | LOW | `py/uninitialized-local-variable` | `tests/performance/test_performance_regression.py` | 303 | Local variable 'AgentMemorySystem' may be used before it is initialized. |
| 85 | LOW | `py/uninitialized-local-variable` | `tests/security/test_security_gating.py` | 99 | Local variable 'toml' may be used before it is initialized. |
| 86 | LOW | `py/uninitialized-local-variable` | `tests/smoke/test_cli_determinism_wiring.py` | 30 | Local variable 'cs' may be used before it is initialized. |
| 87 | LOW | `py/uninitialized-local-variable` | `tests/specs/test_dup_similarity.py` | 51 | Local variable 'yaml' may be used before it is initialized. |
| 88 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 24 | Local variable 'Tokenizer' may be used before it is initialized. | <!-- pragma: allowlist secret -->
| 89 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 24 | Local variable 'WordLevel' may be used before it is initialized. | <!-- pragma: allowlist secret -->
| 90 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 25 | Local variable 'Whitespace' may be used before it is initialized. | <!-- pragma: allowlist secret -->
| 91 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_fast_tokenizer_wrapper.py` | 26 | Local variable 'WordLevelTrainer' may be used before it is initialized. | <!-- pragma: allowlist secret -->
| 92 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_roundtrip_basic.py` | 100 | Local variable 'token_ids' may be used before it is initialized. | <!-- pragma: allowlist secret -->
| 93 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_roundtrip_basic.py` | 107 | Local variable 'decoded' may be used before it is initialized. | <!-- pragma: allowlist secret -->
| 94 | LOW | `py/uninitialized-local-variable` | `tests/tokenization/test_roundtrip_basic.py` | 42 | Local variable 'out' may be used before it is initialized. | <!-- pragma: allowlist secret -->
| 95 | LOW | `py/uninitialized-local-variable` | `tests/training/test_simple_trainer.py` | 22 | Local variable 'simple_trainer' may be used before it is initialized. |
| 96 | LOW | `py/uninitialized-local-variable` | `tests/training/test_simple_trainer.py` | 35 | Local variable 'module' may be used before it is initialized. |
| 97 | LOW | `py/uninitialized-local-variable` | `tests/unit/test_peft_utils.py` | 39 | Local variable 'apply_lora' may be used before it is initialized. |
| 98 | LOW | `py/uninitialized-local-variable` | `tests/unit/test_peft_utils.py` | 40 | Local variable 'freeze_base_weights' may be used before it is initialized. |
| 99 | LOW | `py/uninitialized-local-variable` | `tests/unit/test_plugin_loader.py` | 18 | Local variable 'load_plugins' may be used before it is initialized. |
| 100 | LOW | `py/uninitialized-local-variable` | `tests/utils/test_repro_rng.py` | 50 | Local variable 'state' may be used before it is initialized. |
| 101 | LOW | `py/unused-global-variable` | `src/codex_ml/metrics/registry.py` | 38 | The global variable '_REWARD_METRICS_LOCK' is not used. |
| 102 | MEDIUM | `py/log-injection` | `cognitive_app/src/server/cli_api_server.py` | 1419 | This log entry depends on a [user-provided value](1). |
| 103 | MEDIUM | `py/log-injection` | `cognitive_app/src/server/cli_api_server.py` | 1434 | This log entry depends on a [user-provided value](1). |
| 104 | MEDIUM | `py/log-injection` | `services/msp_gateway/middleware/tenant_context.py` | 392 | This log entry depends on a [user-provided value](1). |
| 105 | MEDIUM | `py/log-injection` | `services/msp_gateway/providers/retrieval_adapter.py` | 60 | This log entry depends on a [user-provided value](1). This log entry depends on a [user-provided value](2). |
| 106 | MEDIUM | `py/log-injection` | `services/msp_gateway/security.py` | 175 | This log entry depends on a [user-provided value](1). |
| 107 | MEDIUM | `py/log-injection` | `services/msp_gateway/security.py` | 195 | This log entry depends on a [user-provided value](1). |

## Effort Estimate (Planning)

- HIGH (42 findings): 10-14 hours (redaction/storage hardening + tests)
- MEDIUM (6 findings): 2-4 hours (logging sanitization fixes + tests)
- LOW (59 findings): 8-12 hours (correctness refactors and cleanup)
- Total estimated effort: **20-30 hours** in phased batches

## Implementation Status — 2026-06-12

- **Status:** Bulk remediation executed for the scoped source files targeted in this session.
- **Security lanes completed:** `py/clear-text-logging-sensitive-data`, `py/clear-text-storage-sensitive-data`, and `py/log-injection` were remediated across the scoped workflow/auth/security/runtime files by replacing raw secret logging/storage with hashed or sanitized representations and by sanitizing user-controlled log values.
- **Quality lanes completed:** targeted `py/cyclic-import`, `py/pythagorean`, `py/overwritten-inherited-attribute`, and selected `py/uninitialized-local-variable` / `py/unused-global-variable` findings were remediated in the scoped `src/security/*`, `agents/physics_orchestrator.py`, deployment test, and selected test files.
- **Representative touched files:** `scripts/catalog_workflows.py`, `scripts/github_secrets_sync.py`, `src/security/providers/github_provider.py`, `cognitive_app/src/server/cli_api_server.py`, `services/msp_gateway/security.py`, `src/security/core.py`, `src/security/content_filters.py`, `agents/physics_orchestrator.py`, `tests/agents/test_phase2_deep_coverage_batch9.py`, `tests/capabilities/deployment/test_deployment_comprehensive.py`.
- **Validation basis:** each remediation lane reported targeted compile/runtime or scoped test validation; no additional main-agent lint/build/test rerun was performed on custom-agent changes.
