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
   - **Top-level directories.** Source code under `src/` spans training loops, registries, and monitoring hooks; automation scripts live in `tools/`; tests sit in `tests/`; documentation is under `docs/`; operational assets (nox, manifests, Dockerfile) sit at the repository root.【F:src/codex_ml/training/__init__.py†L360-L558】【F:tools/apply_interfaces.py†L1-L120】【F:tests/test_training_eval.py†L1-L36】【F:docs/gaps_report.md†L1-L40】【F:noxfile.py†L1-L72】【F:Dockerfile†L1-L20】
   - **Key files.** `pyproject.toml` pins runtime/tooling dependencies and entry points; `noxfile.py` defines lint/test gates; `src/codex_ml/cli/codex_cli.py` surfaces CLI flows; `tools/status/status_update_executor.py` automates link hygiene and placeholder scans; `docs/status_update_outstanding_questions.md` tracks audit follow-ups.【F:pyproject.toml†L1-L120】【F:noxfile.py†L1-L96】【F:src/codex_ml/cli/codex_cli.py†L1-L208】【F:tools/status/status_update_executor.py†L1-L212】【F:docs/status_update_outstanding_questions.md†L1-L74】
   - **Stubs & placeholders.** `codex` CLI’s `repo_map` command still prints “not implemented”; automation scaffolds in `tools/apply_interfaces.py` ship abstract `NotImplementedError` sentinels; `docs/gaps_report.md` lists dozens of TODO/NotImplemented hotspots awaiting regeneration.【F:src/codex_ml/cli/codex_cli.py†L209-L228】【F:tools/apply_interfaces.py†L90-L135】【F:docs/gaps_report.md†L1-L58】
   - **Recent changes.** Added `tools/status/status_update_executor.py` to normalise README links, capture placeholder scans, and emit change logs/error prompts for future audits.【F:tools/status/status_update_executor.py†L1-L212】

2. **Capability Audit Table**

