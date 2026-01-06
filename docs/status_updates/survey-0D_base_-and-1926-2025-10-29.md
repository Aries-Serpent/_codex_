```yaml
branch: 0D_base_
pr: 1926
rollout_ring: 0D_base_
eval_preset: base
deployment_preset: reasoning_pod
generated_utc: Previous Cycle-10-29T16:45:54Z
```text

## File Survey: Branch 0D_base_ / PR #1926

### >>> FILE: src/codex_ml/training/unified_training.py@0D_base_

```python
[BEGIN CONTENT]
"""Unified Training Orchestrator (Superseding preliminary patch)

Capabilities:
 - Backend strategy selection (functional / legacy) with easy future extension.
 - Deterministic seeding.
 - Resume support via consolidated checkpoint_core.
 - Callback dispatch points.
 - Deprecation channel for legacy loop.
 - Structured result dictionary.

Schema Alignment:
 - Checkpoint metadata uses schema_version=2 (see checkpoint_core).

Usage:
    from codex_ml.training.unified_training import UnifiedTrainingConfig, run_unified_training
[END CONTENT]
```text

### >>> FILE: src/codex_ml/train_loop.py@0D_base_

```python
[BEGIN CONTENT]
per_epoch_limit: int
    top_k: int
    threshold: float | None
    traces_written: int = 0

    def bind_model(self, model: Any) -> None:
        try:
            self.harness.attach(model)
        except Exception as exc:  # pragma: no cover - defensive attachment guard
            logger.warning("Failed to bind reasoning modules to model: %s", exc)

    def on_new_epoch(self) -> None:
        self.traces_written = 0

    def should_capture(self) -> bool:
        if getattr(self.config, "trace_mode", None) == "disabled":
[END CONTENT]
```text

### >>> FILE: src/codex_ml/training/strategies.py@0D_base_

```python
[BEGIN CONTENT]
backend_name = "functional"

    def run(
        self,
        config: Any,
        callbacks: Iterable[TrainingCallback],
        resume_from: Optional[str] = None,
    ) -> TrainingResult:
        ft_module = import_module("codex_ml.training.functional_training")
        TrainConfig = getattr(ft_module, "TrainConfig")
        train_fn = getattr(ft_module, "train")

        extra_payload: Dict[str, Any] = {}

        # Minimal shim; functional loop currently handles internal logging.
[END CONTENT]
```text

### >>> FILE: src/codex_ml/models/reasoning.py@0D_base_

```python
[BEGIN CONTENT]
# Trace capture semantics are configured via `training.reasoning.trace_mode`
    # (see configs/training/reasoning/baseline.yaml). Keep this comment aligned
    # with config guidance so downstream surfaces stay honest.
    #
    #   "disabled" (current baseline)
    #       Skip trace capture entirely. Use this for day-to-day iteration.
    #
    #   "param-slice" (diagnostic fingerprint)
    #       Take a deterministic slice of the first trainable parameter tensor
    #       and log it. Useful for reproducibility / regression audits only.
    #       Not an interpretable chain-of-thought.
    #
    #   "activation-snapshot" (planned offline introspection)
    #       Pool forward-pass activations plus metadata (curriculum phase,
    #       tool usage, evaluation preset, etc.) for richer analysis.
    def _vectorise_model(self, model: Any) -> torch.Tensor:
        """Produce a trace vector for logging when traces are enabled.

        Current implementation (``trace_mode='param-slice'``) flattens a
        deterministic slice of the first trainable parameter tensor to produce
        a reproducibility fingerprint. Future "activation-snapshot" work will
        pool hidden activations together with curriculum/tool metadata.
        """
        size = int(self.head.cfg.hidden_size)
        try:
            head_device = next(self.head.parameters()).device
        except StopIteration:  # pragma: no cover - Linear modules always have params
            head_device = torch.device("cpu")
        buffer = torch.zeros(size, dtype=torch.float32, device=head_device)
        if not isinstance(model, nn.Module):
            return buffer
        first_param = None
        for param in model.parameters():
            if param.requires_grad and param.ndim > 0:
                first_param = param.detach().float().flatten()
                break
        if first_param is None:
            return buffer
        data = first_param.to(device=head_device)
        if data.numel() >= size:
            return data[:size]
[END CONTENT]
```text

