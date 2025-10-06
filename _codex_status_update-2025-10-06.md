# 📍_codex_: Status Update (2025-10-06)

## 1. Repo Map
- `src/` – core libraries for tokenization, models, training, monitoring, and utilities exposed via the `codex_ml` namespace.【F:pyproject.toml†L103-L119】
- `configs/` – Hydra-compatible defaults for training, logging, safety policies, and offline modes.【F:configs/default.yaml†L1-L20】【F:configs/safety/policy.yaml†L1-L24】
- `tests/` – extensive pytest suite with marker taxonomy covering data, model, infra, and security checks.【F:pytest.ini†L1-L42】
- `docs/` & `README.md` – quickstarts, architecture notes, safety guidance, and tool bootstrap instructions.【F:README.md†L7-L159】
- `training/` – legacy functional trainer reused through registries for lightweight runs and smoke tests.【F:training/functional_training.py†L439-L520】
- `tokenization/` – Typer CLI shim delegating to the packaged tokenizer utilities for offline workflows.【F:tokenization/cli.py†L1-L46】
- Notable stubs / placeholders: `analysis/intuitive_aptitude.py` still emits TODO scaffolds for error-handling code generation, indicating unfinished analysis helpers.【F:analysis/intuitive_aptitude.py†L640-L666】 The base metrics writer also exposes an abstract `write` placeholder pending concrete subclasses.【F:src/codex_ml/metrics/writers.py†L31-L58】

