# Security Policy

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
2. **Early Disclosure**: We may disclose earlier if:
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

We run the following security scans:

- **Bandit**: Python static analysis for security issues
- **Safety**: Python dependency vulnerability scanning (if configured)
- **GitHub Dependency Graph**: Automatic vulnerability alerts
- **CodeQL**: Semantic code analysis (if enabled)

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

Last updated: 2025-11-02

---

**Thank you** for helping keep _codex_ and its users safe! 🔒
