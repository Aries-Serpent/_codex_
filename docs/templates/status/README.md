# Status Update Templates

This directory contains the canonical templates and schemas for `_codex_` daily status updates.

## Files

### Templates
- **codex_status_template_v1.1.md** - The main template for daily status reports
  - Comprehensive structure for repo audits
  - Includes snapshot, delta tracking, patch diffs, automation hooks
  - Supports dynamic capability discovery and reproducibility tracking

### Schemas
- **codex_status_template.schema_v1.2.json** - Enhanced JSON Schema with 40+ new fields (v1.2)
- **codex_status_template.schema.json** - JSON Schema for validation (v1.1)
- **codex_status_template.schema.yaml** - YAML Schema (same structure as JSON, v1.1)
- **SCHEMA_ENHANCEMENTS_v1.2.md** - Detailed documentation of v1.2 enhancements

### Guides
- **authoring_guide_v1.1.md** - Instructions for creating status reports
  - Explains cadence, storage, scoring rubric
  - Details how to use dynamic capabilities and reproducibility registry
  
- **diff_style_guide_v1.1.md** - Standards for atomic patch diffs
  - Mandatory elements per patch
  - Canonical diff fences format
  - Chunking and sequencing guidance

## Usage

### Creating a Daily Status Report

1. Copy the template:
   ```bash
   cp docs/templates/status/codex_status_template_v1.1.md reports/daily/$(date +%Y-%m-%d).md
   ```

2. Fill in all sections following the authoring guide

3. Validate against schema (if using automation):
   ```bash
   # Using a JSON schema validator
   jsonschema -i your_report.json codex_status_template.schema.json
   ```

### Report Location

Daily reports are stored in:
- **Location**: `reports/daily/<YYYY-MM-DD>.md`
- **Retention**: Keep last 30 reports
- **Archive**: Optional zip/tar.gz for reports > 90 days old

## Template Version

Current version: **v1.2** (Recommended)
Previous version: **v1.1** (Still supported)

### Version History
- **v1.2** (2025-11-02):
  - Enhanced with repository-specific context (git, environment)
  - 40+ new structured fields for automation
  - Cross-referencing system with structured IDs (CAP-XXX, FIND-XXX, PATCH-XXX, REPRO-XXX, Q-XXX, DEC-XXX, DEFER-XXX)
  - ML Test Score framework integration
  - Hydra config snapshot
  - Enhanced tokenization insights
  - Nox session tracking
  - MLflow offline integration
  - Comprehensive delta tracking
  - **See `SCHEMA_ENHANCEMENTS_v1.2.md` for full details**
  
- **v1.1** (2025-11-02): 
  - Dynamic Capability Audit with Extended Catalog
  - Reproducibility Registry for extensible controls
  - Schemas updated to allow additional properties and tagging
  
- **v1.0** (2025-11-02): 
  - Initial release with full snapshot, delta tracking
  - Severity/Confidence scoring (1-5)
  - Atomic patch diffs with validation checklists
  - Automation hooks and tokenization insights

## Semver Rules

- **Patch (v1.1.x)**: Clarifications, minor optional field additions
- **Minor (v1.x.0)**: New optional sections/fields, no breaking changes
- **Major (vX.0.0)**: Structural changes, field renames/removals, breaking changes

## Key Features

### Dynamic Capability Tracking
- Core Capability Table for well-known areas (Tokenization, Modeling, etc.)
- Extended Capability Catalog for discovered capabilities
- Capability Discovery Log with evidence and rationale

### Reproducibility Registry
- Core controls checklist
- Extensible registry with REPRO-IDs
- Severity/confidence scoring for gaps
- Next audit scheduling

### Atomic Patch Diffs
- Standardized format with Begin/End Patch markers
- Risk and confidence scoring
- Rollback plans and validation checklists
- Links to affected CAP-IDs and REPRO-IDs

### Automation Support
- Issue/PR ingestion (no truncation)
- Coverage reporting
- Dependency audits
- Security scans
- Performance snapshots
- Capability auto-discovery

### Security
- Secret-masking guidance throughout
- Redaction patterns for sensitive data
- Safe handling of credentials and tokens

## Contributing

When updating templates:
1. Update version number according to semver rules
2. Update template CHANGELOG
3. Align JSON/YAML schemas with template changes
4. Update authoring guide if structure changes
5. Test with validation tools