## 2. Capability Audit Table
| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization | Implemented | Registry factories resolve HF/whitespace/offline tokenizers; HF adapter handles special tokens, padding, batch encode/decode; SentencePiece trainer supports streaming corpora.【F:src/codex_ml/registry/tokenizers.py†L1-L199】【F:src/codex_ml/tokenization/hf_tokenizer.py†L44-L173】【F:src/tokenization/train_tokenizer.py†L48-L156】 | No command surfaces available vocab metadata or cache location; error paths force manual env setup when assets missing.【F:src/codex_ml/registry/tokenizers.py†L68-L113】 | Operators may misconfigure offline paths and hit FileNotFoundErrors late in the run. | Add CLI subcommand to list resolved tokenizer assets and health-check offline caches (reusing `_resolve_tokenizer_target`). | Revert CLI extension module if discovery causes regressions; fall back to existing registry-only access. |
| ChatGPT Codex Modeling | Implemented | Model registry with offline-first resolution for GPT-2/TinyLLaMA, dtype/device coercion, and LoRA hooks via `create_model`/`build_lora`.【F:src/codex_ml/models/registry.py†L31-L198】【F:src/codex_ml/models/factory.py†L1-L90】【F:src/codex_ml/models/peft_hooks.py†L1-L29】 | Limited catalog (MiniLM, GPT-2, TinyLLaMA); no quantization/adapter configuration surfaced via config schema. | Deployments needing alternate architectures must fork registry code, risking drift. | Introduce registry metadata file (YAML) to declare supported model aliases and optional quantization flags consumed by Hydra configs. | Remove metadata file and revert config wiring to restore prior behaviour. |
| Training Engine | Implemented | Hydra bridge normalises configs to `TrainingRunConfig`; custom trainer covers checkpoints, safety filters, LoRA, AMP, gradient accumulation, resume support; fallback loop records provenance/metrics when deps missing.【F:src/codex_ml/training/__init__.py†L91-L680】【F:src/codex_ml/training/__init__.py†L820-L1090】【F:src/codex_ml/training/functional_training.py†L1-L484】 | Functional fallback materialises entire dataset tensors in memory and lacks Weights & Biases support despite config flags.【F:src/codex_ml/training/functional_training.py†L176-L189】【F:src/codex_ml/training/functional_training.py†L48-L71】 | Large corpora can OOM during tokenisation; observability parity with MLflow is missing. | Stream tokenisation in configurable chunks and wire `wandb_enable` into the trainer using the existing tracking utilities. | Disable chunked path via config flag and remove W&B hook to restore prior deterministic behaviour. |
| Configuration Management | Partially Implemented | Structured dataclasses registered with Hydra; YAML defaults merged at runtime; CLI exposes overrides per component.【F:src/codex_ml/cli/config.py†L9-L109】【F:src/codex_ml/cli/hydra_main.py†L47-L83】 | No config groups for experiment sweeps or dataset registries; logging config for W&B not propagated to runtime. | Teams duplicate configs per experiment and silently lose logging toggles. | Add Hydra config groups (`experiment`, `data`, `logging`) with schema validation and ensure `logging.wandb_enable` maps to runtime flags. | Remove new groups to fall back to single default file if incompatibilities appear. |
| Evaluation & Metrics | Implemented | Batch evaluator computes loss/token accuracy; metric registry covers perplexity/EM/F1/distinctness/ROUGE/offline weighted accuracy; NDJSON/CSV writers provide structured logging.【F:src/codex_ml/training/eval.py†L1-L89】【F:src/codex_ml/metrics/registry.py†L1-L210】【F:src/codex_ml/metrics/writers.py†L15-L58】 | Base writer is not abstract; inadvertent direct use raises `NotImplementedError` at runtime. | Misconfigured pipelines may crash instead of gracefully no-op logging. | Convert `BaseMetricsWriter` into an abstract base class and add smoke tests ensuring concrete writers are selected. | Revert ABC change to allow legacy imports if incompatibilities arise. |
| Logging & Monitoring | Partially Implemented | MLflow guard enforces local URIs; NDJSON metadata writer records seeds, git, hardware; system metrics sampler handles psutil/NVML flags; TensorBoard wrapper degrades gracefully.【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L1-L135】【F:src/codex_ml/logging/run_metadata.py†L34-L131】【F:src/codex_ml/monitoring/system_metrics.py†L20-L200】【F:src/codex_ml/monitoring/tb_writer.py†L11-L41】 | W&B flag unused; no central tracker orchestrates multi-sink logging in `run_functional_training`. | Critical metrics missing from W&B dashboards reduce production observability. | Instantiate `Tracker` (or lightweight wandb shim) inside training loops when flags are set, mirroring MLflow handling. | Guard new hook behind config flag and disable if wandb import fails. |
| Checkpointing & Resume | Implemented | Snapshot utilities persist model/optimizer/scheduler/RNG with SHA-256 manifests and best-K retention; load path verifies checksums; metadata sidecars include git/environment state.【F:src/codex_ml/utils/checkpointing.py†L434-L520】【F:src/codex_ml/utils/checkpoint.py†L203-L397】 | None observed beyond standard optional dependency guards. | N/A | Continue to rely on existing checksum + RNG capture; add doc snippet to remind operators to copy `.meta.json`. | Use existing rollback: delete new docs. |
| Data Handling | Partially Implemented | Deterministic JSONL loader and split utilities respect seeds/env overrides; safety filtering sanitises prompts/outputs before training; fallback tokenizer builds vocabulary when HF datasets unavailable.【F:src/codex_ml/data/jsonl_loader.py†L13-L72】【F:src/codex_ml/data/split_utils.py†L12-L134】【F:src/codex_ml/training/__init__.py†L820-L880】【F:src/codex_ml/safety/sanitizers.py†L80-L118】 | Training pipeline lacks streaming or memory-mapped ingestion; only JSONL/text supported without caching adapters. | Scaling to multi-GB corpora risks OOM and slow restarts. | Introduce chunked iterators or dataset adapters (HF `Dataset` or WebDataset) toggled via config. | Revert to eager loading for regressions by flipping new flag off. |
| Security & Safety | Implemented | Safety filters enforce allow/block rules with YAML/JSON fallback; sanitizers redact secrets/PII; README documents secret handling and `.env` protections; lockfiles pin dependencies.【F:src/codex_ml/safety/filters.py†L1-L182】【F:src/codex_ml/safety/sanitizers.py†L80-L118】【F:README.md†L81-L123】【F:requirements.lock†L1-L18】 | Automated secret scanning exists in tests but runtime sanitisation bypass via env var lacks telemetry alerting. | Silent bypasses could leak sensitive prompts in logs. | Emit warning events when `CODEX_SAFETY_BYPASS` is set and surface them in NDJSON logs. | Drop warning emission if it proves noisy by reverting the logging call. |
| Internal CI/Test | Implemented | `pytest.ini` enforces markers/seeds; `tox` and `nox` sessions gate coverage, lock refresh, and offline runs; README instructs local gating commands.【F:pytest.ini†L1-L42】【F:tox.ini†L1-L29】【F:noxfile.py†L1-L200】【F:README.md†L97-L139】 | Coverage threshold static (70%); slow tests excluded by default; no GPU smoke gate. | Undetected regressions in GPU-only code paths. | Add optional `nox -s tests_gpu` session guarded by CUDA availability and mark minimal GPU smoke tests. | Remove session from noxfile if GPU envs unavailable. |
| Deployment | Partially Implemented | CPU Dockerfile installs editable package with entrypoint `codex-train`; pyproject defines console scripts for CLIs.【F:Dockerfile†L1-L23】【F:pyproject.toml†L65-L98】 | Docker image lacks pinned extras/lock sync; no docker-compose for multi-service telemetry. | Production containers may miss optional deps (mlflow/wandb) without manual pip install. | Extend Dockerfile to install `[ml,logging]` extras and copy lockfile for reproducible builds. | Revert Dockerfile additions to restore lean base image if size regresses. |
| Documentation & Examples | Implemented | README quickstart, LoRA example, evaluation snippet, architecture mermaid; docs tree with guides referenced.【F:README.md†L7-L151】 | Some guides outdated w.r.t. new registries; no diagram for monitoring stack. | Operators may overlook telemetry setup requirements. | Refresh docs to cover `Tracker`, W&B wiring, and offline metrics directories. | Restore previous docs if confusion arises. |
| Experiment Tracking | Partially Implemented | MLflow guard ensures offline backend; `maybe_mlflow` context manager logs params/metrics/artifacts when enabled.【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L31-L135】 | Tracker facade unused; W&B flags ignored; no NDJSON-to-MLflow sync job. | Divergent experiment logs between NDJSON and tracking tools. | Activate `Tracker` inside training loops and document environment variables for wandb/mlflow parity. | Disable tracker instantiation if issues appear. |
| Extensibility | Implemented | Generic registry infrastructure with entry-point discovery and temporary registration context manager; tokenizers/models/metrics plug into registries.【F:src/codex_ml/registry/base.py†L1-L200】【F:src/codex_ml/registry/tokenizers.py†L1-L199】【F:src/codex_ml/models/registry.py†L31-L198】 | No registry health command; conflict diagnostics not surfaced in CLI. | Plugin load failures may remain hidden until runtime. | Add `codex-list-plugins` extensions to report failed entry points and sources. | Remove command if noise outweighs benefits. |

