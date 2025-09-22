# _codex_: Status Update (2025-09-21)

## 1. Repository map

### Top-level highlights

| Area | Highlights | Notes |
| --- | --- | --- |
| `src/codex_ml/training/` | `run_functional_training` normalises configs, prepares datasets, applies safety filters, seeds the run and orchestrates fallback metrics when Hugging Face `datasets`/`transformers` are missing before driving the trainer and optional evaluation hooks.【F:src/codex_ml/training/__init__.py†L362-L641】 | Provides synthetic metrics without disk output when optional deps are absent; checkpoint metadata is returned in-memory only. |
| `src/codex_ml/tokenization/` | Hugging Face adapter (`HFTokenizerAdapter`) covers encode/decode/batch APIs and special-token helpers, while `SentencePieceTokenizer` handles `.model` discovery, special-token remapping and persistence; CLI helpers under `tokenization/pipeline.py` back the `codex tokenizer` commands for train/validate/encode/decode flows.【F:src/codex_ml/tokenization/hf_tokenizer.py†L1-L116】【F:src/codex_ml/tokenization/adapter.py†L1-L232】【F:src/codex_ml/tokenization/pipeline.py†L1-L162】 | Optional dependencies (`transformers`, `sentencepiece`, `tokenizers`) are required for full functionality; CLI surfaces friendly errors when they are missing. |
| `src/codex_ml/data/` | Deterministic loaders stream text, compute checksums, build cache manifests and write split artefacts while exporting provenance for offline reproducibility.【F:src/codex_ml/data/loader.py†L200-L465】 | Manifest writing is local-only; no remote dataset registry is maintained. |
| `src/codex_ml/monitoring/` | `CodexLoggers` toggles TensorBoard/W&B/MLflow, and `SystemMetricsLogger` writes psutil-based telemetry to JSONL with background threads and CLI glue for enabling GPU sampling.【F:src/codex_ml/monitoring/codex_logging.py†L1-L136】【F:src/codex_ml/monitoring/system_metrics.py†L1-L154】 | GPU telemetry depends on `pynvml`; functional training doesn’t automatically start the metrics logger yet. |
| `src/codex_ml/eval/` | Typer CLI wraps dataset loaders and metric registry lookups, emits NDJSON/CSV metrics and optional bootstrap confidence intervals for offline comparison.【F:src/codex_ml/eval/eval_runner.py†L1-L110】 | Evaluation runs are decoupled from training outputs, so orchestration must copy predictions manually. |
| `tests/` | Offline-focused tests cover tokenizer round-trips, functional training fallback metrics, telemetry flags and checkpoint save/load with torch guards.【F:tests/test_tokenizer_roundtrip.py†L1-L44】【F:tests/test_training_eval.py†L1-L33】【F:tests/test_system_metrics_logging.py†L1-L14】【F:tests/test_checkpoint_save_resume.py†L1-L27】 | Torch-dependent tests skip when CPU wheels lack `torch.nn.Linear`, leaving GPU paths untested. |
| `.codex/` | Houses status manifests, repo-scout automation, change logs and workflow runners, plus audit artefacts like `manifest-2025-09-22T02-15-21Z.json` tying together recent patches.【F:.codex/status/manifest-2025-09-22T02-15-21Z.json†L1-L27】 | Automation scripts are verbose and log-heavy; several continue to assume interactive use. |
| `tools/` | Scaffolding utilities (e.g. `apply_interfaces.py`) emit guarded patches, update docs and note errors but still include deliberate `NotImplementedError` placeholders for unimplemented writer logic.【F:tools/apply_interfaces.py†L1-L120】 | Running these generators without completing the stubs will raise, so downstream automation must patch them first. |
| `docs/` | Extensive guides for training, monitoring, interfaces and reproducibility; `docs/gaps_report.md` still lists historical findings from earlier audits without the new header emitted by the current scanner.【F:docs/gaps_report.md†L1-L64】 | Gap report is stale relative to today’s tree; needs regeneration to reflect post-remediation state. |

### Notable stubs & maintenance gaps

