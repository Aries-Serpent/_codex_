# SBOM Regeneration Required After CVE Fixes

**Status:** The sbom/codex-sbom-current.json file contains the pre-upgrade package versions and must be regenerated after dependency updates are installed.

## Current SBOM Package Versions (Pre-Upgrade)
- pip: 24.0 (VULNERABLE)
- jinja2: 3.1.2 (VULNERABLE)
- cryptography: 41.0.7 (VULNERABLE)
- setuptools: 68.1.2 (VULNERABLE)
- requests: 2.31.0 (VULNERABLE)
- urllib3: 2.0.7 (VULNERABLE)
- certifi: 2023.11.17 (VULNERABLE)
- twisted: 24.3.0 (VULNERABLE)
- idna: 3.6 (VULNERABLE)
- configobj: 5.0.8 (VULNERABLE)
- pyasn1: 0.4.8 (VULNERABLE)
- wheel: 0.42.0 (VULNERABLE)

## Post-Deployment SBOM Requirements
After this PR is merged and the environment is refreshed with `pip install -r requirements.txt`:

```bash
# Regenerate SBOM with new package versions
python -m cyclonedx_bom.cli -r requirements.txt -o sbom/codex-sbom-current.json --format json-v1.3

# Commit the updated SBOM
git add sbom/codex-sbom-current.json
git commit -m "chore(sbom): Regenerate SBOM with post-CVE remediation package versions"
```

## Expected SBOM After Regeneration
- pip: 26.1.2+ (SECURE)
- jinja2: 3.1.6+ (SECURE)
- cryptography: 49.0.0+ (SECURE)
- setuptools: 78.1.1+ (SECURE)
- requests: 2.34.2+ (SECURE)
- urllib3: 2.7.0+ (SECURE)
- certifi: 2024.7.4+ (SECURE)
- twisted: 24.7.0+ (SECURE)
- idna: 3.15+ (SECURE)
- configobj: 5.0.9+ (SECURE)
- pyasn1: 0.6.3+ (SECURE)
- wheel: 0.46.2+ (SECURE)

## Timeline
1. ✅ PR Created with security package version updates
2. ✅ Requirements files updated with CVE fixes
3. ⏳ PR Approved & Merged
4. ⏳ Environment refreshed with pip install
5. ⏳ SBOM regenerated post-deployment
6. ⏳ Final SBOM committed to main branch
