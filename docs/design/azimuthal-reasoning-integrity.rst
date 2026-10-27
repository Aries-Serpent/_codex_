Rubber-Duck Recursive Azimuthal Reasoning-Integrity Architecture
=============================================================

Status, provenance and authority
-------------------------------

PROPOSED DESIGN, not adopted governance. Source: the user's Institutional
Foundation and Rubber-Duck Reasoning Integrity request and continuation,
2026-10-25. The architecture claims lineage from SHA-256
``a66560774e6394b430b097bb459f238956bb8775c1c711ccd59e31fde67c96b9``;
this is an unverified historical assertion, not this asset's digest or proof a
predecessor exists. Actual materialized-asset digests belong in iteration evidence.
The formal model is preserved in ``azimuthal-formal-model.rst`` and the packaged
``codex.institutional/review-formulas.json`` bridge, with individual identifiers,
domains, assumptions, undefined cases and implementation mappings.

The physics-inspired notation is a control analogy, not physical law, measured
effectiveness or empirical proof. Synthetic charts are not measurements.
Repository/platform policy, current task authorization and genuine controls
remain authoritative. No design asset authorizes itself.

Purpose and invariants
----------------------

The Rubber-Duck Reconciler is a persistent logical, read-only reasoning-integrity
function. Persistent means attributed history survives sessions, not a background
service, automatic monitor or self-triggering process. It links claims to
evidence, compares attributed analyses, challenges response adequacy, preserves
dissent, and recommends bounded continuation, convergence, reopening or controlled
stop. It does not implement, execute candidate code, reproduce, audit, approve,
activate, release or grant authority. Outputs return to an authorized coordinator
or persistence service which validates and writes records; the Reconciler has no
mutation tools.

Preserve exact candidate/context binding; parallel analytical diversity followed
by sequential reconciliation; separation of orchestration, review, implementation,
verification, reproduction, audit, approval and authority; append-only event
history and reversible epistemic states; separate observation-confidence and
inference-confidence; minority findings; conditional assurance plans; fail-closed
operational boundaries; explicit unknowns; vector-first resilience; and
state-aware interruption/resumption.

Vocabulary
----------

* Candidate manifest: canonical manifest of the reviewed artifact set.
* Review context: bound policy, cutoff, environment, scope, materiality, resources,
  assurance, disclosure, renderer and effective profile.
* Review input snapshot: candidate manifest plus review context.
* Review-state snapshot: input snapshot plus derived graph and append-only events.
* Bearing: bounded analytical perspective, not necessarily a permanent agent.
* Lane: attributed execution of a bearing under a dispatch contract.
* Initial reconciliation: lane-output reconciliation before remediation.
* Meta-reconciliation: response adequacy against the original finding/failure class.
* Final reconciliation: technical/assurance result reconciliation before closure.
* Change authorization: permission for an exact change set on an exact base.
* Disposition authorization: permission for risk acceptance, non-applicability,
  deferral or another disposition.
* Candidate approval: authorized acceptance/rejection for a declared purpose.
* Convergence: readiness for authorized decision, not approval.
* Resilience: separately evidenced capacities under challenge, change, failure
  and reevaluation.

The three authorization categories must never be collapsed.

Roles, bearings and separation
------------------------------

.. list-table::
   :header-rows: 1

   * - Role
     - Responsibility
     - Prohibited substitution
   * - Azimuthal Orchestrator
     - Scheduling, budgeting, isolation, dispatch, collection
     - Adjudicating findings
   * - Bearing Reviewer
     - One bounded read-only analysis
     - Mutation or approval
   * - Specialized Adversarial Critic
     - Replace/supplement a declared bearing
     - Undeclared duplicate work
   * - Minority/Dissent Lane
     - Cross-bearing underrepresented interpretations
     - Extra fixed compass bearing
   * - Rubber-Duck Reconciler
     - Initial, meta and final reconciliation
     - Implementation, execution, audit or approval
   * - Implementer
     - Propose/apply authorized remediation
     - Unilateral closure
   * - Technical Verifier
     - Execute technical acceptance procedures
     - Implicit independence or approval
   * - Independent Reproducer
     - Repeat under assessed separation
     - Approval
   * - Institutional Auditor
     - Evaluate control/process operation
     - Substitute for technical evidence
   * - Authorized Decision Authority
     - Authorize dispositions and candidate decisions
     - Relabel missing evidence as satisfied