## 3. High-Signal Findings
1. `TrainConfig.wandb_enable` is defined but never consulted, and `TrainingRunConfig` lacks an equivalent flag, leaving Weights & Biases logging entirely disabled despite configuration knobs.【F:src/codex_ml/training/functional_training.py†L48-L71】【F:src/codex_ml/cli/config.py†L63-L82】【F:src/codex_ml/training/__init__.py†L91-L139】
2. Functional fallback tokenises the entire corpus in one call, materialising `train_ids`/`val_ids` tensors in memory and risking OOM for large datasets.【F:src/codex_ml/training/functional_training.py†L176-L189】
3. When `datasets`/`transformers` are unavailable, the trainer silently returns synthetic metrics instead of failing fast, which can mask misconfigured environments.【F:src/codex_ml/training/__init__.py†L842-L859】
4. `BaseMetricsWriter` exposes a concrete class with `write` raising `NotImplementedError`, so misconfiguration leads to runtime crashes rather than graceful degradation.【F:src/codex_ml/metrics/writers.py†L31-L58】
5. Hydra `logging` config documents W&B toggles but the training runtime never applies them, creating documentation drift.【F:src/codex_ml/cli/config.py†L63-L82】【F:src/codex_ml/training/__init__.py†L91-L139】
6. Offline tokenizer resolution relies on environment variables without a diagnostic CLI, increasing operator toil during air-gapped deployments.【F:src/codex_ml/registry/tokenizers.py†L68-L114】
7. The MLflow guard is active, but there is no mirrored warning when `CODEX_SAFETY_BYPASS` disables safety filters, reducing auditability of bypass events.【F:src/codex_ml/safety/filters.py†L62-L104】
8. Docker image installs only base dependencies, so running `codex-train` inside the container without extras will miss torch/transformers/peft required by registries.【F:Dockerfile†L14-L23】【F:pyproject.toml†L28-L58】
9. README references coverage tooling and gating, yet coverage floor remains static (70%) and GPUs lack smoke checks, leaving a blind spot for CUDA regressions.【F:README.md†L97-L139】【F:tox.ini†L1-L21】
10. Legacy `training` package still powers registry integrations; without explicit ownership, drift between `training/functional_training.py` and `codex_ml/training/functional_training.py` can introduce subtle behavioural differences.【F:training/functional_training.py†L400-L520】【F:src/codex_ml/training/functional_training.py†L1-L484】

