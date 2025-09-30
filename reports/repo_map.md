# Repository Map

## . (52 files)
- `.bandit.yml`
- `.coveragerc`
- `.dockerignore`
- `.env.example`
- `.gitattributes`
- `.gitignore`
- `.pre-commit-config.yaml`
- `.pre-commit-hybrid.yaml`
- `.pre-commit-ruff.yaml`
- `.secrets.baseline`
- `AUDIT_PROMPT.md`
- `CHANGELOG.md`
- `CHANGELOG_CODEX.md`
- `CHANGELOG_SESSION_LOGGING.md`
- `CODEBASE_AUDIT_2025-08-26_203612.md`
- ... (+37 more)

## .codex (171 files)
- `.codex/DO_NOT_ACTIVATE_ACTIONS.txt`
- `.codex/DO_NOT_ACTIVATE_GITHUB_ACTIONS`
- `.codex/GATES_REPORT.txt`
- `.codex/README.md`
- `.codex/README.md.bak`
- `.codex/action_log.ndjson`
- `.codex/analysis_metrics.jsonl`
- `.codex/archive/README_UPDATED.md`
- `.codex/automation_out/change_log.md`
- `.codex/automation_out/coverage_report.json`
- `.codex/automation_out/db_catalog.json`
- `.codex/automation_out/db_inventory.json`
- `.codex/change_log-large.md`
- `.codex/change_log.md`
- `.codex/change_log_compare_report.json`
- ... (+156 more)

## .github (15 files)
- `.github/CODEOWNERS`
- `.github/Copilot.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/README.md`
- `.github/_workflows_disabled/README.md`
- `.github/_workflows_disabled/_policy.yml`
- `.github/_workflows_disabled/lint.yml`
- `.github/_workflows_disabled/manual_ci.yml`
- `.github/_workflows_disabled/nightly.yml.disabled`
- `.github/_workflows_disabled/release-upload.yml`
- `.github/_workflows_disabled/vuln_scan.yml.disabled`
- `.github/copilot-instructions.md`
- `.github/docs/PoC_Repo_Layout_Copilot.md`
- `.github/workflows/ci.yml.disabled`
- `.github/workflows/validate.yml.disabled`

## LICENSES (3 files)
- `LICENSES/LICENSE`
- `LICENSES/codex-universal-image-sbom.md`
- `LICENSES/codex-universal-image-sbom.spdx.json`

## _codex (4 files)
- `_codex/status/_codex_status_update-2025-09-21.md`
- `_codex/status/_codex_status_update-2025-09-22.md`
- `_codex/status/manifest-20250922T013307Z.json`
- `_codex/status/manifest-20250922T013826Z.json`

## agents (8 files)
- `agents/codex_client/README.md`
- `agents/codex_client/codex_client/__init__.py`
- `agents/codex_client/codex_client/bridge.py`
- `agents/codex_client/codex_client/config.py`
- `agents/codex_client/codex_client/demo_plan_and_call.py`
- `agents/codex_client/codex_client/models.py`
- `agents/codex_client/pyproject.toml`
- `agents/codex_client/tests/test_config.py`

## analysis (8 files)
- `analysis/__init__.py`
- `analysis/audit_pipeline.py`
- `analysis/intuitive_aptitude.py`
- `analysis/metrics.py`
- `analysis/parsers.py`
- `analysis/providers.py`
- `analysis/registry.py`
- `analysis/tests_docs_links_audit.py`

## archive (5 files)
- `archive/removed/ci.yml`
- `archive/removed/codex-ci.yml`
- `archive/removed/codex-self-hosted-ci.yml`
- `archive/removed/codex-self-manage.yml`
- `archive/removed/release.yml`

## artifacts (33 files)
- `artifacts/.gitkeep`
- `artifacts/coverage/coverage.xml`
- `artifacts/coverage/index.html`
- `artifacts/coverage/summary.txt`
- `artifacts/diffs/training_py01_removal.md`
- `artifacts/docs_link_audit/links.json`
- `artifacts/env/hw.txt`
- `artifacts/env/os.txt`
- `artifacts/env/pip-freeze.txt`
- `artifacts/env/python.txt`
- `artifacts/gates/nox-lint.log`
- `artifacts/gates/nox-tests.log`
- `artifacts/gates/nox-tests_min-rerun.log`
- `artifacts/gates/nox-tests_min-rerun2.log`
- `artifacts/gates/nox-tests_min.log`
- ... (+18 more)

