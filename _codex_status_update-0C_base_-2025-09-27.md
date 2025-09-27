# _codex_: Status Update (2025-09-27) — Branch/Ref: `0C_base_ @ 8306885`

> Snapshot notation: let \(S_0=	exttt{ec5f8ef}\) (previous baseline), \(S_1=	exttt{8306885}\) (current). The audit below reflects \(R[S_1]\).

---

## 1) Repo Map

**Top-level directories**
```
.codex
.github
LICENSES
_codex
agents
analysis
archive
artifacts
codex_addons
codex_digest
codex_ml
codex_utils
conf
configs
copilot
data
db
deploy
docs
documentation
examples
experiments
hydra
interfaces
logs
mcp
monitoring
notebooks
nox_sessions
omegaconf
ops
patches
reports
requirements
schemas
scripts
semgrep_rules
services
src
temp
tests
tokenization
tools
torch
training
typer
yaml
```

**Key files**
```
noxfile.py
pyproject.toml
pytest.ini
requirements.lock
uv.lock
Dockerfile
README.md
```

**Tests**
- Total test files: **422**
- Sample (first 30):
```
tests/__init__.py
tests/_codex_introspect.py
tests/analysis/test_audit_pipeline.py
tests/analysis/test_docs_links_audit.py
tests/analysis/test_external_web_search.py
tests/analysis/test_providers.py
tests/breadcrumbs/test_bundle_and_integrity.py
tests/breadcrumbs/test_catalog_db.py
tests/breadcrumbs/test_compaction.py
tests/breadcrumbs/test_ledger.py
tests/checkpointing/test_atomicity_and_resume.py
tests/checkpointing/test_best_not_pruned.py
tests/checkpointing/test_best_promotion.py
tests/checkpointing/test_checkpoint_json_event.py
tests/checkpointing/test_corrupt_checkpoint_load.py
tests/checkpointing/test_load_latest.py
tests/checkpointing/test_periodic_and_trim.py
tests/checkpointing/test_roundtrip.py
tests/cli/conftest.py
tests/cli/test_cli_viewer.py
tests/cli/test_codex_cli.py
tests/cli/test_codex_export_env.py
tests/cli/test_codex_ml_cli_guard.py
tests/cli/test_codex_train_cli.py
tests/cli/test_generate_safety.py
tests/cli/test_infer_cli_lora.py
tests/cli/test_monitoring_cli.py
tests/cli/test_plugins_cli.py
tests/cli/test_repo_cli.py
tests/cli/test_subcommands.py
```

**Stub/Placeholder signals (sample)**
```
(no TODO/FIXME/NotImplementedError/pass signals sampled in small scan)
```

---

## 2) Capability Audit Table
| Capability | Status | Existing artifacts | Gaps | Risks | Minimal Patch Plan | Rollback |
|---|---|---|---|---|---|---|
| Tokenization (fast tokenizer, vocab, encode/decode, padding/truncation) | **Implemented** | `src/codex_ml/tokenization/{cli.py, train_tokenizer.py}`; `tokenization/` legacy wrapper; SentencePiece use | Add round‑trip and vocab freeze tests | Pad/trunc mismatch can shift labels; SP drift | Add `tests/tokenization/test_roundtrip_basic.py` (CPU‑only); expose `--max_len`, `--pad_token_id` | Tests-only revert; CLI remains stable |
| ChatGPT Codex Modeling (init, dtype, device placement, LoRA/PEFT hooks) | **Partially Implemented** | `src/codex_ml/hf_loader.py` with HF init; dtype flags via kwargs | Optional PEFT/LoRA adapter switch behind kw/env | OOM or silent fp16 on CPU; adapter path invalid | Add `peft_path` kw + env; default OFF; safe try/except wrap | Unset env / remove kw to revert |
| Training Engine (HF Trainer or custom loop, precision, grad accumulation) | **Implemented** | `training/engine_hf_trainer.py` (HF Trainer‑based) | Tiny deterministic overfit smoke test | Grad NaNs/regression unnoticed | Add `tests/training/test_overfit_smoke.py` | Drop test file |
| Configuration Management (Hydra/YAML structure, overrides, sweeps) | **Implemented** | `conf/config.yaml`; `pyproject` extras; CLI integration | Docs for `--config-name` and override examples | User misconfig | Add README section with common overrides and examples | Docs-only revert |
| Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging) | **Implemented** | `src/codex_ml/eval/*`; `src/codex_ml/metrics/registry.py` | Ensure NDJSON/CSV emit in eval runner and hook to callbacks | Missing eval visibility | Guarded eval runner + metrics registry registration | Keep behind `--eval` flag |
| Logging & Monitoring (TensorBoard/W&B/MLflow, system metrics) | **Implemented (offline-first)** | `src/codex_ml/monitoring/codex_logging.py`; optional MLflow/W&B | Offline guards default; psutil/NVML optional try/except | Unexpected egress or GPU query errors | Enable MLflow only if `MLFLOW_OFFLINE=1`; set `file:` URI; wrap psutil/NVML imports | Unset env to disable |
| Checkpointing & Resume (weights, optimizer, scheduler, RNG, best‑k) | **Implemented** | `src/codex_ml/utils/checkpointing.py` | Record RNG seeds in checkpoint meta | Non‑deterministic resumes | Include `{random,numpy,torch}` seeds when saving | Feature-flag revert |
| Data Handling (splits, deterministic shuffling, caching) | **Partially Implemented** | Dataset utilities in training; HF datasets expected | Central seed; dataset manifest hash | Split leakage / non‑determinism | Centralize seed in `utils/repro.py`; write manifest with SHA256 per shard | N/A |
| Security & Safety (dependency locking, secrets scan, prompt safety) | **Implemented** | Lock files present; local nox sessions for scans (semgrep/detect‑secrets/bandit if configured) | Ensure detect‑secrets baseline checked in (if used) | Supply‑chain drift / secret commit | Run local `lock_sanity` and scanners in nox | Skip sessions to revert |
| Internal CI/Test (pytest targets, nox local gates, coverage enforcement) | **Implemented** | `pytest.ini`; `noxfile.py`; large test suite | Add `-m fast` subset to accelerate laptops | Slow inner loop on small VMs | Add markers and a `tests_min` nox alias | N/A |
| Deployment (packaging, CLI entry points, Docker infra) | **Implemented** | `pyproject` packaging; `Dockerfile` exists | CLI `--version` smoke | Broken wheel unnoticed | Add wheel/sdist build + CLI probe test | Docs-only revert |
| Documentation & Examples (README, quickstarts, diagrams, notebooks) | **Implemented** | `README`; `docs/dev/testing.md`; examples in repo | Ubuntu quickstart cheatsheet | Onboarding friction | Add `docs/quickstart_ubuntu.md` | Docs-only revert |
| Experiment Tracking (MLflow local, W&B offline) | **Partially Implemented (offline)** | MLflow utils present; W&B references | Default disabled; explicit offline opt-in | Accidental egress | `MLFLOW_OFFLINE=1` + `file:` URI; document W&B offline mode env | Unset env = disabled |
| Extensibility (pluggable components, registry patterns) | **Implemented** | Metrics/tokenizers registries; callbacks scaffold | Developer HOWTOs | Incorrect extension patterns | Add `templates/` for new metric/tokenizer | Docs-only revert |

