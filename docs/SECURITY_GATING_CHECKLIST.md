# Security Gating Checklist — Enabling Live Integration Tests

Purpose
- Checklist for repository administrators to follow before enabling integration-gated CI workflows that run live provider tests.

Preconditions (must be satisfied)
- [ ] Review and approve who has permission to add repository secrets (Admin group identified).
- [ ] Confirm secrets stored in GitHub Secrets with least-privilege keys (e.g., test-only API keys).
- [ ] Confirm branch protection rules: only specific branches (e.g., main, integration) can trigger gated workflows.
- [ ] Confirm audit logging / approval process for enabling gated workflows.

Required secrets (examples)
- OPENAI_API_KEY
- PINECONE_API_KEY
- ENABLE_LIVE_TESTS (set to "true" to enable)

Workflow gating
- Keep integration-gated workflows template-only until secrets are added and reviewed.
- CI should default to mock-only runs; live tests require ENABLE_LIVE_TESTS="true".

Operational steps
1. Add secrets to GitHub: Repository > Settings > Secrets
2. Ensure .github/workflows/integration-gated.yml remains template-only until secrets are added and workflow inputs are validated.
3. Run a dry-run integration in a staging repo or fork to verify expenses and quotas.
4. Monitor first runs closely and rotate keys after initial use.

Post-enablement
- [ ] Validate integration runs complete successfully.
- [ ] Rotate keys periodically.
- [ ] Revoke and audit if unexpected usage occurs.

Notes
- NEVER commit real secrets to repository files.
- Use ephemeral or restricted test keys where supported.
- Verify that CI jobs set provider keys to empty strings unless gating is enabled.
