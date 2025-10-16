# 📍_codex_: Status Update (2025-10-16)

## 1. Repo Map
- **Top-level layout.** Major directories include application source under `src/`, extensive test suites in `tests/`, Hydra/OmegaConf configuration bundles in `configs/`, documentation in `docs/`, operational scripts in `scripts/`, deployment assets (Dockerfiles, compose files), and tooling such as `noxfile.py`, `Makefile`, and lockfiles (`requirements.lock`, `uv.lock`).【f77d60†L1-L36】
- **Key runtime modules.** Core training stack spans tokenisation adapters (`src/codex_ml/tokenization`), model initialisation (`src/modeling.py`), data utilities (`src/codex_ml/data`), training loops (`src/training` and `src/codex_ml/training`), logging/monitoring helpers (`src/logging_utils.py`, `src/codex_ml/monitoring`), configuration shims (`src/codex_ml/config`), and CLI entry points (`src/codex_ml/cli`).【f87461†L1-L200】【de0ac1†L1-L200】【1095b8†L1-L134】【2b1c54†L1-L240】【12e9d5†L1-L200】【9fc136†L1-L160】
- **Test coverage.** The `tests/` tree contains granular suites for tokenizers, trainers, logging, reproducibility, security, pipeline integrations, and CLI smoke runs, indicating a mature offline validation harness.【b41597†L1-L95】【8cf38f†L1-L88】【2bdcba†L1-L118】【62612b†L1-L40】【7a914f†L1-L23】
- **Stubs & deferred code.** Abstract interfaces such as `TokenizerProtocol` and `TrainableTokenizerProtocol` still raise `NotImplementedError`, signalling extension points requiring downstream implementation. Additional NotImplemented hooks exist across interface packages (e.g., reward/RL agents) and deferred tooling pipelines referenced in earlier audits.【e566f6†L220-L276】

## 2. Capability Audit Table

| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization (fast tokenizer, vocab, encode/decode, padding/truncation) | Implemented | HF/whitespace/SentencePiece adapters with config factory, cached encode helpers, NDJSON writers; round-trip padding tests.【f87461†L1-L200】【8cf38f†L1-L88】 | Protocols still expose NotImplemented scaffolds; legacy adapters rely on optional deps without local stubs.【e566f6†L220-L276】 | Downstream packages importing protocol methods directly may trigger runtime errors if concrete adapters aren’t registered. | Provide a thin default implementation for `TokenizerProtocol` delegating to `TokenizerAdapter` when registered; add guard tests ensuring registry yields concrete implementations. | Revert helper module to previous abstract behaviour using `git revert <commit>` if adapters conflict with custom downstream implementations. |
| ChatGPT Codex Modeling (model init, dtype, device placement, LoRA/PEFT hooks) | Implemented | Centralised `ModelInitConfig` resolves dtype/device, integrates PEFT LoRA, and loads HF models with trust_remote_code controls; CLI wiring via Hydra config defaults.【de0ac1†L1-L200】【ce75a8†L1-L28】 | No CPU/GPU availability probing before dtype selection; LoRA path lacks offline smoke coverage; trust_remote_code defaults to false but lacks allowlist. | Misconfigured dtype on unsupported hardware can fail late; LoRA misconfiguration may silently skip adaptation. | Add device capability probe (torch.cuda/bf16) with explicit error; extend tests to cover LoRA config mapping using dummy PEFT stub. | Revert new checks by restoring prior `_resolve_dtype/_resolve_device` logic if they block environments lacking torch. |
| Training Engine (HF Trainer or custom loop, precision, gradient accumulation) | Implemented | Extended trainer adds AMP, gradient accumulation, checkpoint retention, validation metrics, with tests for grad accumulation and retention behaviour.【2b1c54†L1-L240】【2bdcba†L51-L118】 | No automatic resume-from-last-checkpoint path; AMP/scaler coverage limited to CPU tests; SimpleTrainer still CPU-only. | Unexpected power loss could lose state; enabling mixed precision without CUDA guard may crash. | Add resume helper that scans checkpoint dir, loads newest payload, and integrates RNG restoration tests. | Revert resume helper if it interferes with manual resume flows by removing new loader module. |
| Configuration Management (Hydra/YAML structure, overrides, sweeps) | Implemented | Hydra defaults with `_self_` merges, structured CLI entry that merges YAML defaults, OmegaConf conversions, and deterministic config snapshots.【ce75a8†L1-L33】【9fc136†L52-L149】 | No explicit sweep orchestration; defaults rely on external Hydra config registration; limited validation of user overrides beyond dataclass validation. | Config drift between CLI defaults and YAML may cause surprise merges; missing sweep templates slows experimentation. | Introduce `configs/sweeps` templates plus validation test ensuring overrides surface errors; expose CLI flag to dump merged config. | Remove new sweep configs and CLI flag if they complicate minimal offline runs. |
| Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging) | Implemented | Metric helpers (accuracy, cross-entropy, perplexity), NDJSON/CSV writers, evaluation CLI, tests verifying NDJSON and metrics logging.【b47127†L1-L23】【216af9†L1-L38】【62612b†L1-L40】 | No unified evaluation registry for multi-task metrics; NDJSON append lacks schema versioning; evaluation logs not deduplicated. | Inconsistent metric names hamper dashboards; corrupted NDJSON could break ingestion. | Add schema version + JSON schema validation; create metric registry manifest linking evaluation tasks to metrics. | Revert schema enforcement if pipelines expect free-form NDJSON by removing validation hook. |
| Logging & Monitoring (TensorBoard / W&B / MLflow, system metrics via psutil/NVML) | Implemented | Optional TB/MLflow initialisation with offline defaults, system metrics sampler with env-driven fallbacks, tests ensuring offline mlflow/tb behave, monitoring CLI shims.【12e9d5†L1-L200】【c58490†L1-L200】【62612b†L17-L40】 | Lacks WandB integration beyond config flag; psutil/pynvml absence only logged, no degrade telemetry file; GPU metrics disabled by default. | Production observability degraded if psutil missing; partial mlflow initialisation may leak runs. | Add JSONL fallback writer capturing minimal metrics when psutil unavailable; integrate WandB offline stub behind flag. | Remove fallback writer if it inflates disk usage by deleting new JSONL emission code. |
| Checkpointing & Resume (weights, optimizer state, scheduler, RNG, best-k retention) | Implemented | Checkpoint save/load storing RNG states, retention utilities, trainer wiring, tests verifying best-k, RNG restoration.【85459d†L1-L200】【2bdcba†L51-L118】 | No metadata schema versioning; resume path manual; cross-device map_location defaults to CPU without detection. | Restoring GPU checkpoints on CPU may misconfigure optimizer; metadata drift could break older checkpoints. | Add metadata JSON schema with version tag; implement resume helper respecting `map_location` CLI argument. | Revert by deleting schema enforcement and helper if compatibility issues surface. |
| Data Handling (dataset splits, deterministic shuffling, caching) | Implemented | Deterministic split utilities with env-seed overrides, JSONL loader/caching modules, DVC stage definitions for logistics pipeline, dataset checksum capture in reproducibility helpers.【1095b8†L1-L134】【f12ef7†L1-L18】【996dc9†L59-L88】 | No manifest for dataset provenance beyond DVC; large dataset streaming/backpressure policies unclear. | Incorrect seeds or dataset absence may only fail at runtime; caching lacking TTL may stale. | Extend dataset registry to emit manifest+checksums, add tests covering cache eviction. | Revert registry change by restoring original loader if breakage occurs. |
| Security & Safety (dependency locking, secrets scanning, prompt safety) | Partially Implemented | Secrets scanner CLI with pattern checks and tests, security utilities for secret rotation, lockfiles for dependencies.【cf15b8†L1-L84】【48642d†L1-L17】【677bc7†L1-L88】【71109d†L1-L18】 | Prompt safety modules sparse; no automated dependency vulnerability audit; scanner ignores binary formats only superficially. | Secrets may slip through zipped artifacts; lack of policy enforcement for prompt filters. | Add CI-equivalent offline `bandit`/`pip-audit` sessions; extend scanner to parse ZIP/TAR; document prompt safety baseline. | Revert scanner enhancements by removing new archive parsing if perf regresses. |
| Internal CI/Test (pytest targets, tox/nox local gates, coverage enforcement) | Implemented | `pytest.ini` with coverage fail-under and markers, `noxfile.py` providing reusable sessions with coverage JSON export, make targets for debt scanning.【bb3029†L1-L41】【677bae†L1-L120】 | No tox config parity with nox sessions; coverage floor moderate (70%); GPU tests gated externally. | Without GPU gating, devs may skip high-cost tests; coverage floor might allow regressions. | Add lightweight tox.ini delegating to nox; raise coverage threshold gradually with historical data. | Remove tox shim if duplication confuses contributors. |
| Deployment (packaging, CLI entry points, Docker infra) | Implemented | Multi-stage Dockerfile (GPU & CPU), pyproject scripts exposing CLI entry points, docker-compose overrides, `setup_universal.sh` etc.【947b1b†L1-L40】【7070dd†L1-L120】 | Dockerfile installs editable package without pinning extras; runtime image lacks health endpoint for CLI mode; compose stack not validated. | Editable install may break offline build caching; missing runtime entrypoint tests. | Update Dockerfile to install from wheel with hashed requirements; add smoke test verifying CLI healthcheck. | Revert by switching back to editable install if wheel step fails. |
| Documentation & Examples (README, quickstarts, diagrams, notebooks) | Implemented | README with quickstart, evaluation logging instructions, docs tree with CLI guide, notebooks under `notebooks/`, mkdocs config.【17c849†L1-L70】 | Some docs outdated (LoRA mention without step-by-step), diagrams not regenerated; notebooks not validated in CI. | Users may follow stale instructions; notebooks diverge from actual API. | Add doc build + notebook smoke session in nox; update README to reference new resume helper and reproducibility scripts. | Revert doc additions if they cause merge conflicts by restoring prior README. |
| Experiment Tracking (MLflow local tracking, W&B offline mode) | Partially Implemented | Logging utils default to offline MLflow, `mlflow_run` context, monitoring MLflow guard; CLI flags for logging enablement.【12e9d5†L86-L191】【cf5cc3†L1-L75】 | W&B flag currently inert; no run metadata summariser; lacks experiment manifest aggregator. | Missing metadata may hinder reproducibility; W&B enabling fails silently. | Implement `wandb_offline` adapter writing local summaries; add tests verifying manual run id propagation. | Revert adapter if optional dependency not available by toggling feature flag default. |
| Extensibility (pluggable components, registry patterns) | Implemented | Entry points for tokenizers, models, trainers; registry loaders for analysis providers, data loaders, Hydra config registration; plugin tests.【7070dd†L121-L171】【a1b00d†L17-L138】 | Some registries rely on optional packages; plugin discovery errors not surfaced cleanly; NotImplemented stubs still present. | Silent plugin failures degrade functionality; user-supplied plugin errors may mask root cause. | Harden registry loader to raise structured errors; add CLI `codex list-plugins` health check verifying entry points. | Revert error-hardening if third-party plugins expect silent failure. |

