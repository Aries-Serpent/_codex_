# Contributing Guide

Thank you for improving `_codex_`. This document highlights the workflow for using the operational templates and the expectations for role-gated execution.

## Using Operational Templates

We maintain reusable templates under `docs/templates/` to streamline migrations, CLI hardening, and planning work.

| Scenario | Template | Primary Author | Reviewer |
| --- | --- | --- | --- |
| Moving Python modules while keeping imports stable | [Migration – Python File Relocation](docs/templates/Migration_PythonFileRelocation.md) | Developer | Maintainer |
| Increasing CLI robustness and coverage | [Migration – CLI Hardening](docs/templates/Migration_CLIHardening.md) | Developer | Maintainer |
| Capturing intent, risks, and validation before implementation | [Planning – Intent Validation](docs/templates/Planning_IntentValidation.md) | Developer | Maintainer |

### Workflow

1. **Developer drafts** the relevant template, replacing each `[PLACEHOLDER: ...]` marker with project context.
2. **Maintainer reviews** the draft, confirms validation gates, and approves the plan.
3. **Developer executes** the agreed steps, committing code and documentation changes.
4. **Maintainer validates** results, ensuring coverage thresholds and documentation updates are met.
5. **Team archives** the completed template with the associated pull request for future reference.

### Customization Example

```markdown
Intent: Replace legacy CLI auth flow with token refresh
Assumptions: `[PLACEHOLDER:experiment_flag]` toggles rollout in staging only
Validation Gates:
- `pytest tests/cli/test_token_refresh.py -q`
- `coverage run -m pytest src/cli/`
Rollback Signal: `[PLACEHOLDER:rollback_signal]` crossing threshold
```text

### Additional Expectations

- Update `docs/CHANGELOG.md` when template-guided work lands.
- Run `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` for the affected paths.
- Keep placeholder markers intact until you supply concrete values.
- Reference the filled template in pull requests for reviewer context.

For questions, mention `@maintainer` in the Architecture Review forum or open a discussion thread.
