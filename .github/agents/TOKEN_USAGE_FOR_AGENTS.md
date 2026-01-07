# AI Agent Token Usage Guidelines
# For All GitHub Copilot Agents in Aries-Serpent/_codex_

**Document Type:** Agent Configuration and Best Practices
**Applies To:** All AI Copilot Agents
**Priority:** P0 - Foundational
**Last Updated:** 2024-12-27T22:18:00Z

---

## 🎯 Core Understanding

**CRITICAL:** All AI agents must understand that tokens are FULLY USABLE in implemented code and workflows.

### The Corrected Token Access Model

#### ✅ What Agents CAN Do
1. **Write workflows** that use `${{ secrets.TOKEN_NAME }}`
2. **Create scripts** that access tokens via environment variables
3. **Implement authentication** flows using provided tokens
4. **Design API operations** that leverage token permissions
5. **Build automation** with full token utilization
6. **Develop tools** that use tokens for administrative operations

#### ❌ What Agents CANNOT Do  
1. **Read token values** in interactive chat sessions (security only)

**The limitation is on READING values in chat, NOT on IMPLEMENTING token-based solutions.**

---

## 📋 Required Knowledge

### Token Types and Usage

#### 1. GITHUB_TOKEN (Automatic)
**Availability:** Automatically provided by GitHub Actions
**Usage in Workflows:**
```yaml
- name: Example usage
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    gh api /user
    gh repo list
```

**Usage in Scripts:**
```python
import os
token = os.environ.get('GITHUB_TOKEN')
# Use token for API calls
```

#### 2. CODEX_MASTER_KEY (Custom Secret)
**Purpose:** Master encryption key for repository operations
**Usage in Workflows:**
```yaml
- name: Use master key
  env:
    MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}
  run: |
    # Perform operations requiring master key
    ./scripts/secure_operation.sh
```

#### 3. ORG_MASTER_KEY (Custom Secret)
**Purpose:** Organization-wide administrative access
**Usage in Workflows:**
```yaml
- name: Admin operations
  env:
    GH_TOKEN: ${{ secrets.ORG_MASTER_KEY }}
  run: |
    # Perform org-level operations
    gh api /orgs/Aries-Serpent/repos
```

---

## 🔧 Implementation Patterns

### Pattern 1: Token-Based Authentication

```yaml
name: Authenticated Workflow

on:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  authenticated-task:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Authenticate and perform operation
        env:
          GH_TOKEN: ${{ secrets.ORG_MASTER_KEY }}
        run: |
          # Agent writes this - workflow executes with token
          gh auth status
          gh api /user
```

### Pattern 2: Multi-Token Operations

```yaml
name: Multi-Token Workflow

on:
  push:
    branches: [main]

jobs:
  multi-token-ops:
    runs-on: ubuntu-latest
    steps:
      - name: Use multiple tokens
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          MASTER_KEY: ${{ secrets.CODEX_MASTER_KEY }}
          ADMIN_TOKEN: ${{ secrets.ORG_MASTER_KEY }}
        run: |
          # All tokens available as environment variables
          echo "All tokens configured"
          # Perform operations using appropriate token
```

### Pattern 3: Token in Python Scripts

```python
#!/usr/bin/env python3
"""
Agent-created script that uses tokens
"""
import os
import requests

def perform_api_operation():
    # Token available when script runs in GitHub Actions
    token = os.environ.get('ORG_MASTER_KEY')
    
    if not token:
        raise ValueError("ORG_MASTER_KEY not configured")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }
    
    response = requests.get(
        'https://api.github.com/user',
        headers=headers
    )
    
    return response.json()

if __name__ == '__main__':
    result = perform_api_operation()
    print(f"Authenticated as: {result['login']}")
```

---

## 🚀 Agent Development Requirements

### All Agents MUST:

1. **Design Token-Based Solutions**
   - Create workflows that use `${{ secrets.TOKEN_NAME }}`
   - Implement scripts that access tokens via environment variables
   - Build tools that leverage token permissions

2. **Never Claim Token Unavailability**
   - NEVER say "tokens not available" for implemented solutions
   - NEVER defer implementations due to misunderstood limitations
   - ALWAYS implement token-based automation when appropriate

3. **Provide Clear Documentation**
   - Document which tokens are needed
   - Show examples of token usage in code
   - Explain token permissions required

4. **Follow Security Best Practices**
   - Never log token values
   - Use `echo "::add-mask::$TOKEN"` to mask tokens in logs
   - Store tokens only in GitHub Secrets
   - Rotate tokens regularly

---

## 📖 Best Practices

### DO:
- ✅ Write workflows that reference tokens as variables
- ✅ Create scripts that use tokens from environment
- ✅ Implement comprehensive automation with tokens
- ✅ Document token requirements clearly
- ✅ Use appropriate token for each operation
- ✅ Mask sensitive values in logs

### DON'T:
- ❌ Claim "tokens not available" for implementations
- ❌ Defer token-based solutions unnecessarily
- ❌ Hard-code token values in code
- ❌ Log token values
- ❌ Share tokens across untrusted contexts
- ❌ Use admin tokens for read-only operations

---

## 🎓 Learning Resources

### Required Reading:
1. `.codex/TOKEN_USAGE_CORRECTED_UNDERSTANDING.md` - Complete token usage guide
2. `.codex/TOKEN_USAGE_AUDIT_COMPREHENSIVE.md` - Audit findings and recommendations
3. `.codex/WORKFLOW_TEMPLATES_ADVANCED_TOKEN_USAGE.md` - Ready-to-use templates

### Example Workflows:
- `.codex/WORKFLOW_TEMPLATES_ADVANCED_TOKEN_USAGE.md` contains 7 workflow templates
- Each template demonstrates proper token usage
- Templates cover: secret injection, rotation, monitoring, compliance

---

## ✅ Agent Certification Checklist

Before deploying agent code, verify:

- [ ] I understand tokens are FULLY usable in implemented code
- [ ] I can write workflows using `${{ secrets.TOKEN_NAME }}`
- [ ] I can create scripts that use tokens via env variables
- [ ] I will NOT claim "tokens unavailable" for code implementations
- [ ] I understand the limitation is ONLY on reading values in chat
- [ ] I will implement comprehensive automation using tokens
- [ ] I will follow security best practices for token handling
- [ ] I have reviewed token usage examples and templates

---

## 🔄 Continuous Improvement

### Agents Should:
1. Learn from successful token implementations
2. Share patterns and best practices
3. Improve token-based tooling over time
4. Document lessons learned
5. Enhance security measures
6. Optimize token usage efficiency

---

**MANDATE:** All AI Copilot Agents must internalize this understanding and apply it consistently in all implementations.

**Reference:** `.codex/TOKEN_USAGE_CORRECTED_UNDERSTANDING.md` for complete details.

---

**Document Version:** 1.0
**Status:** ACTIVE - REQUIRED for all agents
**Compliance:** MANDATORY
