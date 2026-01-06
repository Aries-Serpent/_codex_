# Archive Standards Mapping

> **Generated**: Previous Cycle-11-03 | **Author**: Archive Standardization Team | **Version**: 1.0

## Overview

This document maps the _codex_ archive standardization implementation to industry standards: SLSA, in-toto, and Software Artifact Attestation (SAA).

---

## SLSA (Supply-chain Levels for Software Artifacts)

### Level 3 Requirements Mapping

| SLSA L3 Requirement | _codex_ Implementation | Evidence Location |
|---------------------|------------------------|-------------------|
| **Provenance exists** | ✅ Evidence records created for all operations | `.codex/evidence/archive_ops.jsonl` |
| **Provenance is authentic** | ✅ Cryptographic signatures via Sigstore | `standardizationMetadata.signature` |
| **Provenance completeness** | ✅ All required fields captured | `schemaVersion: "2.0"` records |
| **Hermetic builds** | ✅ Archive operations isolated, deterministic | Archive DAL + blob storage |
| **Ephemeral credentials** | ✅ GitHub OIDC tokens (short-lived) | Fulcio certificates |
| **Signed provenance** | ✅ Keyless signing via Sigstore | Certificate chain in metadata |
| **Non-falsifiable provenance** | ✅ Append-only JSONL + signatures | Immutable evidence log |
| **Dependency completeness** | ⏳ Phase 3 (SBOM) | Future: SBOM generation |

### Implementation Details

**Provenance Generation**:
```python
# Every archive operation creates signed provenance
from codex.archive.standardization import StandardizationManager

manager = StandardizationManager(enable_signing=True)
evidence_record = {
    "ts": "Previous Cycle-11-03T00:00:00Z",
    "action": "ARCHIVE",
    "actor": "user@example.com",
    "tombstone": "uuid",
    "sha256": "content_hash"
}

# Enhance with SLSA L3 metadata
enhanced = manager.enhance_evidence_record(evidence_record, "user@example.com")
# Result includes signature, certificate chain, OIDC issuer
```text

**Verification**:
```bash
# Verify SLSA L3 compliance
python -m codex.cli archive validate-standardization --check-signatures --check-schema-version
```text

---

## in-toto Framework

### Link Metadata Compatibility

| in-toto Component | _codex_ Implementation | Status |
|-------------------|------------------------|--------|
| **Layout** | Defined in canonical policy | ✅ Complete |
| **Link Metadata** | Evidence records structure | ✅ Compatible |
| **Step Definition** | Archive operations (store/restore/purge) | ✅ Defined |
| **Functionary Keys** | GitHub OIDC identity | ✅ Implemented |
| **Inspection** | Validation commands | ✅ Available |
| **Verification** | Automated PR checklist | ✅ Active |

### Step Mapping

**Archive Step (store)**:
```json
{
  "name": "archive",
  "expected_materials": [
    ["MATCH", "src/**/*.py", "WITH", "PRODUCTS", "FROM", "checkout"]
  ],
  "expected_products": [
    ["CREATE", ".codex/evidence/archive_ops.jsonl"]
  ],
  "pubkeys": ["<GitHub OIDC>"]
}
```text

**Restore Step**:
```json
{
  "name": "restore",
  "expected_materials": [
    ["MATCH", ".codex/evidence/archive_ops.jsonl", "IN", "archive"]
  ],
  "expected_products": [
    ["CREATE", "restored/**/*"]
  ],
  "pubkeys": ["<GitHub OIDC>"]
}
```text

### Future in-toto Integration (Phase 3)

```python
# Optional: Generate in-toto link metadata
from codex.archive.in_toto_integration import generate_link_metadata

link = generate_link_metadata(
    step_name="archive",
    materials={"src/file.py": "sha256:..."},
    products={".codex/evidence/archive_ops.jsonl": "sha256:..."},
    command=["codex", "archive", "store"],
    return_value=0
)
# Store link metadata reference in standardizationMetadata.in_toto_attestation_id
```text

---

## Software Artifact Attestation (SAA)

### Attestation Requirements

| SAA Requirement | _codex_ Implementation | Compliance |
|-----------------|------------------------|------------|
| **Artifact Identity** | SHA256 hash + UUID tombstone | ✅ Yes |
| **Actor Identity** | GitHub OIDC claims | ✅ Yes |
| **Timestamp** | UTC ISO8601 | ✅ Yes |
| **Operation Type** | ARCHIVE/RESTORE/REFERENCE/PURGE | ✅ Yes |
| **Provenance** | Evidence record + signature | ✅ Yes |
| **Retention Policy** | Documented in policy | ✅ Yes |
| **Access Control** | CODEOWNERS + dual-control | ✅ Yes |
| **Audit Trail** | Immutable JSONL log | ✅ Yes |

