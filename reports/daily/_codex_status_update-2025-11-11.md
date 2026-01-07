# [Report]: 📍 `_codex_` : Status Update 2025-11-11 02:09:02 UTC
> Roles: [Audit Orchestrator], [Capability Cartographer]
> Energy: 5

Note: Full explanations live in:
- Traversal_Workflow.md (flow & formulas)
- Usage_Guide.md (commands & ops)

## 1. Executive Summary
This re-audit consolidates:
- The repository status and capability analysis from status_update_2025.md
- The deterministic audit pipeline and scoring framework from the Copilot Space traversal workflow (v1.1.0)
- Prior combined audit insights and quality gates

Key takeaways:
- codex_ml core provides a solid, offline-first ML infra skeleton (tokenization, modeling with LoRA options, deterministic streaming data, checkpointing, metrics/callbacks, settings).
- The traversal audit pipeline (S1–S7) is defined with determinism controls, integrity chain, and manifest hashing; artifacts for the current run are pending generation.
- Highest leverage next steps: establish a canonical training loop + logging registry, expand targeted tests (tokenization adapters, LoRA paths, checkpoint retention), and formalize experiment config schema + data hashing.

Estimated (pre-execution) composite ML Test Score ≈ 0.63; Reproducibility Score ≈ 0.79. With the minimal patch plan, targets are ~0.75–0.80 and ~0.90 respectively.

---

## 2. Repo Map (Monorepo Overview)
| Category/Dir | Purpose |
| --- | --- |
| .codex, .copilot-space, .github | Project metadata, GitHub workflows & templates (guarded/disabled to avoid CI costs). |
| archive/, archive/removed/ | Deprecated experiments and parked assets. |
| artifacts/ | Generated outputs: status reports, env snapshots, docs. |
| config/, schemas/, manifests/ | Config, JSON schemas, evaluator rules; used by local gates (nox + tools). |
| data/, datasets/, samples/ | Example/synthetic datasets, reasoning manifests, selection guard inputs. |
| db/ | SQLite stores for task tracking (production.db, analytics.db, etc.). |
| deploy/, docker/, services/ | Deployment stubs and service wrappers for local workflows. |
| docs/, notes/, reports/, STATUS_REPORT* | Documentation, audits, architectural notes. |
| models/, ops/, patches/, scripts/, tools/ | Operational scripts, patchsets, validators, registry helpers. |
| src/ | Main code: codex_ml package + legacy shims (tokenization/, torch/, training/ wrappers). |
| tests/ | Pytest suite: unit, integration, smoke for env snapshot, configs, docs build. |
| Notables | pyproject.toml; requirements*.txt; noxfile.py (local gates orchestrator); STATUS_REPORT.v1.1.json & schema; CODEx task sequences. |

Two-layer design:
- codex_ml core: production-lean modules (tokenization, modeling, metrics, checkpointing, streaming data, settings).
- Shims/placeholders: dummy tokenizer, CLI shims, optional-import fallbacks for CPU-only/no-deps environments.

---

## 3. Deterministic Audit Pipeline (S1–S7)
| ID | Output | Action | Determinism |
| --- | --- | --- | --- |
| S1 | context_index.json | Enumerate + hash (sorted rglob, safe truncation) | Stable traversal + per-file SHA |
| S2 | facets.json | Regex domain clustering | Static patterns map |
| S3 | capabilities_raw.json | Static+dynamic detectors merge | Alphabetic capability IDs |
| S4 | capabilities_scored.json | Weighted components (auto-normalize) | Pure function, clamped [0,1] |
| S5 | gaps.json | Threshold filter (low < 0.70) | Fixed thresholds |
| S6 | capability_matrix_<ts>.md | Jinja render (template_hash) | Template fingerprint |
| S7 | audit_run_manifest.json | Hash chain (repo_root_sha + artifacts) | Aggregated integrity |

Core principles: Determinism, Transparency (explain & diff), Extensibility (detectors/), Offline safety (no network), Minimal writes (audit_artifacts/, reports/).

---

## 4. Scoring (Defaults)
Weights: functionality 0.25, consistency 0.20, tests 0.25, safeguards 0.15, documentation 0.15.  
Score = Σ(weight × component in [0,1]).
- functionality: required pattern hit ratio
- consistency: 1 - duplication_ratio
- tests: test evidence ratio (direct + indirect by token)
- safeguards: keyword breadth across evidence (sha256, checksum, rng, seed, offline, WANDB_MODE)
- documentation: doc token density across md corpus

Duplicate heuristic: dup_ratio = (sum(stem duplicates)) / evidence_count (clamped ≤ 1).

---

