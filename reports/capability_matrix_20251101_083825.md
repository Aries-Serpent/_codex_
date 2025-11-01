# [Report]: Capability Matrix
> Generated: 2025-11-01 08:38:24 UTC | Author: audit_system
 Roles: [Primary: Automated Auditor], [Secondary: Provenance Engine]  Energy: 5

## 1. Summary
Total Capabilities: 20
Low Maturity (< 0.70): 5

## 2. Capability Scores
| ID | Score | Functionality | Consistency | Tests | Safeguards | Docs | Evidence Count |
|----|-------|--------------:|------------:|------:|-----------:|-----:|---------------:|
| checkpointing | 0.88 | 1.00 | 0.87 | 0.70 | 0.83 | 1.00 | 94 |
| ci-cd-pipeline | 0.88 | 1.00 | 0.91 | 0.58 | 1.00 | 1.00 | 193 |
| code-quality-tooling | 0.84 | 1.00 | 0.86 | 0.57 | 0.83 | 1.00 | 145 |
| configuration | 0.76 | 1.00 | 0.77 | 0.21 | 1.00 | 1.00 | 213 |
| data-pipeline | 0.81 | 1.00 | 0.86 | 0.43 | 0.83 | 1.00 | 140 |
| deployment-infrastructure | 0.62 | 0.80 | 0.74 | 0.09 | 0.67 | 1.00 | 57 |
| documentation-system | 0.67 | 0.75 | 0.93 | 0.00 | 1.00 | 1.00 | 375 |
| duplication_ratio | 0.41 | 0.00 (ZERO) | 0.76 | 0.30 | 1.00 | 0.23 | 2914 |
| evaluation-metrics | 0.82 | 1.00 | 0.89 | 0.46 | 0.83 | 1.00 | 100 |
| experiment-management | 0.80 | 1.00 | 0.76 | 0.38 | 1.00 | 1.00 | 114 |
| inference-serving | 0.60 | 0.50 | 0.89 | 0.33 | 0.67 | 0.79 | 9 |
| logging-tracking | 0.79 | 1.00 | 0.81 | 0.32 | 1.00 | 1.00 | 254 |
| peft_hooks | 0.72 | 1.00 | 0.87 | 0.49 | 1.00 | 0.14 | 99 |
| reproducibility | 0.88 | 1.00 | 0.88 | 0.63 | 1.00 | 1.00 | 68 |
| safeguards_keywords | 0.66 | 1.00 | 0.84 | 0.28 | 1.00 | 0.18 | 800 |
| safety-security | 0.74 | 1.00 | 0.88 | 0.35 | 0.50 | 1.00 | 48 |
| testing-infrastructure | 0.91 | 0.75 | 0.90 | 0.99 | 1.00 | 1.00 | 887 |
| tokenization | 0.80 | 1.00 | 0.83 | 0.52 | 0.67 | 1.00 | 102 |
| training-engine | 0.84 | 1.00 | 0.87 | 0.45 | 1.00 | 1.00 | 201 |
| unified-training | 0.84 | 1.00 | 0.60 | 1.00 | 0.50 | 1.00 | 5 |

## 3. Low Maturity Focus
| ID | Score | Primary Deficit | Missing Patterns |
|----|-------|-----------------|------------------|
| deployment-infrastructure | 0.62 | tests | kubernetes |
| documentation-system | 0.67 | tests | sphinx |
| duplication_ratio | 0.41 | functionality | unique_stems |
| inference-serving | 0.60 | tests | fastapi |
| safeguards_keywords | 0.66 | documentation | None |

## 4. Weight Reference
| Component | Weight |
|-----------|-------:|
| functionality | 0.25 |
| consistency | 0.20 |
| tests | 0.25 |
| safeguards | 0.15 |
| documentation | 0.15 |

## 5. Capability Detail Sections
### checkpointing
Score: 0.8750

Components:
- Functionality: 1.0- Consistency: 0.8723404255319149- Tests: 0.7021276595744681- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: save_checkpoint, load
Patterns Found: load, save_checkpoint
Missing Patterns: None

