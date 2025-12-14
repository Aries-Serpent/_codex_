# Infra Change Policy

## Principles
- Treat Terraform and infra-as-code as the source of truth; never apply changes without a reviewed plan.
- Require plan verifiers for high-risk resources and cross-tenant access.
- Prefer `UNKNOWN` when plan output or verifiers are missing.

## Required Steps
1. Retrieve existing infra definitions and policies before proposing changes.
2. Run plan verifiers (e.g., `infra_plan_verifier`) and attach results to claims.
3. Flag drift or manual changes as risks; recommend remediation steps.

## Evidence Rules
- `VERIFIED` changes must cite plan output and verifier status.
- Record affected resources, blast radius, and rollback approach.
- If registry or policy data is unavailable, halt and request additional inputs.
