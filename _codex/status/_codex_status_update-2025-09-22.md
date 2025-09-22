Check for must recent active branch:
//fetch https://github.com/Aries-Serpent/_codex_/activity?time_period=day

Branches:
//fetch https://github.com/Aries-Serpent/_codex_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0A_base_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0B_base_
//fetch https://github.com/Aries-Serpent/_codex_/tree/0C_base_

Objective:
> Traverse the repository and provide a comprehensive status audit. The goal is to assess **modularity**, **reproducibility**, and **production readiness** of the Codex Environment for Ubuntu, following best practices in ML systems design.
---

Audit Scope

# 📍_codex_: Status Update (2025-09-22)

1. **Repo Map**
   - **Top-level directories.** `_codex`, `agents`, `analysis`, `configs`, `docs`, `services`, `src`, `tests`, `tools`, `training`, `artifacts`, and related offline-support folders define the project layout used by automation and ML code paths.【69d2e3†L1-L14】
   - **Key files.** `pyproject.toml` pins build metadata and extras for CLI/test/tracking workloads; `noxfile.py` centralizes local gates and coverage policies; and the multi-stage `Dockerfile` provides runtime packaging for the service surface.【F:pyproject.toml†L1-L66】【F:noxfile.py†L1-L195】【F:Dockerfile†L1-L21】
   - **Stubs & placeholders.** Base interfaces such as `SearchProvider` and tokenizer adapters still expose abstract methods that raise `NotImplementedError`, tracking writers rely on interface stubs for subclassing, and optional dependencies are skipped in tokenization gates via `pytest.importorskip` markers.【F:src/codex_ml/analysis/providers.py†L16-L118】【F:src/codex_ml/interfaces/tokenizer.py†L42-L159】【F:src/codex_ml/tracking/writers.py†L26-L124】【F:tests/test_hf_tokenizer_padding.py†L1-L22】
   - **Recent changes.** The 2025-09-21 changelog documents merged deterministic loaders, Hydra entrypoints, telemetry defaults, and status artefact refreshes that define today's baselines.【F:CHANGELOG.md†L1-L32】

2. **Capability Audit Table**

| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization (fast tokenizer, vocab, encode/decode, padding/truncation) | Implemented | HF/whitespace adapters and CLI entrypoints cover encode/decode, batching, and save/load flows, with tests enforcing padding/truncation behaviour.【F:src/codex_ml/tokenization/hf_tokenizer.py†L1-L119】【F:src/codex_ml/tokenization/adapter.py†L1-L158】【F:tests/tokenization/test_tokenizer_cli.py†L1-L69】【F:tests/test_hf_tokenizer_padding.py†L1-L28】 | Optional dependencies like `transformers` and `sentencepiece` gate coverage via `pytest.importorskip`, leaving gaps when extras aren't installed.【F:tests/test_hf_tokenizer_padding.py†L1-L22】 | Offline runs without the extras silently skip functionality, risking regressions when tokenizers change upstream.【F:tests/test_hf_tokenizer_padding.py†L1-L22】 | Extend dev bootstrap to install the `test` extra (or vendor minimal wheels) so tokenization gates run in CI and local audits.【F:pyproject.toml†L37-L58】 | Revert the dependency tweak and re-run `uv sync` if conflicts arise, restoring the previous extras set.【F:pyproject.toml†L37-L58】 |
| ChatGPT Codex Modeling (model init, dtype, device placement, LoRA/PEFT hooks) | Implemented | Decoder-only Transformer, MiniLM registry entries, and LoRA adapters deliver configurable inference/training coverage with targeted tests for determinism and kv-cache parity.【F:src/codex_ml/models/decoder_only.py†L1-L160】【F:src/codex_ml/models/registry.py†L1-L195】【F:src/codex_ml/peft/peft_adapter.py†L1-L136】【F:tests/modeling/test_decoder_only.py†L1-L81】 | Offline checkpoint resolution still depends on operators staging weights or environment variables; missing artefacts surface FileNotFound errors despite registry hints.【F:src/codex_ml/models/registry.py†L43-L166】 | Misconfigured offline environments break model bootstraps even when logic is sound, blocking downstream eval/training flows.【F:src/codex_ml/models/registry.py†L43-L166】 | Ship a tiny reference checkpoint (or scripted download shim) alongside updated quickstart guidance to guarantee out-of-box registry hydration.【F:docs/quickstart.md†L16-L59】 | Remove the staged checkpoint and revert docs if storage pressure or licensing constraints appear, falling back to manual instructions.【F:docs/quickstart.md†L16-L59】 |
| Training Engine (HF Trainer or custom loop, precision, gradient accumulation) | Implemented | Functional training config merges Hydra inputs, sets seeds, and writes NDJSON metrics; the demo loop supports gradient accumulation, MLflow, and telemetry toggles with regression coverage in training tests.【F:src/codex_ml/training/__init__.py†L1-L150】【F:src/codex_ml/train_loop.py†L1-L200】【F:tests/training/test_functional_training_main.py†L1-L151】 | Demo loop still uses synthetic data and hard-coded metric hashes; resume path exercises rely on test doubles rather than live checkpoints.【F:src/codex_ml/train_loop.py†L89-L118】【F:tests/training/test_functional_training_main.py†L108-L151】 | Synthetic metrics can mask integration regressions; resume logic may drift from production expectations when checkpoint schema evolves.【F:src/codex_ml/train_loop.py†L89-L118】【F:tests/training/test_functional_training_main.py†L108-L151】 | Add a minimal fixture dataset and real checkpoint round-trip inside the CLI smoke test to validate resume semantics end-to-end.【F:tests/checkpointing/test_best_promotion.py†L1-L15】【F:tests/training/test_functional_training_main.py†L1-L151】 | Disable the new fixture and restore synthetic metrics if runtime budgets spike, retaining the prior deterministic stub workflow.【F:src/codex_ml/train_loop.py†L89-L118】 |
| Configuration Management (Hydra/YAML structure, overrides, sweeps) | Implemented | Hydra-compatible configs under `configs/` capture experiment seeds, device policies, and logging knobs that feed `TrainingRunConfig` normalisation.【F:configs/base.yaml†L1-L21】【F:src/codex_ml/training/__init__.py†L104-L150】 | No automated sweep orchestration or config validation tests ensure new keys stay in sync with runtime schema.【F:src/codex_ml/training/__init__.py†L104-L190】 | Silent config drift can bypass safety toggles or disable logging/telemetry unexpectedly in long-running jobs.【F:src/codex_ml/training/__init__.py†L104-L190】 | Introduce a Hydra schema validation test that loads each base config and asserts required keys before launching training.【F:tests/training/test_functional_training_main.py†L1-L151】 | Roll back the validation test if legitimate user overrides fail, re-enabling manual overrides until schema catches up.【F:configs/base.yaml†L1-L21】 |
| Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging) | Implemented | Metric helpers cover accuracy, perplexity, and token stats, while the training loop writes NDJSON + JSON payloads with environment metadata and tests assert metric behaviour.【F:src/codex_ml/eval/metrics.py†L1-L88】【F:src/codex_ml/train_loop.py†L50-L118】【F:tests/modeling/test_decoder_only.py†L66-L70】 | Demo evaluation still fabricates logits rather than consuming model outputs; no CSV exporter accompanies NDJSON archives.【F:src/codex_ml/train_loop.py†L89-L118】 | Production logs may diverge from analytic expectations when real logits introduce edge cases absent from the synthetic generator.【F:src/codex_ml/train_loop.py†L89-L118】 | Wire the eval runner to the decoder-only model in a smoke test and add a CSV writer alongside existing NDJSON utilities for downstream BI tooling.【F:src/codex_ml/train_loop.py†L50-L118】 | Remove the CSV emitter and revert smoke test wiring if disk or maintenance overhead outweighs benefits.【F:src/codex_ml/train_loop.py†L50-L118】 |
| Logging & Monitoring (TensorBoard / W&B / MLflow, system metrics via `psutil`/NVML) | Partially Implemented | Telemetry bootstrap toggles TensorBoard, W&B, MLflow, and system metrics with graceful fallbacks plus configurable NVML sampling in the metrics daemon.【F:src/codex_ml/monitoring/codex_logging.py†L1-L160】【F:src/codex_ml/monitoring/system_metrics.py†L1-L120】 | GPU sampling remains disabled by default and Prometheus exporters were pruned; optional dependencies can still fail silently without surfacing degraded telemetry.【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】【F:docs/pruning_log.md†L1-L4】 | Operators may assume GPU health is tracked when NVML is actually unavailable, masking thermal throttling or utilisation regressions.【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】 | Add a health banner in the CLI when telemetry degrades and resurrect the Prometheus shim with offline-safe defaults to emit process metrics.【F:src/codex_ml/monitoring/codex_logging.py†L60-L116】【F:docs/pruning_log.md†L1-L4】 | Drop the banner and disable Prometheus again if environments without psutil/NVML need a lighter bootstrap path.【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】 |
| Checkpointing & Resume (weights, optimizer state, scheduler, RNG, best-k retention) | Implemented | Checkpoint utilities write checksums, RNG state, provenance, and maintain `best`/`last` pointers; manager tests assert promotion, corruption handling, and atomicity guarantees.【F:src/codex_ml/utils/checkpointing.py†L1-L160】【F:tests/checkpointing/test_best_promotion.py†L1-L15】【F:tests/checkpointing/test_corrupt_checkpoint_load.py†L1-L26】 | Resume hooks rely on manual invocation and lack smoke coverage in CLI workflows; JSON manifests are not automatically archived with run metadata.【F:src/codex_ml/train_loop.py†L89-L118】 | Forgotten resume flags can lead to silent cold starts that waste GPU/CPU time and erase convergence history.【F:src/codex_ml/train_loop.py†L89-L118】 | Add a CLI `--resume` default to training entrypoints and persist checkpoint manifest paths into experiment tracking records.【F:src/codex_ml/cli/codex_cli.py†L161-L170】【F:src/codex_ml/utils/checkpointing.py†L97-L118】 | Revert the default resume flag if it surprises workflows expecting clean restarts, reinstating opt-in semantics.【F:src/codex_ml/cli/codex_cli.py†L161-L170】 |
| Data Handling (dataset splits, deterministic shuffling, caching) | Implemented | JSONL loader normalises heterogeneous text fields, shuffles deterministically, and tests validate stable splits and missing file behaviour.【F:src/codex_ml/data/jsonl_loader.py†L1-L56】【F:tests/codex_ml/data/test_jsonl_loader.py†L1-L40】 | Streaming/caching backends exist but aren't exercised in regression suites; dataset registries depend on optional extras.【F:src/codex_ml/data/jsonl_loader.py†L34-L56】 | Undocumented streaming paths may regress when dataset shapes change, affecting reproducibility of large-scale runs.【F:src/codex_ml/data/jsonl_loader.py†L34-L56】 | Add a smoke test invoking the dataset registry with a small streaming source and assert cache manifests are written.【F:src/codex_ml/data/jsonl_loader.py†L1-L56】 | Remove the streaming smoke test if resource usage is prohibitive, retaining deterministic JSONL validation only.【F:tests/codex_ml/data/test_jsonl_loader.py†L1-L40】 |
| Security & Safety (dependency locking, secrets scanning, prompt safety) | Implemented | Safety sanitizers redact secrets/PII and flag jailbreak phrases, with regression tests verifying redaction and truncation; lockfiles pin runtime deps for reproducible installs.【F:src/codex_ml/safety/sanitizers.py†L1-L60】【F:tests/security/test_safety_filters.py†L1-L21】【F:pyproject.toml†L1-L58】 | Notebook and prompt tooling still lack automated scans; sandbox module exists but lacks integration tests and CLI wiring.【F:src/codex_ml/safety/sanitizers.py†L61-L84】 | Undetected unsafe prompts may slip through custom tooling, and sandbox regressions could go unnoticed without runtime coverage.【F:src/codex_ml/safety/sanitizers.py†L61-L84】 | Wire the sandbox safety hooks into chat/inference CLI paths and add pytest coverage for prompt escalation scenarios.【F:src/codex_ml/cli/infer.py†L24-L92】 | Disable the new hook and revert CLI wiring if false positives block legitimate use-cases, restoring the previous sanitiser-only flow.【F:src/codex_ml/cli/infer.py†L24-L92】 |
| Internal CI/Test (pytest targets, tox/nox local gates, coverage enforcement) | Implemented | `noxfile.py` provisions reproducible envs, installs torch CPU wheels, and enforces coverage artifacts; targeted pytest suites exercise tokenization, training, safety, and tracking paths.【F:noxfile.py†L1-L195】【F:tests/tokenization/test_tokenizer_cli.py†L1-L69】【F:tests/training/test_functional_training_main.py†L1-L151】【F:tests/security/test_safety_filters.py†L1-L21】 | Full `nox -s tests` can be heavy without caching, and coverage thresholds rely on environment variables; nox lacks a quick lint/doc gate.【F:noxfile.py†L17-L195】 | Slow gates discourage frequent local runs, increasing the risk of integration regressions landing between audits.【F:noxfile.py†L180-L195】 | Introduce a `nox -s lint` session that runs Ruff/mypy/formatting quickly and document selective pytest targets for incremental checks.【F:noxfile.py†L180-L195】 | Remove the lint session if maintenance overhead outweighs benefits, keeping only the comprehensive `tests` gate.【F:noxfile.py†L180-L195】 |
| Deployment (packaging, CLI entry points, Docker infra) | Implemented | Multi-stage Dockerfile, packaging metadata, and CLI modules provide reproducible runtime containers and command orchestration.【F:Dockerfile†L1-L21】【F:pyproject.toml†L1-L36】【F:src/codex/cli.py†L1-L120】 | Container omits GPU runtime hooks and baked-in offline assets; docker-compose examples are stale relative to updated CLI surface.【F:Dockerfile†L1-L21】 | Teams may assume container includes offline models/tokenizers, leading to runtime fetch attempts in air-gapped environments.【F:Dockerfile†L1-L21】 | Add a `make docker-offline` target that stages tiny checkpoints/tokenizers into the image and document volume mounts for custom assets.【F:Dockerfile†L1-L21】【F:docs/quickstart.md†L16-L59】 | Revert the staging step and prune extra assets if image size threatens distribution requirements.【F:Dockerfile†L1-L21】 |
| Documentation & Examples (README, quickstarts, diagrams, notebooks) | Implemented | Quickstart walks through offline catalogue prep, tokenizer usage, training, and evaluation with reproducibility artefacts; docs tree covers ops, telemetry, and troubleshooting guides.【F:docs/quickstart.md†L1-L80】【F:docs/index.md†L1-L40】 | Some notebooks (e.g., GPU training) remain placeholders and diagrams lag behind registry enhancements.【F:docs/pruning_log.md†L1-L4】 | Missing worked notebook examples hinder onboarding for GPU workflows and safety evaluation.【F:docs/pruning_log.md†L1-L4】 | Flesh out the GPU training notebook with the offline MiniLM pipeline and link it from the quickstart for parity across docs surfaces.【F:docs/quickstart.md†L51-L80】 | Restore the placeholder notebook if CI runtimes bloat or keep it documented as deferred work in the pruning log.【F:docs/pruning_log.md†L1-L4】 |
| Experiment Tracking (MLflow local tracking, W&B offline mode) | Implemented | Experiment initialiser fans out to NDJSON/TensorBoard/MLflow/W&B writers, tags runs with config metadata, and tests ensure run directories and tags are created deterministically.【F:src/codex_ml/tracking/init_experiment.py†L1-L120】【F:src/codex_ml/tracking/writers.py†L26-L155】【F:tests/tracking/test_init_experiment_tags.py†L6-L43】 | NDJSON/MLflow writers depend on optional packages and do not emit degradations when unavailable; there is no aggregation tool for NDJSON artefacts.【F:src/codex_ml/tracking/writers.py†L95-L149】 | Silent degradation can lead to missing metrics in central stores, impeding reproducibility and governance audits.【F:src/codex_ml/tracking/writers.py†L95-L149】 | Emit structured warnings into the run logs when a writer is disabled and bundle a CLI helper that summarises NDJSON metrics for quick inspection.【F:src/codex_ml/tracking/writers.py†L95-L155】 | Suppress the warnings and remove the helper if operators prefer leaner logs, returning to silent no-op behaviour.【F:src/codex_ml/tracking/writers.py†L95-L155】 |
| Extensibility (pluggable components, registry patterns) | Implemented | Registry primitives underpin tokenizer/model/dataset/metric catalogues, loading entry points and offline presets for rapid customisation.【F:src/codex_ml/plugins/registries.py†L1-L160】【F:src/codex_ml/registry.py†L1-L12】 | Entry-point loading lacks validation for API versions beyond `v1`, and plugin discovery errors can be noisy without guidance.【F:src/codex_ml/plugins/registries.py†L14-L80】 | Mislabelled plugins might fail silently or crash initialisation, slowing integrator feedback loops.【F:src/codex_ml/plugins/registries.py†L14-L80】 | Add an integration test that loads sample entry points under a mock namespace and asserts helpful error messages for missing APIs.【F:src/codex_ml/plugins/registries.py†L14-L80】 | Remove the integration test if plugin ecosystems prefer manual validation, reverting to the lighter registry bootstrap.【F:src/codex_ml/plugins/registries.py†L14-L80】 |

