# Validation Checklist: Mandated Status Update Template
> Updated: 2025-09-22

Use this checklist to confirm that a `_codex_` status update conforms to the 2025-09-22 mandated format. The report may be generated manually or via automation, but it **must** follow the structure codified in `docs/status_update_prompt.md` and `AUDIT_PROMPT.md`.

## Preflight

| Check | Status | Notes |
| --- | --- | --- |
| Report captured offline (no GitHub Actions, remote CI, or network fetches) |  |  |
| File named `status_update_YYYY-MM-DD.md` under `docs/status_updates/` (or `_codex_status_update-YYYY-MM-DD.md` under `.codex/status/`) |  |  |
| Leading fetch directives present (`Check for must recent active branch`, `Branches`) |  |  |
| Objective block mirrors mandated wording |  |  |
| Audit date in title matches filename |  |  |

## Audit Scope Coverage

| Section | Requirement | Status | Notes |
| --- | --- | --- | --- |
| 1. Repo Map | Lists top-level directories, key files, stub inventory, recent changes |  |  |
| 2. Capability Audit Table | Table includes all 14 capabilities with Status, Existing Artifacts, Gaps, Risks, Minimal Patch Plan, Rollback Plan |  |  |
| 3. High-Signal Findings | 10–20 bullet items covering critical gaps and wins |  |  |
| 4. Atomic Diffs | ≥3 diffs with Why/Risk/Rollback/Tests sub-bullets and fenced diff blocks |  |  |
| 5. Local Tests & Gates | Tabular commands with ML Test Score mapping |  |  |
| 6. Reproducibility Checklist | Table enumerating seeds, environment capture, manifests, determinism, results logging |  |  |
| 7. Deferred Items | Bulleted list with rationale for remaining gaps |  |  |
| 8. Error Capture Blocks | Explicit statement of encountered errors or confirmation that none occurred |  |  |

## Codex-ready Follow-ons

| Section | Requirement | Status | Notes |
| --- | --- | --- | --- |
| Codex-ready Task Sequence | YAML block with six numbered phases and sub-steps referencing remediation work |  |  |
| Executable Script | Runnable script implementing the task sequence end-to-end, including README adjustments, gap logging, and error capture hooks |  |  |
| Error block format | Matches `Question for ChatGPT @codex {{timestamp}}` wording |  |  |

## Compliance & Traceability

| Check | Status | Notes |
| --- | --- | --- |
| References to outstanding questions align with `docs/status_update_outstanding_questions.md` (no embedded table required) |  |  |
| No YAML generated that could trigger GitHub Actions |  |  |
| Mention of local-only validation (`pre-commit`, `nox`, etc.) retained |  |  |

## Sign-off

| Role | Name | Date | Notes |
| --- | --- | --- | --- |
| Reviewer |  |  |  |
| Maintainer |  |  |  |
