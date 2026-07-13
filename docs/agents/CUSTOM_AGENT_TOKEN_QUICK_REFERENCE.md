# CUSTOM_AGENT_TOKEN_QUICK_REFERENCE.md
**Version:** v0.2.1

**Quick Reference Guide for Token Requirements in 13 Level-1 Custom Agents**

**Document Version**: 1.0.0
**Date**: 2026-06-29
**Target Audience**: Agent Developers, Platform Engineers, Security Engineers

---

##  Quick Lookup Table

All 13 Level-1 agents at a glance:

| # | Agent Name | Token Level | Primary Scopes | Fallback? | Status |
|---|---|---|---|---|---|
| 1 | **ci-emergency-response-agent** | Level 3 | repo, workflow, actions:write |  NO |  Active |
| 2 | **security-alert-verification-agent** | Level 2 | repo, security_events, actions:read_self |  YES |  Active |
| 3 | **codeql-alert-resolution-agent** | Level 2 | repo, security_events, contents:write |  YES |  Active |
| 4 | **secret-detection-agent** | Level 2 | repo, security_events, contents:write |  YES |  Active |
| 5 | **dependency-vulnerability-scanner** | Level 2 | repo, contents:read |  YES |  Active |
| 6 | **ci-auto-healer-agent** | Level 2 | repo, workflow, contents:write |  YES |  Active |
| 7 | **workflow-compliance-guardian** | Level 2 | repo, workflow, actions:write |  YES |  Active |
| 8 | **branch-divergence-resolution-agent** | Level 2 | repo, contents:write, pull_requests |  YES |  Active |
| 9 | **self-healing-orchestrator-agent** | Level 3 | repo, workflow, actions:write |  NO |  Active |
| 10 | **ci-parameter-mismatch-healer** | Level 2 | repo, workflow, contents:write |  YES |  Active |
| 11 | **ci-importerror-agent** | Level 2 | repo, contents:write, actions:read_self |  YES |  Active |
| 12 | **unified-security-scanner** | Level 2 | repo, security_events, contents:read |  YES |  Active |
| 13 | **mypy-manager-agent** | Level 2 | repo, contents:write, actions:read_self |  YES |  Active |

---

##  Pattern Library: 4 Common Implementation Patterns

### Pattern A: Level 3 (No Fallback) - Emergency Operations

**Used by**: ci-emergency-response-agent, self-healing-orchestrator-agent

**When to Use**: Operations that MUST fail safely if CODEX_MASTER_KEY unavailable

```python
from scripts.ci._token_resolver import get_token, validate_scope

class EmergencyAgent:
    def __init__(self):
        # MUST use Level 3 - NO FALLBACK
        self.token = get_token(required_elevated=True, require_level=3)
        
        if not self.token:
            logger.critical("CODEX_MASTER_KEY unavailable - agent cannot operate")
            raise RuntimeError("Emergency operations require Level 3 token")
        
        validate_scope(self.token, ['repo', 'workflow', 'actions:write'])
```

**Characteristics**:
- No fallback to lower token levels
- Must raise exception if token unavailable
- Suitable for high-privilege operations
- Used in emergency/critical scenarios

---

### Pattern B: Level 2 with Safe Fallback

**Used by**: 11 other agents (security, CI healing, etc.)

**When to Use**: Operations that can work with lower privileges but prefer elevated access

```python
from scripts.ci._token_resolver import get_token, validate_scope

class HealerAgent:
    def __init__(self):
        # Try Level 2 first
        self.token = get_token(required_elevated=True)
        
        if not self.token:
            # Fallback to Level 1 if elevated unavailable
            logger.warning("Level 2 token unavailable, using standard token")
            self.token = get_token(required_elevated=False)
        
        # Validate available scopes
        required_scopes = ['repo', 'contents:write']
        try:
            validate_scope(self.token, required_scopes)
        except InsufficientScopeError:
            logger.error("Token has insufficient scopes")
            raise
```

**Characteristics**:
- Attempts Level 2 (CODEX_BACKUP_TOKEN) first
- Falls back to Level 1 (GITHUB_TOKEN) if needed
- Validates scopes for available token
- Suitable for most automated operations

---

### Pattern C: Multiple Scopes with Validation

**Used by**: Agents requiring multiple scope types (security + repo operations)

**When to Use**: Operations requiring multiple independent scope categories