| Capability | Status | Existing Artifacts | Gaps | Risks | Minimal Patch Plan | Rollback Plan |
| --- | --- | --- | --- | --- | --- | --- |
| Tokenization (fast tokenizer, vocab, encode/decode, padding/truncation) | Implemented | HF & SentencePiece adapters with CLI pipeline cover training/validate/encode/ decode flows, with config coercion and streaming toggles.【F:src/codex_ml/tokenization/adapter.py†L1-L120】【F:src/codex_ml/tokenization/pipeline.py†L1-L112】【F:src/codex_ml/cli/codex_cli.py†L20-L104】 | Dry-run/streaming paths lack regression tests; adapters depend on optional wheels. | Silent regressions when optional deps absent; CLI errors bubble raw exceptions. | Add pytest dry-run/streaming smoke tests guarded by dependency markers and document fallback behaviour in CLI help. | Remove new tests or guard flags to revert to current behaviour. |
| ChatGPT Codex Modeling (model init, dtype, device placement, LoRA/PEFT hooks) | Partially implemented | Registry resolves offline checkpoints and applies LoRA adapters with dtype/device coercion and optional env overrides.【F:src/codex_ml/models/registry.py†L1-L112】【F:src/codex_ml/peft/peft_adapter.py†L1-L96】 | No schema validation for LoRA params; quantisation/backends limited; offline path errors surface late. | Misconfigurations silently fall back to CPU or skip adapters. | Add dataclass validation for LoRA config, surface warnings in CLI, and extend registry docs with known models. | Gate validation behind flag; disabling restores prior permissive flow. |
| Training Engine (HF Trainer/custom loop, precision, gradient accumulation) | Partially implemented | Functional trainer normalises configs, seeds runs, performs fallback metrics when `datasets`/`transformers` missing, and resumes from checkpoints.【F:src/codex_ml/training/__init__.py†L360-L558】 | Fallback metrics live only in memory; NDJSON manifests absent; limited precision controls beyond defaults. | Observability gaps for offline audits; missing metrics files hinder regression comparisons. | Persist fallback metrics to `output_dir/metrics.ndjson` and expose path in return payload. | Guard file writes behind config flag so toggling reverts to current behaviour. |
| Configuration Management (Hydra/YAML structure, overrides, sweeps) | Implemented | `codex_ml.config` defines dataclasses, validation, and Hydra-aware `load_app_config` override logic; CLI enforces overrides and seed injection.【F:src/codex_ml/config.py†L1-L120】【F:src/codex_ml/cli/codex_cli.py†L129-L176】 | No sweep orchestration beyond manual overrides; config errors surface as exceptions without remediation tips. | Users misconfigure sweeps or seeds leading to inconsistent runs. | Add helper CLI to render sweep manifests and embed remediation hints in `ConfigError`. | Keep new CLI optional; removing entry point restores status quo. |
| Evaluation & Metrics (validation loops, metrics API, NDJSON/CSV logging) | Implemented | Typer CLI runs dataset/metric combos, writes NDJSON & CSV with bootstrap CIs for offline comparison.【F:src/codex_ml/eval/eval_runner.py†L1-L96】 | Training pipeline doesn’t emit evaluation artefacts; metrics/resume interplay manual. | Manual shuffling of predictions between training/eval increases operational toil. | Add integration hook to dump training predictions into eval runner workspace and document path conventions. | Toggle hook off to revert if integration proves noisy. |
| Logging & Monitoring (TensorBoard/W&B/MLflow, system metrics via psutil/NVML) | Partially implemented | `init_telemetry` toggles TB/W&B/MLflow; `SystemMetricsLogger` handles psutil/NVML fallbacks and JSONL output; tests assert degraded paths when deps missing.【F:src/codex_ml/monitoring/codex_logging.py†L1-L88】【F:src/codex_ml/monitoring/system_metrics.py†L1-L120】【F:tests/test_system_metrics_logging.py†L1-L88】 | Functional trainer/CLI lack first-class system-metrics flag; metrics threads rely on manual lifecycle wiring. | Resource regressions or leaked threads in long jobs. | Add `--system-metrics` CLI flag to wrap training with logger lifecycle and ensure clean shutdown. | Default flag to “off”; removing option restores existing behaviour. |
| Checkpointing & Resume (weights, optimizer state, scheduler, RNG, best-k retention) | Partially implemented | Utility saves checkpoints with checksum manifests and provenance metadata; trainer resumes from latest checkpoint when available.【F:src/codex_ml/utils/checkpointing.py†L1-L132】【F:src/codex_ml/training/__init__.py†L494-L558】 | No best-K retention or manifest index; checksum verification optional; tests skip without torch CPU wheels. | Disk sprawl or unnoticed corruption when resumptions skip verification. | Add retention policy keyed on validation loss plus checksum verification on load; extend pytest to cover CPU fallback once torch available. | Keep retention disabled by default; revert config knobs to undo change. |
| Data Handling (dataset splits, deterministic shuffling, caching) | Implemented | Loader streams text, caches shards with checksum manifests, and prepares splits with reproducible shuffling and provenance exports.【F:src/codex_ml/data/loader.py†L200-L320】 | No global dataset index across experiments; caching assumes single-repo usage. | Duplicate datasets or stale caches across repos. | Emit consolidated CSV index of prepared datasets keyed by checksum. | Treat index as auxiliary; deleting file restores prior state. |
| Security & Safety (dependency locking, secrets scanning, prompt safety) | Partially implemented | Safety filters enforce configurable policies with environment overrides; dependencies pinned via `pyproject.toml` extras/locks.【F:src/codex_ml/safety/filters.py†L1-L112】【F:pyproject.toml†L17-L88】 | Safety policy loading relies on external YAML; secrets scanning minimal; lock refresh process manual. | Policy drift or accidental unpinned upgrades may bypass guardrails. | Add automated policy validation test and integrate secret scanning into nox session. | Skip new gate via flag to restore current workflow. |
| Internal CI/Test (pytest targets, tox/nox local gates, coverage enforcement) | Implemented | `noxfile.py` pins toolchain, ensures torch CPU wheels, records coverage artefacts, and reuses venvs for reproducible gating.【F:noxfile.py†L1-L120】 | Some GPU/torch tests still skip without wheels; docs build gate relaxed (`strict: false`). | Latent regressions for GPU-specific logic; docs warnings go unnoticed. | Add lightweight CPU-only smoke for checkpoint round-trip and schedule docs lint with warnings-as-errors behind opt-in flag. | Keep new tests optional; revert skip markers to roll back. |
| Deployment (packaging, CLI entry points, Docker infra) | Partially implemented | `pyproject.toml` exposes multiple console scripts and extras; Dockerfile builds API runtime image from pinned requirements.【F:pyproject.toml†L89-L152】【F:Dockerfile†L1-L20】 | Docker image omits training binaries and optional extras; CLI entry points scattered across packages. | Mismatched runtime vs training dependencies when shipping containers. | Add multi-stage Docker build including training extras and document offline wheelhouse assembly. | Provide separate Docker target; falling back to current runtime image reverts changes. |
| Documentation & Examples (README, quickstarts, diagrams, notebooks) | Partially implemented | README + docs/guides cover training/monitoring/repro; outstanding-questions ledger centralises audit asks.【F:docs/status_update_outstanding_questions.md†L1-L74】 | `docs/gaps_report.md` stale; repo-map CLI stub limits discoverability; notebooks outdated. | Auditors rely on stale TODO list; newcomers lack automated repo overview. | Regenerate gap report via automation, implement CLI repo map, and link to generated artefacts from README. | Revert CLI hook and restore previous doc to roll back. |
| Experiment Tracking (MLflow local tracking, W&B offline mode) | Partially implemented | Tracking utilities lazily configure MLflow runs, handle offline URIs, and expose logging helpers with no-op fallbacks.【F:src/codex_ml/tracking/mlflow_utils.py†L1-L120】 | No end-to-end workflow tying training logs to MLflow/NDJSON outputs; W&B integration lacks CLI toggles. | Missed experiment context or silent failure when enabling tracking. | Extend training CLI to accept `--tracking` preset that wires MLflow config and records run IDs. | Hide flag behind config default; removing option restores existing behaviour. |
| Extensibility (pluggable components, registry patterns) | Implemented | Registry base supports entry-point discovery, conflict detection, and lazy loading; tokenizers/models leverage registries for plug-ins.【F:src/codex_ml/registry/base.py†L1-L112】【F:src/codex_ml/models/registry.py†L1-L88】 | Limited documentation on extending registries; error surfacing minimal when entry point import fails. | Third-party extensions misconfigure entry points without guidance. | Add troubleshooting doc + CLI `codex registry list` to enumerate contributions with provenance. | Make CLI optional; removing command reverts to baseline. |

