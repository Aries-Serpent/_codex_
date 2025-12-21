#!/usr/bin/env bash
set -euo pipefail

curl -sS http://127.0.0.1:8080/health | jq .

curl -sS -X POST http://127.0.0.1:8080/jsonrpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"mcp.listTools","params":{},"id":"1"}' | jq .

curl -sS -X POST http://127.0.0.1:8080/jsonrpc \
  -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","method":"mcp.callTool","params":{"tool_id":"mock.tool.echo","input":{"text":"hello"}},"id":"2"}' | jq .