```python
from scripts.ci._token_resolver import get_token, validate_scope

class SecurityScannerAgent:
    def __init__(self):
        self.token = get_token(required_elevated=True)
        
        if not self.token:
            raise RuntimeError("Security scanning requires elevated token")
        
        # Validate multiple scope categories
        required_scopes = [
            'repo',                # Repository access
            'security_events',     # Security scanning
            'contents:read'        # Read source files
        ]
        
        validate_scope(self.token, required_scopes)
        
        self.logger = logging.getLogger(__name__)
    
    def scan_repository(self, repo):
        """Execute comprehensive security scan."""
        try:
            # Multiple API calls with different scopes
            alerts = self.get_codeql_alerts(repo)
            secrets = self.get_secret_alerts(repo)
            return self.aggregate_results(alerts, secrets)
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.error("Insufficient scope for scanning")
            raise
```

**Characteristics**:
- Validates multiple scopes upfront
- Handles operations requiring different permissions
- Comprehensive error reporting
- Suitable for multi-faceted operations

---

### Pattern D: Hidden Script Integration

**Used by**: Agents storing security-sensitive patterns (secret-detection, self-healing)

**When to Use**: Operations involving sensitive algorithms or security patterns

```python
from scripts.ci._token_resolver import get_token
from scripts.ci._hidden_scripts import execute_hidden_script, retrieve_hidden_script

class SecretDetectionAgent:
    def __init__(self):
        self.token = get_token(required_elevated=True)
        if not self.token:
            raise RuntimeError("Secret detection requires elevated token")
    
    def detect_and_remediate(self, repo):
        """Execute stored detection pattern."""
        
        # Retrieve pattern from secure storage
        pattern = retrieve_hidden_script(
            script_id="secret_detection_v2",
            version="latest"
        )
        
        # Execute in sandbox
        result = execute_hidden_script(
            script_id=pattern.id,
            environment={
                "GITHUB_TOKEN": self.token,
                "REPO": repo,
                "DETECT_MODE": "aggressive"
            },
            timeout_ms=120000,
            audit_log=True  # Emit audit trail
        )
        
        # Log result (metadata only, no secrets)
        self.logger.info(
            "secret_scan_complete",
            extra={
                "repo": repo,
                "found": result.get("secret_count", 0),
                "remediated": result.get("remediated_count", 0)
            }
        )
        
        return result
```

**Characteristics**:
- Retrieves patterns from encrypted storage
- Executes in sandboxed environment
- Prevents exposure of sensitive algorithms
- Includes audit logging
- Validates checksum before execution

---

## 🐛 Common Errors & Solutions

### Error 1: "403 Forbidden - Insufficient Scope"

**Symptoms**:
```
HTTPError: 403 Forbidden
{"message": "Must have admin rights to Repository."}
```

**Root Causes**:
- Using GITHUB_TOKEN for operation requiring elevated scope
- Token doesn't have required scope
- Org-level operation on repo token

**Solution**:
```python
#  Fix: Use get_token(required_elevated=True)
token = get_token(required_elevated=True)
validate_scope(token, ['repo', 'workflow'])

# Handle if elevated unavailable
if not token:
    logger.error("Scope requires elevated token - cannot continue")
    raise RuntimeError("Elevated token required")
```

**Prevention**:
- Always validate scopes upfront: `validate_scope(token, required_scopes)`
- Use elevated token for operations requiring it
- Check agent requirements in AGENT_REGISTRY.yaml

---

### Error 2: "401 Unauthorized - Invalid Token"

**Symptoms**:
```
HTTPError: 401 Unauthorized
{"message": "Bad credentials"}
```

**Root Causes**:
- Token expired or revoked
- Token not found in environment
- Token malformed or corrupted

**Solution**:
```python
try:
    token = get_token(required_elevated=True)
    if not token:
        raise RuntimeError("Token not found")
except TokenNotFoundError:
    logger.critical("CODEX_MASTER_KEY not available in environment")
    raise RuntimeError("Token retrieval failed")

# Verify token is valid
headers = {"Authorization": f"token {token}"}
try:
    response = requests.get("https://api.github.com/user", headers=headers)
    response.raise_for_status()
except requests.HTTPError as e:
    if e.response.status_code == 401:
        logger.error("Token invalid or expired")
    raise
```

**Prevention**:
- Check token is properly loaded: `get_token()` should not return None
- Rotate tokens regularly per `TOKEN_HIERARCHY_GUIDE.md`
- Monitor token expiration (if applicable)

---

### Error 3: "429 Too Many Requests - Rate Limit Exceeded"

**Symptoms**:
```
HTTPError: 429 Too Many Requests
{"message": "API rate limit exceeded"}
```