## 3. High-Signal Findings
1. Tokenizer protocols still raise `NotImplementedError`, risking runtime crashes for callers expecting concrete behaviours.【e566f6†L220-L276】
2. Model initialisation lacks device capability probes, so requesting bf16 on unsupported CPUs fails late.【de0ac1†L74-L155】
3. Extended trainer provides best-k retention but cannot resume automatically from latest checkpoint, complicating fault recovery.【2b1c54†L121-L240】
4. Hydra CLI merges defaults but lacks sweep scaffolding or override validation to catch typos early.【ce75a8†L1-L28】【9fc136†L52-L149】
5. NDJSON evaluation logging omits schema metadata, making downstream ingestion brittle.【216af9†L11-L38】
6. Logging utils degrade gracefully but do not persist fallback metrics when psutil/pynvml missing, reducing observability.【12e9d5†L37-L200】【c58490†L1-L200】
7. Checkpoint metadata lacks schema versioning, risking incompatibility as payload evolves.【85459d†L57-L118】
8. Dataset provenance tracked via DVC but runtime loaders do not emit manifest/checksum snapshots automatically.【f12ef7†L1-L18】【996dc9†L59-L88】
9. Secrets scanner ignores archives, leaving zip-packaged credentials undetected.【cf15b8†L21-L80】
10. Coverage floor fixed at 70%, leaving room for untested regressions despite broad suites.【bb3029†L11-L28】
11. W&B toggle is declared but lacks implementation, confusing users expecting offline tracking.【12e9d5†L37-L149】
12. Docker image installs editable package, which can be fragile in production pipelines compared to wheel installs.【947b1b†L1-L38】
13. Notebook/doc pipelines have no automated execution guard, so published examples may drift.【17c849†L1-L70】
14. Plugin registry error handling is permissive, hiding misconfigured entry points.【7070dd†L121-L171】
15. BF16 capability guard missing from modeling despite config flag in training config referencing requirement.【980aee†L1-L40】