## 4. Atomic Diffs
### Diff 1 — Wire W&B logging into training loops
*Why*: Honour `wandb_enable` flags so experiments get mirrored into W&B alongside MLflow, improving observability.【F:src/codex_ml/training/functional_training.py†L48-L71】【F:src/codex_ml/cli/config.py†L63-L82】
*Risk*: Optional dependency import errors; duplicate logging if both MLflow and W&B run. Mitigate with try/except and ensure no-op when wandb missing.
*Rollback*: Remove new imports and calls from `functional_training.py`/`codex_ml/training/__init__.py` to revert to MLflow-only logging.
*Tests/docs*: Add pytest covering mocked wandb session and document new behaviour in README logging section.
```diff
--- a/src/codex_ml/training/functional_training.py
+++ b/src/codex_ml/training/functional_training.py
@@
-from codex_ml.monitoring.system_metrics import start_metrics_logger
-from codex_ml.monitoring.tb_writer import TBWriter
+from codex_ml.monitoring.system_metrics import start_metrics_logger
+from codex_ml.monitoring.tb_writer import TBWriter
+from codex_ml.monitoring.tracking import Tracker
@@
-    with maybe_mlflow(
+    tracker = Tracker() if config.wandb_enable else None
+    if tracker is not None:
+        tracker.start(run_name=run_name, params={"model": config.model_name})
+    with maybe_mlflow(
         enable=bool(config.mlflow_enable),
         run_name=run_name,
         tracking_uri=config.mlflow_tracking_uri,
     ) as mlf:
@@
-                if config.mlflow_enable:
+                if config.mlflow_enable:
                     try:
                         mlf.log_metrics({"train/loss": loss_value}, step=global_step)
                     except Exception:
                         pass
                     _append_metric(
@@
+                    if tracker is not None:
+                        tracker.log_metrics({"train/loss": loss_value}, step=global_step)
@@
-                if config.mlflow_enable:
+                if config.mlflow_enable:
                     try:
                         mlf.log_metrics(
                             {
                                 "eval/perplexity": float(metrics["val_perplexity"]),
                                 "eval/token_accuracy": float(metrics["val_token_accuracy"]),
                             },
                             step=global_step,
                         )
                     except Exception:
                         pass
                     _append_metric(
                         {
                             "phase": "eval",
                             "epoch": config.epochs,
                             "step": global_step,
                             "perplexity": float(metrics["val_perplexity"]),
                             "token_accuracy": float(metrics["val_token_accuracy"]),
                         }
                     )
+                if tracker is not None:
+                    tracker.log_metrics(
+                        {
+                            "eval/perplexity": float(metrics.get("val_perplexity", ppl)),
+                            "eval/token_accuracy": float(metrics.get("val_token_accuracy", acc)),
+                        },
+                        step=global_step,
+                    )
@@
-    if stop_event is not None and system_thread is not None:
+    if tracker is not None:
+        tracker.end()
+    if stop_event is not None and system_thread is not None:
         try:
             stop_event.set()
             system_thread.join(timeout=5.0)
         except Exception:
             pass
```

