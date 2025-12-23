# AGENTS — Scripts

**Last Updated**: 2025-12-23  
**Scope**: scripts/**

---

## 📋 Script Categories

### Core Scripts
- `run_local_server.sh` - Start MCP server using safe run entrypoint
- `smoke_test_local.sh` - curl-based smoke checks against `/health` and `/jsonrpc`

### Agent Scripts (`agent/`)
- Agent automation and brain activation scripts

### Security Scripts (🆕 2025-12-23)
- `check_documentation_updates.py` - Systematic documentation verification

---

## 🔒 Security Utilities for Scripts

Scripts can use unified security module:

```python
from codex.security import mask_token, sanitize_log
from codex.security.storage import SecureStorage

# Mask secrets in logs
logger.info(f"Token: {mask_token(api_key)}")

# Sanitize user input
logger.info(f"Input: {sanitize_log(user_data)}")
```

---

## 📖 Guidelines

- Keep scripts POSIX-compatible
- Avoid hard dependencies except common CLI tools
- Use security utilities for sensitive data
- Document all scripts with usage examples

---

**See**: [Main AGENTS.md](../AGENTS.md) | [Security Guidelines](../docs/security/SECURITY_GUIDELINES.md)
