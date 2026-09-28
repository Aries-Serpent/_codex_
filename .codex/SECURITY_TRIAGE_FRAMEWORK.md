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

## Customer-agent task pack for workflow run 36282332415

The repo already has the right behavior to address CodeQL findings when the security suite is run. The workflow evidence from `Art_Security Scanning Suite` run `#15082` is the authoritative artifact source for this backlog analysis in the sandbox, because the GitHub code-scanning alert API is currently returning 403 here and therefore cannot be used as the primary source for exact live alert enumeration.

### Required task assignments

#### P1 — `unified-security-scanner`

Assign this agent to:

- inspect the artifact bundle from `https://github.com/Aries-Serpent/_codex_/actions/runs/36282332415`
- classify the relevant output bundles by family and severity, explicitly prioritizing:
  - `security-suite-codeql-python`
  - `security-suite-codeql-javascript`
  - `security-suite-semgrep`
  - `security-suite-comprehensive-findings`
  - `security-suite-summary`
- identify which artifact is intended to capture the majority of the 3.2k alert set and document why
- produce a backlog ledger with columns: `alert_family`, `severity`, `file_path`, `root_cause`, `fix_class`, `status`, `owner_lane`, and `validation`
- mark every unresolved item as one of: `code-fix`, `false-positive`, `admin-only`, `documentation-only`, or `unresolved-with-owner`

Required prompt:

> Analyze the security-suite workflow artifacts for run 36282332415. Do not rely on the GitHub code-scanning API as the primary source because the sandbox is returning 403. Treat the artifact bundles as the canonical evidence and enumerate the findings by CodeQL family, severity, file path, and fix class. Group the backlog into actionable findings, suppressible findings, admin-only requirements, and unresolved items with explicit owner. Do not defer broad findings as out-of-scope.

#### P2 — `codeql-alert-resolution-agent`

Assign this agent to:

- fix actionable families in batches across the repo without pretending the backlog is outside scope
- start with critical/high repo-code findings from the CodeQL surface
- validate by rerunning the relevant static or test gates, not just by claiming the issue is broad or external
- record which families remain after each batch and why they remain unresolved

Required prompt:

> Take the enumerated backlog from the security workflow artifacts and remediate all actionable CodeQL findings in batches by family. Prioritize critical and high repo-code findings, then admin-only requirements, then suppressible findings. Keep the backlog visible and track the remaining items with explicit classification and owner.

#### P3 — `workflow-compliance-guardian`

Assign this agent to:

- reject “out of scope,” “future PR,” or “broader repo issue” language in every status update
- require every unresolved finding to have a formal classification, owner, reason, and next step
- enforce the repo policy that backlog debt is a backlog, not a reason to stop remediation

Required prompt:

> Validate each remediation status update against the repo no-deferral policy. Any unresolved finding must be labeled as code-fix, false-positive, admin-only, documentation-only, or unresolved-with-owner with the reason and owner clearly recorded. Reject any response that contains out-of-scope or deferral phrasing.

#### P4 — `ci-pattern-guardian`

Assign this agent to:

- identify why this security backlog is repeatedly narrowed to “current branch” or “later PR” reasoning
- track repeated findings and prevention measures so subsequent sessions do not reintroduce the same deferral loop
- produce the canonical re-triage queue for the next remediation cycle

Required prompt:

> Audit the pattern behind repeated security backlog deferrals and scope narrowing. Identify the recurring anti-patterns in sessions that classify security debt as out of scope. Produce a canonical backlog queue and a prevention plan so future security work does not restart from zero.

### Artifact interpretation for the 3.2k alert concern

The workflow run is designed to surface the majority of the backlog via artifact-based security scanning rather than via direct GitHub code-scanning API output. The artifact list includes the relevant evidence for that model:

- `security-suite-codeql-python`
- `security-suite-codeql-javascript`
- `security-suite-semgrep`
- `security-suite-dependency`
- `security-suite-cve-python`
- `security-suite-cve-javascript`
- `security-suite-cve-rust`
- `security-suite-comprehensive-findings`
- `security-suite-summary`

This is the expected repo behavior for security/codeql work: the workflow is intended to package the broad security backlog into artifacts for triage, processing, and classification, even when direct API enumeration is restricted in the sandbox. The correct operational model is therefore to use the workflow artifacts as the canonical backlog source and to fix or classify backlog items by family without claiming that the findings do not exist.

## Immediate repo use

The canonical pattern for this repository is:

- `unified-security-scanner` for backlog enumeration and classification
- `codeql-alert-resolution-agent` for fix implementation
- `workflow-compliance-guardian` for no-deferral enforcement
- `ci-pattern-guardian` for anti-regression pattern tracking

This is the repo-native path that matches the repository's own design and avoids the repeated cycle of broad debt + narrow PR rationalization.
