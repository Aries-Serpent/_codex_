# [Report]: Capability Matrix
Roles: [Primary: Automated Auditor], [Secondary: Provenance Engine] Energy: 5

## 1. Summary
Total Capabilities: 20
Low Maturity (< 0.70): 5
Missing Detectors (overrides): 0
Zero Components Observed: 1

## 2. Capability Scores
| ID | Score | Functionality | Consistency | Tests | Safeguards | Docs | Evidence Count |
|----|-------|--------------:|------------:|------:|-----------:|-----:|---------------:|
| checkpointing | 0.88 | 1.00 | 0.87 | 0.70 | 0.83 | 1.00 | 94 |
| ci-cd-pipeline | 0.88 | 1.00 | 0.91 | 0.58 | 1.00 | 1.00 | 193 |
| code-quality-tooling | 0.84 | 1.00 | 0.86 | 0.57 | 0.83 | 1.00 | 145 |
| configuration | 0.76 | 1.00 | 0.77 | 0.21 | 1.00 | 1.00 | 213 |
| data-pipeline | 0.81 | 1.00 | 0.86 | 0.43 | 0.83 | 1.00 | 140 |
| deployment-infrastructure | 0.62 | 0.80 | 0.74 | 0.09 | 0.67 | 1.00 | 57 |
| documentation-system | 0.67 | 0.75 | 0.93 | 0.00 | 1.00 | 1.00 | 377 |
| duplication_ratio | 0.41 | 0.00 (ZERO) | 0.76 | 0.30 | 1.00 | 0.24 | 2932 |
| evaluation-metrics | 0.82 | 1.00 | 0.89 | 0.46 | 0.83 | 1.00 | 100 |
| experiment-management | 0.80 | 1.00 | 0.76 | 0.38 | 1.00 | 1.00 | 114 |
| inference-serving | 0.61 | 0.50 | 0.89 | 0.33 | 0.67 | 0.80 | 9 |
| logging-tracking | 0.79 | 1.00 | 0.82 | 0.31 | 1.00 | 1.00 | 260 |
| peft_hooks | 0.72 | 1.00 | 0.87 | 0.49 | 1.00 | 0.16 | 99 |
| reproducibility | 0.88 | 1.00 | 0.89 | 0.60 | 1.00 | 1.00 | 72 |
| safeguards_keywords | 0.67 | 1.00 | 0.84 | 0.28 | 1.00 | 0.19 | 800 |
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
| inference-serving | 0.61 | tests | fastapi |
| safeguards_keywords | 0.67 | documentation | None |


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
- Functionality: 1.00
- Consistency: 0.87
- Tests: 0.70
- Safeguards: 0.83
- Documentation: 1.00

Required Patterns: save_checkpoint, load
Patterns Found: load, save_checkpoint
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.91
- Tests: 0.58
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: ci, pre-commit, workflow, automation, validation
Patterns Found: automation, ci, pre-commit, validation, workflow
Missing Patterns: None

Meta:
- ci_configs: 2
- github_actions: 8
- note: GitHub Actions present but not activated per AGENTS.md
- pre_commit_hooks: 3
- validation_scripts: 180

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.86
- Tests: 0.57
- Safeguards: 0.83
- Documentation: 1.00

Required Patterns: lint, format, type-check, security-scan, quality
Patterns Found: format, lint, quality, security-scan, type-check
Missing Patterns: None

Meta:
- formatters: 2
- linters: 3
- quality_scripts: 38
- security_scanners: 98
- type_checkers: 7

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.77
- Tests: 0.21
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: config, hydra
Patterns Found: config, hydra
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.86
- Tests: 0.43
- Safeguards: 0.83
- Documentation: 1.00

Required Patterns: split, loader
Patterns Found: loader, split
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 0.80
- Consistency: 0.74
- Tests: 0.09
- Safeguards: 0.67
- Documentation: 1.00

Required Patterns: docker, kubernetes, helm, deploy, service
Patterns Found: deploy, docker, helm, service
Missing Patterns: kubernetes

Meta:
- deploy_scripts: 3
- docker_configs: 6
- helm_charts: 2
- k8s_manifests: 0
- service_definitions: 46

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
Score: 0.6733

Components:
- Functionality: 0.75
- Consistency: 0.93
- Tests: 0.00
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: markdown, docs, mkdocs, sphinx
Patterns Found: docs, markdown, mkdocs
Missing Patterns: sphinx

Meta:
- config_count: 1
- markdown_count: 375
- rst_count: 0
- total_docs: 377

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
Score: 0.4145

Components:
- Functionality: 0.00 (ZERO)
- Consistency: 0.76
- Tests: 0.30
- Safeguards: 1.00
- Documentation: 0.24

