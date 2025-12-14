# Contributing Guide

Thank you for improving `_codex_`. This document highlights the workflow for using the operational templates and the expectations for role-gated execution.

## Testing Requirements

All contributions must include appropriate tests and maintain code coverage standards.

### Running Tests Locally

**Quick test run:**
```bash
pytest
```

**With coverage:**
```bash
pytest --cov=src --cov-report=html --cov-report=xml --cov-report=term
```

**Run specific test categories:**
```bash
pytest -m smoke              # Smoke tests only
pytest -m "not slow"         # Skip slow tests
pytest -m integration        # Integration tests
```

See `tests/README.md` for comprehensive testing instructions.

### CI/CD Testing

All pull requests are automatically tested via GitHub Actions (`.github/workflows/ci-pytest.yml`):
- Tests run on Python 3.11+ (ubuntu-latest)
- Coverage must meet 90% threshold (configurable)
- Coverage reports are uploaded as artifacts
- Automatic PR comment with coverage summary and artifact links

### Coverage Requirements

- **Minimum threshold**: 90% (enforced in CI)
- **Local validation**: `pytest --cov=src --cov-fail-under=90`
- **Coverage reports**: Available as CI artifacts (HTML, XML, JSON formats)
- **Viewing reports**: Download `coverage-html-report` artifact from workflow run

### Before Submitting a PR

1. Run tests locally: `pytest -v`
2. Check coverage: `pytest --cov=src --cov-report=term-missing`
3. Ensure no test failures
4. Add tests for new functionality
5. Update documentation if needed

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
- `pytest --cov=src/cli --cov-fail-under=90`
Rollback Signal: `[PLACEHOLDER:rollback_signal]` crossing threshold
```

### Additional Expectations

- Update `docs/CHANGELOG.md` when template-guided work lands.
- Run `pytest -q` for the affected paths before committing.
- Ensure coverage doesn't decrease with your changes.
- Keep placeholder markers intact until you supply concrete values.
- Reference the filled template in pull requests for reviewer context.

For questions, mention `@maintainer` in the Architecture Review forum or open a discussion thread.