## codex_addons (2 files)
- `codex_addons/metrics/collector.py`
- `codex_addons/spectral.py`

## codex_digest (12 files)
- `codex_digest/EXECUTION.md`
- `codex_digest/README.md`
- `codex_digest/__init__.py`
- `codex_digest/cli.py`
- `codex_digest/error_capture.py`
- `codex_digest/mapper.py`
- `codex_digest/pipeline.py`
- `codex_digest/requirements.txt`
- `codex_digest/semparser.py`
- `codex_digest/tokenizer.py`
- `codex_digest/utils.py`
- `codex_digest/workflow.py`

## codex_ml (5 files)
- `codex_ml/cli/main.py`
- `codex_ml/data/checksums.py`
- `codex_ml/models/peft_hooks.py`
- `codex_ml/tracking/mlflow_utils.py`
- `codex_ml/utils/checkpointing.py`

## codex_utils (5 files)
- `codex_utils/__init__.py`
- `codex_utils/logging_setup.py`
- `codex_utils/mlflow_offline.py`
- `codex_utils/ndjson.py`
- `codex_utils/repro.py`

## conf (3 files)
- `conf/config.yaml`
- `conf/examples/config_minimal.yaml`
- `conf/trainer/base.yaml`

## configs (37 files)
- `configs/__init__.py`
- `configs/base.yaml`
- `configs/base_config.py`
- `configs/config.yaml`
- `configs/data/base.yaml`
- `configs/data/offline/tiny_corpus.yaml`
- `configs/deterministic.yaml`
- `configs/env/ubuntu.yaml`
- `configs/eval/base.yaml`
- `configs/eval/default.yaml`
- `configs/evaluate/default.yaml`
- `configs/interfaces.example.yaml`
- `configs/interfaces.yaml`
- `configs/interfaces/offline.yaml`
- `configs/logging/base.yaml`
- ... (+22 more)

## copilot (6 files)
- `copilot/app/README.md`
- `copilot/extension/.gitignore`
- `copilot/extension/README.md`
- `copilot/extension/extension_manifest.json`
- `copilot/extension/package.json`
- `copilot/extension/server/index.js`

## data (4 files)
- `data/offline/length_reward.json`
- `data/offline/tiny_corpus.txt`
- `data/offline/trainer_functional.json`
- `data/offline/weighted_accuracy.json`

## db (1 files)
- `db/schema.sql`

## deploy (3 files)
- `deploy/deploy_codex_pipeline.py`
- `deploy/helm/Chart.yaml`
- `deploy/helm/values.yaml`

## docs (119 files)
- `docs/FollowUp_Implementation_Plan.md`
- `docs/Implementation_Update_merged.md`
- `docs/README.md`
- `docs/RELEASE_CHECKLIST.md`
- `docs/SOP_CHATGPT_CODEX_PRS_LOCAL.md`
- `docs/api.md`
- `docs/architecture.md`
- `docs/architecture/interfaces.md`
- `docs/bridge/README.md`
- `docs/bridge/governance.md`
- `docs/bridge/overview.md`
- `docs/bridge/ubuntu_cli.md`
- `docs/ci.md`
- `docs/concepts.md`
- `docs/deep_research_prompts.md`
- ... (+104 more)

## documentation (16 files)
- `documentation/TOOLS.md`
- `documentation/checkpointing_README.md`
- `documentation/codex_pipeline_scaffold.md`
- `documentation/codex_setup_integration.md`
- `documentation/codex_symbolic_pipeline.py`
- `documentation/codex_symbolic_training_summary.md`
- `documentation/continuous_improvement.md`
- `documentation/deploy_codex_pipeline.md`
- `documentation/end_to_end_logging.md`
- `documentation/manual_verification_template.md`
- `documentation/option_a_sqlite.md`
- `documentation/option_b_duckdb_parquet.md`
- `documentation/option_c_datasette_lite.md`
- `documentation/safety_README.md`
- `documentation/session_hooks_shell.md`
- ... (+1 more)

