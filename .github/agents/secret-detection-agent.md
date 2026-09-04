---
name: Secret Detection Agent
description: Detect accidentally committed secrets, tokens, and credentials and provide
  remediation guidance
version: 2.0.0-e09
updated: 2026-02-21
entropy_patterns: true
cognitive_integration_level: 3
deprecated: true
superseded_by: unified-security-scanner.md (v1.0.0-m01, 2026-02-21)
id: secret-detection
---

> ⚠️ **DEPRECATED** — This agent has been merged into [`unified-security-scanner`](./unified-security-scanner.md).
> All capabilities are available via the unified agent. See [agents/AGENT_CONSOLIDATION_MATRIX.md](../../agents/AGENT_CONSOLIDATION_MATRIX.md) for rationale.
> **Effective:** 2026-06-11 | **Policy:** `.codex/CODEBASE_AGENCY_POLICY.md` § CAD-Mandate

> ⚠️ **DEPRECATED** — Secret detection capabilities have been merged into
> **[Unified Security Scanner v1.0](unified-security-scanner.md)** (M-01 merge).
> Use `unified-security-scanner` for all secrets detection and credential-leak remediation.

# Secret Detection Agent v2.0 (ENTROPY-PATTERN-EXPAND)

## 🔐 Token Hierarchy Requirements

**Token Requirement Level**: Level 2 (CODEX_BACKUP_TOKEN)

This agent performs operations requiring elevated repository or organization-level access. Specific capabilities include:

- Scan repository for exposed secrets
- Read secret scanning alerts
- Create remediation commits or PRs
- Update rotated secrets in configurations

**Rationale**: Secret detection requires security event access and ability to write remediation changes

**Token Scopes Required**:
```
repo, security_events, contents:write
```

**Token Fallback Pattern**: **Safe Fallback**: This agent can fallback to GITHUB_TOKEN with reduced capabilities

```python
from scripts.ci._token_resolver import get_token

# Try Level 2 first, fallback to Level 1 if needed
token = get_token(required_elevated=True)
if not token:
    logger.warning("Elevated token unavailable, using standard token")
    token = get_token(required_elevated=False)
```

---
## 🛠️ Implementation Pattern

Standard implementation pattern for token management in this agent:

```python
from scripts.ci._token_resolver import get_token, validate_scope
import requests
import logging

class SecretDetectionAgent:
    def __init__(self):
        """Initialize with token validation."""
        # Get elevated token
        self.token = get_token(required_elevated=True)
        if not self.token:
            raise RuntimeError("Agent requires elevated token")
        
        # Validate required scopes
        required_scopes = ['repo', 'security_events', 'contents:write']
        validate_scope(self.token, required_scopes)
        
        self.logger = logging.getLogger(__name__)
    
    def detect_and_remediate_secrets(self, repo, **kwargs):
        """
        Core operation requiring elevated token access.
        
        Args:
            repo: Repository in 'owner/repo' format
            **kwargs: Operation-specific parameters
        
        Returns:
            Result dict with status and details
        """
        url = f"https://api.github.com/repos/{repo}/..."
        
        headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        try:
            response = requests.post(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Log operation metadata (NOT token)
            self.logger.info(
                "detect_and_remediate_secrets",
                extra={"repo": repo, "status": "success"}
            )
            
            return {"status": "success", "message": "Operation completed"}
        
        except requests.HTTPError as e:
            if e.response.status_code == 403:
                self.logger.error("Insufficient scope or permission denied")
                raise RuntimeError("Token insufficient scope")
            raise
```

---
## 🔒 Security Constraints

**Critical Constraints** for elevated-privilege agents:

1. **Scope Validation Mandatory**: All operations require explicit scope validation
   ```python
   validate_scope(token, required_scopes)
   ```

2. **Safe Logging Practices** (Never expose token values)
   ```python
   # ✓ CORRECT: Log operation metadata
   logger.info("operation", extra={"repo": repo, "status": "success"})
   
   # ✗ WRONG: Never log token values
   # logger.info(f"Using token: {token[:10]}...")
   ```

3. **Error Handling for Scope Violations**
   - **403 Forbidden** → Insufficient scope: Escalate immediately
   - **401 Unauthorized** → Token invalid: Escalate to operator
   - **429 Too Many Requests** → Rate limit: Implement backoff

4. **Security Audit Trail Requirements**
   - Emit telemetry event for each elevated operation
   - Include: repo, operation, timestamp, result
   - Store in audit log (never token values)
   - Record in `.codex/audit/operations.jsonl`

