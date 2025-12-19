# AGENTS — Scripts

Scope: scripts/**

- `run_local_server.sh` starts the MCP server using the safe run entrypoint.
- `smoke_test_local.sh` performs curl-based smoke checks against `/health` and `/jsonrpc`.
- Keep scripts POSIX-compatible and avoid hard dependencies except common CLI tools.