Evidence Files (first 10):
```
codex_ml/utils/checkpointing.py
docs/CHECKPOINTS.md
docs/checkpoint_integrity.md
docs/checkpoint_schema_v2.md
docs/guides/CHECKPOINT_SAFETY.md
docs/guides/checkpointing.md
docs/how-to/checkpoint_metadata.md
docs/modules/checkpoint_manager.md
docs/training/Checkpointing_Surfaces.md
great_expectations/checkpoints/clean_checkpoint.yml
```
### ci-cd-pipeline
Score: 0.8751

Components:
- Functionality: 1.0- Consistency: 0.9067357512953368- Tests: 0.5751295336787565- Safeguards: 1.0- Documentation: 1.0

Required Patterns: ci, pre-commit, workflow, automation, validation
Patterns Found: automation, ci, pre-commit, validation, workflow
Missing Patterns: None

Evidence Files (first 10):
```
.codex/smoke/import_check.py
.github/workflows/archive-gates.yml.disabled
.github/workflows/capability-audit.yml
.github/workflows/ci.yml.disabled
.github/workflows/docker-build-push.yml
.github/workflows/runner-diagnostics.yml
.github/workflows/sbom.yml
.github/workflows/validate.yml.disabled
.github/workflows/workflow-expiry-enforcer.yml
.pre-commit-config.yaml
```
### code-quality-tooling
Score: 0.8391

Components:
- Functionality: 1.0- Consistency: 0.8551724137931034- Tests: 0.5724137931034483- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: lint, format, type-check, security-scan, quality
Patterns Found: format, lint, quality, security-scan, type-check
Missing Patterns: None

Evidence Files (first 10):
```
.bandit.yml
.codex/evidence/phase5_privacy_safety.jsonl
.codex/ruff.json
.editorconfig
.pre-commit-ruff.yaml
agents/codex_client/pyproject.toml
artifacts/security/bandit.txt
artifacts/security/detect-secrets.txt
artifacts/security/safety.txt
bandit.yaml
```
### configuration
Score: 0.7556

Components:
- Functionality: 1.0- Consistency: 0.7699530516431925- Tests: 0.20657276995305165- Safeguards: 1.0- Documentation: 1.0

Required Patterns: config, hydra
Patterns Found: config, hydra
Missing Patterns: None

Evidence Files (first 10):
```
.codex/copilot_bridge/config/bridge.config.json
.codex/evidence/phase4_hydra_check.jsonl
.codex/hydra_last/config.yaml
.editorconfig
.github/docs/ARCHIVE_CONFIG_ADR.md
.github/docs/SBOM_Config_InstructionEnhancement.md
.pre-commit-config.yaml
agents/codex_client/codex_client/config.py
agents/codex_client/tests/test_config.py
commitlint.config.mjs
```
### data-pipeline
Score: 0.8050

Components:
- Functionality: 1.0- Consistency: 0.8642857142857143- Tests: 0.42857142857142855- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: split, loader
Patterns Found: loader, split
Missing Patterns: None

Evidence Files (first 10):
```
codex_ml/data/checksums.py
configs/deployment/hhg_logistics/data/default.yaml
configs/schemas/data.schema.yaml
configs/training/data/base.yaml
configs/training/data/offline/tiny_corpus.yaml
configs/training/data/tiny.yaml
data/.gitkeep
data/models/.gitkeep
data/offline/length_reward.json
data/offline/tiny_corpus.txt
```
### deployment-infrastructure
Score: 0.6193

Components:
- Functionality: 0.8- Consistency: 0.736842105263158- Tests: 0.08771929824561403- Safeguards: 0.6666666666666666- Documentation: 1.0

Required Patterns: docker, kubernetes, helm, deploy, service
Patterns Found: deploy, docker, helm, service
Missing Patterns: kubernetes

Evidence Files (first 10):
```
.dockerignore
Dockerfile
Dockerfile.gpu
deploy/helm/Chart.yaml
deploy/helm/values.yaml
deploy/interactive_entrypoint.sh
deploy/setup_universal.sh
docker-compose.yml
docker/entrypoint.sh
docker/msp-gateway.Dockerfile
```
### documentation-system
Score: 0.6732

Components:
- Functionality: 0.75- Consistency: 0.9253333333333333- Tests: 0.0026666666666666666- Safeguards: 1.0- Documentation: 1.0

