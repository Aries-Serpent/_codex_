# [Report]: Capability Matrix
> Generated: 2025-10-30 20:44:04 UTC | Author: audit_system
 Roles: [Primary: Automated Auditor], [Secondary: Provenance Engine]  Energy: 5

## 1. Summary
Total Capabilities: 20
Low Maturity (< 0.45 heuristic): 5

## 2. Capability Scores
| ID | Score | Functionality | Consistency | Tests | Safeguards | Docs | Evidence Count |
|----|-------|--------------:|------------:|------:|-----------:|-----:|---------------:|
| checkpointing | 0.88 | 1.00 | 0.87 | 0.70 | 0.83 | 1.00 | 94 |
| ci-cd-pipeline | 0.88 | 1.00 | 0.91 | 0.58 | 1.00 | 1.00 | 192 |
| code-quality-tooling | 0.84 | 1.00 | 0.87 | 0.58 | 0.83 | 1.00 | 143 |
| configuration | 0.76 | 1.00 | 0.76 | 0.22 | 1.00 | 1.00 | 194 |
| data-pipeline | 0.81 | 1.00 | 0.86 | 0.43 | 0.83 | 1.00 | 140 |
| deployment-infrastructure | 0.65 | 0.80 | 0.84 | 0.14 | 0.67 | 1.00 | 37 |
| documentation-system | 0.67 | 0.75 | 0.93 | 0.00 | 1.00 | 1.00 | 355 |
| duplication_ratio | 0.41 | 0.00 | 0.76 | 0.31 | 1.00 | 0.17 | 2824 |
| evaluation-metrics | 0.81 | 1.00 | 0.90 | 0.50 | 0.67 | 1.00 | 90 |
| experiment-management | 0.80 | 1.00 | 0.76 | 0.38 | 1.00 | 1.00 | 114 |
| inference-serving | 0.59 | 0.50 | 0.89 | 0.33 | 0.67 | 0.69 | 9 |
| logging-tracking | 0.79 | 1.00 | 0.81 | 0.32 | 1.00 | 1.00 | 254 |
| peft_hooks | 0.71 | 1.00 | 0.87 | 0.49 | 1.00 | 0.09 | 98 |
| reproducibility | 0.88 | 1.00 | 0.88 | 0.63 | 1.00 | 1.00 | 68 |
| safeguards_keywords | 0.66 | 1.00 | 0.84 | 0.29 | 1.00 | 0.13 | 774 |
| safety-security | 0.74 | 1.00 | 0.89 | 0.36 | 0.50 | 1.00 | 47 |
| testing-infrastructure | 0.91 | 0.75 | 0.90 | 0.99 | 1.00 | 1.00 | 883 |
| tokenization | 0.80 | 1.00 | 0.83 | 0.52 | 0.67 | 1.00 | 102 |
| training-engine | 0.84 | 1.00 | 0.87 | 0.45 | 1.00 | 1.00 | 201 |
| unified-training | 0.84 | 1.00 | 0.60 | 1.00 | 0.50 | 1.00 | 5 |

## 3. Low Maturity Focus
| ID | Score | Primary Deficit |
|----|-------|-----------------|
| deployment-infrastructure | 0.65 | tests |
| documentation-system | 0.67 | tests |
| duplication_ratio | 0.41 | functionality |
| inference-serving | 0.59 | tests |
| safeguards_keywords | 0.66 | documentation |

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
- Functionality: 1.0
- Consistency: 0.8723404255319149
- Tests: 0.7021276595744681
- Safeguards: 0.8333333333333334
- Documentation: 1.0


Patterns Found: load, save_checkpoint

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
Score: 0.8758

Components:
- Functionality: 1.0
- Consistency: 0.90625
- Tests: 0.578125
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- ci_configs: 2
- github_actions: 7
- note: GitHub Actions present but not activated per AGENTS.md
- pre_commit_hooks: 3
- validation_scripts: 180

Patterns Found: automation, ci, pre-commit, validation, workflow

Evidence Files (first 10):
```
.codex/smoke/import_check.py
.github/workflows/archive-gates.yml.disabled
.github/workflows/ci.yml.disabled
.github/workflows/docker-build-push.yml
.github/workflows/runner-diagnostics.yml
.github/workflows/sbom.yml
.github/workflows/validate.yml.disabled
.github/workflows/workflow-expiry-enforcer.yml
.pre-commit-config.yaml
.pre-commit-hybrid.yaml
```
### code-quality-tooling
Score: 0.8435

Components:
- Functionality: 1.0
- Consistency: 0.8671328671328671
- Tests: 0.5804195804195804
- Safeguards: 0.8333333333333334
- Documentation: 1.0

Meta:
- formatters: 2
- linters: 3
- quality_scripts: 38
- security_scanners: 96
- type_checkers: 7

Patterns Found: format, lint, quality, security-scan, type-check

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
Score: 0.7580

Components:
- Functionality: 1.0
- Consistency: 0.7628865979381443
- Tests: 0.22164948453608246
- Safeguards: 1.0
- Documentation: 1.0


Patterns Found: config, hydra

