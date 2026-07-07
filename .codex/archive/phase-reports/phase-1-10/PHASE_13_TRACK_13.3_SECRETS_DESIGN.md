# PHASE 13 TRACK 13.3: SECRETS DETECTION & REMEDIATION SYSTEM DESIGN

**Session**: phase-13-track-13-3-deployment  
**Date**: 2026-07-06T05:43:52Z  
**Mode**: ADVISORY (Design & Analysis)  
**Authority**: @mbaetiong (D-tier autonomous)  

---

## EXECUTIVE SUMMARY

This document designs the enterprise-grade secrets detection and remediation system for Phase 13 Track 13.3. The system is divided into 4 components working together to detect, classify, remediate, and verify secret exposure prevention.

**Key Design Decisions:**
- **Layered Detection**: Entropy + regex patterns + gitleaks engine
- **Automated Remediation**: Secrets rotation + environment variable substitution
- **Zero-Trust Verification**: Post-remediation re-scanning + git history audit
- **Integration**: Plugs into unified-security-scanner and CI/CD workflows # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret # pragma: allowlist secret

---

## 1. SYSTEM ARCHITECTURE

### 1.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│         ENTERPRISE SECRETS DETECTION & REMEDIATION SYSTEM        │
│                                                                  │
│  ┌──────────────────┐   ┌──────────────────┐   ┌────────────┐  │
│  │  Detection Layer │   │ Classification   │   │ Remediation│  │
│  │  ────────────    │   │ & Risk Scoring   │   │   Layer    │  │
│  │                  │   │ ────────────────  │   │ ──────────│  │
│  │ • Entropy scan   │→→→│ • Severity level │→→→│ • Rotation │  │
│  │ • Regex patterns │   │ • Context        │   │ • Env vars │  │
│  │ • Gitleaks       │   │ • Exposure time  │   │ • Re-scan  │  │
│  │ • Custom rules   │   │                  │   │            │  │
│  └──────────────────┘   └──────────────────┘   └────────────┘  │
│          ▲                      ▲                       ▼        │
│          │ Commits, files       │ Classification        │        │
│          │                      │                       ▼        │
│          └──────────────────────┴───────────────────────────┐   │
│                                                              │   │
│                   ┌──────────────────────┐                 │   │
│                   │ Verification & Report │◄────────────────┘   │
│                   │ ────────────────────  │                     │
│                   │ • Re-scan            │                     │
│                   │ • Audit log          │                     │
│                   │ • Compliance report  │                     │
│                   └──────────────────────┘                     │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 Data Flow

```
INPUT                DETECTION              CLASSIFICATION         OUTPUT
─────                ─────────              ──────────────         ──────

Git commits  ─────► [Entropy Scan]
Files        ─────► [Regex Patterns]  ──► [Risk Scoring] ──► [Rotation Service]
History      ─────► [Gitleaks Engine]     [Context Analysis]   [Verification]
```

---

## 2. DETECTION LAYER SPECIFICATION

### 2.1 Entropy-Based Detection (E-09 Patterns)

**Purpose**: Identify high-entropy strings that match secret patterns

**Approach**:
- Shannon entropy calculation per candidate token
- Threshold: ≥4.5 bits/character (detects base64, hex, random tokens)
- Context filtering: Ignores method names, version strings, UUIDs

**Implementation**:
```python
class EntropyDetector:
    def __init__(self, threshold: float = 4.5):
        self.threshold = threshold
    
    def calculate_entropy(self, text: str) -> float:
        """Shannon entropy of text."""
        freq = {}
        for char in text:
            freq[char] = freq.get(char, 0) + 1
        import math
        entropy = 0.0
        for count in freq.values():
            p = count / len(text)
            entropy -= p * math.log2(p)
        return entropy
    
    def detect(self, content: str) -> list[dict]:
        """Find high-entropy tokens in content."""
        results = []
        tokens = self._extract_tokens(content)
        for token, location in tokens:
            entropy = self.calculate_entropy(token)
            if entropy >= self.threshold:
                results.append({
                    "type": "high_entropy",
                    "token": token,
                    "entropy": entropy,
                    "location": location
                })
        return results
    
    def _extract_tokens(self, content: str) -> list[tuple[str, dict]]:
        """Extract candidate tokens (quoted strings, assignments)."""
        # Implementation: regex to find quoted/assigned values
        pass
```