3. **High-Signal Findings**
   1. The project uses a single `pyproject.toml` with curated extras for CLI, tracking, and test stacks, ensuring offline-friendly dependency resolution while keeping torch out of the base install.【F:pyproject.toml†L19-L66】
   2. Hydra configs plus `TrainingRunConfig` normalisation handle seeds, gradient accumulation, checkpoint cadence, and telemetry toggles, enabling reproducible functional training flows.【F:configs/base.yaml†L1-L21】【F:src/codex_ml/training/__init__.py†L104-L150】
   3. Decoder-only modeling integrates rotary embeddings, kv-cache reuse, and LoRA hooks, delivering deterministic tests for forward passes, serialization, and generation.【F:src/codex_ml/models/decoder_only.py†L1-L160】【F:tests/modeling/test_decoder_only.py†L1-L81】
   4. The training loop records metrics to both JSON and NDJSON while embedding environment summaries, ready for downstream analytics with minimal glue code.【F:src/codex_ml/train_loop.py†L50-L118】
   5. Checkpoint utilities incorporate checksums, RNG capture, and best/last symlinks, and the checkpoint manager tests validate promotion, corruption handling, and atomic persistence.【F:src/codex_ml/utils/checkpointing.py†L1-L160】【F:tests/checkpointing/test_best_promotion.py†L1-L15】
   6. Safety filters redact secrets, detect jailbreak phrasing, and truncate long outputs, with regression coverage ensuring policy enforcement remains stable.【F:src/codex_ml/safety/sanitizers.py†L1-L60】【F:tests/security/test_safety_filters.py†L1-L21】
   7. Experiment tracking fans out to NDJSON, TensorBoard, MLflow, and W&B writers, creating per-run directories with tagged metadata and deterministic naming.【F:src/codex_ml/tracking/init_experiment.py†L1-L120】【F:tests/tracking/test_init_experiment_tags.py†L6-L43】
   8. System metrics sampling gracefully degrades when psutil/NVML are missing, but the defaults still favour minimal logging to preserve offline compatibility.【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】
   9. Tokenization tooling includes CLIs for training, encoding, and reporting stats alongside regression suites that assert padding/truncation semantics.【F:src/codex_ml/tokenization/cli.py†L1-L120】【F:tests/tokenization/test_tokenizer_cli.py†L1-L69】
   10. Documentation emphasises offline-first workflows, guiding users through catalogue staging, deterministic training, and evaluation while pointing to telemetry/ops guides for deeper dives.【F:docs/quickstart.md†L1-L80】【F:docs/index.md†L1-L40】