Evidence Files (first 10):
```
.codex/copilot_bridge/config/bridge.config.json
.codex/evidence/phase4_hydra_check.jsonl
.codex/hydra_last/config.yaml
.editorconfig
.github/docs/ARCHIVE_CONFIG_ADR.md
.pre-commit-config.yaml
agents/codex_client/codex_client/config.py
agents/codex_client/tests/test_config.py
commitlint.config.mjs
configs/README.md
```
### data-pipeline
Score: 0.8050

Components:
- Functionality: 1.0
- Consistency: 0.8642857142857143
- Tests: 0.42857142857142855
- Safeguards: 0.8333333333333334
- Documentation: 1.0


Patterns Found: loader, split

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
Score: 0.6514

Components:
- Functionality: 0.8
- Consistency: 0.8378378378378378
- Tests: 0.13513513513513514
- Safeguards: 0.6666666666666666
- Documentation: 1.0

Meta:
- deploy_scripts: 3
- docker_configs: 5
- helm_charts: 2
- k8s_manifests: 0
- service_definitions: 27

Patterns Found: deploy, docker, helm, service

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
scripts/deploy/orchestrate.sh
```
### documentation-system
Score: 0.6747

Components:
- Functionality: 0.75
- Consistency: 0.9323943661971831
- Tests: 0.0028169014084507044
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- config_count: 1
- markdown_count: 353
- rst_count: 0
- total_docs: 355

Patterns Found: docs, markdown, mkdocs

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
Score: 0.4061

Components:
- Functionality: 0.0
- Consistency: 0.7634560906515581
- Tests: 0.3123229461756374
- Safeguards: 1.0
- Documentation: 0.16853932584269662


Patterns Found: None

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
Score: 0.8050

Components:
- Functionality: 1.0
- Consistency: 0.9
- Tests: 0.5
- Safeguards: 0.6666666666666666
- Documentation: 1.0


Patterns Found: metric, perplexity

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
- Functionality: 1.0
- Consistency: 0.7631578947368421
- Tests: 0.37719298245614036
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- experiment_utils: 13
- metadata_files: 67
- mlflow_integration: 32
- wandb_integration: 4

Patterns Found: experiment, metadata, mlflow, tracking, wandb

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
Score: 0.5900

Components:
- Functionality: 0.5
- Consistency: 0.8888888888888888
- Tests: 0.3333333333333333
- Safeguards: 0.6666666666666666
- Documentation: 0.6928838951310861

Meta:
- layer: serving

Patterns Found: server

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
- Functionality: 1.0
- Consistency: 0.8149606299212598
- Tests: 0.3188976377952756
- Safeguards: 1.0
- Documentation: 1.0


Patterns Found: log, mlflow

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
Score: 0.7100

Components:
- Functionality: 1.0
- Consistency: 0.8673469387755102
- Tests: 0.4897959183673469
- Safeguards: 1.0
- Documentation: 0.09363295880149812


Patterns Found: LoraConfig, get_peft_model, lora, peft, prepare_model_for_kbit_training

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
- Functionality: 1.0
- Consistency: 0.8823529411764706
- Tests: 0.6323529411764706
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- determinism_configs: 5
- integrity_validation: 27
- repro_utils: 16
- seed_management: 25

Patterns Found: deterministic, reproducibility, rng_state, seed, sha256

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
Score: 0.6599

Components:
- Functionality: 1.0
- Consistency: 0.8410852713178294
- Tests: 0.28811369509043927
- Safeguards: 1.0
- Documentation: 0.13108614232209737


Patterns Found: WANDB_MODE, checksum, offline, rng, seed, sha256

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
Score: 0.7441

Components:
- Functionality: 1.0
- Consistency: 0.8936170212765957
- Tests: 0.3617021276595745
- Safeguards: 0.5
- Documentation: 1.0


Patterns Found: sanitize, secret

Evidence Files (first 10):
```
.codex/evidence/phase5_privacy_safety.jsonl
artifacts/security/safety.txt
configs/base/safety/policy.yaml
docs/guides/CHECKPOINT_SAFETY.md
docs/modules/safety.md
docs/safety.md
docs/safety/differential_privacy.md
docs/safety/moderation_adapter.md
docs/safety/policy_guidance.md
docs/safety/safety_guide.md
```
### testing-infrastructure
Score: 0.9147

Components:
- Functionality: 0.75
- Consistency: 0.9003397508493771
- Tests: 0.9886749716874292
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- config_count: 25
- fixture_count: 27
- test_count: 867

Patterns Found: fixture, pytest, test_

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
- Functionality: 1.0
- Consistency: 0.8333333333333334
- Tests: 0.5196078431372549
- Safeguards: 0.6666666666666666
- Documentation: 1.0


Patterns Found: encode, tokenizer

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
- Functionality: 1.0
- Consistency: 0.8656716417910448
- Tests: 0.44776119402985076
- Safeguards: 1.0
- Documentation: 1.0


Patterns Found: epoch, train

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
- Functionality: 1.0
- Consistency: 0.6
- Tests: 1.0
- Safeguards: 0.5
- Documentation: 1.0

Meta:
- category: training

Patterns Found: UnifiedTrainingConfig, run_unified_training

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

Embedded Template SHA256: 7202b060fae306041a38f55fb49bd172b4fd1a57988e590c3a8fe9050dd5d536

*End of Matrix*