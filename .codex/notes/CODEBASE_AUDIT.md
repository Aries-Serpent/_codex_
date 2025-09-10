# Codebase Audit

## 1. Repo Map

- **Top-level directories**

  - `src/` – core library including chat, logging, ML modules.
  - `tests/` – extensive pytest suite for chat, data, metrics, safety and pipeline utilities.
  - `configs/` – Hydra-style YAML configs for env and training defaults.
  - `training/` – training utilities including HuggingFace Trainer wrapper.
  - `tools/` – scaffolding scripts and maintenance helpers.
  - `docs/`, `documentation/`, `examples/`, `notebooks/` – user documentation and demonstrations.
  - `codex_ml/`, `codex_script.py`, `functional_training.py` – top-level scripts for ML workflows.

- **Key files**

  - `pyproject.toml`, `tox.ini`, `noxfile.py`, `pytest.ini` – packaging and test configuration.
  - `Dockerfile`, `docker-compose.yml` – container setup.
  - `.pre-commit-config.yaml` – lint and format gates.
  - `src/codex_ml/tokenization/hf_tokenizer.py` – HuggingFace tokenizer adapter.
  - `src/codex_ml/models/minilm.py` – miniature Transformer for tests.
  - `src/codex_ml/utils/checkpointing.py` – checkpoint and RNG utilities.

- **Stubs & placeholders**

  - `src/codex_ml/peft/peft_adapter.py` – LoRA integration stubbed; function returns input model unmodified.
  - `tools/apply_interfaces.py` – multiple `TODO`/`NotImplementedError` placeholders.
  - `functional_training.py` – several `pass` statements for unimplemented paths.
  - `configs/interfaces.example.yaml` – references TODO module paths.

## 2. Capability Audit Table

| Capability | Status | Existing artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization | Implemented | `HFTokenizerAdapter`, `sentencepiece_adapter`, tokenization interfaces and tests | Limited padding/truncation options; no vocab export in docs | Inconsistent sequences or OOM on long inputs | Add padding/truncation flags to adapters, document vocab save; unit tests for edge lengths | Revert file changes and tests |
| ChatGPT Codex Modeling | Partially Implemented | `MiniLM` model, configuration dataclasses | LoRA/PEFT hooks stubbed; no device/dtype configuration | Cannot fine-tune with parameter-efficient methods; potential device mismatches | Implement `apply_lora` using `peft.get_peft_model`, expose dtype/device args in training scripts | Remove new LoRA import and restore stub |
| Training Engine | Partially Implemented | `train_loop.py`, `training/engine_hf_trainer.py` | No gradient accumulation or precision flags in custom loop | Instability on large batches or FP16 use | Add gradient_accumulation and precision options, tests covering accumulation | Revert changes to `train_loop.py` |
| Configuration Management | Partially Implemented | Hydra-style `configs/config.yaml`, dataclasses in `config.py` | No config overrides/sweeps; limited CLI integration | Hard to reproduce experiments, manual flag wiring | Introduce `hydra.main` entry points and document overrides; add config tests | Revert new config hooks |
| Evaluation & Metrics | Implemented | `eval/metrics.py`, metrics logging in `train_loop.py` | No NDJSON/CSV output besides metrics.json | Hard to integrate with external dashboards | Extend `record_metrics` to emit NDJSON; add CLI flag | Remove metrics output extension |
| Logging & Monitoring | Implemented | `codex_ml/monitoring/codex_logging.py` supports TensorBoard, W&B offline, MLflow, `psutil`/NVML | None major; optional deps | Runtime failures if deps missing | Guard imports (already handled); add smoke tests for disabled modes | Revert tests if failures |
| Checkpointing & Resume | Implemented | `utils/checkpointing.py`, `CheckpointManager`, tests | No best-k retention tests; scheduler state optional | Silent corruption or missing resumes | Add tests for resume and best-k pruning | Revert tests |
| Data Handling | Implemented | `data/loaders.py`, `sharding.py`, caching utilities | Deterministic shuffling limited; no explicit dataset splits | Non-reproducible training order | Add seed-based shuffling and split helpers | Remove new shuffling util |
| Security & Safety | Partially Implemented | `safety/filters.py`, `risk_score.py`, `.secrets.baseline` | Dependency lock files not enforced; prompt safety minimal | Supply chain vulnerabilities, unsafe outputs | Add `requirements.lock`, expand prompt filters, CI secret scans | Remove new lockfile |
| Internal CI/Test | Implemented | `pytest`, `nox`, `tox`, pre-commit; extensive tests | Coverage enforcement missing | Undetected regressions | Add coverage fail under `pytest --cov` | Remove coverage config |
| Deployment | Partially Implemented | `Dockerfile`, `setup.sh`, CLI scripts | No PyPI packaging or CLI entry points | Hard to distribute | Add `console_scripts` in `pyproject.toml`, build step docs | Revert packaging edits |
| Documentation & Examples | Implemented | `README`, `docs/`, notebooks | Some README badges TODO, examples minimal | Users confused about project status | Update badges, add quickstart scripts | Revert README |
| Experiment Tracking | Partially Implemented | MLflow & W&B hooks in monitoring module | No local MLflow setup docs; offline mode default but not exercised in tests | Missing experiment records | Add example MLflow run and tests using temporary directory | Revert examples |
| Extensibility | Partially Implemented | Interface classes (tokenizer, RL agent), modular data loaders | Registry/plug-in pattern absent, many `TODO` in scaffolding tools | Hard to extend with custom components | Implement simple registry in interfaces, resolve TODOs | Revert registry module |

## 3. High-Signal Findings

