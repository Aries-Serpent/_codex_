# MCP Server (Future-Ready)

This directory contains a skeleton Model Context Protocol (MCP) server that will expose the same capabilities as the Internal
Tools API. Constraints to observe when implementing the full server:

- Copilot coding agents currently support tool invocations only.
- Avoid OAuth for remote MCP access; issue short-lived API keys and reuse the ITA security primitives.
- Mirror the OpenAPI contract to keep Codex, Copilot, and MCP clients aligned.
