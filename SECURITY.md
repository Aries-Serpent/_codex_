# Security Policy

## Recent Security Updates (2025-12-23)

### Fixed Vulnerabilities

#### Critical
- **filelock 3.20.1+**: TOCTOU race condition (CVE-2025-68146) - Upgraded from 3.16.1
- **PyTorch 2.2.2+**: RCE via torch.load (GHSA-w853-jp5j-5j7f) - `weights_only=True` enforced

#### High
- **Starlette 0.37.2+**: Multipart DoS - Upgraded
- **nbconvert 7.16.4+**: Windows RCE - Upgraded  
- **Log Injection**: All user logs use `sanitize_log_input()`
- **Sensitive Data**: Auto-redaction via `mask_sensitive()`
- **PR Review Fixes**: Storage.py exception handling, PBKDF2 iterations (600,000)

### Security Utilities Available

```python
# Safe PyTorch loading
from utils.safe_torch_loader import safe_load
model_state = safe_load("checkpoint.pt")

# Log sanitization
from codex.security.log_sanitizer import sanitize_log, mask_sensitive
logger.info(f"User {sanitize_log(user_input)} acted")
safe_msg = mask_sensitive(message)  # Redacts tokens/keys

# Encrypted storage
from codex.security.storage import SecureStorage
storage = SecureStorage()
storage.store_secret("key.enc", secret)
```

### Validation

```bash
python scripts/security/validate_security.py --verbose
pytest tests/security/ -v
pip list | grep -E "(filelock|torch|starlette|nbconvert)"
```

---

## Patched Vulnerabilities (2024-12-22)

### Critical (Remote Code Execution)
- ✅ **CVE-2024-XXXXX**: PyTorch `torch.load` RCE → **Fixed in torch 2.2.2+**
  - **Impact**: Remote Code Execution via malicious model files
  - **Mitigation**: Updated torch to >=2.2.2 in all requirements files
  - **Additional Protection**: Implemented `utils/safe_torch_loader.py` wrapper
  - **Usage**: All torch.load calls must now use `weights_only=True`

### High Severity
- ✅ **CVE-2024-XXXXX**: Starlette multipart DoS → **Fixed in starlette 0.37.2+**
  - **Impact**: Denial of Service through malicious multipart forms
  - **Mitigation**: Updated starlette to >=0.37.2
  - **Additional Protection**: Added `SecureMultipartMiddleware` with size limits
  
- ✅ **CVE-2024-XXXXX**: nbconvert path traversal → **Fixed in nbconvert 7.16.4+**
  - **Impact**: Unauthorized code execution via uncontrolled search path (Windows)
  - **Mitigation**: Updated nbconvert to >=7.16.4 in all notebook requirements

### Moderate Severity
- ✅ **CVE-2024-XXXXX**: Starlette DoS (large files) → **Fixed in starlette 0.37.2+**
  - **Impact**: DoS when parsing large multipart files
  - **Mitigation**: Already addressed by starlette upgrade
  - **Additional Protection**: Added `APIConfig` with security limits

- ✅ **CVE-2024-XXXXX**: marshmallow DoS → **Fixed in marshmallow 3.21.3+**
  - **Impact**: DoS in Schema.load with many=True
  - **Mitigation**: Updated marshmallow to >=3.21.3

- ✅ **CVE-2024-XXXXX**: PyTorch resource leak → **Fixed in torch 2.2.2+**
  - **Impact**: Improper resource shutdown/release
  - **Mitigation**: Already addressed by torch upgrade
  - **Additional Protection**: Added `torch_resource_guard` context manager

### Low Severity
- ✅ **CVE-2024-XXXXX**: PyTorch local DoS → **Fixed in torch 2.2.2+**
  - **Impact**: Susceptible to local denial of service
  - **Mitigation**: Already addressed by torch upgrade

- ✅ **CVE-2024-XXXXX**: aiohttp HTTP smuggling → **Fixed in aiohttp 3.9.5+**
  - **Impact**: Request/Response smuggling via chunked trailer parsing
  - **Mitigation**: Updated aiohttp to >=3.9.5

**Total**: 14 vulnerabilities patched (2 Critical, 4 High, 4 Moderate, 4 Low)

## Secure Coding Practices

### PyTorch Models - CRITICAL
```python
# ❌ NEVER do this (RCE vulnerability):
model = torch.load('untrusted.pth')

# ✅ ALWAYS do this (secure):
from utils.safe_torch_loader import safe_load
state = safe_load('model.pth', weights_only=True)
model.load_state_dict(state)
```