Minimum target separation: Orchestrator != Reconciler; Implementer != Reconciler;
Technical Verifier != Independent Reproducer; Institutional Auditor != Decision
Authority; Reconciler != Decision Authority. Development overlap must be explicitly
attributed and cannot establish compliant operational separation. Different names,
models, contexts or runs do not prove independence.

.. list-table::
   :header-rows: 1

   * - Coordinate
     - Bearing
     - Question
   * - 000 degrees
     - Policy
     - Applicable policy, governance and authority compatibility?
   * - 045 degrees
     - Security
     - Poisoning, bypass, redirection, impersonation, excess privilege?
   * - 090 degrees
     - Architecture
     - Fit with contracts, dependencies, extensions, lifecycle?
   * - 135 degrees
     - Adversarial
     - Conditions making a claim false, incomplete, unsafe or misleading?
   * - 180 degrees
     - Verification
     - Exact proving or falsifying evidence?
   * - 225 degrees
     - Operations
     - Failure, recovery, rollback, pressure, concurrency?
   * - 270 degrees
     - Portability
     - Packaging, installation, migration, external behavior?
   * - 315 degrees
     - History
     - Repeated failures, conflicting decisions, erased lessons?
   * - Center
     - Reasoning integrity
     - Coherent, proportional conclusions across evidence?

Coordinates are visualization indexes, not semantic opposites. Vector cancellation
must never erase source findings.

Candidate and context identity
-------------------------------

Manifests declare normalized relative paths and ordering; digest algorithm; file
type and relevant permissions; explicit line-ending policy; symlink, hard-link,
submodule, generated-file and nested-archive behavior; exclusions with rationale;
canonical serialization and digest. Never silently normalize reviewed bytes;
declare how normalized representations relate to original content.

Candidate approval becomes stale on manifest change. Selective finding retention
requires explicit dependency-impact evidence and policy permission. Advance context
when policy, precedence, cutoff, environment, scope, materiality, resources,
disclosure, renderer, effective profiles/tools or assurance changes. Never silently
mutate an iteration's context.

Apply changes only through optimistic binding or a lock. Base mismatch yields
``CONCURRENCY_CONFLICT`` and stops the affected apply path for renewed impact
review and authorization. The initial read-only SDK does not implement applying
changes or confer any change authorization.

Dispatch and aggregation
------------------------

Dispatch binds the input snapshot; mandatory/critical/priority bearings;
specialized ``replace``/``supplement`` mode; dissent lane; evidence sharing and
isolation; output schemas; effective tools; resources and expected information
value; admission/stop rules; disclosure and retention.

Batch manifests list returned outputs, validation and missing lanes. Reject mixed
candidate/context identities, unsupported critical schemas and undeclared lanes.
Preserve source wording/attribution separately from normalized findings.
Typed relations are ``equivalent``, ``contradicts``, ``depends_on``,
``supersedes``, ``narrows`` and ``supports_minority``.

Complete target lifecycle
-------------------------

1. Bind candidate/context.
2. Normalize claims, goals, non-goals, assumptions, rollback and limitations.
3. Declare applicability/dependencies.
4. Validate inputs, tools, schemas, resources and disclosure.
5. Dispatch bearings and dissent.
6. Validate returned batch.
7. Perform initial reconciliation.
8. Preserve contradiction, dependency, supersession, shared-assumption and
   minority registers.
9. Propose remediation/disposition.
10. Perform meta-reconciliation.
11. Route mutating/nonmutating response.
12. Materialize and authorize exact changes where required.
13. Construct assurance DAG.
14. Execute ready technical/reproduction/audit nodes.
15. Perform final reconciliation.
16. Obtain required disposition authorization.
17. Review closure.
18. Append resolution or continuation.
19. Rotate emphasis without removing mandatory/critical coverage.
20. Continue, converge for decision or stop affected work safely.

Mutating route:
``REMEDIATION_RECONCILED -> CHANGE_SET_MATERIALIZED -> CHANGE_AUTHORIZED -> CHANGE_APPLIED``.