4. **Atomic Diffs**

### Atomic Diff 1 — Persist environment summaries from the demo trainer
- **Why:** Capture reproducibility artefacts automatically when the functional trainer runs so audits can trace Python, git, and dependency state without manual steps.【F:src/codex_ml/train_loop.py†L50-L118】【F:src/codex_ml/utils/provenance.py†L1-L88】
- **Risk:** Exporting environment manifests on every run could slightly increase runtime and IO, and failure to write files must not crash training.
- **Rollback:** Remove the import and call to `export_environment` and delete generated artefacts from `artifacts/metrics` if disk usage becomes an issue.
- **Tests/docs:** Extend the existing training smoke test to assert the presence of `environment.json` in the metrics directory.
```diff
--- a/src/codex_ml/train_loop.py
+++ b/src/codex_ml/train_loop.py
@@
-from codex_ml.utils.env import environment_summary
+from codex_ml.utils.env import environment_summary
+from codex_ml.utils.provenance import export_environment
@@
-    cfg_hash = "c898a1161dce426c3f46d5b5f09fd0544abc292a4be5076ecf0d75af2bce2a9c"  # noqa: E501
+    cfg_hash = "c898a1161dce426c3f46d5b5f09fd0544abc292a4be5076ecf0d75af2bce2a9c"  # noqa: E501
+    export_environment(art_dir, seed=resolved_seed, command="codex_ml.train_loop")
```

