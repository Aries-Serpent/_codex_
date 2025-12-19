# Secrets Runbook (brief)

Purpose
- Document how to store provider secrets, rotate them, and enable gated live integration tests safely.

Key points
- Store secrets in GitHub Secrets (Repository > Settings > Secrets) or an external vault (HashiCorp Vault).
- Do NOT commit secrets to the repository.
- Use the integration-gated workflow to run live tests; enable by setting ENABLE_LIVE_TESTS=true in workflow inputs or in environment.
- Rotate keys regularly and update secrets in repo settings. Use short-lived credentials where supported.

Enabling live tests (high-level)
- Add provider secrets to repository Secrets: OPENAI_API_KEY, PINECONE_API_KEY, etc.
- Set ENABLE_LIVE_TESTS secret to "true" only for authorized branches or by admins.
- Run the integration-gated workflow manually (or via CI policy) to execute live tests.

Least-privilege guidance
- Create API keys scoped to the test environment and restrict index/prefix access where possible.
- Monitor usage and set provider-side billing alerts.

Audit
- Keep an audit log of who enabled live tests and when; record workflow runs and approvals.
