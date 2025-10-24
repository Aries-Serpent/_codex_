# Operational Templates Index

Welcome to the `_codex_` operational template catalog. The templates in this folder capture repeatable flows that contributors can follow end-to-end. Each entry includes a ready-to-run execution blueprint, customization guidance, and explicit validation checkpoints so the maintainer reviewing the work can trust that the same results will be reproduced.

## How to Use the Templates

1. **Choose the template** that matches your task category (migration, hardening, or intent planning).
2. **Duplicate the template** into your working note, replacing each `[PLACEHOLDER: ...]` marker with project-specific details.
3. **Review the validation gates** section to understand the tests, hooks, and documentation updates you must provide before opening a pull request.
4. **Share the filled template** with a maintainer for approval. Our execution model is role-gated: developers draft, maintainers validate and execute.
5. **Archive the completed template** with the implementation artefacts so future contributors can audit decisions and reuse the pattern.

| Template | Primary Use Case | Key Outputs | Linked Resources |
| --- | --- | --- | --- |
| [Migration – Python File Relocation](./Migration_PythonFileRelocation.md) | Move Python modules while preserving history and API stability | Execution phases, sys.modules alias recipe, rollback strategy | [`sitecustomize.py`](../sitecustomize.py), [`legacy_root/`](../..), [`tests/conftest.py`](../../tests/conftest.py) |
| [Migration – CLI Hardening](./Migration_CLIHardening.md) | Harden CLI behaviour, update dependencies, and push coverage above 85% | Coverage roadmap, failure triage, release checklist | [`src/cli/`](../../src/cli/), [`tests/cli/`](../../tests/cli/), [`pyproject.toml`](../../pyproject.toml) |
| [Planning – Intent Validation](./Planning_IntentValidation.md) | Structure discovery and approval work before implementation begins | Intent worksheet, risk ledger, approval gate | [`docs/validation/`](../validation/), [`conftest.py`](../../conftest.py), [`sitecustomize.py`](../sitecustomize.py) |

## When to Reach for Each Template

### Migration – Python File Relocation
Use this template whenever you need to move Python files across packages, split modules, or consolidate duplicated logic while keeping downstream imports working. The plan includes git-history preservation notes and shows how to wire compatibility shims through `sitecustomize.py`.

### Migration – CLI Hardening
Choose this option when the CLI surface needs behavioural improvements, new validation hooks, or coverage uplift. The template documents the hardening phases, recommended pytest markers, and linters to enable in CI.

### Planning – Intent Validation
Start here before kicking off complex work. It provides an approval-ready plan with explicit fields for assumptions, questions, risks, and decision gates so maintainers can sign off quickly.

## Frequently Asked Questions

- **Can I mix templates?** Yes. Start with the planning template, then run the relevant migration or hardening blueprint.
- **How do I update a template?** Increment the version number in the metadata, document the change in `docs/CHANGELOG.md`, and communicate the update in the contributor channel.
- **Where do I add new templates?** Create a new markdown file in this folder, update this index, and add discovery tests under `tests/templates/`.

---
Last updated: 2025-10-24
