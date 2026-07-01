# Archived Documentation

This directory contains deprecated, archived, and phase-specific documentation that is no longer actively maintained but preserved for historical context.

## Contents

### Sessions
Documents in `sessions/` are archived Copilot session reports, exploration logs, and phase-specific execution documentation. These are preserved for historical reference and are not part of the active documentation governance.

## Policy

- Files in this directory are NOT included in documentation coverage validation
- Archived docs should NOT be modified except for reference/historical accuracy
- Links to archived documentation should be marked with `[ARCHIVED]` indicator
- For questions about archived content, refer to the GOVERNANCE_AUDIT reports

## Archived Categories

- **Session Reports**: Copilot coding session documentation and completion reports
- **Phase Documentation**: Phase-specific execution plans, completion reports, and validation summaries
- **Deprecation Notices**: Agent and system deprecation notices with sunset dates
- **Generated Reports**: Build artifacts and generated analysis reports

## Migration

To restore an archived document to active maintenance:

1. Move the file back to its original location
2. Update GOVERNANCE_AUDIT_20260701.json to re-classify it
3. Add to machine-readable-coverage-report.json covered_files
4. Update mkdocs.yml if it's a public-facing document
5. Create a PR with the changes

Generated on: 2026-07-01
Authority: unified-doc-agent governance audit