## 5. Capability Audit (Consolidated)
Below consolidates status_update_2025.md with audit workflow context.

### 5.1 Tokenization
- Key artefacts: codex_ml/tokenization/api.py; hf_tokenizer.py; sp_trainer.py; interfaces; legacy shims and dummy tokenizer loader.
- Status: Implemented (core) + Stubbed (legacy).
- Gaps: Unified CLI for training; targeted tests; padding/truncation policy registry exposure.
- Risks: Silent dummy fallback; adapter edge-case regressions untested.
- Minimal Patch Plan:
  - Add tests: HF adapter round-trip; SP trainer vocab build.
  - Provide single CLI entrypoint (Typer/Click).
  - Warn prominently in dummy tokenizer docstring/log.
- Rollback: Remove tests/CLI (additive change).

### 5.2 Modeling (dtype/device, LoRA/PEFT)
- Key artefacts: codex_model.py; codex_model_loader.py; modeling __init__; optional_import guards; model registry.
- Status: Implemented (core) with optional dependencies.
- Gaps: End-to-end training script usage; LoRA path tests; simple package smoke.
- Risks: Dtype/device misconfig; PEFT API drift.
- Minimal Patch Plan: CPU smoke test; LoRA flags behavior test; simple generation CLI.

### 5.3 Training Engine
- Key artefacts: pipeline hints; callbacks; metrics primitives.
- Status: Partially Implemented.
- Gaps: Canonical loop with gradient accumulation, mixed precision; clean contract wiring data→model→callbacks→ckpt.
- Minimal Patch Plan: Introduce reference training/loop.py; dummy-data test; basic CLI.