Nonmutating proposals: ``ACCEPTED_RISK_PROPOSED``, ``NOT_APPLICABLE_PROPOSED``,
``REJECTED_WITH_EVIDENCE_PROPOSED``, ``SUPERSEDED_PROPOSED``,
``DEFERRED_PROPOSED``, ``OUT_OF_SCOPE_TRANSFER_PROPOSED``. Do not manufacture a
candidate change for a nonmutating disposition.

Assurance requirements are ``required``, ``not_required_with_rationale`` or
``blocked``; outcomes are separately ``PASS``, ``FAIL``, ``INCONCLUSIVE`` or
``BLOCKED``. Dependencies determine readiness; no universal reproduction-before-
audit order exists.

Events and derived state
-------------------------

Core events/states:
``DISCOVERED``, ``ACKNOWLEDGED``, ``ANALYZED``,
``INITIAL_RECONCILIATION_COMPLETED``, ``REMEDIATION_PROPOSED``,
``RUBBER_DUCK_META_REVIEWED``, ``REMEDIATION_RECONCILED``,
``CHANGE_SET_MATERIALIZED``, ``CHANGE_AUTHORIZED``, ``CHANGE_APPLIED``,
``TECHNICALLY_TESTED``, ``AZIMUTHALLY_RETESTED``,
``ASSURANCE_RESULTS_RECONCILED``, ``DISPOSITION_AUTHORIZED``,
``CLOSURE_REVIEWED``, ``RESOLVED``.

Alternative outcomes:
``PARTIALLY_RECONCILED``, ``UNRECONCILED``, ``INSUFFICIENT_EVIDENCE``,
``CONFLICT_RETAINED``, ``OUT_OF_SCOPE``, ``TECHNICAL_RESULT_INCONCLUSIVE``,
``REPRODUCTION_RESULT_INCONCLUSIVE``, ``AUDIT_RESULT_INCONCLUSIVE``,
``AUDIT_NONCONFORMANCE``, ``EVIDENCE_STALE``, ``ARTIFACT_BINDING_INVALIDATED``,
``REOPENED_BY_NEW_EVIDENCE``, ``BLOCKED``, ``REOPENED_BY_EXPIRY_OR_REVOCATION``.

Events are authoritative only within the documented integrity/trust model.
Current state is an event-derived cache bound to its source-event digest.
A local hash chain is not tamper-proof storage. Globally unique event IDs and
existing content-addressed evidence IDs are distinct namespaces and must not
silently change existing wire semantics.

Blockers retain ``blocked_from_state``, ``pending_requirement``, cause, clearance
conditions and scope. Resume at that pending requirement or prior valid state,
not universally at the assurance phase. Expiry/revocation appends reopening and
reevaluates affected closure/activation decisions only through supported runtime
invocations or explicitly authorized scheduling, not an assumed background monitor.

Disposition closure requirements
--------------------------------

* Fixed: reconciled authorized change, required tests/assurance, final
  reconciliation, residual risk and closure review.
* Accepted risk: authorized owner/scope, rationale, controls, expiry,
  review/escalation/revocation and activation consequences.
* Not applicable: applicability evidence, dissent review, transfer check and
  required authorization.
* Rejected with evidence: counterevidence tied to the original finding and
  required reconciliation/authorization.
* Superseded: successor and preserved unresolved obligations.
* Deferred: owner/authority, containment, date or trigger, escalation,
  pending requirement and exact reentry.
* Out-of-scope transfer: destination, accepted transfer/owner, lineage and no
  false source closure.

Unavailable owners remain proposed/unconfirmed.

Evidence, independence, disclosure and retention
------------------------------------------------

Evidence statuses: ``ACTIVE``, ``SUPERSEDED``, ``REVOKED``, ``DISPUTED``,
``STALE``, ``UNAVAILABLE``. These are not aliases for institutional knowledge
lifecycle states. Only eligible ACTIVE evidence supports closure by default;
disputed evidence needs adjudication or exclusion.

Independence dimensions: actor, model, prompt, evidence, environment, procedure,
organization and artifact custody. Unknown critical dimensions remain visible;
scalars cannot hide critical failures/unknowns.

Disclosure classes: ``Public``, ``Repository-Internal``, ``Restricted``,
``Secret``, ``Prohibited-From-Export``, ``Unknown``. Existing fail-closed export
rules remain unchanged; no new exceptions are authorized.

