# [Ops]: GitHub Rulesets vs Classic Branch Protection (Primer)  
> Generated: 2025-10-09 20:04:41 UTC | Author: mbaetiong  
Roles: [Audit Orchestrator], [Capability Cartographer]  Energy: 5

Context
- Classic protection APIs cover approvals, CODEOWNER reviews, and conversation resolution.
- Rulesets provide a more expressive policy model and are the likely long-term path.

Guidance (pragmatic)
- Start with classic protection via bootstrap CLI (safer, widely supported).
- Document desired ruleset equivalent for future migration.
- Keep CODEOWNERS in .github/CODEOWNERS and require CODEOWNER reviews.

Checklist
- [ ] CODEOWNERS present with default "*" rule
- [ ] Branch protection requires CODEOWNER reviews
- [ ] Vulnerability alerts enabled (best effort)
- [ ] Document ruleset intent (future)

*End*