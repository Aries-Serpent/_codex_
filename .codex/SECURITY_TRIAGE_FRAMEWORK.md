# Security Triage Framework for Repo-Wide CodeQL Remediation

## Purpose

This document implements the repo-wide remediation model for the `Aries-Serpent/_codex_` repository. It translates the repo's own security policy into an actionable, multi-lane workflow that explicitly refuses deferral language and requires every open alert to be classified as either:

- code-fix actionable,
- false positive / suppressible,
- admin-only / external dependency requirement,
- documentation-only,
- or unresolved with an explicit owner and reason.

This framework is designed to work with the repository's canonical security agents and to force a broad backlog reduction strategy rather than narrow PR-only patching.

## Repository evidence for the model

The repo already contains the authorizing evidence for this remediation model:

- `.github/codeql/codeql-config.yml` sets the active CodeQL scan surface to `src/`, `tests/`, `scripts/`, `.github/`, `tools/`, and `cognitive_app/` and enables `security-extended` and `security-and-quality` queries.
- `.github/workflows/codeql-ga-gate.yml` parses SARIF results and fails the workflow when critical or high alerts are present.
- `.github/copilot/agent-brain-config.yml` includes the no-deferral rule: `no_deferral` must never say "best suited for follow-up PR".
- `.github/SECURITY_REMEDIATION.md` shows a repeatable history of batch remediation and admin-only exceptions.
- `.github/agents/unified-security-scanner.md` defines the canonical merged security entry point.
- `.github/agents/codeql-alert-resolution-agent.md` defines the remediation executor for CodeQL findings.

This is the core statement of the repo: the security backlog is not imaginary, is not optional, and should not be silently deferred.

## Policy requirements

### No-deferral standard

Every agent or human session working on security backlog must use the following mandatory wording when an item remains unresolved:

- "This issue is classified as [code fix / false positive / admin-only / documented limitation / unresolved with owner]."
- "If unresolved, we record the reason and owner rather than deferring by default."
- "Repo-wide security debt is treated as a backlog, not as an excuse to stop."

Any status update containing one of the following phrases is invalid unless it is immediately converted into a classification and owner assignment:

- out of scope
- broader repo issue
- future PR
- not related to this branch
- will be handled later
- not my responsibility
- pre-existing and safe

### Required triage classification

Every CodeQL finding must be assigned to one bucket:

1. Code-fix actionable
   - real security issue in repo code
   - fixable in-repo
   - can be validated by tests or static checks

2. False positive / suppressible
   - static rule is not an actual vulnerability
   - supported by code intent or runtime safety
   - requires documented suppression or query filter

3. Admin-only / external requirement
   - needs repository secret, org setting, GitHub Actions pinning, or service-side policy change
   - not fixable by code alone

4. Documentation-only
   - explains why a pattern is acceptable or intentional
   - does not change code behavior

5. Unresolved with owner
   - not silently deferred
   - must include reason, owner, and planned remediation

## Canonical multi-lane workflow

### Lane P1 — Unified security triage

Primary agent:
- `unified-security-scanner`

Goal:
- enumerate active findings and classify them by family, root cause, file path, and fix class.

Required prompt:

> Enumerate all open security/code-scanning findings for this repository, grouped by CodeQL family, root cause, file path, and likely fix class. Do not defer broad findings as out-of-scope. Classify each finding as code-fix actionable, false positive / suppressible, admin-only / external dependency requirement, documentation-only, or unresolved with explicit owner. Produce a canonical backlog table with severity, family, file, fix class, status, and owner lane.

Required output:

- one backlog inventory for all active findings
- one summary by family
- one summary by severity
- one explicit list of admin-only findings
- one explicit list of suppressible findings

### Lane P2 — CodeQL batch remediation

Primary agent:
- `codeql-alert-resolution-agent`

Goal:
- remediate actionable alert families in batches instead of one-by-one, and reduce the backlog by family.

Required prompt:

> Take the classified CodeQL backlog and remediate actionable families in batches: unsafe subprocess or command execution, path traversal or unsafe file handling, insecure temp file creation, weak crypto or randomness in security-sensitive paths, SSRF or URL validation issues, insecure deserialization, eval-like patterns, and tainted data flow and dangerous sink patterns. Fix all actionable findings in each family before moving to the next family. Do not stop on a single issue or claim the backlog is broader than scope when the fix is within the repo.

