# IMDS Canonical Manifest
> Generated: 2025-11-14 23:00:10 UTC | Author: mbaetiong

## Purpose
Enumerate all authoritative IMDS diagnostic tooling assets to retain under `0D_base_` and list duplicates marked for decommission.

## Canonical Files (To KEEP)
| File | Purpose | Version Source |
|------|---------|----------------|
| `.github/scripts/imds_diagnostic.sh` | Diagnostics + guarded remediation | Consolidated (2233 base) |
| `.github/docs/imds_diagnostic_RUNBOOK.md` | Operational usage & safety model | 2228 baseline + revisions |
| `.github/docs/IMDS_FILE_CONSOLIDATION_MATRIX.md` | PR artifact mapping | New consolidation |
| `.github/docs/IMDS_IMPLEMENTATION_MERGE_PLAN.md` | Merge & rollout steps | New |
| `.github/docs/IMDS_JSON_SCHEMA.md` | JSON contract for automation | New |
| `.github/docs/IMDS_CHANGELOG.md` | Version history | New |
| `.github/docs/IMDS_MANIFEST.md` | This manifest | New |

## Optional / Conditional Files
| File | Condition to Include | Notes |
|------|----------------------|-------|
| `IMDS_IMPLEMENTATION_SUMMARY.md` | If maintainers request deeper audit context | From PR 2230 |
| ShellCheck workflow | After canonical merge | Adds lint enforcement |
| Pre-flight IMDS workflow | Before deployment merges | Ensures IMDS accessible |

## Duplicate / Redundant PR Artifacts (To REMOVE or CLOSE)
| PR # | Artifact Type | Action | Rationale |
|------|---------------|--------|-----------|
| 2228 | Runbook copy | Close | Integrated |
| 2230 | Script + runbook + summary | Cherry-pick summary then close | Summaries only |
| 2231 | Duplicate script/runbook | Close | No unique content |
| 2232 | Iterative duplicate | Close | Redundant changes |
| 2229 | Conflicted/dirtied state | Close | Superseded by canonical |

## Merge Sequence Snapshot
1. Validate canonical script & runbook.
2. Merge into staging or directly into `0D_base_`.
3. Add supporting documentation (matrix, merge plan, schema, changelog).
4. Close duplicates with link to commit SHA.
5. Rebase dependent orchestration PRs (2225, 2227).
6. Add CI enhancements (ShellCheck, pre-flight action).

## Governance / Approval
| Action | Required Approval | Artifact |
|--------|-------------------|----------|
| Remediation run (`--apply`) | @mbaetiong | Script |
| Duplicate closure | @mbaetiong | PRs 2228/2230/2231/2232/2229 |
| Workflow introduction | @mbaetiong | ShellCheck / Pre-flight gating |

Relates to issue: #2226