### Attestation Format

**v2 Evidence Record** (SAA-compliant):
```json
{
  "ts": "Previous Cycle-11-03T00:00:00Z",
  "action": "ARCHIVE",
  "actor": "user@example.com",
  "repo": "_codex_",
  "path": "src/module.py",
  "tombstone": "d3e8729-1234-5678-abcd-ef0123456789",
  "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "size": 4096,
  "commit": "abc123def456",
  "schemaVersion": "2.0",
  "standardizationMetadata": {
    "schema_version": "2.0",
    "slsa_level": "L3",
    "signature": "MOCK_SIG_abc123...",
    "certificate_chain": ["-----BEGIN CERTIFICATE-----..."],
    "issuer": "https://token.actions.githubusercontent.com",
    "signed_at": "Previous Cycle-11-03T00:00:01Z"
  }
}
```text

### Compliance Verification

```bash
# Generate compliance report
python << 'EOF'
from codex.archive.standardization import StandardizationManager

manager = StandardizationManager(enable_signing=False)
report = manager.get_standardization_report()

print("=== SAA Compliance Report ===")
print(f"SLSA Level: {report['slsa_level']}")
print(f"Signing: {'Enabled' if report['signing_enabled'] else 'Disabled'}")
print(f"Schema Versions: {report['schema_versions_supported']}")
print("\nCompliance Status:")
for standard, status in report['compliance'].items():
    print(f"  {standard}: {'✅' if status else '❌'}")
EOF
```text

---

## Compliance Matrix

### Overall Standards Alignment

| Standard | Requirement | Implementation | Evidence | Status |
|----------|-------------|----------------|----------|--------|
| **SLSA L3** | Signed provenance | Sigstore keyless | `standardizationMetadata.signature` | ✅ |
| **SLSA L3** | Hermetic process | Isolated archive ops | DAL + blob storage | ✅ |
| **SLSA L3** | Non-falsifiable | Append-only log | JSONL format | ✅ |
| **in-toto** | Link metadata | Compatible structure | Evidence records | ✅ |
| **in-toto** | Layout definition | Policy document | `canonical-archiving-policy.md` | ✅ |
| **in-toto** | Functionary auth | GitHub OIDC | OIDC token → Fulcio cert | ✅ |
| **SAA** | Artifact identity | SHA256 + tombstone | `sha256` + `tombstone` fields | ✅ |
| **SAA** | Actor identity | OIDC claims | `actor` + `issuer` fields | ✅ |
| **SAA** | Audit trail | Immutable log | `.codex/evidence/archive_ops.jsonl` | ✅ |
| **SAA** | Retention policy | Documented | `docs/ops/retention.md` | ✅ |

---

## Audit Procedures

### For External Auditors

**1. Verify Evidence Log Integrity**:
```bash
# Check file exists and is append-only
ls -la .codex/evidence/archive_ops.jsonl

# Verify no modifications (git history)
git log --follow .codex/evidence/archive_ops.jsonl
```text

**2. Validate Signatures**:
```bash
# Run signature verification
python -m codex.cli archive validate-standardization --check-signatures
```text

**3. Check Schema Compliance**:
```bash
# Verify all records match declared schema version
python -m codex.cli archive validate-standardization --check-schema-version
```text

**4. Review Standardization Status**:
```bash
# Display compliance report
python -m codex.cli archive show-standardization-status
```text

**5. Examine Sample Records**:
```bash
# View recent evidence records
tail -10 .codex/evidence/archive_ops.jsonl | python -m json.tool
```text

### Expected Audit Outputs

**Clean Run**:
```text
📊 Validation Results: 1234 records scanned
   ✅ Valid: 1234
   ⚠️  Warnings: 0
   ❌ Errors: 0

✅ All checks passed!
```text
**Standardization Status**:
```text
============================================================
📋 Archive Standardization Status
============================================================
Standard Version: 2.0
SLSA Level: L3
Signing Enabled: ✅ Yes
Schema Versions Supported: 1.0, 2.0

Compliance:
  ✅ SLSA_L3
  ✅ IN_TOTO_READY
  ✅ SAA_COMPLIANT
```text
---

## References

- [SLSA Framework](https://slsa.dev/)
- [in-toto Specification](https://in-toto.io/)
- [Sigstore Documentation](https://docs.sigstore.dev/)
- [Software Artifact Attestation Best Practices](https://github.com/in-toto/attestation)

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Previous Cycle-11-03 | Initial standards mapping for Phase 2 |
