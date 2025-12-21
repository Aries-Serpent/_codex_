# Codex Sequential Execution Block: LoRA Integration, Metrics, Security, Packaging, Reproducibility

## Phase 1 — Preparation
1.1 Establish working directories (`logs/codex_tasks`, `reports/codex_tasks`) and timestamped run identifier.
1.2 Parse `README.md` and linked guides to capture existing references to LoRA, metrics, security gates, packaging, and reproducibility. Persist structured notes to `logs/codex_tasks/readme_audit.json`.
1.3 Snapshot environment context (Python version, OS, CPU/GPU availability, `pip freeze`, Git HEAD) into `logs/codex_tasks/provenance.json`.
1.4 Assert no cost-incurring automation (`.github/workflows`, remote telemetry) will be enabled. Abort if automation files are staged.

## Phase 2 — Search & Mapping
2.1 Enumerate candidate modules/scripts for each requirement:
    - LoRA CLI + docs/tests → `src/codex_cli/`, `training/`, `docs/guides`, `tests/`.
    - Metrics registry/aggregator → `codex_ml/eval`, `analysis/metrics`, `tools/`, `scripts/`.
    - Secret scanning gates → `noxfile.py`, `requirements-dev.txt`, `docs/modules/safety.md`.
    - Packaging + Docker → root `pyproject.toml`/`setup.cfg`, `Dockerfile*`, `docs/runbook*`.
    - Reproducibility → `docs/repro*`, `training/`, `codex_utils/environment`.
    Persist findings to `logs/codex_tasks/mapping.json`.
2.2 For each module, compare current purpose with task requirements and document adaptation viability notes (`logs/codex_tasks/adaptation_notes.json`).
2.3 Identify related tooling (Hydra configs, scripts, templates) that could be reused. Record path, description, and reuse strategy.

## Phase 3 — Best-Effort Construction
3.1 LoRA CLI & docs/tests
    a. Modify CLI (Typer) to expose LoRA parameters (`lora_r`, `lora_alpha`, `lora_dropout`, `target_modules`).
    b. Update model loading to consume CLI-specified LoRA settings and ensure defaults disable LoRA gracefully.
    c. Extend docs with CLI usage examples and add pytest covering CLI parameter plumbing.
3.2 Metrics registry & aggregator
    a. Create registry module supporting registration and computation of metrics (accuracy, precision, recall, F1).
    b. Implement NDJSON → aggregated NDJSON/CSV scripts under `tools/` with CLI entry points.
    c. Integrate registry with evaluator configuration and add unit tests.
    d. Update docs with metric registration/aggregation instructions.
3.3 Secret scanning gates
    a. Update `noxfile.py` (gates session) to run `detect-secrets` and `bandit` with offline-only flags.
    b. Record scan baselines/config (e.g., `.secrets.baseline`) without enabling GitHub Actions.
    c. Document workflow in safety guide and add gating tests.
3.4 Packaging & Docker
    a. Ensure `pyproject.toml`/`setup.cfg` defines CLI entry points and pinned dependency metadata.
    b. Implement hardened `Dockerfile` following docs (non-root, multi-stage, offline wheels).
    c. Update runbook with packaging and deployment instructions; add smoke test script for container build.
3.5 Reproducibility improvements
    a. Capture runtime environment (OS, Python, CUDA, package hashes) during training/eval runs.
    b. Enforce lockfile installation (`uv.lock`/`requirements-lock.txt`) in tooling (nox sessions/Makefile).
    c. Document deterministic settings (seeds, torch deterministic flags, dataset checksums) and add validation tests.
    d. Emit reproducibility manifest per run.
    Execute sub-steps sequentially, recording successes in change log before considering pruning.

## Phase 4 — Controlled Pruning
4.1 For any sub-step where best-effort implementation fails, document exhaustive rationale in `reports/codex_tasks/pruning_report.md` (include explored paths and blockers).
4.2 Cross-reference pruning decisions with adaptation notes to avoid duplicate effort.
4.3 Tag deferred work in-code using explicit `NotImplementedError` or doc TODOs referencing pruning report.

## Phase 5 — Error Capture
5.1 Wrap each numbered step in structured try/except. On failure, append research question to `logs/codex_tasks/error_captures.ndjson` using the format:
    > Question from ChatGPT @codex {{timestamp}}:
    > While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error: [ERROR_MESSAGE] Context: [BRIEF_CONTEXT]. What are the possible causes, and how can this be resolved while preserving intended functionality?
5.2 After logging, continue if subsequent steps remain safe; otherwise halt with non-zero exit code.

## Phase 6 — Finalization
6.1 Summarise completed actions, outstanding gaps, and follow-up recommendations in `reports/codex_tasks/final_summary.md`.
6.2 Run local tests (`nox -s tests`, `nox -s gates`) if environment permits; store outputs in `logs/codex_tasks/test_results.json`.
6.3 Update or create `codex_change_log.jsonl` with all recorded actions and pruning outcomes.
6.4 Emit console summary highlighting artifact locations, key docs updated, and any pending research questions.
