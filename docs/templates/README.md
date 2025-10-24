# Operational Templates Index

This directory collects reusable templates that codify common operational rituals for the `_codex_` program. Each document includes metadata, phase-based execution guidance, and placeholders so teams can adapt the template to their specific engagement.

## Available templates

- [Migration — Python File Relocation](./Migration_PythonFileRelocation.md): Aligns stakeholders on how to move or consolidate Python modules while maintaining import stability, release hygiene, and reproducibility checkpoints.
- [Migration — CLI Hardening](./Migration_CLIHardening.md): Defines a phased approach for validating command-line interfaces, tightening argument contracts, and coordinating rollouts across developer environments.
- [Planning — Intent Validation](./Planning_IntentValidation.md): Provides a structured planning ritual for confirming business intent, scoping unknowns, and scheduling validation gates before implementation work begins.
- [Manual Verification Checklist](./verification.md): Walkthrough for validating snapshot artifacts using SQLite, DuckDB, or Datasette Lite.

## How to use these templates

1. Pick the template that matches your scenario and duplicate it into your workstream docs.
2. Fill in the `{{placeholder}}` markers with project-specific details. Keep the YAML metadata block intact so MkDocs renders the front-matter panels.
3. Cross-link related templates (e.g., pair a migration template with the intent validation planner) to give reviewers a full picture of risk, rollback, and test coverage.
4. Update any referenced runbooks or guides after executing the phases to keep our documentation canonically synced.
