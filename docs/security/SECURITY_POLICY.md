# Security Policy

This repository now includes a lightweight security module under `src/security/`. The
module centralises safe defaults that are meant to be reused by services across the
Codex platform.

## Guidance

- Use `security.sanitize_sql_input` to validate user generated SQL fragments before
  forwarding them to a database interface. The helper enforces a deny-list policy that
  can be extended via `SecurityPolicy`.
- Prefer `security.secure_compare` when comparing sensitive tokens (API keys, session
  identifiers, etc.) so timing side-channels remain bounded.
- Secrets should be retrieved via `security.environment_secret_provider`, which can be
  swapped with more advanced providers when required.

## Reporting

- Report security vulnerabilities privately via the Codex security channel documented
  in the internal handbook.
- Do not disclose vulnerabilities publicly until a fix has been released.
