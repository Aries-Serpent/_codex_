# Supply Chain Security Guide - Aries-Serpent v0.1.0

**Document Type:** Security & Release Engineering Guide  
**Audience:** Release Engineers, DevOps, Security Team  
**Last Updated:** 2026-07-09

## 1. Overview

This document defines secure practices for verifying the integrity and authenticity of Aries-Serpent software supply chain, from source code through release distribution.

## 2. SBOM (Software Bill of Materials)

### 2.1 What is an SBOM?
A Software Bill of Materials (SBOM) is a comprehensive list of all components, libraries, and dependencies included in a software product, including:
- Direct dependencies (explicitly required)
- Transitive dependencies (required by dependencies)
- Version numbers and license information
- Known vulnerabilities and patches

### 2.2 SBOM Generation

**Tools Used:**
- **cyclonedx-bom:** Generate CycloneDX-compliant SBOMs
- **pip:** Extract Python package metadata

**Generation Process:**

```bash
# Install SBOM generation tools
pip install cyclonedx-bom

# Generate SBOM for aries-serpent package
cyclonedx-bom -o aries-serpent-bom.json pyproject.toml

# Generate SBOM in XML format
cyclonedx-bom -o aries-serpent-bom.xml -of xml pyproject.toml

# Include vulnerability information
cyclonedx-bom -o aries-serpent-bom.json \
  --with-vulnerability-data pyproject.toml
```

### 2.3 SBOM Contents

The generated SBOM includes:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.4",
  "version": 1,
  "metadata": {
    "component": {
      "name": "aries-serpent",
      "version": "0.1.0",
      "type": "library",
      "licenses": [
        {
          "license": {
            "id": "MIT"
          }
        }
      ]
    },
    "tools": [
      {
        "vendor": "CycloneDX",
        "name": "cyclonedx-bom",
        "version": "latest"
      }
    ]
  },
  "components": [
    {
      "name": "pydantic",
      "version": "2.4.0",
      "type": "library",
      "licenses": [
        {
          "license": {
            "id": "MIT"
          }
        }
      ],
      "purl": "pkg:pypi/pydantic@2.4.0"
    }
    // ... more components
  ]
}
```

### 2.4 SBOM Distribution

SBOMs are included in release artifacts:

```bash
# Release package contents
aries-serpent-0.1.0-final.tar.gz
├── aries-serpent-0.1.0-final.tar.gz
├── aries-serpent-0.1.0-final.tar.gz.sha256
├── aries-serpent-0.1.0-final.tar.gz.sig
├── aries-serpent-sbom.json        # ✅ SBOM (JSON)
├── aries-serpent-sbom.xml         # ✅ SBOM (XML)
└── docs/release/RELEASE_NOTES.md

# Wheel distribution
aries-serpent-0.1.0-py3-none-any.whl
├── aries-serpent-0.1.0-py3-none-any.whl
├── aries-serpent-0.1.0-py3-none-any.whl.sha256
├── aries-serpent-0.1.0-py3-none-any.whl.sig
├── aries-serpent-sbom.json        # ✅ SBOM (JSON)
└── aries-serpent-sbom.xml         # ✅ SBOM (XML)
```

### 2.5 SBOM Verification

Verify SBOM integrity:

```bash
# Validate SBOM schema
pip install cyclonedx-python
python -c "from cyclonedx.model.bom import Bom; Bom.model_validate(sbom_json)"

# Check for known vulnerabilities
pip-audit --with-vulnerable-check < sbom.json

# Extract component list
jq '.components[] | .name + "@" + .version' aries-serpent-sbom.json
```

## 3. Cryptographic Signatures

### 3.1 GPG Signature Strategy

All official releases are signed with GPG:

```bash
# Sign a release package
gpg --armor --detach-sign aries-serpent-0.1.0-final.tar.gz
# Creates: aries-serpent-0.1.0-final.tar.gz.sig

# Sign wheel distribution
gpg --armor --detach-sign aries-serpent-0.1.0-py3-none-any.whl
# Creates: aries-serpent-0.1.0-py3-none-any.whl.sig
```

### 3.2 Release Manager Public Key

The release manager's public key is published for verification:

```bash
# Location: Repository root
# File: RELEASE_MANAGER_PUBLIC_KEY.gpg
# Fingerprint: [RELEASE_MANAGER_FINGERPRINT]

# Import public key
gpg --import RELEASE_MANAGER_PUBLIC_KEY.gpg