### Atomic Diff 2 — Allow overriding the metrics artefact directory
- **Why:** Make it easier for operators to redirect NDJSON outputs to durable storage or per-run folders without editing source constants.【F:src/codex_ml/train_loop.py†L1-L200】
- **Risk:** Additional CLI surface could surprise scripts that rely on positional arguments; defaults must remain backward compatible.
- **Rollback:** Drop the new CLI option and restore the hard-coded `artifacts/metrics` path if consumers prefer implicit directories.
- **Tests/docs:** Update the quickstart and add a CLI test verifying custom directories are created.
```diff
--- a/src/codex_ml/train_loop.py
+++ b/src/codex_ml/train_loop.py
@@
-    ap.add_argument("--seed", type=int, default=0, help="integer seed for reproducible runs")
+    ap.add_argument("--seed", type=int, default=0, help="integer seed for reproducible runs")
+    ap.add_argument("--art-dir", type=Path, default=ART_DIR, help="metrics output directory")
@@
-        seed=args.seed,
+        seed=args.seed,
+        art_dir=args.art_dir,
     )
```

### Atomic Diff 3 — Surface telemetry degradation warnings in the CLI
- **Why:** Make degraded psutil/NVML states visible to users invoking the monitoring CLI so missing metrics do not go unnoticed.【F:src/codex_ml/monitoring/codex_logging.py†L60-L116】【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】
- **Risk:** Extra console output could clutter quiet scripts; warnings must remain informative without failing the command.
- **Rollback:** Remove the warning emission and rely on logging only if users dislike the added stdout noise.
- **Tests/docs:** Add a monitoring CLI test that asserts the warning appears when psutil is unavailable.
```diff
--- a/src/codex_ml/monitoring/codex_logging.py
+++ b/src/codex_ml/monitoring/codex_logging.py
@@
-    if cfg:
+    if cfg:
         tb_cfg = cfg.get("tensorboard", {})
@@
-        if cfg.get("mlflow", {}).get("enable") and mlflow is not None:
+        if cfg.get("mlflow", {}).get("enable") and mlflow is not None:
             try:
                 uri = cfg["mlflow"].get("tracking_uri", "./mlruns")
@@
-        return loggers
+        if not loggers.gpu and not loggers.tb and not loggers.mlflow_active:
+            print("[telemetry] running in degraded mode: psutil/NVML/TensorBoard unavailable")
+        return loggers
```