Required Patterns: unique_stems
Patterns Found: None
Missing Patterns: unique_stems


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.89
- Tests: 0.46
- Safeguards: 0.83
- Documentation: 1.00

Required Patterns: metric, perplexity
Patterns Found: metric, perplexity
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.76
- Tests: 0.38
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: experiment, tracking, metadata, mlflow, wandb
Patterns Found: experiment, metadata, mlflow, tracking, wandb
Missing Patterns: None

Meta:
- experiment_utils: 13
- metadata_files: 67
- mlflow_integration: 32
- wandb_integration: 4

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
Score: 0.6063

Components:
- Functionality: 0.50
- Consistency: 0.89
- Tests: 0.33
- Safeguards: 0.67
- Documentation: 0.80

Required Patterns: server, fastapi
Patterns Found: server
Missing Patterns: fastapi

Meta:
- layer: serving

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
Score: 0.7917

Components:
- Functionality: 1.00
- Consistency: 0.82
- Tests: 0.31
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: log, mlflow
Patterns Found: log, mlflow
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

Evidence Files (first 10):
```
.codex/action_log.ndjson
.codex/automation_out/change_log.md
.codex/automation_out/db_catalog.json
.codex/cache/uv_sync.log
.codex/cache/uv_sync_maint.log
.codex/change_log-large.md
.codex/change_log.md
.codex/change_log_compare_report.json
.codex/codex_run.log
.codex/copilot_bridge/var/logs/.gitkeep
```
### peft_hooks
Score: 0.7210

Components:
- Functionality: 1.00
- Consistency: 0.87
- Tests: 0.49
- Safeguards: 1.00
- Documentation: 0.16

Required Patterns: LoraConfig, get_peft_model, lora, peft, prepare_model_for_kbit_training
Patterns Found: LoraConfig, get_peft_model, lora, peft, prepare_model_for_kbit_training
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
Score: 0.8771

Components:
- Functionality: 1.00
- Consistency: 0.89
- Tests: 0.60
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: seed, deterministic, sha256, rng_state, reproducibility
Patterns Found: deterministic, reproducibility, rng_state, seed, sha256
Missing Patterns: None

Meta:
- determinism_configs: 5
- integrity_validation: 31
- repro_utils: 16
- seed_management: 25

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

Evidence Files (first 10):
```
.codex/cache/maint_vendor_hash_post.json
.codex/cache/maint_vendor_hash_pre_sync.json
.codex/cache/vendor_hash_post_purge.json
.codex/cache/vendor_hash_pre_sync.json
.codex/validation/file_integrity_compare.json
_codex_reports/2025-10-06/reproducibility.json
_codex_reports/2025-10-06/seed_scan.json
codex_ml/data/checksums.py
configs/base/deterministic.yaml
docs/checkpoint_integrity.md
```
### safeguards_keywords
Score: 0.6671

Components:
- Functionality: 1.00
- Consistency: 0.84
- Tests: 0.28
- Safeguards: 1.00
- Documentation: 0.19

Required Patterns: WANDB_MODE, checksum, offline, rng, seed, sha256
Patterns Found: WANDB_MODE, checksum, offline, rng, seed, sha256
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.88
- Tests: 0.35
- Safeguards: 0.50
- Documentation: 1.00

Required Patterns: secret, sanitize
Patterns Found: sanitize, secret
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 0.75
- Consistency: 0.90
- Tests: 0.99
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: pytest, test_, fixture, marker
Patterns Found: fixture, pytest, test_
Missing Patterns: marker

Meta:
- config_count: 25
- fixture_count: 27
- test_count: 871

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.83
- Tests: 0.52
- Safeguards: 0.67
- Documentation: 1.00

Required Patterns: tokenizer, encode
Patterns Found: encode, tokenizer
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.87
- Tests: 0.45
- Safeguards: 1.00
- Documentation: 1.00

Required Patterns: train, epoch
Patterns Found: epoch, train
Missing Patterns: None


Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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
- Functionality: 1.00
- Consistency: 0.60
- Tests: 1.00
- Safeguards: 0.50
- Documentation: 1.00

Required Patterns: UnifiedTrainingConfig, run_unified_training
Patterns Found: UnifiedTrainingConfig, run_unified_training
Missing Patterns: None

Meta:
- category: training

Remediation Links:
- Components: docs/remediation/components.md
- Detectors: docs/remediation/detectors.md
- Policy: docs/remediation/policy.md

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

Embedded Template SHA256: 2dba6b3a850e97cb21fa75127a11d3aeaa57d5da89a51005d119effb4c0dff4b

*End of Matrix*