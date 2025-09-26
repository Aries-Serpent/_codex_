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

# 📍_codex_: Status Update (2025-09-23)

1. **Repo Map**
   - **Top-level directories.** Source lives under `src/` (CLI, trainer, registries, monitoring); automation and scaffolding live in `tools/`; regression coverage sits in `tests/`; documentation and policy guides live beneath `docs/`; operational assets (`noxfile.py`, Dockerfile, Makefile, requirements) stay at the root.【F:src/codex_ml/cli/codex_cli.py†L33-L244】【F:src/codex_ml/training/__init__.py†L514-L681】【F:tools/status/status_update_executor.py†L1-L200】【F:tests/test_system_metrics_logging.py†L1-L102】【F:docs/guides/AGENTS.md†L1-L46】【F:noxfile.py†L1-L200】【F:Dockerfile†L1-L42】
   - **Key files.** `pyproject.toml` pins dependencies and console scripts; `noxfile.py` codifies lint/test gates with pinned torch/pytest-cov; `src/codex_ml/cli/codex_cli.py` exposes training/tokenizer CLIs; `src/codex_ml/training/__init__.py` orchestrates dataset prep, safety filters, resume logic; `tools/status/status_update_executor.py` materialises repo maps, placeholder scans, and change logs; `docs/status_update_outstanding_questions.md` tracks unresolved automation items.【F:pyproject.toml†L1-L105】【F:noxfile.py†L1-L200】【F:src/codex_ml/cli/codex_cli.py†L33-L244】【F:src/codex_ml/training/__init__.py†L514-L681】【F:tools/status/status_update_executor.py†L1-L200】【F:docs/status_update_outstanding_questions.md†L1-L74】
   - **Stubs & placeholders.** The `codex repo_map` Click command still prints "not implemented"; tooling scaffolds in `tools/apply_interfaces.py` retain `NotImplementedError` sentinels for tokenizer/reward/RL adapters; `docs/gaps_report.md` enumerates dozens of historical TODO/NotImplemented hotspots awaiting regeneration.【F:src/codex_ml/cli/codex_cli.py†L238-L244】【F:tools/apply_interfaces.py†L80-L150】【F:docs/gaps_report.md†L1-L79】
   - **Recent changes.** Status-update automation (`tools/status/status_update_executor.py`) remains the latest notable addition, normalising README links, emitting repo maps, and capturing placeholder scans for audits.【F:tools/status/status_update_executor.py†L1-L200】

2. **Capability Audit Table**

| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization (fast tokenizer, vocab, encode/decode, padding/truncation) | Implemented | YAML-driven pipeline loads, trains, validates tokenizers and exposes CLI encode/decode flows with SentencePiece/HF adapters.【F:src/codex_ml/tokenization/pipeline.py†L1-L200】【F:src/codex_ml/cli/codex_cli.py†L44-L149】 | Dry-run/streaming toggles lack regression tests and manifest refresh automation. | Silent CLI regressions if optional deps drift; stale manifests mislead auditors. | Add pytest smoke tests covering dry-run + streaming toggles and surface manifest regeneration instructions in docs. | Skip new tests and revert doc additions to restore current behaviour. |
| ChatGPT Codex Modeling (model init, dtype, device placement, LoRA/PEFT hooks) | Partially implemented | Registry resolves offline checkpoints, enforces local-files-only semantics, and applies LoRA adapters before returning models.【F:src/codex_ml/models/registry.py†L16-L180】 | No schema validation on LoRA params; missing docs for offline directory layout. | Misconfiguration falls back to CPU silently or crashes late in training. | Introduce dataclass validation for LoRA config fields and document offline weight layout in README. | Guard validation behind flag and revert README snippet if it causes churn. |
| Training Engine (HF Trainer or custom loop, precision, gradient accumulation) | Partially implemented | Functional trainer normalises configs, seeds runs, applies safety filters, supports resume, and falls back to synthetic metrics when HF deps missing.【F:src/codex_ml/training/__init__.py†L520-L681】 | Fallback metrics never persist to disk; resume path lacks NDJSON manifest for audits. | Offline runs lose provenance; resume debugging requires manual reproduction. | Persist fallback metrics to `metrics.ndjson` and log resume manifests alongside provenance. | Wrap writes in feature flag; disabling flag reverts to current in-memory metrics. |
| Configuration Management (Hydra/YAML structure, overrides, sweeps) | Implemented | `load_app_config` enforces schema, CLI exposes overrides/seed injection, and training config coercion handles LoRA/optimiser defaults.【F:src/codex_ml/cli/codex_cli.py†L160-L216】【F:src/codex_ml/training/__init__.py†L360-L512】 | Sweep orchestration still manual and lacks CLI helper. | Operators duplicate configs or forget to set seeds. | Add `codex config sweep` command to render Hydra overrides and seed matrix templates. | Remove CLI helper to restore manual override flow. |
| Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging) | Implemented | Standalone evaluation runner writes NDJSON/CSV outputs, bootstraps metrics, and integrates with metrics registry.【F:src/codex_ml/eval/eval_runner.py†L1-L133】 | Training fallback path doesn't emit NDJSON, forcing manual collation. | Hard to correlate fallback training with evaluation dashboards. | Share evaluation writer with training fallback to emit NDJSON artefacts and document shared format. | Toggle writer off via config if integration causes churn. |
| Logging & Monitoring (TensorBoard / W&B / MLflow, system metrics via `psutil`/NVML) | Partially implemented | Telemetry bootstrap selects TB/W&B/MLflow modes; system metrics sampler degrades gracefully when psutil/NVML absent and is covered by tests.【F:src/codex_ml/monitoring/system_metrics.py†L1-L200】【F:tests/test_system_metrics_logging.py†L1-L102】 | CLI lacks first-class toggle for background sampler; thread lifecycle tied to manual wiring. | Background threads can leak or never start in production. | Add `--system-metrics` flag to CLI training to manage sampler lifecycle with guaranteed shutdown. | Default flag to off; removing new code restores existing behaviour. |
| Checkpointing & Resume (weights, optimizer state, scheduler, RNG, best-k retention) | Partially implemented | Trainer coerces checkpoint paths, ensures directories exist, and integrates resume-from CLI flag for manual restarts.【F:src/codex_ml/training/__init__.py†L654-L707】【F:src/codex_ml/cli/codex_cli.py†L169-L216】 | No best-K retention or checksum validation on load; CLI lacks health summary after resume. | Resuming stale or corrupt checkpoints without detection. | Add checksum verification and limited best-K policy plus CLI summary of restored checkpoint metadata. | Skip verification/retention behind config knob to revert. |
| Data Handling (dataset splits, deterministic shuffling, caching) | Implemented | Loader caches datasets with checksum manifests, enforces deterministic shuffles, and splits JSONL via helper utilities.【F:src/codex_ml/training/__init__.py†L531-L586】【F:src/codex_ml/data/loader.py†L208-L316】 | Global dataset index absent; manifest artefacts not consolidated for audits. | Duplicate corpora and cache drift across runs. | Emit consolidated manifest index CSV/JSON summarising prepared datasets and hook into README. | Treat index as optional artefact; removing writer reverts behaviour. |
| Security & Safety (dependency locking, secrets scanning, prompt safety) | Partially implemented | Safety filters enforce policy files, bypass flags, and log matches; dependencies pinned in pyproject extras/locks.【F:src/codex_ml/safety/filters.py†L1-L182】【F:pyproject.toml†L1-L88】 | Secrets scanning only via optional git-secrets; policy validation tests absent. | Policy drift or unnoticed bypass undermines guardrails. | Add pytest covering policy parsing plus integrate offline secret scan in nox session. | Skip new test/session to roll back without side effects. |
| Internal CI/Test (pytest targets, tox/nox local gates, coverage enforcement) | Implemented | `noxfile.py` pins torch/pytest-cov, enforces coverage fail-under, records coverage artefacts, and reuses venvs for deterministic gates.【F:noxfile.py†L1-L200】 | GPU-specific smoke coverage absent; docs build runs in non-strict mode. | Latent GPU regressions and silent doc drift. | Add CPU-only checkpoint round-trip test and optional strict docs lint session. | Keep new tests optional; disable session to revert. |
| Deployment (packaging, CLI entry points, Docker infra) | Partially implemented | Multi-stage Dockerfile ships runtime image; pyproject exposes multiple console scripts and entry points.【F:Dockerfile†L1-L42】【F:pyproject.toml†L54-L83】 | Docker image omits training extras and telemetry deps; no multi-stage build for offline wheelhouse. | Runtime/container drift between training and inference. | Introduce optional Docker target installing `[train,tracking]` extras and document offline wheel mirroring. | Retain existing Docker target as default and drop extras stage if issues arise. |
| Documentation & Examples (README, quickstarts, diagrams, notebooks) | Partially implemented | README links to quickstart, architecture diagram, and policy docs; outstanding-question ledger centralises audit asks.【F:README.md†L1-L120】【F:docs/status_update_outstanding_questions.md†L1-L74】 | `docs/gaps_report.md` stale; repo-map CLI stub blocks live topology exports. | Auditors rely on outdated TODO catalogue and manual tree inspection. | Regenerate gap report via automation, implement `codex repo_map` JSON writer, and cross-link from README. | Revert CLI change and restore prior report snapshot to roll back. |
| Experiment Tracking (MLflow local tracking, W&B offline mode) | Partially implemented | Telemetry helpers initialise TB/W&B/MLflow; tracker utilities respect offline URIs and degrade gracefully.【F:src/codex_ml/monitoring/codex_logging.py†L1-L88】【F:src/codex_ml/monitoring/system_metrics.py†L1-L200】 | No end-to-end workflow wiring training outputs into MLflow/NDJSON simultaneously. | Tracking runs miss metrics or diverge from saved artefacts. | Add CLI preset that configures MLflow experiment + NDJSON sink in tandem. | Guard preset behind optional flag; disabling removes integration. |
| Extensibility (pluggable components, registry patterns) | Implemented | Registry primitives support entry-point discovery; tokenizers/models leverage registries for plug-ins and offline fallback.【F:src/codex_ml/models/registry.py†L16-L200】【F:pyproject.toml†L65-L83】 | CLI lacks `registry list` helper and docs omit troubleshooting for failed entry points. | Third-party plug-ins fail silently without discovery surface. | Add `codex registry list` command enumerating entry points and statuses with doc linkage. | Remove helper command to restore baseline ergonomics. |