### >>> FILE: configs/training/reasoning/baseline.yaml@0D_base_

```yaml
[BEGIN CONTENT]
# Template: Baseline reasoning overlay enabling traces and curriculum hooks.
# @package _global_
defaults:
  - ../base

# === CONTROL SURFACE (local-first) ===
# The fields below are the documented knobs surfaced via `codex repo-map --reasoning`
# and the deployment dry-run workflow. Adjusting them does not require code changes.

# trace_mode controls how the reasoning harness captures traces during training.
# Allowed values are "param-slice" (deterministic fingerprint) and
# "activation-snapshot" (future richer trace capture).
trace_mode: "param-slice"

curriculum:
  # preset is the curriculum name exposed to PM/infra reviewers.
  preset: starter
  phase_schedule: ${.preset}

evaluation:
  # preset defines which evaluation suite must pass before promotion.
  preset: base

deployment:
  # preset points at the expected dry-run deployment manifest.
  preset: reasoning_pod

metadata:
  # rollout_ring gate enforced by codex deploy --dry-run.
  rollout_ring: 0D_base_
  owner: reasoning-foundations

reasoning:
  template: baseline

training:
  reasoning:
    enabled: true
    # trace_mode controls how (or whether) the harness records traces.
    #
[END CONTENT]
```text

### >>> FILE: configs/training/reasoning/curricula/starter.yaml@0D_base_

```yaml
[BEGIN CONTENT]
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
  - id: challenge
    dataset: datasets/reasoning/challenge.jsonl
    steps: 300
    metrics:
      - reasoning.latency_p95
      - reasoning.judge_disagreement
[END CONTENT]
```text

### >>> FILE: configs/evaluation/reasoning/base.yaml@0D_base_

```yaml
[BEGIN CONTENT]
# Base reasoning evaluation configuration.
# Runs theorem proving accuracy, math verification, and tool trace audits
# over the sample reasoning corpora bundled with Codex ML.

defaults:
  - override hydra/job_logging: disabled
  - override hydra/hydra_logging: disabled
  - _self_

datasets:
  proof_logs:
    path: ${oc.env:CODEX_REASONING_DATA_DIR, ${hydra:runtime.cwd}/data/sample/reasoning}/proof_logs.jsonl
    limit: ${oc.env:CODEX_REASONING_PROOF_LIMIT, 50}
  math_word_problems:
    path: ${oc.env:CODEX_REASONING_DATA_DIR, ${hydra:runtime.cwd}/data/sample/reasoning}/math_word_problems.jsonl
    limit: ${oc.env:CODEX_REASONING_MATH_LIMIT, 50}
  tool_traces:
    path: ${oc.env:CODEX_REASONING_DATA_DIR, ${hydra:runtime.cwd}/data/sample/reasoning}/tool_traces.jsonl
    limit: ${oc.env:CODEX_REASONING_TOOL_LIMIT, 50}

probes:
  - theorem_proving
  - math_verification
  - tool_audit

output:
  dir: ${oc.env:CODEX_REASONING_EVAL_DIR, ${hydra:runtime.cwd}/artifacts/reasoning_eval}
  summary_filename: summary.json
  records_filename: records.ndjson
  metrics_filename: metrics.ndjson
[END CONTENT]
```text

### >>> FILE: src/codex_ml/eval/evaluator.py@0D_base_

```python
[BEGIN CONTENT]
metrics: dict[str, Any] = {}
    loss = getattr(outputs, "loss", None)
    if isinstance(outputs, Mapping):
        if loss is None and "loss" in outputs:
            loss = outputs.get("loss")
        for key in metric_keys:
            if key in outputs:
                metrics[key] = outputs[key]
    else:
        for key in metric_keys:
            metrics[key] = getattr(outputs, key, None)
    if loss is not None:
        metrics.setdefault("loss", loss)
    elif isinstance(outputs, Mapping) and "loss" in outputs:
        metrics.setdefault("loss", outputs["loss"])
    return {k: v for k, v in metrics.items() if v is not None}


class _MetricAggregator:
    def __init__(self) -> None:
        self._totals: dict[str, float] = {}
[END CONTENT]
```text

