# Repo Survey — work & PR 1926 — 2025-10-30 (UTC)

**Ref:** branch `work`  commit `6404edf9`  •  **Artifacts:** `docs/status_updates/artifacts/Previous Cycle-10-30-survey-work-and-1926_`

---

## 1) Scope & Goal
- Branch: `work`
- PR: `#1926`
- Date (UTC): `Previous Cycle-10-30`
- Objective: Re-run branch-aware survey; capture artifacts with sanitized content blocks.

## 2) Targets Collected
- A) Trainer/orchestration — unified training orchestrator + legacy shims documented.
- B) Reasoning harness — adapters + docs show trace capture alignment.
- C) Baseline configs/curricula — baseline template references curricula fragments.
- D) Evaluation preset — base reasoning evaluation preset reachable.
- E) Deploy dry-run — reasoning pod YAML + guide mirror CLI expectations.
- F) CLI/docs mismatch — audit repo-map + deploy docs vs Click command.

## 3) Findings (Highlights)
- **Trainer stack parity:** `UnifiedTrainingConfig` still enforces deterministic seeding, continual replay schema, and maintains a `train_loop` shim so legacy entrypoints hit the same orchestrator.
- **Reasoning harness coverage:** `ReasoningHead`/`ReasoningHarness` modules expose trace / tool adapters while docs walk through trace pipelines and CLI steps, indicating the reasoning stack remains discoverable.
- **Docs drift:** `docs/guides/reasoning_overview.md` still instructs `codex deploy ... --model ... --dry-run`, but the Click command only exposes `--config`, `--dry-run`, `--run-metadata-dir`; needs doc patch or CLI flag restoration.

## 4) Evidence
- `src/codex_ml/training/unified_training.py`
```text
"""Unified Training Orchestrator (Superseding preliminary patch)

Capabilities:
 - Backend strategy selection (functional / legacy) with easy future extension.
 - Deterministic seeding.
 - Resume support via consolidated checkpoint_core.
 - Callback dispatch points.
 - Deprecation channel for legacy loop.
 - Structured result dictionary.
```text

- `src/codex_ml/training/unified_training.py` (legacy shim)
```text
def train_loop(*args: Any, **kwargs: Any) -> Any:
    """Compatibility shim preserving the historical ``train_loop`` entrypoint."""

    _emit_legacy_warning(
        "train_loop",
        "codex_ml.train_loop.run_training or run_unified_training",
    )
    from codex_ml.train_loop import run_training as _legacy_train_loop

    return _legacy_train_loop(*args, **kwargs)
```text

- `src/codex_ml/models/reasoning.py`
```text
class ReasoningHead(nn.Module):
    """Projection head that maps hidden states to reasoning logits."""

    def __init__(self, cfg: ReasoningHeadConfig) -> None:
        super().__init__()
        self.cfg = cfg
        input_size = int(cfg.hidden_size)
        proj_size = int(cfg.projection_size)
        vocab = int(cfg.trace_vocab_size)
        self.projection = nn.Linear(input_size, proj_size)
        self.activation = nn.Tanh()
        self.dropout = nn.Dropout(cfg.dropout)
        self.decoder = nn.Linear(proj_size, vocab)
```text

- `docs/guides/reasoning_overview.md`
```text
2. **Training** — Training and trace capture are coordinated by the
   unified training stack:
   - `src/codex_ml/training/unified_training.py`
     exposes configuration for curriculum phases, continual replay,
     and resume strategy,
   - `src/codex_ml/train_loop.py`
     executes a single run, attaches the reasoning harness,
     and logs traces / checkpoints.
...
1. Validate manifests:
   ```bash
   codex deploy --config configs/deploy/reasoning_pod.yaml \
     --model artifacts/runs/reasoning-starter:last \
     --dry-run
   

- `configs/training/reasoning/baseline.yaml`
```text
trace_capture:
  mode: weights

curriculum:
  preset: starter
  phase_schedule: ${.preset}

reasoning:
  template: baseline

training:
  reasoning:
    enabled: true
    trace_mode: "weights"
    trace_history: 128
```text

- `configs/training/reasoning/curricula/starter.yaml`
```text
phase_schedule:
  - id: warmup
    dataset: datasets/reasoning/warmup.jsonl
    steps: 200
    metrics:
      - reasoning.trace_coverage
  - id: first_principles
    dataset: datasets/reasoning/first_principles.jsonl
    steps: 400
    metrics:
      - reasoning.win_rate
      - reasoning.critique_density
```text

- `configs/evaluation/reasoning/base.yaml`
```text
datasets:
  proof_logs:
    path: ${oc.env:CODEX_REASONING_DATA_DIR, ${hydra:runtime.cwd}/data/sample/reasoning}/proof_logs.jsonl
    limit: ${oc.env:CODEX_REASONING_PROOF_LIMIT, 50}
...
probes:
  - theorem_proving
  - math_verification
  - tool_audit
```text

- `configs/deploy/reasoning_pod.yaml`
```text
kind: ReasoningPod
name: codex-reasoning-pod
rollout_ring: 0D_base_  # Must match training metadata to pass dry-run validation.

reasoning:
  trace_capture:
    mode: weights  # {weights, activations}; switch in baseline.yaml as desired
  evaluation_preset: configs/evaluation/reasoning/base.yaml
  curriculum_template: configs/training/reasoning/baseline.yaml
```text

- `src/codex_ml/cli/codex_cli.py`
```text
@codex.command()
@click.option(
    "--config",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Path to deployment preset YAML (e.g. configs/deploy/reasoning_pod.yaml).",
)
@click.option(
    "--dry-run",
    is_flag=True,
    help="Required flag. Perform offline validation only; never touch live infra.",
)
@click.option(
    "--run-metadata-dir",
    default=Path("runs/train_loop"),
    show_default=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory containing run_metadata.json from the latest TrainLoop run.",
)
def deploy(config: Path, dry_run: bool, run_metadata_dir: Path) -> None:
    """Validate reasoning pod deployment readiness in dry-run mode."""
```text

## 5) Gaps & Remediations
| Gap | Impact | Fix (owner) | Target Ring |
|---|---|---|---|
| Deploy docs reference `--model` flag that CLI no longer exposes | Reviewers Phase 5 expect a non-existent flag, blocking dry-run parity | Update `docs/guides/reasoning_overview.md` (Docs) to drop or clarify the flag | 0D_base_/main |

## 6) Promotion Signal
# Symbolic: R = α·E + β·T + γ·D, with α+β+γ=1
- E (Eval completeness): 0.6
- T (Trace quality):     0.7
- D (Docs/deploy parity):0.9
- Weights: α=0.2, β=0.2, γ=0.6
- R = α·E + β·T + γ·D → 0.80

## 7) Artifacts
- docs/status_updates/artifacts/Previous Cycle-10-30-survey-work-and-1926_/report.md
- docs/status_updates/artifacts/Previous Cycle-10-30-survey-work-and-1926_/readiness.json
- docs/status_updates/artifacts/Previous Cycle-10-30-survey-work-and-1926_/metrics/
- docs/status_updates/artifacts/Previous Cycle-10-30-survey-work-and-1926_/logs/

## 8) Changelog (survey)
- Re-affirmed unified training + reasoning harness parity; flagged deploy CLI/doc drift.

## 9) Next Steps
- With R ≥ 0.50, commit artifacts to branch `work` once readiness gate passes.

---
_Generated with `scripts/survey.sh` • R = α·E + β·T + γ·D (α+β+γ=1)_

```