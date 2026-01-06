# Security Policy

## Reporting Security Issues

**Do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via GitHub Security Advisories:
1. Navigate to the [Security tab](https://github.com/Aries-Serpent/_codex_/security)
2. Click "Report a vulnerability"
3. Provide detailed information about the vulnerability

We will respond within 48 hours and work with you to understand and address the issue.

## Supported Versions

We release security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| latest (main branch) | :white_check_mark: |
| 0.x.x   | :white_check_mark: |

## Dependency Monitoring & Management

### Automated Security Scanning

We use the following tools to continuously monitor dependencies for security vulnerabilities:

1. **Dependabot** - Automated dependency updates and security alerts
   - Alerts appear in the [Security tab](https://github.com/Aries-Serpent/_codex_/security/dependabot)
   - Auto-merge enabled for patch versions (when CI passes)
   - Manual review required for minor/major version updates

2. **GitHub Security Advisories** - CVE tracking and vulnerability database integration

3. **CodeQL** - Static analysis for security vulnerabilities in code

### Dependency Update Process

#### For Patch Versions (x.x.X)
- Dependabot creates PR automatically
- CI runs full test suite
- If tests pass, auto-merge after 24 hours
- If tests fail, manual investigation required

#### For Minor/Major Versions (x.X.x or X.x.x)
1. Dependabot creates PR with changelog
2. Manual review of breaking changes
3. Update code if needed
4. Run full test suite
5. Merge after approval

### Monthly Security Review

Conducted on the first Monday of each month:

#### Review Checklist
- [ ] Review all open Dependabot alerts
- [ ] Check for new CVEs affecting dependencies
- [ ] Verify transitive dependencies are up-to-date
- [ ] Review security audit logs
- [ ] Update security documentation

#### Alert Triage Process
1. **High/Critical Severity**
   - Address within 48 hours
   - Create emergency fix PR if needed
   - Notify team immediately

2. **Moderate Severity**
   - Address within 1 week
   - Schedule fix in next sprint
   - Document in security audit

3. **Low Severity**
   - Address within 1 month
   - Include in regular maintenance cycle
   - Track in security backlog

### Verifying Patched Vulnerabilities

When Dependabot reports a vulnerability that's already patched:

1. Verify current version in `requirements/lock.txt`
   ```bash
   grep "package-name==" requirements/lock.txt
   ```

2. Check CVE databases for fix version:
   - [National Vulnerability Database (NVD)](https://nvd.nist.gov/)
   - [GitHub Security Advisories](https://github.com/advisories)
   - Package-specific security advisories

3. If current version includes the patch:
   - Document verification in `reports/security_audit.md`
   - Dismiss alert with reason: "Already fixed - using patched version X.Y.Z"
   - Create detailed analysis in `reports/security_analysis_<package>_<date>.md`

4. If update needed:
   - Follow standard dependency update process
   - Run security scans after update
   - Document in security audit

### Example: aiohttp Security Analysis (2026-01-06)

Recent analysis of 8 Dependabot alerts for aiohttp:
- **Current Version:** 3.13.3 (latest, patched)
- **Vulnerabilities:** CVE-2025-69223 (High), CVE-2025-69229 (Moderate), plus 6 others
- **Status:** All patched in current version
- **Action:** Alerts dismissed after verification
- **Documentation:** `reports/security_analysis_aiohttp_2026-01-06.md`

This demonstrates our verification process for transitive dependencies.

## Security Best Practices

### For Contributors

1. **Never commit secrets**
   - Use environment variables for sensitive data
   - Review `.gitignore` to ensure secrets are excluded
   - Use `git-secrets` or similar tools

2. **Keep dependencies updated**
   - Run `pip list --outdated` regularly
   - Review Dependabot PRs promptly
   - Test updates before merging

3. **Follow secure coding practices**
   - Validate all user inputs
   - Use parameterized queries for SQL
   - Sanitize data before output
   - Follow principle of least privilege

4. **Run security scans locally**
   ```bash
   # Bandit SAST scan
   nox -s sec_scan
   
   # Generate SBOM
   nox -s sbom
   
   # Check for known vulnerabilities
   pip-audit
   ```

### For Maintainers

1. **Review security alerts daily**
   - Check GitHub Security tab each morning
   - Triage new alerts within 4 hours
   - Assign severity levels consistently

2. **Maintain security documentation**
   - Update `reports/security_audit.md` monthly
   - Document all security decisions
   - Keep runbooks current

3. **Conduct security reviews**
   - Review all PRs for security implications
   - Require security checklist for major changes
   - Schedule quarterly security audits

4. **Configure Dependabot**
   ```yaml
   # .github/dependabot.yml
   version: 2
   updates:
     - package-ecosystem: "pip"
       directory: "/requirements"
       schedule:
         interval: "weekly"
       open-pull-requests-limit: 10
       labels:
         - "dependencies"
         - "security"
   ```

## Security Tools & Commands

### Vulnerability Scanning
```bash
# Run Bandit security scanner
nox -s sec_scan

# Generate SBOM (Software Bill of Materials)
nox -s sbom

# Check for vulnerabilities in dependencies
pip-audit

# Scan with safety
safety check --file requirements/lock.txt
```

### Dependency Analysis
```bash
# List outdated packages
pip list --outdated

# Show dependency tree
pipdeptree

# Check for conflicts
pip check
```

### Security Testing
```bash
# Run security-focused tests
pytest tests/ -m security

# Check for hardcoded secrets
detect-secrets scan
```

## Incident Response

### If you discover a security vulnerability:

1. **Assess Impact**
   - Determine affected versions
   - Identify potential attack vectors
   - Estimate severity (Low/Moderate/High/Critical)

2. **Contain the Issue**
   - Create private security advisory
   - Develop fix in private repository fork
   - Test fix thoroughly

3. **Coordinate Disclosure**
   - Notify affected users via security advisory
   - Prepare security patch release
   - Coordinate with CVE program if applicable

4. **Release Fix**
   - Release patched version
   - Update SECURITY.md with details
   - Publish security advisory
   - Monitor for issues

5. **Post-Incident Review**
   - Document lessons learned
   - Update security procedures
   - Enhance detection mechanisms

## Contact

For security-related questions or concerns:
- **Security Advisories:** https://github.com/Aries-Serpent/_codex_/security/advisories
- **Dependabot Alerts:** https://github.com/Aries-Serpent/_codex_/security/dependabot
- **General Security:** Open a discussion in the Security category

## Security Acknowledgments

We appreciate the efforts of security researchers who help keep our project secure. Contributors who responsibly disclose security vulnerabilities will be acknowledged in our security advisories (with permission).

## Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)

---

**Last Updated:** 2026-01-06  
**Next Review:** 2026-02-03 (monthly review schedule)
