# Reasoning adapters and trace logging

Codex ML now ships structured configuration for reasoning-centric runs. The schemas live in
`codex_ml.config` as `ReasoningConfig`, `ReasoningHeadConfig`, `ReasoningObjectiveConfig`, and
`ToolAdapterConfig`. Hydra presets in `configs/training/reasoning/` compose these dataclasses with the
existing training profiles so you can enable chain-of-thought supervision or tool-use adapters without
hand editing Python.

## Quick starts

### Chain-of-thought supervision

```bash
python -m codex_ml.cli.train \
  training=base \
  training.reasoning=@configs/training/reasoning/chain_of_thought.yaml \
  artifacts.dir=artifacts/cot_run
```text

This preset activates the `ReasoningHeadConfig` defaults for a 768-d projection head, stores traces in
`artifacts/cot_run/cot_traces.ndjson`, and logs per-step reasoning summaries to
`artifacts/cot_run/reasoning_traces.json` while emitting telemetry events.

### Tool-execution adapters

```bash
python -m codex_ml.cli.train \
  training=base \
  training.reasoning=@configs/training/reasoning/tool_execution.yaml \
  artifacts.dir=artifacts/tool_run
```text

The tool-execution preset enables the `ToolAdapterConfig` so each optimisation step records the
highest-probability tool, temperature-scaled confidence, and the full probability distribution. These
records are appended to `metrics.ndjson` as `reasoning_trace` events and saved alongside your model
checkpoints.

## Continual or unified workflows

Reasoning presets are additive: layer them on top of `configs/training/continual/rehearsal.yaml` or any
`training.profiles/*` selection. The dataclasses ensure validation—Hydra will surface configuration
mistakes (such as missing tool names) before the trainer starts.

## What gets logged

* `metrics.ndjson` receives a `reasoning_trace` record per captured step.
* `reasoning_traces.json` mirrors the most recent history from the `ReasoningHarness` deque.
* Optional NDJSON sinks use the `trace_store` value from the objective (defaulting to
  `reasoning_traces.ndjson`).

The runtime also annotates `environment.json` with the active reasoning mode, top-k depth, and any
probability thresholds applied.
