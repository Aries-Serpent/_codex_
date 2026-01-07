# Archive Standardization Framework

> **Status**: Phase 2 | **Effective**: Previous Cycle-11-02 | **Version**: 1.0

## Executive Overview

The standardization framework elevates the _codex_ archive system from baseline production implementation to industry-aligned, fully auditable methodology framework aligned with SLSA L3, in-toto, and SAA standards while maintaining complete **backward compatibility** with v1 records.

## Standardization Pillars

### 1. Schema Versioning (v1 → v2)

**Objective**: Enable schema evolution without breaking existing deployments

**Implementation Details**:

| Aspect | Detail |
|--------|--------|
| **Version Field** | Explicit `schemaVersion` in every record |
| **Coexistence** | v1 and v2 records can coexist indefinitely |
| **Auto-Detection** | System automatically detects record version |
| **Migration** | Optional, non-breaking upgrade path |

**Example v2 Record**:
```json
{
  "ts": "Previous Cycle-11-02T19:44:00Z",
  "action": "ARCHIVE",
  "actor": "marc",
  "tombstone": "d3e8729-...",
  "sha256": "e3b0c442...",
  "schemaVersion": "2.0",
  "standardizationMetadata": {
    "slsa_level": "L3",
    "signature": "MEUCIQDx...",
    "issuer": "https://token.actions.githubusercontent.com"
  }
}
```text

### 2. Cryptographic Signing (Sigstore Keyless)

**Objective**: Achieve SLSA L3 cryptographic identity binding

**Technology Stack**:

| Component | Purpose | Details |
|-----------|---------|---------|
| **GitHub OIDC** | Ephemeral identity | Token provided by GitHub Actions |
| **Sigstore Fulcio** | Certificate authority | Issues short-lived X.509 certificates |
| **Sigstore Rekor** | Transparency log | Records all signatures publicly |
| **cosign** | Signing/verification tool | CLI interface for operations |

**Identity Flow**:
```text
GitHub Actions Job
  ↓ (id-token permission)
GitHub OIDC Provider
  ↓ (SIGSTORE_ID_TOKEN)
_codex_ archive store()
  ↓ (calls Fulcio)
Ephemeral Certificate
  ↓ (signs evidence record)
Signature + Certificate
  ↓ (uploaded to Rekor)
Transparency Log Entry
```text
### 3. Schema Validation

**Objective**: Ensure all records conform to their declared schema version

**Validation Process**:

1. **On Write**: Record validated against target schema before appending to JSONL
2. **On Read**: Record validated before use (cached validators for performance)
3. **On Migrate**: Both source and target schemas validated during v1→v2 migration

**Tool**: `EvidenceSchemaValidator` class

### 4. Standardization Metadata

**Objective**: Track compliance and enable auditing

**Metadata Fields**:

```python
StandardizationMetadata(
    schema_version: str = "2.0",                      # v2 identifier
    slsa_level: str = "L3",                           # SLSA compliance
    signature: Optional[str] = None,                  # Sigstore signature
    certificate_chain: Optional[list[str]] = None,    # Fulcio certs
    issuer: Optional[str] = None,                     # OIDC issuer
    signed_at: Optional[str] = None,                  # Signature timestamp
    in_toto_attestation_id: Optional[str] = None,     # Link metadata (Phase 2+)
    merkle_proof: Optional[Dict[str, Any]] = None     # Tree proof (Phase 3+)
)
```text

## Standardization Guarantees

| Guarantee | Implementation | Verification |
|-----------|---|---|
| **Append-Only** | JSONL write-mode `"a"` | `ls -l` file size only increases |
| **Immutable Records** | No rewrites to existing JSONL lines | Git history + evidence hash |
| **Cryptographic Identity** | Sigstore OIDC + Fulcio | Signature + certificate chain |
| **Tamper Detection** | SHA256 digests + signatures | Automatic via PR checklist |
| **Backward Compatibility** | v1 records valid as-is | Parser handles both versions |

## Configuration

### Environment Variables

```bash
# Enable standardization (default: false for backward compatibility)
export CODEX_STANDARDIZATION_ENABLED=true

# Enable signing (default: false, true in GitHub Actions)
export CODEX_ENABLE_SIGNING=true

# GitHub OIDC token (auto-provided in GitHub Actions)
export SIGSTORE_ID_TOKEN=$(gh auth token)

# Custom schema directory (default: ./schemas)
export CODEX_SCHEMA_DIR=/path/to/schemas
```text

### GitHub Actions Integration

```yaml
permissions:
  id-token: write  # ← REQUIRED for OIDC token
  contents: read

steps:
  - name: Archive with standardization
    env:
      CODEX_STANDARDIZATION_ENABLED: "true"
      CODEX_ENABLE_SIGNING: "true"
    run: python -m codex.cli archive store _codex_ file.py --reason "test" --by "${{ github.actor }}"
```text

## Compliance Mapping

### SLSA L3 Alignment

