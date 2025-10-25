# Documentation Index

Welcome to the `_codex_` documentation hub.

## Prompts

- **Self-Healing Disciplined Engineer — Gap Card Sweep**
  See: [docs/prompts/custom_gpt_self_healing_engineer.md](./prompts/custom_gpt_self_healing_engineer.md)

## Operational Templates

Refer to the [Operational Templates index](./templates/README.md) for detailed usage guidance.

- **[Migration — Python File Relocation](./templates/Migration_PythonFileRelocation.md)**: Coordinate module moves while preserving imports and release hygiene.
- **[Migration — CLI Hardening](./templates/Migration_CLIHardening.md)**: Stage interface tightening, argument validation, and rollout checks.
- **[Planning — Intent Validation](./templates/Planning_IntentValidation.md)**: Structure discovery work to confirm intent, risks, and validation gates before execution.

## Conventions

- Keep docs small and composable.
- Use a single fenced `diff` block for proposed patches in prompts/guides.
- Prefer citations to live repo files when referencing code or config.

## Related

- Project audit ritual: see `AUDIT_PROMPT.md`
- CHANGELOG practices follow “Keep a Changelog” with an **Unreleased** section at the top.

---
Last updated: 2025-10-20
