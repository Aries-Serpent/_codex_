# AGENTS — Prompts Directory Guidance

> **Updated**: 2025-12-16

## Scope
These instructions apply to all files within `prompts/` and its subdirectories.

## Requirements
- Keep prompts and templates concise, explicit, and action-oriented for AI agents.
- Emphasize the distinction between `VERIFIED`, `INFERRED`, and `UNKNOWN`; require evidence links for `VERIFIED` claims.
- Provide concrete tool/RAG usage guidance and discourage unsupported assumptions.
- Use markdown or YAML that is valid and machine-consumable; avoid trailing whitespace and unrenderable placeholders.
- Do not include secrets or environment-specific credentials.

## Copilot Task Execution Protocol (CTEP)

When creating prompts for task execution, consider using CTEP format:
- Include progress trackers with checkboxes
- Specify codebase audit requirements
- Define completion criteria

See `.github/docs/Copilot_Task_Execution_Protocol.md` for full specification.

## Validation
- For YAML templates, ensure they parse with `yaml.safe_load`.
- For markdown system prompts, include clear section headings and bullet lists for quick retrieval.

## Related Documentation
- [Main AGENTS.md](/AGENTS.md) - Comprehensive operations playbook
- [CTEP Protocol](/.github/docs/Copilot_Task_Execution_Protocol.md) - Task execution protocol
