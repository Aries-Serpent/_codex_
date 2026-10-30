Fixture-only assurance SDK
==========================

Start here
----------

``codex.institutional.assurance`` adds an inert assurance DAG to a supplied-input
``codex.institutional.review`` plan. It helps a coordinator declare work, ingest
external fixture observations, recheck prerequisites and retain an auditable
Draft recommendation. It does **not** execute work, authenticate actors, approve
a candidate or activate anything. No new dependencies are required.

Install and identify the candidate outside the source checkout. For a complete
offline distribution install, supply an approved wheelhouse containing all
declared dependencies; missing dependencies must fail rather than be ignored::

    python -m venv /tmp/codex-assurance-example
    /tmp/codex-assurance-example/bin/python -m pip install --no-index \
        --find-links /absolute/approved-wheelhouse \
        /absolute/codex_ml-0.3.0-py3-none-any.whl
    /tmp/codex-assurance-example/bin/python -I -c \
        "from codex.institutional import assurance; print(assurance.__file__)"

Use that environment's Python for the examples below. The retained iteration-005
wheel experiments validate the institutional SDK's dependency subset, not a
complete ML-distribution installation. A failed whole-distribution dependency
check remains a separate limitation; the command above is not claimed as an
observed complete installation. Runtime procedures remain inert and offline.

The three assurance node kinds are ``technical_verification``,
``independent_reproduction`` and ``institutional_audit``. Dependencies are only
those explicitly declared. An audit may depend on technical verification without
depending on reproduction. Role names, different runs and different actor names
never establish trusted independence.

The sole additive envelope is ``codex.assurance.v1`` with kinds ``plan``,
``history`` and ``recommendation``. Every envelope is Draft, candidate and
unverified with no authority references. Plans and recommendations additionally
validate these structural limits::

    fixture_only = True
    identity_assurance = "unverified"
    authority = "none"
    approval = False
    activation = False
    full_convergence_model = "unsupported"

Working supplied-data example
-----------------------------

Run this with an environment containing the SDK. All inputs below are
deliberately synthetic. The SDK never reads the named candidate path, executes
the procedure identifiers or discovers targets. In real use, an external,
authorized runner supplies observations; this example only fabricates fixtures.

.. code-block:: python

    from uuid import uuid4
    from codex.institutional import assurance, core, review

    manifest = review.candidate_manifest(
        [{"path": "candidate.py", "kind": "file", "mode": 0o644,
          "content": b"supplied candidate bytes"}],
        {"purpose": "fixture-only"},
    )
    bearings = [
        ("000", "Policy"), ("045", "Security"), ("090", "Architecture"),
        ("135", "Adversarial"), ("180", "Verification"), ("225", "Operations"),
        ("270", "Portability"), ("315", "History"),
    ]
    lanes = [
        {"id": coordinate, "bearing": bearing, "actor": "fixture:" + coordinate,
         "run": "run:" + coordinate, "dissent": False, "required": True,
         "coverage": ["correctness"], "tools": ["read", "search"]}
        for coordinate, bearing in bearings
    ]
    # Dissent is cross-cutting, not a ninth compass coordinate.
    # The separate Center identity is Reasoning integrity, not an independence axis.
    lanes.append(
        {"id": "dissent", "bearing": "cross-cutting", "actor": "fixture:dissent",
         "run": "run:dissent", "dissent": True, "required": True,
         "coverage": ["correctness"], "tools": ["read", "search"]}
    )
    review_plan = review.review_plan(manifest, lanes, ["correctness"], ["correctness"])
    outputs = [
        review.lane_output(review_plan, lane["id"], "No concern in synthetic fixture.", [])
        for lane in lanes
    ]
    kinds = assurance.KINDS
    procedures = [
        {"id": kind + "-fixture", "version": "1", "kind": kind,
         "expected_outputs": ["report"]}
        for kind in kinds
    ]
    nodes = [
        {"id": kind, "kind": kind,
         "depends_on": [] if kind == "technical_verification"
                       else ["technical_verification"],
         "requirement": "required", "rationale": "Synthetic demonstration only.",
         "role": kind, "actor": "fixture:" + kind,
         "identity_assurance": "unverified", "independence": "fixture-only",
         "procedure": {"id": kind + "-fixture", "version": "1"},
         "environment_digest": core.digest({"environment": "synthetic"}),
         "expected_outputs": ["report"],
         "resource_caps": {"max_bytes": 65536, "max_attempts": 4},
         "finding_requirements": [],
         "evidence_requirements": ["procedure-observation"],
         "pending": "Supply a bound external result.",
         "recovery": "Recheck dependencies and append an explicit retry."}
        for kind in kinds
    ]
    plan = assurance.assurance_plan(review_plan, outputs, [], procedures, nodes)
    history = assurance.new_history(plan)
    assert assurance.resume(history, manifest, kinds[0])["ready"]

    for node in nodes:
        prerequisites = assurance.readiness(history, manifest)["nodes"][node["id"]]
        result = {
            "node_id": node["id"], "plan_digest": core.digest(plan),
            "binding": plan["payload"]["data"]["binding"],
            "procedure": node["procedure"],
            "environment_digest": node["environment_digest"],
            "actor": node["actor"], "identity_assurance": "unverified",
            "outcome": "PASS", "outputs": ["report"], "bytes_used": 100,
            "prerequisites": prerequisites["prerequisites"],
            "evidence": [
                {"id": "observation", "source": "Synthetic external observation.",
                 "provenance": "unverified", "authority": "none",
                 "status": "ACTIVE", "applicability": "applicable",
                 "eligibility": "eligible", "critical": True,
                 "requirements": ["procedure-observation"], "finding_requirements": []}
            ],
        }
        history = assurance.ingest_result(history, manifest, str(uuid4()), result)

    recommendation = assurance.reconcile(history, manifest, [])
    data = recommendation["payload"]["data"]
    assert data["recommendation"] == "CONVERGED_FOR_AUTHORIZED_DECISION"
    assert data["limits"]["approval"] is False
    assurance.validate_artifact(recommendation)