3. **High-Signal Findings**
   1. `codex repo_map` still prints a stub message, blocking auditors from generating live topology directly from the CLI.【F:src/codex_ml/cli/codex_cli.py†L209-L228】
   2. `docs/gaps_report.md` lists dozens of historical TODO/NotImplemented markers without the regenerated header produced by current tooling, leaving stale guidance in circulation.【F:docs/gaps_report.md†L1-L58】
   3. Automation scaffolds in `tools/apply_interfaces.py` keep `NotImplementedError` sentinels for tokenizer/reward/RL adapters, so generator flows raise unless manually patched first.【F:tools/apply_interfaces.py†L90-L148】
   4. Functional training’s fallback metrics never hit disk—successful runs only return an in-memory list—limiting reproducibility for offline audits.【F:src/codex_ml/training/__init__.py†L516-L544】
   5. Safety policy loading depends on optional YAML files/environment overrides; missing policies degrade silently without explicit audit trails.【F:src/codex_ml/safety/filters.py†L1-L112】
   6. System metrics logging gracefully degrades when psutil/NVML are absent, but the CLI offers no toggle to ensure threads start/stop automatically.【F:tests/test_system_metrics_logging.py†L1-L88】【F:src/codex_ml/cli/codex_cli.py†L145-L208】
   7. MLflow helpers provide lazy contexts yet training workflows never surface run IDs or tracking toggles, keeping experiment tracking manual.【F:src/codex_ml/tracking/mlflow_utils.py†L1-L120】【F:src/codex_ml/cli/codex_cli.py†L145-L208】
   8. Checkpoint manager writes checksum metadata but lacks best-K retention or checksum verification on resume, leaving corruption undetected until load time fails.【F:src/codex_ml/utils/checkpointing.py†L1-L120】
   9. Dependency locks live in `pyproject.toml`/`requirements.lock`, yet refresh procedures remain manual and undocumented in CLI scripts.【F:pyproject.toml†L1-L120】
   10. Outstanding-questions ledger hasn’t been updated since 2025-09-18; status updates must reference it but no automation ensures freshness.【F:docs/status_update_outstanding_questions.md†L1-L74】
   11. Docker image targets API runtime only—training extras and offline artefacts require manual layering, risking drift between local and container environments.【F:Dockerfile†L1-L20】
   12. Tests around checkpoint resume and training rely on torch availability; in CPU-only setups the most critical coverage still skips, masking regressions.【F:tests/test_checkpoint_save_resume.py†L1-L27】【F:tests/test_training_eval.py†L1-L36】

