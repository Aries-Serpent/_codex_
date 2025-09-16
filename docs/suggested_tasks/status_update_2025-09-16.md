# Suggested Tasks — _codex_ Status Update (2025-09-16)

This execution blueprint sequences the follow-up work required to close the partially implemented capabilities, high-signal findings, and atomic diffs captured in the 2025-09-16 status update. Each suggested task references the existing artefacts to touch, explains how it mitigates the recorded risks and gaps, and lists the offline validation gates to run before hand-off.

## Execution Envelope & Baseline Gates

1. **Bootstrap environment (shared prerequisite)**
   - Create/refresh a local virtual environment and install dev dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -e .[dev]`.
   - Export offline flags recommended by the repo (`export NO_NETWORK=1 PYTHONHASHSEED=0`).
2. **Run repository gates upfront**
   - `pre-commit run --all-files --verbose` and `nox -s tests` per local gate guidance, rerunning these after every major group of changes.
   - Baseline pytest run: `pytest -q -m "not slow"`; add focused invocations noted in each task.
3. **Documentation hygiene**
   - Update CHANGELOG entries and status notes as tasks land.

## Phase 1 — Modeling & Training Hardening

### Suggested Task ST-1.1 — Expose configurable LoRA defaults
- **Capability Alignment**: ChatGPT Codex Modeling (partially implemented).
- **High-Signal / Diff Inputs**: HS3 (hidden LoRA config), Atomic Diff 1.
- **Existing Artefacts**: `src/codex_ml/peft/peft_adapter.py`, `tests/test_peft_adapter.py`, `README.md` LoRA section.
- **Implementation Steps**:
  1. Apply the Atomic Diff 1 patch so `DEFAULT_CFG` includes `task_type` and `apply_lora` pops overrides before constructing the PEFT config.
  2. Extend `tests/test_peft_adapter.py` to assert that `task_type` defaults to `CAUSAL_LM` and is overridable via kwargs.
  3. Document the new flags in README/CLI usage and ensure Hydra configs expose LoRA knobs.
- **Validation**:
  - `pytest tests/test_peft_adapter.py`.
  - `pre-commit run --files src/codex_ml/peft/peft_adapter.py tests/test_peft_adapter.py README.md`.
- **Deliverables**: Updated adapter defaults, regression test, and documentation snippet covering LoRA parameters.

### Suggested Task ST-1.2 — Register offline pretrained model loading
- **Capability Alignment**: ChatGPT Codex Modeling.
- **High-Signal Inputs**: HS2 (model support minimal).
- **Existing Artefacts**: `src/codex_ml/models/registry.py`, `configs/model/` Hydra templates, `tests/test_registry.py`.
- **Implementation Steps**:
  1. Extend the model registry to load local HuggingFace causal LMs (e.g., GPT-2, LLaMA checkpoints) strictly from offline caches, failing gracefully if weights are absent.
  2. Add configuration entries and documentation for pointing to local model directories; include device/dtype handling per registry gaps.
  3. Add tests that stub a tiny pretrained model (use fixtures) to ensure the registry surfaces load failures with actionable messaging.
- **Validation**:
  - `pytest tests/test_registry.py -k pretrained` (new marker).
  - `pytest tests/test_models.py` (new coverage for offline loading).
- **Deliverables**: Extended registry API, offline load documentation, and regression tests.

### Suggested Task ST-1.3 — Unify training loops with experiment tracking
- **Capability Alignment**: Training Engine.
- **High-Signal / Diff Inputs**: HS1 (training loop duplication), HS7 (inconsistent experiment tracking), Atomic Diff 3.
- **Existing Artefacts**: `src/codex_ml/train_loop.py`, `src/codex_ml/training/__init__.py`, `tests/test_train_loop.py`, `tracking/init_experiment.py`.
- **Implementation Steps**:
  1. Apply Atomic Diff 3 by refactoring `run_training` to consume the experiment tracking context and eliminate the legacy MLflow-specific branch.
  2. Deduplicate `run_functional_training` and the toy loop into a single trainer entry point that accepts hooks for evaluation and telemetry.
  3. Expand `tests/test_train_loop.py` to cover the unified path, including verifying that metrics flow through `ExperimentContext` and NDJSON outputs still materialize.
- **Validation**:
  - `pytest tests/test_train_loop.py`.
  - `pytest tests/test_mlflow_utils.py` to ensure the tracking shims remain stable.
- **Deliverables**: Single training loop entry point, updated experiment tracking integration, expanded tests.

### Suggested Task ST-1.4 — Add resume-from-checkpoint support to CLI
- **Capability Alignment**: Training Engine / Checkpointing & Resume touchpoint.
- **High-Signal / Diff Inputs**: HS1 (duplication), Atomic Diff 2.
- **Existing Artefacts**: `src/codex_ml/training/__init__.py`, `src/codex_ml/cli/main.py`, `tests/test_checkpointing.py`.
- **Implementation Steps**:
  1. Apply Atomic Diff 2 to accept `resume_from` in `run_functional_training` and surface informative logging when resume fails.
  2. Wire the flag through Hydra CLI (Typer entry) and ensure config schema allows `resume_from` path validation.
  3. Extend checkpoint tests to cover save/resume flows and guard against stale RNG state.
- **Validation**:
  - `pytest tests/test_checkpointing.py`.
  - `pytest tests/test_cli.py -k resume` (new test case ensuring CLI propagation).
- **Deliverables**: CLI flag, resume logic, regression coverage.

### Suggested Task ST-1.5 — Surface optional telemetry dependency health
- **Capability Alignment**: Training Engine (execution observability) & Logging/Monitoring risk mitigation.
- **High-Signal Inputs**: HS9 (telemetry dependencies optional).
- **Existing Artefacts**: `src/codex_ml/monitoring/codex_logging.py`, `src/codex_ml/telemetry/metrics.py`, `scripts/codex_local_gates.sh`.
- **Implementation Steps**:
  1. Detect missing optional deps (`psutil`, `pynvml`, `wandb`, `mlflow`) at startup and emit structured warnings or gate toggles rather than silently disabling features.
  2. Add unit tests that monkeypatch dependency import failures and assert clear user messaging.
  3. Update local gate scripts to echo the telemetry status summary after pre-commit/test runs.
- **Validation**:
  - `pytest tests/test_mlflow_utils.py tests/test_logging.py` (add new coverage where needed).
  - Manual invocation of `python -m codex_ml.monitoring.codex_logging --dry-run` to confirm warnings.
- **Deliverables**: Enhanced dependency reporting, guardrail tests, and gate script updates.

## Phase 2 — Data Management & Evaluation

### Suggested Task ST-2.1 — Introduce deterministic dataset split utilities
- **Capability Alignment**: Data Handling.
- **High-Signal / Diff Inputs**: HS5 (missing split management), Atomic Diff 4.
- **Existing Artefacts**: `src/codex_ml/data/`, `src/codex_ml/training/__init__.py`, `tests/test_data_loaders.py`.
- **Implementation Steps**:
  1. Add `data/split_utils.py` per Atomic Diff 4 with seed-controlled JSONL splitting helpers returning `SplitPaths`.
  2. Integrate the helper into training config loading so users can request deterministic splits via config fields.
  3. Write tests ensuring records are neither lost nor duplicated and that ratio validation errors are surfaced.
- **Validation**:
  - `pytest tests/test_data_loaders.py tests/test_data_split_utils.py` (new file).
  - `pre-commit run --files src/codex_ml/data/split_utils.py`.
- **Deliverables**: Split utility module, integration wiring, tests.

### Suggested Task ST-2.2 — Add dataset manifest caching & schema validation
- **Capability Alignment**: Data Handling.
- **High-Signal Inputs**: HS5 (caching/schema gaps).
- **Existing Artefacts**: `src/codex_ml/data/loaders.py`, `src/codex_ml/utils/provenance.py`, dataset config schema.
- **Implementation Steps**:
  1. Introduce optional manifest generation capturing checksums and offsets to enable offline caching.
  2. Validate dataset schema (required keys such as `prompt`/`completion`) using Pydantic models; fail fast on violations.
  3. Document how to precompute manifests for large corpora to avoid repeated shuffles.
- **Validation**:
  - `pytest tests/test_data_loaders.py -k manifest` (new coverage).
  - `pytest tests/test_config_schema.py` (new tests verifying schema validation).
- **Deliverables**: Manifest support, schema validation, docs.

### Suggested Task ST-2.3 — Expand evaluation metrics and runner
- **Capability Alignment**: Evaluation & Metrics.
- **High-Signal Inputs**: HS6 (metrics limited).
- **Existing Artefacts**: `src/codex_ml/eval/metrics.py`, `analysis/metrics.py`, `tests/test_metrics.py`, training loop evaluation hooks.
- **Implementation Steps**:
  1. Add metrics for F1, ROUGE-L, BLEU, and plug them into a metrics registry to enable selection via config.
  2. Build an evaluation runner that consumes saved checkpoints and dataset splits to compute metrics offline.
  3. Add tests for each metric (including edge cases) and integration tests verifying runner outputs to NDJSON/CSV.
- **Validation**:
  - `pytest tests/test_metrics.py tests/test_eval_runner.py` (new integration coverage).
  - `python -m codex_ml.cli.main evaluate --config-name=<new-config>` (dry-run to verify Hydra wiring).
- **Deliverables**: Extended metrics library, evaluation runner, tests & docs.

## Phase 3 — Configuration, Safety & Governance

### Suggested Task ST-3.1 — Enrich TrainConfig & Hydra templates
- **Capability Alignment**: Configuration Management.
- **High-Signal Inputs**: HS4 (narrow schema).
- **Existing Artefacts**: `src/codex_ml/config_schema.py`, `configs/training/`, `src/codex_ml/cli/validate.py`.
- **Implementation Steps**:
  1. Extend `TrainConfig` to cover seed, batch size, scheduler, device, dtype, LoRA, evaluation splits, and checkpoint retention fields.
  2. Generate updated Hydra defaults demonstrating overrides for new fields; ensure backward compatibility by providing versioned config entries.
  3. Update the validation CLI to reject unknown fields and print helpful migration hints.
- **Validation**:
  - `pytest tests/test_config_schema.py`.
  - `python -m codex_ml.cli.validate --config configs/training/default.yaml`.
- **Deliverables**: Richer schema, config examples, validation updates.

### Suggested Task ST-3.2 — Enforce safety filters in training & generation
- **Capability Alignment**: Security & Safety.
- **High-Signal Inputs**: HS8 (safety optional).
- **Existing Artefacts**: `src/codex_ml/safety/filters.py`, `src/codex_ml/training/__init__.py`, `src/codex_ml/train_loop.py`, `tests/test_safety_filters.py`.
- **Implementation Steps**:
  1. Wire `SafetyFilters` invocations into the training data pipeline and any generation utilities, with opt-out flags for testing only.
  2. Add tests ensuring redaction occurs on banned phrases and that bypass flags are auditable.
  3. Update documentation to highlight safe defaults and how to supply custom safety policies offline.
- **Validation**:
  - `pytest tests/test_safety_filters.py`.
  - `pytest tests/test_train_loop.py -k safety` (new scenario verifying integration).
- **Deliverables**: Enforced safety path, guardrail tests, docs.

### Suggested Task ST-3.3 — Integrate security tooling into local gates
- **Capability Alignment**: Security & Safety.
- **High-Signal Inputs**: same as above plus gaps in minimal patch plan (pip audit integration).
- **Existing Artefacts**: `scripts/codex_local_gates.sh`, `tools/pip_audit_wrapper.py`, `.pre-commit-config.yaml`.
- **Implementation Steps**:
  1. Update `scripts/codex_local_gates.sh` to run `pip_audit_wrapper.py` and semgrep/bandit in offline mode.
  2. Ensure failing scans break the gate; add docs guiding developers on caching vulnerability databases offline.
  3. Add tests or CI smoke scripts verifying wrapper exit codes.
- **Validation**:
  - Manual `scripts/codex_local_gates.sh` execution.
  - `pytest tests/test_security_tooling.py` (new test verifying wrapper invocation).
- **Deliverables**: Hardened local gate script, documentation, tests.

### Suggested Task ST-3.4 — Telemetry redaction & log rotation controls
- **Capability Alignment**: Cross-cutting risk from Logging & Monitoring (complements ST-1.5).
- **High-Signal Inputs**: HS9 (NDJSON redaction gaps).
- **Existing Artefacts**: `src/codex_ml/monitoring/codex_logging.py`, `tracking/init_experiment.py`, `tests/test_logging.py`.
- **Implementation Steps**:
  1. Extend `write_ndjson` to support size-based rotation and ensure prompts/completions pass through safety filter redaction before persistence.
  2. Provide config toggles for rotation thresholds and document recommended defaults.
  3. Add regression tests verifying rotation triggers and redaction coverage.
- **Validation**:
  - `pytest tests/test_logging.py`.
  - Manual run `python -m codex_ml.monitoring.codex_logging --emit-sample` to inspect output.
- **Deliverables**: Rotating NDJSON logging with robust redaction and tests.

## Phase 4 — Deployment, Documentation & Enablement

### Suggested Task ST-4.1 — Optimize offline Docker images & health checks
- **Capability Alignment**: Deployment.
- **High-Signal Inputs**: Deployment gaps from capability audit.
- **Existing Artefacts**: `Dockerfile`, `docker-compose.yml`, `Makefile`, `codex.mk`.
- **Implementation Steps**:
  1. Split the Docker build into CPU and CUDA variants using multi-stage builds, ensuring wheelhouse/offline caches feed the installs.
  2. Add healthcheck scripts for the API/CLI entry points and wire them into `docker-compose.yml`.
  3. Document offline build procedures and publish sample `make` targets for image creation.
- **Validation**:
  - `docker build -f Dockerfile.cpu -t codex:cpu .` (offline context) and analogous GPU build.
  - `docker compose up --build` to verify healthchecks succeed.
- **Deliverables**: Lean Dockerfiles, healthchecks, documentation updates.

### Suggested Task ST-4.2 — Author quickstart & architecture docs
- **Capability Alignment**: Documentation & Examples.
- **High-Signal Inputs**: HS10 (docs insufficient).
- **Existing Artefacts**: `README.md`, `docs/`, `mkdocs.yml`, example notebooks directory.
- **Implementation Steps**:
  1. Add a structured quickstart covering tokenizer prep, model fine-tuning with LoRA, and experiment tracking offline.
  2. Produce an architecture overview (diagram + narrative) showing data flow, registries, and safety/telemetry hooks.
  3. Provide an executable notebook or Markdown tutorial demonstrating end-to-end fine-tuning with the new split/evaluation tooling.
- **Validation**:
  - `mkdocs serve` (if allowed offline) or `mkdocs build` to ensure docs compile.
  - Run notebook smoke test via `pytest --nbmake docs/examples/*.ipynb` (if NB tests added) or manual execution.
- **Deliverables**: Updated README, docs site content, tutorial assets.

### Suggested Task ST-4.3 — Strengthen examples & CLI help surface
- **Capability Alignment**: Documentation & Examples, Deployment.
- **High-Signal Inputs**: HS10 (lack of examples).
- **Existing Artefacts**: `src/codex_ml/cli/main.py`, `codex_ml/cli/helptext`, `examples/`.
- **Implementation Steps**:
  1. Expand CLI help to include new flags (LoRA, resume, evaluation, safety) and provide usage examples that align with updated config schema.
  2. Curate example configs and datasets under `examples/` showcasing typical workflows with deterministic splits and evaluation.
  3. Add smoke tests ensuring example commands run end-to-end (with small fixture datasets) offline.
- **Validation**:
  - `pytest tests/test_cli.py -k example` (new coverage verifying help text and sample commands).
  - Manual run `python -m codex_ml.cli.main train --config-name=examples/minimal` using synthetic data.
- **Deliverables**: Enhanced CLI help, runnable examples, tests.

## Phase 5 — Final Regression & Release Readiness

1. Re-run full local gates: `pre-commit run --all-files`, `nox -s lint type tests coverage`, `pytest -q -m "not slow"` plus any new markers (perf/safety).
2. Generate updated release notes summarizing capability closures and docs/training changes.
3. Capture telemetry/safety status snapshots to include in project documentation for auditability.

> **Hand-off criteria**: All tasks in Phases 1–4 completed with passing tests, documentation built, Docker images verified, and reproducibility checklist updated to reflect dataset manifests, config schema fields, and telemetry warnings.