3. **High-Signal Findings**
   1. `codex repo_map` remains a stub, forcing auditors to run helper scripts instead of the primary CLI for topology snapshots.【F:src/codex_ml/cli/codex_cli.py†L238-L244】
   2. Fallback training metrics stay in memory and never persist to disk, undermining reproducibility for offline runs that skip HF dependencies.【F:src/codex_ml/training/__init__.py†L672-L681】
   3. System metrics logging is implemented but cannot be toggled from the CLI, leaving background threads unmanaged during trainings.【F:src/codex_ml/monitoring/system_metrics.py†L1-L200】【F:src/codex_ml/cli/codex_cli.py†L160-L216】
   4. `docs/gaps_report.md` lists historical TODOs/NotImplemented sentinels without the regenerated context from current scanners, risking stale remediation plans.【F:docs/gaps_report.md†L1-L79】
   5. Registry helpers enforce offline-first semantics yet lack documentation on expected directory structures, increasing friction for air-gapped installs.【F:src/codex_ml/models/registry.py†L120-L179】
   6. Coverage gate remains healthy but still lacks GPU-aware smoke cases, leaving future CUDA-specific regressions undetected.【F:noxfile.py†L1-L200】
   7. Safety filters rely on external YAML policies; missing validation tests mean policy syntax errors surface only at runtime.【F:src/codex_ml/safety/filters.py†L50-L182】
   8. Tokenizer pipeline supports streaming toggles but lacks automated manifest regeneration, risking stale corpora indexes for audits.【F:src/codex_ml/tokenization/pipeline.py†L69-L123】
   9. Outstanding-questions ledger continues to require manual syncing with status reports, inviting drift if not embedded or referenced explicitly.【F:docs/status_update_outstanding_questions.md†L1-L74】
   10. Status-update automation script (`tools/status/status_update_executor.py`) provides repo maps and placeholder scans, but reports still rely on manual embedding of results, slowing daily hygiene.【F:tools/status/status_update_executor.py†L98-L200】