4. **Atomic Diffs**
### Atomic Diff 1 — Implement CLI repo map
- **Why:** Expose a deterministic repo topology snapshot for auditors without leaving the CLI.
- **Risk:** Imports `tools.status.status_update_executor` at runtime; mis-packaged tooling could raise `ImportError`.
- **Rollback:** Revert the new command body to the previous stub.
- **Tests/docs:** Add CLI smoke test ensuring `codex repo_map --json tmp` writes JSON.
```diff
diff --git a/src/codex_ml/cli/codex_cli.py b/src/codex_ml/cli/codex_cli.py
@@
-@codex.command()
-def repo_map() -> None:
-    click.echo("repo map not implemented")
+@codex.command()
+@click.option(
+    "--json",
+    "json_path",
+    default=None,
+    type=click.Path(path_type=str),
+    help="Optional path to persist the generated repo map as JSON.",
+)
+def repo_map(json_path: Optional[str]) -> None:
+    """Emit a lightweight repository map for offline audits."""
+    from tools.status.status_update_executor import build_repo_map  # type: ignore
+
+    payload = build_repo_map()
+    click.echo(json.dumps(payload, indent=2, sort_keys=True))
+    if json_path:
+        Path(json_path).write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
```

### Atomic Diff 2 — Persist fallback training metrics
- **Why:** Align fallback path with evaluation runner by saving NDJSON to disk when optional deps are missing.
- **Risk:** File-system failures could surface new exceptions; guard with best-effort logging.
- **Rollback:** Remove the write block or gate behind config flag to restore in-memory-only behaviour.
- **Tests/docs:** Extend `tests/test_training_eval.py` to assert NDJSON creation during fallback.
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
+        except Exception as exc:  # pragma: no cover - best effort logging
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

### Atomic Diff 3 — Add `--system-metrics` gate to CLI training
- **Why:** Allow operators to toggle psutil/NVML logging directly from the CLI, ensuring telemetry threads start/stop automatically.
- **Risk:** Incorrect flag wiring could leave background threads running; ensure proper shutdown even on exceptions.
- **Rollback:** Remove the new option or default to `off` to restore current behaviour.
- **Tests/docs:** Add CLI test mocking `system_metrics.log_system_metrics` to verify invocation; document flag in README.
```diff
diff --git a/src/codex_ml/cli/codex_cli.py b/src/codex_ml/cli/codex_cli.py
@@
-@click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
-@click.option(
-    "--seed",
-    type=int,
-    default=None,
-    help="Override the random seed from the config (best-effort determinism).",
-)
-def train(config: str, overrides: Tuple[str, ...], resume: bool, seed: Optional[int]) -> None:
+@click.option("--resume", is_flag=True, help="Resume from the latest checkpoint if available.")
+@click.option(
+    "--seed",
+    type=int,
+    default=None,
+    help="Override the random seed from the config (best-effort determinism).",
+)
+@click.option(
+    "--system-metrics",
+    type=click.Choice(["off", "cpu", "gpu"], case_sensitive=False),
+    default="off",
+    show_default=True,
+    help="Enable psutil/NVML system metrics logging during training.",
+)
+def train(
+    config: str,
+    overrides: Tuple[str, ...],
+    resume: bool,
+    seed: Optional[int],
+    system_metrics: str,
+) -> None:
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
+            metrics_thread = sys_metrics.log_system_metrics(metrics_path, interval=5.0)
+        run_functional_training(config=training_cfg, resume=resume)
+        provenance_dir = Path(cfg_obj.training.output_dir) / "provenance"
+        _emit_provenance_summary(provenance_dir)
+        click.echo("training complete")
     except Exception as exc:  # pragma: no cover - Click handles presentation
         log_training_error("cli.train", str(exc), f"config={config} resume={resume}")
         raise click.ClickException(str(exc)) from exc
+    finally:
+        if metrics_thread is not None:
+            metrics_thread.stop()
+            metrics_thread.join()
```