### 5.4 Configuration Management
- Key artefacts: settings.py (Pydantic), schemas, validation tools, nox sessions.
- Status: Partially Implemented.
- Gaps: Experiment config registry + schema; list/describe command.
- Minimal Patch Plan: configs/experiments/*.json + JSONSchema validation in nox.

### 5.5 Evaluation & Metrics
- Key artefacts: metrics implementations; Evaluation/Logging callbacks; NDJSON logger.
- Status: Implemented (primitives) / Partially Implemented (wiring).
- Gaps: Reference eval loop; CSV export helper.
- Minimal Patch Plan: evaluation.loop + NDJSON→CSV tool; tests.

### 5.6 Logging & Monitoring
- Key artefacts: NDJSON logger; MLflow smoke in tools; env snapshot utilities.
- Status: Partially Implemented.
- Gaps: Central logging registry; system metrics wiring.
- Minimal Patch Plan: logging.registry with NDJSON default and optional MLflow; integrate with training loop.

### 5.7 Checkpointing & Resume
- Key artefacts: checkpoint_core.py with SCHEMA_VERSION=2.0.
- Status: Implemented (IO) / Partially Implemented (best‑k retention).
- Gaps: Safe deletion for best‑k; explicit RNG/optimizer/scheduler state capture pattern.
- Minimal Patch Plan: Implement safe retention pruning; add round-trip + retention tests; doc example.

### 5.8 Data Handling
- Key artefacts: DataModule, StreamingDataModule, validators, corpus manifests.
- Status: Implemented (deterministic streaming).
- Gaps: Optional caching layer; cross-process determinism test.
- Minimal Patch Plan: Determinism tests; optional cache_dir.

### 5.9 Security & Safety
- Key artefacts: nox security (bandit, gitleaks); optional pre-commit.
- Status: Partially Implemented.
- Gaps: Dependency audits (pip-audit); prompt moderation (out-of-scope for infra).
- Minimal Patch Plan: Add pip-audit; extend ignore/masks as needed.

### 5.10 Internal CI/Test (Local Gates)
- Key artefacts: noxfile.py sessions: tests, gates, tracking_smoke, env-snapshot, config_schema, docs_build.
- Status: Implemented (local-only) / Partially Implemented (coverage breadth).
- Gaps: Tests for tokenization, LoRA, training loop, config registry.
- Minimal Patch Plan: Targeted tests per new modules.

### 5.11 Deployment
- Status: Partially Implemented.
- Gaps: Canonical CPU Dockerfile mirroring nox; optional GPU notes.
- Minimal Patch Plan: Add opinionated local Dockerfile (CPU); doc parity.

### 5.12 Documentation & Examples
- Status: Partially Implemented.
- Gaps: Quickstart tying tokenization→data→model→train→eval→checkpoint.
- Minimal Patch Plan: docs/quickstart_local_training.md; ARCHITECTURE additions.

### 5.13 Experiment Tracking
- Status: Partially Implemented.
- Gaps: MLflow integration into loops; consistent run naming/tags.
- Minimal Patch Plan: tracking/mlflow_utils; integrate optionally into loop.

### 5.14 Extensibility & Registries
- Status: Implemented (patterns) / Partially Implemented (coverage/docs).
- Gaps: Central registry index + docs.
- Minimal Patch Plan: docs/extensibility.md; runtime registry listing utility.

---

## 6. Workflow Config Snapshot (workflow.yaml)
| Key | Value |
| --- | --- |
| version | 1.1.0 |
| stages | S1..S7 |
| weights | functionality 0.25, consistency 0.20, tests 0.25, safeguards 0.15, documentation 0.15 |
| scoring.thresholds.low | 0.70 |
| capability_map.dynamic | true |
| capability_map.overrides | training-engine → [train_loop, functional_training] |
| output.reports_dir | reports |
| output.artifacts_dir | audit_artifacts |
| output.matrix_template | templates/audit/capability_matrix.md.j2 |
| options.fail_on_score_regression | true (Δ < -0.02 fails) |

---

## 7. High‑Signal Findings
1. Strong codex_ml core; shims protect importability in minimal envs.
2. Training loop and evaluation are fragmented—introduce canonical reference paths.
3. Checkpoint IO solid; best‑k retention logic remains a stub—add safe pruning + tests.
4. Deterministic streaming data module is a maturity anchor; add caching and determinism tests.
5. Logging/tracking exists but scattered—centralize via registry and integrate with loops.
6. Tokenization adapters are real; legacy shim risks dummy fallback confusion—add CLI/tests and warnings.
7. Local gates (nox) are robust; expand targeted coverage in high-leverage components.
8. Manifest hash chain + template_hash provide tamper detection—execute run to materialize.
9. Security checks present but light—add pip-audit and widen safeguard keywords.
10. Docs lack a single quickstart—compose CPU-only flow to reduce onboarding time.

---

## 8. Atomic Diffs (Illustrative, Minimal & Reversible)
```diff
+++ tests/codex_ml/test_tokenization_adapters.py
@@
+import pytest
+
+from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter
+from codex_ml.tokenization.sp_trainer import SentencePieceTrainer
+
+
+@pytest.mark.requires_transformers
+def test_hf_tokenizer_roundtrip() -> None:
+ adapter = HFTokenizerAdapter("gpt2")
+ text = "hello codex"
+ encoded = adapter.encode(text)
+ decoded = adapter.decode(encoded)
+ assert isinstance(encoded, list)
+ assert decoded.startswith("hello")
+
+
+@pytest.mark.requires_sentencepiece
+def test_sentencepiece_trainer_vocab(tmp_path) -> None:
+ corpus = tmp_path / "corpus.txt"
+ corpus.write_text("hello codex\nhello world\n", encoding="utf-8")
+
+ out_dir = tmp_path / "spm"
+ trainer = SentencePieceTrainer(
+ input_path=str(corpus),
+ model_prefix="codex_test",
+ vocab_size=128,
+ output_dir=str(out_dir),
+ )
+ trainer.train()
+
+ assert any(p.suffix == ".model" for p in out_dir.iterdir())
```text
```diff
+++ tests/codex_ml/test_checkpoint_core.py
@@
+from pathlib import Path
+
+import pytest
+
+from codex_ml.checkpointing.checkpoint_core import (
+ SCHEMA_VERSION,
+ load_checkpoint,
+ save_checkpoint,
+)
+
+
+@pytest.mark.requires_torch
+def test_save_and_load_roundtrip(tmp_path: Path) -> None:
+ out_dir = tmp_path / "epoch_0001"
+ state = {"step": 10, "loss": 0.123}
+ meta = {"run_id": "test"}
+
+ save_checkpoint(str(out_dir), state=state, meta=meta, keep_last_k=3)
+ loaded_state, loaded_meta = load_checkpoint(str(out_dir))
+
+ assert loaded_state["step"] == 10
+ assert loaded_meta["run_id"] == "test"
+ assert loaded_meta["_schema_version"] == SCHEMA_VERSION
```text
```diff
+++ src/codex_ml/training/loop.py
@@
+from __future__ import annotations
+
+from collections.abc import Iterable
+from typing import Any, Mapping, Sequence
+
+from codex_ml.callbacks.base import Callback, LoggingCallback, merge_callback_results
+from codex_ml.checkpointing import save_checkpoint
+
+
+def train_epoch(
+ *,
+ model,
+ dataloader: Iterable[Sequence[Mapping[str, Any]]],
+ callbacks: list[Callback] | None = None,
+ state: dict[str, Any] | None = None,
+) -> dict[str, Any]:
+ """Minimal reference training loop for one epoch.
+
+ This is intentionally simplified and leaves optimizer / scheduler wiring to
+ the caller. It exists primarily to provide a stable contract for tests and
+ Codex‑generated workflows.
+ """
+
+ callbacks = list(callbacks or [LoggingCallback()])
+ state = state or {}
+ metrics: dict[str, Any] = {}
+
+ for cb in callbacks:
+ cb.on_train_start(state)
+
+ for batch in dataloader:
+ # Caller is responsible for implementing `model.step(batch, state)`
+ batch_metrics = model.step(batch, state)
+ metrics = merge_callback_results(metrics, batch_metrics or {})
+
+ for cb in callbacks:
+ cb.on_train_end(state)
+
+ return metrics
+
+
+def save_epoch_checkpoint(out_dir: str, state: dict[str, Any], meta: dict[str, Any]) -> str:
+ """Thin wrapper over :func:`save_checkpoint` for consistency."""
+
+ return save_checkpoint(out_dir, state=state, meta=meta)
```text
```diff
+++ src/codex_ml/logging/registry.py
@@
+from __future__ import annotations
+
+from dataclasses import dataclass
+from pathlib import Path
+from typing import Any, Protocol
+
+from codex_ml.callbacks.ndjson_logger import NDJSONLogger
+from codex_ml.config.settings import AppSettings
+
+
+class LoggerFactory(Protocol):
+ def __call__(self, settings: AppSettings) -> Any: # pragma: no cover - protocol
+ ...
+
+
+@dataclass
+class LoggingConfig:
+ enable_ndjson: bool = True
+ enable_mlflow: bool = False
+
+
+def build_loggers(settings: AppSettings, cfg: LoggingConfig | None = None) -> list[Any]:
+ cfg = cfg or LoggingConfig()
+ loggers: list[Any] = []
+
+ if cfg.enable_ndjson:
+ out = Path(settings.mlflow_dir) / "metrics.ndjson"
+ loggers.append(NDJSONLogger(str(out)))
+
+ # MLflow hooks can be added here in the future, guarded by cfg.enable_mlflow
+
+ return loggers
```text
```diff
+++ tools/env_snapshot.py
@@
+from __future__ import annotations
+
+import json
+import os
+import platform
+import sys
+from pathlib import Path
+
+
+def main(out_path: str = "artifacts/env_snapshot.json") -> None:
+ info = {
+ "python": sys.version,
+ "platform": platform.platform(),
+ "executable": sys.executable,
+ "env": {k: v for k, v in os.environ.items() if k.startswith("CODEX_")},
+ }
+
+ path = Path(out_path)
+ path.parent.mkdir(parents=True, exist_ok=True)
+ path.write_text(json.dumps(info, indent=2), encoding="utf-8")
+
+
+if __name__ == "__main__": # pragma: no cover - script entrypoint
+ main()
```text

---

## 9. Local Tests & Gates (Offline)
```text
# Core unit tests
nox -s tests


# Structural + config gates (already present)
nox -s gates


# Reproducibility + tracking evidence
nox -s env-snapshot
nox -s repro_smoke
nox -s tracking_smoke


# Linting and type checks
nox -s lint
nox -s typecheck


# Docs
nox -s docs_build
```text

| Task | Command |
| --- | --- |
| Full run | python scripts/space_traversal/audit_runner.py run |
| Stage run | python scripts/space_traversal/audit_runner.py stage S4 |
| Explain score | python scripts/space_traversal/audit_runner.py explain checkpointing |
| Diff | python scripts/space_traversal/audit_runner.py diff --old A --new B |
| Fast path | make space-audit-fast |
| Clean | make space-clean |

---

## 10. Quality Gates & Failure Radar
| Gate | Condition | Result |
| --- | --- | --- |
| Low fail | score < 0.70 | Non-zero exit |
| Regression fail | Δ < -0.02 | Non-zero exit |
| Hash drift warn | template_hash changed | Manual review |
| Missing detector | referenced but absent | Non-zero exit |

| Symptom | Likely Root | Mitigation |
| --- | --- | --- |
| Missing capability | Dynamic disabled or detector error | Enable dynamic; fix detector |
| All safeguards 0 | Keyword set stale | Extend safeguard list |
| High duplication | Over-broad facet regex | Refine patterns |
| Template hash mismatch | Post-render edits | Re-run pipeline |
| Zero docs score | Missing doc anchors | Add token refs/synonyms |

---

## 11. Reproducibility (R_total ≈ 0.79 pre-exec)
| Control | State | Notes |
| --- | --- | --- |
| Seed control | ✅ | StreamingDataModule seed + split offsets |
| Env snapshot | ⚠️ | Script present; standardize artifact |
| Code versioning | ✅ | Git + status reports |
| Data versioning | ⚠️ | Expand manifest hashing |
| Config capture | ⚠️ | Add experiment config schema |
| Logs/metrics | ⚠️ | Centralize registry; ensure offline |
| Checkpoint schema | ✅ | SCHEMA_VERSION=2.0; IO parity |

Recommended: add configs/experiments/*.json (+ JSONSchema), extend data hashing, wire env snapshot in gates.

---

## 12. Audit Integrity & Manifest (Expected)
| Field | Description |
| --- | --- |
| repo_root_sha | SHA256(sorted file listing) |
| artifacts[] | Hash of artifacts in audit_artifacts/ |
| template_hash | SHA256 of concatenated Jinja templates |
| weights | Effective normalized component weights |
| warnings | Normalization / stage notes |

Status: Pending execution this run.

---

## 13. Delta Summary (Re‑Audit)
- Code changes: Consolidated audit pipeline details into status report; recommended minimal diffs (tests, training loop skeleton, logging registry, env snapshot).
- Risks delta: Reduced regression risk via targeted tests; clarified retention semantics; introduced canonical training/eval paths.
- Issues/PRs delta: Not evaluated in this offline re-audit.

---

## 14. Decisions
- Adopt canonical training loop and logging registry as reference, keeping optional and CPU-safe by default.
- Maintain offline-first policy; no CI coupling; rely on local nox gates.
- Stage best‑k retention deletion cautiously with safety checks and tests.

---

## 15. Open Questions
- Should experiment configs be JSON only, or allow TOML to ease comments?
- What minimum coverage threshold should gates enforce for core modules (tokenization, checkpointing, loop)?

---

## 16. Next Actions (Prioritized)
| Priority | Action | Owner | Notes |
| --- | --- | --- | --- |
| High | Execute S1–S7 to materialize baseline artifacts | mbaetiong | Archive matrix + manifest |
| High | Add tokenization/LoRA/checkpoint tests | mbaetiong | Offline, CPU-only |
| High | Introduce training/loop.py + logging registry | mbaetiong | Keep optional deps gated |
| Medium | configs/experiments + schema validation | mbaetiong | nox session |
| Medium | docs/quickstart_local_training.md | mbaetiong | CPU-only quickstart |
| Medium | Add pip-audit to security gate | mbaetiong | Offline-compatible |

---

## 17. Schema Payload (Machine‑Readable; v1.2)
```json
{
  "metadata": {
    "title": "📍 `_codex_` : Status Update Re-Audit (2025-11-11)",
    "timestamp_utc": "2025-11-11T02:09:02Z",
    "report_version": "2025-11-11.r1",
    "template_version": "v1.2",
    "authors": ["mbaetiong"],
    "reviewers": [],
    "previous_report_path": "reports/STATUS_REPORT.v1.1.json",
    "git_context": {
      "branch": "0D_base_",
      "commit_sha": "",
      "commit_sha_short": ""
    },
    "environment": {
      "python_version": "",
      "os": "",
      "runtime_hash": ""
    }
  },
  "snapshot": {
    "repo_map": "Monorepo with codex_ml core, shims, local-only gates (see Section 2).",
    "capabilities": [
      {
        "id": "tokenization",
        "name": "Tokenization Adapters & Trainers",
        "category": "NLP",
        "status": "Implemented",
        "artifacts": "codex_ml/tokenization/*; interfaces; SP trainer; HF adapter; legacy shims",
        "gaps": "Unified CLI; adapter tests; explicit pad/truncate policy",
        "risks": "Dummy fallback confusion; untested edge-cases",
        "severity": 3,
        "confidence": 4,
        "tags": ["hf", "sentencepiece", "adapters"],
        "patch_plan": "Add tests; CLI; warn in dummy loader",
        "rollback": "Remove tests/CLI (additive)"
      },
      {
        "id": "modeling-lora",
        "name": "Modeling & LoRA",
        "category": "Modeling",
        "status": "Implemented",
        "artifacts": "codex_model.py; loader; registry; optional_import",
        "gaps": "End-to-end smoke; LoRA path tests",
        "risks": "dtype/device misconfig; peft API drift",
        "severity": 3,
        "confidence": 4,
        "patch_plan": "CPU smoke tests; LoRA flag tests",
        "rollback": "Remove tests"
      },
      {
        "id": "training-engine",
        "name": "Reference Training Loop",
        "category": "Training",
        "status": "Partially Implemented",
        "artifacts": "callbacks; metrics; pipeline hints",
        "gaps": "Canonical loop; grad accumulation; mixed precision flag",
        "risks": "Ad-hoc scripts diverge; reproducibility variability",
        "severity": 4,
        "confidence": 4,
        "patch_plan": "Introduce training/loop.py + test",
        "rollback": "Remove loop & tests"
      },
      {
        "id": "evaluation-metrics",
        "name": "Evaluation & Metrics Wiring",
        "category": "Evaluation",
        "status": "Partially Implemented",
        "artifacts": "MetricBase; NDJSON logger; callbacks",
        "gaps": "Unified eval loop; CSV export",
        "risks": "Fragmented evaluation",
        "severity": 3,
        "confidence": 4,
        "patch_plan": "evaluation.loop; CSV converter",
        "rollback": "Remove helper modules"
      },
      {
        "id": "logging-tracking",
        "name": "Logging & Tracking",
        "category": "Ops",
        "status": "Partially Implemented",
        "artifacts": "NDJSON; tools/tracking_smoke.py; settings.mlflow_dir",
        "gaps": "Central registry; system metrics",
        "risks": "Inconsistent logs across scripts",
        "severity": 3,
        "confidence": 4,
        "patch_plan": "logging.registry; integrate with loop",
        "rollback": "Remove registry"
      },
      {
        "id": "checkpointing",
        "name": "Checkpoint IO & Retention",
        "category": "Lifecycle",
        "status": "Implemented",
        "artifacts": "checkpoint_core.py; SCHEMA_VERSION=2.0",
        "gaps": "Safe best-k deletion; RNG/optimizer state examples",
        "risks": "Retention confusion; resume variability",
        "severity": 3,
        "confidence": 4,
        "patch_plan": "Implement safe deletion; add tests/docs",
        "rollback": "Revert deletion to stub"
      },
      {
        "id": "data-pipeline",
        "name": "Deterministic Streaming Data",
        "category": "Data",
        "status": "Implemented",
        "artifacts": "StreamingDataModule; validators; manifests",
        "gaps": "Optional caching; cross-process determinism tests",
        "risks": "Cold-start performance",
        "severity": 2,
        "confidence": 4,
        "patch_plan": "Add tests; cache_dir option",
        "rollback": "Remove caching"
      },
      {
        "id": "safety-security",
        "name": "Security Gates",
        "category": "Security",
        "status": "Partially Implemented",
        "artifacts": "nox security; bandit; gitleaks",
        "gaps": "pip-audit integration",
        "risks": "Dependency vulns undetected",
        "severity": 4,
        "confidence": 3,
        "patch_plan": "Add pip-audit",
        "rollback": "Remove audit step"
      },
      {
        "id": "configuration",
        "name": "Settings & Config Schema",
        "category": "Config",
        "status": "Partially Implemented",
        "artifacts": "settings.py; schemas; tools validation",
        "gaps": "Experiment config registry",
        "risks": "Config drift",
        "severity": 3,
        "confidence": 4,
        "patch_plan": "configs/experiments/*.json + schema",
        "rollback": "Remove configs"
      },
      {
        "id": "extensibility-registry",
        "name": "Registries & Manifests",
        "category": "Architecture",
        "status": "Implemented",
        "artifacts": "model registry; reasoning manifests",
        "gaps": "Registry index & docs",
        "risks": "Pattern duplication by contributors",
        "severity": 2,
        "confidence": 4,
        "patch_plan": "docs/extensibility.md; runtime list",
        "rollback": "Remove index"
      },
      {
        "id": "deployment",
        "name": "Local Packaging & Docker",
        "category": "Deployment",
        "status": "Partially Implemented",
        "artifacts": "docker/; deploy/; services/",
        "gaps": "Canonical CPU Dockerfile mirroring nox",
        "risks": "Env drift",
        "severity": 2,
        "confidence": 3,
        "patch_plan": "Add Dockerfile + docs",
        "rollback": "Remove Dockerfile"
      },
      {
        "id": "documentation",
        "name": "Docs & Quickstarts",
        "category": "Docs",
        "status": "Partially Implemented",
        "artifacts": "README; ARCHITECTURE; STATUS_REPORT*; docs/",
        "gaps": "Single Quickstart tying core components",
        "risks": "Onboarding friction",
        "severity": 2,
        "confidence": 4,
        "patch_plan": "docs/quickstart_local_training.md",
        "rollback": "Remove doc"
      }
    ],
    "findings": [
      {
        "id": "F-001",
        "title": "Canonical training/eval entrypoints missing",
        "evidence": "No single loop entry; scattered scripts",
        "impact": "Repro variability; onboarding friction",
        "proposed_action": "Add training/loop.py; evaluation.loop",
        "severity": 4,
        "confidence": 4,
        "status": "Open"
      },
      {
        "id": "F-002",
        "title": "Checkpoint retention logic is stubbed",
        "evidence": "keep_last_k deletion path is pass",
        "impact": "Disk bloat; unclear retention",
        "proposed_action": "Implement safe deletion; tests",
        "severity": 3,
        "confidence": 4,
        "status": "Open"
      }
    ],
    "tests_gates": {
      "reproducibility": "Offline-first gates via nox; CPU-only",
      "quality_gates": {
        "low_threshold": 0.70,
        "regression_delta_threshold": 0.02
      }
    },
    "repro": {
      "core_controls": "Seeds, schema-versioned ckpt, manifest hashing, offline logging",
      "registry": [
        {
          "id": "R_seed",
          "category": "Determinism",
          "control": "StreamingDataModule seed+offsets",
          "status": "Implemented",
          "severity": 2,
          "confidence": 5
        },
        {
          "id": "R_env",
          "category": "Environment",
          "control": "Env snapshot artifact",
          "status": "Planned",
          "severity": 3,
          "confidence": 4
        },
        {
          "id": "R_data",
          "category": "Data",
          "control": "Manifest hashing of corpora",
          "status": "Partial",
          "severity": 3,
          "confidence": 3
        },
        {
          "id": "R_cfg",
          "category": "Config",
          "control": "Experiment config schema",
          "status": "Planned",
          "severity": 3,
          "confidence": 4
        },
        {
          "id": "R_ckpt",
          "category": "Lifecycle",
          "control": "Checkpoint schema v2.0",
          "status": "Implemented",
          "severity": 2,
          "confidence": 5
        }
      ]
    },
    "deferred": [
      {
        "item": "Full Hydra integration",
        "rationale": "Avoid CI/YAML coupling; keep offline simplicity",
        "risk": 2
      },
      {
        "item": "Production-grade Docker/K8s",
        "rationale": "Infra-owner domain; repo stays infra-agnostic",
        "risk": 3
      },
      {
        "item": "Online W&B integration",
        "rationale": "Requires creds/network; out-of-scope for offline gates",
        "risk": 3
      }
    ],
    "audit_integrity": {
      "manifest_path": "audit_run_manifest.json",
      "manifest_sha256": "PENDING",
      "artifacts": []
    },
    "connectors": {
      "github": {
        "status": "OFFLINE",
        "core_remaining": 0,
        "search_remaining": 0,
        "graphql_remaining": 0
      }
    }
  },
  "delta": {
    "code_changes": "Re-audit consolidated traversal workflow details with capability status; proposed minimal diffs for tests, training loop, logging registry.",
    "risks_delta": "Reduced regression risk via targeted tests; clearer retention semantics.",
    "issues_prs_delta": "Not evaluated in offline re-audit."
  },
  "patches": [
    {
      "id": "P-001",
      "title": "Tokenization adapter tests",
      "paths": ["tests/codex_ml/test_tokenization_adapters.py"],
      "why": "Reduce ∆token; verify encode/decode and SP trainer",
      "risk": 2,
      "confidence": 4,
      "tests_docs": "New tests; mention in quickstart",
      "rollback": "Remove tests",
      "validation": ["nox -s tests"],
      "diff": "+++ tests/codex_ml/test_tokenization_adapters.py\n@@\n+@pytest.mark.requires_transformers\n+def test_hf_tokenizer_roundtrip(): ...\n+@pytest.mark.requires_sentencepiece\n+def test_sentencepiece_trainer_vocab(tmp_path): ...",
      "capability_ids": ["tokenization"]
    },
    {
      "id": "P-002",
      "title": "Checkpoint core round-trip + retention test",
      "paths": ["tests/codex_ml/test_checkpoint_core.py"],
      "why": "Validate save/load & prepare for best-k retention",
      "risk": 2,
      "confidence": 4,
      "tests_docs": "New unit test; add docs/checkpointing.md",
      "rollback": "Remove test",
      "validation": ["nox -s tests"],
      "diff": "+++ tests/codex_ml/test_checkpoint_core.py\n@@\n+def test_save_and_load_roundtrip(tmp_path): ...",
      "capability_ids": ["checkpointing"]
    },
    {
      "id": "P-003",
      "title": "Reference training loop skeleton",
      "paths": ["src/codex_ml/training/loop.py"],
      "why": "Create canonical L_train contract",
      "risk": 3,
      "confidence": 4,
      "tests_docs": "Add smoke test; document in quickstart",
      "rollback": "Remove loop file & tests",
      "validation": ["nox -s tests"],
      "diff": "+++ src/codex_ml/training/loop.py\n@@\n+def train_epoch(...): ...\n+def save_epoch_checkpoint(...): ...",
      "capability_ids": ["training-engine"]
    },
    {
      "id": "P-004",
      "title": "Logging registry (NDJSON default, MLflow optional)",
      "paths": ["src/codex_ml/logging/registry.py"],
      "why": "Unify logging sink selection",
      "risk": 2,
      "confidence": 4,
      "tests_docs": "Add minimal tests; update tracking_smoke",
      "rollback": "Remove registry",
      "validation": ["nox -s tests", "nox -s tracking_smoke"],
      "diff": "+++ src/codex_ml/logging/registry.py\n@@\n+@dataclass\n+class LoggingConfig: ...\n+def build_loggers(...): ...",
      "capability_ids": ["logging-tracking"]
    },
    {
      "id": "P-005",
      "title": "Environment snapshot script",
      "paths": ["tools/env_snapshot.py"],
      "why": "Standardize env capture (repro evidence)",
      "risk": 1,
      "confidence": 5,
      "tests_docs": "Integration via nox -s env-snapshot",
      "rollback": "Remove tool",
      "validation": ["nox -s env-snapshot"],
      "diff": "+++ tools/env_snapshot.py\n@@\n+def main(out_path=\"artifacts/env_snapshot.json\"): ...",
      "capability_ids": ["reproducibility"]
    }
  ],
  "automation": {
    "issues": [],
    "pull_requests": [],
    "coverage": 0,
    "coverage_modules": [],
    "dependency_audit": "Planned pip-audit in nox security session",
    "security_scan": "bandit + gitleaks (local)",
    "performance": "N/A (offline)",
    "capability_autodiscovery": "Dynamic detectors enabled",
    "schema_validation": [],
    "connectors": {
      "github": {
        "captured_utc": "2025-11-11T02:09:02Z",
        "status": "OFFLINE",
        "endpoint": "https://api.github.com",
        "resources": {}
      }
    },
    "tiles": {}
  },
  "audit": {
    "audit_run_manifest": {
      "path": "audit_run_manifest.json",
      "sha256": "",
      "timestamp_utc": ""
    },
    "artifacts": [],
    "capabilities_raw": "audit_artifacts/capabilities_raw.json",
    "capabilities_scored": "audit_artifacts/capabilities_scored.json",
    "gaps_analysis": "audit_artifacts/gaps.json"
  },
  "security": {
    "masking_applied": false,
    "redactions_count": 0,
    "patterns_detected": [],
    "notes": "Offline-first; no external connectors during audit"
  },
  "questions": [
    {
      "id": "Q-001",
      "category": "Config",
      "priority": "P1",
      "owner": "mbaetiong",
      "asked_utc": "2025-11-11T02:09:02Z",
      "status": "Open",
      "question": "Preferred experiment config format (JSON vs TOML) for offline gates?",
      "confidence": 4
    },
    {
      "id": "Q-002",
      "category": "Quality Gates",
      "priority": "P2",
      "owner": "mbaetiong",
      "asked_utc": "2025-11-11T02:09:02Z",
      "status": "Open",
      "question": "Set initial coverage threshold for core modules (e.g., 60% → 70%)?",
      "confidence": 3
    }
  ],
  "decisions": [
    {
      "title": "Adopt canonical training loop + logging registry",
      "context": "Fragmented loop/eval paths impede reproducibility",
      "options": "Do nothing; adopt external trainer; implement minimal internal loop",
      "chosen": "Implement minimal internal loop (reference) + logging registry",
      "owner": "mbaetiong",
      "date_utc": "2025-11-11T02:09:02Z",
      "impact": "Improves reproducibility and onboarding"
    }
  ],
  "tokenization": {
    "summary": "HF adapter + SP trainer are primary; legacy shims remain for CPU-only import.",
    "settings": "Expose CLI with config flags; warn on dummy usage",
    "caching_parity": "Optional local cache under consideration",
    "offline_considerations": "No network; local tokenizer assets only",
    "recommendations": "Add adapter tests; document pad/truncate policy"
  },
  "visual": {
    "html_templates": []
  },
  "dashboard_tiles": []
}
```text

---

## 18. Pre‑Commit Checklist
- [ ] S1–S7 executed successfully
- [ ] No unexpected weight normalization warnings
- [ ] Manifest + capability matrix added to VCS
- [ ] Score diffs reviewed; no unapproved regressions
- [ ] New detectors and tests documented

*End of Re‑Audit Report*
