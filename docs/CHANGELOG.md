# Changelog

All notable changes to this project will be documented in this file.

## 2025-10-26

### Added
- **Operational templates (v1.0.0):** Introduced Python File Relocation, CLI Hardening, and Intent Validation templates under `docs/templates/` with a navigation index.
  - Files: `docs/templates/Migration_PythonFileRelocation.md`, `docs/templates/Migration_CLIHardening.md`, `docs/templates/Planning_IntentValidation.md`, `docs/templates/README.md`
  - Include role-gated workflows, `[PLACEHOLDER: …]` customization prompts, and cross-references to runtime shims (`sitecustomize.py`), CLI modules, and pytest suites.
- **Documentation:** Extended `docs/README.md` with usage triggers and a handoff checklist for the templates, and refreshed `docs/CONTRIBUTING.md` with a role-based workflow plus a task-to-template mapping table.
- **Tests:** Added `tests/templates/test_template_discovery.py` and `tests/templates/test_template_structure.py` to verify template presence, metadata, and required sections.

### Notes
- No GitHub Actions were created or modified.
- Hooks are **local-only** and optional to run in CI.

## 2025-10-26 (Self-management)

### Added
- Local status reporter:
  - `tools/status_report.py` to run gates and emit `STATUS_REPORT.md`.
  - Docs in `docs/ops/status_reports.md` and template in `docs/templates/status_update.md`.
  - Manual pre-commit hook `codex-status`.
  - Tests under `tests/status/`.

### Enhanced
- **`tools/status_report.py`**
  - Added `--template` rich rendering, local repo scan heuristics, and capability table support.
  - Added `--verbose` to embed stdout/stderr and `--save-logs` to persist tool output under `.codex/status/`.
  - Report footer now notes saved artifacts when applicable.
- **Documentation**
  - Expanded `docs/ops/status_reports.md` with verbose/artifact usage details.
  - README quickstart now calls out offline-first setup and status reporting flags.

### Fix
- **Evaluator DX:** emit a friendly installation hint when optional dependencies such as `pydantic` or `typer` are missing.

### Added
- `requirements-dev.txt` with local dev tools.
- `noxfile.py` sessions: `gates`, `tests`, `precommit`.
- Updated `docs/ops/local_gates.md` and added ADR for self-management.

---
2025-10-25