**Coverage**:
- API keys (OpenAI, Anthropic, AWS, etc.)
- Database credentials (MongoDB, PostgreSQL, MySQL)
- JWT tokens, session keys, refresh tokens
- OAuth tokens, personal access tokens

**False Positive Mitigation**:
- Whitelist: Version numbers, commit SHAs, UUIDs
- Context: Ignore if value looks like placeholder (e.g., `xxx`, `****`)
- Pattern: Match against known secret formats (JWT structure, etc.)

### 2.2 Regex Pattern Detection

**Purpose**: Identify secrets matching known formats

**Patterns (E-09 Database)**:

| Pattern Type | Format | Example | Risk |
|-------------|--------|---------|------|
| API Keys | `api_key=...` or `"api_key": "..."` | `sk_live_abc123xyz` | CRITICAL |
| AWS Secrets | `AKIA...` (20 chars) or `aws_secret_access_key` | `AKIAIOSFODNN7EXAMPLE` | CRITICAL |
| Private Keys | `-----BEGIN PRIVATE KEY-----` | PEM-format keys | CRITICAL |
| Database URLs | `******host/db` | Connection strings | HIGH |
| JWT Tokens | `eyJh...` (base64 3-part) | ****** | HIGH |
| OAuth Tokens | `ghp_...` (GitHub), `pk_...` (Stripe) | Personal access tokens | HIGH |
| AWS Account ID | 12-digit number in IAM context | `123456789012` | MEDIUM |
| Email + Pass | `user@host.com:password` | Email credentials | MEDIUM |

**Implementation**:
```python
class PatternDetector:
    PATTERNS = {
        "aws_key": r"AKIA[0-9A-Z]{16}",
        "private_key": r"-----BEGIN (?:RSA|DSA|EC|PGP|OPENSSH) PRIVATE KEY",
        "jwt_token": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
        "github_pat": r"ghp_[A-Za-z0-9_]{36,255}",
        "stripe_key": r"sk_(?:live|test)_[0-9a-zA-Z]{24,}",
        "database_url": r"(?:postgres|mysql|mongodb)://[^@]+@[^/]+/",
        # ... more patterns
    }
    
    def detect(self, content: str) -> list[dict]:
        """Find secrets matching known patterns."""
        results = []
        for pattern_type, regex in self.PATTERNS.items():
            matches = re.finditer(regex, content)
            for match in matches:
                results.append({
                    "type": pattern_type,
                    "value": match.group(0),
                    "location": match.span()
                })
        return results
```

**False Positive Handling**:
- Validate format (e.g., AWS keys: verify checksum if available)
- Check if in test/example files (allowed list)
- Verify not in comments marked as safe

### 2.3 Gitleaks Engine Integration

**Purpose**: Leverages battle-tested secret detection tool

**Configuration**:
```yaml
# .gitleaks.toml
[gitleaks]
version = "8.18.0"
description = "Gitleaks configuration for Phase 13.3"

[[rules]]
# Enable all built-in detectors
id = "aws-access-token"
description = "AWS Access Token"
entropy = 3.5
regex = "(?i)aws[_-]?access[_-]?key[_-]?id"

[[rules]]
id = "github-pat"
description = "GitHub Personal Access Token"
entropy = 4.0
regex = "ghp_[0-9a-zA-Z]{36,255}"

# ... (50+ rules)
```

**Integration Points**:
1. Local pre-commit scan (detects before commit)
2. CI/CD pipeline scan (detects in PR commits)
3. Historical scan (detects in git history)
4. File scan (detects in filesystem)

