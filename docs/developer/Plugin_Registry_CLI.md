# Plugin Registry CLI — stdout/stderr contract

## Contract
- **stdout**: reserved for final data output (`--format text` or `--format json`).
- **stderr**: logging/diagnostics only. JSON mode suppresses info-level logs.

## Examples
```bash
# Machine-readable output (stdout only)
python -m codex_ml.cli.list_plugins --format json > plugins.json

# Names-only (deterministic `(none)` marker when empty)
python -m codex_ml.cli.list_plugins --names-only --format text

# Skip discovery to avoid entry-point scans
python -m codex_ml.cli.list_plugins --no-discover --format json
```

## JSON schema
```json
{
  "programmatic": { "discovered": 0, "names": ["..."] },
  "legacy": {
    "tokenizers": ["..."],
    "models": ["..."],
    "datasets": ["..."],
    "metrics": ["..."],
    "trainers": ["..."],
    "reward_models": ["..."],
    "rl_agents": ["..."]
  },
  "options": { "discover": true, "names_only": false, "format": "json" }
}
```

*End*