## examples (19 files)
- `examples/TROUBLESHOOTING.md`
- `examples/__init__.py`
- `examples/chat_finetune.py`
- `examples/evaluate_toy.py`
- `examples/mlflow_offline.py`
- `examples/notebooks/chat_finetune.ipynb`
- `examples/notebooks/demo_infer.ipynb`
- `examples/notebooks/demo_train_eval.ipynb`
- `examples/notebooks/tokenizer_quickstart.ipynb`
- `examples/plugins/__init__.py`
- `examples/plugins/broken.py`
- `examples/plugins/toy_data_loader/__init__.py`
- `examples/plugins/toy_metric/__init__.py`
- `examples/plugins/toy_model/__init__.py`
- `examples/plugins/toy_tokenizer/__init__.py`
- ... (+4 more)

## experiments (1 files)
- `experiments/2025-01-15_smoke.md`

## hydra (2 files)
- `hydra/__init__.py`
- `hydra/errors.py`

## interfaces (2 files)
- `interfaces/__init__.py`
- `interfaces/tokenizer.py`

## logs (1 files)
- `logs/error_captures.log`

## mcp (2 files)
- `mcp/mcp.json`
- `mcp/server/README.md`

## monitoring (1 files)
- `monitoring/.gitkeep`

## notebooks (2 files)
- `notebooks/gpu_training_example.ipynb`
- `notebooks/quick_start.ipynb`

## nox_sessions (1 files)
- `nox_sessions/fence_tests.py`

## omegaconf (1 files)
- `omegaconf/__init__.py`

## ops (1 files)
- `ops/threat_model/STRIDE.md`

## patches (20 files)
- `patches/analysis.patch`
- `patches/analysis___init__.py.patch`
- `patches/analysis_audit_pipeline.py.patch`
- `patches/analysis_metrics.jsonl.patch`
- `patches/analysis_metrics.py.patch`
- `patches/analysis_parsers.py.patch`
- `patches/analysis_providers.py.patch`
- `patches/analysis_registry.py.patch`
- `patches/changelog.patch`
- `patches/ci_local.patch`
- `patches/pending/2025-09-21_deterministic_loader.patch`
- `patches/pending/2025-09-21_eval_loop.patch`
- `patches/pending/2025-09-21_hydra_entrypoint.patch`
- `patches/pending/2025-09-21_metrics_default_min.patch`
- `patches/readme_offline_block.patch`
- ... (+5 more)

## reports (13 files)
- `reports/_codex_status_update-2025-09-28.md`
- `reports/_codex_status_update-2025-09-29.md`
- `reports/branch_analysis.md`
- `reports/capability_audit.md`
- `reports/critical_repo_summary.md`
- `reports/deferred.md`
- `reports/high_signal_findings.md`
- `reports/local_checks.md`
- `reports/observability_runbook.md`
- `reports/repo_map.md`
- `reports/report_templates.md`
- `reports/reproducibility.md`
- `reports/security_audit.md`

## requirements (1 files)
- `requirements/base.txt`

## schemas (2 files)
- `schemas/run_metrics.schema.json`
- `schemas/run_params.schema.json`

## scripts (53 files)
- `scripts/__init__.py`
- `scripts/apply_session_logging_workflow.py`
- `scripts/archive_paths.sh`
- `scripts/benchmark_logging.py`
- `scripts/build_wheel.sh`
- `scripts/check_licenses.py`
- `scripts/cli/__init__.py`
- `scripts/cli/viewer.py`
- `scripts/codex-audit`
- `scripts/codex_end_to_end.py`
- `scripts/codex_local_audit.sh`
- `scripts/codex_local_gates.sh`
- `scripts/codex_local_gates.sh01`
- `scripts/codex_orchestrate.py`
- `scripts/codex_precommit_dispatch.sh`
- ... (+38 more)

## semgrep_rules (8 files)
- `semgrep_rules/default.yml`
- `semgrep_rules/python-basic.yml`
- `semgrep_rules/python/insecure_eval.yml`
- `semgrep_rules/python/pickle_load.yml`
- `semgrep_rules/python/requests_no_timeout.yml`
- `semgrep_rules/python/ssl_verify_off.yml`
- `semgrep_rules/python/subprocess_shell.yml`
- `semgrep_rules/python/yaml_unsafe_load.yml`