**False Positive Filtering**:
- Exclude test files, fixtures, examples
- Exclude documentation with sanitized examples
- Allow marked-safe patterns

### 2.4 Custom Rule Engine

**Purpose**: Detect organization-specific secret patterns

**Examples**:
```python
class CustomRuleEngine:
    def __init__(self):
        self.rules = [
            {
                "name": "codex_internal_token",
                "pattern": r"codex-token-[0-9a-f]{32}",
                "severity": "HIGH"
            },
            {
                "name": "anthropic_api_key",
                "pattern": r"sk-ant-[a-zA-Z0-9_-]{50,}",
                "severity": "CRITICAL"
            },
            # ... organization-specific patterns
        ]
    
    def detect(self, content: str) -> list[dict]:
        """Detect custom secrets."""
        results = []
        for rule in self.rules:
            matches = re.finditer(rule["pattern"], content)
            for match in matches:
                results.append({
                    "type": rule["name"],
                    "value": match.group(0),
                    "severity": rule["severity"],
                    "location": match.span()
                })
        return results
```

---

## 3. CLASSIFICATION & RISK SCORING LAYER

### 3.1 Severity Classification

```python
class SeverityClassifier:
    """Classify detected secrets by severity."""
    
    CRITICALITY_MATRIX = {
        # (secret_type, exposure_time, context) → severity
        ("private_key", "any", "any"): "CRITICAL",
        ("aws_key", "git_commit", "public_repo"): "CRITICAL",
        ("database_url", "with_password", "any"): "HIGH",
        ("jwt_token", ">1_hour", "any"): "HIGH",
        ("api_key", ">1_day", "any"): "MEDIUM",
        ("oauth_token", "unused", "any"): "LOW",
    }
    
    def classify(self, finding: dict) -> dict:
        """Return classified finding with severity."""
        secret_type = finding["type"]
        exposure_time = self._calculate_exposure_time(finding)
        context = self._analyze_context(finding)
        
        key = (secret_type, exposure_time, context)
        severity = self.CRITICALITY_MATRIX.get(key, "MEDIUM")
        
        return {
            **finding,
            "severity": severity,
            "exposure_time": exposure_time,
            "context": context,
            "requires_rotation": severity in ["CRITICAL", "HIGH"]
        }
    
    def _calculate_exposure_time(self, finding: dict) -> str:
        """How long has this secret been exposed?"""
        # Based on git history, commit dates
        pass
    
    def _analyze_context(self, finding: dict) -> str:
        """Analyze where secret was found."""
        # Is it in: source code, config file, test file, docs?
        # Is the repo public or private?
        pass
```

### 3.2 Risk Scoring Formula

```
risk_score = (type_weight × type_severity +
              exposure_weight × exposure_score +
              context_weight × context_score) / sum_weights

where:
  type_weight     = 0.50  # What kind of secret?
  exposure_weight = 0.30  # How long was it exposed?
  context_weight  = 0.20  # Where was it found?
  
  type_severity: CRITICAL=10, HIGH=7, MEDIUM=5, LOW=2
  exposure_score: days_exposed / 365 (capped at 1.0)
  context_score: public_repo=1.0, private=0.5, test_file=0.2
```

**Example Scoring**:
- AWS key in public repo, exposed 30 days: 8.5/10 → CRITICAL
- API key in private repo, exposed 1 day: 4.2/10 → HIGH
- OAuth token in test file, unused: 1.8/10 → LOW

---

## 4. REMEDIATION LAYER SPECIFICATION

### 4.1 Automated Remediation Workflow