| SLSA Requirement | _codex_ Implementation | Evidence |
|---|---|---|
| **Provenance exists** | ✅ Evidence records created | `.codex/evidence/archive_ops.jsonl` |
| **Provenance signed** | ✅ Sigstore keyless signature | `standardizationMetadata.signature` |
| **Signed by service account** | ✅ GitHub OIDC identity | `standardizationMetadata.issuer` |
| **Ephemeral credentials** | ✅ Short-lived Fulcio cert | Certificate chain in Rekor |
| **Tamper protection** | ✅ Append-only + immutable | JSONL format + git history |

### in-toto Framework Readiness

| in-toto Component | _codex_ Support | Status |
|---|---|---|
| **Layout** | Canonically defined in policy doc | ✅ Phase 2 |
| **Link Metadata** | Structure compatible | ✅ Phase 2 (optional field) |
| **Step Authorization** | Via OIDC claims + CODEOWNERS | ✅ Phase 2 |
| **Verification** | Automated checklist | ✅ Phase 2 |

## Migration & Deployment

### For Existing Deployments

**Option 1: No Action Required**
- v1 records remain fully valid
- New archives default to v2 (with standardization disabled for backward compat)
- Coexistence indefinite

**Option 2: Gradual Transition**
- Enable `CODEX_STANDARDIZATION_ENABLED=true` in CI/CD
- All new archives use v2 with metadata
- Old v1 records still valid for queries
- Use `codex archive migrate-evidence-to-v2` for batch upgrade (optional)

**Option 3: Immediate Migration**
- Run database migration scripts
- Execute `codex archive migrate-evidence-to-v2`
- Enable signing in GitHub Actions workflows

### Rollback Procedure

If issues arise:

1. **Disable standardization**:
   ```bash
   export CODEX_STANDARDIZATION_ENABLED=false
   ```

2. **Revert database migrations** (if applied):
   ```bash
   # SQLite: No explicit rollback needed (columns optional)
   # Postgres/MariaDB: Use `ALTER TABLE DROP COLUMN` if necessary
   ```

3. **Restore from backup**:
   ```bash
   cp .codex/evidence/archive_ops.jsonl.backup .codex/evidence/archive_ops.jsonl
   ```

## Validation & Testing

### Pre-Deployment Checks

```bash
# Validate standardization setup
python -m codex.cli archive show-standardization-status

# Run tests
pytest tests/archive/test_standardization.py -v

# Validate evidence log
python -m codex.cli archive validate-standardization \
  --check-schema-version \
  --check-signatures
```text

### Post-Deployment Verification

```bash
# Verify new archives have standardization
tail -1 .codex/evidence/archive_ops.jsonl | python -m json.tool | grep schemaVersion
# Should output: "schemaVersion": "2.0"

# Verify signatures (if enabled)
tail -1 .codex/evidence/archive_ops.jsonl | python -m json.tool | grep -A 3 standardizationMetadata
# Should show signature field
```text

## CLI Commands

### Show Standardization Status

```bash
python -m codex.cli archive show-standardization-status

# Output:
# ============================================================
# 📋 Archive Standardization Status
# ============================================================
# Standard Version: 2.0
# SLSA Level: L3
# Signing Enabled: ✅ Yes
# Schema Versions Supported: 1.0, 2.0
#
# Compliance:
#   ✅ SLSA_L3
#   ✅ IN_TOTO_READY
#   ✅ SAA_COMPLIANT
```text

### Validate Evidence Records

```bash
# Validate schema versions
python -m codex.cli archive validate-standardization --check-schema-version

# Validate signatures
python -m codex.cli archive validate-standardization --check-signatures

# Attempt repair (migrate v1→v2)
python -m codex.cli archive validate-standardization --check-schema-version --repair
```text

### Migrate to v2 Schema

```bash
# Interactive migration with confirmation
python -m codex.cli archive migrate-evidence-to-v2

# Output:
# ⚠️  This will modify .codex/evidence/archive_ops.jsonl. Continue? [y/N]: y
# 🔄 Starting migration v1 → v2...
# 📦 Backed up original to: .codex/evidence/archive_ops.jsonl.backup
# ✅ Migration complete: 1234 records converted
#    v1 records: 0
#    v2 records: 1234
```text

## FAQ

**Q: Will v1 records break?**  
A: No. v1 records remain fully supported and valid.

**Q: Can I disable signing?**  
A: Yes, via `CODEX_ENABLE_SIGNING=false`, but SLSA L3 requires signing.

**Q: What if Sigstore is unavailable?**  
A: Archives will fail if signing enabled but Sigstore unreachable. Fallback to `CODEX_ENABLE_SIGNING=false` for continuity.

**Q: Can I verify signatures offline?**  
A: No—signature verification requires Rekor transparency log access.

**Q: Will standardization impact performance?**  
A: Minor overhead (~5-10%) for signing operations, negligible for reads.

**Q: How do I verify backward compatibility?**  
A: Run the test suite: `pytest tests/archive/test_standardization.py::TestBackwardCompatibility`

## References

- [Sigstore Documentation](https://docs.sigstore.dev/)
- [SLSA Framework](https://slsa.dev/)
- [in-toto Project](https://in-toto.io/)
- [GitHub OIDC Tokens](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/about-security-hardening-with-openid-connect)
- [JSON Schema](https://json-schema.org/)

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Previous Cycle-11-02 | Initial Phase 2 standardization framework |