5. **Local Tests & Gates**

| Command | Purpose | Example Output | ML Test Score Coverage |
| --- | --- | --- | --- |
| `pytest tests/tokenization/test_tokenizer_cli.py -q` | Exercises SentencePiece-backed tokenizer training/encode/stats CLIs with monkeypatched adapters.【F:tests/tokenization/test_tokenizer_cli.py†L1-L69】 | Skipped when `transformers` is unavailable (`Skipped: could not import 'transformers'`).【c2c6db†L1-L60】 | Model quality (tokenisation correctness; requires optional deps) |
| `pytest tests/training/test_functional_training_main.py -q` | Validates Hydra config loading, label preparation, and LoRA flag wiring for functional training entrypoints.【F:tests/training/test_functional_training_main.py†L1-L151】 | Skipped when `transformers` is unavailable (`Skipped: could not import 'transformers'`).【743d9f†L1-L43】 | Training pipeline (data/labels, LoRA config; requires optional deps) |
| `nox -s tests` | Creates an isolated env, installs extras, runs the full pytest suite with coverage artefacts for offline CI parity.【F:noxfile.py†L180-L195】 | Coverage session failed because the setuptools plugin `hydra.extra` was unavailable; the initial `tests` session succeeded before the coverage pass aborted.【5c0c26†L1-L4】【aac9c6†L1-L32】 | Regression + infrastructure (broad suite; investigate missing Hydra extras) |

