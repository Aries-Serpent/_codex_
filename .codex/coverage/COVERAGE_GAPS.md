# Coverage Gaps Index — codex repository
> **Generated:** 2026-03-30T19:22:24Z  | **SHA:** `d2d9565`  | **Overall:** 10.5%
> **Suites:** s240

<!-- AUTO-GENERATED — do not edit manually; see generate_coverage_map.py -->

## Quick Summary

| Stat | Value |
|------|-------|
| Total modules measured | 175 |
| Overall line rate | 10.5% |
| Modules with 0% coverage | 120 |
| Modules below 50% | 44 |
| Total uncovered functions | 15 |
| High-risk uncovered functions | 15 |

## 🔴 Zero-Coverage Modules

| Module | File | Lines |
|--------|------|-------|
| `codex.chat` | `codex/chat.py` | 37 |
| `codex.cli` | `codex/cli.py` | 276 |
| `codex.logging.config` | `codex/logging/config.py` | 2 |
| `codex.logging.conversation_logger` | `codex/logging/conversation_logger.py` | 51 |
| `codex.logging.db_utils` | `codex/logging/db_utils.py` | 91 |
| `codex.logging.export` | `codex/logging/export.py` | 71 |
| `codex.logging.fetch_messages` | `codex/logging/fetch_messages.py` | 63 |
| `codex.logging.import_ndjson` | `codex/logging/import_ndjson.py` | 107 |
| `codex.logging.query_logs` | `codex/logging/query_logs.py` | 158 |
| `codex.logging.session_hooks` | `codex/logging/session_hooks.py` | 97 |
| `codex.logging.session_logger` | `codex/logging/session_logger.py` | 214 |
| `codex.logging.session_query` | `codex/logging/session_query.py` | 115 |
| `codex.logging.viewer` | `codex/logging/viewer.py` | 145 |
| `codex.search.providers` | `codex/search/providers.py` | 61 |
| `codex.utils.subprocess` | `codex/utils/subprocess.py` | 6 |
| `codex_ml.analysis.extractors` | `codex_ml/analysis/extractors.py` | 45 |
| `codex_ml.analysis.metrics` | `codex_ml/analysis/metrics.py` | 9 |
| `codex_ml.analysis.parsers` | `codex_ml/analysis/parsers.py` | 30 |
| `codex_ml.analysis.providers` | `codex_ml/analysis/providers.py` | 196 |
| `codex_ml.analysis.registry` | `codex_ml/analysis/registry.py` | 14 |
| `codex_ml.callbacks` | `codex_ml/callbacks.py` | 41 |
| `codex_ml.cli.__main__` | `codex_ml/cli/__main__.py` | 1 |
| `codex_ml.cli.audit_pipeline` | `codex_ml/cli/audit_pipeline.py` | 99 |
| `codex_ml.cli.config` | `codex_ml/cli/config.py` | 61 |
| `codex_ml.cli.evaluate` | `codex_ml/cli/evaluate.py` | 98 |
| `codex_ml.cli.generate` | `codex_ml/cli/generate.py` | 60 |
| `codex_ml.cli.hydra_main` | `codex_ml/cli/hydra_main.py` | 17 |
| `codex_ml.cli.infer` | `codex_ml/cli/infer.py` | 57 |
| `codex_ml.cli.list_plugins` | `codex_ml/cli/list_plugins.py` | 19 |
| `codex_ml.cli.plugins_cli` | `codex_ml/cli/plugins_cli.py` | 53 |
| `codex_ml.cli.train` | `codex_ml/cli/train.py` | 116 |
| `codex_ml.cli.validate` | `codex_ml/cli/validate.py` | 79 |
| `codex_ml.config_schema` | `codex_ml/config_schema.py` | 57 |
| `codex_ml.data.cache` | `codex_ml/data/cache.py` | 37 |
| `codex_ml.data.cli` | `codex_ml/data/cli.py` | 24 |
| `codex_ml.data.hf_datasets` | `codex_ml/data/hf_datasets.py` | 27 |
| `codex_ml.data.integrity` | `codex_ml/data/integrity.py` | 14 |
| `codex_ml.data.jsonl_loader` | `codex_ml/data/jsonl_loader.py` | 44 |
| `codex_ml.data.jsonl_stream` | `codex_ml/data/jsonl_stream.py` | 23 |
| `codex_ml.data.loaders` | `codex_ml/data/loaders.py` | 277 |
| `codex_ml.data.registry` | `codex_ml/data/registry.py` | 173 |
| `codex_ml.data.sharding` | `codex_ml/data/sharding.py` | 7 |
| `codex_ml.data.split` | `codex_ml/data/split.py` | 80 |
| `codex_ml.data.split_utils` | `codex_ml/data/split_utils.py` | 71 |
| `codex_ml.data.splits` | `codex_ml/data/splits.py` | 6 |
| `codex_ml.eval.evaluator` | `codex_ml/eval/evaluator.py` | 38 |
| `codex_ml.eval.run_eval` | `codex_ml/eval/run_eval.py` | 60 |
| `codex_ml.hf_loader` | `codex_ml/hf_loader.py` | 116 |
| `codex_ml.logging.ndjson_logger` | `codex_ml/logging/ndjson_logger.py` | 55 |
| `codex_ml.logging.run_logger` | `codex_ml/logging/run_logger.py` | 77 |
| `codex_ml.metrics.curves` | `codex_ml/metrics/curves.py` | 17 |
| `codex_ml.modeling.codex_model_loader` | `codex_ml/modeling/codex_model_loader.py` | 81 |
| `codex_ml.models.activations` | `codex_ml/models/activations.py` | 30 |
| `codex_ml.models.generate` | `codex_ml/models/generate.py` | 39 |
| `codex_ml.models.loader_registry` | `codex_ml/models/loader_registry.py` | 25 |
| `codex_ml.models.offline_tiny` | `codex_ml/models/offline_tiny.py` | 35 |
| `codex_ml.models.utils.peft` | `codex_ml/models/utils/peft.py` | 13 |
| `codex_ml.monitoring.cli` | `codex_ml/monitoring/cli.py` | 40 |
| `codex_ml.monitoring.microhelpers` | `codex_ml/monitoring/microhelpers.py` | 76 |
| `codex_ml.monitoring.mlflow_utils` | `codex_ml/monitoring/mlflow_utils.py` | 23 |
| `codex_ml.monitoring.tb_writer` | `codex_ml/monitoring/tb_writer.py` | 22 |
| `codex_ml.monitoring.tracking` | `codex_ml/monitoring/tracking.py` | 48 |
| `codex_ml.perf.bench` | `codex_ml/perf/bench.py` | 105 |
| `codex_ml.registry` | `codex_ml/registry.py` | 9 |
| `codex_ml.registry.data_loaders` | `codex_ml/registry/data_loaders.py` | 6 |
| `codex_ml.registry.metrics` | `codex_ml/registry/metrics.py` | 3 |
| `codex_ml.registry.models` | `codex_ml/registry/models.py` | 3 |
| `codex_ml.registry.token_cache` | `codex_ml/registry/token_cache.py` | 31 |
| `codex_ml.registry.tokenizers` | `codex_ml/registry/tokenizers.py` | 179 |
| `codex_ml.registry.trainers` | `codex_ml/registry/trainers.py` | 27 |
| `codex_ml.reward_models.rlhf` | `codex_ml/reward_models/rlhf.py` | 138 |
| `codex_ml.reward_models.simple` | `codex_ml/reward_models/simple.py` | 11 |
| `codex_ml.rl.scripted_agent` | `codex_ml/rl/scripted_agent.py` | 45 |
| `codex_ml.rl.simple_agent` | `codex_ml/rl/simple_agent.py` | 15 |
| `codex_ml.safety.risk_score` | `codex_ml/safety/risk_score.py` | 29 |
| `codex_ml.tokenization.adapter` | `codex_ml/tokenization/adapter.py` | 271 |
| `codex_ml.tokenization.cli` | `codex_ml/tokenization/cli.py` | 66 |
| `codex_ml.tokenization.hf_tokenizer` | `codex_ml/tokenization/hf_tokenizer.py` | 56 |
| `codex_ml.tokenization.offline_vocab` | `codex_ml/tokenization/offline_vocab.py` | 34 |
| `codex_ml.tokenization.pipeline` | `codex_ml/tokenization/pipeline.py` | 126 |
| `codex_ml.tokenization.sentencepiece_adapter` | `codex_ml/tokenization/sentencepiece_adapter.py` | 154 |
| `codex_ml.tokenization.train_tokenizer` | `codex_ml/tokenization/train_tokenizer.py` | 11 |
| `codex_ml.tracking.cli` | `codex_ml/tracking/cli.py` | 10 |
| `codex_ml.tracking.git_tag` | `codex_ml/tracking/git_tag.py` | 19 |
| `codex_ml.tracking.init_experiment` | `codex_ml/tracking/init_experiment.py` | 186 |
| `codex_ml.tracking.mlflow_guard` | `codex_ml/tracking/mlflow_guard.py` | 28 |
| `codex_ml.tracking.mlflow_utils` | `codex_ml/tracking/mlflow_utils.py` | 113 |
| `codex_ml.tracking.writers` | `codex_ml/tracking/writers.py` | 141 |
| `codex_ml.train_loop` | `codex_ml/train_loop.py` | 823 |
| `codex_ml.training` | `codex_ml/training.py` | 41 |
| `codex_ml.training.callbacks` | `codex_ml/training/callbacks.py` | 21 |
| `codex_ml.training.dataloader_utils` | `codex_ml/training/dataloader_utils.py` | 10 |
| `codex_ml.training.eval` | `codex_ml/training/eval.py` | 53 |
| `codex_ml.training.functional_training` | `codex_ml/training/functional_training.py` | 265 |
| `codex_ml.utils.checkpoint` | `codex_ml/utils/checkpoint.py` | 317 |
| `codex_ml.utils.checksum` | `codex_ml/utils/checksum.py` | 14 |
| `codex_ml.utils.checksums` | `codex_ml/utils/checksums.py` | 14 |
| `codex_ml.utils.config_loader` | `codex_ml/utils/config_loader.py` | 163 |
| `codex_ml.utils.determinism` | `codex_ml/utils/determinism.py` | 61 |
| `codex_ml.utils.env` | `codex_ml/utils/env.py` | 24 |
| `codex_ml.utils.jsonl` | `codex_ml/utils/jsonl.py` | 10 |
| `codex_ml.utils.logging_mlflow` | `codex_ml/utils/logging_mlflow.py` | 23 |
| `codex_ml.utils.logging_wandb` | `codex_ml/utils/logging_wandb.py` | 13 |
| `codex_ml.utils.modeling` | `codex_ml/utils/modeling.py` | 47 |
| `codex_ml.utils.retention` | `codex_ml/utils/retention.py` | 85 |
| `codex_ml.utils.subproc` | `codex_ml/utils/subproc.py` | 68 |
| `codex_ml.utils.train_helpers` | `codex_ml/utils/train_helpers.py` | 42 |
| `ingestion.csv_ingestor` | `ingestion/csv_ingestor.py` | 12 |
| `ingestion.encoding_detect` | `ingestion/encoding_detect.py` | 71 |
| `ingestion.file_ingestor` | `ingestion/file_ingestor.py` | 9 |
| `ingestion.io_text` | `ingestion/io_text.py` | 81 |
| `ingestion.json_ingestor` | `ingestion/json_ingestor.py` | 11 |
| `ingestion.utils` | `ingestion/utils.py` | 170 |
| `logging_config` | `logging_config.py` | 11 |
| `tokenization.cli` | `tokenization/cli.py` | 62 |
| `tokenization.sentencepiece_adapter` | `tokenization/sentencepiece_adapter.py` | 26 |
| `tokenization.train_tokenizer` | `tokenization/train_tokenizer.py` | 145 |
| `utils.checkpointing` | `utils/checkpointing.py` | 100 |
| `utils.trackers` | `utils/trackers.py` | 20 |
| `utils.training_callbacks` | `utils/training_callbacks.py` | 24 |

