# [Report]: Capability Matrix
Roles: [Primary: Automated Auditor], [Secondary: Provenance Engine] Energy: 5

## 1. Summary
Total Capabilities: 25
Low Maturity (< 0.70): 8
Medium Maturity (0.70 - 0.85): 12
High Maturity (>= 0.85): 5

## 2. Capability Scores
| ID | Score | Level | Functionality | Consistency | Tests | Safeguards | Docs | Evidence Count |
|----|-------|-------|--------------:|------------:|------:|-----------:|-----:|---------------:|
| archival-bundling | 0.66 | Low | 1.00 | 0.88 | 0.23 | 0.83 | 0.37 | 184 |
| checkpointing | 0.86 | High | 1.00 | 0.88 | 0.68 | 0.83 | 0.94 | 101 |
| ci-cd-pipeline | 0.85 | High | 1.00 | 0.92 | 0.48 | 1.00 | 1.00 | 262 |
| code-quality-tooling | 0.81 | Medium | 1.00 | 0.87 | 0.45 | 0.83 | 1.00 | 211 |
| configuration | 0.76 | Medium | 1.00 | 0.77 | 0.21 | 1.00 | 1.00 | 255 |
| data-pipeline | 0.80 | Medium | 1.00 | 0.88 | 0.42 | 0.83 | 1.00 | 156 |
| deployment-infrastructure | 0.65 | Low | 0.80 | 0.69 | 0.13 | 0.83 | 1.00 | 62 |
| documentation-system | 0.68 | Low | 0.75 | 0.94 | 0.00 | 1.00 | 1.00 | 554 |
| duplication_ratio | 0.40 | Low | 0.00 (ZERO) | 0.78 | 0.28 | 1.00 | 0.15 | 3679 |
| evaluation-metrics | 0.82 | Medium | 1.00 | 0.88 | 0.46 | 0.83 | 1.00 | 111 |
| experiment-management | 0.79 | Medium | 1.00 | 0.77 | 0.36 | 1.00 | 1.00 | 137 |
| inference-serving | 0.52 | Low | 0.33 | 0.79 | 0.26 | 0.67 | 0.74 | 19 |
| logging-tracking | 0.79 | Medium | 1.00 | 0.82 | 0.31 | 1.00 | 1.00 | 275 |
| mcp-tools-integration | 0.62 | Low | 1.00 | 0.93 | 0.08 | 1.00 | 0.09 | 290 |
| ml-serving | 0.86 | High | 1.00 | 0.78 | 0.71 | 0.83 | 1.00 | 93 |
| peft_hooks | 0.72 | Medium | 1.00 | 0.87 | 0.49 | 1.00 | 0.15 | 112 |
| reproducibility | 0.88 | High | 1.00 | 0.89 | 0.61 | 1.00 | 1.00 | 76 |
| safeguards_keywords | 0.64 | Low | 1.00 | 0.85 | 0.26 | 1.00 | 0.06 | 964 |
| safety-security | 0.74 | Medium | 1.00 | 0.88 | 0.35 | 0.50 | 1.00 | 48 |
| status-reporting | 0.76 | Medium | 1.00 | 0.90 | 0.10 | 1.00 | 1.00 | 421 |
| testing-infrastructure | 0.91 | High | 0.75 | 0.89 | 0.99 | 1.00 | 1.00 | 1044 |
| tokenization | 0.80 | Medium | 1.00 | 0.83 | 0.52 | 0.67 | 1.00 | 113 |
| training-engine | 0.83 | Medium | 1.00 | 0.87 | 0.45 | 1.00 | 1.00 | 217 |
| unified-training | 0.84 | Medium | 1.00 | 0.60 | 1.00 | 0.50 | 1.00 | 5 |
| vector-stores | 0.33 | Low | 0.00 (ZERO) | 1.00 | 0.33 | 0.00 (ZERO) | 0.32 | 3 |

## 3. Low Maturity Focus
| ID | Score | Primary Deficit | Missing Patterns |
|----|-------|-----------------|------------------|
| archival-bundling | 0.66 | tests | None |
| deployment-infrastructure | 0.65 | tests | None |
| documentation-system | 0.68 | tests | None |
| duplication_ratio | 0.40 | functionality | None |
| inference-serving | 0.52 | tests | None |
| mcp-tools-integration | 0.62 | tests | None |
| safeguards_keywords | 0.64 | documentation | None |
| vector-stores | 0.33 | functionality | None |


## 4. Weight Reference
| Component | Weight |
|-----------|-------:|
| functionality | 0.25 |
| consistency | 0.20 |
| tests | 0.25 |
| safeguards | 0.15 |
| documentation | 0.15 |