### Diff 2 — Propagate W&B toggles through structured configs
*Why*: Ensure Hydra logging config actually feeds into runtime flags by extending `TrainingRunConfig` and config coercion.【F:src/codex_ml/cli/config.py†L63-L82】【F:src/codex_ml/training/__init__.py†L560-L680】
*Risk*: New dataclass fields may require test fixture updates.
*Rollback*: Drop added fields from dataclasses and config coercion helpers.
*Tests/docs*: Update config round-trip tests and README logging section.
```diff
--- a/src/codex_ml/cli/config.py
+++ b/src/codex_ml/cli/config.py
@@
 @dataclass
 class LogCfg:
     """Logging integrations."""

     tensorboard: bool = False
     tensorboard_dir: str = ".codex/tb"
     wandb_enable: bool = False
+    wandb_project: str | None = None
     mlflow_enable: bool = False
     mlflow_tracking_uri: Optional[str] = None
```
```diff
--- a/src/codex_ml/training/__init__.py
+++ b/src/codex_ml/training/__init__.py
@@
 class TrainingRunConfig:
@@
     tensorboard: bool = True
+    wandb_enable: bool = False
+    wandb_project: str | None = None
     mlflow_enable: bool = False
@@
-    log_system_metrics: bool = False
+    log_system_metrics: bool = False
@@
-    optimizer: OptimizerSettings = field(default_factory=OptimizerSettings)
+    optimizer: OptimizerSettings = field(default_factory=OptimizerSettings)
```
```diff
@@ def _coerce_config(...):
-    tensorboard_value = _scalar(base.tensorboard, "tensorboard")
+    tensorboard_value = _scalar(base.tensorboard, "tensorboard")
+    wandb_value = _scalar(base.wandb_enable, "wandb_enable")
+    wandb_project_value = _scalar(base.wandb_project, "wandb_project")
@@
-    mlflow_value = _scalar(base.mlflow_enable, "mlflow_enable")
+    mlflow_value = _scalar(base.mlflow_enable, "mlflow_enable")
@@
-        tensorboard=(
-            tensorboard_value if isinstance(tensorboard_value, bool) else bool(tensorboard_value)
-        ),
+        tensorboard=(
+            tensorboard_value if isinstance(tensorboard_value, bool) else bool(tensorboard_value)
+        ),
+        wandb_enable=(wandb_value if isinstance(wandb_value, bool) else bool(wandb_value)),
+        wandb_project=(
+            str(wandb_project_value).strip() if wandb_project_value not in (None, "") else None
+        ),
         mlflow_enable=(mlflow_value if isinstance(mlflow_value, bool) else bool(mlflow_value)),
```
```diff
--- a/src/codex_ml/training/__init__.py
+++ b/src/codex_ml/training/__init__.py
@@ def run_functional_training(...):
-    tracker = None
+    tracker = None
     if isinstance(config, TrainingRunConfig):
         cfg = config
@@
-    if cfg.mlflow_enable:
+    if cfg.wandb_enable:
+        tracker = Tracker()
+        tracker.start(run_name=f"run-{cfg.seed}", params={"model": cfg.model})
+    if cfg.mlflow_enable:
@@
-    if tracker is not None:
-        tracker.end()
```

