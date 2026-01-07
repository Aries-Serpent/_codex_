# Plugin Registry CLI — Developer Notes

## Entrypoints
| Command | Purpose |
|---------|---------|
| codex-list-plugins | Print available plugins (text/json) |

## Behavior Contract
- JSON mode prints to stdout only; stderr remains empty unless an error occurs
- Non-JSON modes Phase 5 print informational messages to stderr

## Testing
- tests/plugins/test_list_plugins_cli_json.py (shape)
- tests/plugins/test_list_plugins_cli_json_stdout_only.py (stderr empty)
- tests/plugins/test_list_plugins_cli_smoke.py (basic smoke)

*End of doc*
