# NETWORK_POLICY_AUDIT

Date: 2026-07-07
Source: lane3-network (security-audit-agent)

## Executive Summary

- `enforce_network_policy(url)` exists and is fail-closed capable.
- Adoption is fragmented; many outbound paths still rely on local guards or scheme-only checks.
- Policy is functional but not yet centralized at every outbound edge.

## Key Findings

| Severity | Finding |
|---|---|
| High | Central `enforce_network_policy()` not consistently called in runtime outbound paths |
| Medium | Allowlist models are fragmented (YAML, hardcoded, env, scheme-only) |
| Medium | `PolicyViolationError` handling is not consistently surfaced in app-level flows |
| Medium | Fail-open mode exists and requires strict governance in isolated deployments |

## Recommended Controls

1. Require centralized policy guard before all `requests/httpx/urllib` outbound calls.
2. Use one canonical allowlist source with controlled overrides.
3. Enforce isolated mode at startup with fail-fast checks.
4. Improve `PolicyViolationError` context fields for observability/audit.
5. Add CI static checks for outbound-call guard coverage.