``CONVERGED_FOR_AUTHORIZED_DECISION`` means this bounded **fixture** has no
remaining declared blockers. It is not an authorized decision, full formal
convergence, production assurance, G5, acceptance or approval. At least one
required node must pass; an empty/all-exempt required set always blocks.

Plan and external result contract
---------------------------------

All example fields are required; undeclared fields are rejected. Node IDs and
procedure ID/version pairs are unique. Missing dependencies and cycles reject.
``requirement`` is exactly ``required``, ``not_required_with_rationale`` or
``blocked``. Every node needs nonempty rationale, pending and recovery text,
including exempt nodes. ``role`` must equal its node kind. ``independence`` is
``fixture-only`` or ``trusted-required``; the latter always blocks because this
SDK cannot authenticate production separation. Procedure entries are inert
descriptions, not callables, commands or runner configuration.

An exemption skips only that node's execution, not its declared prerequisites.
An exempt bridge remains blocked until its dependencies satisfy their gates,
and its proof includes their current proofs. Replacement/invalidation therefore
propagates through exempt nodes rather than bypassing them.

``environment_digest`` binds the supplied environment description; it does not
prove that environment ran. Results bind exact node, plan digest, candidate and
context binding, procedure/version, actor, environment and current prerequisite
proofs. Outcomes are ``PASS``, ``FAIL``, ``INCONCLUSIVE`` or ``BLOCKED``.
``bytes_used`` is a bounded assertion; serialized result size also must fit the
node byte cap. PASS requires every expected output and evidence requirement.

``finding_requirements`` is a list of objects with ``finding`` and
``requirement_digest``. References use the review SDK's ``lane-id/finding-id``
identity. Compute each digest from the full finding returned by a freshly
recomputed ``review.reconcile(...)["payload"]["data"]["findings"]``. This binds
original wording, clearance conditions and attribution, not a replacement
summary. Evidence must carry the node's exact finding-requirement list.

Evidence provenance is always ``unverified`` and authority always ``none``.
Status is exactly one of ``ACTIVE``, ``SUPERSEDED``, ``REVOKED``, ``DISPUTED``,
``STALE`` or ``UNAVAILABLE``. Applicability is separately ``applicable``,
``not_applicable`` or ``unknown``; eligibility is ``eligible``, ``ineligible`` or
``unknown``. Only active, applicable, eligible evidence satisfies a node.
Unknown critical eligibility is an explicit blocker, not a seventh status.
These fields are supplied assertions, never verified source truth.

Retries, invalidation and exact resume
-------------------------------------

Every appended event has a caller-issued UUIDv4 identity, ordered sequence and
predecessor digest. To retry, supply ``previous_result`` equal to that node's
current result digest from ``fold_events(history)["latest_results"]``.
An identical result is rejected even with an explicit predecessor. A changed
result appends a new event; the old result remains in history as superseded.

This example revokes the technical observation without rewriting its result:

.. code-block:: python

    state = assurance.fold_events(history)
    result_digest = state["latest_results"]["technical_verification"]
    previous = state["evidence_states"][result_digest]["observation"]
    history = assurance.evidence_status(
        history, str(uuid4()), result_digest, "observation", core.digest(previous),
        {"status": "REVOKED", "applicability": "applicable",
         "eligibility": "eligible", "reason": "Fixture observation withdrawn."},
    )
    reopened = assurance.reconcile(history, manifest, [])
    assert reopened["payload"]["data"]["recommendation"] == "BLOCKED"

