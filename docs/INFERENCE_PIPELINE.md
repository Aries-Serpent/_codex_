# Deterministic Inference Pipeline (v1.0.0)

This pipeline provides reproducible, offline-only inference for pre-trained models. It is organized into deterministic stages (I1–I4) and produces hashes for inputs, model artifacts, and outputs.

## Usage

```bash
WANDB_MODE=offline \
python scripts/inference_pipeline.py \
  --config .copilot-space/workflow.yaml \
  --input scripts/config/sample_inference_input.json \
  --output audit_artifacts/inference_output.json \
  --manifest audit_artifacts/inference_manifest.json \
  --explain
```

- **Config keys** (`.copilot-space/workflow.yaml`):
  - `inference.model_path`: Local directory or file containing the model/tokenizer.
  - `inference.seed`: Defaults to `42`.
  - `inference.deterministic`: When true, deterministic algorithms are enforced.
  - `inference.max_input_length`: Token truncation limit (default `512`).
  - `inference.preprocessor_override`: Optional `module:function` string to override tokenization.

## Determinism Expectations
- Seeds for `random`, `numpy`, and `torch` are set at each stage.
- Offline mode is required (`WANDB_MODE=offline`); the runner aborts otherwise.
- Hashes include `input_hash`, `model_hash`, and `output_hash`. Re-running with the same inputs produces identical hashes.
- Batch size is pinned to 1 and greedy decoding is used to avoid nondeterministic sampling.

## Outputs
- **Output JSON**: Prediction payload plus `output_hash` and stage timings.
- **Manifest (optional)**: SHA256 hash of the output artifact with pipeline metadata.

## Troubleshooting
- **Missing model path**: Ensure `inference.model_path` exists locally; the pipeline never downloads models.
- **Non-deterministic results**: Verify seeds and that `deterministic` is set to `true` in the config.
- **Plugin interference**: Run tests with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1` to keep the environment minimal.
