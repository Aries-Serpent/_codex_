# STRIDE Snapshot (Bridge)

- **Spoofing:** Short-lived API keys; GitHub App JWT exchanged for installation tokens.
- **Tampering:** Idempotency keys, `confirm` gate, and `dry_run` defaults on destructive endpoints.
- **Repudiation:** Correlation IDs (`X-Request-Id`) and audit logging with agent/user identity.
- **Information Disclosure:** Least-privilege GitHub App scopes; secrets are redacted in logs.
- **Denial of Service:** Rate limits, exponential backoff, and client-side concurrency caps.
- **Elevation of Privilege:** Repository/org allowlists and explicit guardrails for write operations.
