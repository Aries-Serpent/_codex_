# Archive Standardization Guide

> **Generated**: 2025-11-03 | **Author**: Archive Team | **Version**: 1.0

## Table of Contents

1. [Introduction](#introduction)
2. [Getting Started](#getting-started)
3. [Schema Versioning](#schema-versioning)
4. [Cryptographic Signing](#cryptographic-signing)
5. [Validation & Verification](#validation--verification)
6. [Migration Guide](#migration-guide)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Introduction

Archive standardization brings **SLSA L3 compliance**, **cryptographic integrity**, and **schema versioning** to the _codex_ archive system while maintaining **100% backward compatibility**.

### What You Get

✅ **SLSA L3 Compliance** - Industry-standard supply chain security  
✅ **Schema Versioning** - Explicit v1/v2 format support  
✅ **Cryptographic Signatures** - Keyless signing via Sigstore  
✅ **Backward Compatibility** - Existing v1 records work unchanged  
✅ **Audit-Ready** - Compliance mapping and verification tools  

### Prerequisites

- Python 3.10+
- `jsonschema` package (for schema validation)
- `sigstore` package (optional, for production signing)
- GitHub Actions (optional, for OIDC-based signing)

---

## Getting Started

### 1. Check Current Status

```bash
# Display standardization status
python -m codex.cli archive show-standardization-status
```text

**Expected Output**:
```text
============================================================
📋 Archive Standardization Status
============================================================
Standard Version: 2.0
SLSA Level: L3
Signing Enabled: ❌ No
Schema Versions Supported: 1.0, 2.0

Compliance:
  ✅ SLSA_L3
  ✅ IN_TOTO_READY
  ✅ SAA_COMPLIANT
```text
### 2. Enable Standardization

**Local Development** (no signing):
```bash
export CODEX_STANDARDIZATION_ENABLED=true
export CODEX_ENABLE_SIGNING=false
```text

**GitHub Actions** (with signing):
```yaml
env:
  CODEX_STANDARDIZATION_ENABLED: "true"
  CODEX_ENABLE_SIGNING: "true"
```text

### 3. Validate Evidence Log

```bash
# Validate schema versions
python -m codex.cli archive validate-standardization --check-schema-version

# Validate signatures (if enabled)
python -m codex.cli archive validate-standardization --check-signatures
```text

---

## Schema Versioning

### v1 vs. v2 Schemas

**v1 (Legacy)**:
```json
{
  "ts": "2025-11-03T00:00:00Z",
  "action": "ARCHIVE",
  "actor": "user",
  "tombstone": "uuid",
  "sha256": "hash"
}
```text

**v2 (Standardized)**:
```json
{
  "ts": "2025-11-03T00:00:00Z",
  "action": "ARCHIVE",
  "actor": "user",
  "tombstone": "uuid",
  "sha256": "hash",
  "schemaVersion": "2.0",
  "standardizationMetadata": {
    "slsa_level": "L3",
    "signature": "...",
    "issuer": "https://token.actions.githubusercontent.com"
  }
}
```text

### Auto-Detection

The system automatically detects record versions:

```python
from codex.archive.evidence_schema import EvidenceSchemaValidator

validator = EvidenceSchemaValidator()
record = {"ts": "...", "action": "ARCHIVE", ...}

version = validator.auto_detect_version(record)
# Returns "1.0" if no schemaVersion field or standardizationMetadata
# Returns "2.0" if schemaVersion="2.0" or standardizationMetadata present
```text

### Coexistence

Both v1 and v2 records can exist in the same evidence log:

```text
.codex/evidence/archive_ops.jsonl:
  Line 1: {"ts": "...", ...}                                    [v1]
  Line 2: {"ts": "...", "schemaVersion": "2.0", ...}            [v2]
  Line 3: {"ts": "...", ...}                                    [v1]
  Line N: {"ts": "...", "schemaVersion": "2.0", ...}            [v2]
```text
---

## Cryptographic Signing

### Local Development (Mock Signing)

```python
from codex.archive.standardization import StandardizationManager

# Create manager with signing disabled
manager = StandardizationManager(enable_signing=False)

record = {
    "ts": "2025-11-03T00:00:00Z",
    "action": "ARCHIVE",
    "actor": "developer",
    "tombstone": "uuid",
    "sha256": "hash"
}

# Enhance without signature
enhanced = manager.enhance_evidence_record(record, "developer", sign_now=False)
```text

### GitHub Actions (Production Signing)

**Workflow Configuration**:
```yaml
name: Archive with Signing

on: [push]

jobs:
  archive:
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # ← REQUIRED for OIDC
      contents: read
    
    steps:
      - uses: actions/checkout@v4
      
      - name: Archive with signing
        env:
          CODEX_ENABLE_SIGNING: "true"
          SIGSTORE_ID_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python -m codex.cli archive store _codex_ file.py \
            --reason "cleanup" \
            --by "${{ github.actor }}"
```text

**Signing Flow**:
```text
GitHub Actions Job
  ↓ (OIDC token via id-token permission)
Sigstore Fulcio
  ↓ (ephemeral certificate)
Evidence Record Signing
  ↓ (signature + cert chain)
Rekor Transparency Log
  ↓ (public verification)
Evidence Log (.codex/evidence/archive_ops.jsonl)
```text
---

## Validation & Verification

### Command-Line Validation

**Check Schema Compliance**:
```bash
python -m codex.cli archive validate-standardization --check-schema-version
```text

**Check Signatures** (if signing enabled):
```bash
python -m codex.cli archive validate-standardization --check-signatures
```text

**Combined Check**:
```bash
python -m codex.cli archive validate-standardization \
  --check-schema-version \
  --check-signatures
```text

### Programmatic Validation

```python
from codex.archive.standardization import StandardizationManager
from codex.archive.evidence_schema import EvidenceSchemaValidator

manager = StandardizationManager(enable_signing=False)
validator = EvidenceSchemaValidator()

# Validate a record
record = {...}  # Your evidence record

# Check schema
version = validator.auto_detect_version(record)
is_valid = validator.validate(record, version=version)

# Check standardization
result = manager.verify_standardization(record)
print(f"Valid: {result['valid']}")
print(f"Schema version: {result['schema_version']}")
print(f"Details: {result['verification_details']}")
```text

### Expected Outputs

**Success**:
```text
📊 Validation Results: 1234 records scanned
   ✅ Valid: 1234
   ⚠️  Warnings: 0
   ❌ Errors: 0

✅ All checks passed!
```text
**With Issues**:
```text
📊 Validation Results: 1234 records scanned
   ✅ Valid: 1230
   ⚠️  Warnings: 2
   ❌ Errors: 2

⚠️  Warnings:
   Line 100: Signature verification failed

❌ Errors:
   Line 50: Schema error: 'schemaVersion' is required
   Line 75: Invalid JSON: Expecting ',' delimiter
```text
---

## Migration Guide

### When to Migrate

Migrate to v2 if you:
- Want explicit schema versioning
- Need SLSA L3 compliance
- Plan to enable cryptographic signing
- Want future-proof evidence records

**Note**: Migration is **optional**. v1 records remain fully valid.

### Migration Process

**1. Backup Existing Evidence**:
```bash
cp .codex/evidence/archive_ops.jsonl .codex/evidence/archive_ops.jsonl.$(date +%Y%m%d).bak
```text

**2. Run Migration**:
```bash
python -m codex.cli archive migrate-evidence-to-v2
```text

**Interactive Prompt**:
```text
⚠️  This will modify .codex/evidence/archive_ops.jsonl. Continue? [y/N]: y
🔄 Starting migration v1 → v2...
📦 Backed up original to: .codex/evidence/archive_ops.jsonl.backup
✅ Migration complete: 1234 records converted
   v1 records: 0
   v2 records: 1234
```text
**3. Verify Migration**:
```bash
python -m codex.cli archive validate-standardization --check-schema-version
```text

**4. Check Sample Records**:
```bash
# Should show v2 format with schemaVersion
tail -5 .codex/evidence/archive_ops.jsonl | python -m json.tool
```text

### Rollback

If migration fails or causes issues:

```bash
# Restore from backup
mv .codex/evidence/archive_ops.jsonl.backup .codex/evidence/archive_ops.jsonl

# Verify restoration
python -m codex.cli archive validate-standardization --check-schema-version
```text

---

## Troubleshooting

### Issue: Schema validation fails

**Symptom**:
```text
❌ Line 50: Schema error: 'sha256' is a required property
```text
**Solution**:
1. Check record has all required fields: `ts`, `action`, `actor`, `tombstone`, `sha256`
2. For v2 records, ensure `schemaVersion` field present
3. Run with `--repair` to attempt automatic fix:
   ```bash
   python -m codex.cli archive validate-standardization --check-schema-version --repair
   ```

### Issue: Module not found

**Symptom**:
```text
❌ Standardization module not available
```text
**Solution**:
```bash
# Ensure standardization modules exist
ls -la src/codex/archive/standardization.py
ls -la src/codex/archive/evidence_schema.py

# Reinstall if needed
pip install -e .
```text

### Issue: Signing fails in GitHub Actions

**Symptom**:
```text
RuntimeError: Cannot obtain OIDC token
```text
**Solution**:
1. Check workflow has correct permissions:
   ```yaml
   permissions:
     id-token: write  # ← Must be present
     contents: read
   ```

2. Verify environment variable:
   ```yaml
   env:
     CODEX_ENABLE_SIGNING: "true"
   ```

3. Check Sigstore availability:
   ```bash
   curl -I https://fulcio.sigstore.dev
   curl -I https://rekor.sigstore.dev
   ```

### Issue: Performance degradation

**Symptom**:
Archive operations significantly slower after enabling standardization.

**Solution**:
1. Check if signing is enabled (adds ~5-10ms per operation):
   ```bash
   python -m codex.cli archive show-standardization-status
   ```

2. Disable signing for development:
   ```bash
   export CODEX_ENABLE_SIGNING=false
   ```

3. Monitor with benchmarks:
   ```python
   import time
   start = time.time()
   # ... archive operation ...
   elapsed = time.time() - start
   print(f"Operation took {elapsed*1000:.2f}ms")
   ```

---

## Best Practices

### 1. Version Control

✅ **DO**: Commit evidence log changes with meaningful messages
```bash
git add .codex/evidence/archive_ops.jsonl
git commit -m "Archive legacy module per retention policy"
```text

❌ **DON'T**: Manually edit evidence log
```bash
# Never do this:
vim .codex/evidence/archive_ops.jsonl
```text

### 2. Schema Version Selection

✅ **DO**: Use v2 for new deployments
```bash
export CODEX_STANDARDIZATION_ENABLED=true
```text

✅ **DO**: Keep v1 for existing deployments (backward compatible)
```bash
# No action required - v1 works as-is
```text

❌ **DON'T**: Mix standardization settings across environments
```bash
# Avoid:
# Dev: CODEX_STANDARDIZATION_ENABLED=true
# Prod: CODEX_STANDARDIZATION_ENABLED=false
```text

### 3. Signing Strategy

✅ **DO**: Enable signing in production (GitHub Actions)
```yaml
permissions:
  id-token: write
env:
  CODEX_ENABLE_SIGNING: "true"
```text

✅ **DO**: Disable signing in development (faster iteration)
```bash
export CODEX_ENABLE_SIGNING=false
```text

❌ **DON'T**: Enable signing without OIDC setup
```bash
# Will fail:
CODEX_ENABLE_SIGNING=true python -m codex.cli archive store ...
# (unless SIGSTORE_ID_TOKEN provided)
```text

### 4. Validation Frequency

✅ **DO**: Validate in CI/CD pipelines
```yaml
steps:
  - name: Validate archive standardization
    run: |
      python -m codex.cli archive validate-standardization \
        --check-schema-version \
        --check-signatures
```text

✅ **DO**: Validate before major migrations
```bash
python -m codex.cli archive validate-standardization --check-schema-version
```text

❌ **DON'T**: Skip validation after schema changes
```bash
# Always validate after updates to standardization code
```text

### 5. Evidence Log Maintenance

✅ **DO**: Keep evidence log in version control
```bash
git add .codex/evidence/archive_ops.jsonl
```text

✅ **DO**: Monitor evidence log size
```bash
ls -lh .codex/evidence/archive_ops.jsonl
```text

✅ **DO**: Backup before migrations
```bash
cp .codex/evidence/archive_ops.jsonl{,.backup}
```text

---

## Quick Reference

### Commands

```bash
# Status
python -m codex.cli archive show-standardization-status

# Validate schema
python -m codex.cli archive validate-standardization --check-schema-version

# Validate signatures
python -m codex.cli archive validate-standardization --check-signatures

# Migrate v1 → v2
python -m codex.cli archive migrate-evidence-to-v2
```text

### Environment Variables

```bash
CODEX_STANDARDIZATION_ENABLED=true   # Enable standardization
CODEX_ENABLE_SIGNING=true            # Enable cryptographic signing
CODEX_SCHEMA_DIR=./schemas           # Schema directory
SIGSTORE_ID_TOKEN=$(gh auth token)   # OIDC token (GitHub Actions)
```text

### File Locations

```text
.codex/evidence/archive_ops.jsonl              # Evidence log
schemas/archive_evidence_schema_v1.json        # v1 schema
schemas/archive_evidence_schema_v2.json        # v2 schema
src/codex/archive/standardization.py           # Standardization manager
src/codex/archive/evidence_schema.py           # Schema validator
```text
---

## Additional Resources

- **Framework Guide**: `docs/arch/_archive-policy/standardization-framework.md`
- **Sigstore Setup**: `docs/arch/_archive-policy/README-standardization.md`
- **Standards Mapping**: `docs/compliance/archive_standards_mapping.md`
- **ADRs**: `docs/arch/adr-Previous Cycle-11-*.md`

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review ADRs for architectural decisions
3. Run diagnostic: `python -m codex.cli archive show-standardization-status`
4. Validate evidence: `python -m codex.cli archive validate-standardization`

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-11-03 | Initial comprehensive guide for Phase 2 |