### >>> FILE: src/codex_cli/app.py@0D_base_

```python
[BEGIN CONTENT]
help="Only include specified categories (can be repeated).",
        ),
    ) -> None:
        from codex_ml.cli.repo_map import render_repo_map

        categories = tuple(include or [])
        echo(render_repo_map(reasoning=reasoning, include=categories))

    @app.command("version")
    def version() -> None:
        try:
            from . import __version__
        except Exception:  # pragma: no cover - defensive fallback
            __version__ = "unknown"
        echo(__version__)
[END CONTENT]
```text

### >>> FILE: src/codex_ml/cli/codex_cli.py@0D_base_

```python
[BEGIN CONTENT]
click.echo("prometheus_client missing", err=True)


@codex.command()
@click.argument("text")
def tokenize(text: str) -> None:
    from codex_ml.tokenization.hf_tokenizer import HFTokenizerAdapter

    tok = HFTokenizerAdapter.load()
    ids = tok.encode(text)
    click.echo(str(ids))


@codex.command()
@click.option(
    "--reasoning",
    is_flag=True,
    help=(
        "Emit reasoning-specific control surface entries (curriculum preset, "
        "trace_mode, rollout ring, evaluation preset, deployment preset)."
    ),
)
def repo_map(reasoning: bool) -> None:
    """Print a repository summary (optionally including reasoning knobs)."""

    from codex_ml.cli.repo_map import render_repo_map

    click.echo(render_repo_map(reasoning=reasoning))


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
[END CONTENT]
```text

### >>> FILE: src/codex_ml/cli/repo_map.py@0D_base_

```python
[BEGIN CONTENT]
section_key="evaluation",
                summary_key="evaluation.preset",
                rel_path=rel_path,
                value=str(evaluation),
            )
        if metadata_ring:
            _add_entry(
                section_key="rollout_ring",
                summary_key="metadata.rollout_ring",
                rel_path=rel_path,
                value=str(metadata_ring),
            )

    deploy_cfg = repo_root / "configs" / "deploy" / "reasoning_pod.yaml"
    if deploy_cfg.exists():
        data = _load_yaml(deploy_cfg)
        ring = None
        trace = None
        curriculum_phase = None
        eval_preset = None
        if data:
            ring = data.get("rollout_ring")
            env = data.get("pod", {}).get("env", [])
            if isinstance(env, list):
                for entry in env:
                    if not isinstance(entry, Mapping):
                        continue
                    name = entry.get("name")
                    value = entry.get("value")
                    if name == "CODEX_TRACE_MODE":
                        trace = value
                    elif name == "CODEX_CURRICULUM_PHASE":
                        curriculum_phase = value
                    elif name == "CODEX_EVAL_PRESET":
                        eval_preset = value
        else:
[END CONTENT]
```text

### >>> FILE: docs/README_ROOT.md@0D_base_

