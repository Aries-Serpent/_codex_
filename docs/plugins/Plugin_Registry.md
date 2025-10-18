# Plugin Registry — Programmatic Interfaces

This document captures the canonical programmatic registry surfaces and JSON contracts.

## Programmatic API
| Module | Purpose |
|--------|---------|
| codex_ml.plugins.registry | Discover and enumerate plugins |
| codex_ml.plugins.loader | Resolve and load plugin entrypoints |
| codex_ml.plugins.programmatic | Convenience helpers for in-process queries |

## JSON/CLI Contract
`codex-list-plugins --format json` emits:
- Either an array of plugin names or an object with {names: [...], meta: {...}}
- stdout only (no stderr) on success
- exit code 0

## Examples
```python
from codex_ml.plugins.programmatic import list_plugins
print(list_plugins())  # ["plugin_a", "plugin_b"]
```

*End of doc*
