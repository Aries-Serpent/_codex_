# Human-maintainer actions: CDX continuation

## Purpose and authority

This companion lists **only actions requiring a human maintainer, platform
operator, independent reviewer or external service owner**. The sole
[continuation](./CONTINUATION.md) owns Copilot's CLI/VS Code execution lanes,
local validation, technical diagnosis, source changes, evidence collection and
conditional publication procedures. Do not duplicate those procedures here.

The owner has already approved scoped implementation, CLI use in this VS Code
workspace, ready scoped publication and both runtime activation targets. Do not
re-ask for generic consent. This approval does not grant unavailable
credentials, signer material, administrative rights, merge authority,
independent review, private-source clearance or blanket workflow/archiving
authority. This plan records requested human interventions, not evidence that
they have occurred.

The detailed state and evidence in the continuation are authoritative and may
change. References to branch tips, failed access, CI and missing facilities in
older checkpoints are historical; recheck them through the continuation's
Copilot-owned lanes before asking anyone to act.

## Human/provider actions

Perform an action only when Copilot identifies the specific unavailable
facility or decision. Routine CLI commands, local tests, native task use,
read-only API queries, source-level fixes and evidence reconciliation belong to
Copilot's continuation lanes, not to the human queue.

| ID / responsible party | Human-only action, if required | Return to Copilot |
| --- | --- | --- |
| **H1 / workspace maintainer** | No standing action: the native VS Code task/terminal route has been exercised. Intervene only if Copilot reports that the actual workspace task or terminal bridge is no longer available. Do not run routine CLI probes on Copilot's behalf. | Identify the specific unavailable host facility and restore its supported access; do not share IPC/socket values. |
| **H2 / account and signing maintainer** | Complete inaccessible account, SSO or device authentication through the supported UI; restore the configured genuine signing facility. If it cannot be restored, provide an approved signer or perform the authorized signed operation locally with the maintainer's own identity. Never disable signing or impersonate another signer. | Redacted confirmation of the repaired facility or signed-operation reference, bound to the resulting commit/SHA. Do not send credentials, device codes or private keys. |
| **H3 / repository or organization administrator** | Where an actual operation is denied, grant only the needed repository/App access or entitlement, or expose the inaccessible control. Preserve branch protections, required reviews, environments and least privilege; do not grant blanket administration to solve transport. | Identify the control changed and the permitted operation. Copilot independently verifies the actual operation through its supported interface. |
| **H4 / local VS Code operator** | Only if Copilot has no usable local selector: select the existing CDX profile in the intended harness and initiate the approved bounded synthetic task. Do not substitute a default agent or an unverified profile with the same name. | Invocation reference and the actual selected source/harness; Copilot verifies binding, effective tools and per-target isolation. |
| **H5a/H5b / integration maintainer and required reviewers** | Perform genuine required reviews and platform merges when Copilot lacks authorized merge authority/transport. Follow the established sub-PR to `0D_base_`, then promotion to `main` route. Do not bypass checks, self-approve, push directly to `main` or treat an open PR as integration. | Actual review/merge record and resulting head/default SHA. Copilot verifies profile bytes and the next-stage route. |
| **H6 / hosted Copilot operator** | Only if Copilot cannot use an actual hosted task-launch interface: select the repository's CDX profile after reviewed default-branch integration and initiate the bounded synthetic task, after checking the target's side effects and isolation constraints. | Hosted task reference, selected profile/revision and completed result. Copilot validates the evidence; a screenshot or task name alone is insufficient. |
| **H7 / Actions or runner owner** | Supply diagnostics that remain inaccessible after Copilot's authorized inspection; repair a demonstrated runner/account/service fault. Authorize a specific dispatch/retry only when existing operation authority does not cover it. | Exact workflow/run/attempt/SHA and repaired-control reference, or the remaining infrastructure limitation. Never authorize a retry of the prohibited timed-out CodeQL operation. |
| **H8 / security-service and CodeQL owner (S)** | Provide authentic current alert records and exact owner dispositions, or expose an authorized suitable external-analysis service and completed result. Do not substitute a stale analysis, a local review, or a denied API response for clearance. | Non-sensitive analysis/result reference bound to revision and scope, and attributable alert disposition. |
| **H9 / data-retention owner (D)** | Identify or provision approved durable private custody, access control, retention, backup/recovery and cleanup. If restoring a historical epoch, make the complete matching bundle available through the approved private channel. | Redacted control/result reference and confirmation that persistence/recovery and bundle completeness can be verified. Keep keys, private endpoints, raw findings and source bytes out of this plan/chat. |
| **H10 / runtime or source owner (R)** | Provide or provision enforced source containment, network/resource boundaries and writer exclusion for the exact source/snapshot. A shared directory, file mode or policy statement is not sufficient. | Control reference identifying the scope and enforcement mechanism. Copilot separately verifies actual denial and snapshot binding before acquisition. |
| **P / policy or tooling owner** | Only if a documented distribution restriction or required official tool/service access is unavailable to Copilot, provide the controlling policy reference or provision the authorized access. Do not prescribe a pin change or treat a cache/version string as provenance. | Policy/access reference and applicable scope. Copilot performs the technical provenance checks. |
| **H11/C and A / scanner-policy owner and independent reviewer** | The policy owner reviews/accepts the separately implemented stock-evidence contract. A genuinely independent reviewer must establish their identity/authority/access and make attributable current finding decisions using authentic evidence. These roles cannot be collapsed into the implementer or an agent persona. | Contract acceptance by the responsible owner and independently attributable decision evidence through the approved private mechanism. Copilot checks completeness, freshness and bindings. |
| **F / domain or source-context owner** | Supply trustworthy origin/consumer context only for findings whose relevant private context Copilot cannot access. Do not infer harmlessness from names or appearances, or make decisions on behalf of the independent reviewer. | Non-sensitive evidence reference and scope; the independent reviewer remains responsible for attributable disposition. |
| **H12/E, F and G / archive or source owner** | Only after applicable prerequisites, specify the exact source/selection and operation for a justified restore/acquisition. For packing, provide separate G authority for the exact destination only after complete clearance. If true secrets block the unchanged source, decide whether a separately scoped sanitized derivative is acceptable; never relabel the original as clear. | Specific operation authorization and non-sensitive scope reference. Copilot verifies the gates and performs only the authorized maintained operation; no authorization is implied by this plan. |

