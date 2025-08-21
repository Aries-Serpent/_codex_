# Contributing

Thank you for improving `codex-universal`.

## Getting Started

This project accepts documentation updates and `.codex` artefacts. Before submitting a pull request, run the standard checks:

```bash
pre-commit run --all-files
mypy .
pytest
```

If the secret scan (detect-secrets) fails due to a false positive (and no actual secret is present), update the baseline by running:

```
$ detect-secrets scan --baseline .secrets.baseline
```

## Manual Validation

When changes affect the snapshot database or related tooling, perform manual validation. Follow the [Manual Verification Template](documentation/manual_verification_template.md) and record the steps you completed (A1–A4, B1–B2, or C1) in your pull request description or issue.

## Scope

See [AGENTS.md](AGENTS.md) for full guidelines.