- Generator scripts in `tools/` (notably `apply_interfaces.py`) still contain sentinel `NotImplementedError` branches that need to be replaced before the automation can self-host interface updates.【F:tools/apply_interfaces.py†L80-L119】
- `docs/gaps_report.md` predates the latest audit pipeline and lacks the `# Gap Analysis Report` header and deduplicated entries that `scripts/run_codex_tasks.py` now emits.【F:docs/gaps_report.md†L1-L64】
- `scripts/run_codex_tasks.py` always invokes `pre-commit` and every nox session, logging failures but offering no short-circuit when those CLIs are unavailable, making local runs noisy on fresh machines.【F:scripts/run_codex_tasks.py†L34-L92】
- Functional training’s fallback path emits synthetic metrics without persisting them anywhere on disk, so observability relies on capturing stdout logs manually.【F:src/codex_ml/training/__init__.py†L520-L532】

## 2. Capability audit table

| Capability | Status | Evidence | Gaps | Risks | Minimal patch plan | Rollback plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization pipeline | **Implemented** | HF + SentencePiece adapters plus CLI pipeline cover training, validation and encode/decode workflows.【F:src/codex_ml/tokenization/adapter.py†L1-L232】【F:src/codex_ml/tokenization/pipeline.py†L41-L160】【F:src/codex_ml/cli/codex_cli.py†L20-L144】 | Streaming SentencePiece training lacks regression tests; CLI depends on optional wheels. | Silent regressions if sentencepiece/tokenizers aren’t installed; CLI exits with errors that automation must catch. | Add lightweight pytest exercising `tokenizer_train` in dry-run mode and a SentencePiece encode/decode smoke test when dependency is present. | Skip new tests when deps missing; revert to previous behaviour by removing the new test modules. |
| Model registry & PEFT | **Implemented** | Registry loads MiniLM / HF models and applies LoRA via `apply_lora` with graceful fallback when `peft` is absent.【F:src/codex_ml/models/registry.py†L1-L70】【F:src/codex_ml/peft/peft_adapter.py†L1-L109】 | LoRA config isn’t validated (dtype/device/target modules); quantisation and extended model list still absent. | Misconfiguration may silently run on CPU or ignore LoRA, reducing model quality. | Add schema validation for LoRA fields and extend registry docs to enumerate supported models; surface warnings in CLI when fallback occurs. | Make validation warnings optional behind a flag and revert new checks if they block users. |
| Functional training & evaluation | **Partially implemented** | Functional trainer normalises configs, synthesises metrics when datasets/transformers missing and runs evaluation when val data exists.【F:src/codex_ml/training/__init__.py†L362-L641】 | Metrics are returned in-memory only; no manifest or NDJSON output mirrors `eval_runner`. | Hard to audit training runs post-hoc; automation can’t diff metrics without parsing stdout. | Persist metrics to `output_dir` as NDJSON/JSON and note location in return payload; document path for tooling. | Guard writes behind a config flag so reverting just toggles the option off. |
| Data preparation & manifests | **Implemented** | Loader caches datasets, writes checksums, split counts and provenance metadata for offline reuse.【F:src/codex_ml/data/loader.py†L248-L455】 | No central catalogue or hash registry ensures dataset reuse across repos. | Duplicate datasets or corrupted caches may go unnoticed. | Emit a simple CSV/JSON index of prepared datasets keyed by checksum to aid deduplication. | Treat the index as additive metadata; delete the file to roll back. |
| Monitoring & telemetry | **Partially implemented** | `init_telemetry` toggles TB/W&B/MLflow and `SystemMetricsLogger` streams psutil metrics with NVML opt-in.【F:src/codex_ml/monitoring/codex_logging.py†L68-L133】【F:src/codex_ml/monitoring/system_metrics.py†L1-L154】 | Functional trainer doesn’t wire metrics logging; CLI lacks flag to capture system metrics automatically. | Missed resource regressions when running long jobs; threads may remain idle if not stopped explicitly. | Wrap `run_functional_training` and CLI `train` command with optional `SystemMetricsLogger` lifecycle driven by config flag. | Keep the flag defaulting to “off”; disable to revert to current no-op behaviour. |
| Checkpointing & resume | **Partially implemented** | `save_checkpoint`/`load_checkpoint` roundtrip model/optimiser state; tests verify torch integration when available.【F:tests/test_checkpoint_save_resume.py†L1-L27】 | No best-K retention, checksum validation or manifest of created checkpoints. | Disk bloat or resuming from corrupt state without warning. | Extend checkpoint metadata to include SHA256 and implement retention policy keyed by validation metric. | Keep retention disabled by default; remove metadata additions if issues arise. |
| Automation & reporting | **Needs follow-up** | `scripts/run_codex_tasks.py` updates README, generates gap reports and runs local gates, while `.codex/status/` tracks audit history.【F:scripts/run_codex_tasks.py†L1-L106】【F:.codex/status/manifest-2025-09-22T02-15-21Z.json†L1-L27】 | Gap report is stale; tasks script doesn’t short-circuit when toolchain missing; repo-scout utilities remain verbose prototypes. | Developers may chase outdated TODOs or experience noisy failures when tooling isn’t installed. | Refresh `docs/gaps_report.md`, add CLI availability checks and capture structured results for automation consumption. | Revert regenerated report and checks if they introduce regressions; existing logs remain untouched. |