**Root Causes**:
- Too many requests in short time
- Batch operation without rate limit handling
- Concurrent operations exceeding limits

**Solution**:
```python
import time
import requests

def api_call_with_retry(url, token, max_retries=3):
    """Make API call with rate limit backoff."""
    headers = {"Authorization": f"token {token}"}
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 429:
                # Extract wait time from headers
                retry_after = int(e.response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited, waiting {retry_after}s")
                time.sleep(retry_after)
                continue
            raise
    
    raise RuntimeError(f"Max retries exceeded for {url}")
```

**Prevention**:
- Implement rate limit backoff (wait and retry)
- Use elevated tokens for higher rate limits
- Batch operations efficiently
- Monitor API usage

---

### Error 4: "Invalid Checksum on Hidden Script"

**Symptoms**:
```
ValueError: Checksum validation failed for script_id=pattern_detection_v2
Expected: abc123def456..., Got: xyz789uvw456...
```

**Root Causes**:
- Script file corrupted
- Script version mismatch
- Hidden script database out of sync

**Solution**:
```python
from scripts.ci._hidden_scripts import execute_hidden_script, retrieve_hidden_script

try:
    pattern = retrieve_hidden_script(
        script_id="pattern_detection",
        version="latest"
    )
except ChecksumError as e:
    logger.error(f"Script integrity check failed: {e}")
    # Fallback to explicit version
    pattern = retrieve_hidden_script(
        script_id="pattern_detection",
        version="2.1.0"  # Use known good version
    )

result = execute_hidden_script(
    script_id=pattern.id,
    environment={...},
    validate_checksum=True  # Validate before execute
)
```

**Prevention**:
- Verify script checksums after updates
- Use pinned versions instead of "latest"
- Monitor script database for corruption
- Maintain backup of critical scripts

---

### Error 5: "Insufficient Scope: security_events"

**Symptoms**:
```
SecurityError: Token does not have 'security_events' scope
Scopes available: ['repo', 'contents:read']
```

**Root Causes**:
- Agent security operation using standard token
- CODEX_BACKUP_TOKEN missing security scope
- Token not properly configured

**Solution**:
```python
# Get token with explicit scope requirements
token = get_token(
    required_elevated=True,
    required_scopes=['repo', 'security_events']
)

if not token:
    # Try alternative approach with reduced scope
    logger.warning("Security scope unavailable - limited functionality")
    token = get_token(required_elevated=False)
    
    if not token:
        raise RuntimeError("Unable to acquire token with required scopes")

# Validate before proceeding
validate_scope(token, ['security_events'])
```

**Prevention**:
- Check agent's `scopes_required` in AGENT_REGISTRY.yaml
- Ensure CODEX_BACKUP_TOKEN has all required scopes
- Validate scopes upfront, fail fast

---

### Error 6: "Agent Cannot Operate Without Level 3 Token"

**Symptoms**:
```
RuntimeError: Agent requires Level 3 token
```

**Root Causes**:
- CODEX_MASTER_KEY not available
- Agent is emergency-only (no fallback)
- Token rotation in progress

**Solution**:
```python
# For Emergency agents (no fallback)
try:
    token = get_token(required_elevated=True, require_level=3)
    if not token:
        raise RuntimeError("CODEX_MASTER_KEY required")
except Exception:
    logger.critical("Emergency agent disabled - CODEX_MASTER_KEY unavailable")
    # Alert human operator
    emit_alert("EMERGENCY_AGENT_DISABLED", severity="critical")
    raise

# For Non-Emergency agents (with fallback)
token = get_token(required_elevated=True)
if not token:
    logger.warning("Elevated token unavailable, degrading to standard")
    token = get_token(required_elevated=False)
```

**Prevention**:
- Monitor token availability
- Implement operator notification for emergency agents
- Maintain token rotation schedule
- Keep fallback tokens available

---

##  Testing Checklist for Agent Developers

Use this checklist when implementing or updating an agent:

- [ ] **Token Requirement in Prompt**
  - [ ] Agent .md file specifies token level (Level 1/2/3)
  - [ ] Rationale documented for token choice
  - [ ] Scope requirements listed explicitly

- [ ] **Scope Validation Called**
  - [ ] `validate_scope(token, required_scopes)` called after token acquisition
  - [ ] Scopes match requirements in AGENT_REGISTRY.yaml
  - [ ] Error handling for insufficient scope

