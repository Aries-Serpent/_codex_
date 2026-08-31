# Example QA walkthrough

This example documents the expected repository-level check flow for the Codebase QA Walkthrough agent.

1. Verify the workflow file exists at `.github/workflows/codebase-qa-walkthrough.yml`.
2. Validate the agent metadata file and README are present.
3. Install required tooling (`ruff`, `pylint`, `mypy`, `bandit`).
4. Review static analysis output and summarize issues.
5. Record any follow-up actions for the PR or branch.