4. **Atomic Diffs**
### Atomic Diff 1 — Implement `codex repo_map`
- **Why:** Surface repository topology via the primary CLI, matching automation output without bespoke scripts.
- **Risk:** Miswired imports could drag in heavy tooling or break on Windows paths.
- **Rollback:** Remove the new command body and reinstate the stub string.
- **Tests/docs:** Add CLI smoke test verifying JSON output and document command usage in README.
```diff
diff --git a/src/codex_ml/cli/codex_cli.py b/src/codex_ml/cli/codex_cli.py
@@
-@codex.command()
-def repo_map() -> None:
-    click.echo("repo map not implemented")
+@codex.command()
+@click.option(
+    "--json-path",
+    type=click.Path(dir_okay=False, path_type=str),
+    default=None,
+    help="Optional path to write the repo-map JSON payload.",
+)
+def repo_map(json_path: Optional[str]) -> None:
+    """Print a repository topology summary suitable for audits."""
+    from tools.status.status_update_executor import build_repo_map
+
+    payload = build_repo_map()
+    click.echo(json.dumps(payload, indent=2, sort_keys=True))
+    if json_path:
+        Path(json_path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
```

### Atomic Diff 2 — Persist fallback training metrics to disk
- **Why:** Preserve reproducibility for offline runs that rely on synthetic metrics when HF dependencies are unavailable.
- **Risk:** File-system write failures could raise new exceptions unless guarded.
- **Rollback:** Remove the write block or gate it behind a config flag.
- **Tests/docs:** Extend `tests/test_training_eval.py` (or new fallback test) to assert NDJSON emission.
```diff
diff --git a/src/codex_ml/training/__init__.py b/src/codex_ml/training/__init__.py
@@
-    except Exception:  # pragma: no cover - optional dependencies
-        tokens = sum(len(text.split()) for text in train_texts)
-        metrics = [
-            {"epoch": epoch, "tokens": tokens, "loss": round(1.0 / (epoch + 1), 4)}
-            for epoch in range(max(cfg.max_epochs, 1))
-        ]
-        return {"metrics": metrics, "checkpoint_dir": None, "resumed_from": None}
+    except Exception:  # pragma: no cover - optional dependencies
+        tokens = sum(len(text.split()) for text in train_texts)
+        metrics = [
+            {"epoch": epoch, "tokens": tokens, "loss": round(1.0 / (epoch + 1), 4)}
+            for epoch in range(max(cfg.max_epochs, 1))
+        ]
+        metrics_path = output_dir / "metrics.ndjson"
+        try:
+            with metrics_path.open("w", encoding="utf-8") as handle:
+                for row in metrics:
+                    handle.write(json.dumps(row, sort_keys=True) + "\n")
+        except Exception as exc:  # pragma: no cover - best-effort logging
+            log_error(
+                "train.persist_metrics",
+                repr(exc),
+                json.dumps({"path": str(metrics_path)}),
+            )
+        return {
+            "metrics": metrics,
+            "metrics_path": str(metrics_path),
+            "checkpoint_dir": None,
+            "resumed_from": None,
+        }
```

### Atomic Diff 3 — Add `--system-metrics` toggle to CLI training
- **Why:** Allow operators to enable/disable psutil/NVML sampling from the CLI while guaranteeing clean shutdowns.
- **Risk:** Improper thread management could hang process exit if join logic fails.
- **Rollback:** Remove the new option and lifecycle block.
- **Tests/docs:** Add CLI test mocking `system_metrics.log_system_metrics` and document flag in README.
```diff
diff --git a/src/codex_ml/cli/codex_cli.py b/src/codex_ml/cli/codex_cli.py
@@
-@click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
+@click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
 @click.option(
@@
-@click.option(
-    "--resume-from",
-    type=click.Path(file_okay=False, path_type=str),
-    default=None,
-    help="Optional checkpoint directory or file to resume from.",
-)
+@click.option(
+    "--resume-from",
+    type=click.Path(file_okay=False, path_type=str),
+    default=None,
+    help="Optional checkpoint directory or file to resume from.",
+)
+@click.option(
+    "--system-metrics",
+    type=click.Choice(["off", "cpu", "gpu"], case_sensitive=False),
+    default="off",
+    show_default=True,
+    help="Enable psutil/NVML system metrics logging during training.",
+)
 def train(
-    config: str,
-    overrides: Tuple[str, ...],
-    resume: bool,
-    seed: Optional[int],
-    resume_from: Optional[str],
+    config: str,
+    overrides: Tuple[str, ...],
+    resume: bool,
+    seed: Optional[int],
+    resume_from: Optional[str],
+    system_metrics: str,
 ) -> None:
@@
-    try:
-        run_functional_training(config=training_cfg, resume=resume)
-        provenance_dir = Path(cfg_obj.training.output_dir) / "provenance"
-        _emit_provenance_summary(provenance_dir)
-        click.echo("training complete")
+    metrics_thread = None
+    try:
+        if system_metrics.lower() != "off":
+            from codex_ml.monitoring import system_metrics as sys_metrics
+
+            metrics_path = Path(cfg_obj.training.output_dir) / "system-metrics.ndjson"
+            metrics_thread = sys_metrics.log_system_metrics(
+                metrics_path,
+                interval=5.0,
+                poll_gpu=system_metrics.lower() == "gpu",
+            )
+        run_functional_training(config=training_cfg, resume=resume)
+        provenance_dir = Path(cfg_obj.training.output_dir) / "provenance"
+        _emit_provenance_summary(provenance_dir)
+        click.echo("training complete")
     except Exception as exc:  # pragma: no cover - Click handles presentation
         log_training_error(
             "cli.train",
             str(exc),
             f"config={config} resume={resume} resume_from={resume_from}",
         )
         raise click.ClickException(str(exc)) from exc
+    finally:
+        if metrics_thread is not None:
+            metrics_thread.stop()
+            metrics_thread.join()
```

