# Documentation Index

Welcome to the `_codex_` documentation hub.

## Prompts

- **Self-Healing Disciplined Engineer — Gap Card Sweep**
  See: [docs/prompts/custom_gpt_self_healing_engineer.md](./prompts/custom_gpt_self_healing_engineer.md)

## Operational Templates

Operational templates capture repeatable delivery patterns (migrations, hardening passes, investigative sprints) so teams can execute with consistent safeguards. Start with the [Operational Templates index](./templates/README.md) to review prerequisites, placeholders, and rollout checklists before copying a template into a service.

**Template catalog**

- **[Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)** — Coordinate module moves while preserving imports, dependency edges, and release hygiene.
- **[Migration — CLI Hardening](./templates/Migration_CLIHardening.md)** — Stage interface tightening, argument validation, and rollout checks.
- **[Planning — Intent Validation](./templates/Planning_IntentValidation.md)** — Structure discovery work to confirm intent, risks, and validation gates before execution.

Each template ships with inline `[PLACEHOLDER: …]` prompts and linked regression suites. Follow the role workflow in [`docs/CONTRIBUTING.md`](./CONTRIBUTING.md#role-based-template-workflow) to assign drafting, review, and rollout ownership.

## Conventions

- Keep docs small and composable.
- Use a single fenced `diff` block for proposed patches in prompts/guides.
- Prefer citations to live repo files when referencing code or config.

## Related

- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-20
