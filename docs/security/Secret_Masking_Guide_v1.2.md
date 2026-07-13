# Security: Secret Masking Guidance (v1.2)
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> Generated: 2026-06-22 (audited) | Author: mbaetiong  
 Roles: [Primary: Security Maintainer], [Secondary: Reviewer]  Energy: 5

Rules
- Never commit plaintext secrets or tokens.
- Redact as "[REDACTED:<class>]" in reports and logs.
- Avoid quoting .env or key files verbatim.

Procedures
- If exposure suspected: remove artifact, rotate, invalidate tokens, document incident privately.
- Maintain .secrets.baseline and audit changes in PRs.