H8-H11, F and P may be prepared in parallel as provider work packages, without
accessing real source material. For the archive lifecycle, preserve the
dependency order **S/D/R/P/C -> E -> F -> genuine A -> separately authorized
G**. H5 platform review/merge and H6 hosted selection remain distinct from
Copilot's technical work and from the archive gates.

## Human handback format

Return only what Copilot needs to verify the next step:

1. Action ID, responsible role and operation/decision performed.
2. Non-sensitive control or artifact reference, with revision/scope binding.
3. Result, limitations and the approved private-evidence access method.
4. The specific facility or authority now available to Copilot.

Do not paste credentials, device codes, private keys/endpoints, raw findings,
private source bytes or sensitive storage details into this public plan or chat.
Human UI handback should identify the repaired facility and successful
operation, not include credential screens.

## Completion boundary

This human plan is complete only when each applicable human/provider action is
resolved or explicitly recorded as unavailable with its responsible owner and
next decision. It does not certify local validation, publication, CI, hosted
activation, custody, finding approval or archive creation; those require the
actual evidence and gates in [the continuation](./CONTINUATION.md).

If an irreducible blocker remains, the archive/source owner may accept a
no-archive disposition that safely ends authorized attempts. Record that as
blocked/not archived, not as successful completion of G or of the original
archive objective. A separately approved derivative has its own scope and
clearance; it cannot retroactively complete the original one.

## Platform references

- [VS Code custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents)
- [GitHub custom agents](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/create-custom-agents)

Use the platform's actual supported controls if labels or interfaces change.
Do not infer that a documented feature is enabled for the current account.