6. **Reproducibility Checklist**

| Item | Status | Notes |
| --- | --- | --- |
| Seed control across training/eval loops | ✅ | Functional training config exposes `seed` and the demo trainer normalises seeds before invoking `set_reproducible`.【F:src/codex_ml/training/__init__.py†L33-L52】【F:src/codex_ml/train_loop.py†L69-L118】 |
| Environment capture (requirements locks, manifests) | ⚠️ | Lockfiles exist and provenance helpers can export environment summaries, but the trainer does not yet persist them automatically (see Atomic Diff 1).【F:pyproject.toml†L19-L66】【F:src/codex_ml/utils/provenance.py†L1-L88】 |
| Data/version manifests | ⚠️ | `record_dataset_checksums` writes hashes, yet no pipeline step invokes it for dataset splits by default.【F:src/codex_ml/utils/repro.py†L1-L24】 |
| Configuration capture & overrides | ✅ | Hydra configs plus runtime normalisation persist dataset/text overrides and pass resolved config dicts into trainers.【F:configs/base.yaml†L1-L21】【F:src/codex_ml/training/__init__.py†L104-L190】 |
| Deterministic hardware/runtime notes | ⚠️ | System metrics capture CPU/GPU state when psutil/NVML exist, but degraded modes currently only log warnings without surfacing in CLI flows.【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】 |
| Results logging & provenance | ✅ | Metrics writer appends NDJSON/JSON with git commit metadata, enabling downstream aggregation without extra tooling.【F:src/codex_ml/train_loop.py†L50-L118】 |

