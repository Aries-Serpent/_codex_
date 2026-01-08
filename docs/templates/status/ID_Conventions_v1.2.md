# Guide: ID Conventions for Status v1.2 (CAP/FIND/PATCH/REPRO/Q/Phase 12/DEFER)
> Generated: 2025-11-02 15:01:45 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Taxonomy Steward], [Secondary: QA Reviewer] ⚡ Energy: 5  


Purpose
- Standardize identifiers used across reports, code, and CI to enable reliable cross-referencing and automation.

ID Formats
| Kind | Pattern | Example | Where Used |
|---|---|---|---|
| Capability | CAP-XXX (zero-padded) | CAP-001 | Template 2.2, patches[].capability_ids, repro.registry[].links |
| Finding | FIND-XXX | FIND-012 | Template 2.3, patches[].finding_ids |
| Patch | PATCH-XXX | PATCH-021 | Template 4.x, Extended Catalog links |
| Repro Control | REPRO-XXX | REPRO-003 | Template 2.5.2, patches[].repro_ids |
| Question | Q-XXX | Q-007 | Template 9 |
| Decision | Phase 12-XXX | Phase 12-005 | Template 10 |
| Deferred | DEFER-XXX | DEFER-002 | Template 2.9 |

Allocation Rules
- IDs are monotonic per kind and do not recycle.
- Use zero-padding to 3 digits at minimum; allow growth beyond 999.
- The author of a new item claims the next ID; collisions resolved in PR review.

Validation Hints
- Regexes to validate:
  - CAP: ^CAP-[0-9]{3,}$
  - FIND: ^FIND-[0-9]{3,}$
  - PATCH: ^PATCH-[0-9]{3,}$
  - REPRO: ^REPRO-[0-9]{3,}$
  - Q: ^Q-[0-9]{3,}$
  - Phase 12: ^Phase 12-[0-9]{3,}$
  - DEFER: ^DEFER-[0-9]{3,}$

DoD
- Every new capability/finding/patch has an ID and owner.
- Cross-links are present in patches and registry entries.
- CI validators pass for ID formats in JSON status reports.
