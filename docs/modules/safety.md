# Safety

The safety module provides simple content filters.

## Data Loading Integration

`stream_paths` from `codex_ml.data.loaders` applies `SafetyFilters` when `cfg.data.safety_filter_enabled` is true.
Redacted phrases are replaced with `{REDACTED}` and the original text is logged via `log_error`.