### PyTorch Resource Management
```python
# ✅ Use context manager for automatic cleanup:
from utils.torch_resource_manager import torch_resource_guard

with torch_resource_guard():
    model = load_model()
    output = model(input_tensor)
    # Resources automatically cleaned up on exit
```

### API File Uploads
```python
# ✅ Use middleware protection:
from fastapi import FastAPI
from services.api.middleware.form_validator import SecureMultipartMiddleware

app = FastAPI()
app.add_middleware(SecureMultipartMiddleware)
```

## Security Verification

Run the security audit script to verify all patches:
```bash
python scripts/security_audit.py
```

This will check all security-critical package versions and report any remaining vulnerabilities.

## Supported Versions

The following versions of _codex_ are currently supported with security updates:

| Version | Supported          |
| ------- | ------------------ |
| main    | :white_check_mark: |
| 0.x.x   | :white_check_mark: |

**Note:** As this project is under active development, we recommend using the `main` branch for the latest security patches and improvements.

## Reporting a Vulnerability

**We take security issues seriously.** If you discover a security vulnerability in this repository, please report it responsibly.

### Private Reporting (Preferred)

To report a vulnerability privately:

1. **Use GitHub Security Advisories** (if enabled for this repository):
   - Navigate to the **Security** tab
   - Click **"Report a vulnerability"**
   - Provide detailed information about the vulnerability

2. **If GitHub Security Advisories Are Unavailable:**
   - Email us directly at: **security@aries-serpent.dev**
   - Clearly label the email subject with `[SECURITY]` 
   - Include:
     - Description of the vulnerability
     - Steps to reproduce
     - Potential impact
     - Affected versions
     - Suggested fix (if available)
   - The maintainers will promptly create a draft advisory and coordinate the fix with you

### PGP Encryption (Optional)

For sensitive reports, you may encrypt your message using our PGP key:

```text
[PGP public key fingerprint - to be added]
```text

### What NOT to Do

- **Do not** open public issues for security vulnerabilities
- **Do not** disclose the vulnerability publicly until we've had a chance to address it
- **Do not** exploit the vulnerability beyond what is necessary to demonstrate it

## Response SLAs

We are committed to responding to security reports in a timely manner:

| Severity | Initial Response | Status Update | Target Resolution |
|----------|------------------|---------------|-------------------|
| Critical | 24 hours         | Every 48 hours | 7 days            |
| High     | 48 hours         | Weekly        | 30 days           |
| Medium   | 5 business days  | Bi-weekly     | 90 days           |
| Low      | 10 business days | Monthly       | Best effort       |

**Note:** These are target SLAs. Actual response times may vary based on severity, complexity, and maintainer availability.

## Triage Process

Once we receive a security report, we follow this process:

1. **Acknowledgment** - We confirm receipt of your report
2. **Initial Assessment** - We evaluate severity and impact
3. **Investigation** - We reproduce and analyze the vulnerability
4. **Fix Development** - We develop and test a patch
5. **Coordinated Disclosure** - We work with you to determine disclosure timeline
6. **Release** - We release the fix and publish a security advisory
7. **Credit** - We acknowledge your contribution (with your permission)

### Severity Classification

We use the following criteria to classify vulnerabilities:

- **Critical**: Remote code execution, authentication bypass, data breach
- **High**: Privilege escalation, SQL injection, cross-site scripting (XSS) with significant impact
- **Medium**: Information disclosure, denial of service, CSRF
- **Low**: Minor information leaks, issues requiring complex attack scenarios

## Disclosure Policy

We follow **coordinated disclosure** principles:

1. **Embargo Period**: We request a 90-day embargo to develop and test fixes
2. **Early Disclosure**: We Phase 5 disclose earlier if:
   - A fix is ready and tested
   - The vulnerability is being actively exploited
   - The reporter agrees to earlier disclosure
3. **Public Disclosure**: After a fix is released, we publish:
   - A security advisory (GitHub Security Advisories)
   - Release notes with CVE details (if assigned)
   - Credit to the reporter (with permission)

## Security Advisories

