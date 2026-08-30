# per-iteration Status Reports

This directory contains per-iteration status update reports generated using the `_codex_` status template.

## Purpose

per-iteration reports provide:
- Complete snapshot of repository state
- Delta tracking from previous reports
- High-signal findings with severity/confidence scoring
- Atomic patch diffs ready for implementation
- Automation data (issues, PRs, coverage, security scans)
- Reproducibility and capability tracking

## File Naming Convention

Reports follow this naming pattern:
- **Format**: `YYYY-MM-DD.md`
- **Example**: `2025-11-02.md`

## Report Structure

Each report is generated from the template at `docs/templates/status/codex_status_template_v1.1.md` and includes:

1. **Metadata** - Title, timestamp, version, authors
2. **Executive Summary** - Health status, top findings, key deltas
3. **Full Snapshot** - Repo map, capabilities, findings, tests, reproducibility
4. **Delta** - Changes since last report
5. **Atomic Patches** - Implementation-ready diffs with rollback plans
6. **Automation Data** - Issues, PRs, coverage, security, performance
7. **Tokenization Insights** - Current state and recommendations
8. **Questions & Decisions** - Managed Q&A and decision log

## Retention Policy

- **Keep**: Last 30 reports (rolling window)
- **Archive**: Reports older than 90 iterations (optional zip/tar.gz)
- **Location**: This directory (`reports/per-iteration/`)

## Creating a New Report

1. Copy the template:
   ```bash
   cp docs/templates/status/codex_status_template_v1.1.md reports/per-iteration/$(date +%Y-%m-%d).md
   ```

2. Follow the authoring guide:
   - `docs/templates/status/authoring_guide_v1.1.md`

3. Use the diff style guide for patches:
   - `docs/templates/status/diff_style_guide_v1.1.md`

## Validation

Reports can be validated against the schemas:
- JSON Schema: `docs/templates/status/codex_status_template.schema.json`
- YAML Schema: `docs/templates/status/codex_status_template.schema.yaml`

## Prior Reports Reference

Each report should reference the previous report in its metadata:
```markdown
- Prior Report Reference:
  - Path: reports/per-iteration/YYYY-MM-DD.md
```text

This enables delta tracking and historical analysis.

## See Also

- Template documentation: `docs/templates/status/README.md`
- Authoring guide: `docs/templates/status/authoring_guide_v1.1.md`
- Diff style guide: `docs/templates/status/diff_style_guide_v1.1.md`
