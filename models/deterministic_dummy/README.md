# Deterministic Dummy Model Placeholder

Provide a local, pre-trained model and tokenizer artifacts here for deterministic inference runs.

Suggested contents:
- `config.json` / tokenizer files compatible with `transformers.AutoTokenizer`
- Model weights saved locally (no network fetches)

Update `.copilot-space/workflow.yaml` to point to the actual path if you store the model elsewhere.
