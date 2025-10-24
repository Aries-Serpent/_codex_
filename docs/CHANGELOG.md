# Changelog
All notable changes to this project will be documented in this file.

The format is based on “Keep a Changelog” and uses an **Unreleased** section to collect upcoming changes.

## [Unreleased]

### Added
- **Prompt:** Self-Healing Disciplined Engineer — Gap Card Sweep
  File: `docs/prompts/custom_gpt_self_healing_engineer.md`
  - Introduces “Gap Card” sweep on each user request
  - Enforces single-`diff` fence output, WHY/Risk/Rollback/Tests
  - Zero-trust retrieval posture; read-only connector usage
- **Docs:** Operational templates catalog and supporting tests
  - Added template index at `docs/templates/README.md`
  - Added migration templates for Python file relocation and CLI hardening (v1.0.0)
  - Added intent validation planning template (v1.0.0)
  - Introduced `tests/templates/` discovery suite and new `CONTRIBUTING.md`

### Refactored
- Consolidated eight legacy CLI scripts into the `cli/` package, preserving
  history via `git mv` and registering console entry points (`codex-setup`,
  `codex-patch-runner`, `codex-update-runner`, `codex-script`, `codex-workflow`,
  `codex-task-sequence`, `codex-ast-upgrade`, `codex-audit-runner`).
  Packaging metadata now includes the `cli` package and ships the directory in
  sdists and wheels.

---
2025-10-20
