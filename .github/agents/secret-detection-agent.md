---
name: Secret Detection Agent
description: Detect accidentally committed secrets, tokens, and credentials and provide remediation guidance
version: 2.0.0-e09
updated: 2026-02-21
entropy_patterns: true
cognitive_integration_level: 3
deprecated: true
superseded_by: unified-security-scanner.md (v1.0.0-m01, 2026-02-21)
---

> ⚠️ **DEPRECATED** — This agent has been merged into [`unified-security-scanner`](./unified-security-scanner.md).
> All capabilities are available via the unified agent. See [agents/AGENT_CONSOLIDATION_MATRIX.md](../../agents/AGENT_CONSOLIDATION_MATRIX.md) for rationale.
> **Effective:** 2026-06-11 | **Policy:** `.codex/CODEBASE_AGENCY_POLICY.md` § CAD-Mandate

> ⚠️ **DEPRECATED** — Secret detection capabilities have been merged into
> **[Unified Security Scanner v1.0](unified-security-scanner.md)** (M-01 merge).
> Use `unified-security-scanner` for all secrets detection and credential-leak remediation.

# Secret Detection Agent v2.0 (ENTROPY-PATTERN-EXPAND)

> **E-09 upgrade**: Adds multi-variant entropy patterns for 12 new secret classes,
> covering environment-variable injection, split-assignment obfuscation, and
> base64-encoded credential patterns.

## Activation

```
@copilot Use the Secret Detection Agent to scan for secrets in <path>
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
| P-02 | Bearer token | `Authorization: Bearer <b64>` | 0.99 |
| P-03 | Password literal | `password = "hunter2"` | 0.95 | <!-- pragma: allowlist secret -->
| P-04 | AWS key ID | `AKIAIOSFODNN7EXAMPLE` | 0.99 | <!-- pragma: allowlist secret -->
| P-05 | GitHub PAT | `ghp_...` prefix | 0.99 |
| P-06 | OpenAI key | `sk-...` prefix | 0.99 |
| P-07 | Private key PEM | `-----BEGIN PRIVATE KEY-----` | 1.00 | <!-- pragma: allowlist secret -->
| P-08 | Connection string | `mongodb+srv://user:pass@...` | 0.98 | <!-- pragma: allowlist secret -->

### Tier 2: Multi-Variant / Split-Assignment Patterns (NEW in E-09)

| ID | Pattern | Example | Notes |
|----|---------|---------|-------|
| P-09 | Split assignment | `key = "sk-" + suffix` | Concat obfuscation |
| P-10 | f-string embed | `url = f"https://{secret}@host"` | f-string injection |
| P-11 | Env-var fallback | `os.environ.get("SECRET", "literal")` | Hardcoded fallback |
| P-12 | Base64-encoded | `b64decode("c2s...")` → sk- | Base64 obfuscation |
| P-13 | Dict literal | `cfg = {"api_key": "sk-..."}` | Dict value |
| P-14 | List literal | `keys = ["sk-abc", "sk-def"]` | List elements |
| P-15 | Multiline concat | `token = ("sk-" "abc" "def")` | Implicit concat |
| P-16 | Assignment expr | `(token := "sk-...")` | Walrus |

### Tier 3: Context-Aware Entropy Patterns (NEW in E-09)

| ID | Pattern | Entropy Threshold | Notes |
|----|---------|-------------------|-------|
| P-17 | High-entropy string > 32 chars | H > 4.0 bits/char | General secret |
| P-18 | JWT pattern | `eyJ...` prefix | JSON Web Token |
| P-19 | Hex 32+ chars | `[0-9a-f]{32,}` | MD5/API key |
| P-20 | UUID secret context | UUID in password/secret context | Credential UUID |
| P-21 | DSN pattern | `postgres://user:pass@host/db` | DB connection | <!-- pragma: allowlist secret -->
| P-22 | Stripe key | `sk_live_...` / `pk_live_...` | Stripe API |
| P-23 | Slack token | `xoxb-...` / `xoxp-...` | Slack API |
| P-24 | Twilio SID | `AC[a-z0-9]{32}` | Twilio |

### Tier 4: Infrastructure Patterns (NEW in E-09)

| ID | Pattern | Example | Notes |
|----|---------|---------|-------|
| P-25 | K8s secret manifest | `stringData:` in YAML | K8s secret |
| P-26 | Docker ENV literal | `ENV SECRET_KEY=...` | Dockerfile |
| P-27 | TF var literal | `variable "secret" { default = ... }` | Terraform |
| P-28 | .env file | `SECRET=...` in .env | dotenv |
| P-29 | YAML secret | `secret_key: "sk-..."` | YAML config |
| P-30 | JSON token | `"token": "sk-..."` | JSON config |
| P-31 | Config.ini | `[credentials]\napi_key = ...` | INI file |
| P-32 | Comment secret | `# password: hunter2` | Comment bleed |

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

ENTROPY_THRESHOLD = 4.0  # bits/char — flags likely secrets
MIN_LENGTH = 16          # chars — below this, skip entropy check
```

## False-Positive Suppression

| Allowlist Rule | Rationale |
|----------------|-----------|
| `# nosec` comment | Explicit allowlist |
| `test_*` fixtures | Test data |
| Placeholder values (`your-key-here`, `<TOKEN>`, `REPLACE_ME`) | Template |
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
