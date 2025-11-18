# [Guide]: MCP Usage & Validation

> This guide describes how MCP (Model Context Protocol) capabilities are surfaced and validated in the `_codex_` audit.

## 1. Running MCP-Aware Audit

```bash
# Run full audit with MCP capabilities
python scripts/space_traversal/audit_runner.py run

# Explain specific MCP capabilities
python scripts/space_traversal/audit_runner.py explain mcp-tooling-registry
python scripts/space_traversal/audit_runner.py explain mcp-error-handling
python scripts/space_traversal/audit_runner.py explain mcp-protocol-surface
python scripts/space_traversal/audit_runner.py explain mcp-rate-limiting
python scripts/space_traversal/audit_runner.py explain mcp-authz-authn
```

## 2. MCP Capabilities in the Matrix

The MCP capabilities (mcp-protocol-surface, mcp-tooling-registry, mcp-authz-authn, etc.) appear as rows in the capability matrix with their own scores and evidence counts.

*End of MCP Guide*