Evidence events preserve the previous status digest and a nonempty reason.
Replayed evidence states also expose a ``revision`` equal to the originating
event digest. Include this field when hashing the previous state, but do not
supply it inside the new status object. Dependency proofs include the revision,
so restoring the exact original status fields and reason cannot erase an
intervening revocation or dispute.
Any upstream evidence-state change or result replacement invalidates dependent
result proofs. Restoring upstream ACTIVE status does not silently restore old
downstream results: append explicit retries with the newly computed prerequisite
proofs. Invalidations propagate through declared dependencies.

``readiness(history, current_manifest)`` rechecks the supplied current binding.
Candidate byte, permission or context drift reopens required nodes and blocks
the recommendation. Ingestion and resume reject drift; create a new bound plan,
not an event that clears an old plan. ``resume(history, manifest, pending_node)``
requires the exact current pending node and rechecks its dispatch prerequisites.
It returns readiness only, never clears a pending result using a flag/string.

Finding responses and dissent
----------------------------

``reconcile`` always recomputes the original review from the plan's original
outputs and relations. It retains every original finding and relation, including
minority findings and contradictions. No majority vote, averaging, relation
deletion or numeric scoring clears a concern.

Every finding needs an explicit bound fixture rejection recommendation to remove
its fixture blocker. ``REJECTED_WITH_EVIDENCE`` is the one supported nonmutating
disposition. ``dispositions`` accepts these three shapes:

* ``{"finding": ref, "route": "retain", "rationale": text}``: retains an
  unresolved concern without purporting to make a formal disposition.
* ``{"finding": ref, "disposition": "FIXED", "route": "proposed-mutation",
  "rationale": text}``: only a proposed mutation route, never executed or
  treated as closure.
* ``{"finding": ref, "disposition": "REJECTED_WITH_EVIDENCE",
  "route": "nonmutating", "disposition_reason": source_grounded_rejection,
  "followup": review_output,
  "evidence": remediation_evidence, "result_digest": digest,
  "evidence_id": id, "dissent": {"source_quote": original_quote,
  "response": nonempty_text}}``.

The third shape invokes ``review.remediation_adequacy`` against the original
output/finding, not a cached boolean. Its rotated followup must preserve the
original quote and normalization and cover every original clearance condition
with source-grounded observations. ``result_digest`` must identify the current
PASSED node result; the referenced eligible evidence must bind the exact original
finding requirement digest and contain both original quote and response
observations. Dissent handling retains the original quote and an explicit
response. The rejection rationale must occur verbatim in both the rotated
followup source and bound result evidence: an unrelated coverage observation
or renamed boolean cannot become a rejection recommendation.
A contradiction needs dispositions for both endpoints; its original
relation still remains in the ledger. Revocation or stale result binding reopens
these dispositions. This establishes fixture evidence coverage only, not semantic
truth, independently authenticated closure or an institutional decision.

The ledger explicitly labels its decision meaning as a fixture-only rejection
recommendation, not authorized adjudication. This SDK does not implement
ACCEPTED_RISK, NOT_APPLICABLE, SUPERSEDED, DEFERRED or OUT_OF_SCOPE_TRANSFER
dispositions. In particular, fixture evidence cannot grant real accepted risk.
Those names, FIXED on the nonmutating route and the former generic
``fixture-response`` route reject rather than implying all formal routes exist.

Persistence and limits
----------------------

Use ``assurance.attach_continuation(existing_continuation, [plan, history,
recommendation])`` to prepare a compatible Draft successor. Pass that successor
to the existing storage/coordinator preview/apply path; the coordinator must
revalidate repository drift before writing. The helper preserves user extensions
and the predecessor chain, rejects duplicate artifact identities and validates
each artifact. It never writes files, creates a second store or changes
knowledge lifecycle. It may read the installed core schema resource.

Public inputs are bounded by one MiB per JSON artifact, depth 48, 63-bit integers,
32 nodes/procedures, 128 events, bounded lists and per-node byte/attempt caps.
Booleans are not integers for caps. Resource checks occur before huge-integer
serialization. Large histories/recommendations fail closed; no truncation drops
findings or events. ``fold_events(history, cache)`` replays and compares caches;
stale or forged caches reject.

The attachment adapter uses the existing ``core.MAX_BYTES`` aggregate limit
(currently 64 MiB) for the continuation, combined attachment list and successor
payload/envelope. It does not apply the smaller per-assurance-artifact cap to
the user's whole existing continuation. Each individual assurance artifact still
receives its own one-MiB semantic validation; event/count and node resource caps
are unchanged. Oversized aggregate successors reject rather than being written.

Digests provide reproducibility and accidental-corruption detection, not
tamperproof or independently witnessed logs: a hostile party could reseal a
complete history. The coordinator owns cross-store UUID uniqueness and durable
append policy. Imported artifacts never invoke procedures. Approval, activation,
authenticated identity, production trusted independence, semantic evidence truth,
numerical sensitivity proofs and the full convergence model remain unsupported.