### Diff 3 — Chunked tokenisation to reduce peak memory
*Why*: Avoid loading entire corpora into memory by tokenising in configurable batches before concatenation.【F:src/codex_ml/training/functional_training.py†L176-L189】
*Risk*: Incorrect chunk stitching could misalign labels/masks; ensure deterministic concatenation.
*Rollback*: Revert helper to restore eager encoding.
*Tests/docs*: Extend training smoke test with large synthetic corpus to assert chunked path equivalence.
```diff
--- a/src/codex_ml/training/functional_training.py
+++ b/src/codex_ml/training/functional_training.py
@@
-class TrainConfig:
+class TrainConfig:
@@
     gradient_accumulation_steps: int = 1
     max_length: int = 512
+    encode_chunk_size: int | None = None
@@
-    def _prepare(batch_texts: Iterable[str]):
-        enc = tokenizer(
-            list(batch_texts),
-            padding="max_length",
-            truncation=True,
-            max_length=config.max_length,
-            return_tensors="pt",
-        )
-        return enc["input_ids"], enc["attention_mask"]
-
-    train_ids, _ = _prepare(texts)
-    val_ids, _ = _prepare(val_texts) if val_texts is not None else (None, None)
+    def _chunk_encode(items: Iterable[str]) -> tuple[torch.Tensor, torch.Tensor]:
+        chunk = max(int(config.encode_chunk_size or config.batch_size), 1)
+        id_chunks: list[torch.Tensor] = []
+        mask_chunks: list[torch.Tensor] = []
+        buffer: list[str] = []
+        for text in items:
+            buffer.append(text)
+            if len(buffer) >= chunk:
+                enc = tokenizer(
+                    list(buffer),
+                    padding="max_length",
+                    truncation=True,
+                    max_length=config.max_length,
+                    return_tensors="pt",
+                )
+                id_chunks.append(enc["input_ids"])
+                mask_chunks.append(enc["attention_mask"])
+                buffer.clear()
+        if buffer:
+            enc = tokenizer(
+                list(buffer),
+                padding="max_length",
+                truncation=True,
+                max_length=config.max_length,
+                return_tensors="pt",
+            )
+            id_chunks.append(enc["input_ids"])
+            mask_chunks.append(enc["attention_mask"])
+        if not id_chunks:
+            return torch.empty((0, config.max_length), dtype=torch.long), torch.empty((0, config.max_length), dtype=torch.long)
+        return torch.cat(id_chunks, dim=0), torch.cat(mask_chunks, dim=0)
+
+    train_ids, _ = _chunk_encode(texts)
+    val_ids, _ = _chunk_encode(val_texts) if val_texts is not None else (None, None)
```

