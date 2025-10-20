# [Report]: Capability Matrix
> Generated: 2025-10-20 04:05:53 UTC | Author: audit_system
 Roles: [Primary: Automated Auditor], [Secondary: Provenance Engine]  Energy: 5

## 1. Summary
Total Capabilities: 17
Low Maturity (< 0.45 heuristic): 3

## 2. Capability Scores
| ID | Score | Functionality | Consistency | Tests | Safeguards | Docs | Evidence Count |
|----|-------|--------------:|------------:|------:|-----------:|-----:|---------------:|
| checkpointing | 0.87 | 1.00 | 0.90 | 0.68 | 0.83 | 1.00 | 96 |
| ci-cd-pipeline | 0.88 | 1.00 | 0.91 | 0.60 | 1.00 | 1.00 | 168 |
| code-quality-tooling | 0.85 | 1.00 | 0.88 | 0.58 | 0.83 | 1.00 | 129 |
| configuration | 0.72 | 1.00 | 0.76 | 0.28 | 0.67 | 1.00 | 134 |
| data-pipeline | 0.81 | 1.00 | 0.86 | 0.44 | 0.83 | 1.00 | 129 |
| deployment-infrastructure | 0.58 | 0.80 | 0.83 | 0.07 | 0.33 | 1.00 | 29 |
| documentation-system | 0.68 | 0.75 | 0.93 | 0.00 | 1.00 | 1.00 | 245 |
| evaluation-metrics | 0.82 | 1.00 | 0.90 | 0.57 | 0.67 | 1.00 | 67 |
| experiment-management | 0.79 | 1.00 | 0.76 | 0.37 | 1.00 | 1.00 | 112 |
| inference-serving | 0.46 | 0.50 | 0.89 | 0.33 | 0.00 | 0.46 | 9 |
| logging-tracking | 0.79 | 1.00 | 0.82 | 0.30 | 1.00 | 1.00 | 261 |
| reproducibility | 0.85 | 1.00 | 0.90 | 0.59 | 0.83 | 1.00 | 68 |
| safety-security | 0.74 | 1.00 | 0.88 | 0.35 | 0.50 | 1.00 | 43 |
| testing-infrastructure | 0.91 | 0.75 | 0.89 | 0.99 | 1.00 | 1.00 | 806 |
| tokenization | 0.79 | 1.00 | 0.85 | 0.48 | 0.67 | 1.00 | 106 |
| training-engine | 0.85 | 1.00 | 0.88 | 0.51 | 1.00 | 1.00 | 158 |
| unified-training | 0.80 | 1.00 | 0.60 | 1.00 | 0.50 | 0.70 | 5 |

## 3. Low Maturity Focus
| ID | Score | Primary Deficit |
|----|-------|-----------------|
| deployment-infrastructure | 0.58 | tests |
| documentation-system | 0.68 | tests |
| inference-serving | 0.46 | safeguards |

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
Score: 0.8734

Components:
- Functionality: 1.0
- Consistency: 0.8958333333333334
- Tests: 0.6770833333333334
- Safeguards: 0.8333333333333334
- Documentation: 1.0


Patterns Found: load, save_checkpoint

Evidence Files (first 10):
```text
codex_ml/utils/checkpointing.py
docs/CHECKPOINTS.md
docs/checkpoint_integrity.md
docs/checkpoint_schema_v2.md
docs/guides/CHECKPOINT_SAFETY.md
docs/how-to/checkpoint_metadata.md
docs/modules/checkpoint_manager.md
docs/training/Checkpointing_Surfaces.md
documentation/checkpointing_README.md
great_expectations/checkpoints/clean_checkpoint.yml
```text
### ci-cd-pipeline
Score: 0.8810

Components:
- Functionality: 1.0
- Consistency: 0.9107142857142857
- Tests: 0.5952380952380952
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- ci_configs: 2
- github_actions: 3
- note: GitHub Actions present but not activated per AGENTS.md
- pre_commit_hooks: 3
- validation_scripts: 160

Patterns Found: automation, ci, pre-commit, validation, workflow

Evidence Files (first 10):
```text
.codex/smoke/import_check.py
.github/workflows/archive-gates.yml.disabled
.github/workflows/ci.yml.disabled
.github/workflows/validate.yml.disabled
.pre-commit-config.yaml
.pre-commit-hybrid.yaml
.pre-commit-ruff.yaml
analysis/audit_pipeline.py
analysis/tests_docs_links_audit.py
audit_runner.py
```text
### code-quality-tooling
Score: 0.8455

Components:
- Functionality: 1.0
- Consistency: 0.875968992248062
- Tests: 0.5813953488372093
- Safeguards: 0.8333333333333334
- Documentation: 1.0

Meta:
- formatters: 2
- linters: 3
- quality_scripts: 28
- security_scanners: 92
- type_checkers: 7

Patterns Found: format, lint, quality, security-scan, type-check

