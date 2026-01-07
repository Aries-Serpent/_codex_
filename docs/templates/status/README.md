# Status Update Templates

This directory contains the canonical templates and schemas for `_codex_` daily status updates.

## Files

### Templates
- **codex_status_template_v1.2.md** - Enhanced template with schema validation and audit integrity (v1.2) **[RECOMMENDED]**
  - All v1.1 features plus schema validation, security input validation, and audit integrity chains
  - Structured tracking for git context, environment, ML Test Scores, Hydra configs
  - Integrated with validation tooling (`tools/validate_configs.py`, `src/codex_ml/cli/validate.py`)

- **codex_status_template_v1.1.md** - Original comprehensive template (v1.1)
  - Full structure for repo audits with snapshot, delta tracking, patch diffs
  - Dynamic capability discovery and reproducibility tracking
  - Still supported for backward compatibility

### Schemas
- **codex_status_template.schema_v1.2.json** - Enhanced JSON Schema with 40+ new fields (v1.2) **[RECOMMENDED]**
- **codex_status_template.schema_v1.2.yaml** - YAML Schema for v1.2
- **codex_status_template.schema.json** - JSON Schema for validation (v1.1)
- **codex_status_template.schema.yaml** - YAML Schema (v1.1)
- **SCHEMA_ENHANCEMENTS_v1.2.md** - Detailed documentation of v1.2 enhancements

### Guides
- **authoring_guide_v1.2.md** - Enhanced authoring guide for v1.2 **[RECOMMENDED]**
  - Includes schema validation, security input validation, and audit integrity guidance
  - Documents integration with validation tooling

- **authoring_guide_v1.1.md** - Original authoring guide (v1.1)
  - Cadence, storage, scoring rubric
  - Dynamic capabilities and reproducibility registry

- **diff_style_guide_v1.2.md** - Enhanced diff style guide for v1.2 **[RECOMMENDED]**
  - Schema validation requirements for patches
  - Security code handling guidance

- **diff_style_guide_v1.1.md** - Original diff style guide (v1.1)
  - Mandatory patch elements
  - Canonical diff fences format
  - Chunking and sequencing

## Audit pipeline linkage (single canonical view)

- The capability-audit command path lives in `docs/cli/status_audit.md` and orchestrates `scripts/space_traversal/audit_runner.py` → `status_update_report.py` using these templates/schemas.
- Detectors that populate the capability catalog are documented in `detectors/README.md` and implemented under `scripts/space_traversal/detectors/`.
- Validation helpers (`tools/validate_status_report.py`, `tools/generate_status_update.py`) and tests (`tests/templates/test_status_template.py`, `tests/cli/test_status_audit.py`, `tests/detectors/`) keep the template + pipeline in sync and reproducible.

## Usage

### Creating a Daily Status Report

#### Using v1.2 (Recommended)

1. Copy the v1.2 template:
   ```bash
   cp docs/templates/status/codex_status_template_v1.2.md reports/daily/$(date +%Y-%m-%d).md
   ```

2. Fill in all sections following `authoring_guide_v1.2.md`

3. Run schema validation:
   ```bash
   python tools/validate_configs.py  # Validate Hydra configs
   python tools/validate_status_report.py reports/daily/$(date +%Y-%m-%d).md  # Validate report structure
   ```

4. Validate against JSON schema (if using automation):
   ```bash
   jsonschema -i your_report.json codex_status_template.schema_v1.2.json
   ```

#### Using v1.1 (Legacy)

1. Copy the v1.1 template:
   ```bash
   cp docs/templates/status/codex_status_template_v1.1.md reports/daily/$(date +%Y-%m-%d).md
   ```

2. Fill in all sections following `authoring_guide_v1.1.md`

3. Validate against schema (if using automation):
   ```bash
   jsonschema -i your_report.json codex_status_template.schema.json
   ```

### Canonical capability-audit pipeline (deterministic)

Use the packaged CLI to generate reports and artifacts in one deterministic pass:

```bash
python cli/status_audit.py --output reports --artifacts audit_artifacts
```

- The command shells out to `scripts/space_traversal/audit_runner.py` and `status_update_report.py` for artifact creation and
  templated report rendering.
- For existing artifact re-use, run `python cli/status_audit.py --skip-audit --artifacts audit_artifacts --output reports`.
  When `--skip-audit` is used the CLI now validates `audit_artifacts/capabilities_scored.json` up-front so failures are fast and
  deterministic.
- Detectors referenced by the pipeline live in `scripts/space_traversal/detectors/` and should remain side‑effect free
  (see `detectors/README.md`).

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
  - **Enhanced Template**: Schema validation, audit integrity chains, security input validation
  - **Repository Context**: Git state (branch, commit SHA, dirty flag), environment snapshot
  - **40+ New Fields**: ML Test Score, Hydra configs, structured automation data
  - **Cross-Referencing**: 7 structured ID patterns (CAP/FIND/PATCH/REPRO/Q/Phase 12/DEFER-XXX)
  - **Validation Integration**: `tools/validate_configs.py`, `src/codex_ml/cli/validate.py`
  - **Security Patterns**: SQL injection, XSS, path traversal, JSON injection detection
  - **Audit Integrity**: SHA256 hashing for tamper-evident audit trails
  - **Enhanced Tracking**: Nox sessions, MLflow offline, per-module coverage, determinism tests
  - **See `SCHEMA_ENHANCEMENTS_v1.2.md` for complete details**

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
