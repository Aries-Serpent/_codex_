# AGENTS — MCP (Model Context Protocol)

**Last Updated**: 2025-12-23  
**Scope**: src/mcp/**

---

## 📋 MCP Server Components

This directory contains the MCP server implementation.

---

## 🔒 Security Integration (2025-12-23)

MCP server integrates with security utilities:

```python
from codex.security import mask_token, sanitize_log

# In MCP handlers
@app.post("/endpoint")
async def handler(request: Request):
    # Mask any tokens in logs
    logger.info(f"Request from: {mask_token(request.headers.get('Authorization'))}")

    # Sanitize user input
    user_data = await request.json()
    logger.info(f"Data: {sanitize_log(user_data)}")
```

### Security Features

- ✅ **Request Logging**: All tokens masked automatically
- ✅ **Input Sanitization**: User data sanitized before logging
- ✅ **Secure Storage**: Secrets encrypted at rest
- ✅ **Token Hashing**: API tokens hashed for comparison

---

## 📖 MCP Guidelines

- Use security utilities for all sensitive data
- Sanitize all user-provided input
- Never log plain authentication tokens
- Use SecureStorage for configuration secrets

---

**See**: [Main .codex/archive/deprecated/AGENTS.md](../../../.codex/archive/deprecated/AGENTS.md) | [Security Guidelines](../../../docs/security/SECURITY_GUIDELINES.md) | [MCP Docs](server/README.md)

---

## 📂 Related Module Paths

**Security Module**: `src/codex/security/` - Use in MCP handlers  
**AST Module**: `src/codex/ast/` - Code analysis integration  
**Agent Directory**: `agents/` - Agent implementations  
**Agent Scripts**: `scripts/agent/` - Automation utilities
