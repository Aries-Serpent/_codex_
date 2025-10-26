# Documentation Index

Welcome to the `_codex_` documentation hub.

## Prompts
- **Self-Healing Disciplined Engineer — Gap Card Sweep**
  See: [docs/prompts/custom_gpt_self_healing_engineer.md](./prompts/custom_gpt_self_healing_engineer.md)

## 📋 Operational Templates
Operational templates encode recurring delivery rituals so teams can execute migrations, hardening passes, and planning checkpoints with consistent safeguards. Begin with the [Operational Templates index](./templates/README.md) to review prerequisites, required metadata, and cross-references before copying a template into your service.

### When to use a template
- You are planning a migration or hardening effort that will cross team boundaries.
- You need an auditable checklist with rollback, communications, and verification steps.
- You want a consistent structure for maintaining ≥85% coverage through scoped test additions.

### Quick Links
- [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./templates/Migration_CLIHardening.md)
- [Planning — Intent Validation](./templates/Planning_IntentValidation.md)

### Handoff checklist
Each template includes role guidance (developers draft → maintainers execute), `[PLACEHOLDER: …]` prompts, and success criteria aligned with the coverage standard. Ensure the following before requesting review:

1. All placeholders are replaced with repo-specific context and linked artifacts.
2. Rollback and communication steps point to real runbooks or dashboards.
3. The template is stored alongside the service codebase (usually under `docs/`) and linked from the change description or PR.

See [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#using-operational-templates) for the full drafting workflow and role expectations.

## Conventions
- Keep docs small and composable.
- Use a single fenced `diff` block for proposed patches in prompts/guides.
- Prefer citations to live repo files when referencing code or config.

## Related
- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-25
