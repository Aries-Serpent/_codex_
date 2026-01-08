# Planset 05: Token Security Neutralization

**Planset ID:** PS-05  
**Priority:** P0 - Critical (Security)  
**Phase:** Pre-commit Cycle 1  
**Status:** 📋 Planned  
**Dependencies:** None  
**Cognitive Brain Objective:** Eliminate token exposure risks, implement safe verification

---

## Context

**Problem:** `scripts/security/copilot_token_decoder.py` decodes and logs raw secrets
- Token leak risk
- Credential exposure in logs
- Violates security best practices

**Security Risk:** CRITICAL - Potential credential compromise

**Solution:** Move decoder to manual extraction area, create scope verification tool

---

## Implementation Plan

### Pre-commit Cycle 1: Secure Token Handling

**Goal:** Neutralize dangerous tooling, implement safe verification

**Tasks:**
- [ ] Move `scripts/security/copilot_token_decoder.py` to `misc/manual_tools/`
- [ ] Add security warning to file header
- [ ] Create `scripts/security/verify_token_scope.py`
- [ ] Implement scope verification via GitHub API
- [ ] Use `x-oauth-scopes` header inspection
- [ ] Zero token logging or decoding
- [ ] Comprehensive security testing

**Files to Move:**
- `scripts/security/copilot_token_decoder.py` → `misc/manual_tools/token_decoder.py`

**Files to Create:**
- `scripts/security/verify_token_scope.py` (~150 lines)
- `tests/test_token_verification.py` (~200 lines)

**Verification Implementation:**
```python
import requests
import os

def verify_token_scopes() -> dict:
    """
    Verify GitHub token scopes WITHOUT decoding token.
    
    Returns:
        dict: Scope verification results
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        return {"error": "GITHUB_TOKEN not set"}
    
    # Make authenticated request
    response = requests.get(
        "https://api.github.com/user",
        headers={
            "Authorization": f"******",
            "Accept": "application/vnd.github.v3+json"
        },
        timeout=10
    )
    
    # Extract scopes from header (NO token decoding)
    scopes = response.headers.get("x-oauth-scopes", "").split(", ")
    
    return {
        "scopes": scopes,
        "has_repo": "repo" in scopes,
        "has_read_org": "read:org" in scopes,
        "status": "valid" if response.status_code == 200 else "invalid"
    }
```

**Success Criteria:**
- [ ] Decoder moved to manual area
- [ ] Scope verifier working
- [ ] Zero token exposure
- [ ] Security audit passing

---

## Security Requirements

### Token Handling Rules

1. **NEVER log tokens**
2. **NEVER decode tokens programmatically**
3. **NEVER store tokens in files**
4. **ALWAYS use environment variables**
5. **ALWAYS verify via API, not decoding**

### Verification vs. Decoding

**❌ WRONG (Decoder):**
```python
decoded = base64.decode(token)  # Exposes secret
print(decoded)  # Logs secret
```

**✅ CORRECT (Verifier):**
```python
response = requests.get(API_URL, headers={"Authorization": f"token {token}"})
scopes = response.headers.get("x-oauth-scopes")  # No decoding
```

---

## Success Metrics

- **Token Exposure Risk:** 0% (eliminated)
- **Security Score:** 10/10
- **Audit Trail:** Complete
- **Compliance:** 100%

---

## Cognitive Brain Integration

**Patterns Learned:**
1. Safe token verification patterns
2. Security-first tool design
3. GitHub API scope inspection
4. Zero-exposure authentication

**Reusable Utilities:**
1. `verify_token_scope.py` - Safe token verifier
2. Security testing patterns
3. Audit logging for auth operations

---

**Created:** 2026-01-08  
**Agent:** GitHub Copilot (PR #2750)
