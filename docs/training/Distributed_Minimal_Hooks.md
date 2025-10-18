# Distributed Minimal Hooks — Behavior & Expectations

This repository includes minimal distributed hooks intended to be environment-gated and no-op in unsupported contexts.

## Principles
- No-op unless explicitly enabled via environment flags
- Fallback to single-process semantics gracefully
- Clear error messages on incompatible configurations

## Environment Flags
| Variable | Effect |
|----------|--------|
| CODEX_DDP=1 | Opt-in to distributed hooks where available |
| WORLD_SIZE | Used to determine multi-rank runs |
| RANK, LOCAL_RANK | Passed through to initialize process group |

## Behavior
- If CODEX_DDP is unset or 0, training proceeds as single-process
- CODEX_DDP_ENABLE remains accepted as a legacy alias for CODEX_DDP
- Any initialization errors are caught and surfaced as runtime warnings with guidance
- Hooks avoid altering random seeds unless explicitly instructed

## Verification
Run:
```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q tests/distributed
```
Expected: no-op + env opt-in tests pass unchanged.

*End of doc*