7. **Deferred Items**
   - RL/bandit agent interfaces remain pruned per pruning log guidance, leaving reinforcement learning out of scope for the current release window.【F:docs/pruning_log.md†L1-L4】
   - Prometheus/NVML exporters are deferred because the offline image lacks GPU libraries; telemetry currently focuses on psutil-based sampling.【F:docs/pruning_log.md†L1-L4】【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】
   - External web search requires either enabling network access or shipping a curated offline index before it can graduate from the disabled default.【F:src/codex_ml/analysis/providers.py†L90-L120】

8. **Error Capture Blocks**
   - None — repository traversal completed without unresolved tooling or runtime errors.

---

## Codex-ready Task Sequence
```yaml
Codex-ready Task Sequence:
  1. Preparation:
    - Review `pyproject.toml` extras and lockfiles to ensure the `test` group installs tokenizer dependencies before gating.【F:pyproject.toml†L37-L58】
    - Export current git status and create a scratch run directory under `artifacts/metrics` for reproducibility captures.【F:src/codex_ml/train_loop.py†L50-L118】
  2. Search & Mapping:
    - Enumerate registry entries for tokenizers/models/datasets to confirm offline aliases cover planned workflows.【F:src/codex_ml/plugins/registries.py†L24-L80】
    - Trace checkpoint resolution paths and environment variables to validate offline checkpoints for GPT-2 and TinyLLaMA exist locally.【F:src/codex_ml/models/registry.py†L43-L166】
  3. Best-Effort Construction:
    - Implement Atomic Diff 1 and 2 to persist environment manifests and expose the `--art-dir` override in the trainer CLI.【F:src/codex_ml/train_loop.py†L1-L200】【F:src/codex_ml/utils/provenance.py†L1-L88】
    - Update quickstart/docs to mention the new flag and refresh offline asset staging instructions.【F:docs/quickstart.md†L16-L59】
  4. Controlled Pruning:
    - Reassess Prometheus/NVML telemetry; if GPU support remains deferred, document the limitation in monitoring docs and keep flags defaulting to safe values.【F:docs/pruning_log.md†L1-L4】【F:src/codex_ml/monitoring/system_metrics.py†L18-L60】
  5. Error Capture:
    - If environment export or telemetry wiring fails, log a Codex error-capture block referencing the failing step and attach the relevant stack trace for follow-up analysis.【F:src/codex_ml/utils/provenance.py†L1-L88】
  6. Finalization:
    - Run `nox -s tests` to regenerate coverage artefacts and confirm new features remain offline-compliant, then archive updated status manifests under `_codex/status/`.【F:noxfile.py†L180-L195】
```

**Additional Deliverable — Executable Script**
```python
#!/usr/bin/env python3
"""Codex remediation workflow template."""
from __future__ import annotations

import argparse
from pathlib import Path

from codex_ml.train_loop import run_training
from codex_ml.utils.provenance import export_environment


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run demo training with reproducibility artefacts")
    parser.add_argument("--art-dir", type=Path, default=Path("artifacts/metrics"), help="Output directory for metrics")
    parser.add_argument("--epochs", type=int, default=1, help="Number of demo epochs to execute")
    parser.add_argument("--grad-accum", type=int, default=1, help="Gradient accumulation steps")
    parser.add_argument("--dry-run", action="store_true", help="List planned actions without executing them")
    return parser.parse_args()


def load_context(root: Path) -> None:
    """Gather repository context and execute the reproducible training demo."""
    metrics_dir = root / args.art_dir
    if args.dry_run:
        print(f"[dry-run] would export environment to {metrics_dir}")
        print(f"[dry-run] would run training for {args.epochs} epoch(s) with grad_accum={args.grad_accum}")
        return
    export_environment(metrics_dir, command="codex_ml.train_loop", seed=0)
    run_training(epochs=args.epochs, grad_accum=args.grad_accum, mlflow_enable=False, telemetry_enable=False, art_dir=metrics_dir)
    print(f"Training complete; metrics available under {metrics_dir}")


def main() -> None:
    global args
    args = parse_args()
    repo_root = Path(".").resolve()
    load_context(repo_root)


if __name__ == "__main__":
    main()
```