Retention design includes non-sensitive tombstones and separately protected
payloads where applicable. Cryptographic erasure requires actual encryption/key
controls; plaintext deletion is not cryptographic erasure. Legal holds/deletion
require applicable authority. No automatic deletion is part of this slice.

Dynamic bearings, resources and exceptions
------------------------------------------

Dynamic bearings declare trigger, parent, scope, duplicate check,
replace/supplement relationship, expected value, budget, output schema, expiry,
retirement proposal and history. Rejected admission preserves the triggering
concern. Reopening beyond an explicitly configured policy threshold requires
root-cause escalation and Architecture/History review.

Resource profiles cover time, calls, subprocesses, inspection volume, generated
data, package size, network and retained checkpoints. Exceptions bind actor,
authority, scope, candidate, reason, expiry, consequences, controls and
revalidation. Exceptions cannot silently satisfy missing evidence.

Complete contract inventory
---------------------------

All records require versioned schema identity, unique record identity, applicable
candidate/context references, provenance, disclosure/retention, serialization
profile and integrity. This inventory is a target, not a claim all schemas exist.

.. list-table::
   :header-rows: 1

   * - Contract
     - Minimum purpose
   * - codex.candidate-manifest.v1
     - Canonical artifact entries, rules, exclusions, digest
   * - codex.azimuthal-review-context.v1
     - Policies, cutoff, environment, profiles/tools, assurance, renderer, disclosure/resources
   * - codex.policy-record.v1
     - Scope, revision, precedence, supersession, authority
   * - codex.policy-conflict.v1
     - Competing rules, applicability, interpretations, authority
   * - codex.azimuthal-dispatch-plan.v1
     - Lanes, modes, isolation, schemas, tools, budgets
   * - codex.review-bearing.v1
     - Attributed findings, evidence, applicability, assurance
   * - codex.review-batch-manifest.v1
     - Snapshot, outputs, completeness, validation
   * - codex.dynamic-bearing.v1
     - Trigger, scope, duplication, expiry, resources
   * - codex.rubber-duck-finding.v1
     - Claim, observation, evidence, dependencies, severity, uncertainty, cache
   * - codex.finding-relation.v1
     - Typed relationship and rationale
   * - codex.evidence.v1
     - Provenance, binding, confidence, status, disclosure/retention
   * - codex.remediation-response.v1
     - Proposed disposition, response, tests, recovery
   * - codex.change-set.v1
     - Bound base, operations, expected manifest, rollback
   * - codex.reconciliation.v1
     - Stage, inputs, conflicts, assumptions, outcome
   * - codex.assurance-plan.v1
     - DAG, requirements, procedures, roles, budgets
   * - codex.assurance-result.v1
     - Node, artifact, procedure, outcome, independence, limits
   * - codex.test-result.v1
     - Environment, repetitions, result, variance, output
   * - codex.authorization.v1
     - Authority type/source, actor, scope, artifact, expiry
   * - codex.blocker.v1
     - Cause, blocked state, pending requirement, clearance
   * - codex.resource-profile.v1
     - Ceilings, consumption, exhaustion
   * - codex.exception.v1
     - Authorized bounded exception
   * - codex.lifecycle-event.v1
     - Subject, transition, actor, bindings, evidence
   * - codex.resolution-snapshot.v1
     - Disposition closure, risks, authorization, reopening
   * - codex.continuation-state.v1
     - Existing compatible continuation plus pending-node semantics; no incompatible second v1
   * - codex.resilience-record.v1
     - Full vector, evidence, critical floor, unknowns, sensitivity
   * - codex.renderer-validation.v1
     - Renderer/version/source digest, results, fallback
   * - codex.schema-migration.v1
     - Source/target compatibility, transformation, preservation and verification

Compatibility categories: ``backward-compatible``, ``forward-compatible``,
``migration-required``, ``unsupported``. Implemented migrations produce evidence;
unsupported operations reject without rewriting records.

Deployment modes and profile constraints
----------------------------------------

* Profile-only: human selects read-only reconciler; external mechanism handles
  lanes/state.
* CLI/SDK hosted: parent runtime creates supported isolated contexts and validates
  outputs.