## 🟠 Low-Coverage Modules (< 50%)

| Module | Coverage | Uncovered Functions |
|--------|----------|---------------------|
| `codex_ml.safety.sandbox` | 8.0% | — |
| `codex_ml.eval.runner` | 9.5% | — |
| `codex_ml.eval.metrics` | 10.7% | — |
| `codex.training` | 11.2% | — |
| `codex_ml.pipeline` | 12.9% | _load |
| `codex_ml.utils.checkpointing` | 13.4% | — |
| `codex_ml.metrics.evaluator` | 15.0% | — |
| `codex_ml.plugins.loader` | 15.2% | — |
| `codex_ml.data_utils` | 16.7% | — |
| `codex_ml.eval.datasets` | 17.3% | — |
| `codex_ml.data.loader` | 18.2% | — |
| `codex_ml.monitoring.codex_logging` | 20.4% | — |
| `codex_ml.models.registry` | 20.4% | — |
| `codex_ml.plugins.registries` | 21.3% | — |
| `codex_ml.safety.filters` | 21.5% | — |
| `codex_ml.peft.peft_adapter` | 22.2% | — |
| `codex_ml.monitoring.system_metrics` | 23.3% | — |
| `codex_ml.eval.eval_runner` | 23.5% | — |
| `codex_ml.tokenization.sp_trainer` | 24.3% | — |
| `codex_ml.utils.provenance` | 24.4% | — |
| `codex_ml.models.decoder_only` | 24.7% | — |
| `codex_ml.metrics.registry` | 24.7% | — |
| `codex_ml.interfaces.registry` | 26.9% | — |
| `codex_ml.data.checksums` | 26.9% | _sha256_file, manifest_for_paths |
| `codex_ml.utils.error_log` | 27.3% | — |
| `codex_ml.monitoring.async_writer` | 28.4% | — |
| `codex_ml.utils.hf_pinning` | 28.6% | — |
| `codex_ml.interfaces.reward_model` | 28.9% | — |
| `codex_ml.symbolic_pipeline` | 30.2% | — |
| `codex_ml.utils.experiment_tracking_mlflow` | 30.9% | — |
| `codex_ml.safety.sanitizers` | 31.2% | — |
| `codex_ml.interfaces.rl` | 32.0% | — |
| `codex_ml.logging.file_logger` | 32.3% | — |
| `codex_ml.cli.main` | 32.9% | _load |
| `codex_ml.utils.seeding` | 34.9% | — |
| `codex_ml.interfaces.tokenizer` | 35.1% | — |
| `codex_ml.utils.checkpoint_event` | 35.1% | — |
| `codex_ml.models.minilm` | 39.1% | — |
| `codex_ml.monitoring.prometheus` | 39.6% | — |
| `codex_ml.cli.codex_cli` | 41.8% | — |
| `codex_ml.metrics.text` | 42.9% | — |
| `codex_ml.plugins.registry` | 43.8% | — |
| `codex_ml.registry.base` | 45.9% | — |
| `codex_ml.telemetry.metrics` | 47.6% | — |