5. **Local Tests & Gates**

| Command | Purpose | Example Output | ML Test Score Coverage |
| --- | --- | --- | --- |
| `python -m pytest tests/test_training_eval.py::test_training_eval_fallback_metrics` | Ensure fallback metrics path (and future NDJSON write) works offline. | `1 passed in 2.31s` | Model, Data |
| `nox -s ci_local` | Full lint+pytest gate with coverage artefacts and torch CPU wheel installation. | `nox > Session ci_local successful` | Infrastructure, Regression |
| `python tools/status/status_update_executor.py --write` | Normalise README links, capture placeholder scan, emit change log/error prompts. | JSON snapshot with repo map & placeholder list | Infrastructure |

6. **Reproducibility Checklist**

| Item | Status | Notes |
| --- | --- | --- |
| Deterministic seeding across training/data loaders | ✅ | `run_functional_training` calls `set_reproducible`, and data prep reuses deterministic shuffles.【F:src/codex_ml/training/__init__.py†L386-L404】【F:src/codex_ml/data/loader.py†L200-L256】 |
| Environment capture (configs, pip freeze, git SHA) | ✅ | Checkpointing utilities embed provenance summaries, and training exports environment metadata per run.【F:src/codex_ml/utils/checkpointing.py†L64-L132】【F:src/codex_ml/training/__init__.py†L504-L528】 |
| Metrics artefacts persisted | ⚠️ | Evaluation runner emits NDJSON/CSV, but training fallback metrics remain in-memory until Atomic Diff 2 lands.【F:src/codex_ml/eval/eval_runner.py†L22-L86】【F:src/codex_ml/training/__init__.py†L516-L544】 |
| Dependency/version pinning | ✅ | `pyproject.toml`/lockfiles pin accelerate/transformers/torch plus dev tooling for reproducible installs.【F:pyproject.toml†L17-L88】 |
| Outstanding question ledger referenced | ⚠️ | Ledger exists but last update 2025-09-18; needs refresh when new findings arise.【F:docs/status_update_outstanding_questions.md†L1-L74】 |

7. **Deferred Items**
   - Regenerate `docs/gaps_report.md` with modern scanner output and wire refresh into `scripts/run_codex_tasks.py`.
   - Replace `tools/apply_interfaces.py` sentinels with concrete interface adapters or downgrade templates to documented examples.
   - Extend CLI training to surface MLflow run IDs and integrate with NDJSON metrics once persistence lands.

8. **Error Capture Blocks**
   - No runtime errors encountered during this audit. Future automation should leverage `tools/status/status_update_executor.py` to append structured prompts if steps fail.【F:tools/status/status_update_executor.py†L29-L88】

---

## Codex-ready Task Sequence
```yaml
Codex-ready Task Sequence:
  1. Preparation:
    - Run `python tools/status/status_update_executor.py --write` to normalise README links and capture existing placeholders.
    - Review `.codex/status/status_update_change_log.md` and docs/status_update_outstanding_questions.md for inherited gaps.【F:tools/status/status_update_executor.py†L1-L212】【F:docs/status_update_outstanding_questions.md†L1-L74】
  2. Search & Mapping:
    - Execute `codex repo_map` (post-implementation) to snapshot directory topology.
    - Inspect `docs/gaps_report.md` entries and correlate with source locations before editing.【F:docs/gaps_report.md†L1-L58】
  3. Best-Effort Construction:
    - Apply Atomic Diff 1 to expose repo map CLI, then Atomic Diff 2 to persist fallback metrics, validating with targeted pytest.
    - Wire `--system-metrics` flag (Atomic Diff 3) and document usage in README/CLI help.【F:src/codex_ml/training/__init__.py†L516-L544】【F:src/codex_ml/cli/codex_cli.py†L145-L228】
  4. Controlled Pruning:
    - Regenerate `docs/gaps_report.md`; close resolved rows in outstanding-questions ledger with timestamps.【F:docs/status_update_outstanding_questions.md†L1-L74】
    - Remove dead NotImplemented scaffolds from `tools/apply_interfaces.py` once concrete adapters land.【F:tools/apply_interfaces.py†L90-L148】
  5. Error Capture:
    - If automation fails (e.g., placeholder scan), call `ErrorCaptureRecorder.record` in `status_update_executor` to emit a prompt and log context.【F:tools/status/status_update_executor.py†L29-L88】
  6. Finalization:
    - Commit regenerated artefacts, update outstanding-questions ledger, and rerun `nox -s ci_local` before publishing.
```