## 3. High-signal findings

1. Generator scripts in `tools/` still ship sentinel `NotImplementedError` branches; running them directly will raise unless the placeholders are replaced, so they remain manual templates rather than turnkey automation.【F:tools/apply_interfaces.py†L80-L119】
2. `docs/gaps_report.md` is out-of-date and missing the new header/format produced by the latest scanner, so downstream analysts see obsolete TODO locations.【F:docs/gaps_report.md†L1-L64】
3. Functional training returns metrics as an in-memory list and never persists them to `output_dir`, leaving observability to whoever captured stdout; aligning with the evaluation runner would simplify auditing.【F:src/codex_ml/training/__init__.py†L520-L641】
4. When `datasets`/`transformers` are unavailable, the fallback trainer produces synthetic token/loss metrics without an explicit warning flag, which risks treating placeholder numbers as real results in automation.【F:src/codex_ml/training/__init__.py†L520-L534】
5. The CLI `codex train` command doesn’t expose a switch to turn on `SystemMetricsLogger`, even though the lower-level API supports it, so system telemetry must be managed manually.【F:src/codex_ml/cli/codex_cli.py†L145-L198】
6. `scripts/run_codex_tasks.py` always executes `pre-commit` and every nox session; missing CLIs raise and are only logged, creating noisy error captures rather than skipping gracefully.【F:scripts/run_codex_tasks.py†L66-L92】
7. Evaluation tooling writes NDJSON/CSV artefacts but isn’t wired into training outputs, forcing orchestration layers to shuttle predictions into `eval_runner` manually.【F:src/codex_ml/eval/eval_runner.py†L39-L110】
8. Torch-dependent tests skip whenever CPU wheels omit `torch.nn.Linear`, meaning checkpoint integrity has limited automated coverage in minimal environments.【F:tests/test_checkpoint_save_resume.py†L7-L27】

## 4. Atomic diffs

- **Diff 1 — Persist functional-training metrics to disk**  
  **Why:** Align training outputs with `eval_runner` by writing metrics to `output_dir/metrics.ndjson`, enabling offline comparisons without scraping stdout.  
  **Risk:** File IO errors could interrupt runs; ensure writes are best-effort.  
  **Rollback:** Guard behind a config flag (`training.persist_metrics`); disabling restores current behaviour.  
  **Tests:** Extend `tests/test_training_eval.py` to assert the metrics file is created during the synthetic fallback path.

- **Diff 2 — Harden `scripts/run_codex_tasks.py` gap scanning**  
  **Why:** Skip `pre-commit`/`nox` when binaries are missing and always write the modern `# Gap Analysis Report` header so `docs/gaps_report.md` stays current.  
  **Risk:** Conditional execution might hide genuine failures if detection is incorrect; log when commands are skipped.  
  **Rollback:** Remove the availability checks and header injection to return to unconditional invocation.  
  **Tests:** Add a lightweight unit test mocking `shutil.which` to ensure skips are triggered, and run the script in CI to confirm header emission.