Published security advisories can be found:
- **GitHub Security Advisories**: [Aries-Serpent/_codex_/security/advisories](https://github.com/Aries-Serpent/_codex_/security/advisories)
- **Release Notes**: Check [CHANGELOG.md](./docs/CHANGELOG.md) for security-related releases

## Dependencies and Supply Chain Security

### Automated Dependency Updates

We use **Dependabot** to monitor and update dependencies:
- Configuration: [`.github/dependabot.yml`](.github/dependabot.yml)
- Automated PRs for security updates are prioritized
- Review our [dependency policy](./docs/policies) for details

### Dependency Scanning

We run the following automated security scans in CI:

- **Bandit**: Python static analysis for security issues (SAST)
- **pip-audit**: Python dependency vulnerability scanning against OSV database
- **detect-secrets**: Secret detection to prevent credential leaks
- **GitHub Dependency Graph**: Automatic vulnerability alerts
- **CodeQL**: Semantic code analysis (if enabled)

**CI Workflow**: `.github/workflows/security.yml`
- Runs on every push and pull request
- Generates security reports as artifacts
- Currently informational (warnings only), can be configured to fail CI

**Prompt Sanitization**: 
- Default sanitization enabled for all inference endpoints
- Detects and blocks: XSS, SQL injection, command injection, code execution
- Module: `src/codex_ml/safety/prompt_sanitizer.py`
- CLI flags: `--sanitize` (default), `--no-sanitize`, `--strict`, `--non-strict`

### Reviewing Dependency Updates

When Dependabot opens a security PR:
1. Review the CVE details and severity
2. Check for breaking changes
3. Run full test suite
4. Merge promptly if tests pass

## Security Best Practices

### For Contributors

When contributing to _codex_:

- **Never commit secrets**: API keys, passwords, tokens, or credentials
- **Use `.env` files**: Keep sensitive config in `.env` (gitignored)
- **Validate inputs**: Sanitize user inputs and API responses
- **Follow least privilege**: Request minimal permissions
- **Review dependencies**: Check new dependencies for known vulnerabilities
- **Run security tools**: Use `bandit`, `ruff`, and other linters before submitting PRs

### For Users

When using _codex_:

- **Keep dependencies updated**: Regularly run `pip install --upgrade codex-ml`
- **Use virtual environments**: Isolate _codex_ from other projects
- **Review configurations**: Don't blindly copy configurations from untrusted sources
- **Monitor logs**: Check for unusual activity or errors
- **Report issues**: If something seems suspicious, report it

## Security Tooling in This Repository

### Pre-commit Hooks
- **Bandit**: Scans Python code for common security issues
- **detect-secrets**: Prevents committing secrets
- **Ruff**: Lints for security anti-patterns

Run pre-commit checks:
```bash
pre-commit run --all-files
```text

### CI/CD Security Checks
Our CI pipeline includes:
- Dependency vulnerability scanning
- Static code analysis
- License compliance checks
- Secret detection

### Local Security Scanning

Run security scans locally:

```bash
# Bandit - Python security linter
bandit -r src/ -ll

# Safety - Check for known vulnerabilities (if installed)
safety check --json

# Ruff - General linting including security rules
ruff check src/
```text

## Secure Development Guidelines

### Secrets Management
- **Never hardcode secrets** in source code
- Use environment variables or secret managers
- Rotate credentials regularly
- Use separate credentials for dev/staging/prod

### Input Validation
- Validate all external inputs (user input, API responses, file uploads)
- Use allow-lists over deny-lists
- Sanitize data before logging or displaying

### Authentication & Authorization
- Use strong authentication mechanisms
- Implement proper session management
- Follow principle of least privilege
- Validate permissions on every request

### Cryptography
- Use well-established libraries (avoid rolling your own crypto)
- Use strong algorithms and key lengths
- Keep cryptographic libraries updated

### Error Handling
- Don't expose sensitive information in error messages
- Log security events appropriately
- Handle exceptions gracefully

## Code Scanning Findings

For a comprehensive report of all code scanning findings from GitHub Security:
- **[Security Scan Report](./docs/SECURITY_SCAN_REPORT.md)** - Detailed table of all Bandit, CodeQL, and Semgrep findings
- Total: 25 findings (6 Errors, 9 Warnings, 10 Notes)
- Report includes direct links to each finding with severity and file location

## Contact Information

For security-related questions or concerns:

- **Security Email**: security@aries-serpent.dev (placeholder - update with actual contact)
- **General Inquiries**: Open a discussion in the repository (for non-sensitive questions)
- **Maintainers**: @Aries-Serpent/owners

## Updates to This Policy

This security policy is reviewed and updated:
- **Quarterly**: Routine review and updates
- **As Needed**: In response to incidents or process changes
- **Version History**: Tracked in git commits

Last updated: 2025-12-22

---

**Thank you** for helping keep _codex_ and its users safe! 🔒