## 5. Capability Detail Sections
### archival-bundling
Score: 0.6635

Components:
- Functionality: 1.0- Consistency: 0.8804347826086957- Tests: 0.22826086956521738- Safeguards: 0.8333333333333334- Documentation: 0.36866359447004604

Required Patterns: None
Patterns Found: archive, bundle, manifest
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/archive/README_UPDATED.md
.codex/copilot_bridge/manifests/bridge_manifest.schema.json
.codex/copilot_bridge/var/manifests/.gitkeep
.codex/evidence/archive_ops.jsonl
.codex/evidence/artifacts/archive_plan_root_cleanup_2025-10-17.json
.codex/reports/Archive_Policy_Operations.md
.codex/reports/archive_policy_operations.md
.codex/reports/merge_summary_archive_policy_20251024.txt
.codex/status/manifest-2025-09-22T02-15-21Z.json
.codex/validation/20250910T052842Z/post_manifest.json
```text
### checkpointing
Score: 0.8626

Components:
- Functionality: 1.0- Consistency: 0.8811881188118812- Tests: 0.6831683168316832- Safeguards: 0.8333333333333334- Documentation: 0.9370199692780337

Required Patterns: None
Patterns Found: load, save_checkpoint
Missing Patterns: None

Evidence Files (first 10):
```text
codex_ml/utils/checkpointing.py
configs/schemas/checkpoint_manifest.schema.json
docs/CHECKPOINTS.md
docs/checkpoint_integrity.md
docs/checkpoint_schema_v2.md
docs/guides/CHECKPOINT_SAFETY.md
docs/guides/checkpointing.md
docs/how-to/checkpoint_metadata.md
docs/modules/checkpoint_manager.md
docs/training/Checkpointing_Surfaces.md
```text
### ci-cd-pipeline
Score: 0.8544

Components:
- Functionality: 1.0- Consistency: 0.916030534351145- Tests: 0.4847328244274809- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: automation, ci, pre-commit, validation, workflow
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/smoke/import_check.py
.github/scripts/validate_agents_infrastructure.sh
.github/workflows/archive-gates.yml.disabled
.github/workflows/audit_chain.yml
.github/workflows/automation_ingest.yml
.github/workflows/capability-audit.yml
.github/workflows/ci.yml
.github/workflows/coverage_report.yml
.github/workflows/daily_status_cron.yml
.github/workflows/daily_status_enrich.yml
```text
### code-quality-tooling
Score: 0.8120

Components:
- Functionality: 1.0- Consistency: 0.8720379146919431- Tests: 0.45023696682464454- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: None
Patterns Found: format, lint, quality, security-scan, type-check
Missing Patterns: None

Evidence Files (first 10):
```text
.bandit.yaml
.bandit.yml
.codex/evidence/phase5_privacy_safety.jsonl
.codex/ruff.json
.editorconfig
.github/ISSUE_TEMPLATE/security.yml
.github/ISSUE_TEMPLATE/security_gap.md
.github/docs/DEPLOYMENT_ORCHESTRATION_SECURITY_SUMMARY.md
.github/docs/Security_Gates_Copilot.md
.github/docs/Security_Session_Copilot.md
```text
### configuration
Score: 0.7565