# Verify signature
gpg --verify aries-serpent-0.1.0-final.tar.gz.sig \
    aries-serpent-0.1.0-final.tar.gz
```

### 3.3 Signature Verification in CI/CD

Automated signature verification in GitHub Actions:

```yaml
# .github/workflows/release-verification.yml
name: Verify Release Signatures

on:
  release:
    types: [published]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Import GPG Key
        run: |
          echo "${{ secrets.RELEASE_MANAGER_PUBLIC_KEY }}" | gpg --import
      
      - name: Verify Signature
        run: |
          gpg --verify ${{ github.event.release.tag_name }}.sig \
              ${{ github.event.release.tag_name }}.tar.gz
          
      - name: Verify Checksum
        run: |
          sha256sum -c ${{ github.event.release.tag_name }}.sha256
```

## 4. Checksum Verification

### 4.1 SHA256 Checksums

All release packages include SHA256 checksums:

```bash
# Generate SHA256 checksum
sha256sum aries-serpent-0.1.0-final.tar.gz > aries-serpent-0.1.0-final.tar.gz.sha256

# Contents of .sha256 file
01a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1 aries-serpent-0.1.0-final.tar.gz
```

### 4.2 Checksum Verification

Verify package integrity using SHA256:

```bash
# Verify single file
sha256sum -c aries-serpent-0.1.0-final.tar.gz.sha256

# Batch verification
sha256sum -c release-checksums.txt

# Manual verification
sha256sum aries-serpent-0.1.0-final.tar.gz
# Compare output with published checksum
```

### 4.3 Checksum File Format

```
# release-checksums.txt
01a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0d1 aries-serpent-0.1.0-final.tar.gz
f2e3d4c5b6a7908192f0e1d2c3b4a5968778695a4b3c2d1e0f1a2b3c4d5e6 aries-serpent-0.1.0-final-py3-none-any.whl
7z8y9x0w1v2u3t4s5r6q7p8o9n0m1l2k3j4i5h6g7f8e9d0c1b2a3f4e5d6c7 aries-serpent-sbom.json
```

## 5. Dependency Verification

### 5.1 Dependency Pinning

**Core Dependencies:** Pinned to exact versions
```txt
# requirements.txt (production)
pydantic==2.4.0
hydra-core==1.3.2
cryptography==48.0.0
PyJWT==2.13.0
PyNaCl==1.5.0
pyOpenSSL==26.0.0
requests==2.33.0
urllib3==2.7.0
```

**Development Dependencies:** Flexible versioning
```txt
# requirements-dev.txt
pytest>=7.4.0,<8.0
pytest-cov>=4.1.0
black>=23.7.0
ruff>=0.0.275
```

### 5.2 Dependency Verification Tools

**pip-audit:** Scan for known vulnerabilities
```bash
pip-audit --desc
# Shows: CRITICAL, HIGH, MEDIUM, LOW severity vulnerabilities
```

**safety:** CVE database checker
```bash
safety check --json
# Compares installed packages against known CVE database
```

**pip install --require-hashes:** Enforce checksum verification
```bash
# Installation with hash verification
pip install --require-hashes -r requirements.txt

# Generate hashes
pip freeze | pip-compile --generate-hashes > requirements.txt
```

### 5.3 Transitive Dependency Tree

Visualize all dependencies:

```bash
# Install pipdeptree
pip install pipdeptree

# Show dependency tree
pipdeptree -p aries-serpent

# Export to file
pipdeptree --graph-output png > dependency-tree.png
```

## 6. Build & Release Process

### 6.1 Build Verification

Verify build artifacts before release:

```bash
# 1. Clean build environment
python -m venv clean-env
source clean-env/bin/activate

# 2. Install from source
pip install -e .

# 3. Run security checks
pip-audit --desc
safety check

# 4. Run test suite
pytest --cov=src tests/

# 5. Generate SBOMs
cyclonedx-bom -o aries-serpent-sbom.json pyproject.toml
cyclonedx-bom -o aries-serpent-sbom.xml pyproject.toml

# 6. Build distributions
python -m build