- [ ] **No Fallback for Level 3**
  - [ ] Emergency agents (Level 3) raise exception if token unavailable
  - [ ] No attempt to continue with lower token level
  - [ ] Clear error message for operator

- [ ] **Error Handling for "Insufficient Scope"**
  - [ ] 403 errors caught and handled gracefully
  - [ ] Operation escalated or failed safely
  - [ ] No silent failures on permission errors

- [ ] **Logging Doesn't Expose Token**
  - [ ] Token value never logged
  - [ ] Operation metadata logged (repo, status, timestamp)
  - [ ] Audit trail includes who/what/when/where (not token)

- [ ] **Run Integration Test**
  - [ ] `pytest tests/agents/test_{agent_name}_token.py`
  - [ ] Token acquisition test passes
  - [ ] Scope validation test passes
  - [ ] Insufficient scope error test passes
  - [ ] Hidden script integration test (if applicable)

- [ ] **Registry Entry Updated**
  - [ ] `token_requirement` field set correctly
  - [ ] `scopes_required` array complete
  - [ ] `implementation_guide` references token resolver
  - [ ] `documentation` references TOKEN_HIERARCHY_GUIDE.md

---

##  Reference Documentation

| Document | Purpose | Link |
|----------|---------|------|
| Token Hierarchy Guide | Comprehensive token overview | `.codex/TOKEN_HIERARCHY_GUIDE.md` |
| Custom Agent Token Guidance | Full agent requirements | `.codex/CUSTOM_AGENT_TOKEN_GUIDANCE.md` |
| Hidden Scripts Security | Pattern storage architecture | `.codex/HIDDEN_SCRIPTS_SECURITY.md` |
| Token Resolver Implementation | API reference | `scripts/ci/_token_resolver.py` |
| Agent Registry | All agent metadata | `.github/agents/AGENT_REGISTRY.yaml` |

---

##  Token Usage Summary

### By Level

| Level | Token | Usage | Scopes | Rate Limit |
|-------|-------|-------|--------|-----------|
| 1 | GITHUB_TOKEN | Standard CI/CD | repo, status | 1,000/hr |
| 2 | CODEX_BACKUP_TOKEN | Elevated operations | repo, workflow, actions | 5,000/hr |
| 3 | CODEX_MASTER_KEY | Emergency only | admin:org, admin:repo_hook | 10,000/hr + burst |

### By Agent (Distribution)

- **Level 3 (No Fallback)**: 2 agents (ci-emergency-response, self-healing-orchestrator)
- **Level 2 (With Fallback)**: 11 agents (security, healing, governance)
- **Level 1 Only**: 0 agents (all agents require Level 2+)

### Scope Frequency

| Scope | Count | Primary Agents |
|-------|-------|---|
| `repo` | 13/13 | All |
| `contents:write` | 9/13 | Healer, security, type checking |
| `workflow` | 6/13 | CI operations, orchestration |
| `security_events` | 5/13 | Security scanning agents |
| `actions:write` | 3/13 | Emergency, compliance, orchestration |
| `pull_requests` | 1/13 | branch-divergence-resolution |

---

## Quick Start for New Agent Development

### Step 1: Choose Token Level

```
Is this an emergency operation?
  → YES: Use Level 3 (CODEX_MASTER_KEY)
  → NO: Use Level 2 (CODEX_BACKUP_TOKEN)
```

### Step 2: Define Required Scopes

List all API scopes needed by this agent.

```python
REQUIRED_SCOPES = ['repo', 'contents:write']
```

### Step 3: Implement Token Pattern

Choose pattern based on token level:

```python
# Level 3: Emergency (Pattern A)
token = get_token(required_elevated=True, require_level=3)
if not token:
    raise RuntimeError("Level 3 required")

# Level 2: Standard (Pattern B)
token = get_token(required_elevated=True)
if not token:
    token = get_token(required_elevated=False)
```

### Step 4: Validate Scopes

```python
validate_scope(token, REQUIRED_SCOPES)
```

### Step 5: Update Documentation

- Add 4 sections to agent .md prompt
- Update AGENT_REGISTRY.yaml
- Reference TOKEN_HIERARCHY_GUIDE.md

### Step 6: Test

```bash
pytest tests/agents/test_<agent_name>_token.py
```

---

## 📞 Support

For questions about token requirements:
- Check AGENT_REGISTRY.yaml for your agent
- Review TOKEN_HIERARCHY_GUIDE.md for detailed specs
- See "Common Errors & Solutions" section above
- Reference example implementations in `docs/agents/token_integration_examples/`

Last Updated: 2026-06-29