Components:
- Functionality: 1.0- Consistency: 0.7725490196078432- Tests: 0.20784313725490197- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: config, hydra
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/copilot_bridge/config/bridge.config.json
.codex/evidence/phase4_hydra_check.jsonl
.codex/hydra_last/config.yaml
.editorconfig
.github/ISSUE_TEMPLATE/config.yml
.github/docs/ARCHIVE_CONFIG_ADR.md
.github/docs/SBOM_Config_InstructionEnhancement.md
.pre-commit-config.yaml
agents/codex_client/codex_client/config.py
agents/codex_client/tests/test_config.py
```text
### data-pipeline
Score: 0.8048

Components:
- Functionality: 1.0- Consistency: 0.8782051282051282- Tests: 0.4166666666666667- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: None
Patterns Found: loader, split
Missing Patterns: None

Evidence Files (first 10):
```text
.github/workflows/data_validation.yml
codex_ml/data/checksums.py
configs/deployment/hhg_logistics/data/default.yaml
configs/schemas/data.schema.yaml
configs/schemas/dataset_manifest.schema.json
configs/training/data/base.yaml
configs/training/data/offline/tiny_corpus.yaml
configs/training/data/tiny.yaml
data/.gitkeep
data/models/.gitkeep
```text
### deployment-infrastructure
Score: 0.6460

Components:
- Functionality: 0.8- Consistency: 0.6935483870967742- Tests: 0.12903225806451613- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: None
Patterns Found: deploy, docker, helm, service
Missing Patterns: None

Evidence Files (first 10):
```text
.dockerignore
Dockerfile
Dockerfile.gpu
Dockerfile.local
deploy/helm/Chart.yaml
deploy/helm/values.yaml
deploy/interactive_entrypoint.sh
deploy/setup_universal.sh
docker-compose.yml
docker/Dockerfile.cpu
```text
### documentation-system
Score: 0.6754

Components:
- Functionality: 0.75- Consistency: 0.9350180505415162- Tests: 0.0036101083032490976- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: docs, markdown, mkdocs
Missing Patterns: None

Evidence Files (first 10):
```text
README.md
docs/ARCHITECTURE.md
docs/CHANGELOG.md
docs/CHANGELOG/change_log.md
docs/CHANGELOG/changelog_codex.md
docs/CHANGELOG/changelog_session_logging.md
docs/CHECKPOINTS.md
docs/CLI.md
docs/CODEX_STRUCTURE_CONSOLIDATION_PROMPT.md
docs/CONTRIBUTING.addendum.md
```text
### duplication_ratio
Score: 0.4002

Components:
- Functionality: 0.0 (ZERO)- Consistency: 0.7817341668931774- Tests: 0.28322913835281327- Safeguards: 1.0- Documentation: 0.15360983102918585

Required Patterns: None
Patterns Found: None
Missing Patterns: None

Evidence Files (first 10):
```text
.bandit.yaml
.bandit.yml
.codex/DO_NOT_ACTIVATE_ACTIONS.txt
.codex/DO_NOT_ACTIVATE_GITHUB_ACTIONS
.codex/GATES_REPORT.txt
.codex/README.md
.codex/README.md.bak
.codex/action_log.ndjson
.codex/analysis_metrics.jsonl
.codex/archive/README_UPDATED.md
```text
### evaluation-metrics
Score: 0.8164

Components:
- Functionality: 1.0- Consistency: 0.8828828828828829- Tests: 0.4594594594594595- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: None
Patterns Found: metric, perplexity
Missing Patterns: None

Evidence Files (first 10):
```text
.github/docs/PostMergeValidation_IssueTemplate_InstructionEnhancement.md
configs/deployment/hhg_logistics/eval/default.yaml
configs/evaluation/base.yaml
configs/evaluation/default.yaml
configs/evaluation/metrics/offline/weighted_accuracy.yaml
configs/evaluation/offline.yaml
configs/evaluation/reasoning/base.yaml
configs/evaluation/reasoning/default.yaml
configs/evaluation/reasoning/local_ci.yaml
configs/evaluation/reasoning/math.yaml
```text
### experiment-management
Score: 0.7942

Components:
- Functionality: 1.0- Consistency: 0.7737226277372262- Tests: 0.35766423357664234- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: experiment, metadata, mlflow, tracking, wandb
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/copilot_bridge/manifests/bridge_manifest.schema.json
.codex/copilot_bridge/var/manifests/.gitkeep
.codex/evidence/provenance/root-cleanup/intoto.jsonl
.codex/evidence/provenance/root-cleanup/slsa.json
.codex/status/manifest-2025-09-22T02-15-21Z.json
.codex/status/provenance.json
.codex/validation/20250910T052842Z/post_manifest.json
.codex/validation/20250910T052842Z/pre_manifest.json
.codex/validation/20250910T071257Z/post_manifest.json
.codex/validation/20250910T071257Z/pre_manifest.json
```text
### inference-serving
Score: 0.5176

Components:
- Functionality: 0.3333333333333333- Consistency: 0.7894736842105263- Tests: 0.2631578947368421- Safeguards: 0.6666666666666666- Documentation: 0.7373271889400921

Required Patterns: None
Patterns Found: serve
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/copilot_bridge/bridge/server.js
configs/deployment/hhg_logistics/serve/local.yaml
copilot/extension/server/index.js
mcp/server/README.md
scripts/local/serve_local.sh
src/codex_ml/telemetry/server.py
src/hhg_logistics/monitor/serve_report.py
src/hhg_logistics/serve/__init__.py
src/hhg_logistics/serve/app.py
src/hhg_logistics/serve/smoke.py
```text
### logging-tracking
Score: 0.7925

Components:
- Functionality: 1.0- Consistency: 0.8218181818181818- Tests: 0.31272727272727274- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: log, mlflow
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/action_log.ndjson
.codex/automation_out/change_log.md
.codex/automation_out/db_catalog.json
.codex/change_log-large.md
.codex/change_log.md
.codex/change_log_compare_report.json
.codex/codex_run.log
.codex/copilot_bridge/var/logs/.gitkeep
.codex/errors_codex.log
.codex/evidence/phase5_structured_logging.jsonl
```text
### mcp-tools-integration
Score: 0.6199

