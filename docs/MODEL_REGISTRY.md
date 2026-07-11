# Model registry
**Last Updated:** 2026-07-11
**Version:** v0.2.1

**Last Updated: 2026-06-22

See [docs/modules/model_registry.md](./modules/model_registry.md) for the full list of supported models and LoRA settings.

## LoRA validation summary
- `dtype` values are validated; unsupported dtypes raise errors (or warnings when strict mode is disabled).
- `device` must be `cpu` or `cuda`.
- Validation occurs before adapters are applied to keep runs deterministic and offline-friendly.