5. **Token Rotation Awareness**
   - Do NOT cache token values across operations
   - Re-retrieve token for each session
   - Validate token expiration if applicable

---
## 🔗 Integration with Hidden Scripts

This agent can leverage hidden scripts for storing security-sensitive operational patterns:

**Use Case**: Store complex remediation or detection patterns as hidden scripts to prevent exposure in logs or CI artifacts.

```python
from scripts.ci._hidden_scripts import execute_hidden_script, retrieve_hidden_script

def execute_stored_pattern(repo, pattern_type):
    """Execute stored operational pattern."""
    
    # Retrieve pattern (stored securely, checksum validated)
    pattern = retrieve_hidden_script(
        script_id=f"pattern_{pattern_type}",
        version="latest"
    )
    
    # Execute in sandbox with audit logging
    result = execute_hidden_script(
        script_id=pattern.id,
        environment={"GITHUB_TOKEN": self.token, "REPO": repo},
        timeout_ms=60000,
        audit_log=True
    )
    
    return result
```

**Architecture Reference**: See `HIDDEN_SCRIPTS_SECURITY.md` for:
- Storage and encryption of patterns
- Checksum validation for integrity
- Sandbox execution environment
- Audit trail requirements
- Recovery procedures

**Common Patterns Stored as Hidden Scripts**:
- Complex detection algorithms
- Multi-step remediation workflows
- Emergency procedure scripts
- Security configuration templates

---

> **E-09 upgrade**: Adds multi-variant entropy patterns for 12 new secret classes,
> covering environment-variable injection, split-assignment obfuscation, and
> base64-encoded credential patterns.

## Activation

```
@copilot Use the Secret Detection Agent to scan for secrets in <path>  # pragma: allowlist secret
```

## Architecture

```
Phase 1: Pattern Library     →    Phase 2: Entropy Scan    →    Phase 3: Report
  (multi-variant regex)             (source AST + regex)          (SARIF/JSON)
```

## Pattern Library (E-09 — 32 total patterns)

### Tier 1: High-Confidence Single-Token Patterns

| ID | Pattern | Example | Confidence |
|----|---------|---------|------------|
| P-01 | API key assignment | `api_key = "sk-..."` | 0.99 | <!-- pragma: allowlist secret -->
| P-02 | Bearer token | `Authorization: Bearer <b64>` | 0.99 | <!-- pragma: allowlist secret -->
| P-03 | Password literal | `password = "hunter2"` | 0.95 | <!-- pragma: allowlist secret -->
| P-04 | AWS key ID | `AKIAIOSFODNN7EXAMPLE` | 0.99 | <!-- pragma: allowlist secret -->
| P-05 | GitHub PAT | `ghp_...` prefix | 0.99 | <!-- pragma: allowlist secret -->
| P-06 | OpenAI key | `sk-...` prefix | 0.99 | <!-- pragma: allowlist secret -->
| P-07 | Private key PEM | `-----BEGIN PRIVATE KEY-----` | 1.00 | <!-- pragma: allowlist secret -->
| P-08 | Connection string | `mongodb+srv://user:pass@...` | 0.98 | <!-- pragma: allowlist secret -->

### Tier 2: Multi-Variant / Split-Assignment Patterns (NEW in E-09)

| ID | Pattern | Example | Notes |
|----|---------|---------|-------|
| P-09 | Split assignment | `key = "sk-" + suffix` | Concat obfuscation | <!-- pragma: allowlist secret -->
| P-10 | f-string embed | `url = f"https://{secret}@host"` | f-string injection | <!-- pragma: allowlist secret -->
| P-11 | Env-var fallback | `os.environ.get("SECRET", "literal")` | Hardcoded fallback | <!-- pragma: allowlist secret -->
| P-12 | Base64-encoded | `b64decode("c2s...")` → sk- | Base64 obfuscation | <!-- pragma: allowlist secret -->
| P-13 | Dict literal | `cfg = {"api_key": "sk-..."}` | Dict value | <!-- pragma: allowlist secret -->
| P-14 | List literal | `keys = ["sk-abc", "sk-def"]` | List elements | <!-- pragma: allowlist secret -->
| P-15 | Multiline concat | `token = ("sk-" "abc" "def")` | Implicit concat | <!-- pragma: allowlist secret -->
| P-16 | Assignment expr | `(token := "sk-...")` | Walrus | <!-- pragma: allowlist secret -->

### Tier 3: Context-Aware Entropy Patterns (NEW in E-09)