Required output:

- a patch grouped by root cause and family
- validation results for each family
- re-run results of the gate after the batch
- remaining backlog classified after each group

### Lane P3 — No-deferral enforcement and governance

Primary agent:
- `workflow-compliance-guardian`

Goal:
- enforce the no-deferral policy during remediation and prevent “out of scope” justification from surviving into status updates.

Required prompt:

> Validate every remediation step against the repository no-deferral policy. Reject any status update containing out-of-scope language such as broader repo issue, future PR, not related to this branch, or will be handled later. Require every unresolved issue to be classified as code fix, false positive, admin-only, or documented limitation with explicit owner and reason.

Required output:

- a classification ledger for all unresolved issues
- a list of blocked or invalid statuses
- final compliance signoff before merge or branch exit

### Lane P4 — Pattern detection and regression prevention

Primary agent:
- `ci-pattern-guardian`

Goal:
- identify the recurring root cause behind deferral behavior and ensure the repo does not re-enter the same backlog state again.

Required prompt:

> Collect patterns from all security remediation sessions and identify repeated deferral behaviors, scope-narrowing mistakes, and backlog re-entry. Flag sessions that narrow scope without classifying unresolved issues. Track the repeated families and create a canonical remediation queue so the next session does not restart from zero.

Required output:

- a pattern log of repeated deferral causes
- a backlog re-entry analysis
- a canonical re-triage queue for the next cycle

## Required workflow sequence

1. P1 runs first and produces the canonical backlog.
2. P2 fixes all actionable findings by family in batches.
3. P3 verifies the no-deferral policy and rejects out-of-scope language.
4. P4 audits repeated deferral patterns and tracks backlog churn.
5. Final validation is executed:
   - re-run CodeQL gate
   - compare alert counts by family before and after
   - confirm every leftover item is explicitly classified
   - confirm no item is silently left as “broad or out of scope”

## Backlog table schema

Use a single repo-wide table with the following columns:

| Column | Purpose |
|---|---|
| alert_family | CodeQL family or pattern group |
| severity | critical / high / medium / low |
| file_path | Primary file or files |
| root_cause | Why the alert exists |
| fix_class | code-fix / false-positive / admin-only / doc-only / unresolved |
| status | open / fixed / suppressed / deferred-with-owner |
| owner_lane | unified-security-scanner / codeql-alert-resolution-agent / workflow-compliance-guardian / ci-pattern-guardian |
| validation | tests, static checks, or admin verification |

## Family-oriented remediation batching

Prioritization should follow the repo's own security logic and the CodeQL gate semantics:

1. Critical and high in-repo code issues
2. unsafe file handling and subprocess execution
3. URL / SSRF / validation issues
4. insecure randomness or crypto-sensitive logic
5. taint propagation and dangerous sink patterns
6. admin-only or external configuration issues
7. false positives and documented suppressions

This sequence ensures the gate is driven down in a predictable way while keeping the backlog auditable.

## Allowed classification outcomes

### Accepted final states

- fixed
- false-positive documented
- admin-only requirement documented
- documented limitation with owner

### Rejected final states

- broader than scope
- future PR
- not related to this branch
- will fix later
- out of scope
- no owner

Any unresolved item must contain all of the following:

- owner
- reason
- remediation plan
- validation outcome or next validation step

## Operational rules for future sessions

1. Security work is repo-wide by default; the task must not be narrowed unless the alert is truly out of repo scope.
2. If a finding is not immediately fixable, classify it explicitly rather than denying it.
3. Use batch remediation by family to prevent session churn and repeated rediscovery.
4. Re-run the CodeQL gate after each batch to measure improvement by family.
5. Keep the backlog visible and auditable so it does not vanish behind deferral language.
6. Record all remaining admin-only or suppressible findings in the repo's governance or security docs, not in private commentary.

## Immediate repo use

The canonical pattern for this repository is:

- `unified-security-scanner` for backlog enumeration and classification
- `codeql-alert-resolution-agent` for fix implementation
- `workflow-compliance-guardian` for no-deferral enforcement
- `ci-pattern-guardian` for anti-regression pattern tracking

This is the repo-native path that matches the repository's own design and avoids the repeated cycle of broad debt + narrow PR rationalization.