* Cloud agent: repository profiles with validated effective tool/MCP boundaries.
* IDE: selected read-only specialist; IDE properties separately validated.

Proposed identities: ``rubber-duck-reconciler``,
``azimuthal-bearing-reviewer``, ``azimuthal-review-orchestrator``.
The reconciler name differs intentionally from a shorter built-in ``rubber-duck``;
availability of any such built-in is environment-specific.

Desired reconciler: read/search only, mutation/execution/approval prohibited,
user invocation where supported, source/profile identity recorded.
Desired bearing reviewer: bounded read/search, programmatic invocation where
supported, dispatch-defined bearing rather than a permanent agent per coordinate.
Desired orchestrator: only approved delegation/reading tools, no edit/unrestricted
execution; external orchestration when profile enforcement is unavailable.

Validate actual frontmatter, target values, tool names, invocation properties,
MCP behavior, precedence and runtime before generating deployable profiles.
A profile forbidding model invocation cannot simultaneously be assumed callable.
Changes to hosted behavior remain inactive proposals or explicit opt-in candidates;
do not silently activate via automatic discovery.

Record effective filename, source level, digest, precedence, tools, MCP allowlist,
target environment, runtime/version and unavailable visibility. Unknown effective
configuration means enforcement unverified, not enforced requested tools.

Reuse compatible profiles, prompts, packaged resources and one existing review
namespace. Do not create a parallel ``.codex/rubber-duck/`` memory system.
Record ownership/reuse decisions in the ADR; proposed owners are not confirmed.

Visual design views and accessibility
-------------------------------------

Target intent is CommonMark, Mermaid 11-style syntax and MathJax 3-compatible
LaTeX, not a claim of support by every GitHub/client renderer. Source fences below
are literal design references in RST. Renderer success requires actual versioned
tool results. A rendering failure does not block unrelated runtime development
when the following text alternatives convey the design.

Edge legend::

    flowchart LR
        A[Source] -->|authorized transition| B[Target]
        C[Source] -. advisory or evidence .-> D[Target]
        E[Decision] -->|conditional path| F[Outcome]
        G[Current state] -->|invalidation or reopening| H[Earlier valid state]

Text alternative: solid edges are authorized transitions; dashed edges are
advice/evidence; labeled decision edges are conditional routes; backward edges
mean invalidation or state-aware resumption.

End-to-end model::

    flowchart TB
        U[Authorized request] --> BIND[Candidate and context]
        BIND --> PLAN[Validated dispatch]
        PLAN --> LANES[Bearing lanes and dissent]
        LANES --> BATCH[Validated batch]
        BATCH -. evidence .-> R0[Initial reconciliation]
        R0 -. requirements .-> RESP[Response proposed]
        RESP -. proposal .-> R1[Meta-reconciliation]
        R1 --> ROUTE{Disposition route}
        ROUTE -->|mutating| CA{Change authorized}
        CA -->|yes| APPLY[Apply bound change]
        CA -->|no| BLOCK[Typed blocker and continuation]
        ROUTE -->|nonmutating| AP[Assurance DAG]
        APPLY --> AP
        AP --> ASSURE[Execute ready nodes]
        ASSURE -. results .-> R2[Final reconciliation]
        R2 --> DA{Disposition authorization}
        DA -->|granted or not required| CLOSE[Closure review]
        DA -->|blocked or denied| BLOCK
        CLOSE --> RS[Resilience assessment]
        RS --> NEXT{Next state}
        NEXT -->|continue| ROT[Rotate bounded bearings]
        ROT --> PLAN
        NEXT -->|stop affected work| BLOCK
        NEXT -->|converged| DEC[Authorized candidate decision]
        BLOCK --> RESUME{Resume checks}
        RESUME -->|satisfied| TARGET[Exact pending node or prior state]
        RESUME -->|unsatisfied| BLOCK

Text alternative: parallel review feeds sequential initial/meta/final
reconciliation. Mutating/nonmutating routes differ. Assurance follows dependencies.
Closure, convergence and candidate approval are separate. Resume targets the
recorded pending state, not universally assurance.

