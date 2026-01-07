# Business Rules

> For AI Agents - Last Updated: 2025-12-24

This document defines business rules and constraints for the _codex_ system.

## Core Principles

1. **Security First** - Never compromise security for convenience
2. **Minimal Changes** - Make the smallest change that solves the problem
3. **Test Coverage** - All code changes must include tests
4. **Documentation** - Document breaking changes and new features

## Operational Rules

### Code Changes

| Rule | Description |
|------|-------------|
| R1 | All changes must pass CI before merge |
| R2 | Breaking changes require version bump |
| R3 | Security fixes take priority over features |
| R4 | Tests must cover new functionality |

### API Usage

| Rule | Description |
|------|-------------|
| R5 | Respect rate limits (see `configs/routing.yaml`) |
| R6 | Use cost-effective models when possible |
| R7 | Cache responses where appropriate |
| R8 | Log all API calls for audit |

### Data Handling

| Rule | Description |
|------|-------------|
| R9 | Never log PII or secrets |
| R10 | Encrypt sensitive data at rest |
| R11 | Minimize data retention |
| R12 | Anonymize data for analytics |

## Model Selection Rules

Select models based on task requirements:

| Task Type | Preferred Model | Max Cost Tier |
|-----------|-----------------|---------------|
| Simple queries | gpt-4o-mini | low |
| Code generation | gpt-4o | medium |
| Complex reasoning | o1-mini | medium |
| Critical decisions | o1-preview | high |

## Error Handling Rules

| Scenario | Action |
|----------|--------|
| API error (retryable) | Retry with exponential backoff |
| API error (non-retryable) | Log and return error |
| Validation failure | Return descriptive error |
| Unknown error | Log full context, alert if critical |

## Cost Management

| Limit | Value | Action on Breach |
|-------|-------|------------------|
| Daily API spend | $100 | Alert + throttle |
| Per-request cost | $0.10 | Require approval |
| Monthly budget | $2000 | Hard limit |

## Compliance Requirements

1. **Audit Trail** - All actions logged with timestamp and user
2. **Access Control** - RBAC enforced for sensitive operations
3. **Data Retention** - Logs kept for 90 days minimum
4. **Incident Response** - Security issues reported within 24h

## Prohibited Actions

The following are strictly prohibited:

- Storing secrets in code or logs
- Bypassing rate limits
- Ignoring test failures
- Deploying without review
- Accessing data outside authorization

## Exception Process

For rule exceptions:
1. Document the business justification
2. Get approval from code owner
3. Implement compensating controls
4. Add to exception registry

## See Also

- [Coding Standards](coding_standards.md)
- [Glossary](glossary.md)