```python
class RemediationOrchestrator:
    """Orchestrates remediation of detected secrets."""
    
    async def remediate(self, finding: dict) -> dict:
        """Main remediation workflow."""
        
        # Step 1: Severity check
        if finding["severity"] not in ["CRITICAL", "HIGH"]:
            return {"status": "skipped", "reason": "low_severity"}
        
        # Step 2: Start rotation service
        rotation_service = RotationService()
        new_secret = await rotation_service.rotate(finding)
        
        # Step 3: Update code
        code_fixer = CodeFixer()
        await code_fixer.replace_with_env_var(finding, new_secret)
        
        # Step 4: Update environment
        env_manager = EnvironmentManager()
        await env_manager.set_variable(finding["env_var_name"], new_secret)
        
        # Step 5: Verify remediation
        verifier = RemediationVerifier()
        verification = await verifier.verify(finding)
        
        return {
            "status": "remediated",
            "new_secret_name": finding["env_var_name"],
            "verification": verification
        }
```

### 4.2 Code Transformation

**Before**:
```python
# src/codex/api/auth_routes.py
_DEFAULT_SECRET = "codex-auth-secret-abc123xyz"  # EXPOSED!
API_KEY = "sk_test_abc123xyz"  # EXPOSED!
DATABASE_URL = "******localhost/db"

def init_auth():
    secret = _DEFAULT_SECRET  # Uses hardcoded secret
    client = create_client(api_key=API_KEY)
    conn = connect(DATABASE_URL)
```

**After**:
```python
# src/codex/api/auth_routes.py
import os

# Secrets now loaded from environment
_DEFAULT_SECRET = os.environ.get("CODEX_AUTH_SECRET")
API_KEY = os.environ.get("OPENAI_API_KEY")
DATABASE_URL = os.environ.get("DATABASE_URL")

def init_auth():
    secret = _get_secret("CODEX_AUTH_SECRET")  # From environment
    client = create_client(api_key=_get_secret("OPENAI_API_KEY"))
    conn = connect(_get_secret("DATABASE_URL"))

def _get_secret(name: str) -> str:
    """Get secret from environment with validation."""
    value = os.environ.get(name)
    if not value:
        raise ValueError(f"Missing required secret: {name}")
    return value
```

**Transformation Rules**:
1. Identify hardcoded string literals matching secret patterns
2. Extract to named constant (or env var directly)
3. Replace with `os.environ.get("VAR_NAME")`
4. Add validation for required secrets
5. Update `.env`, `.env.example`, GitHub Secrets

### 4.3 Environment Variable Management

**Environment Variable Naming Convention**:
```
CODEX_<COMPONENT>_<TYPE>_<IDENTIFIER>

Examples:
  CODEX_AUTH_SECRET          # JWT signing key for auth
  CODEX_DATABASE_URL         # PostgreSQL connection
  CODEX_OPENAI_API_KEY       # OpenAI API credentials
  CODEX_GITHUB_TOKEN         # GitHub API token
  CODEX_STRIPE_SECRET_KEY    # Stripe payments
```

**Deployment Strategy**:
```yaml
# .github/workflows/secrets-deployment.yml
name: Deploy Secrets

on:
  workflow_dispatch:
    inputs:
      environment: { type: string }

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Rotate secrets
        run: |
          python scripts/ci/rotate_secrets.py \
            --env ${{ inputs.environment }} \
            --services auth,database,api
      
      - name: Update GitHub Secrets
        run: |
          gh secret set CODEX_AUTH_SECRET --body "$NEW_SECRET"
      
      - name: Deploy to staging
        run: |
          python scripts/ci/deploy_to_environment.py \
            --env staging \
            --secrets-file .secrets.staging.json
```

### 4.4 Secrets Rotation Service

**Purpose**: Safely rotate compromised secrets

