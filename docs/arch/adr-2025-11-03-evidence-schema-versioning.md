# ADR-Previous Cycle-11-03: Evidence Record Schema Versioning

**Date**: 2025-11-03  
**Status**: Accepted (Phase 2)  
**Author**: Archive Standardization Team  
**Stakeholders**: Architecture, Data Engineering, Operations  

## Problem Statement

The evidence log (`.codex/evidence/archive_ops.jsonl`) uses a fixed v1 schema. To support standardization enhancements (standardization metadata, cryptographic signatures, future Merkle proofs), we need an evolution strategy that:

- ✅ Enables schema changes without breaking existing deployments
- ✅ Supports coexistence of multiple schema versions
- ✅ Allows automatic migration and validation
- ✅ Maintains append-only guarantees

## Requirements

- Multi-version support (v1, v2, future v3+)
- Backward compatibility indefinitely
- Automatic version detection
- Schema validation at write and read time
- Optional automatic migration
- Zero downtime deployment

## Decision

Implement **explicit schema versioning** with:

1. **Versioning Field**: Add `schemaVersion` to every record
2. **Parallel Support**: v1 and v2 coexist indefinitely
3. **Auto-Detection**: System determines version automatically
4. **Validation**: JSON Schema validation against declared version
5. **Migration**: Optional, non-breaking upgrade path

## Implementation Details

### V1 Schema (Legacy)

```json
{
  "ts": "ISO8601 timestamp",
  "action": "ARCHIVE|RESTORE|REFERENCE|PURGE",
  "actor": "string",
  "tombstone": "UUID",
  "sha256": "hex string",
  "repo": "optional string",
  "path": "optional string",
  "size": "optional integer",
  "commit": "optional string"
}
```text

### V2 Schema (Standardized)

```json
{
  // All v1 fields preserved
  "ts": "...",
  "action": "...",
  "actor": "...",
  
  // NEW: Schema version field
  "schemaVersion": "2.0",
  
  // NEW: Standardization metadata
  "standardizationMetadata": {
    "schema_version": "2.0",
    "slsa_level": "L3",
    "signature": "base64 Sigstore signature",
    "certificate_chain": ["PEM certificates"],
    "issuer": "https://token.actions.githubusercontent.com",
    "signed_at": "ISO8601 timestamp",
    "in_toto_attestation_id": "optional UUID",
    "merkle_proof": "optional object for Phase 3"
  }
}
```text

### Coexistence Strategy

**Unified Evidence Log**:
```text
Line 1: {"ts": "...", "action": "ARCHIVE", ...}                    [v1 record]
Line 2: {"ts": "...", "action": "ARCHIVE", ..., "schemaVersion": "1.0"}  [v1]
Line 3: {"ts": "...", "action": "ARCHIVE", ..., "schemaVersion": "2.0", "standardizationMetadata": {...}}  [v2]
Line N: ...
```text
**Version Detection**:
```python
version = record.get("schemaVersion", auto_detect(record))
# If no explicit version:
#   - Has standardizationMetadata? → v2
#   - Otherwise → v1
```text

## Consequences

### Positive

✅ **Non-Breaking**: v1 records remain valid and queryable  
✅ **Flexible**: Schema changes don't require all-or-nothing migration  
✅ **Auditable**: Version field makes record provenance clear  
✅ **Scalable**: Supports unlimited future schema versions  
✅ **Safe**: Validation catches malformed records early  

### Negative

⚠️ **Parser Complexity**: Code must handle multiple versions  
⚠️ **Storage**: JSONL file slightly larger (repeated `schemaVersion` field)  
⚠️ **Query Complexity**: Queries must account for multiple schemas  

### Mitigation

| Complexity | Solution |
|---|---|
| Parser logic | `EvidenceSchemaValidator` handles version detection and validation |
| Storage growth | Marginal (JSON field names are deduplicated in compression) |
| Query complexity | Typed data models abstract schema differences |

## Validation Approach

### Write-Time Validation

```python
record = create_evidence_record(...)
if standardization_enabled:
    record = standardization_manager.enhance_evidence_record(record)
    # Validates against v2 schema
_evidence_append(record)
```text

### Read-Time Validation

```python
for record in read_evidence_log():
    version = auto_detect_version(record)
    validator.validate(record, version=version)
    # Use record...
```text

### Migration (Optional)

```bash
python -m codex.cli archive migrate-evidence-to-v2
# Converts all v1 → v2, creates backup
```text

## Backward Compatibility Guarantee

All existing v1 records:
- ✅ Remain readable indefinitely
- ✅ Valid for all queries and operations
- ✅ No automatic modification unless explicitly migrated
- ✅ Coexist with v2 records in same log file

## Schema Registry

Store schema definitions in `schemas/` directory:

```text
schemas/
├── archive_evidence_schema_v1.json   [v1 definition]
├── archive_evidence_schema_v2.json   [v2 definition]
└── archive_evidence_schema_v3.json   [future]
```text
Each schema is:
- ✅ JSON Schema (draft-07) compliant
- ✅ Self-documenting (includes descriptions)
- ✅ Versioned in git for audit trail
- ✅ Used for runtime validation

## Timeline

1. **Pre-commit 1-2**: Create schema definitions (v1 + v2)
2. **Pre-commit 3-4**: Implement `EvidenceSchemaValidator`
3. **Pre-commit 5-6**: Integrate into archive operations
4. **Pre-commit 7-8**: Testing + documentation

## Future Considerations

### V3 Schema (Possible Phase 3+)

Could add:
- Merkle tree proof fields
- in-toto link metadata references
- SBOM/CycloneDX fields
- Additional compliance metadata

All without breaking v1 or v2 records.

## Approval

- [ ] Architecture Lead
- [ ] Data Engineering Lead
- [ ] Operations Lead

## References

- [JSON Schema Specification](https://json-schema.org/)
- [Schema Evolution Best Practices](https://martin.kleppmann.com/2012/12/05/schema-evolution-in-avro-protocol-buffers-thrift.html)