5. **Local Tests & Gates**

| Command | Purpose | Example Output | ML Test Score Coverage |
| --- | --- | --- | --- |
| `python -m pytest tests/test_system_metrics_logging.py::test_log_system_metrics_degrades_when_dependencies_missing` | Ensure telemetry degrades gracefully and still records metrics when psutil/NVML absent. | `1 passed in 0.42s` | Infrastructure |
| `python -m pytest tests/test_training_eval.py::test_training_eval_fallback_metrics` | Validate fallback metrics path (extend once NDJSON persistence lands). | `1 passed in 2.3s` | Model, Data |
| `nox -s tests` | Run pinned lint/test/coverage gate with offline torch handling. | `nox > Session tests successful` | Infrastructure, Regression |
| `python tools/status/status_update_executor.py --write` | Normalise README links, emit repo map + placeholder scan for audit hygiene. | `{"repo_map": {...}, "placeholders": [...]}` | Infrastructure |

6. **Reproducibility Checklist**

| Item | Status | Notes |
| --- | --- | --- |
| Deterministic seeds propagated | ✅ | Trainer seeds RNG via config coercion and dataset loaders maintain reproducible shuffles.【F:src/codex_ml/training/__init__.py†L531-L586】【F:src/codex_ml/data/loader.py†L208-L355】 |
| Dependency pins / lockfiles | ✅ | `pyproject.toml` pins core deps/extras; nox enforces specific torch/pytest-cov versions for gates.【F:pyproject.toml†L1-L105】【F:noxfile.py†L1-L120】 |
| Provenance capture | ✅ | Training exports provenance summaries and CLI emits JSON overview post-run.【F:src/codex_ml/cli/codex_cli.py†L174-L209】【F:src/codex_ml/training/__init__.py†L654-L681】 |
| Metrics artefacts persisted | ⚠️ | Evaluation runner emits NDJSON/CSV, but fallback training path still missing NDJSON until Atomic Diff 2 is applied.【F:src/codex_ml/eval/eval_runner.py†L1-L133】【F:src/codex_ml/training/__init__.py†L672-L681】 |
| Offline automation/logging | ✅ | Status executor writes change logs, repo maps, and placeholder scans for audit traceability.【F:tools/status/status_update_executor.py†L98-L200】 |

7. **Deferred Items**
   - Regenerate `docs/gaps_report.md` via latest placeholder scanner to avoid stale remediation pointers.【F:docs/gaps_report.md†L1-L79】
   - Replace `tools/apply_interfaces.py` scaffolds with concrete adapters or mark intentionally deferred to reduce noise in audits.【F:tools/apply_interfaces.py†L80-L150】
   - Document offline model directory expectations for registry aliases in README or dedicated guide.【F:src/codex_ml/models/registry.py†L120-L179】

8. **Error Capture Blocks**
   - No new automation errors captured during this audit; retain `tools/status/status_update_executor.py` recorder for future failures.【F:tools/status/status_update_executor.py†L37-L65】

