# AGENTS — _codex_ Internal

**Last Updated**: 2024-12-23  
**Scope**: _codex_/**

---

## 📋 Internal Codex Structures

This directory contains internal codex structures and utilities.

For complete repository guidance, see the main AGENTS.md file in the repository root.

---

## 🔒 Security Module (2024-12-23)

The repository now includes comprehensive security utilities:

```python
from codex.security import mask_token, sanitize_log, hash_secure
from codex.security.storage import SecureStorage

# All security functions documented in main AGENTS.md
```

**Performance**: All functions <0.01ms, suitable for high-throughput use.

---

**See**: [Main AGENTS.md](../AGENTS.md) - Complete repository guidance

---

## 📂 Repository Module Paths

**Security Module**: `src/codex/security/` - Security utilities  
**AST Module**: `src/codex/ast/` - Syntax tree analysis  
**Agent Directory**: `agents/` - Agent implementations  
**Agent Scripts**: `scripts/agent/` - Automation scripts