# 7. Sign packages
gpg --armor --detach-sign dist/*.tar.gz
gpg --armor --detach-sign dist/*.whl

# 8. Generate checksums
sha256sum dist/* > dist/checksums.sha256
```

### 6.2 Release Workflow

**Automated Release Process:**

```yaml
# .github/workflows/release.yml
name: Create Release

on:
  push:
    tags:
      - 'v*'

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      
      - name: Build & Sign
        env:
          GPG_SIGNING_KEY: ${{ secrets.GPG_SIGNING_KEY }}
        run: |
          pip install build
          python -m build
          
          # Sign packages
          echo "$GPG_SIGNING_KEY" | gpg --import
          gpg --armor --detach-sign dist/*.tar.gz
          gpg --armor --detach-sign dist/*.whl
          
          # Generate checksums
          sha256sum dist/* > dist/checksums.sha256
      
      - name: Generate SBOMs
        run: |
          pip install cyclonedx-bom
          cyclonedx-bom -o dist/aries-serpent-sbom.json pyproject.toml
          cyclonedx-bom -o dist/aries-serpent-sbom.xml pyproject.toml
      
      - name: Create Release
        uses: actions/create-release@v1
        with:
          tag_name: ${{ github.ref }}
          release_name: Release ${{ github.ref }}
          files: |
            dist/**/*
      
      - name: Publish to PyPI
        env:
          TWINE_USERNAME: __token__
          TWINE_PASSWORD: ${{ secrets.PYPI_TOKEN }}
        run: |
          pip install twine
          twine upload dist/* --skip-existing
```

## 7. Distribution Verification

### 7.1 PyPI Verification

Verify package on PyPI:

```bash
# Check package metadata
curl https://pypi.org/pypi/aries-serpent/0.1.0/json | jq '.info'

# Download and verify
pip download aries-serpent==0.1.0 --no-deps
sha256sum aries-serpent-0.1.0-py3-none-any.whl
# Compare with published checksum
```

### 7.2 Package Installation Verification

Verify installation integrity:

```bash
# Install from PyPI
pip install aries-serpent==0.1.0

# Verify package contents
pip show aries-serpent
pip show -f aries-serpent | grep -E "\.py|\.so"

# Check for expected modules
python -c "import aries_serpent; print(aries_serpent.__version__)"

# Run smoke tests
python -m pytest --co aries-serpent
```

## 8. Incident Response

### 8.1 Compromised Package Response

**If a release package is compromised:**

1. **IMMEDIATE:**
   - Yank package from PyPI: `pip index versions aries-serpent`
   - Remove release from GitHub
   - Notify users via security advisory

2. **INVESTIGATION:**
   - Analyze build logs for unauthorized changes
   - Review access logs for suspicious activity
   - Audit source code for injected code

3. **REMEDIATION:**
   - Identify root cause
   - Fix vulnerabilities in source code
   - Rotate signing keys if compromised
   - Create new release with fixes

4. **COMMUNICATION:**
   - Post security advisory
   - Update users of risk and mitigation
   - Provide remediation steps

### 8.2 Dependency Vulnerability Response

**If a dependency has a critical vulnerability:**

1. **ASSESS:** Determine impact on aries-serpent
2. **UPDATE:** Bump dependency version if patch available
3. **TEST:** Run full test suite with updated dependency
4. **RELEASE:** Create new version of aries-serpent with fix
5. **COMMUNICATE:** Notify users of critical update

## 9. Tools & Resources

### 9.1 SBOM Tools
- **cyclonedx-bom:** Generate CycloneDX SBOMs
- **syft:** Universal SBOM generator (supports multiple formats)
- **SPDX:** Alternative SBOM format

### 9.2 Signature & Verification Tools
- **GPG:** GNU Privacy Guard for signing
- **openssl:** TLS/SSL toolkit
- **pip:** Package installer with hash verification

### 9.3 Dependency Tools
- **pip-audit:** Vulnerability scanner for Python packages
- **safety:** CVE database checker
- **pipdeptree:** Dependency tree visualization
- **pip-compile:** Deterministic dependency pinning

### 9.4 Release Tools
- **twine:** PyPI package uploader
- **build:** PEP 517/518 build tool
- **GitHub Actions:** CI/CD automation

## 10. Compliance & Standards

- **CycloneDX v1.4:** SBOM generation standard
- **SLSA Framework:** Supply chain security level
- **NTIA SBOM Minimum Elements:** Essential SBOM data
- **OpenChain ISO 5230:** License compliance framework
- **NIST Secure Software Development Framework:** SSDF practices

---

**Document Status:** ✅ COMPLETE  
**Next Review:** 2026-10-09 (quarterly)  
**Owner:** Release Engineering / Security Team