Evidence Files (first 10):
```text
.bandit.yml
.codex/ruff.json
.editorconfig
.pre-commit-ruff.yaml
agents/codex_client/pyproject.toml
artifacts/security/bandit.txt
artifacts/security/detect-secrets.txt
artifacts/security/safety.txt
bandit.yaml
configs/safety/policy.yaml
```text
### configuration
Score: 0.7213

Components:
- Functionality: 1.0
- Consistency: 0.7611940298507462
- Tests: 0.27611940298507465
- Safeguards: 0.6666666666666666
- Documentation: 1.0


Patterns Found: config, hydra

Evidence Files (first 10):
```text
.codex/copilot_bridge/config/bridge.config.json
.codex/hydra_last/config.yaml
.editorconfig
.github/docs/ARCHIVE_CONFIG_ADR.md
.pre-commit-config.yaml
agents/codex_client/codex_client/config.py
agents/codex_client/tests/test_config.py
commitlint.config.mjs
conf/config.yaml
conf/examples/config_minimal.yaml
```text
### data-pipeline
Score: 0.8076

Components:
- Functionality: 1.0
- Consistency: 0.8604651162790697
- Tests: 0.4418604651162791
- Safeguards: 0.8333333333333334
- Documentation: 1.0


Patterns Found: loader, split

Evidence Files (first 10):
```text
codex_ml/data/checksums.py
configs/data/base.yaml
configs/data/offline/tiny_corpus.yaml
configs/data/tiny.yaml
data/.gitkeep
data/models/.gitkeep
data/offline/length_reward.json
data/offline/tiny_corpus.txt
data/offline/trainer_functional.json
data/offline/weighted_accuracy.json
```text
### deployment-infrastructure
Score: 0.5828

Components:
- Functionality: 0.8
- Consistency: 0.8275862068965517
- Tests: 0.06896551724137931
- Safeguards: 0.3333333333333333
- Documentation: 1.0

Meta:
- deploy_scripts: 1
- docker_configs: 4
- helm_charts: 2
- k8s_manifests: 0
- service_definitions: 22

Patterns Found: deploy, docker, helm, service

Evidence Files (first 10):
```text
.dockerignore
Dockerfile
Dockerfile.gpu
deploy/helm/Chart.yaml
deploy/helm/values.yaml
docker-compose.yml
scripts/deploy/orchestrate.sh
services/__init__.py
services/api/__init__.py
services/api/main.py
```text
### documentation-system
Score: 0.6755

Components:
- Functionality: 0.75
- Consistency: 0.9346938775510204
- Tests: 0.004081632653061225
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- config_count: 1
- markdown_count: 241
- rst_count: 0
- total_docs: 245

Patterns Found: docs, markdown, mkdocs

Evidence Files (first 10):
```text
CHANGELOG.md
CONTRIBUTING.md
README.md
docs/CHECKPOINTS.md
docs/CLI.md
docs/CONTRIBUTING.md
docs/FollowUp_Implementation_Plan.md
docs/Implementation_Update_merged.md
docs/LOGGING.md
docs/PR_PLAN.md
```text
### evaluation-metrics
Score: 0.8209

Components:
- Functionality: 1.0
- Consistency: 0.8955223880597015
- Tests: 0.5671641791044776
- Safeguards: 0.6666666666666666
- Documentation: 1.0


Patterns Found: metric, perplexity

Evidence Files (first 10):
```text
configs/eval/base.yaml
configs/eval/default.yaml
configs/evaluate/default.yaml
docs/examples/eval_metrics.md
docs/modules/evaluation_runner.md
docs/training/Evaluation_CLI.md
docs/training/Evaluation_CLI_Addendum.md
examples/evaluate_toy.py
examples/notebooks/demo_train_eval.ipynb
patches/pending/2025-09-21_eval_loop.patch
```text
### experiment-management
Score: 0.7933

Components:
- Functionality: 1.0
- Consistency: 0.7589285714285714
- Tests: 0.36607142857142855
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- experiment_utils: 12
- metadata_files: 66
- mlflow_integration: 34
- wandb_integration: 2

Patterns Found: experiment, metadata, mlflow, tracking, wandb

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
Score: 0.4557

Components:
- Functionality: 0.5
- Consistency: 0.8888888888888888
- Tests: 0.3333333333333333
- Safeguards: 0.0
- Documentation: 0.46391752577319584

Meta:
- layer: serving

Patterns Found: server

Evidence Files (first 10):
```text
src/codex_ml/telemetry/server.py
src/hhg_logistics/monitor/serve_report.py
src/hhg_logistics/serve/__init__.py
src/hhg_logistics/serve/app.py
src/hhg_logistics/serve/smoke.py
temp/bridge_codex_copilot_bridge/mcp/server/main.py
temp/bridge_codex_copilot_bridge/mcp/server/server.py
tests/hhg_logistics/serve/test_app.py
tests/telemetry/test_metrics_server.py
```text
### logging-tracking
Score: 0.7877

Components:
- Functionality: 1.0
- Consistency: 0.8199233716475096
- Tests: 0.2950191570881226
- Safeguards: 1.0
- Documentation: 1.0