| ID | Pattern | Entropy Threshold | Notes |
|----|---------|-------------------|-------|
| P-17 | High-entropy string > 32 chars | H > 4.0 bits/char | General secret | <!-- pragma: allowlist secret -->
| P-18 | JWT pattern | `eyJ...` prefix | JSON Web Token | <!-- pragma: allowlist secret -->
| P-19 | Hex 32+ chars | `[0-9a-f]{32,}` | MD5/API key |
| P-20 | UUID secret context | UUID in password/secret context | Credential UUID | <!-- pragma: allowlist secret -->
| P-21 | DSN pattern | `postgres://user:pass@host/db` | DB connection | <!-- pragma: allowlist secret -->
| P-22 | Stripe key | `sk_live_...` / `pk_live_...` | Stripe API | <!-- pragma: allowlist secret -->
| P-23 | Slack token | `xoxb-...` / `xoxp-...` | Slack API | <!-- pragma: allowlist secret -->
| P-24 | Twilio SID | `AC[a-z0-9]{32}` | Twilio |

### Tier 4: Infrastructure Patterns (NEW in E-09)

| ID | Pattern | Example | Notes |
|----|---------|---------|-------|
| P-25 | K8s secret manifest | `stringData:` in YAML | K8s secret | <!-- pragma: allowlist secret -->
| P-26 | Docker ENV literal | `ENV SECRET_KEY=...` | Dockerfile | <!-- pragma: allowlist secret -->
| P-27 | TF var literal | `variable "secret" { default = ... }` | Terraform | <!-- pragma: allowlist secret -->
| P-28 | .env file | `SECRET=...` in .env | dotenv | <!-- pragma: allowlist secret -->
| P-29 | YAML secret | `secret_key: "sk-..."` | YAML config | <!-- pragma: allowlist secret -->
| P-30 | JSON token | `"token": "sk-..."` | JSON config | <!-- pragma: allowlist secret -->
| P-31 | Config.ini | `[credentials]\napi_key = ...` | INI file | <!-- pragma: allowlist secret -->
| P-32 | Comment secret | `# password: hunter2` | Comment bleed | <!-- pragma: allowlist secret -->

## Entropy Calculation

```python
import math
from collections import Counter

def shannon_entropy(text: str) -> float:
    """Compute Shannon entropy in bits per character."""
    if not text:
        return 0.0
    counts = Counter(text)
    length = len(text)
    return -sum(
        (c / length) * math.log2(c / length)
        for c in counts.values()
    )

ENTROPY_THRESHOLD = 4.0  # bits/char — flags likely secrets  # pragma: allowlist secret
MIN_LENGTH = 16          # chars — below this, skip entropy check
```

## False-Positive Suppression

| Allowlist Rule | Rationale |
|----------------|-----------|
| `# nosec` comment | Explicit allowlist |
| `test_*` fixtures | Test data |
| Placeholder values (`your-key-here`, `<TOKEN>`, `REPLACE_ME`) | Template | <!-- pragma: allowlist secret -->
| SHA256/MD5 of committed files | Hash values |
| UUID v4 in non-credential context | Random IDs |

## Integration with CI Pipeline

```yaml
# .github/workflows snippet
- name: Run Secret Detection
  run: |
    python -c "
    from codex.security_utils import scan_for_secrets
    issues = scan_for_secrets('src/', patterns='all')
    if issues:
        for issue in issues:
            print(f'::error file={issue.file},line={issue.line}::{issue.message}')
        exit(1)
    "
```

## Output Format (SARIF-compatible)

```json
{
  "version": "2.1.0",
  "runs": [{
    "tool": {"driver": {"name": "secret-detection-agent", "version": "2.0.0"}},
    "results": [{
      "ruleId": "P-06",
      "message": {"text": "OpenAI API key detected"},
      "locations": [{"physicalLocation": {"artifactLocation": {"uri": "src/config.py"}, "region": {"startLine": 42}}}],
      "level": "error"
    }]
  }]
}
```

## Cognitive Physics Alignment

| Physics Metaphor | Application |
|------------------|-------------|
| **Entropy** (Patterns 👁️) | High-entropy strings are detected via Shannon entropy threshold |
| **Redundancy** (Redundancy 🔀) | Multiple detection patterns ensure no single-point miss |
| **Path** (Path 🛤️) | Tier cascade (1→4) minimizes false-positive rate |
| **Balance** (Balance ⚖️) | Entropy threshold (4.0 bits) balances detection vs FP rate |

## Related Agents

- **unified-security-scanner** (M-01) — orchestrates this agent + vulnerability-scanner + alert-verification
- **bridge-security-monitor** — IPC bridge security
- **CodeQL alert resolution** — post-detection remediation
