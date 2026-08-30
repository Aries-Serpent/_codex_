
# STRIDE Snapshot (Bridge)

- **Spoofing**: Short-lived API keys; GitHub App JWT → installation token.
- **Tampering**: Idempotency keys; `confirm` gate; dry-run defaults.
- **Repudiation**: Correlation IDs; audit log with agent/user identity.
- **Information Disclosure**: Least-privilege App scopes; redact secrets in logs.
- **Denial of Service**: Rate limits + backoff headers; concurrency caps in clients.
- **Elevation of Privilege**: Repo/org allowlists; explicit guardrails for write ops.