## 🟡 Partially-Covered Modules (50–90%)

| Module | Coverage | Uncovered Functions |
|--------|----------|---------------------|
| `codex_ml.telemetry.server` | 50.0% | — |
| `codex_ml.utils.artifacts` | 50.0% | — |
| `codex_ml.utils.repro` | 50.0% | — |
| `codex_ml.config` | 50.6% | — |
| `codex_ml.utils.yaml_support` | 52.4% | — |
| `codex_ml.utils.seed` | 60.0% | — |
| `codex_ml.utils.torch_checks` | 61.1% | — |
| `codex_ml.utils.hf_revision` | 63.6% | — |
| `codex_ml.monitoring.schema` | 67.9% | — |
| `codex_ml.utils.optional` | 77.8% | — |

## ⚠️ High-Risk Uncovered Functions

> These functions have < 20% line coverage. Modifying them without
> adding tests first risks introducing undetected regressions.

| Module | Function | Lines | Risk |
|--------|----------|-------|------|
| `codex_ml.cli.main` | `_load` | 21–28 | CRITICAL |
| `codex_ml.data.checksums` | `_sha256_file` | 26–34 | CRITICAL |
| `codex_ml.data.checksums` | `manifest_for_paths` | 37–61 | CRITICAL |
| `codex_ml.pipeline` | `_load` | 22–29 | CRITICAL |
| `codex_ml.tracking.mlflow_utils` | `_load` | 19–26 | CRITICAL |
| `codex_ml.tracking.writers` | `set_output_dir` | 67–72 | CRITICAL |
| `codex_ml.tracking.writers` | `_ensure_default_output_dir` | 75–77 | CRITICAL |
| `codex_ml.tracking.writers` | `log_metrics` | 80–88 | CRITICAL |
| `codex_ml.tracking.writers` | `get_paths` | 91–98 | CRITICAL |
| `codex_ml.tracking.writers` | `__init__` | 28–30 | CRITICAL |
| `codex_ml.tracking.writers` | `write` | 32–35 | CRITICAL |
| `codex_ml.tracking.writers` | `__init__` | 39–43 | CRITICAL |
| `codex_ml.tracking.writers` | `write` | 45–59 | CRITICAL |
| `tokenization.cli` | `_load` | 13–20 | CRITICAL |
| `tokenization.cli` | `_run_app` | 28–42 | CRITICAL |

---

_Generated by `scripts/ci/generate_coverage_map.py`._
_See `.codex/plans/codebase_wide_coverage_plan.md` for the full architecture._
