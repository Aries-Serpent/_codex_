# Metric Plugin Duplicate Resolution Summary
> Generated: 2025-11-12 06:54:52 UTC | Author: mbaetiong

## Duplicates Detected
exact_match, f1, ppl, token_accuracy

## Active Policy
prefer_local (default)

## Resolution Outcomes
| Metric | Policy | Local Retained | Plugin Retained | Alias Created | Notes |
|--------|--------|----------------|-----------------|---------------|-------|
| exact_match | prefer_local | ✅ | ❌ | ❌ | Suppressed plugin re-reg |
| f1 | prefer_local | ✅ | ❌ | ❌ | Suppressed plugin re-reg |
| ppl | prefer_local | ✅ | ❌ | ❌ | Suppressed plugin re-reg |
| token_accuracy | prefer_local | ✅ | ❌ | ❌ | Suppressed plugin re-reg |

Switch policy to override:
```bash
export CODEX_METRIC_PLUGIN_POLICY=prefer_plugin
```text

— End
