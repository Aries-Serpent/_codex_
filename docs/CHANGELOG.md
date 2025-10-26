# Changelog
All notable changes to this project will be documented in this file.

The format follows “Keep a Changelog” and maintains an **Unreleased** section for in-flight work.

## [Unreleased]

### Added
- **Operational templates (v1.0.0):** Introduced Python File Relocation, CLI Hardening, and Intent Validation templates under `docs/templates/` with a navigation index.
  - Files: `docs/templates/Migration_PythonFileRelocation.md`, `docs/templates/Migration_CLIHardening.md`, `docs/templates/Planning_IntentValidation.md`, `docs/templates/README.md`
  - Include role-gated workflows, `[PLACEHOLDER: …]` customization prompts, and cross-references to runtime shims (`sitecustomize.py`), CLI modules, and pytest suites.
- **Documentation:** Updated `docs/README.md` with an "Operational Templates" section and refreshed `docs/CONTRIBUTING.md` to outline template adoption responsibilities.
- **Tests:** Added `tests/templates/test_template_discovery.py` and `tests/templates/test_template_structure.py` to verify template presence, metadata, and required sections.

### Changed
- Reinforced coverage expectations (≥85%) across templates and contribution guidance.

---
2025-10-25
