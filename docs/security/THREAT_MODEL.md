# Threat Model

## Overview
This document captures the major threats to the Codex platform and the controls that mitigate them.

## Assets
- Model artifacts and training data
- API credentials and secrets
- Deployment infrastructure (Kubernetes, Docker images)
- User-supplied prompts and evaluation datasets

## Attack Surfaces
| Surface | Description | Primary Controls |
|---------|-------------|------------------|
| REST API | FastAPI endpoints serving inference and management actions | Input validation, rate limiting, audit logging |
| File ingestion | Dataset loaders and manifest generation | Path validation, sandboxing, checksum verification |
| Deployment pipeline | Docker images, Helm charts, orchestrator scripts | Signed images (future), multi-stage builds, health probes |
| Configuration | Environment variables, secrets injection | Entropy checks, rotation policy, detect-secrets gating |

## Trust Boundaries
- **User Input → API Gateway**: validated by `src.security.core.validate_input` and content filters.
- **API Gateway → Model Runtime**: sanitized prompts prevent injection and output masking hides sensitive content.
- **CI/CD → Cluster**: orchestrator script ensures reproducible builds; Helm validation prevents malformed releases.

## Data Flow
1. Client request hits API and passes through security middleware (API key enforcement, CSRF/session checks).
2. Request payload sanitized and logged; rate limiter ensures fair usage.
3. Response serialized with secret redaction before returning to client.

## Threat Scenarios
- **Injection Attacks**: Mitigated via strict input validation (SQL, path traversal, XSS) and Semgrep rules.
- **Credential Stuffing**: Rate limiter and mandatory CSRF/session integrity guard login flows.
- **Secrets Exposure**: Entropy checks reject weak credentials; rotation policy enforces renewal.
- **Container Compromise**: Non-root runtime images, minimal packages, and health checks detect drift.

## Residual Risks
- Dependencies may contain undisclosed vulnerabilities; monitor advisories and patch regularly.
- GPU runtime requires NVIDIA base image updates; track CVE bulletins.

## Future Improvements
- Integrate automated secret rotation workflows
- Add anomaly detection for API usage patterns
- Expand fuzz testing for content filters