Components:
- Functionality: 1.0- Consistency: 0.9310344827586207- Tests: 0.07931034482758621- Safeguards: 1.0- Documentation: 0.09216589861751151

Required Patterns: None
Patterns Found: mcp, tool
Missing Patterns: None

Evidence Files (first 10):
```text
configs/evaluation/reasoning/tools.yaml
configs/training/reasoning/tool_execution.yaml
data/sample/reasoning/tool_eval.jsonl
data/sample/reasoning/tool_traces.jsonl
docs/guides/CODEX_TOOL_SELECTION.md
docs/ops/Local_Tooling_Prereqs.md
docs/reference/tools.md
docs/validation/Schema_Validation_Tooling.md
mcp/mcp.json
mcp/server/README.md
```text
### ml-serving
Score: 0.8594

Components:
- Functionality: 1.0- Consistency: 0.7849462365591398- Tests: 0.7096774193548387- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: None
Patterns Found: api, predict, serve
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/copilot_bridge/bridge/server.js
P1_FIX_API_KEY_OPTIONAL.md
actions/openapi.yaml
configs/deployment/hhg_logistics/serve/local.yaml
copilot/extension/server/index.js
data/zendesk_api_index.json
docs/api.md
docs/api/README.md
docs/api/loop_eval.md
docs/api_catalog.md
```text
### peft_hooks
Score: 0.7190

Components:
- Functionality: 1.0- Consistency: 0.8660714285714286- Tests: 0.49107142857142855- Safeguards: 1.0- Documentation: 0.15360983102918585

Required Patterns: None
Patterns Found: LoraConfig, get_peft_model, lora, peft, prepare_model_for_kbit_training
Missing Patterns: None

Evidence Files (first 10):
```text
cli/script_polish.py
cli/update_runner.py
codex_addons/metrics/collector.py
codex_task_executor.py
models/chat_model.py
models/lora/_test_utils.py
models/peft_utils.py
nox_sessions/docs_validation.py
noxfile.py
scripts/codex_ready_task_runner.py
```text
### reproducibility
Score: 0.8803

Components:
- Functionality: 1.0- Consistency: 0.8947368421052632- Tests: 0.6052631578947368- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: deterministic, reproducibility, rng_state, seed, sha256
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/validation/file_integrity_compare.json
_codex_reports/2025-10-06/reproducibility.json
_codex_reports/2025-10-06/seed_scan.json
codex_ml/data/checksums.py
configs/base/deterministic.yaml
docs/checkpoint_integrity.md
docs/guides/serving_reproducibility.md
docs/integrity_and_uris.md
docs/manifest_integrity.md
docs/ops/Deterministic_Installs.md
```text
### safeguards_keywords
Score: 0.6431

Components:
- Functionality: 1.0- Consistency: 0.8464730290456431- Tests: 0.258298755186722- Safeguards: 1.0- Documentation: 0.06144393241167434

Required Patterns: None
Patterns Found: WANDB_MODE, checksum, offline, rng, seed, sha256
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/README.md
.codex/change_log-large.md
.codex/disabled_workflows/release-upload.yml
.codex/notes/CODEBASE_AUDIT.md
.codex/notes/ERROR_CAPTURE_BLOCKS.md
.codex/notes/MERGE_NOTES.md
.codex/notes/REPRO_NOTES.md
.codex/reports/PHASE2_STANDARDIZATION_SUMMARY.md
.codex/scripts/maintenance.sh
.codex/scripts/setup.sh
```text
### safety-security
Score: 0.7385

Components:
- Functionality: 1.0- Consistency: 0.875- Tests: 0.3541666666666667- Safeguards: 0.5- Documentation: 1.0

Required Patterns: None
Patterns Found: sanitize, secret
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/evidence/phase5_privacy_safety.jsonl
artifacts/security/safety.txt
configs/base/safety/policy.yaml
configs/msp/safety.yaml
docs/guides/CHECKPOINT_SAFETY.md
docs/modules/safety.md
docs/safety.md
docs/safety/differential_privacy.md
docs/safety/moderation_adapter.md
docs/safety/policy_guidance.md
```text
### status-reporting
Score: 0.7556