Required Patterns: markdown, docs, mkdocs, sphinx
Patterns Found: docs, markdown, mkdocs
Missing Patterns: sphinx

Evidence Files (first 10):
```
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
```
### duplication_ratio
Score: 0.4125

Components:
- Functionality: 0.0 (ZERO)- Consistency: 0.7608098833218944- Tests: 0.3040494166094715- Safeguards: 1.0- Documentation: 0.2288732394366197

Required Patterns: unique_stems
Patterns Found: None
Missing Patterns: unique_stems

Evidence Files (first 10):
```
.bandit.yml
.codex/DO_NOT_ACTIVATE_ACTIONS.txt
.codex/DO_NOT_ACTIVATE_GITHUB_ACTIONS
.codex/GATES_REPORT.txt
.codex/README.md
.codex/README.md.bak
.codex/action_log.ndjson
.codex/analysis_metrics.jsonl
.codex/archive/README_UPDATED.md
.codex/automation_out/change_log.md
```
### evaluation-metrics
Score: 0.8180

Components:
- Functionality: 1.0- Consistency: 0.89- Tests: 0.46- Safeguards: 0.8333333333333334- Documentation: 1.0

Required Patterns: metric, perplexity
Patterns Found: metric, perplexity
Missing Patterns: None

Evidence Files (first 10):
```
configs/deployment/hhg_logistics/eval/default.yaml
configs/evaluation/base.yaml
configs/evaluation/default.yaml
configs/evaluation/metrics/offline/weighted_accuracy.yaml
configs/evaluation/offline.yaml
configs/evaluation/reasoning/base.yaml
configs/evaluation/reasoning/default.yaml
configs/evaluation/reasoning/local_ci.yaml
configs/evaluation/reasoning/math.yaml
configs/evaluation/reasoning/proof.yaml
```
### experiment-management
Score: 0.7969

Components:
- Functionality: 1.0- Consistency: 0.7631578947368421- Tests: 0.37719298245614036- Safeguards: 1.0- Documentation: 1.0

Required Patterns: experiment, tracking, metadata, mlflow, wandb
Patterns Found: experiment, metadata, mlflow, tracking, wandb
Missing Patterns: None

Evidence Files (first 10):
```
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
```
### inference-serving
Score: 0.6049

Components:
- Functionality: 0.5- Consistency: 0.8888888888888888- Tests: 0.3333333333333333- Safeguards: 0.6666666666666666- Documentation: 0.7922535211267605

Required Patterns: server, fastapi
Patterns Found: server
Missing Patterns: fastapi

Evidence Files (first 10):
```
src/codex_ml/telemetry/server.py
src/hhg_logistics/monitor/serve_report.py
src/hhg_logistics/serve/__init__.py
src/hhg_logistics/serve/app.py
src/hhg_logistics/serve/smoke.py
temp/bridge_codex_copilot_bridge/mcp/server/main.py
temp/bridge_codex_copilot_bridge/mcp/server/server.py
tests/hhg_logistics/serve/test_app.py
tests/telemetry/test_metrics_server.py
```
### logging-tracking
Score: 0.7927

Components:
- Functionality: 1.0- Consistency: 0.8149606299212598- Tests: 0.3188976377952756- Safeguards: 1.0- Documentation: 1.0

Required Patterns: log, mlflow
Patterns Found: log, mlflow
Missing Patterns: None

Evidence Files (first 10):
```
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
```
### peft_hooks
Score: 0.7186

Components:
- Functionality: 1.0- Consistency: 0.8686868686868687- Tests: 0.494949494949495- Safeguards: 1.0- Documentation: 0.1408450704225352

Required Patterns: LoraConfig, get_peft_model, lora, peft, prepare_model_for_kbit_training
Patterns Found: LoraConfig, get_peft_model, lora, peft, prepare_model_for_kbit_training
Missing Patterns: None

Evidence Files (first 10):
```
cli/script_polish.py
cli/update_runner.py
codex_addons/metrics/collector.py
codex_task_executor.py
models/chat_model.py
models/peft_utils.py
scripts/codex_ready_task_runner.py
scripts/make_quickstart_notebook.py
scripts/space_traversal/detectors/detector_peft.py
scripts/train.py
```
### reproducibility
Score: 0.8846

