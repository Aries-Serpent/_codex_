# Changelog
All notable changes to this project will be documented in this file.

The format is based on “Keep a Changelog” and uses an **Unreleased** section to collect upcoming changes.

## [Unreleased]

### Added
- **Operational templates:** Migration — Python File Relocation, Migration — CLI Hardening, and Planning — Intent Validation now
  live under `docs/templates/` with a README index for quick discovery.
  - Files: `docs/templates/Migration_PythonFileRelocation.md`, `docs/templates/Migration_CLIHardening.md`,
    `docs/templates/Planning_IntentValidation.md`, `docs/templates/README.md`
  - Provide phase-based guidance, placeholder callouts, and cross-linking tips for reuse across services.
- **Prompt:** Self-Healing Disciplined Engineer — Gap Card Sweep
  File: `docs/prompts/custom_gpt_self_healing_engineer.md`
  - Introduces “Gap Card” sweep on each user request
  - Enforces single-`diff` fence output, WHY/Risk/Rollback/Tests
  - Zero-trust retrieval posture; read-only connector usage

### Changed
- Refreshed `docs/README.md` and `docs/CONTRIBUTING.md` to index the new operational templates and clarify how contributors
  adopt them while preserving test coverage expectations.

### Refactored
- Consolidated eight legacy CLI scripts into the `cli/` package, preserving
  history via `git mv` and registering console entry points (`codex-setup`,
  `codex-patch-runner`, `codex-update-runner`, `codex-script`, `codex-workflow`,
  `codex-task-sequence`, `codex-ast-upgrade`, `codex-audit-runner`).
  Packaging metadata now includes the `cli` package and ships the directory in
  sdists and wheels.

---
2025-10-20
