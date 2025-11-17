# Metrics Plugin Conflict Resolution Guide
> Generated: 2025-11-12 06:54:52 UTC | Author: mbaetiong

## Overview
Plugin-discovered metrics (entry points) may duplicate locally registered metrics. A policy-based resolver prevents repeated error logs and provides explicit control over precedence.

## Policy Table

| Policy | Behavior | Local Retained | Plugin Retained | Additional Registration | Raises Error |
|--------|----------|----------------|-----------------|-------------------------|--------------|
| prefer_local (default) | Suppress plugin | ✅ | ❌ | None | ❌ |
| prefer_plugin | Override with plugin | ❌ (replaced) | ✅ | None | ❌ |
| alias_plugin | Keep both | ✅ | ✅ (as alias) | plugin:<name> | ❌ |
| shadow_warn | Keep local; warn | ✅ | ❌ | None | ❌ |
| error | Strict legacy behavior | Depends | Depends | None | ✅ |

## Configuration Sources
1. Environment variable: `CODEX_METRIC_PLUGIN_POLICY`
2. Config file: `configs/metrics_plugin_policy.toml`

Environment variable overrides file configuration.

## Example (Environment Override)
```bash
export CODEX_METRIC_PLUGIN_POLICY=prefer_plugin
python -m codex_ml.eval.run ...
```text

## Example (Config File)
```toml
# configs/metrics_plugin_policy.toml
policy = "alias_plugin"
```text

## Alias Naming
When `alias_plugin` is active, plugin metrics register under:
```text
plugin:<original_name>
```text
Lookup of the original name returns the local implementation; alias invokes plugin version.

## Logging
Resolutions are appended to daily error report as structured entries:
- Step: `metric-plugin.conflict-resolution`
- Context includes `policy` and retained implementation details.

## Testing
Run policy tests:
```bash
pytest -k plugin_policy
```text

## Best Practices
| Scenario | Recommended Policy |
|----------|--------------------|
| Stable local metrics; experimental plugins | prefer_local |
| Rapid plugin iteration; replace local code | prefer_plugin |
| Comparative benchmarking | alias_plugin |
| Visibility without override | shadow_warn |
| Enforce uniqueness | error |

## Rollback
To restore strict behavior:
```bash
export CODEX_METRIC_PLUGIN_POLICY=error
```text
Or remove config file and unset environment variable.

— End