**Additional Deliverable — Executable Script**
```python
#!/usr/bin/env python3
"""Automate status-update hygiene tasks for the `_codex_` repository."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
CODEX_DIR = REPO_ROOT / ".codex"
STATUS_DIR = CODEX_DIR / "status"
DEFAULT_CHANGELOG = STATUS_DIR / "status_update_change_log.md"
DEFAULT_JSON = STATUS_DIR / "status_update_scan.json"
DEFAULT_ERROR_LOG = STATUS_DIR / "status_update_errors.ndjson"


@dataclass
class ChangeLogEntry:
    """Structured entry for the status-update change log."""

    title: str
    details: Sequence[str] = field(default_factory=list)

    def render(self) -> str:
        lines = [f"- **{self.title}**"]
        for note in self.details:
            lines.append(f"  - {note}")
        return "\n".join(lines)


class ErrorCaptureRecorder:
    """Emit error-capture prompts in the mandated format."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def record(self, step: str, error: str, context: Optional[Dict[str, str]] = None) -> None:
        timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        prompt = textwrap.dedent(
            f""":::
Question for ChatGPT @codex {timestamp}:
While performing {step}, encountered the following error:
{error}
Context: {json.dumps(context or {}, sort_keys=True)}
What are the possible causes, and how can this be resolved while preserving intended functionality?
:::
"""
        ).strip()
        payload = {
            "timestamp": timestamp,
            "step": step,
            "error": error,
            "context": context or {},
            "prompt": prompt,
        }
        with self.path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, sort_keys=True) + "\n")


def normalise_readme_links(*, write: bool) -> Dict[str, Sequence[str]]:
    """Normalise README doc links and report adjustments."""

    readme_path = REPO_ROOT / "README.md"
    original_text = readme_path.read_text(encoding="utf-8")
    pattern = re.compile(r"\]\((\.\/?docs\/[^)]+)\)")
    replacements: List[str] = []

    def _replace(match: re.Match[str]) -> str:
        target = match.group(1)
        normalised = re.sub(r"/+/", "/", target)
        normalised = normalised.lstrip("./")
        if normalised.startswith("docs/"):
            if normalised != target:
                replacements.append(f"{target} -> {normalised}")
            return f"]({normalised})"
        return match.group(0)

    new_text = pattern.sub(_replace, original_text)
    missing: List[str] = []
    for link in re.findall(r"\]\((docs/[^)]+)\)", new_text):
        link_path = REPO_ROOT / link
        if not link_path.exists():
            missing.append(link)

    if write and new_text != original_text:
        readme_path.write_text(new_text, encoding="utf-8")

    return {"updated": replacements, "missing": missing}


def build_repo_map() -> Dict[str, Sequence[str]]:
    """Summarise the repository layout for downstream embedding."""

    directories: Dict[str, List[str]] = {}
    for child in sorted(REPO_ROOT.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            directories[child.name] = sorted(p.name for p in child.iterdir() if p.is_file())[:10]
    key_files = [
        "pyproject.toml",
        "requirements-dev.txt",
        "Makefile",
        "noxfile.py",
        "codex_workflow.py",
    ]
    present_files = [item for item in key_files if (REPO_ROOT / item).exists()]
    return {"directories": directories, "key_files": present_files}


def scan_placeholders() -> List[Dict[str, object]]:
    """Locate sentinel placeholders that should feed the change log."""

    targets = [REPO_ROOT / "src", REPO_ROOT / "tools", REPO_ROOT / "scripts"]
    keywords = ("NotImplementedError", "TODO", "FIXME", "pass  # stub")
    findings: List[Dict[str, object]] = []
    for base in targets:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            for idx, line in enumerate(text.splitlines(), start=1):
                if any(keyword in line for keyword in keywords):
                    findings.append({"path": str(path.relative_to(REPO_ROOT)), "line": idx, "snippet": line.strip()})
    return findings


def synthesise_change_log(entries: Sequence[ChangeLogEntry], *, write: bool, path: Path = DEFAULT_CHANGELOG) -> None:
    """Write the aggregated change log to disk when requested."""

    header = ["# Status Update Change Log", ""]
    body = [entry.render() for entry in entries]
    content = "\n".join(header + list(body)) + "\n"
    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def write_json_snapshot(payload: Dict[str, object], *, write: bool, path: Path = DEFAULT_JSON) -> None:
    """Persist the automation snapshot to JSON for reproducibility."""

    if write:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def run(work_dir: Optional[Path] = None, *, write: bool = False, error_recorder: Optional[ErrorCaptureRecorder] = None) -> Dict[str, object]:
    """Execute the automation workflow and return collected artefacts."""

    del work_dir  # Present for parity with other runners.

    results: Dict[str, object] = {}

    try:
        readme_info = normalise_readme_links(write=write)
        results["readme_links"] = readme_info
    except Exception as exc:  # pragma: no cover - defensive
        if error_recorder:
            error_recorder.record("STEP_1:README_LINK_NORMALISATION", repr(exc))
        results["readme_links_error"] = repr(exc)

    try:
        repo_map = build_repo_map()
        results["repo_map"] = repo_map
    except Exception as exc:  # pragma: no cover - defensive
        if error_recorder:
            error_recorder.record("STEP_2:REPO_MAP", repr(exc))
        results["repo_map_error"] = repr(exc)

    try:
        placeholders = scan_placeholders()
        results["placeholders"] = placeholders
    except Exception as exc:  # pragma: no cover - defensive
        if error_recorder:
            error_recorder.record("STEP_3:PLACEHOLDER_SCAN", repr(exc))
        results["placeholders_error"] = repr(exc)

    changelog_entries: List[ChangeLogEntry] = []

    readme_updates = results.get("readme_links", {})
    if isinstance(readme_updates, dict):
        updated = readme_updates.get("updated") or []
        missing = readme_updates.get("missing") or []
        if updated:
            changelog_entries.append(ChangeLogEntry("README link normalisation", list(updated)))
        if missing:
            details = [f"Missing documentation link: {item}" for item in missing]
            changelog_entries.append(ChangeLogEntry("Broken documentation links", details))

    placeholder_list = results.get("placeholders", [])
    if isinstance(placeholder_list, list) and placeholder_list:
        details = [
            f"{item['path']}:{item['line']} — {item['snippet']}"  # type: ignore[index]
            for item in placeholder_list
        ][:25]
        changelog_entries.append(ChangeLogEntry("Sentinel placeholders detected", details))

    synthesise_change_log(changelog_entries, write=write)
    write_json_snapshot(results, write=write)

    return results


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Persist generated artefacts instead of dry-run output")
    parser.add_argument(
        "--error-log", default=str(DEFAULT_ERROR_LOG), help="Path to the NDJSON error-capture log"
    )
    parser.add_argument("--json", default=str(DEFAULT_JSON), help="Override JSON snapshot path")
    parser.add_argument("--changelog", default=str(DEFAULT_CHANGELOG), help="Override change log path")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    recorder = ErrorCaptureRecorder(Path(args.error_log))

    results = run(write=args.write, error_recorder=recorder)
    if args.json != str(DEFAULT_JSON):
        write_json_snapshot(results, write=args.write, path=Path(args.json))
    if args.changelog != str(DEFAULT_CHANGELOG):
        entries = []
        if args.write:
            try:
                entries = [ChangeLogEntry("See default change log", [str(DEFAULT_CHANGELOG)])]
            except Exception as exc:  # pragma: no cover - defensive
                recorder.record("STEP_4:ALT_CHANGELOG", repr(exc))
        synthesise_change_log(entries, write=args.write, path=Path(args.changelog))

    if not args.write:
        print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
```