Assurance DAG::

    flowchart LR
        PLAN[Assurance plan] --> TV{Technical verification}
        PLAN --> IR{Independent reproduction}
        PLAN --> AU{Institutional audit}
        TV -->|optional declared dependency| IR
        TV -->|optional declared dependency| AU
        IR -->|only if policy requires| AU
        TV -. result .-> R2[Final reconciliation]
        IR -. result .-> R2
        AU -. result .-> R2

Text alternative: verification, reproduction and audit are separate nodes.
Inter-node dependencies shown are optional examples; validated plans determine order.

Finding-state view::

    stateDiagram-v2
        [*] --> DISCOVERED
        DISCOVERED --> ACKNOWLEDGED
        ACKNOWLEDGED --> ANALYZED
        ANALYZED --> INITIAL_RECONCILIATION_COMPLETED
        INITIAL_RECONCILIATION_COMPLETED --> REMEDIATION_PROPOSED
        REMEDIATION_PROPOSED --> RUBBER_DUCK_META_REVIEWED
        RUBBER_DUCK_META_REVIEWED --> REMEDIATION_RECONCILED
        RUBBER_DUCK_META_REVIEWED --> PARTIALLY_RECONCILED
        RUBBER_DUCK_META_REVIEWED --> UNRECONCILED
        RUBBER_DUCK_META_REVIEWED --> INSUFFICIENT_EVIDENCE
        RUBBER_DUCK_META_REVIEWED --> CONFLICT_RETAINED
        RUBBER_DUCK_META_REVIEWED --> OUT_OF_SCOPE
        PARTIALLY_RECONCILED --> REMEDIATION_PROPOSED
        UNRECONCILED --> ANALYZED
        INSUFFICIENT_EVIDENCE --> ANALYZED
        CONFLICT_RETAINED --> ANALYZED
        OUT_OF_SCOPE --> ANALYZED: accepted transfer or authorized routing
        REMEDIATION_RECONCILED --> CHANGE_SET_MATERIALIZED: mutating
        CHANGE_SET_MATERIALIZED --> CHANGE_AUTHORIZED
        CHANGE_AUTHORIZED --> CHANGE_APPLIED
        CHANGE_APPLIED --> TECHNICALLY_TESTED: applicable
        TECHNICALLY_TESTED --> TECHNICAL_RESULT_INCONCLUSIVE
        TECHNICAL_RESULT_INCONCLUSIVE --> ANALYZED
        TECHNICALLY_TESTED --> AZIMUTHALLY_RETESTED
        AZIMUTHALLY_RETESTED --> ASSURANCE_RESULTS_RECONCILED: applicable nodes complete
        CHANGE_APPLIED --> ASSURANCE_RESULTS_RECONCILED: no assurance nodes required
        REMEDIATION_RECONCILED --> ASSURANCE_RESULTS_RECONCILED: nonmutating with no required nodes
        ASSURANCE_RESULTS_RECONCILED --> DISPOSITION_AUTHORIZED: required
        ASSURANCE_RESULTS_RECONCILED --> CLOSURE_REVIEWED: authorization not required
        DISPOSITION_AUTHORIZED --> CLOSURE_REVIEWED
        CLOSURE_REVIEWED --> RESOLVED
        RESOLVED --> REOPENED_BY_NEW_EVIDENCE
        RESOLVED --> REOPENED_BY_EXPIRY_OR_REVOCATION
        REOPENED_BY_NEW_EVIDENCE --> ANALYZED
        REOPENED_BY_EXPIRY_OR_REVOCATION --> ANALYZED
        ANALYZED --> BLOCKED
        BLOCKED --> ResumeTarget: validated recorded state
        state ResumeTarget <<choice>>

Text alternative: findings are analyzed, reconciled, remediated or dispositioned,
assured, authorized where required and closure-reviewed. Conflict can remain;
findings can block/reopen. This simplified view does not replace validated event
transitions and the assurance DAG for other legal blocked/nonmutating paths.

Synthetic resilience illustration::

    xychart
        title "Synthetic full resilience vector"
        x-axis ["Log", "Adv", "Inst", "Ops", "Hist", "Port", "Epi", "Eco", "Res", "Gov", "Arch", "Evid", "Temp"]
        y-axis "Normalized value" 0 --> 1
        bar [0.79, 0.73, 0.68, 0.77, 0.72, 0.81, 0.76, 0.66, 0.70, 0.64, 0.75, 0.78, 0.69]