## 4. Atomic Diffs
1. **Guard tokenizer protocols**
   ```diff
   diff --git a/src/codex_ml/interfaces/tokenizer.py b/src/codex_ml/interfaces/tokenizer.py
   @@
   -    def encode(...):
   -        raise NotImplementedError
   +    def encode(...):
   +        raise RuntimeError("TokenizerProtocol must be backed by a registered adapter")
   ```
   - *Why*: Provide actionable runtime message instead of abstract stub when protocol used directly, aiding debugging.【e566f6†L220-L276】
   - *Risk*: Projects relying on catching `NotImplementedError` must adjust.
   - *Rollback*: `git revert` the change set to restore original abstract behaviour.
   - *Tests/docs*: Extend `tests/test_interfaces_compat.py` to assert informative error message.

2. **Add device capability probe in modeling**
   ```diff
   diff --git a/src/modeling.py b/src/modeling.py
   @@
   -    if not name:
   -        return torch.float32
   +    if not name:
   +        return torch.float32
   +    if name.lower() in {"bf16", "bfloat16"} and not torch.cuda.is_bf16_supported():
   +        raise RuntimeError("Requested bf16 but CUDA device lacks support")
   ```
   - *Why*: Surface unsupported bf16 early, aligning with `training.reproducibility.bf16_require_capability` flag.【de0ac1†L74-L155】【980aee†L31-L40】
   - *Risk*: Environments without CUDA but requesting bf16 will now raise earlier.
   - *Rollback*: Remove capability check and reintroduce previous logic.
   - *Tests/docs*: Add unit test covering bf16 guard in `tests/test_modeling_utils.py` and README note.

3. **Auto-resume helper for extended trainer**
   ```diff
   diff --git a/src/training/trainer.py b/src/training/trainer.py
   @@
       def __init__(...):
           ...
+        if cfg.checkpoint and cfg.checkpoint.directory:
+            latest = self._find_latest_checkpoint(cfg.checkpoint.directory)
+            if latest is not None:
+                self._load_checkpoint(latest)
   ```
   - *Why*: Enables fault-tolerant restarts using existing checkpoint metadata.【2b1c54†L171-L186】【85459d†L86-L118】
   - *Risk*: Incorrect detection may reload stale checkpoints.
   - *Rollback*: Remove `_find_latest_checkpoint` helper to disable auto-resume.
   - *Tests/docs*: Add regression test in `tests/test_resume_training.py` verifying resume behaviour; update training docs.

4. **NDJSON schema versioning**
   ```diff
   diff --git a/src/evaluation/writers.py b/src/evaluation/writers.py
   @@
   -def write_ndjson(records, path):
   +def write_ndjson(records, path, *, schema_version="v1"):
   +    metadata = {"schema_version": schema_version}
   ```
   - *Why*: Embed schema info to ease ingestion compatibility.【216af9†L11-L38】
   - *Risk*: Downstream consumers expecting raw dicts must ignore new field.
   - *Rollback*: Revert function signature to remove metadata injection.
   - *Tests/docs*: Update `tests/test_ndjson_writer.py`; document schema semantics.

5. **Fallback metrics JSONL writer**
   ```diff
   diff --git a/src/logging_utils.py b/src/logging_utils.py
   @@
   +class FallbackMetricsWriter:
   +    def __init__(self, path: Path):
   +        self.path = path
   +    def write(self, metrics, step):
   +        payload = {"ts": time.time(), "step": step, "metrics": metrics}
   +        with self.path.open("a", encoding="utf-8") as handle:
   +            handle.write(json.dumps(payload) + "\n")
   ```
   - *Why*: Retain minimal telemetry when psutil unavailable.【12e9d5†L151-L182】【c58490†L85-L200】
   - *Risk*: Disk usage growth if metrics frequent.
   - *Rollback*: Delete fallback writer usage.
   - *Tests/docs*: Add smoke test under `tests/test_logging_utils.py` verifying JSONL creation; document path in LOGGING.md.

6. **Dataset manifest emission**
   ```diff
   diff --git a/src/codex_ml/data/split_utils.py b/src/codex_ml/data/split_utils.py
   @@
       return SplitPaths(...)
+    record_dataset_checksums([train_path, val_path, test_path], Path(out_dir)/"split_checksums.json")
   ```
   - *Why*: Persist reproducibility metadata alongside generated splits.【1095b8†L47-L90】【996dc9†L59-L88】
   - *Risk*: Additional IO may slow massive datasets.
   - *Rollback*: Remove checksum call if overhead unacceptable.
   - *Tests/docs*: Extend `tests/test_dataset_manifest.py` to assert checksum file exists; note path in docs.

