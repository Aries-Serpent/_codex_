# Codex Status Update Generator

This tool generates comprehensive status update reports for the `_codex_` repository following the JSON schema defined in `schemas/codex_status_update.schema.json`.

## Overview

The status update report provides a complete snapshot of the repository state, including:

- **Metadata**: Timestamp, version, git context, environment info
- **Snapshot**: Repository map, capabilities, findings, test gates, reproducibility controls
- **Delta**: Changes since last report
- **Patches**: Proposed changes and their validation
- **Automation**: CI/CD, coverage, security scans
- **Security**: Security findings and mitigations
- **Questions & Decisions**: Open questions and architectural decisions

## Usage

### Direct Script Execution

```bash
# Generate a new status update
python tools/generate_status_update.py

# Output location
.codex/status/_codex_status_update-YYYY-MM-DD.json
```text

### Via CLI Command

```bash
# Using the codex-status-audit CLI
codex-status-audit --generate

# Or via Python module
python -m cli.status_audit --generate
```text

## Output

The tool generates a JSON file with the following structure:

```json
{
  "metadata": {
    "title": "📍 `_codex_` : Status Update 2025-11-10",
    "timestamp_utc": "2025-11-10T23:00:00.000000+00:00",
    "report_version": "1.0.0",
    "template_version": "v1.2",
    "git_context": { ... },
    "environment": { ... }
  },
  "snapshot": {
    "repo_map": "...",
    "capabilities": [ ... ],
    "findings": [ ... ],
    "tests_gates": { ... },
    "repro": { ... }
  },
  "delta": { ... },
  "patches": [ ... ],
  "automation": { ... },
  "security": { ... },
  "questions": [ ... ],
  "decisions": [ ... ]
}
```text

## Capabilities Tracked

The tool automatically discovers and tracks the following capabilities:

1. **Tokenization** - NLP tokenization pipelines
2. **Training Engine** - ML model training infrastructure
3. **Configuration Management** - Hydra-based config system
4. **Evaluation & Metrics** - Model evaluation harness
5. **Logging & Monitoring** - System metrics and telemetry
6. **Security & Safety** - Security controls and safety filters
7. **CI & Testing** - Test infrastructure and quality gates
8. **Documentation** - Documentation and guides

Each capability includes:
- Status (Implemented/Partially Implemented/Stubbed/Missing)
- Artifacts (file paths)
- Gaps and risks
- Severity and confidence scores
- Patch plan and rollback strategy

## Schema Validation

The generated report is automatically validated against the JSON schema:

```bash
# Schema location
schemas/codex_status_update.schema.json

# The tool uses jsonschema for validation
# Install: pip install jsonschema
```text

## Integration

### Pre-commit Hook

Add to `.pre-commit-config.yaml`:

```yaml
- repo: local
  hooks:
    - id: generate-status-update
      name: Generate Status Update
      entry: python tools/generate_status_update.py
      language: python
      pass_filenames: false
      always_run: true
```text

### CI/CD Pipeline

Add to your workflow:

```yaml
- name: Generate Status Update
  run: |
    python tools/generate_status_update.py
    git add .codex/status/_codex_status_update-*.json
```text

## Customization

The tool can be extended by modifying:

- `analyze_capabilities()` - Add more capability checks
- `gather_findings()` - Add more automated findings
- `analyze_tests()` - Enhance test analysis
- `build_repro_registry()` - Add more reproducibility controls

## Dependencies

Required:
- Python 3.10+
- Standard library only (no external dependencies for basic usage)

Optional:
- `jsonschema` - For schema validation
- `pytest` - For test discovery
- `coverage` - For coverage metrics

## Files

- `tools/generate_status_update.py` - Main generator script
- `schemas/codex_status_update.schema.json` - JSON schema definition
- `cli/status_audit.py` - CLI integration
- `.codex/status/` - Output directory for generated reports

## Development

To modify the schema:

1. Edit `schemas/codex_status_update.schema.json`
2. Update `generate_status_update()` in the generator script
3. Run the generator to test
4. Validate output with: `jsonschema -i output.json schema.json`

## Examples

### View Generated Report

```bash
# Pretty-print the JSON
cat .codex/status/_codex_status_update-2025-11-10.json | python -m json.tool

# Extract specific section
cat .codex/status/_codex_status_update-2025-11-10.json | \
  python -c "import json, sys; print(json.dumps(json.load(sys.stdin)['snapshot']['capabilities'], indent=2))"
```text

### Compare Reports

```bash
# Diff two reports
diff <(jq -S . report1.json) <(jq -S . report2.json)
```text

## Troubleshooting

### Schema Validation Errors

If validation fails, check:
1. All required fields are present
2. Enum values match schema constraints
3. Data types are correct (string/number/array/object)

### Missing Capabilities

If capabilities aren't detected:
1. Check that module paths exist
2. Verify file structure matches expected layout
3. Add explicit checks in `analyze_capabilities()`

## License

MIT License - See LICENSE file for details.

## Contact

For questions or issues, please open an issue in the repository.
