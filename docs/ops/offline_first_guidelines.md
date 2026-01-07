# Ops: Offline-First Guidelines
> Generated: 2025-11-02 15:30:24 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Ops Lead], [Secondary: Developer Experience] ⚡ Energy: 5

Guidelines
- Vendor minimal tooling where possible or cache wheels
- Use tools/hf_cache_prepare.py to pre-warm tokenizers
- Avoid external network in tests; skip conditional when needed
- Prefer deterministic tests and small artifacts
