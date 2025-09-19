# Model registry guidelines

The Codex ML model registry provides a thin wrapper around Hugging Face models
to ensure deterministic, offline-friendly loading semantics.

## Tasks and loaders

- Decoder-only language models (`task: "causal"`) are loaded through
  `transformers.AutoModelForCausalLM`.
- Masked-language models (`task: "mlm"`) use `transformers.AutoModelForMaskedLM`.

The bundled `bert-base-uncased` entry is configured for the masked-language
task. Custom registrations should declare the appropriate task to avoid routing
a masked model through the causal loader.

## Offline-first resolution

Model builders look for the following keys in the configuration dictionary, in
order:

1. `local_path` / `path` / `model_path`
2. `pretrained_model_name_or_path`
3. `model_id`

If none are provided, the registration's default identifier is used. The loader
passes `local_files_only=True` by default so that CI runs and air-gapped
environments never attempt to hit the network. To opt in to remote downloads set
`local_files_only=False` explicitly.

`trust_remote_code` is honoured when supplied, allowing advanced users to enable
custom model code on a per-entry basis without changing the global policy.

### Error handling

Missing checkpoints raise a `RuntimeError` with a clear remediation message. To
resolve the error either place the weights under the configured `local_path` or
allow remote downloads by relaxing `local_files_only`.