## Outstanding Automation Questions

The canonical ledger remains authoritative; review before acting on historical blockers.【F:docs/status_update_outstanding_questions.md†L1-L74】

| Timestamp(s) | Step / Phase | Recorded blocker | Status | Still Valid? | Current disposition |
| --- | --- | --- | --- | --- | --- |
| 2025-08-26T20:36:12Z | Audit bootstrap (STEP_1:REPO_TRAVERSAL) | Repository snapshot unavailable inside the Copilot session. | Documented resolution | No – environment limitation | Run `tools/offline_repo_auditor.py` locally or attach the repo before auditing; the blocker is archived now that the workspace has direct file access. |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | Hook execution failed because `yamllint`, `mdformat`, and `detect-secrets-hook` were missing. | Retired | No – hooks removed | The active pre-commit configuration only invokes local commands (ruff, black, mypy, pytest, git-secrets, license checker, etc.), so those CLIs are optional for developers and no longer required by automation. |
| 2025-08-28T03:55:32Z | PH6: Run pytest with coverage | `pytest` rejected legacy `--cov=src/codex_ml` arguments. | Retired | No – command updated | Coverage flags were removed from `pytest.ini`, and the nox helper now targets `src/codex`, so the legacy failure mode is obsolete. |
| 2025-08-28T03:55:32Z | PH6: Run pre-commit | `check-merge-conflicts` and ruff flagged merge markers / unused imports. | Retired | No – tooling simplified | The hook set no longer includes `check-merge-conflicts`; ruff/black remain for lint enforcement, so the merge-marker question is superseded. |
| 2025-09-10T05:02:28Z; 2025-09-13 | `nox -s tests` | Coverage session failed because `pytest-cov` (or equivalent coverage plugin) was missing. | Action required | No | Resolved by commit `f0a1d82`, which pins `pytest-cov==7.0.0`, enforces coverage flags in `noxfile.py`, and logs generated JSON artifacts for auditability. |
| 2025-09-10T05:45:43Z; 08:01:19Z; 08:01:50Z; 08:02:00Z | Phase 4: `file_integrity_audit compare` | Compare step reported unexpected file changes. | Resolved | No – gate clean | Allowlist now covers the `.github/workflows.disabled/**` migration, generated validation manifests, and helper tooling; refreshed manifests produce zero unexpected entries. |
| 2025-09-10T05:46:35Z; 08:02:12Z; 13:54:41Z; 2025-09-13 | Phase 6: pre-commit | `pre-commit` command missing in the validation environment. | Action required | No | Commit `f0a1d82` adds a pinned `pre-commit==4.0.1`, verifies `pre-commit --version` during bootstrap, and records gate availability in `.codex/session_logs.db`. |
| 2025-09-10T05:46:47Z; 08:02:25Z; 13:55:11Z; 2025-09-13 | Phase 6: pytest | Test suite failed because optional dependencies were missing and locale/encoding issues surfaced. | Documented resolution | No | Tests now guard heavy imports with `pytest.importorskip` and fall back cleanly, so `pytest -q` skips gracefully without torch/transformers. |
| 2025-09-10T05:46:52Z; 07:14:07Z; 08:02:32Z | Phase 6 & Validation: MkDocs | MkDocs build aborted (strict mode warnings / missing pages). | Mitigated / deferred | Deferred | MkDocs now runs with `strict: false`; revisit strict mode once docs backlog clears. |
| 2025-09-10T07:13:54Z; 11:12:28Z | Validation: pre-commit | `pre-commit` command not found during validation. | Action required | No | See commit `f0a1d82`: validation scripts now gate on `pre-commit --version`, and the ledger entry is marked complete. |
| 2025-09-10T07:14:03Z; 11:12:36Z | Validation: pytest | Legacy `--cov=src/codex_ml` arguments rejected. | Retired | No – command updated | Covered by the coverage tooling update; rely on the current nox/pytest configuration targeting `src/codex`. |
| 2025-09-10T08:01:17Z | Phase 4: `file_integrity_audit compare` | `file_integrity_audit.py` rejected argument order. | Documented resolution | No – documented | Follow the documented invocation order to avoid the error (`compare pre post --allow-*`). |
| 2025-09-10 (`$ts`) | `tests_docs_links_audit` | Script crashed with `NameError: name 'root' is not defined`. | Documented resolution | No – fixed | `analysis/tests_docs_links_audit.py` now initialises the repository root and audit passes locally. |
| 2025-09-10T21:10:43Z; 2025-09-13 | Validation: nox | `nox` command not found. | Action required | No | Commit `f0a1d82` pins `nox==2025.5.1`, adds startup detection in `codex_workflow.py`, and logs presence/absence to `.codex/session_logs.db`. |
| 2025-09-13 | Training CLI (`python -m codex_ml.cli train-model`) | `ModuleNotFoundError: No module named "torch"`. | Documented resolution | No | Training CLI now checks for PyTorch, logs to `.codex/errors.ndjson`, and instructs installation via `codex_ml[torch]`. |
| Undated (Codex_Questions.md) | Metrics generation (`analysis_metrics.jsonl`) | `ModuleNotFoundError: No module named 'codex_ml.cli'`. | Documented resolution | No – resolved | Reference `codex.cli` instead and ensure editable install before generating metrics. |
| 2025-09-17 | Training CLI (resume) | Resume workflows required manual checkpoint selection and lacked docs. | Documented resolution | No – feature implemented | `CheckpointManager.load_latest` now finds the latest checkpoint and CLI `--resume-from` flag is documented. |

