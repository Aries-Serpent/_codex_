# Authentication & Secret Management

## Principles
- Prefer short-lived credentials with automatic rotation.
- Never store secrets in source control; use environment variables and secret stores.
- Validate entropy using `check_secret_entropy` before accepting new credentials.

## Credential Lifecycle
1. Generate secret via `rotate_secret` or approved tooling.
2. Store the secret in the platform vault with appropriate access controls.
3. Deploy secret to runtime via Kubernetes secrets or parameter store.
4. Rotate secrets at most every 30 days, or immediately after an incident.

## API Keys
- API requests must include `X-API-Key`; middleware enforces equality with server-side value.
- Rate limiting is enforced per-key by the `rate_limiter` decorator.
- Keys should be scoped to environment (dev/staging/prod) and associated to an owner.

## Session Security
- CSRF tokens validated via `verify_csrf_token` header/cookie pair.
- Session metadata (fingerprint, IP, user agent) checked with `verify_session_integrity`.

## Tooling Checklist
- Install pre-commit hooks to run detect-secrets before commits.
- Execute `pytest tests/security/ -v` before releasing new features touching auth.

## References
- [Security Policy](SECURITY_POLICY.md)
- [Threat Model](THREAT_MODEL.md)
