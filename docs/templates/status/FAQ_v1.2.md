# FAQ: Status v1.2
> Generated: 2025-11-02 15:05:03 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Docs Maintainer], [Secondary: Onboarding Mentor] ⚡ Energy: 5

Q: Do I need to fill every section?
- A: Provide a full snapshot; mark delta N/A if no prior report.

Q: Which schema version is enforced?
- A: JSON Schema Draft 2020-12; validator auto-detects and falls back accordingly.

Q: Where do I put remediation for schema failures?
- A: Section 2.6.2 (Schema Remediation Actions).

Q: How do I prove report integrity?
- A: Run scripts/audit/build_integrity_chain.py and include audit_run_manifest.json in the report artifacts.

Q: What IDs are required?
- A: CAP-/FIND-/PATCH-/REPRO-/Q-/Phase 12-/DEFER- per ID_Conventions_v1.2.md.
