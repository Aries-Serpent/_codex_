# Model registry

See [docs/modules/model_registry.md](./modules/model_registry.md) for the full list of supported models and LoRA settings.

## LoRA validation summary
- `dtype` values are validated; unsupported dtypes raise errors (or warnings when strict mode is disabled).
- `device` must be `cpu` or `cuda`.
- Validation occurs before adapters are applied to keep runs deterministic and offline-friendly.
