# Process: Schema Remediation (v1.2)
> Generated: 2025-11-02 15:30:24 UTC | Author: mbaetiong  
🧠 Roles: [Primary: Schema Owner], [Secondary: Reviewer] ⚡ Energy: 5

Steps
| Step | Owner | Action | Artifact |
|---|---|---|---|
| Detect | Author/CI | Run schema validations | workflow logs |
| Assess | Schema Owner | Classify: fix data or relax schema | issue (schema_failure) |
| Remediate | Author | Update config/data and tests | PR with changes |
| Validate | CI | Re-run validations | green checks |
| Document | Author | Update Status 2.6.2 actions | daily report |

Policies
- Prefer fixing data/config to match schema
- Relax schema only with rationale and version bump (minor)
