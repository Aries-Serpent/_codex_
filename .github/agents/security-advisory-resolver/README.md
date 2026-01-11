# Security Advisory Resolver Agent

> **Agent Type**: Security Automation
> **Version**: 1.0.0
> **Status**: 🟢 ACTIVE

## Purpose

Auto-investigate and resolve security advisories from cargo audit, pip-audit, etc.

## Capabilities

- Scan for advisories (RustSec, NVD, GitHub Advisory)
- Analyze dependency tree impact
- Generate version bump fixes
- Create security fix PRs

## Usage

```bash
python -m agents.security_advisory_resolver resolve RUSTSEC-2025-0020
```

See `agent.yaml` for configuration.
