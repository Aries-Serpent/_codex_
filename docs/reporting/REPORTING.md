# Codex Reporting

This guide documents how to generate audit trend reports and dashboards from the
trend database produced by the audit pipeline.

## Inputs

* **Trend database**: SQLite file created by the audit pipeline
  (default: `audit_artifacts/trends.db`).
* **Branch filter** (optional): limit report data to a specific branch.

## Outputs

* **JSON/YAML report payloads** containing metadata plus summary, detail, or
  trend sections.
* **HTML dashboard** rendered from the trend payload.
* **PDF** (optional) rendered from the HTML dashboard if the PDF dependency is
  installed.

## Commands

Generate a JSON summary report:

```bash
codex-report --format json --type summary --output reports/summary.json
```

Generate a YAML trend report:

```bash
codex-report --format yaml --type trend --output reports/trend.yaml
```

Generate an HTML report (dashboard view):

```bash
codex-report --format html --output reports/dashboard.html
```

Generate the interactive dashboard directly:

```bash
codex-dashboard --output reports/dashboard.html
```

Filter to a specific branch and custom DB path:

```bash
codex-report --format json --type detail \
  --db-path audit_artifacts/trends.db \
  --branch main \
  --output reports/detail.json
```

## Optional PDF Output

PDF generation requires an additional dependency:

```bash
pip install weasyprint
codex-report --format pdf --output reports/report.pdf
```

If the dependency is missing, the CLI will exit with a clear error explaining
how to install it.

## Implementation Status

**Current Phase**: Phase 3 (Stub Implementation)

The `codex-report` and `codex-dashboard` commands are currently stubs that output
placeholder messages. Full reporting functionality will be implemented in Phase 3
of the project roadmap.

### Planned Features

- Quality score trends over time
- Code smell metrics and visualizations  
- Complexity charts and heat maps
- File-level drill-down capabilities
- Interactive HTML dashboards
- Export to JSON, YAML, HTML, and PDF formats

### Related Scripts

The following existing scripts provide partial reporting functionality:

- `scripts/generate_audit_dashboard.py` - Legacy audit dashboard generator
- `scripts/space_traversal/trend_dashboard.py` - Trend analysis dashboard
- `scripts/status/render_html_report.py` - HTML status report renderer

These scripts will be integrated into the unified `codex-report` and 
`codex-dashboard` commands in Phase 3.