DATA STATUS: SYNTHETIC ILLUSTRATION; no measurements or confidence interval.
Text/fallback: logical 0.79; adversarial 0.73; institutional 0.68; operational 0.77;
historical 0.72; portability 0.81; epistemic 0.76; ecological 0.66; resource 0.70;
governance 0.64; architectural 0.75; evidentiary 0.78; temporal 0.69.

Synthetic uncertainty::

    xychart
        title "Synthetic known uncertainty"
        x-axis ["Baseline", "Intent", "Review", "Reconcile", "Change", "Retest", "Assure", "Converge"]
        y-axis "Known uncertainty" 0 --> 100
        line [42, 55, 78, 66, 61, 43, 31, 24]

Text/fallback: synthetic sequence 42, 55, 78, 66, 61, 43, 31, 24.
Production output separately reports unknown-weight.

Synthetic information return::

    xychart
        title "Synthetic normalized information return"
        x-axis ["I1", "I2", "I3", "I4", "I5", "I6", "I7"]
        y-axis "Information return" 0 --> 1
        line [0.92, 0.81, 0.69, 0.53, 0.34, 0.18, 0.08]

Text/fallback: synthetic sequence 0.92, 0.81, 0.69, 0.53, 0.34, 0.18, 0.08.
The complete information-return vector remains primary.

Staged implementation and validation
------------------------------------

Current target: consumer corrections, complete proposed design/formula
preservation, candidate-bound review/event foundation. Next: remediation/
disposition routing, assurance DAG, evidence eligibility and response adequacy.
Following: rotation, recurrence, dynamic bearings, richer independence,
resilience/sensitivity. Later: authorized disposition/approval integrations,
institutional audit, retention controls and representative downstream profiles.
No roadmap item grants operational authority.

Preserve broader institutional decisions/dissent, knowledge lifecycle, ecology,
capability export and independent reproduction objectives. Reuse existing
continuation semantics and a predecessor-verified noncolliding successor.

Executable acceptance targets: manifest determinism/path rules; context drift;
mixed/undeclared/missing-lane handling; source attribution/dissent; typed relations;
event ordering/transitions; event-digest/cache mismatch; mutating/nonmutating
routing; DAG cycles/blocked prerequisites; unknown/zero-weight formula cases;
critical failures hidden by averages; stale/disputed/revoked evidence; exact
resumption; no approval/activation from reconciliation; no fixture-principal trust;
disclosure/path/resource limits; no automatic dispatch; installed resources.
For planned formulas, test presence/mapping/assumptions/status, not mathematical
correctness. Implemented numerics need analytic examples, boundaries and
invariants. Renderer results require actual renderer/version and text alternatives.

When runtime/assets change, build from an identified candidate, retain wheel
digest/manifest, install without editable/source assistance, exercise the external
fixture, verify origins/offline runtime and retain logs/limits. Unchanged-subset
parity is not complete package assurance; documentation skips never close previous
runtime security-analysis gaps. Publication remains unauthorized.

Continuation retains source/candidate/context/manifest digests; predecessor;
design/formula traceability; implemented/planned contracts/formulas; attributed
lanes and assurance; event/cache digest; completed/pending assurance nodes;
blocker state/clearance; findings, dissent, alternatives and failures;
package/renderer/profile limits; local/remote retention; next action and test.
Never use a self-referential commit digest or hide bookkeeping drift.

Acceptance identifiers RD4-01 through RD4-12 respectively cover baseline
reconciliation; consumer chain; complete design preservation; formula mapping;
reuse ADR; binding; findings/events/cache; rotation/blockers/resume; read-only
recommendation; package/external validation; profile/tool/renderer visibility;
successor continuation/roadmap. They supplement rather than redefine G0 preflight,
G1 investigation, G2 design, G3 implementation, G4 safety, G5 independent
verification, G6 packaging, G7 external-wheel validation and G8 continuation.
Task-gate statuses are PASS, FAIL, NOT_RUN, BLOCKED_AUTHORITY,
BLOCKED_RESOURCE_LIMIT and NOT_APPLICABLE_WITH_RATIONALE; assurance outcomes
remain a separate vocabulary.
