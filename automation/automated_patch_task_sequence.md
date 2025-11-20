# Automated Patch Task Sequence

## Purpose
Structured playbook for Codex automation to design and apply high-impact patches with auditable rationale, explicit risks, and rollback coverage. The sequence complements `codex_ready_task_sequence.yaml` by adding atomic diff proposals tied to observed artefacts and gaps.

## Inputs & Preconditions
- Repository state captured (clean git status, `git rev-parse HEAD`).
- Offline-first guardrails active (no `.github/workflows` writes, cost-incurring calls disabled).
- Logs root set (default: `codex_logs/`) with provenance snapshot available.
- Tests runnable locally via `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` and `nox -s tests` when dependencies are installed.

## Execution Phases
1. **Preparation**
   - Validate clean working tree; export `CODEX_SESSION_ID`.
   - Capture environment snapshot (python version, platform, CPU/GPU, pip freeze) into `codex_logs/provenance.json` and `pip_freeze.txt`.
   - Assert offline guard: `test ! -e .github/workflows`.
2. **Audit & Mapping**
   - Run targeted scans for `TODO`, `NotImplementedError`, and remote connectors; persist to `codex_logs/stub_scan.json`.
   - Map findings to capability buckets (tokenisation, modeling, training, config, eval, metrics, logging, checkpointing, data handling, safety, CI/tests, deployment, docs, experiment tracking, extensibility).
   - Record existing artefacts and gaps in `codex_logs/capability_gaps.json` with severity and owners.
3. **Atomic Diff Construction**
   - Select top-priority gaps (impact vs. effort) and bind to one of the atomic diffs below.
   - For each diff, draft a minimal patchset, validation plan, and rollback note; store per-diff plan under `codex_logs/diffs/<diff_id>.md`.
4. **Execution & Validation**
   - Apply one diff at a time; run scoped tests (unit or nox sessions) and collect outputs under `codex_logs/tests/<diff_id>.txt`.
   - Update evidence register `codex_logs/patch_evidence.json` with commands run, exit codes, and artefact paths.
5. **Rollback & Closure**
   - If a diff fails validation or raises regressions, rollback using the noted steps; log outcome in `codex_logs/rollbacks.md`.
   - Summarise completed diffs and residual gaps in `codex_logs/summary.md`; prepare PR notes.

## Atomic Diff Catalogue
Each diff is self-contained; apply incrementally with validation and rollback as described.

### Diff A — Deterministic tokenizer tests
- **Existing artefacts:** `tokenizer/fast_tokenizer.py` implements training/encode/decode; no round-trip tests.
- **Gap/Risk:** Silent vocab regressions; padding/truncation behaviour untested.
- **Patchset:**
  1. Add `tests/tokenization/test_fast_tokenizer.py` covering round-trip encode/decode and padding/truncation length enforcement.
  2. Raise coverage floor via `.coveragerc` or `CODEX_COV_FLOOR` in `noxfile.py` (target ≥10%).
  3. Document deterministic test invocation in `README.md` or `docs/guides/testing.md`.
- **Validation:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/tokenization -q` then `nox -s coverage` if available.
- **Rollback:** Remove the new test file and coverage tweak; revert documentation snippet.

### Diff B — Dataset loader registry
- **Existing artefacts:** Data split/validation utilities exist under `src/codex_ml/data/`; no loader registry.
- **Gap/Risk:** No standard entry point for dataset ingestion; users build ad-hoc loaders.
- **Patchset:**
  1. Create `src/codex_ml/data/registry.py` with `register_loader`, `load`, and `available` helpers and collision checks.
  2. Add `[project.entry-points."codex_ml.datasets"]` group to `pyproject.toml` with docstring guidance.
  3. Provide unit test registering a dummy loader and asserting dispatch/duplicate guard.
  4. Add short how-to section to `docs/how-to/dataset_manifest.md` explaining registration and discovery.
- **Validation:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/data -q` plus optional import smoke: `python -c "from codex_ml.data.registry import available"`.
- **Rollback:** Delete the registry module, entry-point block, and test; revert doc addition.

### Diff C — GPU deployment + compose
- **Existing artefacts:** CPU Dockerfile present; GPU path absent in compose orchestration.
- **Gap/Risk:** No tested GPU deployment recipe; local orchestration incomplete.
- **Patchset:**
  1. Add `Dockerfile.gpu` using `nvidia/cuda` base with offline-friendly install path; preserve non-root user where feasible.
  2. Create `docker-compose.yml` services for CPU and GPU variants with port and runtime guards.
  3. Update deployment docs (`docs/deploy/README.md` or similar) with build/run commands and GPU prerequisites.
  4. Add optional `nox` session for `hadolint` against both Dockerfiles.
- **Validation:** `docker build -f Dockerfile.gpu .` (where GPU toolchain exists); `docker compose config` for syntax check.
- **Rollback:** Remove the GPU Dockerfile and compose additions; drop doc/nox references.

### Diff D — Checkpoint resilience tests
- **Existing artefacts:** `training/checkpoint_manager.py` manages saves/resume; limited automated tests.
- **Gap/Risk:** Resume correctness unverified; potential silent divergence after interruptions.
- **Patchset:**
  1. Add pytest covering save/resume on a tiny synthetic model/dataloader ensuring metrics continuity and RNG state restoration.
  2. Capture minimal checkpoint manifest summary (path, step, metrics) in NDJSON for audit.
  3. Wire test to `nox -s tests` and ensure optional GPU/accelerate paths are skipped when unavailable.
- **Validation:** `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest tests/checkpointing -q` plus `nox -s tests` where configured.
- **Rollback:** Remove new tests and manifest write; retain existing checkpoint code path.

### Diff E — Quickstart + plugin scaffolding clarity
- **Existing artefacts:** README and scattered docs; plugin entry points registered in `pyproject.toml` but scaffolding sparse.
- **Gap/Risk:** Onboarding friction; contributors lack guided plugin template.
- **Patchset:**
  1. Author `docs/quickstart.md` with end-to-end CPU-only walkthrough (train → eval → log review) referencing offline defaults.
  2. Add `cli/plugin_scaffold.py` to generate a template plugin module and entry-point snippet; expose via project script (e.g., `codex-plugin-scaffold`).
  3. Provide example plugin stub under `examples/plugins/hello_plugin.py` linked from docs.
- **Validation:** `python -m cli.plugin_scaffold --help`; run scaffold in temp dir and import generated module.
- **Rollback:** Remove quickstart doc, scaffold script, entry-point wiring, and example plugin.

## Evidence & Risk Register
- Maintain `codex_logs/patch_evidence.json` capturing commands, exit codes, runtime, and artefact paths per diff.
- Record identified risks (e.g., dependency drift, missing optional drivers) in `codex_logs/risks.md` with mitigation and owner.
- For deferred work, create `reports/deferred.md` with reasons, affected modules, and unblockers.

## Rollback Strategy
- One diff per commit; use `git restore -SW <paths>` or `git revert <commit>` when regression detected.
- Preserve logs in `codex_logs/rollbacks.md` detailing trigger, steps taken, and follow-up actions.
- Avoid multi-diff reverts unless interactions are proven; prefer targeted rollback to limit blast radius.

## Reporting & PR Notes
- Summarise executed diffs, validations, and residual gaps in PR description; attach pointers to evidence artefacts.
- Mention offline guardrails upheld and list any skipped validations with justification (e.g., no GPU available for Diff C).
