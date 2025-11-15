# Plugin Development Guide

This guide explains how to extend `_codex_` with custom datasets, metrics, and
logging sinks using the existing registry patterns.

## Registries at a glance

| Registry | Module | Decorator | Notes |
| --- | --- | --- | --- |
| Datasets | `codex_ml.data.registry` | `@register_dataset` | Exposes JSONL/CSV loaders plus offline fixtures. |
| Metrics | `codex_ml.metrics.registry` | `@register_metric` | Supports numeric and generative metrics (BLEU/ROUGE). |
| Logging | `codex_ml.logging.registry` | `@register_logger` | Builds NDJSON, MLflow, and custom sinks. |

Each registry uses a shared pattern:

```python
from codex_ml.data.registry import register_dataset


@register_dataset("my_dataset")
def load_my_dataset(path: str, *, seed: int = 1234) -> dict[str, list[dict[str, str]]]:
    # Load records and reuse deterministic split helpers
    from codex_ml.data.registry import split_dataset

    records = _read_custom_format(path)
    return split_dataset(records, ratios=(0.8, 0.1, 0.1), seed=seed)
```

## Testing your plugin

1. Write targeted tests under `tests/plugins/` to exercise your loader/metric.
2. Reuse the deterministic helpers imported from the canonical modules to
   avoid duplicating shuffle logic.
3. Run `nox -s tests -- tests/plugins -q` to ensure your plugin passes the
   standard gates.

## Distribution tips

- Provide optional dependencies via extras (e.g. `pip install codex-ml[my_plugin]`).
- Document environment variables or offline assets required by your plugin.
- Update `docs/how-to` or `docs/training` sections with usage instructions when
  shipping new registries.

*Last updated: 2025-11-12*

