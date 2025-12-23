# AGENTS — Prompts

**Last Updated**: 2025-12-23  
**Scope**: prompts/**

---

## 📋 Prompt Templates

This directory contains prompt templates and task templates for agents.

---

## 🔒 Security Guidelines for Prompts

When creating prompts that handle sensitive data:

```python
from codex.security import mask_sensitive, sanitize_log

# Mask any credentials in prompts
prompt = f"Process data with key: {mask_sensitive(api_key)}"

# Sanitize user-provided prompt content
user_prompt = sanitize_log(user_input)
```

---

## 📖 Best Practices

- Never include actual secrets in prompt templates
- Use placeholder values like `<API_KEY>` or `${SECRET}`
- Document required environment variables
- Test prompts with security utilities

---

**See**: [Main AGENTS.md](../AGENTS.md) | [Security Guidelines](../docs/security/SECURITY_GUIDELINES.md)
