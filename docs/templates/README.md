# Operational Templates Index

This directory centralizes reusable templates that codify common operational rituals for the `_codex_` program. Each template provides consistent metadata, phase-based execution guidance, and `{{placeholder}}` markers so teams can adapt the workflow to their engagement.

## Available templates

| Template | Purpose | Primary Focus |
| --- | --- | --- |
| [Migration — Python File Relocation](./Migration_PythonFileRelocation.md) | Guides module/package moves while safeguarding import stability, release hygiene, and observability hooks. | Codebase topology and release readiness |
| [Migration — CLI Hardening](./Migration_CLIHardening.md) | Details a phased approach for validating command-line interfaces, tightening argument contracts, and coordinating rollouts. | Developer ergonomics and operational resilience |
| [Planning — Intent Validation](./Planning_IntentValidation.md) | Establishes a structured planning ritual to align stakeholders, scope unknowns, and schedule validation gates. | Discovery, stakeholder alignment, and risk framing |
| [Manual Verification Checklist](./verification.md) | Supplies options for verifying artifacts (SQLite, DuckDB, Datasette Lite) during reviews or rollback drills. | Snapshot validation |

## How to use these templates

1. Identify the template that matches your scenario and duplicate it into your workstream docs.
2. Fill in every `{{placeholder}}` with project-specific data. Keep the YAML front matter intact so downstream tooling renders metadata panels correctly.
3. Cross-link related templates—e.g., pair a migration template with the intent validation planner—to give reviewers full visibility into risk, rollback, and validation coverage.
4. After executing the phases, update referenced runbooks or guides so canonical documentation reflects the latest state.
