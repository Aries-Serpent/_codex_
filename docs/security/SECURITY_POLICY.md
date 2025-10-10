# Security Policy

## Supported Versions
| Version | Supported |
|---------|-----------|
| main | ✅ |

## Reporting Vulnerabilities
- Email: security@codex-project.org
- PGP Key: `0xC0D3XSEC`

## Security Measures
- Input validation on all user data through `src.security` utilities
- Secret management enforced with entropy checks and rotation policies
- Rate limiting on API endpoints via security middleware
- Audit logging for security events with centralized logging
- Regular dependency scanning (Semgrep, detect-secrets, pip-audit)

## Threat Model
See [THREAT_MODEL.md](THREAT_MODEL.md) for a detailed analysis of attack surfaces, trust boundaries, and mitigations.

## Incident Response
Refer to [incident_response.md](incident_response.md) for escalation paths and communication templates.

## Authentication & Secrets
Guidance for credential handling and API key lifecycle is documented in [authentication.md](authentication.md).