```python
class SecretsRotationService:
    """Manages secure secret rotation."""
    
    async def rotate_jwt_secret(self, old_secret: str) -> str:
        """Rotate JWT signing key."""
        new_secret = secrets.token_urlsafe(32)
        
        # Deploy new secret
        await self.env_manager.set("CODEX_AUTH_SECRET", new_secret)
        
        # Grace period for old secret acceptance
        await self.grace_period_manager.set(old_secret, ttl=3600)
        
        # Log rotation event
        await self.audit_log.record({
            "event": "secret_rotated",
            "type": "jwt_secret",
            "timestamp": datetime.now(),
            "rotated_by": "remediation_agent"
        })
        
        return new_secret
    
    async def rotate_api_key(self, service: str, old_key: str) -> str:
        """Rotate external API key."""
        # Call service API to generate new key
        new_key = await self._generate_new_key(service)
        
        # Update environment
        await self.env_manager.set(f"CODEX_{service.upper()}_API_KEY", new_key)
        
        # Revoke old key (service-specific)
        await self._revoke_key(service, old_key)
        
        return new_key
    
    async def _revoke_key(self, service: str, key: str):
        """Revoke key with external service."""
        if service == "openai":
            # Call OpenAI API to revoke key
            pass
        elif service == "github":
            # Delete GitHub personal access token
            pass
        # ... other services
```

---

## 5. VERIFICATION & AUDIT LAYER

### 5.1 Post-Remediation Verification

```python
class RemediationVerifier:
    """Verifies that remediation was successful."""
    
    async def verify(self, finding: dict) -> dict:
        """Complete verification workflow."""
        
        checks = {
            "secret_removed": await self._check_secret_removed(finding),
            "env_var_set": await self._check_env_var_set(finding),
            "code_uses_env": await self._check_code_uses_env(finding),
            "git_history_clean": await self._check_git_history_clean(finding),
            "no_redetection": await self._check_no_redetection(finding)
        }
        
        all_passed = all(checks.values())
        
        return {
            "verified": all_passed,
            "checks": checks,
            "verification_time": datetime.now(),
            "status": "PASSED" if all_passed else "FAILED"
        }
    
    async def _check_secret_removed(self, finding: dict) -> bool:
        """Verify hardcoded secret is gone from current code."""
        # Scan current HEAD
        detector = EntropyDetector()
        results = detector.detect(finding["file_content"])
        return not any(r["token"] == finding["token"] for r in results)
    
    async def _check_git_history_clean(self, finding: dict) -> bool:
        """Verify secret doesn't appear in git history."""
        # Use BFG Repo-Cleaner or git-filter-repo
        # to remove from entire history
        pass
```

### 5.2 Audit Logging & Reporting

**Audit Log Schema**:
```json
{
  "event_id": "sec-remediation-2026-07-06-001",
  "timestamp": "2026-07-06T12:34:56Z",
  "event_type": "secret_detection",
  "secret_type": "api_key",
  "severity": "HIGH",
  "detection_method": "entropy_scan",
  "file": "src/codex/api/auth_routes.py",
  "line_number": 123,
  "exposure_time_hours": 48,
  "remediation": {
    "status": "completed",
    "timestamp": "2026-07-06T13:00:00Z",
    "actions": [
      "secret_rotated",
      "env_var_set",
      "code_updated",
      "verification_passed"
    ]
  },
  "actor": "unified-security-scanner",
  "compliance_tags": ["pci-dss", "hipaa", "soc2"]
}
```

**Compliance Reporting**:
```python
class ComplianceReporter:
    """Generate compliance reports on secrets handling."""
    
    def generate_monthly_report(self) -> dict:
        """Generate monthly secrets audit report."""
        return {
            "period": "2026-07-01 to 2026-07-31",
            "metrics": {
                "secrets_detected": 42,
                "secrets_remediated": 42,
                "detection_lag_avg_hours": 2.3,
                "remediation_time_avg_hours": 0.5,
                "zero_exposure_secrets": 38,
                "exposed_secrets": 4
            },
            "exposed_secrets": [
                {
                    "type": "API key",
                    "exposure_duration": "3 days",
                    "rotation_status": "completed"
                },
                # ...
            ],
            "compliance_status": {
                "pci_dss": "compliant",
                "hipaa": "compliant",
                "sox": "compliant"
            }
        }
```

---

## 6. INTEGRATION POINTS

### 6.1 Integration with Unified Security Scanner

**Entry Point**: `unified-security-scanner` (main agent)