## 5. Local Tests & Gates
| Command | Purpose | ML Test Score Mapping |
| --- | --- | --- |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -m "not slow"` | Core unit/integration suite (CPU) | Model, Data, Regression |
| `nox -s tests` | Offline gating with coverage enforcement | Infrastructure, Regression |
| `tox -e py3` | Minimal reproducibility/coverage smoke | Infrastructure |
| `nox -s lock_refresh` (opt-in) | Ensures lockfiles match pyproject updates | Infrastructure |
| `pytest -m "security"` | Safety & sanitisation checks | Security |
| `pytest tests/training/test_functional_training_main.py -k chunk` (new) | Validates chunked tokenisation path | Performance |

Sample outputs should remain attached in CI logs; run locally before publishing diffs.

## 6. Reproducibility Checklist
- ✅ **Deterministic seeding** – `set_reproducible` synchronises Python/NumPy/Torch RNGs and cuBLAS determinism.【F:src/codex_ml/utils/seeding.py†L25-L109】
- ✅ **Environment capture** – Checkpoint metadata & provenance snapshots record git commit, hardware, pip freeze.【F:src/codex_ml/utils/checkpointing.py†L434-L520】【F:src/codex_ml/utils/provenance.py†L1-L119】
- ✅ **Config versioning** – Hydra configs + `config_snapshot` persisted when MLflow enabled.【F:src/codex_ml/training/functional_training.py†L192-L211】
- ⚠️ **Experiment tracking parity** – MLflow wired; W&B flag currently inert (needs Diff 1/2).【F:src/codex_ml/training/functional_training.py†L48-L71】【F:src/codex_ml/utils/experiment_tracking_mlflow.py†L31-L135】
- ⚠️ **Data provenance** – JSONL loader captures text but lacks checksum manifest for datasets; consider extending `load_jsonl` to record hashes.【F:src/codex_ml/data/jsonl_loader.py†L13-L72】
- ⚠️ **Hardware reproducibility docs** – README emphasises deterministic flags but lacks GPU-specific guidance; update docs alongside Diff 1.

## 7. Deferred Items
- **GPU smoke gate** – Requires CUDA CI hardware; deprioritised pending resource availability.
- **Dataset cache manifests** – Complexity of hashing large corpora and no immediate owner; revisit after chunked tokenisation lands.
- **Plugin diagnostics CLI** – Lower priority; focus on W&B/logging parity first.

## 8. Error Capture Blocks
_None encountered during audit._

---

## Codex-ready Task Sequence
1. **Preparation**
   1. Activate project venv and install `[ml,logging,dev]` extras using `requirements.lock`.
   2. Export `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` and `CODEX_DISABLE_NVML=1` for deterministic tests.
   3. Inspect `git status` to ensure clean workspace.
2. **Search & Mapping**
   1. Read `src/codex_ml/training/functional_training.py` around W&B and tokenisation hotspots.
   2. Map Hydra logging config in `src/codex_ml/cli/config.py` to runtime dataclasses.
   3. Review `codex_ml/monitoring/tracking.py` for reusable tracker APIs.
3. **Best-Effort Construction**
   1. Patch training modules to integrate `Tracker` when W&B is enabled.
   2. Extend structured configs (`TrainingRunConfig`, Hydra logging) to expose new flags.
   3. Implement chunked tokenisation helper honouring optional `encode_chunk_size`.
   4. Update or add unit tests covering new behaviour (mocked wandb, chunked encoding).
   5. Refresh README logging section with W&B usage notes.
4. **Controlled Pruning**
   1. If wandb integration proves too invasive, disable via config flag but document rationale.
   2. If chunked path introduces regressions, gate behind feature flag defaulting to eager mode.
5. **Error Capture**
   - Question from ChatGPT @codex {{timestamp}}:
     While performing [STEP_3.4: run unit tests], encountered the following error: `[ERROR_MESSAGE]` Context: `pytest -k wandb_chunk`. What are the possible causes, and how can this be resolved while preserving intended functionality?
6. **Finalization**
   1. Run `nox -s tests` and targeted pytest suites.
   2. Update changelog/STATUS doc with outcomes.
   3. Commit with message referencing W&B integration and chunked tokenisation.

### Executable Script (Python)
```python
#!/usr/bin/env python3
"""Automate W&B wiring + chunked tokenisation workflow."""
import json
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def run(cmd: list[str], cwd: Path = REPO) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True)


def main() -> None:
    # Preparation
    run(["pip", "install", "-r", "requirements.lock"])
    run(["pip", "install", "-e", ".[ml,logging,dev]"])

    # Search & Mapping (generate references for IDE/navigation)
    paths = [
        "src/codex_ml/training/functional_training.py",
        "src/codex_ml/cli/config.py",
        "src/codex_ml/monitoring/tracking.py",
    ]
    print(json.dumps({"inspect": paths}, indent=2))

    # Best-Effort Construction placeholders (editors apply patches outside script)
    print("Apply patches for W&B integration and chunked encoding now.")

    # Controlled pruning decision log
    pruning_log = REPO / "artifacts" / "pruning_log.ndjson"
    pruning_log.parent.mkdir(parents=True, exist_ok=True)
    pruning_log.write_text("[]\n", encoding="utf-8")

    # Error capture template
    errors_path = REPO / ".codex" / "errors.ndjson"
    errors_path.parent.mkdir(parents=True, exist_ok=True)
    errors_path.write_text("[]\n", encoding="utf-8")

    # Finalization commands (tests)
    run(["nox", "-s", "tests"])
    run(["pytest", "tests/training/test_functional_training_main.py", "-k", "chunk"])


if __name__ == "__main__":
    main()
```
