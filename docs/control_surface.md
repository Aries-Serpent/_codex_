# Control Surface: Internal Alpha Knob Contract

The `_codex_` control surface enumerates the product-facing knobs that
Engineering and Product agree to expose in the ChatGPT-Codex UI. The
same contract will be reused when we graduate to a standalone control
panel.

The scope is intentionally narrow and offline-first—every knob listed
here must be operable without calling external services.

---

## 1. Curriculum Phase / Schedule
**What it controls:** Which curriculum phase or continual-learning
schedule is active for training or replay.

**Where defined now:**
`configs/training/reasoning/curricula/*.yaml` and referenced by
`src/codex_ml/training/unified_training.py` /
`src/codex_ml/training/strategies.py`.

**Intended UI element:** Dropdown of available curricula / phases.

---

## 2. Trace Capture Toggle (`logging.reasoning_trace`)
**What it controls:** Whether the reasoning harness records a
deterministic parameter slice while running. When disabled the harness
skips trace capture entirely.

**Where defined now:**
`logging.reasoning_trace` and the reasoning config block in
`configs/training/reasoning/baseline.yaml`, with capture behavior
implemented in `src/codex_ml/models/reasoning.py`
(`ReasoningHarness.capture_trace`).

**Intended UI element:** Boolean toggle. Include helper text clarifying
that the captured slice is a reproducibility fingerprint, not a semantic
explanation of reasoning.

---

## 3. Evaluation Preset / Gate Run
**What it controls:** Which offline evaluation bundle to execute
(theorem/maths/tool probes) and which NDJSON ledger to emit.

**Where defined now:**
`configs/evaluation/reasoning/*.yaml` and
`src/codex_ml/eval/evaluator.py`.

**Intended UI element:** "Run Evaluation Suite" button that returns
metrics and writes to the ledger.

---

## 4. Deployment Preset (Reasoning Pod Dry-Run)
**What it controls:** Which deployment manifest shape to validate.
Produces a pod spec for inspection, NOT a live rollout.

**Where defined now:**
The dry-run manifest generator in `deploy/deploy_codex_pipeline.py` and
the rollout guidance in `docs/README_ROOT.md` (see "Deployment checks").

**Intended UI element:** "Generate deployment manifest (dry run)"
button that prints the manifest plus warnings.

---

## 5. Continual Replay / Training Strategy
**What it controls:** Whether the unified trainer runs pretrain-only,
staged replay, etc., and how resume points are handled.

**Where defined now:**
`src/codex_ml/training/unified_training.py` and
`src/codex_ml/training/strategies.py`.

**Intended UI element:** Dropdown of strategy presets (read-only if
some presets are experimental).

---

## 6. Rollout Ring / Target Environment
**What it controls:** Declares which ring this artifact is targeting
next in the branch promotion ladder:
`0A_base_` → `0B_base_` → `0C_base_` → `0D_base_` → `main`.

**Where defined now:**
Runbook expectations in `docs/README.md` and release workflows across
`docs/templates/`. These documents set the target ring for each branch
promotion.

**Intended UI element:** Read-only badge, e.g.
"Target ring: 0D_base_ (internal RC). Not production."

---

## Contract
The internal alpha product surface is the set:

```text
AlphaProductSurface = {
  curriculum_phase,
  trace_mode,
  eval_preset,
  deploy_preset,
  replay_strategy,
  rollout_ring
}
```text

Each knob is offline-first and review-gated:

- `curriculum_phase` / `replay_strategy` come from the training configs and
  continual replay logic in
  `src/codex_ml/training/unified_training.py` / `src/codex_ml/training/strategies.py`.
- `trace_mode` is documented as "disabled" by default. When enabled it is a
  diagnostic fingerprint (`param-slice`) and remains offline-only until the
  planned "activation-snapshot" ships.
- `eval_preset` is declared in `configs/evaluation/reasoning/*.yaml` and powers
  offline theorem/tool probes.
- `deploy_preset` is the dry-run manifest (`configs/deploy/reasoning_pod.yaml`)
  rendered via `codex deploy --dry-run` for inspection (never auto-deploy).
- `rollout_ring` is an intent badge in the ladder `0A_base_` → `0B_base_` →
  `0C_base_` → `0D_base_` → `main`. It is not production approval.

Product signoff to merge `0D_base_` → `main` should not happen unless every
knob above is documented, has a safe offline default, and is reflected in
status / rollout notes.