```markdown
[BEGIN CONTENT]
`codex repo-map --reasoning` surfaces a shared set of knobs defined in
[`configs/training/reasoning/baseline.yaml`](../configs/training/reasoning/baseline.yaml):

- `trace_mode`
- `curriculum.preset`
- `evaluation.preset`
- `deployment.preset`
- `metadata.rollout_ring`

Every smoke run of the training loop writes machine-readable artifacts under `runs/train_loop/`:

- `run_metadata.json` — captures `metadata.*`, the selected presets, and the rollout ring.
- `reasoning.json` — snapshot of the reasoning harness configuration plus runtime summary.
- `evaluation.json` — evaluation preset enforced for the run.

Promotion toward `main` requires:

1. The evaluation preset to pass (or carry explicit sign-off in status reports).
2. `metadata.rollout_ring` declared in the training config and matching the target pod ring.
3. `codex deploy --dry-run` to succeed, which enforces the ring match between training output and `configs/deploy/reasoning_pod.yaml`.

## Architecture at a glance

The canonical topology is captured in [`docs/diagrams/architecture.svg`](diagrams/architecture.svg). Pair it with the
Mermaid source (`architecture.mmd`) when proposing changes so reviewers can diff rendered assets and source together.

Key flows:

1. **Authoring** — Hydra configuration layers resolve reasoning templates from `configs/training/reasoning/*` before model
   instantiation.
2. **Training** — Training is orchestrated by:
   - `src/codex_ml/training/unified_training.py`
     (deterministic seeding, checkpoint / resume plumbing,
      continual replay strategy hooks),
   - `src/codex_ml/train_loop.py`
[END CONTENT]
```text

### >>> FILE: docs/README.md@0D_base_

```markdown
[BEGIN CONTENT]
codex deploy \
  --config configs/deploy/reasoning_pod.yaml \
  --model artifacts/runs/reasoning-starter:last \
  --dry-run

This renders the "reasoning pod" manifest for inspection. It does **not**
create or update any live service. See [`deployment/reasoning_pod.md`](./deployment/reasoning_pod.md)
for what that pod is expected to look like (resources, telemetry, trace
capture mode, curriculum phase, etc.). The CLI intentionally supports
dry-run review only — there is no automatic apply step, and the embedded
`rollout_ring` is declarative intent, not permission.

Always keep `--dry-run` in place; manifests must be reviewed before any
apply/rollout tooling is engaged.

### Rollout rings

This repository uses staged rollout rings to represent maturity and review
state:

* `0A_base_` / `0B_base_`: active development, unstable knobs.
* `0C_base_`: integration of multiple features landing together.
* `0D_base_`: release candidate. Content here should be explainable
  to Engineering and Product.
* `main`: canonical internal "alpha product" surface after approval.

When you generate a deployment manifest (`configs/deploy/reasoning_pod.yaml`),
it includes a `rollout_ring` field. That field is a declaration of intent
[END CONTENT]
```text

### >>> FILE: docs/guides/reasoning_overview.md@0D_base_

```markdown
[BEGIN CONTENT]
# Reasoning overview

This guide orients you across the systems, checkpoints, and metrics that define the reasoning roadmap. Keep it close when
triaging milestones or proposing architectural changes.

## Milestone guardrails

| Milestone | Gate | Acceptance notes |
| --- | --- | --- |
| M0 | Trace coverage ≥95% on curated templates | Validate with `codex metrics summarize --metric reasoning.trace_coverage`. |
| M1 | Curriculum win rate ≥0.55 on `benchmarks/cot-lite` | Run the curriculum smoke in [First principles curricula](first_principles_curricula.md). |
| M2 | Shadow latency p95 ≤700 ms | Capture with `codex deploy --dry-run --latency-report`. |
| M3 | Weekly redeploy cadence with zero manual overrides | Enforced by the deployment checklist in [`templates/`](../templates/README.md). |

Milestones build sequentially: do not advance without closing action items or documenting explicit risk trade-offs in
[`status_updates/`](../status_updates/).

## Systems topology

1. **Authoring** — Hydra defaults stitch reasoning templates from `configs/training/reasoning/` with classical knobs. Updating a
   template requires bumping the manifest digest and notifying deployment partners.
2. **Training** — Training and trace capture are coordinated by the
   unified training stack:
   - `src/codex_ml/training/unified_training.py`
     exposes configuration for curriculum phases, continual replay,
     and resume strategy,
   - `src/codex_ml/train_loop.py`
     executes a single run, attaches the reasoning harness,
     and logs traces / checkpoints.
   When these docs refer to "the trainer", they mean this pair of
[END CONTENT]
```text

### >>> FILE: docs/guides/first_principles_curricula.md@0D_base_

```markdown
[BEGIN CONTENT]
# First principles curricula

Curriculum-first training anchors the reasoning roadmap. This guide walks through how we design, stage, and evaluate
curricula across training, evaluation, and deployment.

## Design principles

1. **Start from the target metric** — Anchor every phase on the milestone gate (for example M1 win rate ≥0.55).
2. **Minimise hidden state** — Curriculum YAML fragments must be diff-friendly; prefer declarative overrides to custom code.
3. **Embed observability** — Each phase should emit trace markers (`phase_id`, `prompt_complexity`) for downstream dashboards.
4. **Document fallback paths** — Capture baselines in [`../status_updates/`](../status_updates/) before experimenting.

## Curriculum blueprint

| Phase | Objective | Dataset preset | Signals |
| --- | --- | --- | --- |
| Warm-up | Stabilise reasoning traces | `datasets/reasoning/warmup.jsonl` | Trace coverage, loss |
| First principles | Teach decomposition heuristics | `datasets/reasoning/first_principles.jsonl` | Win rate, critique density |
| Challenge set | Stress bespoke behaviors | `datasets/reasoning/challenge.jsonl` | Latency deltas, judge disagreement |

Phase definitions live in `configs/training/reasoning/curricula/`. Each YAML file exports:

phase_schedule:
  - id: warmup
    dataset: datasets/reasoning/warmup.jsonl
    steps: 200
  - id: first_principles
    dataset: datasets/reasoning/first_principles.jsonl
    steps: 400
[END CONTENT]
```text

### >>> FILE: docs/deployment/reasoning_pod.md@0D_base_

```markdown
[BEGIN CONTENT]
# Reasoning Pod (Dry-Run Deployment Preset)

## Purpose
The "reasoning pod" describes how a bespoke reasoning agent *would* be
packaged and hosted. It defines resource shape, expected inputs, and
telemetry expectations so that Product, Engineering, and on-call
stakeholders can reason about rollout impact without touching
production infrastructure.

This is explicitly **not** production hosting. It exists for:
- reproducibility review,
- resource sizing review (CPU / memory / GPU),
- telemetry + trace expectations,
- rollout ring declaration.

## Dry-run flow
1. Prepare or select a model bundle:

       artifacts/runs/reasoning-starter:last

2. Execute the dry run:

       codex deploy \
         --config configs/deploy/reasoning_pod.yaml \
         --model artifacts/runs/reasoning-starter:last \
         --dry-run

3. Inspect the generated manifest:
   - `image` / tag are correct for the artifact you intend to ship.
   - resource requests/limits make sense.
   - `CODEX_CURRICULUM_PHASE`, `CODEX_TRACE_MODE`
     (usually `disabled`, occasionally `param-slice` when
[END CONTENT]
```text

### >>> FILE: configs/deploy/reasoning_pod.yaml@0D_base_

```yaml
[BEGIN CONTENT]
# Reasoning pod dry-run deployment preset
# Consumed by `codex deploy --dry-run` to generate a manifest that
# describes how a bespoke reasoning agent *would* be hosted.
#
# This is NOT a production-ready spec. It exists to force review of:
# - resource shape (CPU/memory/GPU),
# - curriculum + trace_mode settings,
# - telemetry expectations,
# - rollout ring intent.
#
# The `--model` argument to `codex deploy` should point at the
# artifact bundle you want evaluated (e.g. artifacts/runs/...:last).

pod:
  name: reasoning-agent-pod
  image: "ghcr.io/your-org/codex-reasoning:LOCAL_DEV_TAG"

  resources:
    cpu_request: "2"
    cpu_limit: "4"
    memory_request: "8Gi"
    memory_limit: "16Gi"
    gpu_request: "0"    # set to "1" if GPU inference is required

  env:
    - name: CODEX_CURRICULUM_PHASE
      value: "starter"
    - name: CODEX_TRACE_MODE
      value: "disabled"        # or "param-slice" once diagnostic traces are enabled
    - name: CODEX_EVAL_PRESET
      value: "configs/evaluation/reasoning/base.yaml"
[END CONTENT]
```text

### >>> FILE: docs/how-to/run_audit_0D_base_.md@0D_base_

```markdown
[BEGIN CONTENT]
# [How-to]: Run the Deterministic Audit on 0D_base_
> Generated: Previous Cycle-10-10 01:27:43 UTC | Author: mbaetiong
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Purpose
- Produce canonical, hash-stamped maturity artifacts (S1–S7) for branch 0D_base_.

Prereqs
- Python 3.10+ environment; install pyyaml and jinja2 for rendering:
  - pip install pyyaml jinja2

Commands
- Full pipeline (S1–S7)
  - python scripts/space_traversal/audit_runner.py run
- Fast path (S1, S3, S4, S6)
  - make space-audit-fast
- Explain a capability's score
  - python scripts/space_traversal/audit_runner.py explain checkpointing
- Diff two runs
  - python scripts/space_traversal/audit_runner.py diff --old <old.json|md> --new <new.json|md>

Outputs (deterministic)
- audit_artifacts/context_index.json (S1)
- audit_artifacts/facets.json (S2)
[END CONTENT]
```text

### >>> FILE: docs/index.md@0D_base_

```markdown
[BEGIN CONTENT]
# Documentation Index

- [Architecture](architecture.md)
- [Formal Artifacts](specs/FORMAL_ARTIFACTS.md) — Specs, prompts, acceptance guides
- [How-to: Offline Tracking Guards](how-to/offline_tracking.md)
- [How-to: Checkpoint Metadata](how-to/checkpoint_metadata.md)
- [How-to: Dataset Manifest](how-to/dataset_manifest.md)
- [How-to: CODEOWNERS Validation](how-to/codeowners_validation.md)
- [How-to: Admin Bootstrap](how-to/admin_bootstrap.md)
- [How-to: Bootstrap Self‑Hosted Runner](how-to/bootstrap_runner.md)
- [Ops: Rulesets vs Protection](ops/repo_rulesets_vs_protection.md)
- [How-to: Run Audit on 0D_base_](how-to/run_audit_0D_base_.md)
  - [Traversal Workflow](Traversal_Workflow.md)
  - [Usage Guide](Usage_Guide.md)
[END CONTENT]
```text

---

## Survey Results

### >>> RESULT: Control surface knobs@0D_base_

```text
[BEGIN CONTENT]
- trace_mode (baseline.yaml top-level): param-slice
- training.reasoning.trace_mode: disabled
- curriculum.preset: starter
- evaluation.preset: base
- deployment.preset: reasoning_pod
- metadata.rollout_ring: 0D_base_
[END CONTENT]
```text

### >>> RESULT: ReasoningTrainer search@0D_base_

```text
[BEGIN CONTENT]
ReasoningTrainer: NOT FOUND in code. References exist in docs/README_ROOT.md and docs/guides/reasoning_overview.md as historical context.
[END CONTENT]
```text

### >>> RESULT: PR #1926 diff availability@PR#1926

```text
[BEGIN CONTENT]
No local checkout or diff artifacts for PR #1926 were found. Unable to surface file changes.
[END CONTENT]
```text

### >>> RESULT: CLI mismatch audit@0D_base_

```text
[BEGIN CONTENT]
Docs (e.g. docs/README_ROOT.md, docs/guides/first_principles_curricula.md) describe `codex deploy --config ... --model ... --dry-run`, but src/codex_ml/cli/codex_cli.py deploy command only accepts `--config`, `--dry-run`, and `--run-metadata-dir` with no `--model` option. Repo-map docs and CLI align: `codex repo-map --reasoning` supports `--include` as documented.
[END CONTENT]
```text

### >>> RESULT: repo ring semantics@0D_base_

```text
[BEGIN CONTENT]
See docs/README.md, docs/README_ROOT.md, docs/how-to/run_audit_0D_base_.md, docs/index.md for rollout ring definitions covering 0A_base_→0D_base_→main.
[END CONTENT]
```text

### >>> RESULT: Reasoning harness trace hook@0D_base_

```text
[BEGIN CONTENT]
See src/codex_ml/models/reasoning.py::_vectorise_model for trace vector fingerprint used when trace_mode is enabled.
[END CONTENT]
```text

### >>> RESULT: Evaluation dependencies summary@0D_base_

```text
[BEGIN CONTENT]
src/codex_ml/eval/evaluator.py enforces optional deps (torch/datasets/transformers) and raises EvaluationDependencyError when missing.
[END CONTENT]
```text

### >>> RESULT: Deployment preset summary@0D_base_

```text
[BEGIN CONTENT]
configs/deploy/reasoning_pod.yaml declares rollout_ring "0D_base_", dry_run_only true, and sets CODEX_TRACE_MODE=disabled, CODEX_CURRICULUM_PHASE=starter, CODEX_EVAL_PRESET=configs/evaluation/reasoning/base.yaml.
[END CONTENT]
```text

### >>> RESULT: Reasoning repo-map summary@0D_base_

```text
[BEGIN CONTENT]
src/codex_ml/cli/repo_map.py surfaces reasoning_status with trace_mode, curriculum.preset, evaluation.preset, metadata.rollout_ring, deployment.rollout_ring.
[END CONTENT]
```text