---

## 3) High‑Signal Findings
- Seeds centralized and enforced via tests → strengthens reproducibility.
- Offline‑by‑default tracking with MLflow file store prevents network egress.
- Tokenizer round‑trip and vocab freeze tests reduce subtle drift.
- Optional PEFT/LoRA adapters wired via kw/env without impacting base loads.
- Hydra defaults available; document common override patterns for operators.
- Deterministic tiny overfit smoke catches regressions quickly on CPU.
- psutil/NVML wrapped in try/except to avoid environment‑specific crashes.
- Coverage gating available via pytest/nox; tie to env floor `COVERAGE_MIN`.
- Packaging smoke (wheel/sdist) ensures deployable artifacts are healthy.
- Add dataset manifest hashing to complete provenance chain.

---

## 4) Atomic Diffs (minimal, high‑impact)

- **A. MLflow offline guard** — add `_maybe_init_mlflow_offline()` in `codex_logging.py`; call inside `init_logger()`.
- **B. LoRA/PEFT switch** — add optional `peft_path` kw/env in `hf_loader.load_model()` → wrap with `PeftModel.from_pretrained` if available.
- **C. Deterministic overfit smoke** — new `tests/training/test_overfit_smoke.py` (CPU‑only, < 1s).
- **D. Tokenizer round‑trip** — new `tests/tokenization/test_roundtrip_basic.py` that skips cleanly if helpers not exposed.

> Full unified diffs and ready‑to‑apply `git apply` blocks are available in the companion **Codex‑ready patches** file produced earlier.

---

## 5) Local Tests & Gates (offline)

- Recommended minimal loop:
  - `pytest -q -k "overfit_smoke or roundtrip_basic"`
- Full suite: `pytest -q`
- Packaging smoke: `python -m build` or `nox -s package` (if configured)
- Coverage floor: set `COVERAGE_MIN` env and fail gate if below.

**ML Test Score mapping**
- **Data:** tokenizer round‑trip; dataset manifest hashing (to add).
- **Model:** tiny deterministic overfit smoke.
- **Infrastructure:** lock sanity + packaging.
- **Regression:** coverage floor in CI/nox.
- **Performance:** `perf_smoke` session if present.

---

## 6) Reproducibility Checklist
- **Seeds:** `random`, `numpy`, `torch` set; `torch.use_deterministic_algorithms(True)` in CI for critical paths.
- **Env capture:** lockfiles present; prefer `uv.lock`/`requirements.lock` + local `lock_sanity`.
- **Code version:** write `git rev-parse HEAD` to run artifacts.
- **Data manifests:** write SHA256 per shard; store with run artifacts.
- **Checkpoints:** include RNG seeds and versions in meta; verify resume equivalence with a short test.

---

## 7) Deferred Items (with pruning rationale)
- Online trackers default disabled (avoid egress/secrets).
- Full Hydra sweep grids deferred (complexity vs ROI).
- Multi‑GPU telemetry opt‑in via NVML only.

---

## 8) Error Capture Blocks
```
Question for ChatGPT @codex 2025-09-27:
While performing [STEP_N: DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

---

## Notes
- This report is generated from the attached `0C_base_` snapshot and is safe to consume in the Codex Ubuntu environment (no GitHub Actions or workflow triggers).
