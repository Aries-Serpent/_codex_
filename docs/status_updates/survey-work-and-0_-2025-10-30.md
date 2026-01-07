# Repo Survey — work & PR 0 — 2025-10-30 (UTC)

**Ref:** branch `work`  commit `63694ea8`  •  **Artifacts:** `docs/status_updates/artifacts/Previous Cycle-10-30-survey-work-and-0_`

---

```yaml
branch: work
pr: 0
rollout_ring: 0D_base_   # intent badge carried forward in templates (docs)
eval_preset: base
deployment_preset: reasoning_pod
generated_utc: 2025-10-30T00:00:00Z
```text

## File Survey: Branch work

### >>> FILE: src/codex_ml/training/unified_training.py@work
text
(brief highlights: deterministic seeding; resume plumbing; continual phases; callback relay)

### >>> FILE: src/codex_ml/train_loop.py@work
text
(checkpoint sha256; config snapshot; retention policy; reasoning harness hooks; telemetry)

### >>> FILE: src/codex_ml/training/strategies.py@work
text
(FunctionalStrategy + ContinualReplayStrategy; callback surface; dataset materializers)

### >>> FILE: src/codex_ml/models/reasoning.py@work
text
(ReasoningHead; ToolUseAdapter; ReasoningHarness; trace modes: disabled|weights|activations)

### >>> FILE: configs/training/reasoning/baseline.yaml@work
text
(control-surface: trace_mode, curriculum preset, evaluation preset, deployment preset, rollout_ring)

### >>> FILE: configs/training/reasoning/curricula/starter.yaml@work
text
(phase_schedule: warmup → first_principles → challenge)

### >>> FILE: configs/evaluation/reasoning/base.yaml@work
text
(datasets: proof_logs, math_word_problems, tool_traces; probes; output paths)

### >>> FILE: src/codex_ml/eval/evaluator.py@work
text
(optional deps; synthetic fallback; hydra/omegaconf env resolvers; probe runner)

### >>> FILE: src/codex_cli/app.py@work
text
(reasoning-templates list/explain; offline helpers; Typer/Click duality)

### >>> FILE: src/codex_ml/cli/codex_cli.py@work
text
(repo_map --reasoning; deploy --dry-run with run_metadata_dir; status-report)

### >>> FILE: docs/*
text
(README_ROOT: roadmap, rings; README: ops pointers; guides: reasoning_overview, curricula; deployment/reasoning_pod.md)

---

## Control Surface (detected)
text

* trace_mode: weights
* curriculum.preset: starter
* evaluation.preset: base
* deployment.preset: reasoning_pod
* metadata.rollout_ring: 0D_base_

## CLI/Docs Mismatch Audit (quick)
text

* Docs sometimes show `codex deploy --model ...`; CLI `deploy` currently expects `--run-metadata-dir` (no `--model` flag).
* Otherwise surfaces align with repo_map/status-report.

## Readiness
```javascript
Let R = α·E + β·T + γ·D with α=0.2, β=0.2, γ=0.6.

* E: 0.0 (no online eval required in this ring; treat as 0.0 unless artifacts exist)
* T: 0.0 (set via latest run artifacts if present; default 0.0)
* D: 0.9 (docs + dry-run parity strong)
  => R = 0.54  → Recommendation: Proceed
```text
---
_Generated with `scripts/survey.sh` • R = α·E + β·T + γ·D (α+β+γ=1)_