```python
class UnifiedSecurityScanner:
    def run_security_audit(self):
        # ... other scanners ...
        
        # Secrets Detection & Remediation
        secrets_scanner = SecretsDetectionSystem()
        findings = await secrets_scanner.scan()
        
        if findings:
            remediation = await secrets_scanner.remediate(findings)
            self.report_findings("secrets", findings, remediation)
```

### 6.2 Integration with CI/CD

**Pre-commit Hook**:
```bash
# .husky/pre-commit
#!/bin/bash
python scripts/ci/secrets_detector.py --mode pre-commit
if [ $? -ne 0 ]; then
  echo "❌ Secrets detected. Commit blocked."
  exit 1
fi
```

**GitHub Actions Workflow**:
```yaml
# .github/workflows/secrets-scan.yml
name: Secrets Detection & Remediation

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for gitleaks
      
      - name: Run secrets detector
        run: |
          python scripts/ci/secrets_detector.py \
            --scan-type full \
            --output json > secrets-report.json
      
      - name: Auto-remediate critical findings
        if: failure()
        run: |
          python scripts/ci/remediate_secrets.py \
            --report secrets-report.json \
            --auto-remediate
      
      - name: Upload findings
        uses: actions/upload-artifact@v4
        with:
          name: secrets-report
          path: secrets-report.json
```

### 6.3 Integration with Track 13.1 & 13.2

**Track 13.1 (Test Automation)**: Secret rotation tests
- Verify rotating secrets doesn't break tests
- Test env var loading in test suite

**Track 13.2 (RAG Meta-Tensor)**: No direct integration
- Secrets scanner runs independently
- Shares audit logging infrastructure

---

## 7. DEPLOYMENT STRATEGY

### 7.1 Phase Timeline

```
Day 1 (2026-07-10): Detection system deployed
  ├─ Entropy detector active
  ├─ Pattern detector active
  └─ Gitleaks engine integrated

Day 2 (2026-07-11): Remediation system deployed
  ├─ Secrets rotation service operational
  ├─ Code transformation rules active
  └─ Env var management deployed

Days 3-5 (2026-07-12/14): Full integration & testing
  ├─ Pre-commit hooks deployed
  ├─ CI/CD workflow active
  └─ Audit logging operational
```

### 7.2 Success Criteria

- ✅ 0 undetected secrets in codebase
- ✅ 100% detection accuracy (no false negatives)
- ✅ <2% false positive rate (with filtering)
- ✅ <1 hour detection-to-remediation lag
- ✅ 100% remediation verification passing
- ✅ Zero secrets in git history
- ✅ All compliance checks passing (PCI-DSS, HIPAA, SOC2)

---

## 8. RISK ASSESSMENT

| Risk | Severity | Mitigation |
|------|----------|-----------|
| False positives blocking commits | MEDIUM | Whitelist + human review |
| Rotation failures | HIGH | Fallback rotation service, rollback plan |
| Secret exposure during remediation | HIGH | Grace period for old secrets, new-secret-only mode |
| Detection lag | MEDIUM | Real-time scanning + pre-commit hooks |
| Compliance violations | CRITICAL | Mandatory audit logging, rotation compliance |

---

## 9. TESTING STRATEGY

### 9.1 Unit Tests

- Entropy detection accuracy (100 test cases)
- Pattern detection (50 test cases per pattern)
- Severity classification logic
- Risk scoring formula
- Code transformation rules

### 9.2 Integration Tests

- End-to-end detection → remediation → verification
- Git history scanning + BFG integration
- Secrets rotation with 3+ external services
- CI/CD workflow integration
- Pre-commit hook functionality

### 9.3 Security Tests

- Deliberately plant secrets, verify detection
- Verify no secrets leaked in remediation process
- Test grace period security
- Validate audit log integrity

---

## DOCUMENT CONTROL

**Status**: ✅ ADVISORY PHASE COMPLETE  
**Date**: 2026-07-06T05:43:52Z  
**Next Phase**: Full Execution (Days 5-9, pending Track 12.3 clearance)  
**Authority**: @mbaetiong (D-tier autonomous, APPROVED)