7. **Archive-aware secrets scanner**
   ```diff
   diff --git a/tools/scan_secrets.py b/tools/scan_secrets.py
   @@
   -    if candidate.is_dir():
   +    if candidate.is_dir():
   +        targets.extend(_iter_archive_members(candidate))
   ```
   - *Why*: Detect secrets packaged inside zip/tar artifacts.【cf15b8†L33-L80】
   - *Risk*: Archive parsing may be slow; needs careful error handling.
   - *Rollback*: Revert archive iteration helper.
   - *Tests/docs*: Add fixture in `tests/test_secrets_scanner.py` covering zipped secrets; update README security section.

## 5. Local Tests & Gates
- **Recommended gating commands:**
  - ✅ `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/test_trainer_extended.py tests/test_resume_training.py` (Model & training coverage — *ML Test Score: model, regression*).【2bdcba†L51-L118】
  - ✅ `nox -s coverage -- tests/test_ndjson_writer.py tests/test_logging_utils.py` (Evaluation/logging regressions — *ML Test Score: infrastructure, regression*).【677bae†L73-L120】
  - ✅ `python tools/scan_secrets.py scripts --diff HEAD` (Security regression gate — *ML Test Score: infrastructure, security*).【cf15b8†L1-L84】
  - ✅ `nox -s docs -- positional notebooks/quickstarts` (Documentation determinism — *ML Test Score: infrastructure*).【677bae†L1-L120】【17c849†L1-L70】
  - ⚠️ `nox -s gpu-smoke -- tests/test_system_metrics_logging.py` (GPU metrics optional; skip gracefully when CUDA absent — *ML Test Score: performance*).【c58490†L32-L132】

## 6. Reproducibility Checklist
- [x] **Seeds**: Utilities expose `set_seed`, `set_reproducible`, deterministic splits default to env-controlled seeds.【996dc9†L22-L57】【1095b8†L33-L90】
- [x] **Environment capture**: `capture_environment` records pip freeze + env vars with secret redaction.【996dc9†L59-L88】
- [x] **Code versioning**: Git-based workflow with lockfiles (`requirements.lock`, `uv.lock`) ensures pinned deps.【71109d†L1-L18】
- [ ] **Hardware determinism**: No automatic capability checks for bf16/AMP; needs hardware gating (gap flagged above).【de0ac1†L74-L155】
- [ ] **Results determinism validation**: No nightly pipeline verifying run-to-run equivalence; rely on unit tests only.
- [ ] **Dataset manifests**: Generation manual via DVC; runtime pipelines do not automatically emit checksums (planned in Atomic Diff #6).【f12ef7†L1-L18】

## 7. Deferred Items
- **Tokenizer protocol defaults**: Historically left abstract to enforce explicit adapter registration; change requires stakeholder agreement to avoid breaking plugin assumptions. Recommend targeted RFC with interface owners before implementation (see Atomic Diff #1).
- **W&B integration**: Optional due to licence/policy constraints; low priority until offline-friendly stub ready.
- **GPU telemetry**: NVML optional; enabling by default increases dependency footprint. Defer until GPU deployment targeted.
- **Notebook execution**: Full execution gating costly; consider partial sampling or docstring-based tests in future work.

## 8. Error Capture Blocks
_No blocking errors encountered during analysis; no remediation queries required._

## 9. Automation Evidence (`scripts/codex_ready_execution.py`)
- **Command**: `python scripts/codex_ready_execution.py`
- **Timestamp**: 2025-10-16T14:16:27.555370+00:00 (UTC)
- **README placeholders**: `README.md` still contains the placeholder link token `](#)`; no sanitized copy was produced.
- **Change log artifact**: `artifacts/codex_ready/change_log.jsonl` updated with the execution metadata.
- **Pattern scan**: 106 total matches recorded; top 50 surfaced in `artifacts/codex_ready/summary.json` covering TODO/NotImplemented references across codex automation tooling (e.g., `codex_task_sequence.py`, `.codex/codex_repo_scout.py`, `tools/apply_interfaces.py`).
- **Follow-up**: Use the summary file to prioritise resolving automation stubs before implementing new safeguards.