Components:
- Functionality: 1.0- Consistency: 0.9002375296912114- Tests: 0.1021377672209026- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: audit, report, status
Missing Patterns: None

Evidence Files (first 10):
```text
.codex/GATES_REPORT.txt
.codex/automation_out/coverage_report.json
.codex/change_log_compare_report.json
.codex/evidence/audit_fixes_phase1.jsonl
.codex/evidence/phase1_audit_fixes.jsonl
.codex/evidence/phase2_requirements_audit.jsonl
.codex/evidence/phase3_summary.md
.codex/evidence/phase4_dependencies_audit.jsonl
.codex/notes/CODEBASE_AUDIT.md
.codex/reports/.gitkeep
```text
### testing-infrastructure
Score: 0.9126

Components:
- Functionality: 0.75- Consistency: 0.8898467432950191- Tests: 0.9885057471264368- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: fixture, pytest, test_
Missing Patterns: None

Evidence Files (first 10):
```text
.github/docs/AGENTS_Integration_Test_Fixture_Refactor_Copilot.md
agents/codex_client/pyproject.toml
configs/base/offline/tiny_fixtures.yaml
configs/development/pytest.ini
conftest.py
pyproject.toml
pytest.ini
services/ita/pyproject.toml
temp/bridge_codex_copilot_bridge/agents/codex_client/pyproject.toml
temp/bridge_codex_copilot_bridge/mcp/server/pyproject.toml
```text
### tokenization
Score: 0.7969

Components:
- Functionality: 1.0- Consistency: 0.831858407079646- Tests: 0.5221238938053098- Safeguards: 0.6666666666666666- Documentation: 1.0

Required Patterns: None
Patterns Found: encode, tokenizer
Missing Patterns: None

Evidence Files (first 10):
```text
_codex_reports/2025-10-06/tokenizer_check.json
artifacts/models/tiny_tokenizer/vocab.json
codex_digest/tokenizer.py
configs/training/tokenization/base.yaml
configs/training/tokenizer/multilingual.yaml
configs/training/tokenizer/offline/gpt2.yaml
configs/training/tokenizer/offline/tiny_vocab.yaml
configs/training/tokenizer/offline/tinyllama.yaml
configs/training/tokenizer/train_tokenizer.yaml
docs/guides/tokenization.md
```text
### training-engine
Score: 0.8350

Components:
- Functionality: 1.0- Consistency: 0.8663594470046083- Tests: 0.4470046082949309- Safeguards: 1.0- Documentation: 1.0

Required Patterns: None
Patterns Found: epoch, train
Missing Patterns: None

Evidence Files (first 10):
```text
_codex_reports/2025-10-06/trainer_smoke.json
_codex_reports/2025-10-06/trainer_smoke.log
artifacts/diffs/training_py01_removal.md
cli/train_schema_demo.py
configs/deployment/hhg_logistics/train/default.yaml
configs/deployment/hhg_logistics/train/lora.yaml
configs/schemas/training.schema.yaml
configs/schemas/training_profile.schema.json
configs/simple/train.yaml
configs/training/base.yaml
```text
### unified-training
Score: 0.8450

Components:
- Functionality: 1.0- Consistency: 0.6- Tests: 1.0- Safeguards: 0.5- Documentation: 1.0

Required Patterns: None
Patterns Found: UnifiedTrainingConfig, run_unified_training
Missing Patterns: None

Evidence Files (first 10):
```text
scripts/space_traversal/detectors/unified_training.py
src/codex_ml/detectors/unified_training.py
src/codex_ml/training/unified_training.py
tests/detectors/test_unified_training.py
tools/bench_unified_training.py
```text
### vector-stores
Score: 0.3317

Components:
- Functionality: 0.0 (ZERO)- Consistency: 1.0- Tests: 0.3333333333333333- Safeguards: 0.0 (ZERO)- Documentation: 0.32258064516129026

Required Patterns: None
Patterns Found: None
Missing Patterns: None

Evidence Files (first 10):
```text
codex_addons/vector_stores/__init__.py
codex_addons/vector_stores/pgvector_stub.py
codex_addons/vector_stores/weaviate_stub.py
```text

## 6. Appendix
| Field | Description |
|-------|-------------|
| template_hash | Hash of concatenated Jinja templates |
| generation_strategy | Weighted component aggregation |
| scoring_components | functionality, consistency, tests, safeguards, documentation |

Embedded Template SHA256: aab8f6f3f24738ab6e544a887cbe459a6dea9a4e569b92954048fa8404361035

*End of Matrix*