Patterns Found: log, mlflow

Evidence Files (first 10):
```text
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
```text
### reproducibility
Score: 0.8515

Components:
- Functionality: 1.0
- Consistency: 0.8970588235294118
- Tests: 0.5882352941176471
- Safeguards: 0.8333333333333334
- Documentation: 1.0

Meta:
- determinism_configs: 5
- integrity_validation: 32
- repro_utils: 12
- seed_management: 24

Patterns Found: deterministic, reproducibility, rng_state, seed, sha256

Evidence Files (first 10):
```text
.codex/cache/maint_vendor_hash_post.json
.codex/cache/maint_vendor_hash_pre_sync.json
.codex/cache/vendor_hash_post_purge.json
.codex/cache/vendor_hash_pre_sync.json
.codex/validation/file_integrity_compare.json
_codex_reports/2025-10-06/reproducibility.json
_codex_reports/2025-10-06/seed_scan.json
codex_ml/data/checksums.py
configs/deterministic.yaml
docs/checkpoint_integrity.md
```text
### safety-security
Score: 0.7390

Components:
- Functionality: 1.0
- Consistency: 0.8837209302325582
- Tests: 0.3488372093023256
- Safeguards: 0.5
- Documentation: 1.0


Patterns Found: sanitize, secret

Evidence Files (first 10):
```text
artifacts/security/safety.txt
configs/safety/policy.yaml
docs/guides/CHECKPOINT_SAFETY.md
docs/modules/safety.md
docs/safety.md
docs/safety/policy_guidance.md
docs/safety_api.md
documentation/safety_README.md
examples/safety/policy_bypass_example.yaml
src/codex_ml/safety/__init__.py
```text
### testing-infrastructure
Score: 0.9130

Components:
- Functionality: 0.75
- Consistency: 0.8945409429280398
- Tests: 0.9863523573200993
- Safeguards: 1.0
- Documentation: 1.0

Meta:
- config_count: 25
- fixture_count: 27
- test_count: 790

Patterns Found: fixture, pytest, test_

Evidence Files (first 10):
```text
__pycache__/conftest.cpython-312-pytest-8.4.1.pyc
agents/codex_client/pyproject.toml
configs/offline/tiny_fixtures.yaml
conftest.py
pyproject.toml
pytest.ini
services/ita/pyproject.toml
temp/bridge_codex_copilot_bridge/agents/codex_client/pyproject.toml
temp/bridge_codex_copilot_bridge/mcp/server/pyproject.toml
temp/bridge_codex_copilot_bridge/services/ita/pyproject.toml
```text
### tokenization
Score: 0.7901

Components:
- Functionality: 1.0
- Consistency: 0.8490566037735849
- Tests: 0.4811320754716981
- Safeguards: 0.6666666666666666
- Documentation: 1.0


Patterns Found: encode, tokenizer

Evidence Files (first 10):
```text
_codex_reports/2025-10-06/tokenizer_check.json
artifacts/models/tiny_tokenizer/vocab.json
codex_digest/tokenizer.py
configs/tokenization/base.yaml
configs/tokenizer/multilingual.yaml
configs/tokenizer/offline/gpt2.yaml
configs/tokenizer/offline/tiny_vocab.yaml
configs/tokenizer/offline/tinyllama.yaml
configs/train_tokenizer.yaml
docs/guides/tokenization.md
```text
### training-engine
Score: 0.8541

Components:
- Functionality: 1.0
- Consistency: 0.879746835443038
- Tests: 0.5126582278481012
- Safeguards: 1.0
- Documentation: 1.0


Patterns Found: epoch, train

Evidence Files (first 10):
```text
_codex_reports/2025-10-06/trainer_smoke.json
_codex_reports/2025-10-06/trainer_smoke.log
artifacts/diffs/training_py01_removal.md
conf/trainer/base.yaml
configs/train/default.yaml
configs/train/small.yaml
configs/train_tokenizer.yaml
configs/training/base.yaml
configs/training/functional_base.yaml
configs/training/offline/functional.yaml
```text
### unified-training
Score: 0.7994

Components:
- Functionality: 1.0
- Consistency: 0.6
- Tests: 1.0
- Safeguards: 0.5
- Documentation: 0.6958762886597938

Meta:
- category: training

Patterns Found: UnifiedTrainingConfig, run_unified_training

Evidence Files (first 10):
```text
scripts/space_traversal/detectors/unified_training.py
src/codex_ml/detectors/unified_training.py
src/codex_ml/training/unified_training.py
tests/detectors/test_unified_training.py
tools/bench_unified_training.py
```text

## 6. Appendix
| Field | Description |
|-------|-------------|
| template_hash | Hash of concatenated Jinja templates |
| generation_strategy | Weighted component aggregation |
| scoring_components | functionality, consistency, tests, safeguards, documentation |

Embedded Template SHA256: 7202b060fae306041a38f55fb49bd172b4fd1a57988e590c3a8fe9050dd5d536

*End of Matrix*