---

## Codex-ready Task Sequence
```text
Codex-ready Task Sequence:
  1. Preparation:
     - Sync environment with `uv sync --frozen` (includes pinned dev/test extras) and run `python tools/status/status_update_executor.py --write` to refresh repo map.【F:pyproject.toml†L1-L105】【F:tools/status/status_update_executor.py†L98-L200】
  2. Search & Mapping:
     - Implement `codex repo_map` using `build_repo_map()` and document expected JSON payload for auditors.【F:src/codex_ml/cli/codex_cli.py†L238-L244】【F:tools/status/status_update_executor.py†L98-L200】
  3. Best-Effort Construction:
     - Persist fallback training metrics to NDJSON, add CLI `--system-metrics` flag, and regenerate README/docs guidance for new knobs.【F:src/codex_ml/training/__init__.py†L672-L681】【F:src/codex_ml/cli/codex_cli.py†L160-L216】
  4. Controlled Pruning:
     - Trim or annotate deferred scaffolds in `tools/apply_interfaces.py` and refresh `docs/gaps_report.md` via automation to remove obsolete TODOs.【F:tools/apply_interfaces.py†L80-L150】【F:docs/gaps_report.md†L1-L79】
  5. Error Capture:
     - If automation fails, pipe exceptions through `ErrorCaptureRecorder` so prompts land in `.codex/status/status_update_errors.ndjson`.【F:tools/status/status_update_executor.py†L37-L200】
  6. Finalization:
     - Run `nox -s tests` plus targeted pytest cases, regenerate status update artefacts, and update outstanding-questions ledger before merging.【F:noxfile.py†L1-L200】【F:docs/status_update_outstanding_questions.md†L1-L74】
```
**Additional Deliverable — Executable Script**
```python
#!/usr/bin/env python3
"""Offline status-update assistant for Codex audits."""

from __future__ import annotations

import json
from pathlib import Path

from tools.status.status_update_executor import (
    ErrorCaptureRecorder,
    build_repo_map,
    normalise_readme_links,
    run,
    scan_placeholders,
)

ROOT = Path(__file__).resolve().parents[1]
STATUS_DIR = ROOT / ".codex" / "status"
STATUS_DIR.mkdir(parents=True, exist_ok=True)

def main() -> None:
    recorder = ErrorCaptureRecorder(STATUS_DIR / "status_update_errors.ndjson")
    results = run(write=False, error_recorder=recorder)
    results["repo_map"] = build_repo_map()
    results["placeholders"] = scan_placeholders()
    results["readme_links"] = normalise_readme_links(write=False)
    (STATUS_DIR / "status_update_scan.json").write_text(
        json.dumps(results, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    change_log = STATUS_DIR / "status_update_change_log.md"
    lines = ["# Status Update Change Log", "", "- **Repo map refreshed via CLI helper.**"]
    change_log.write_text("\n".join(lines) + "\n", encoding="utf-8")

if __name__ == "__main__":
    main()
```