- LoRA/PEFT integration is stubbed; without it, parameter-efficient fine-tuning is impossible.
- Configuration relies on basic YAML without sweep/override tooling, limiting reproducibility.
- Custom training loop lacks gradient accumulation and precision options; may fail on limited hardware.
- No deterministic dataset shuffling or split helpers, risking inconsistent training runs.
- Safety filters exist but dependency locking is weak; security posture is unclear.
- Coverage reporting is absent despite an extensive test suite.
- README badges and interface config placeholders contain TODOs, indicating unfinished onboarding materials.
- Experiment tracking hooks exist but lack usage documentation and tests.
- Docker image present but missing publication workflow and CLI entry points for deployment.
- Tools directory contains numerous `TODO` and `NotImplementedError` markers, suggesting incomplete automation.
- Metrics logging writes to JSON but lacks NDJSON/CSV formats for analytics pipelines.
- Registry/plug-in pattern not formalized; extension requires manual wiring.
- Seed handling exists in checkpointing but not consistently wired across scripts.
- Notebook examples are sparse and partly stubbed, reducing educational value.
- `chatgpt-codex` CLI absent; static analysis must be run manually.

## 4. Atomic Diffs

<details><summary><code>src/codex_ml/peft/peft_adapter.py</code> – enable LoRA via PEFT</summary>

```diff
@@
-from __future__ import annotations
-
-
-def apply_lora(model, cfg: dict | None = None):
-    """Optional PEFT LoRA application. If peft not installed, returns model unchanged."""
-    try:
-        return model
-    except Exception:
-        return model
+from __future__ import annotations
+
+try:  # optional dependency
+    from peft import LoraConfig, get_peft_model
+except Exception:  # pragma: no cover - peft not installed
+    LoraConfig = None  # type: ignore
+    get_peft_model = None  # type: ignore
+
+
+def apply_lora(model, cfg: dict | None = None):
+    """Apply LoRA adapters when ``peft`` is available."""
+    if get_peft_model is None:
+        return model
+    cfg = cfg or {"r": 8, "lora_alpha": 16, "lora_dropout": 0.05, "bias": "none"}
+    config = LoraConfig(task_type="CAUSAL_LM", **cfg)
+    return get_peft_model(model, config)
```

*Why*: enables parameter-efficient fine-tuning.

*Risk*: adds optional dependency; misuse of config may break forward pass.

*Rollback*: remove new lines and restore stub.

*Tests/docs*: add unit test applying LoRA to `MiniLM`; document config options.

</details>

<details><summary><code>src/codex_ml/train_loop.py</code> – support gradient accumulation</summary>

```diff
@@
-    for ep in range(args.epochs):
-        m = demo_epoch(ep)
-        record_metrics("epoch_end", ep, m, cfg_hash)
+    accum = getattr(args, "grad_accum", 1)
+    for ep in range(args.epochs):
+        m = demo_epoch(ep)
+        record_metrics("epoch_end", ep, m, cfg_hash)
+        if accum > 1:
+            m["grad_accum"] = accum
```

*Why*: exposes gradient accumulation metadata for reproducibility.

*Risk*: none when `grad_accum` default is 1.

*Rollback*: revert diff.

*Tests/docs*: extend toy loop test verifying metadata field.

</details>

<details><summary><code>configs/config.yaml</code> – document MLflow offline defaults</summary>

```diff
@@
 mlflow:
-  enable: false
-  tracking_uri: ./mlruns
-  experiment: codex-experiments
+  enable: false  # set true to record runs locally
+  tracking_uri: ./mlruns  # created automatically
+  experiment: codex-experiments
```

*Why*: clarifies local tracking expectations.

*Risk*: none.

*Rollback*: remove comments.

*Tests/docs*: update README quickstart to show local run.

</details>

## 5. Local Tests & Gates

- `pre-commit run --all-files` – lints and formatting.
- `pytest` – executes full test suite.
- Suggested new gate: `pytest --cov=src/codex_ml` to enforce coverage (Infrastructure & Regression).
- New tests proposed:
  - `tests/test_peft_integration.py` (Model, Regression) – ensures `apply_lora` attaches adapters when `peft` installed.
  - `tests/test_grad_accum_metadata.py` (Infrastructure) – checks `grad_accum` logged in metrics.

## 6. Reproducibility Checklist

- [x] Deterministic seeds via `set_seed` and `seeds.json`.
- [ ] Environment capture (no `requirements.lock` or `conda` export).
- [x] Code versioning with Git.
- [ ] Deterministic data shuffling/splits.
- [x] Checkpoints include RNG state and config hash.
- [ ] Hardware/OS metadata not recorded.

## 7. Deferred Items

The following features are intentionally postponed for a later cycle, with minimal plans noted for future work:

- **Advanced RL support:** Implementing RL agents and reward models is complex and not required for initial production. Defer until a clear use case arises. Minimal plan: finish scaffolding and implement a trivial reward model for testing.
- **Full multi-node distributed training:** While single-node multi-GPU support is important, adding multi-node support requires significant engineering and may not be necessary for the current scale. Defer until model sizes demand it.
- **Comprehensive secret scanning integration:** Adding third-party secret scanning tools requires careful tuning to avoid false positives. Schedule for a later security audit.
- **Notebook auto-generation:** Automatically generating interactive notebooks (e.g., quick start) can be helpful but is not critical. Provide manual examples first.

## 8. Error Capture Blocks

Automation scripts should capture unexpected errors and format them as research questions for ChatGPT-5 using a standard template:

```text
Question for ChatGPT @codex {timestamp}:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

`tools/apply_interfaces.py` appends these blocks to `.codex/errors.ndjson`; new automation should adopt the same pattern.
