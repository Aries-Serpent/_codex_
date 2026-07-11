# Ops: Offline-First Guidelines
**Last Updated:** 2026-07-11
**Version:** v0.2.1

> Generated: 2026-06-22 (audited) | Author: mbaetiong  
 Roles: [Primary: Ops Lead], [Secondary: Developer Experience] ⚡ Energy: 5

Guidelines
- Vendor minimal tooling where possible or cache wheels
- Use tools/hf_cache_prepare.py to pre-warm tokenizers
- Avoid external network in tests; skip conditional when needed
- Prefer deterministic tests and small artifacts