- **Diff 3 — Wire `SystemMetricsLogger` into CLI training**  
  **Why:** Offer a `--system-metrics` flag that spawns the existing logger during `codex train`, capturing CPU/memory telemetry without manual scaffolding.  
  **Risk:** psutil absence should degrade gracefully; ensure errors are surfaced as warnings.  
  **Rollback:** Default the flag to “off” or remove the option entirely if issues arise.  
  **Tests:** Extend CLI smoke tests (or add a new one) to invoke `codex train --system-metrics auto` under monkeypatched psutil to confirm the logger starts.

## 5. Local tests & gates

```bash
python -m pytest -q --disable-warnings
nox -s lint type tests coverage
python scripts/run_codex_tasks.py  # ensures gap report regeneration succeeds
```

## 6. Reproducibility checklist

- **Seeds:** Functional trainer propagates the configured seed through dataset shuffles and numpy/torch helpers.【F:src/codex_ml/training/__init__.py†L372-L466】
- **Data provenance:** Loader writes per-split checksums and manifests alongside provenance exports for dataset preparation.【F:src/codex_ml/data/loader.py†L248-L465】
- **Environment capture:** Training/export helpers record pip-freeze and config snapshots under `provenance/` directories.【F:src/codex_ml/training/__init__.py†L430-L448】【F:src/codex_ml/utils/provenance.py†L1-L120】
- **Metrics:** Evaluation runner emits NDJSON/CSV with timestamps, enabling deterministic diffing when inputs are fixed.【F:src/codex_ml/eval/eval_runner.py†L34-L107】
- **Optional deps:** Document required extras (`transformers`, `datasets`, `sentencepiece`, `peft`, `psutil`, `wandb`, `mlflow`) for full parity; fallback paths exist but reduce fidelity.

## 7. Deferred items

- Replace sentinel `NotImplementedError` blocks in `tools/` generators with concrete implementations or clearly documented scripts.  
- Integrate checkpoint retention/verification before expanding to heavier training workloads.  
- Add packaging metadata (`pyproject.toml`) and offline wheelhouse automation once core workflows stabilise.

## 8. Error capture template

```text
Question for ChatGPT-5 YYYY-MM-DDTHH:MM:SSZ:
While performing [STEP_NUMBER:STEP_DESCRIPTION], encountered the following error:
[ERROR_MESSAGE]
Context: [BRIEF_CONTEXT]
What are the possible causes, and how can this be resolved while preserving intended functionality?
```

## 9. Integration notes

- `codex train` loads Hydra configs via `load_app_config`, emits provenance summaries and delegates to `run_functional_training`; errors are logged through `codex_ml.utils.error_log` for post-mortem review.【F:src/codex_ml/cli/codex_cli.py†L145-L198】
- Tokenizer CLI commands (`train`, `validate`, `encode`, `decode`) reuse `tokenization/pipeline.py`, honouring streaming and dry-run options to operate offline on cached corpora.【F:src/codex_ml/cli/codex_cli.py†L20-L144】【F:src/codex_ml/tokenization/pipeline.py†L41-L160】
- Evaluation CLI writes both NDJSON and CSV summaries, enabling spreadsheets or manifest ingestion for audits without additional scripting.【F:src/codex_ml/eval/eval_runner.py†L39-L107】
- Offline tests validate core flows: tokenizer round-trips, training fallback metrics, telemetry flags and checkpoint round-trips, providing confidence for environments without GPUs.【F:tests/test_tokenizer_roundtrip.py†L1-L44】【F:tests/test_training_eval.py†L1-L33】【F:tests/test_system_metrics_logging.py†L1-L14】【F:tests/test_checkpoint_save_resume.py†L1-L27】
- Latest manifest (`manifest-2025-09-22T02-15-21Z.json`) links core automation scripts, docs and tests touched during the remediation cycle, ensuring provenance for audit trails.【F:.codex/status/manifest-2025-09-22T02-15-21Z.json†L1-L27】
