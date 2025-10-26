# Documentation Index

Welcome to the `_codex_` documentation hub.

## Prompts
- **Self-Healing Disciplined Engineer — Gap Card Sweep**  
  See: [docs/prompts/custom_gpt_self_healing_engineer.md](./prompts/custom_gpt_self_healing_engineer.md)

## 📋 Operational Templates
Operational templates encode recurring delivery rituals so teams can execute migrations, hardening passes, and planning checkpoints with consistent safeguards. Begin with the [Operational Templates index](./templates/README.md) to review prerequisites, placeholders, and cross-references before copying a template into your service.

### Quick Links
- [Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)
- [Migration — CLI Hardening](./templates/Migration_CLIHardening.md)
- [Planning — Intent Validation](./templates/Planning_IntentValidation.md)

Each template includes role guidance (developers draft → maintainers execute), `[PLACEHOLDER: …]` prompts, and success criteria aligned with the 85% coverage standard. See [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#using-operational-templates) for drafting and review expectations.

## Conventions
- Keep docs small and composable.
- Use a single fenced `diff` block for proposed patches in prompts/guides.
- Prefer citations to live repo files when referencing code or config.

## Related
- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-25