Components:
- Functionality: 1.0- Consistency: 0.8823529411764706- Tests: 0.6323529411764706- Safeguards: 1.0- Documentation: 1.0

Required Patterns: seed, deterministic, sha256, rng_state, reproducibility
Patterns Found: deterministic, reproducibility, rng_state, seed, sha256
Missing Patterns: None

Evidence Files (first 10):
```
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
```
### safeguards_keywords
Score: 0.6648

Components:
- Functionality: 1.0- Consistency: 0.83875- Tests: 0.2825- Safeguards: 1.0- Documentation: 0.176056338028169

Required Patterns: WANDB_MODE, checksum, offline, rng, seed, sha256
Patterns Found: WANDB_MODE, checksum, offline, rng, seed, sha256
Missing Patterns: None

Evidence Files (first 10):
```
.codex/README.md
.codex/change_log-large.md
.codex/disabled_workflows/release-upload.yml
.codex/notes/CODEBASE_AUDIT.md
.codex/notes/ERROR_CAPTURE_BLOCKS.md
.codex/notes/MERGE_NOTES.md
.codex/notes/REPRO_NOTES.md
.codex/scripts/maintenance.sh
.codex/scripts/setup.sh
.codex/status/_codex_status_update-2025-08-28.md
```
### safety-security
Score: 0.7385

Components:
- Functionality: 1.0- Consistency: 0.875- Tests: 0.3541666666666667- Safeguards: 0.5- Documentation: 1.0

Required Patterns: secret, sanitize
Patterns Found: sanitize, secret
Missing Patterns: None

Evidence Files (first 10):
```
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
```
### testing-infrastructure
Score: 0.9148

Components:
- Functionality: 0.75- Consistency: 0.9007891770011274- Tests: 0.9887260428410372- Safeguards: 1.0- Documentation: 1.0

Required Patterns: pytest, test_, fixture, marker
Patterns Found: fixture, pytest, test_
Missing Patterns: marker

Evidence Files (first 10):
```
agents/codex_client/pyproject.toml
configs/base/offline/tiny_fixtures.yaml
configs/development/pytest.ini
conftest.py
pyproject.toml
services/ita/pyproject.toml
temp/bridge_codex_copilot_bridge/agents/codex_client/pyproject.toml
temp/bridge_codex_copilot_bridge/mcp/server/pyproject.toml
temp/bridge_codex_copilot_bridge/services/ita/pyproject.toml
tests/__init__.py
```
### tokenization
Score: 0.7966

Components:
- Functionality: 1.0- Consistency: 0.8333333333333334- Tests: 0.5196078431372549- Safeguards: 0.6666666666666666- Documentation: 1.0

Required Patterns: tokenizer, encode
Patterns Found: encode, tokenizer
Missing Patterns: None

Evidence Files (first 10):
```
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
```
### training-engine
Score: 0.8351

Components:
- Functionality: 1.0- Consistency: 0.8656716417910448- Tests: 0.44776119402985076- Safeguards: 1.0- Documentation: 1.0

Required Patterns: train, epoch
Patterns Found: epoch, train
Missing Patterns: None

Evidence Files (first 10):
```
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
```
### unified-training
Score: 0.8450

Components:
- Functionality: 1.0- Consistency: 0.6- Tests: 1.0- Safeguards: 0.5- Documentation: 1.0

Required Patterns: UnifiedTrainingConfig, run_unified_training
Patterns Found: UnifiedTrainingConfig, run_unified_training
Missing Patterns: None

Evidence Files (first 10):
```
scripts/space_traversal/detectors/unified_training.py
src/codex_ml/detectors/unified_training.py
src/codex_ml/training/unified_training.py
tests/detectors/test_unified_training.py
tools/bench_unified_training.py
```

## 6. Appendix
| Field | Description |
|-------|-------------|
| template_hash | Hash of concatenated Jinja templates |
| generation_strategy | Weighted component aggregation |
| scoring_components | functionality, consistency, tests, safeguards, documentation |

Embedded Template SHA256: fded686db9b7567754a44227d8bcf9d229f13c397436f26743bc6be99aa6907b

*End of Matrix*