## services (20 files)
- `services/api/__init__.py`
- `services/api/main.py`
- `services/api/requirements.txt`
- `services/ita/.gitignore`
- `services/ita/README.md`
- `services/ita/app/__init__.py`
- `services/ita/app/git_ops.py`
- `services/ita/app/hygiene.py`
- `services/ita/app/knowledge_base.py`
- `services/ita/app/main.py`
- `services/ita/app/models.py`
- `services/ita/app/security.py`
- `services/ita/app/tests_runner.py`
- `services/ita/openapi.yaml`
- `services/ita/pyproject.toml`
- ... (+5 more)

## src (223 files)
- `src/__init__.py`
- `src/codex/__init__.py`
- `src/codex/_version.py`
- `src/codex/chat.py`
- `src/codex/cli.py`
- `src/codex/db/sqlite_patch.py`
- `src/codex/logging/__init__.py`
- `src/codex/logging/config.py`
- `src/codex/logging/conversation_logger.py`
- `src/codex/logging/db_utils.py`
- `src/codex/logging/export.py`
- `src/codex/logging/fetch_messages.py`
- `src/codex/logging/import_ndjson.py`
- `src/codex/logging/query_logs.py`
- `src/codex/logging/session_hooks.py`
- ... (+208 more)

## temp (43 files)
- `temp/bridge_codex_copilot_bridge/LICENSE`
- `temp/bridge_codex_copilot_bridge/README-FROM-USER.md`
- `temp/bridge_codex_copilot_bridge/README.md`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/client/openai_tools.py`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/codex_client/demo_plan_and_call.py`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/codex_client/openai_wrapper.py`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/codex_client/tool_specs.json`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/pyproject.toml`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/toolspecs/git_create_pr.json`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/toolspecs/kb_search.json`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/toolspecs/repo_hygiene.json`
- `temp/bridge_codex_copilot_bridge/agents/codex_client/toolspecs/tests_run.json`
- `temp/bridge_codex_copilot_bridge/copilot/app/README.md`
- `temp/bridge_codex_copilot_bridge/copilot/app/app_manifest.json`
- `temp/bridge_codex_copilot_bridge/copilot/extension/README.md`
- ... (+28 more)

## tests (465 files)
- `tests/__init__.py`
- `tests/_codex_introspect.py`
- `tests/analysis/test_audit_pipeline.py`
- `tests/analysis/test_docs_links_audit.py`
- `tests/analysis/test_external_web_search.py`
- `tests/analysis/test_providers.py`
- `tests/assets/README.md`
- `tests/assets/corpus_tiny.txt`
- `tests/breadcrumbs/test_bundle_and_integrity.py`
- `tests/breadcrumbs/test_catalog_db.py`
- `tests/breadcrumbs/test_compaction.py`
- `tests/breadcrumbs/test_ledger.py`
- `tests/checkpointing/test_atomicity_and_resume.py`
- `tests/checkpointing/test_best_not_pruned.py`
- `tests/checkpointing/test_best_promotion.py`
- ... (+450 more)

## tokenization (1 files)
- `tokenization/__init__.py`

## tools (129 files)
- `tools/__init__.py`
- `tools/allowlist_args.py`
- `tools/answer_codex_questions.py`
- `tools/apply_ci_precommit.py`
- `tools/apply_container_api.py`
- `tools/apply_data_loaders.py`
- `tools/apply_docs.py`
- `tools/apply_hydra_scaffold.py`
- `tools/apply_interfaces.py`
- `tools/apply_ml_metrics.py`
- `tools/apply_mlflow_tracking.py`
- `tools/apply_patch_safely.py`
- `tools/apply_patch_safely.sh`
- `tools/apply_pyproject_packaging.py`
- `tools/apply_safety.py`
- ... (+114 more)

## torch (1 files)
- `torch/__init__.py`

## training (8 files)
- `training/__init__.py`
- `training/cache.py`
- `training/checkpoint_manager.py`
- `training/data_utils.py`
- `training/datasets.py`
- `training/engine_hf_trainer.py`
- `training/functional_training.py`
- `training/streaming.py`

## typer (1 files)
- `typer/testing.py`

## yaml (1 files)
- `yaml/__init__.py`
